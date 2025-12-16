import re
from typing import List, Dict

SKALL_TERMS = [
    "ska", "skall", "måste", "krävs", "åligger",
    "får ej", "icke", "förbinder sig att"
]

BOR_TERMS = [
    "bör", "borde", "önskvärt", "meriterande",
    "eftersträvas", "ser gärna", "bedöms positivt"
]

SKALL_REGEX = re.compile(r"\b(" + "|".join(SKALL_TERMS) + r")\b", re.IGNORECASE)
BOR_REGEX = re.compile(r"\b(" + "|".join(BOR_TERMS) + r")\b", re.IGNORECASE)

def classify_candidate(sentence: str) -> Dict | None:
    """
    Klassar meningar i SKALL / BÖR / IGNORE (information).
    """
    skall_matches = SKALL_REGEX.findall(sentence)
    bor_matches = BOR_REGEX.findall(sentence)

    if skall_matches:
        return {
            "rule_hint": "SKALL",
            "matched_terms": list(set(m.lower() for m in skall_matches))
        }

    if bor_matches:
        return {
            "rule_hint": "BÖR",
            "matched_terms": list(set(m.lower() for m in bor_matches))
        }

    return None  # Information → ignoreras


def extract_requirement_candidates(pages: List[Dict]) -> List[Dict]:
    candidates = []

    for page in pages:
        for para in page["paragraphs"]:
            result = classify_candidate(para["text"])
            if not result:
                continue

            candidates.append({
                "id": para["id"],
                "page": page["page"],
                "text": para["text"],
                "rule_hint": result["rule_hint"],
                "matched_terms": result["matched_terms"]
            })

    return candidates
