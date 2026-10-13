"""Helper script to create sample PDF documents for testing the ingestion pipeline."""

from pathlib import Path
try:
    import pymupdf as fitz
except ImportError:
    import fitz  # type: ignore[import-not-found]


def create_sample_pdf(file_path: Path, title: str, paragraphs: list[str]) -> Path:
    """Create a multi-page PDF with headers, footers, page numbers, and body text."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()

    for page_idx, para in enumerate(paragraphs, start=1):
        page = doc.new_page(width=595, height=842)  # A4 size

        # Running Header (top margin: y ~ 25)
        page.insert_text(
            fitz.Point(50, 30),
            f"DOCULENS SAMPLE ARCHIVE | {title.upper()}",
            fontsize=8,
            color=(0.4, 0.4, 0.4),
        )

        # Body Title and Content (margin: y ~ 80..700)
        page.insert_text(
            fitz.Point(50, 90),
            f"Section {page_idx}: {title}",
            fontsize=14,
            color=(0.1, 0.1, 0.1),
        )

        # Body paragraph with intentional messy spacing to test collapsing
        body_text = (
            f"{para}\n\n"
            "This document establishes the official specifications and contractual requirements.   "
            "All authorized personnel must adhere strictly to these operational guidelines. "
            "Failure to comply may result in audit findings and security reviews."
        )
        rect = fitz.Rect(50, 120, 545, 750)
        page.insert_textbox(rect, body_text, fontsize=11, color=(0.15, 0.15, 0.15))

        # Running Footer & Page Number (bottom margin: y ~ 815)
        page.insert_text(
            fitz.Point(50, 815),
            "Confidential & Proprietary - All Rights Reserved",
            fontsize=8,
            color=(0.4, 0.4, 0.4),
        )
        page.insert_text(
            fitz.Point(500, 815),
            f"Page {page_idx} of {len(paragraphs)}",
            fontsize=8,
            color=(0.4, 0.4, 0.4),
        )

    doc.save(str(file_path))
    doc.close()
    return file_path


def generate_test_pdfs(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf1_path = output_dir / "sample_contract.pdf"
    create_sample_pdf(
        pdf1_path,
        "Software License Agreement",
        [
            "The vendor grants the licensee a non-exclusive license to utilize the document intelligence platform. "
            "The licensee agrees to maintain confidential records and protect intellectual property rights. "
            "Short. "  # under 4 words, should be filtered by text_service!
            "12345. "  # numeric noise, should be filtered!
            "Annual maintenance and support subscriptions shall renew automatically unless terminated with sixty days prior notice.",
            "Payment schedules shall be settled on a net thirty basis following invoice issuance. "
            "Late payments are subject to a statutory interest charge calculated on the overdue balance. "
            "Liability limitations shall strictly apply to indirect damages or incidental operational losses.",
        ],
    )

    pdf2_path = output_dir / "sample_technical_spec.pdf"
    create_sample_pdf(
        pdf2_path,
        "System Architecture Specification",
        [
            "The ingestion subsystem parses multi-page documents and converts raw streams into clean text blocks. "
            "Natural language processing pipelines split documents into discrete syntactic sentences for analysis. "
            "Dense vector embeddings capture rich semantic relationships across high-dimensional latent space.",
            "Distributed vector indexing accelerates approximate nearest neighbor retrieval across massive corpora. "
            "Cross-encoder re-ranking models compute precise relevance scores to eliminate hallucinations. "
            "High availability clusters ensure sub-second response latency for enterprise compliance auditing.",
        ],
    )

    return pdf1_path, pdf2_path


if __name__ == "__main__":
    p1, p2 = generate_test_pdfs(Path("data/sample_docs"))
    print(f"Generated sample PDFs: {p1} and {p2}")
