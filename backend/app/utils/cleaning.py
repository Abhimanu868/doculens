"""Text and dataset cleaning utilities for DocuLens data pipeline."""

import re
from typing import Optional, Set
import pandas as pd


ALLOWED_LABELS: Set[str] = {"entailment", "neutral", "contradiction"}


def normalize_whitespace(text: Optional[str]) -> str:
    """Strip leading/trailing whitespace and collapse multiple whitespace/newlines."""
    if text is None or not isinstance(text, str):
        return ""
    # Replace non-breaking spaces, excessive spaces, tabs, newlines
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned


def clean_text_columns(df: pd.DataFrame, text_cols: list[str]) -> pd.DataFrame:
    """Normalize whitespace across specified text columns."""
    df_clean = df.copy()
    for col in text_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).apply(normalize_whitespace)
    return df_clean


def remove_nulls_and_duplicates(
    df: pd.DataFrame,
    subset: list[str],
    drop_empty_strings: bool = True
) -> pd.DataFrame:
    """Remove null records, empty strings, and duplicate pairs."""
    df_clean = df.dropna(subset=subset).copy()
    if drop_empty_strings:
        for col in subset:
            df_clean = df_clean[df_clean[col].str.strip() != ""]
    df_clean = df_clean.drop_duplicates(subset=subset)
    return df_clean


def validate_and_filter_labels(
    df: pd.DataFrame,
    label_col: str = "label",
    allowed_labels: Set[str] = ALLOWED_LABELS
) -> pd.DataFrame:
    """Ensure labels are lowercased and only valid NLI labels are retained."""
    df_clean = df.copy()
    df_clean[label_col] = df_clean[label_col].astype(str).str.strip().str.lower()
    df_clean = df_clean[df_clean[label_col].isin(allowed_labels)]
    return df_clean
