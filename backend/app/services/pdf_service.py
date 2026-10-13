import os
import re
from pathlib import Path
from typing import Union

try:
    import pymupdf as fitz  # Modern PyMuPDF import
except ImportError:
    import fitz  # type: ignore[import-not-found]


PAGE_NUMBER_PATTERN = re.compile(
    r"^\s*(?:page\s+)?(?:\d+|[ivxlcdm]+)(?:\s*(?:of|/|-)\s*(?:\d+|[ivxlcdm]+))?\.?\s*$",
    re.IGNORECASE,
)
STANDALONE_NUMBER_PATTERN = re.compile(r"^\s*[-—–]?\s*\d+\s*[-—–]?\s*$")


def _is_header_or_footer(
    y0: float,
    y1: float,
    page_height: float,
    text: str,
    header_margin_ratio: float = 0.08,
    footer_margin_ratio: float = 0.08,
) -> bool:
    """Detect if a text block is located in the header or footer zone and looks like header/footer content."""
    clean_text = text.strip()
    if not clean_text:
        return True

    # Check for standalone page numbers anywhere in block
    if PAGE_NUMBER_PATTERN.match(clean_text) or STANDALONE_NUMBER_PATTERN.match(clean_text):
        return True

    in_top_margin = y1 <= (page_height * header_margin_ratio) or y0 <= 40.0
    in_bottom_margin = y0 >= (page_height * (1.0 - footer_margin_ratio)) or y1 >= (page_height - 40.0)

    # In top or bottom margins, short text lines are typically running headers/footers
    if (in_top_margin or in_bottom_margin) and len(clean_text.splitlines()) <= 2:
        return True

    return False


def _clean_extracted_text(text: str) -> str:
    """Clean raw extracted text:

    - Strips isolated page number lines.
    - Normalizes horizontal whitespace.
    - Collapses repeated newlines and excessive whitespace.
    """
    lines = text.splitlines()
    cleaned_lines: list[str] = []

    for line in lines:
        stripped_line = line.strip()

        # Drop lines that are purely page numbers
        if PAGE_NUMBER_PATTERN.match(stripped_line) or STANDALONE_NUMBER_PATTERN.match(stripped_line):
            continue

        # Collapse repeated horizontal whitespace within the line
        normalized_line = re.sub(r"[^\S\r\n]+", " ", stripped_line)
        cleaned_lines.append(normalized_line)

    # Reassemble lines
    combined = "\n".join(cleaned_lines)

    # Collapse 3 or more consecutive newlines into double newlines (paragraph separator)
    combined = re.sub(r"\n{3,}", "\n\n", combined)

    # Collapse multiple spaces that might cross newlines or remnants
    combined = re.sub(r"[ \t]+", " ", combined)

    return combined.strip()


def extract_text(file_path: Union[str, Path]) -> str:
    """Extract raw text from a PDF file using PyMuPDF (fitz) and clean the output:

    - Strips headers, footers, and page numbers where detectable.
    - Collapses repeated whitespace and excessive newlines.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Cleaned text extracted from the PDF.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid PDF or is unreadable.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a regular file: {file_path}")

    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        raise ValueError(f"Failed to open PDF file '{file_path}': {exc}") from exc

    page_texts: list[str] = []

    try:
        for page in doc:
            page_height = page.rect.height
            blocks = page.get_text("blocks")
            # blocks: list of (x0, y0, x1, y1, "text", block_no, block_type)
            # block_type == 0 indicates text; 1 indicates image

            valid_blocks_text: list[str] = []
            for block in blocks:
                if len(block) >= 5:
                    x0, y0, x1, y1, text = block[0], block[1], block[2], block[3], block[4]
                    block_type = block[6] if len(block) > 6 else 0

                    if block_type != 0:
                        continue

                    if _is_header_or_footer(y0, y1, page_height, text):
                        continue

                    valid_blocks_text.append(text)

            if valid_blocks_text:
                page_texts.append("\n\n".join(valid_blocks_text))
    finally:
        doc.close()

    raw_text = "\n\n".join(page_texts)
    return _clean_extracted_text(raw_text)
