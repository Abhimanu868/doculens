"""Rule-based prioritization for NLI contradiction results.

This is a transparent keyword and confidence heuristic, not a trained model.
"""

from typing import Optional


CATEGORY_KEYWORDS = {
    "payment": ["payment", "invoice", "fee"],
    "deadline": ["deadline", "due date", "days"],
    "termination": ["termination", "terminate", "notice period"],
    "salary": ["salary", "compensation", "wage"],
    "security": ["security", "access", "confidential", "privacy"],
    "remote_work": ["remote", "work from home", "office"],
}


def assess_risk(sentence_a: str, sentence_b: str, confidence: float) -> dict:
    """Classify topic and priority using keyword matching and confidence rules.

    The category is the first configured category with a keyword in either
    sentence. Risk is assigned by fixed thresholds; no model is trained or
    called by this rule-based prioritization layer.
    """
    combined_text = f"{sentence_a} {sentence_b}".casefold()
    category: Optional[str] = None

    for candidate, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.casefold() in combined_text for keyword in keywords):
            category = candidate
            break

    if category is not None and confidence > 0.85:
        risk = "HIGH"
    elif category is not None and confidence > 0.6:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {"category": category, "risk": risk}