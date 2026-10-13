"""Run the document ingestion services end to end."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.pdf_service import extract_text
from backend.app.services.text_service import split_sentences


FALLBACK_TEXT = [
    (
        "The document ingestion pipeline extracts text from source files. "
        "Sentence segmentation prepares readable units for semantic analysis."
    ),
    (
        "Sentence embeddings represent document meaning as dense vectors. "
        "Cosine similarity compares the resulting vectors across documents."
    ),
]


def _load_documents() -> list[tuple[str, str]]:
    """Load two generated PDFs when available, otherwise use sample paragraphs."""
    pdf_paths = sorted((PROJECT_ROOT / "data" / "sample_docs").glob("*.pdf"))[:2]
    if len(pdf_paths) == 2:
        return [(path.name, extract_text(path)) for path in pdf_paths]

    return [(f"fallback document {index}", text) for index, text in enumerate(FALLBACK_TEXT, 1)]


def main() -> None:
    documents = _load_documents()
    sentence_groups = [split_sentences(text) for _, text in documents]

    embedding_service = EmbeddingService()
    embeddings = [embedding_service.embed(sentences) for sentences in sentence_groups]

    for (name, _), sentences, document_embeddings in zip(
        documents, sentence_groups, embeddings
    ):
        print(f"{name}: {len(sentences)} sentences")
        print(f"  embedding shape: {document_embeddings.shape}")

    print(f"sample embedding shape: {embeddings[0][0].shape}")


if __name__ == "__main__":
    main()
