#!/usr/bin/env python3
"""Clean and combine datasets into final train, validation, and test splits.

Pipeline:
1. Loads raw domain dataset (data/raw/domain_pairs.csv) and MNLI splits (data/processed/mnli_*.csv).
2. Standardizes schema: premise, hypothesis, label.
3. Cleans: normalizes whitespace, removes duplicates & nulls, validates labels.
4. Splits domain dataset into train (60%), validation (20%), and test (20%).
5. Samples MNLI dataset and combines with domain data:
   - Domain data is weighted more heavily in validation and test sets (~44-50% domain).
6. Outputs final train.csv, validation.csv, and test.csv in data/processed/.
"""

import sys
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.utils.cleaning import (
    clean_text_columns,
    remove_nulls_and_duplicates,
    validate_and_filter_labels,
    ALLOWED_LABELS,
)

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

DOMAIN_RAW_FILE = RAW_DIR / "domain_pairs.csv"
MNLI_TRAIN_FILE = PROCESSED_DIR / "mnli_train.csv"
MNLI_VAL_FILE = PROCESSED_DIR / "mnli_validation.csv"
MNLI_TEST_FILE = PROCESSED_DIR / "mnli_test.csv"

OUTPUT_TRAIN_FILE = PROCESSED_DIR / "train.csv"
OUTPUT_VAL_FILE = PROCESSED_DIR / "validation.csv"
OUTPUT_TEST_FILE = PROCESSED_DIR / "test.csv"

# Configuration for MNLI sampling
MNLI_SAMPLE_TRAIN = 10000
MNLI_SAMPLE_VAL = 500
MNLI_SAMPLE_TEST = 500
RANDOM_STATE = 42


def clean_dataframe(df: pd.DataFrame, is_domain: bool = False) -> pd.DataFrame:
    """Clean and standardize dataframe columns."""
    df_clean = df.copy()
    if is_domain:
        # Standardize column names if sentence_a / sentence_b
        rename_dict = {}
        if "sentence_a" in df_clean.columns:
            rename_dict["sentence_a"] = "premise"
        if "sentence_b" in df_clean.columns:
            rename_dict["sentence_b"] = "hypothesis"
        df_clean = df_clean.rename(columns=rename_dict)

    required_cols = ["premise", "hypothesis", "label"]
    for col in required_cols:
        if col not in df_clean.columns:
            raise ValueError(f"Missing required column '{col}' in dataframe.")

    df_clean = clean_text_columns(df_clean, ["premise", "hypothesis"])
    df_clean = remove_nulls_and_duplicates(df_clean, ["premise", "hypothesis"])
    df_clean = validate_and_filter_labels(df_clean, "label", ALLOWED_LABELS)
    return df_clean[required_cols]


def sample_balanced_per_class(df: pd.DataFrame, target_total: int, random_state: int = RANDOM_STATE) -> pd.DataFrame:
    """Sample approximately target_total rows balanced equally across the 3 NLI classes."""
    target_per_class = target_total // 3
    sampled = [
        group.sample(n=min(len(group), target_per_class), random_state=random_state)
        for _, group in df.groupby("label")
    ]
    return pd.concat(sampled, ignore_index=True)


def main() -> None:
    print("🚀 Starting dataset cleaning & combination pipeline ...")

    # 1. Load and clean domain data
    if not DOMAIN_RAW_FILE.exists():
        raise FileNotFoundError(
            f"Domain dataset not found at {DOMAIN_RAW_FILE}. Please run data/generate_domain_data.py first."
        )

    domain_raw = pd.read_csv(DOMAIN_RAW_FILE)
    domain_clean = clean_dataframe(domain_raw, is_domain=True)
    domain_clean["source"] = "domain"
    print(f"Loaded and cleaned domain data: {len(domain_clean):,} pairs.")

    # Stratified split for domain data: 60% train, 20% val, 20% test
    train_domain, test_val_domain = train_test_split(
        domain_clean,
        test_size=0.40,
        random_state=RANDOM_STATE,
        stratify=domain_clean["label"],
    )
    val_domain, test_domain = train_test_split(
        test_val_domain,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=test_val_domain["label"],
    )

    print(f"Domain splits -> Train: {len(train_domain)}, Val: {len(val_domain)}, Test: {len(test_domain)}")

    # 2. Load and sample MNLI data
    if not (MNLI_TRAIN_FILE.exists() and MNLI_VAL_FILE.exists() and MNLI_TEST_FILE.exists()):
        raise FileNotFoundError(
            "MNLI files not found in data/processed/. Please run data/download_mnli.py first."
        )

    mnli_train = clean_dataframe(pd.read_csv(MNLI_TRAIN_FILE))
    mnli_val = clean_dataframe(pd.read_csv(MNLI_VAL_FILE))
    mnli_test = clean_dataframe(pd.read_csv(MNLI_TEST_FILE))

    # Balanced sampling from MNLI
    mnli_train_sampled = sample_balanced_per_class(mnli_train, MNLI_SAMPLE_TRAIN)
    mnli_train_sampled["source"] = "mnli"

    mnli_val_sampled = sample_balanced_per_class(mnli_val, MNLI_SAMPLE_VAL)
    mnli_val_sampled["source"] = "mnli"

    mnli_test_sampled = sample_balanced_per_class(mnli_test, MNLI_SAMPLE_TEST)
    mnli_test_sampled["source"] = "mnli"

    print(
        f"MNLI sampled -> Train: {len(mnli_train_sampled)}, Val: {len(mnli_val_sampled)}, Test: {len(mnli_test_sampled)}"
    )

    # 3. Combine splits
    final_train = pd.concat([mnli_train_sampled, train_domain], ignore_index=True)
    final_val = pd.concat([mnli_val_sampled, val_domain], ignore_index=True)
    final_test = pd.concat([mnli_test_sampled, test_domain], ignore_index=True)

    # Shuffle each split
    final_train = final_train.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    final_val = final_val.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    final_test = final_test.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    # Save to CSV
    final_train.to_csv(OUTPUT_TRAIN_FILE, index=False)
    final_val.to_csv(OUTPUT_VAL_FILE, index=False)
    final_test.to_csv(OUTPUT_TEST_FILE, index=False)

    print("\n=======================================================")
    print("✨ FINAL DATASET GENERATION SUMMARY")
    print("=======================================================")
    for split_name, split_df in [
        ("Train", final_train),
        ("Validation", final_val),
        ("Test", final_test),
    ]:
        total = len(split_df)
        label_counts = split_df["label"].value_counts().to_dict()
        source_counts = split_df["source"].value_counts().to_dict()
        domain_pct = (source_counts.get("domain", 0) / total) * 100 if total else 0
        print(f"\n📂 Split: {split_name} ({total:,} total examples)")
        print(f"   Labels: {label_counts}")
        print(f"   Sources: {source_counts} ({domain_pct:.1f}% domain)")

    print("\n✅ All files written successfully to data/processed/")


if __name__ == "__main__":
    main()
