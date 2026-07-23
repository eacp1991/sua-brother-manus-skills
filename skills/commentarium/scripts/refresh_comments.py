#!/usr/bin/env python3
"""
refresh_comments.py — coleta INCREMENTAL de comentários (commentarium v0.8).

Princípio: o 1º run (FULL) é caro e vira BASELINE no ledger. Todo re-run
depois é REFRESH: puxa só uma fatia dos mais recentes (--slice, default 300),
deduplica por id contra o ledger (o "cutoff" vem do run antigo, sempre
auto-descoberto) e anexa APENAS os novos ao corpus. Custo do refresh =
fatia, nunca o corpus inteiro de novo.

Uso:
  python3 refresh_comments.py full    --post-url URL [--limit 10000] [--corpus out.json]
  python3 refresh_comments.py refresh --post-url URL [--slice 300]  [--corpus out.json]
  python3 refresh_comments.py status  [--ledger ledger.json]

Estado: ledger.json (por diretório de trabalho, ou --ledger). Guarda por post:
runs originais (run_id/dataset/input), ids conhecidos e timestamp mais novo.
Anti-fabricação: falha de API/dataset vazio → exit≠0, nunca inventar.

⚠️ Limite conhecido: o IG não devolve comentários em ordem estritamente
cronológica (ranking). Se o refresh voltar SATURADO (novos == slice), rode de
novo com --slice maior ou um full — há mais novidade do que a fatia cobriu.
Recomendação: 1 full de ressincronização por mês.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

BASE = "https://api.apify.com/v2"
ACTOR = "apify~instagram-scraper"
POLL_S = 15
POLL_MAX = 80  # ~20 min


def token() -> str:
    for name in ("APIFY_TOKEN", "APIFY_API_TOKEN"):
        v = os.environ.get(name)
        if v:
            return v
    # ~/.env sem export (gotcha conhecido): parse direto
    envf = Path.home() / ".env"
    if envf.exists():
        for line in envf.read_text().splitlines():
            m = re.match(r"^(APIFY_TOKEN|APIFY_API_TOKEN)=(.+)$", line.strip())
            if m:
                return m.group(2).strip().strip('"').strip("'")
    sys.exit("ERRO: APIFY_TOKEN/APIFY_API_TOKEN não encontrado (env ou ~/.env)")


def api(method: str, path: str, tok: str, body: dict | None = None):
    cmd = ["curl", "-sS", "-m", "120", "-X", method, f"{BASE}/{path}{'&' if '?' in path else '?'}token={tok}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ERRO curl {path}: {r.stderr.strip()[:200]}")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(f"ERRO resposta não-JSON em {path}: {r.stdout[:200]}")


def shortcode(url: str) -> str:
    m = re.search(r"/(?:reel|p|tv)/([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else re.sub(r"\W", "", url)[-12:]


def cid(c: dict) -> str:
    return str(c.get("id") or c.get("commentUrl") or hash(json.dumps(c, sort_keys=True)[:400]))


def run_and_fetch(tok: str, url: str, limit: int) -> tuple[dict, list]:
    inp = {"directUrls": [url], "resultsType": "comments", "resultsLimit": limit}
    d = api("POST", f"acts/{ACTOR}/runs", tok, inp)["data"]
    run_id, ds = d["id"], d["defaultDatasetId"]
    print(f"run {run_id} lançada (limit={limit})…", file=sys.stderr)
    for _ in range(POLL_MAX):
        time.sleep(POLL_S)
        st = api("GET", f"actor-runs/{run_id}", tok)["data"]["status"]
        if st == "SUCCEEDED":
            break
        if st in ("FAILED", "ABORTED", "TIMED-OUT"):
            sys.exit(f"ERRO: run {run_id} terminou {st} — nada foi inventado, corpus intacto")
    else:
        sys.exit(f"ERRO: run {run_id} não terminou em {POLL_MAX*POLL_S}s")
    items = api("GET", f"datasets/{ds}/items?format=json&clean=1", tok)
    if not isinstance(items, list):
        sys.exit(f"ERRO: dataset {ds} não retornou lista")
    meta = {"run_id": run_id, "dataset_id": ds, "started_at": d["startedAt"],
            "input": inp, "items": len(items)}
    return meta, items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["full", "refresh", "status"])
    ap.add_argument("--post-url")
    ap.add_argument("--limit", type=int, default=10000)
    ap.add_argument("--slice", type=int, default=300)
    ap.add_argument("--corpus")
    ap.add_argument("--ledger", default="ledger.json")
    a = ap.parse_args()

    ledger_p = Path(a.ledger)
    ledger = json.loads(ledger_p.read_text()) if ledger_p.exists() else {}

    if a.mode == "status":
        for sc, rec in ledger.items():
            print(f"{sc}: {len(rec.get('known_ids', []))} ids · {len(rec.get('runs', []))} runs · newest_ts={rec.get('newest_ts')}")
        return

    if not a.post_url:
        sys.exit("--post-url obrigatório em full/refresh")
    tok = token()
    sc = shortcode(a.post_url)
    corpus_p = Path(a.corpus or f"comments_{sc}_FULL.json")
    rec = ledger.setdefault(sc, {"post_url": a.post_url, "runs": [], "known_ids": [], "newest_ts": None})

    # cutoff SEMPRE do run antigo: ledger e, se existir, o corpus em disco
    known = set(rec["known_ids"])
    corpus = []
    if corpus_p.exists():
        corpus = json.loads(corpus_p.read_text())
        known |= {cid(c) for c in corpus}

    if a.mode == "refresh" and not known:
        sys.exit(f"ERRO: refresh sem baseline pra {sc} — rode 'full' primeiro (o cutoff nasce do run original)")

    limit = a.limit if a.mode == "full" else a.slice
    meta, items = run_and_fetch(tok, a.post_url, limit)
    meta["kind"] = a.mode.upper()

    fresh = [c for c in items if cid(c) not in known]
    if a.mode == "full" and not corpus:
        corpus = items
        fresh = items
    else:
        corpus.extend(fresh)

    corpus_p.write_text(json.dumps(corpus, ensure_ascii=False, indent=1))
    rec["runs"].append(meta)
    rec["known_ids"] = sorted(known | {cid(c) for c in items})
    ts = [str(c.get("timestamp")) for c in corpus if c.get("timestamp")]
    rec["newest_ts"] = max(ts) if ts else rec.get("newest_ts")
    ledger_p.write_text(json.dumps(ledger, ensure_ascii=False, indent=1))

    saturado = a.mode == "refresh" and len(fresh) >= limit
    print(f"{sc} [{a.mode}]: fetched={len(items)} novos={len(fresh)} corpus={len(corpus)} → {corpus_p}")
    if saturado:
        print(f"⚠️ SATURADO: novos == slice ({limit}) — há mais novidade; rode --slice maior ou full")
        sys.exit(3)


if __name__ == "__main__":
    main()
