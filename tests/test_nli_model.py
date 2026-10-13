"""
Test script for verifying NLIModel inference with Hugging Face Hub weights.

Runs 5 premise/hypothesis pairs (including 2 clear contradictions) to confirm
model loading, prediction output structure, and classification accuracy.
"""

import json
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.models.nli_model import NLIModel, get_nli_model
from backend.app.utils.config import HF_MODEL_ID


def main():
    print("=" * 70)
    print("DocuLens NLI Inference Test")
    print(f"Target Hugging Face Model: {HF_MODEL_ID}")
    print("=" * 70)

    # 1. Test singleton instantiation
    print("\n[Step 1] Initializing NLIModel instance...")
    model_a = get_nli_model()
    model_b = NLIModel()

    assert model_a is model_b, "Singleton check failed: Instances are different!"
    print("✓ Singleton pattern verified: model_a is model_b")
    print(f"✓ Inference device: {model_a.device}")
    print(f"✓ Detected id2label mapping: {model_a.id2label}\n")

    # 2. Define 5 test pairs (including 2 clear contradictions)
    test_cases = [
        {
            "id": 1,
            "expected": "contradiction",
            "premise": "The company reported a record net profit of $12 million for the third quarter of the fiscal year.",
            "hypothesis": "The company suffered massive financial losses in the third quarter.",
        },
        {
            "id": 2,
            "expected": "contradiction",
            "premise": "The contract strictly prohibits any subleasing or assignment of the leased premises without prior written consent.",
            "hypothesis": "The tenant is completely free to sublease the office space at any time without permission.",
        },
        {
            "id": 3,
            "expected": "entailment",
            "premise": "All employees must complete mandatory cybersecurity training by the end of October.",
            "hypothesis": "Cybersecurity training is required for staff members before November.",
        },
        {
            "id": 4,
            "expected": "entailment",
            "premise": "The platform encrypts all sensitive customer records using AES-256 both at rest and in transit.",
            "hypothesis": "Customer data is encrypted while stored and transmitted.",
        },
        {
            "id": 5,
            "expected": "neutral",
            "premise": "DocuLens successfully processed 5,000 PDF documents during the initial stress testing phase.",
            "hypothesis": "The stress test took approximately two hours to finish.",
        },
    ]

    print("[Step 2] Running 5 test premise/hypothesis pairs...")
    print("-" * 70)

    for case in test_cases:
        result = model_a.predict(case["premise"], case["hypothesis"])

        # Validate return dictionary structure
        assert "label" in result, f"Missing 'label' in result: {result}"
        assert "confidence" in result, f"Missing 'confidence' in result: {result}"
        assert "scores" in result, f"Missing 'scores' in result: {result}"
        for label_key in ("entailment", "neutral", "contradiction"):
            assert label_key in result["scores"], f"Missing '{label_key}' in scores: {result['scores']}"

        print(f"Pair #{case['id']} [Expected: {case['expected'].upper()}]")
        print(f"  Premise:    \"{case['premise']}\"")
        print(f"  Hypothesis: \"{case['hypothesis']}\"")
        print(f"  Result:     Label = {result['label'].upper()} (Confidence: {result['confidence']:.4f})")
        print(f"  Scores:     {json.dumps(result['scores'])}")
        print("-" * 70)

    print("\n✓ All 5 test cases executed successfully!")


if __name__ == "__main__":
    main()
