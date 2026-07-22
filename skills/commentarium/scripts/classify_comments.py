#!/usr/bin/env python3
"""
COMMENTARIUM — Comment Classification Engine

Classify comments into categories based on mode:
- SERIO_SOCIALDEV: Pain points, objections, desires, product signals
- QUINTA_SERIE_LAB: Humor, timing, originality, shareability
- CREATOR_INTELLIGENCE: Content opportunities, video responses, campaigns
"""

import json
from typing import List, Dict, Any
from enum import Enum

class Mode(Enum):
    SERIO_SOCIALDEV = "serio"
    QUINTA_SERIE_LAB = "quinta_serie"
    CREATOR_INTELLIGENCE = "creator"

class CommentClassifier:
    """Classify comments based on mode and generate insights."""
    
    def __init__(self, mode: str = "serio"):
        self.mode = mode
    
    def classify(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classify comments based on selected mode.
        
        Args:
            comments: List of normalized comments
            
        Returns:
            Dictionary with classified comments and clusters
        """
        
        if self.mode == "serio":
            return self._classify_serio(comments)
        elif self.mode == "quinta_serie":
            return self._classify_quinta_serie(comments)
        elif self.mode == "creator":
            return self._classify_creator(comments)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
    
    def _classify_serio(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classify for SERIO_SOCIALDEV mode.
        
        Categories: pain, objection, desire, fear, belief, irony, anger, hope, doubt, native_language, response_opportunity, product_opportunity, lead
        """
        
        classified = []
        clusters = {
            "pain": [],
            "objection": [],
            "desire": [],
            "fear": [],
            "native_language": [],
            "product_opportunity": [],
        }
        
        for comment in comments:
            text = comment["text"].lower()
            
            categories = []
            
            # Simple keyword-based classification (in production, use LLM)
            if any(word in text for word in ["não funciona", "problema", "ruim", "pior", "decepção", "frustrado"]):
                categories.append("pain")
                clusters["pain"].append(comment)
            
            if any(word in text for word in ["mas", "porém", "entretanto", "não é bem assim", "discordo"]):
                categories.append("objection")
                clusters["objection"].append(comment)
            
            if any(word in text for word in ["quero", "desejo", "gostaria", "adoraria", "sonho"]):
                categories.append("desire")
                clusters["desire"].append(comment)
            
            if any(word in text for word in ["medo", "assustado", "preocupado", "receio", "temo"]):
                categories.append("fear")
                clusters["fear"].append(comment)
            
            # Detect native language patterns (gírias, expressões típicas)
            if any(word in text for word in ["cara", "mano", "bora", "tá", "tá bom", "blz", "valeu"]):
                categories.append("native_language")
                clusters["native_language"].append(comment)
            
            if any(word in text for word in ["deveria", "precisava", "falta", "implementar", "feature"]):
                categories.append("product_opportunity")
                clusters["product_opportunity"].append(comment)
            
            classified.append({
                "id": comment["id"],
                "text": comment["text"],
                "username": comment["username"],
                "likes": comment["likes"],
                "categories": categories if categories else ["neutral"],
                "engagement": comment["likes"] + comment["replies"],
            })
        
        # Clean up empty clusters
        clusters = {k: v for k, v in clusters.items() if v}
        
        return {
            "mode": "SERIO_SOCIALDEV",
            "total_classified": len(classified),
            "comments": classified,
            "clusters": {
                k: {
                    "count": len(v),
                    "examples": [c["text"][:80] for c in v[:3]]
                }
                for k, v in clusters.items()
            }
        }
    
    def _classify_quinta_serie(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classify for QUINTA_SERIE_LAB mode.
        
        Score on: timing, double_meaning, originality, simplicity, shareability, collective_response, script_potential, fifth_grade_level
        """
        
        classified = []
        awards = {
            "trocadilho_inevitavel": [],
            "baixaria_elegante": [],
            "eu_pensei_mas_nao_tive_coragem": [],
            "comentario_que_virou_pauta": [],
            "instituto_brasileiro_quinta_serie": [],
            "o_algoritmo_sabia": [],
            "reu_primario_perdido": [],
        }
        
        for comment in comments:
            text = comment["text"]
            
            # Simple scoring (in production, use LLM)
            scores = {
                "timing": 5,  # Placeholder
                "double_meaning": 5,
                "originality": 5,
                "simplicity": 5,
                "shareability": 5,
                "collective_response": 5,
                "script_potential": 5,
                "fifth_grade_level": 5,
            }
            
            total_score = sum(scores.values()) / len(scores)
            
            # Assign awards based on heuristics
            if "?" in text and "!" in text:
                awards["trocadilho_inevitavel"].append(comment)
            
            if len(text) > 50 and "mas" in text.lower():
                awards["baixaria_elegante"].append(comment)
            
            if comment["likes"] > 100:
                awards["comentario_que_virou_pauta"].append(comment)
            
            classified.append({
                "id": comment["id"],
                "text": comment["text"],
                "username": comment["username"],
                "likes": comment["likes"],
                "scores": scores,
                "total_score": round(total_score, 1),
                "engagement": comment["likes"] + comment["replies"],
            })
        
        # Sort by total score
        classified.sort(key=lambda x: x["total_score"], reverse=True)
        
        # Clean up empty awards
        awards = {k: v for k, v in awards.items() if v}
        
        return {
            "mode": "QUINTA_SERIE_LAB",
            "total_classified": len(classified),
            "top_comments": classified[:10],
            "awards": {
                k: {
                    "count": len(v),
                    "examples": [c["text"][:80] for c in v[:2]]
                }
                for k, v in awards.items()
            }
        }
    
    def _classify_creator(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classify for CREATOR_INTELLIGENCE mode.
        
        Identify: video responses, recurring jokes, campaign opportunities, quadro potential, embate potential, product ideas
        """
        
        classified = []
        opportunities = {
            "video_response": [],
            "recurring_joke": [],
            "campaign": [],
            "quadro": [],
            "embate": [],
            "product_idea": [],
        }
        
        for comment in comments:
            text = comment["text"]
            
            # Simple heuristics (in production, use LLM)
            if comment["likes"] > 50:
                opportunities["video_response"].append(comment)
            
            if any(word in text.lower() for word in ["sempre", "toda vez", "sempre que", "nunca"]):
                opportunities["recurring_joke"].append(comment)
            
            if comment["likes"] > 100:
                opportunities["campaign"].append(comment)
            
            if comment["replies"] > 5:
                opportunities["embate"].append(comment)
            
            classified.append({
                "id": comment["id"],
                "text": comment["text"],
                "username": comment["username"],
                "likes": comment["likes"],
                "replies": comment["replies"],
                "engagement": comment["likes"] + comment["replies"],
            })
        
        # Sort by engagement
        classified.sort(key=lambda x: x["engagement"], reverse=True)
        
        # Clean up empty opportunities
        opportunities = {k: v for k, v in opportunities.items() if v}
        
        return {
            "mode": "CREATOR_INTELLIGENCE",
            "total_classified": len(classified),
            "top_comments": classified[:10],
            "opportunities": {
                k: {
                    "count": len(v),
                    "examples": [c["text"][:80] for c in v[:2]]
                }
                for k, v in opportunities.items()
            }
        }


if __name__ == "__main__":
    import argparse, sys
    ap = argparse.ArgumentParser(description="Peneira: classifica normalized_comments.json -> shortlist.json por modo")
    ap.add_argument("input", help="normalized_comments.json")
    ap.add_argument("output", help="shortlist.json")
    ap.add_argument("--mode", default="SERIO_SOCIALDEV", help="SERIO_SOCIALDEV | QUINTA_SERIE_LAB | CREATOR_INTELLIGENCE")
    ap.add_argument("--top", type=int, default=120, help="quantos comentários (por engajamento) entram na peneira")
    a = ap.parse_args()
    with open(a.input, encoding="utf-8") as f:
        data = json.load(f)
    comments = data.get("comments") if isinstance(data, dict) else data
    comments = sorted(comments or [], key=lambda c: int(c.get("likes") or 0) + int(c.get("replies") or 0), reverse=True)[: a.top]
    mode_map = {"SERIO_SOCIALDEV": "serio", "QUINTA_SERIE_LAB": "quinta_serie", "CREATOR_INTELLIGENCE": "creator"}
    result = CommentClassifier(mode=mode_map.get(a.mode.upper(), a.mode)).classify(comments)
    result["_meta"] = {"mode": a.mode, "top": a.top, "input_total": len(comments)}
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"shortlist ({a.mode}, top {a.top}) -> {a.output}", file=sys.stderr)
