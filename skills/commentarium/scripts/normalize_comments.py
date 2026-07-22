#!/usr/bin/env python3
"""
COMMENTARIUM — Comment Normalization & Processing

Normalize raw comment data from Apify, remove duplicates, spam, and empty entries.
Identify recurrent words, high-engagement comments, and create anonymized versions.
"""

import json
import re
from collections import Counter
from datetime import datetime
from typing import List, Dict, Any

def normalize_comments(raw_comments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalize raw comment data from Apify.
    
    Args:
        raw_comments: List of raw comment dictionaries from Apify
        
    Returns:
        Dictionary with normalized comments and metadata
    """
    
    # Remove duplicates and empty entries
    seen = set()
    normalized = []
    
    for comment in raw_comments:
        text = (comment.get("comment_text") or "").strip()
        
        # Skip empty, spam, or mention-only comments
        if not text or len(text) < 3 or text.startswith("@"):
            continue
        
        # Skip duplicates
        if text in seen:
            continue
        
        seen.add(text)
        normalized.append({
            "id": comment.get("comment_id"),
            "text": text,
            "username": comment.get("username"),
            "likes": int(comment.get("likes_count", 0)),
            "replies": int(comment.get("replies_count", 0)),
            "timestamp": comment.get("timestamp"),
            "post_url": comment.get("post_url"),
        })
    
    # Sort by engagement (likes + replies)
    normalized.sort(key=lambda x: x["likes"] + x["replies"], reverse=True)
    
    # Extract recurrent words
    all_text = " ".join([c["text"] for c in normalized])
    words = extract_recurrent_words(all_text)
    
    return {
        "total_raw": len(raw_comments),
        "total_valid": len(normalized),
        "comments": normalized,
        "recurrent_words": words,
        "processed_at": datetime.now().isoformat(),
    }

def extract_recurrent_words(text: str, top_n: int = 30, min_length: int = 4) -> List[Dict[str, Any]]:
    """
    Extract most recurrent words from text.
    
    Args:
        text: Combined text from all comments
        top_n: Number of top words to return
        min_length: Minimum word length to consider
        
    Returns:
        List of (word, count) tuples
    """
    
    # Convert to lowercase and split
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter: remove common stopwords and short words
    stopwords = {
        'o', 'a', 'de', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com',
        'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como',
        'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser',
        'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo',
        'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo',
        'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão', 'você',
        'tinha', 'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha',
        'têm', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual', 'será', 'nós',
        'tenho', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'fosse',
        'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu',
        'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela',
        'delas', 'haja', 'hão', 'há', 'hei', 'hemos', 'há', 'hão', 'haja',
    }
    
    filtered_words = [w for w in words if len(w) >= min_length and w not in stopwords]
    
    # Count occurrences
    word_counts = Counter(filtered_words)
    
    return [
        {"word": word, "count": count}
        for word, count in word_counts.most_common(top_n)
    ]

def anonymize_comments(comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create anonymized version of comments for public output.
    
    Args:
        comments: List of normalized comments
        
    Returns:
        List of comments with anonymized usernames
    """
    
    anonymized = []
    for idx, comment in enumerate(comments, 1):
        comment_copy = comment.copy()
        comment_copy["username"] = f"Comentarista {idx:02d}"
        comment_copy["original_username"] = comment["username"]  # Keep for internal use
        anonymized.append(comment_copy)
    
    return anonymized


if __name__ == "__main__":
    import argparse, sys
    ap = argparse.ArgumentParser(description="Normaliza comentários crus (formato Apify instagram-comment-scraper ou intermediário) -> normalized_comments.json")
    ap.add_argument("input", help="raw_comments.json (lista de comentários)")
    ap.add_argument("output", help="normalized_comments.json")
    a = ap.parse_args()
    with open(a.input, encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        raw = raw.get("comments") or raw.get("data") or raw.get("items") or []
    def _map(c):
        return {
            "comment_id": c.get("comment_id") or c.get("id"),
            "comment_text": c.get("comment_text") or c.get("text") or "",
            "username": c.get("username") or c.get("ownerUsername") or "",
            "likes_count": c.get("likes_count") or c.get("likesCount") or 0,
            "replies_count": c.get("replies_count") or c.get("repliesCount") or 0,
            "timestamp": c.get("timestamp"),
            "post_url": c.get("post_url") or c.get("postUrl"),
        }
    result = normalize_comments([_map(c) for c in raw])
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    n = len(result.get("comments", [])) if isinstance(result, dict) else len(result)
    print(f"normalizados: {n} -> {a.output}", file=sys.stderr)
