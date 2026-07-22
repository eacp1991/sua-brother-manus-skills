#!/usr/bin/env python3
"""
COMMENTARIUM v0.2 — Comment normalization

Accepts raw JSON from Apify-like actors and normalizes field names.
Outputs a JSON object with metadata, valid comments, recurrent words and removed stats.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

TEXT_FIELDS = ["comment_text", "commentText", "text", "comment", "caption", "body"]
USER_FIELDS = ["username", "ownerUsername", "owner_username", "user", "author", "profileName"]
LIKE_FIELDS = ["likes_count", "likesCount", "likeCount", "likes", "diggCount"]
REPLY_FIELDS = ["replies_count", "repliesCount", "replyCount", "replies", "childCommentsCount"]
ID_FIELDS = ["comment_id", "commentId", "id", "pk", "shortCode"]
TIME_FIELDS = ["timestamp", "createdAt", "postedAt", "created_at", "date"]
URL_FIELDS = ["post_url", "postUrl", "url", "inputUrl", "postPage"]

PT_STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das", "e", "é", "em",
    "no", "na", "nos", "nas", "por", "para", "pra", "pro", "com", "sem", "que", "se", "ao", "aos",
    "mais", "mas", "não", "sim", "só", "ja", "já", "ta", "tá", "to", "tô", "vc", "vcs", "voce", "você",
    "eu", "tu", "ele", "ela", "eles", "elas", "me", "te", "seu", "sua", "meu", "minha", "isso", "esse",
    "essa", "este", "esta", "aqui", "ali", "lá", "foi", "ser", "ter", "tem", "vai", "vou", "muito", "muita",
    "muitos", "muitas", "como", "quando", "onde", "porque", "porquê", "né", "hein", "hahaha", "kkkk", "kkk"
}

SENSITIVE_PATTERNS = [
    ("email", re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)),
    ("phone", re.compile(r"(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9?\d{4}[-\s]?\d{4}")),
    ("cpf_like", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
]

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
MENTION_ONLY_RE = re.compile(r"^(?:@\w+[\s,;:]*)+$")
HAS_LETTER_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]")


def first_value(obj: Dict[str, Any], fields: Iterable[str], default: Any = None) -> Any:
    for field in fields:
        if field in obj and obj[field] not in (None, ""):
            return obj[field]
    return default


def to_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().lower().replace(".", "").replace(",", ".")
    multiplier = 1
    if text.endswith("k") or text.endswith("mil"):
        multiplier = 1000
        text = text.replace("mil", "").replace("k", "").strip()
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0


def clean_text(text: str) -> str:
    text = URL_RE.sub("[URL]", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_key(text: str) -> str:
    text = text.lower().strip()
    text = URL_RE.sub("", text)
    text = re.sub(r"\W+", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def flags_for(text: str) -> List[str]:
    flags: List[str] = []
    for name, pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            flags.append(f"contains_{name}")
    if MENTION_ONLY_RE.match(text.strip()):
        flags.append("mention_only")
    if not HAS_LETTER_RE.search(text):
        flags.append("no_letters")
    return flags


def mask_sensitive(text: str) -> str:
    masked = text
    for name, pattern in SENSITIVE_PATTERNS:
        masked = pattern.sub(f"[{name.upper()}_REMOVED]", masked)
    return masked


def load_items(path: str) -> List[Dict[str, Any]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ["items", "data", "comments", "results"]:
            if isinstance(raw.get(key), list):
                return raw[key]
    raise ValueError("Input JSON must be a list or contain items/data/comments/results list")


def extract_words(comments: List[Dict[str, Any]], top_n: int = 50) -> List[Dict[str, Any]]:
    all_text = " ".join(c["text_clean"].lower() for c in comments)
    words = re.findall(r"\b[\wÀ-ÖØ-öø-ÿ]{3,}\b", all_text, flags=re.UNICODE)
    words = [w for w in words if w not in PT_STOPWORDS and not w.startswith("url")]
    counts = Counter(words)
    return [{"word": w, "count": n} for w, n in counts.most_common(top_n)]


def normalize_comments(items: List[Dict[str, Any]], dedupe: str = "text_user") -> Dict[str, Any]:
    seen = set()
    comments: List[Dict[str, Any]] = []
    removed = defaultdict(int)

    for idx, item in enumerate(items):
        text = str(first_value(item, TEXT_FIELDS, "") or "").strip()
        username = first_value(item, USER_FIELDS, None)
        flags = flags_for(text)

        if not text or len(text.strip()) < 2:
            removed["empty_or_too_short"] += 1
            continue
        if "mention_only" in flags:
            removed["mention_only"] += 1
            continue
        if "no_letters" in flags:
            removed["no_letters"] += 1
            continue

        text_masked = mask_sensitive(text)
        text_clean = clean_text(text_masked)
        key_text = normalize_key(text_clean)
        if dedupe == "text":
            dedupe_key = key_text
        elif dedupe == "text_user":
            dedupe_key = f"{username or 'unknown'}::{key_text}"
        else:
            dedupe_key = hashlib.sha1(f"{idx}:{key_text}".encode()).hexdigest()

        if dedupe_key in seen:
            removed["duplicate"] += 1
            continue
        seen.add(dedupe_key)

        likes = to_int(first_value(item, LIKE_FIELDS, 0))
        replies = to_int(first_value(item, REPLY_FIELDS, 0))
        comment_id = first_value(item, ID_FIELDS, None)
        if comment_id is None:
            comment_id = hashlib.sha1(f"{username}:{text_clean}:{idx}".encode("utf-8")).hexdigest()[:16]

        comments.append({
            "id": str(comment_id) if comment_id is not None else None,
            "text": text_masked,
            "text_clean": text_clean,
            "username": str(username) if username is not None else None,
            "public_alias": f"Comentarista {len(comments)+1:02d}",
            "likes": likes,
            "replies": replies,
            "engagement": likes + replies,
            "timestamp": first_value(item, TIME_FIELDS, None),
            "post_url": first_value(item, URL_FIELDS, None),
            "flags": flags,
        })

    comments.sort(key=lambda c: (c["engagement"], c["likes"], c["replies"]), reverse=True)
    # Reassign public aliases after sorting so top comments get stable top aliases.
    for i, c in enumerate(comments, 1):
        c["public_alias"] = f"Comentarista {i:02d}"

    return {
        "meta": {
            "total_raw": len(items),
            "total_valid": len(comments),
            "removed": dict(removed),
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "dedupe": dedupe,
        },
        "recurrent_words": extract_words(comments),
        "comments": comments,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output", nargs="?", default="normalized_comments.json")
    parser.add_argument("--dedupe", choices=["text", "text_user", "none"], default="text_user")
    args = parser.parse_args()

    items = load_items(args.input)
    result = normalize_comments(items, dedupe=args.dedupe)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Normalized {result['meta']['total_valid']} / {result['meta']['total_raw']} comments → {args.output}")
    if result["meta"]["removed"]:
        print("Removed:", result["meta"]["removed"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
