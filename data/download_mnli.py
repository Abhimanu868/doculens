#!/usr/bin/env python3
"""Download the MNLI dataset from Hugging Face and save as CSV files.

Saves three splits (train / validation / test) into data/processed/
with columns: premise, hypothesis, label.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

LABEL_MAP = {0: "entailment", 1: "neutral", 2: "contradiction"}

# Mapping from HuggingFace split names → our filenames
SPLITS = {
    "train": "mnli_train.csv",
    "validation_matched": "mnli_validation.csv",
    "validation_mismatched": "mnli_test.csv",
}


def main() -> None:
    # Lazy imports so --help / IDE indexing stays fast
    import pandas as pd
    from datasets import load_dataset

    print("📥 Downloading MNLI dataset (nyu-mll/glue / mnli) from Hugging Face …")
    dataset = load_dataset("nyu-mll/glue", "mnli")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    for split_name, filename in SPLITS.items():
        split = dataset[split_name]
        df = pd.DataFrame(split)

        # Keep only the columns we need
        df = df[["premise", "hypothesis", "label"]]

        # Map integer labels → human-readable strings
        df["label"] = df["label"].map(LABEL_MAP)

        # Drop rows that didn't map (e.g. label == -1 in test splits)
        df = df.dropna(subset=["label"])

        out_path = OUTPUT_DIR / filename
        df.to_csv(out_path, index=False)

        counts = df["label"].value_counts().to_dict()
        print(f"  ✅ {split_name:30s} → {filename:25s}  {len(df):>7,} rows  {counts}")
        total += len(df)

    print(f"\n✨ Done — {total:,} total rows saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
