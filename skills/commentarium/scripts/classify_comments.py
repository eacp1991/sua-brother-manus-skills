#!/usr/bin/env python3
"""
COMMENTARIUM v0.3 — Serious-first comment classification engine

Use this for quick local previews. Final strategic interpretation should still be
performed by an LLM using COMMENTARIUM_MANUS_PROMPT.md.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

CATEGORY_TERMS = {
    "pain": ["não funciona", "problema", "ruim", "pior", "decepção", "frustrado", "cansado", "difícil", "complicado", "sozinho", "sozinha", "em paz"],
    "fear_or_risk": ["medo", "receio", "processo", "assédio", "cancelado", "risco", "perigoso", "denúncia", "exposto"],
    "objection": ["mas", "porém", "discordo", "não é bem assim", "depende", "só que", "na prática", "isso não"],
    "desire": ["quero", "queria", "gostaria", "adoraria", "sonho", "preciso", "seria bom", "seria ótimo"],
    "doubt": ["?", "não entendi", "alguém sabe", "como assim", "como faço", "como faz", "qual", "quando", "onde"],
    "native_language": ["cara", "mano", "bora", "tá", "blz", "valeu", "véi", "vei", "brother", "oxi", "eita"],
    "product_opportunity": ["deveria", "precisava", "falta", "implementar", "feature", "app", "curso", "mentoria", "clube", "plano"],
    "lead_signal": ["link", "preço", "valor", "onde compro", "quero entrar", "como faço", "me chama", "dm"],
    "anger_or_resentment": ["raiva", "ódio", "absurdo", "ridículo", "vergonha", "palhaçada", "não reclamem", "venceu"],
    "hope_or_agreement": ["concordo", "perfeito", "finalmente", "verdade", "sensato", "necessário", "obrigado", "obrigada"],
}

MODE_CHOICES = ["SERIO_SOCIALDEV", "CREATOR_INTELLIGENCE"]


def load_comments(path: str) -> List[Dict[str, Any]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("comments"), list):
        return raw["comments"]
    if isinstance(raw, dict) and isinstance(raw.get("items"), list):
        return raw["items"]
    if isinstance(raw, list):
        return raw
    raise ValueError("Input must be normalized JSON with comments/items or a list")


def classify_text(text: str) -> List[str]:
    low = text.lower()
    cats: List[str] = []
    for category, terms in CATEGORY_TERMS.items():
        if any(term in low for term in terms):
            cats.append(category)
    return cats or ["neutral_or_low_signal"]


def normalize_comment(c: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": c.get("id"),
        "public_alias": c.get("public_alias") or c.get("username") or "Comentarista",
        "text": c.get("text_clean") or c.get("text") or "",
        "username_internal": c.get("username"),
        "likes": int(c.get("likes", 0) or 0),
        "replies": int(c.get("replies", 0) or 0),
        "engagement": int(c.get("engagement", 0) or (int(c.get("likes", 0) or 0) + int(c.get("replies", 0) or 0))),
    }


def classify(comments: List[Dict[str, Any]], mode: str) -> Dict[str, Any]:
    classified: List[Dict[str, Any]] = []
    clusters: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for raw in comments:
        c = normalize_comment(raw)
        categories = classify_text(c["text"])
        for category in categories:
            clusters[category].append(c)
        classified.append({
            "id": c["id"],
            "public_alias": c["public_alias"],
            "text": c["text"],
            "likes": c["likes"],
            "replies": c["replies"],
            "engagement": c["engagement"],
            "categories": categories,
        })

    classified.sort(key=lambda x: x["engagement"], reverse=True)

    cluster_summary = {
        k: {
            "count": len(v),
            "examples": [item["text"][:140] for item in sorted(v, key=lambda x: x["engagement"], reverse=True)[:5]],
        }
        for k, v in sorted(clusters.items(), key=lambda item: len(item[1]), reverse=True)
        if k != "neutral_or_low_signal"
    }

    output = {
        "mode": mode,
        "total_classified": len(classified),
        "top_comments": classified[:20],
        "clusters": cluster_summary,
    }

    if mode == "CREATOR_INTELLIGENCE":
        output["creator_opportunities"] = build_creator_opportunities(classified)

    return output


def build_creator_opportunities(classified: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    opportunities = {
        "video_response": [],
        "live_or_embate": [],
        "content_series": [],
        "product_or_offer_angle": [],
    }
    for c in classified:
        cats = set(c["categories"])
        if "doubt" in cats:
            opportunities["video_response"].append(c)
        if c["replies"] >= 10 or "objection" in cats:
            opportunities["live_or_embate"].append(c)
        if "native_language" in cats or "hope_or_agreement" in cats:
            opportunities["content_series"].append(c)
        if "lead_signal" in cats or "product_opportunity" in cats:
            opportunities["product_or_offer_angle"].append(c)
    return {k: v[:10] for k, v in opportunities.items() if v}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output", nargs="?", default="classified_comments.json")
    parser.add_argument("--mode", choices=MODE_CHOICES, default="SERIO_SOCIALDEV")
    args = parser.parse_args()

    comments = load_comments(args.input)
    result = classify(comments, args.mode)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Classified {result['total_classified']} comments → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
