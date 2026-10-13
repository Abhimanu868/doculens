"""Document upload endpoint — accepts PDF files, processes and indexes them."""

import logging
import shutil
import uuid
from pathlib import Path

from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..database.models import Document
from ..database.session import SessionLocal
from ..services.embedding_service import EmbeddingService
from ..services.faiss_service import get_faiss_service
from ..services.pdf_service import extract_text
from ..services.text_service import split_sentences

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

_UPLOAD_DIR = Path(__file__).resolve().parents[3] / "data" / "uploads"
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Lazy-loaded singleton services
_embedding_service: Optional[EmbeddingService] = None


def _get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document for analysis.

    Steps:
    1. Save file to disk
    2. Extract text (PyMuPDF)
    3. Split into sentences (spaCy)
    4. Generate embeddings (SentenceTransformer)
    5. Index in FAISS
    6. Store metadata in database
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    # Basic validation
    allowed_extensions = {".pdf"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {allowed_extensions}",
        )

    doc_id = str(uuid.uuid4())
    save_path = _UPLOAD_DIR / f"{doc_id}{suffix}"
    db = SessionLocal()

    try:
        # 1. Save uploaded file
        with save_path.open("wb") as buf:
            shutil.copyfileobj(file.file, buf)

        file_size = save_path.stat().st_size

        # 2. Extract text
        raw_text = extract_text(save_path)
        if not raw_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract any text from the uploaded PDF.",
            )

        # 3. Sentence splitting
        sentences = split_sentences(raw_text)
        if not sentences:
            raise HTTPException(
                status_code=422,
                detail="No meaningful sentences found in the document.",
            )

        # 4. Generate embeddings
        emb_service = _get_embedding_service()
        embeddings = emb_service.embed(sentences)

        # 5. Index in FAISS
        faiss_svc = get_faiss_service(dimension=emb_service.embedding_dimension)
        faiss_svc.add_document(doc_id, sentences, embeddings)

        # 6. Store in database
        doc = Document(
            id=doc_id,
            filename=file.filename,
            content_type=file.content_type,
            status="ready",
            num_chunks=len(sentences),
            file_size_bytes=file_size,
            extracted_text=raw_text,
        )
        db.add(doc)
        db.commit()

        logger.info(
            "Uploaded '%s' → %d chunks indexed (doc_id=%s)",
            file.filename,
            len(sentences),
            doc_id,
        )

        return {
            "id": doc_id,
            "filename": file.filename,
            "status": "ready",
            "num_chunks": len(sentences),
            "file_size_bytes": file_size,
            "message": f"Successfully processed and indexed {len(sentences)} text chunks.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to process upload '%s'", file.filename)
        # Record failure in DB
        error_doc = Document(
            id=doc_id,
            filename=file.filename or "unknown",
            content_type=file.content_type,
            status="error",
            error_message=str(exc),
        )
        db.add(error_doc)
        db.commit()

        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}") from exc
    finally:
        db.close()
