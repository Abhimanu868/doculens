import re
from typing import Optional

import spacy
from spacy.language import Language

_NLP_INSTANCE: Optional[Language] = None


def get_spacy_nlp() -> Language:
    """Get or initialize the cached spaCy language model."""
    global _NLP_INSTANCE
    if _NLP_INSTANCE is None:
        # Disable NER to maximize sentence segmentation throughput
        _NLP_INSTANCE = spacy.load("en_core_web_sm", disable=["ner"])
        # Ensure sentence boundaries are set if parser is enabled or sentencizer is added
        if not _NLP_INSTANCE.has_pipe("parser") and not _NLP_INSTANCE.has_pipe("sentencizer"):
            _NLP_INSTANCE.add_pipe("sentencizer")
    return _NLP_INSTANCE


def split_sentences(text: str, min_words: int = 4) -> list[str]:
    """Split text into sentences using spaCy (en_core_web_sm) and filter out short/noisy sentences.

    Args:
        text: Input text string to segment.
        min_words: Minimum number of words required for a valid sentence (default: 4).

    Returns:
        List of cleaned, high-quality sentence strings.
    """
    if not text or not text.strip():
        return []

    nlp = get_spacy_nlp()
    doc = nlp(text)

    valid_sentences: list[str] = []

    for sent in doc.sents:
        # Normalize whitespace in the sentence
        cleaned_sent = " ".join(sent.text.strip().split())
        if not cleaned_sent:
            continue

        # Extract meaningful word tokens (containing alphanumeric characters)
        words = [w for w in cleaned_sent.split() if any(c.isalnum() for c in w)]

        # Filter out sentences with fewer than `min_words`
        if len(words) < min_words:
            continue

        # Filter out noise: must contain at least one alphabetic character
        if not any(c.isalpha() for c in cleaned_sent):
            continue

        valid_sentences.append(cleaned_sent)

    return valid_sentences
