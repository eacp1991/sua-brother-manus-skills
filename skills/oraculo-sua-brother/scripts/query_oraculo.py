#!/usr/bin/env python3
"""
query_oraculo.py — consulta o super KB da Sua Brother (dual-db, escada FTS5).

KBs (na pasta kb/ da skill):
  renatinha_kb.db  — master: método, voz, cursos, analytics, comentários,
                     funil, produto (atoms: wing, path, heading, body, source_type)
  social_kb.db     — social/copy: hooks, formatos, CTA, posicionamento
                     (atoms: eixo, tipo, texto)

Escada de busca (multi-termo zera no AND implícito do FTS5):
  AND exato → OR ranqueado → LIKE substring.
Prefira 2-3 consultas CURTAS (2-3 termos) a uma consulta longa.

Uso:
  python3 scripts/query_oraculo.py "<termos>" [N] [--kb master|social|both]
  python3 scripts/query_oraculo.py --stats
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "kb"
DB_MASTER = KB_DIR / "renatinha_kb.db"
DB_SOCIAL = KB_DIR / "social_kb.db"


def ladder(con: sqlite3.Connection, table: str, select_fts: str, select_like: str,
           terms: list[str], n: int) -> tuple[str, list[tuple]]:
    quoted = ['"' + t.replace('"', "") + '"' for t in terms]
    for mode, match in (("AND", " ".join(quoted)), ("OR", " OR ".join(quoted))):
        try:
            rows = con.execute(
                f"{select_fts} WHERE {table} MATCH ? ORDER BY rank LIMIT ?",
                (match, n),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
        if rows:
            return mode, rows
    like = f"%{terms[0]}%"
    rows = con.execute(f"{select_like} LIMIT ?", (like, like, n)).fetchall()
    return "LIKE", rows


def q_master(terms: list[str], n: int) -> None:
    if not DB_MASTER.exists():
        print(f"(master ausente: {DB_MASTER})")
        return
    con = sqlite3.connect(f"file:{DB_MASTER}?mode=ro", uri=True)
    mode, rows = ladder(
        con, "atoms",
        "SELECT wing, path, heading, snippet(atoms, 3, '«', '»', '…', 22), source_type FROM atoms",
        "SELECT wing, path, heading, substr(body,1,240), source_type FROM atoms "
        "WHERE body LIKE ? OR heading LIKE ?",
        terms, n,
    )
    con.close()
    print(f"\n═══ KB MASTER ({mode}, {len(rows)} hits) ═══")
    for wing, path, heading, snip, st in rows:
        print(f"\n[{wing}] {heading or '(sem heading)'}  ·  {st}")
        print(f"  fonte: {path}")
        print(f"  {(snip or '').strip()}")
    if not rows:
        print("  (nada — tente termos mais curtos ou sinônimos)")


def q_social(terms: list[str], n: int) -> None:
    if not DB_SOCIAL.exists():
        print(f"(social ausente: {DB_SOCIAL})")
        return
    con = sqlite3.connect(f"file:{DB_SOCIAL}?mode=ro", uri=True)
    mode, rows = ladder(
        con, "atoms",
        "SELECT rowid, eixo, tipo, snippet(atoms, 2, '«', '»', '…', 22) FROM atoms",
        "SELECT rowid, eixo, tipo, substr(texto,1,240) FROM atoms WHERE texto LIKE ? OR eixo LIKE ?",
        terms, n,
    )
    con.close()
    print(f"\n═══ KB SOCIAL ({mode}, {len(rows)} hits) ═══")
    for rid, eixo, tipo, snip in rows:
        print(f"\n[{eixo}] {tipo}  ·  átomo social #{rid}")
        print(f"  {(snip or '').strip()}")
    if not rows:
        print("  (nada — tente termos mais curtos ou sinônimos)")


def stats() -> None:
    for name, db, cols in (
        ("master", DB_MASTER, "wing"),
        ("social", DB_SOCIAL, "eixo"),
    ):
        if not db.exists():
            print(f"{name}: AUSENTE")
            continue
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        total = con.execute("SELECT count(*) FROM atoms").fetchone()[0]
        groups = con.execute(
            f"SELECT {cols}, count(*) FROM atoms GROUP BY {cols} ORDER BY 2 DESC"
        ).fetchall()
        con.close()
        print(f"\n{name}: {total} átomos · {len(groups)} {cols}s")
        for g, c in groups:
            print(f"  {c:5d}  {g}")


def main() -> None:
    args = [a for a in sys.argv[1:]]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    if args[0] == "--stats":
        stats()
        return
    which = "both"
    if "--kb" in args:
        i = args.index("--kb")
        which = args[i + 1] if i + 1 < len(args) else "both"
        del args[i:i + 2]
        if which not in ("master", "social", "both"):
            sys.exit(f"--kb inválido: {which!r} (use master|social|both)")
    n = 6
    if args and args[-1].isdigit():
        n = int(args[-1])
        args = args[:-1]
    terms = " ".join(args).split()
    if not terms:
        print("uso: query_oraculo.py \"<termos>\" [N] [--kb master|social|both]")
        sys.exit(1)
    if which in ("master", "both"):
        q_master(terms, n)
    if which in ("social", "both"):
        q_social(terms, n)


if __name__ == "__main__":
    main()
