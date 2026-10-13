"""Examples for the rule-based contradiction risk prioritization layer."""

from backend.app.services.risk_service import assess_risk


def test_assess_risk_examples():
    examples = [
        (
            "The invoice must be paid within 30 days.",
            "No payment is due for this service.",
            0.91,
            {"category": "payment", "risk": "HIGH"},
        ),
        (
            "Submit the report before the deadline.",
            "The report is due next month.",
            0.75,
            {"category": "deadline", "risk": "MEDIUM"},
        ),
        (
            "Termination requires a notice period.",
            "The agreement may be terminated immediately.",
            0.60,
            {"category": "termination", "risk": "LOW"},
        ),
        (
            "Employee salary is paid monthly.",
            "No wage or compensation is provided.",
            0.85,
            {"category": "salary", "risk": "MEDIUM"},
        ),
        (
            "Confidential files require secure access.",
            "Private information may be shared publicly.",
            0.86,
            {"category": "security", "risk": "HIGH"},
        ),
    ]

    for sentence_a, sentence_b, confidence, expected in examples:
        assessment = assess_risk(sentence_a, sentence_b, confidence)
        print(f"{assessment} | confidence={confidence:.2f} | {sentence_a} / {sentence_b}")
        assert assessment == expected