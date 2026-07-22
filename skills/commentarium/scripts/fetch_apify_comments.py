#!/usr/bin/env python3
"""
COMMENTARIUM v0.2 — Generic Apify fetcher

Runs an Apify actor synchronously and saves returned dataset items.
This script intentionally does not hardcode one Instagram actor, because actor input schemas vary.

Environment:
  APIFY_TOKEN required unless --token is passed.

Usage:
  python3 scripts/fetch_apify_comments.py \
    --post-url "https://www.instagram.com/reel/..." \
    --actor-id "username~actor-name" \
    --limit 500 \
    --out raw_comments.json

For actors with custom input schema, pass --input-json custom_input.json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict

API_BASE = "https://api.apify.com/v2"


def load_input(args: argparse.Namespace) -> Dict[str, Any]:
    if args.input_json:
        with open(args.input_json, "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        # Generic input accepted by many Instagram actors, but not guaranteed.
        # Manus/user should adapt when actor docs require different fields.
        payload = {
            "directUrls": [args.post_url],
            "resultsLimit": args.limit,
            "includeReplies": args.include_replies,
            "proxy": {"useApifyProxy": True},
        }
    return payload


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
    parser.add_argument("--post-url", required=False, help="Public post URL. Required unless custom --input-json includes it.")
    parser.add_argument("--actor-id", required=True, help="Apify actor id, e.g. username~actor-name")
    parser.add_argument("--token", default=os.environ.get("APIFY_TOKEN"), help="Apify API token or APIFY_TOKEN env var")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--include-replies", action="store_true", default=True)
    parser.add_argument("--input-json", help="Custom actor input JSON")
    parser.add_argument("--out", default="raw_comments.json")
    parser.add_argument("--format", default="json", choices=["json", "jsonl", "csv"])
    args = parser.parse_args()

    if not args.token:
        print("ERROR: Missing APIFY_TOKEN. Set env var or pass --token.", file=sys.stderr)
        return 2
    if not args.post_url and not args.input_json:
        print("ERROR: --post-url required unless --input-json is provided.", file=sys.stderr)
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
            print("Hint: synchronous run timed out. Run the actor/task asynchronously in Apify UI/API, then export dataset JSON.", file=sys.stderr)
        return 1

    out = Path(args.out)
    if args.format == "json":
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        out.write_text(str(result), encoding="utf-8")

    count = len(result) if isinstance(result, list) else "unknown"
    print(f"Saved {count} items to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
