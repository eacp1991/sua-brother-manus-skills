#!/usr/bin/env python3
"""Tiny Markdown renderer for shortlist previews. Final reports should be LLM-rendered."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("shortlist")
    p.add_argument("output", nargs="?", default="commentarium_preview.md")
    p.add_argument("--title", default="COMMENTARIUM PREVIEW")
    args = p.parse_args()

    data = json.loads(Path(args.shortlist).read_text(encoding="utf-8"))
    lines = [f"# {args.title}", "", f"Modo: `{data.get('mode')}`", "", data.get("note", ""), ""]
    meta = data.get("meta", {})
    if meta:
        lines += ["## Números", "", f"- Total bruto: {meta.get('total_raw', 'n/a')}", f"- Total válido: {meta.get('total_valid', 'n/a')}", ""]
    lines += ["## Top shortlist", ""]
    for i, item in enumerate(data.get("items", [])[:20], 1):
        lines += [f"### {i}. {item.get('public_alias')} — {item.get('likes',0)} likes / {item.get('replies',0)} replies", "", f"> {item.get('text')}", ""]
        if "scores" in item:
            lines += [f"Scores: `{item['scores']}`", ""]
        if "signals" in item:
            lines += [f"Signals: `{item['signals']}`", ""]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"Rendered preview → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
