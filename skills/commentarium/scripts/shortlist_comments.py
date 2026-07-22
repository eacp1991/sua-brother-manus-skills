#!/usr/bin/env python3
"""
COMMENTARIUM v0.3 — Serious-first shortlist

This is not the final judge. It selects strategically useful comments and gives
heuristic signals for LLM review.

Modes:
- SERIO_SOCIALDEV: pain, objection, desire, fear, doubt, native language, lead/product/content signals
- CREATOR_INTELLIGENCE: video responses, recurrent frames, campaigns, editorial opportunities
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List

QUESTION_RE = re.compile(r"\?")
EXCLAIM_RE = re.compile(r"!")

NATIVE_TERMS = [
    "mano", "cara", "véi", "vei", "brother", "bora", "oxi", "eita", "pqp", "mds", "crlh",
    "só", "né", "tá", "to", "tô", "vcs", "vc", "valeu", "blz", "rapaz", "do nada"
]

PAIN_TERMS = [
    "problema", "ruim", "pior", "decepção", "frustrado", "cansado", "não aguento", "sofro",
    "dor", "triste", "difícil", "complicado", "inseguro", "confuso", "sozinho", "sozinha", "em paz", "desisto"
]

FEAR_RISK_TERMS = [
    "medo", "receio", "risco", "processo", "assédio", "cancelado", "cancelamento", "exposto",
    "denúncia", "perigoso", "preocupado", "insegurança", "não cheguem", "dar ruim"
]

OBJECTION_TERMS = [
    "mas", "porém", "discordo", "não é bem assim", "depende", "só que", "entretanto", "na prática",
    "isso não", "não funciona", "errado", "mentira"
]

DESIRE_TERMS = [
    "quero", "queria", "gostaria", "adoraria", "sonho", "preciso", "necessito", "tomara",
    "seria bom", "seria ótimo", "faz", "fazem", "deveria", "podia", "poderia"
]

CONTENT_OPPORTUNITY_TERMS = [
    "como faço", "como faz", "como assim", "explica", "explica isso", "parte 2", "continua", "faz um", "faz vídeo", "live",
    "podcast", "fala sobre", "ensina", "dica", "guia", "tutorial", "duvida", "dúvida"
]

PRODUCT_SIGNAL_TERMS = [
    "comprar", "preço", "valor", "curso", "mentoria", "clube", "produto", "app", "feature", "falta", "deveria", "precisava",
    "serviço", "plano", "assinatura", "onde acho", "link", "quero entrar"
]

ANGER_TERMS = ["raiva", "ódio", "absurdo", "ridículo", "vergonha", "palhaçada", "cansativo", "não reclamem", "venceu"]
HOPE_TERMS = ["concordo", "perfeito", "finalmente", "verdade", "sensato", "necessário", "obrigado", "obrigada"]


def load_normalized(path: str) -> Dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"meta": {}, "comments": data}
    return data


def sigmoid_log(n: int) -> float:
    return min(10.0, math.log1p(max(0, n)) * 2.1)


def contains_any(text: str, terms: List[str]) -> int:
    low = text.lower()
    return sum(1 for t in terms if t in low)


def signal_tags(text: str, likes: int, replies: int) -> List[str]:
    tags: List[str] = []
    low = text.lower()

    if contains_any(low, PAIN_TERMS):
        tags.append("pain")
    if contains_any(low, FEAR_RISK_TERMS):
        tags.append("fear_or_risk")
    if contains_any(low, OBJECTION_TERMS):
        tags.append("objection")
    if contains_any(low, DESIRE_TERMS):
        tags.append("desire")
    if QUESTION_RE.search(text) or contains_any(low, ["não entendi", "alguém sabe", "como assim"]):
        tags.append("doubt_or_question")
    if contains_any(low, NATIVE_TERMS):
        tags.append("native_language")
    if contains_any(low, CONTENT_OPPORTUNITY_TERMS):
        tags.append("content_opportunity")
    if contains_any(low, PRODUCT_SIGNAL_TERMS):
        tags.append("product_or_lead_signal")
    if contains_any(low, ANGER_TERMS):
        tags.append("anger_or_resentment")
    if contains_any(low, HOPE_TERMS):
        tags.append("hope_or_agreement")
    if likes >= 100:
        tags.append("high_like_signal")
    if replies >= 10:
        tags.append("discussion_signal")
    if EXCLAIM_RE.search(text):
        tags.append("emphasis")

    return tags


def score_serio(c: Dict[str, Any]) -> Dict[str, Any]:
    text = c.get("text_clean") or c.get("text") or ""
    likes = int(c.get("likes", 0))
    replies = int(c.get("replies", 0))
    engagement = int(c.get("engagement", likes + replies))
    tags = signal_tags(text, likes, replies)

    # Weight signals that usually matter in serious social listening.
    weights = {
        "pain": 2.4,
        "fear_or_risk": 2.7,
        "objection": 2.2,
        "desire": 1.8,
        "doubt_or_question": 2.1,
        "native_language": 1.2,
        "content_opportunity": 2.0,
        "product_or_lead_signal": 2.4,
        "anger_or_resentment": 1.6,
        "hope_or_agreement": 1.2,
        "high_like_signal": 1.6,
        "discussion_signal": 1.7,
        "emphasis": 0.4,
    }
    weighted = sum(weights.get(t, 1.0) for t in tags)
    engagement_bonus = min(2.2, sigmoid_log(engagement) * 0.22)
    length = len(text)
    length_bonus = 0.5 if 25 <= length <= 240 else 0.0
    # Keep the heuristic useful as a ranking signal without saturating every viral comment at 10.
    score = min(10.0, 1.2 + weighted * 0.55 + engagement_bonus + length_bonus)

    return {
        "tags": tags if tags else ["low_signal"],
        "serious_score": round(score, 2),
        "why_shortlisted": explain(tags),
    }


def score_creator(c: Dict[str, Any]) -> Dict[str, Any]:
    text = c.get("text_clean") or c.get("text") or ""
    likes = int(c.get("likes", 0))
    replies = int(c.get("replies", 0))
    engagement = int(c.get("engagement", likes + replies))
    tags = signal_tags(text, likes, replies)
    creator_tags: List[str] = []

    if "doubt_or_question" in tags:
        creator_tags.append("video_response")
    if "discussion_signal" in tags or replies >= 10:
        creator_tags.append("live_or_embate")
    if "content_opportunity" in tags:
        creator_tags.append("editorial_prompt")
    if "native_language" in tags and likes >= 50:
        creator_tags.append("hook_candidate")
    if "product_or_lead_signal" in tags:
        creator_tags.append("offer_or_product_angle")
    if likes >= 100:
        creator_tags.append("high_signal")

    score = min(10.0, 1.2 + len(creator_tags) * 1.45 + min(2.2, sigmoid_log(engagement) * 0.24))
    return {
        "tags": creator_tags if creator_tags else tags if tags else ["low_signal"],
        "creator_score": round(score, 2),
        "why_shortlisted": explain(creator_tags or tags),
    }


def explain(tags: List[str]) -> str:
    if not tags:
        return "Comentário mantido apenas por engajamento/representatividade."
    translations = {
        "pain": "expressa dor ou frustração",
        "fear_or_risk": "sinaliza medo/risco percebido",
        "objection": "traz resistência ou contraponto",
        "desire": "expressa desejo ou demanda",
        "doubt_or_question": "contém dúvida que pode virar conteúdo",
        "native_language": "traz linguagem nativa útil",
        "content_opportunity": "pede explicação ou continuação",
        "product_or_lead_signal": "indica oportunidade comercial/produto",
        "anger_or_resentment": "mostra ressentimento ou indignação",
        "hope_or_agreement": "mostra concordância/esperança",
        "high_like_signal": "tem alto sinal de curtidas",
        "discussion_signal": "gerou discussão",
        "emphasis": "tem ênfase emocional",
        "video_response": "merece resposta em vídeo",
        "live_or_embate": "pode virar live/embate",
        "editorial_prompt": "vira pauta editorial",
        "hook_candidate": "pode virar hook",
        "offer_or_product_angle": "pode virar ângulo de oferta",
        "high_signal": "alto sinal de engajamento",
    }
    return "; ".join(translations.get(t, t) for t in tags[:5])


def shortlist(data: Dict[str, Any], mode: str, top: int) -> Dict[str, Any]:
    out = []
    for c in data.get("comments", []):
        row = {
            "public_alias": c.get("public_alias"),
            "text": c.get("text_clean") or c.get("text"),
            "likes": c.get("likes", 0),
            "replies": c.get("replies", 0),
            "engagement": c.get("engagement", 0),
            "flags": c.get("flags", []),
        }
        if mode == "CREATOR_INTELLIGENCE":
            row["signals"] = score_creator(c)
            sort_key = row["signals"]["creator_score"]
        else:
            row["signals"] = score_serio(c)
            sort_key = row["signals"]["serious_score"]
        row["_sort_key"] = round(sort_key, 4)
        out.append(row)

    out.sort(key=lambda r: (r["_sort_key"], r["engagement"]), reverse=True)
    for r in out:
        r.pop("_sort_key", None)

    return {
        "mode": mode,
        "meta": data.get("meta", {}),
        "note": "Shortlist heurística serious-first. O veredito final deve ser feito por LLM com rubrica COMMENTARIUM.",
        "items": out[:top],
        "recurrent_words": data.get("recurrent_words", [])[:40],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output", nargs="?", default="shortlist.json")
    parser.add_argument("--mode", choices=["SERIO_SOCIALDEV", "CREATOR_INTELLIGENCE"], default="SERIO_SOCIALDEV")
    parser.add_argument("--top", type=int, default=120)
    args = parser.parse_args()

    data = load_normalized(args.input)
    result = shortlist(data, args.mode, args.top)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(result['items'])} shortlist items → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
