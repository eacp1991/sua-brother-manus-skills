#!/usr/bin/env python3
"""
COMMENTARIUM v0.6 — Apify comment fetcher (actor canônico: apify/instagram-scraper)

Roda um actor Apify síncrono e salva os itens do dataset. Default = apify~instagram-scraper
no modo resultsType:comments (pega 3-15x mais que o comment-scraper legado; case 3.724).

ANTI-FABRICAÇÃO: resposta vazia, null ou inesperada FALHA com exit != 0 — nunca "sucesso vazio".

Environment:
  APIFY_TOKEN obrigatório, exceto se --token for passado.

Usage:
  python3 scripts/fetch_apify_comments.py \
    --post-url "https://www.instagram.com/reel/..." \
    --limit 5000 \
    --out raw_comments.json

Para input custom, passar --input-json custom_input.json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict

API_BASE = "https://api.apify.com/v2"
DEFAULT_ACTOR = "apify~instagram-scraper"


def load_input(args: argparse.Namespace) -> Dict[str, Any]:
    if args.input_json:
        with open(args.input_json, "r", encoding="utf-8") as f:
            return json.load(f)
    # Schema confirmado do apify/instagram-scraper em modo comentários.
    return {
        "directUrls": [args.post_url],
        "resultsType": "comments",
        "resultsLimit": args.limit,
    }


def post_json(url: str, payload: Dict[str, Any], timeout: int = 310) -> Any:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-url", required=False, help="URL do post público. Obrigatório exceto se --input-json já incluir.")
    parser.add_argument("--actor-id", default=DEFAULT_ACTOR, help=f"Apify actor id (default {DEFAULT_ACTOR})")
    parser.add_argument("--token", default=os.environ.get("APIFY_TOKEN"), help="Token Apify ou env APIFY_TOKEN")
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--input-json", help="Input custom do actor (JSON)")
    parser.add_argument("--out", default="raw_comments.json")
    parser.add_argument("--format", default="json", choices=["json", "jsonl", "csv"])
    args = parser.parse_args()

    if not args.token:
        print("ERROR: APIFY_TOKEN ausente. Defina a env var ou passe --token.", file=sys.stderr)
        return 2
    if not args.post_url and not args.input_json:
        print("ERROR: --post-url obrigatório (exceto com --input-json).", file=sys.stderr)
        return 2

    payload = load_input(args)
    actor = urllib.parse.quote(args.actor_id, safe="~")
    url = f"{API_BASE}/acts/{actor}/run-sync-get-dataset-items?token={urllib.parse.quote(args.token)}&format={args.format}"

    try:
        result = post_json(url, payload)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: Apify HTTP {e.code}: {msg}", file=sys.stderr)
        if e.code == 408:
            print("Hint: run síncrono estourou. Rode async na API/UI do Apify e exporte o dataset.", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"ERROR: rede/conexão falhou: {e.reason}", file=sys.stderr)
        return 1
    except (TimeoutError, json.JSONDecodeError) as e:
        print(f"ERROR: timeout ou resposta não-JSON: {e}", file=sys.stderr)
        return 1

    # ANTI-FABRICAÇÃO: vazio/null/inesperado = FALHA, nunca "sucesso vazio".
    if result is None or not isinstance(result, list):
        print("ERROR: Apify retornou resposta vazia ou inesperada (não é lista). PARE — não invente comentários.", file=sys.stderr)
        return 3
    if len(result) == 0:
        print("ERROR: Apify retornou 0 comentários. Pode ser rate-limit, post sem comentários, ou actor errado. NÃO fabrique dados — verifique o actor/limite e re-rode.", file=sys.stderr)
        return 3

    out = Path(args.out)
    if args.format == "json":
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        out.write_text(str(result), encoding="utf-8")
    print(f"Saved {len(result)} items to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
