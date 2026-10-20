"""Document upload endpoint — accepts PDF files, processes and indexes them."""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from ..database.models import Document
from ..database.session import SessionLocal
from ..services.embedding_service import EmbeddingService
from ..services.faiss_service import get_faiss_service
from ..services.pdf_service import extract_text
from ..services.text_service import split_sentences
from ..utils.config import DATA_DIR, MAX_STORED_DOCUMENTS, MAX_UPLOAD_MB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

_UPLOAD_DIR = DATA_DIR / "uploads"
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _get_embedding_service(request: Request) -> EmbeddingService:
    service = getattr(request.app.state, "embedding_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="Embedding model is not ready.")
    return service


@router.post("/upload")
def upload_document(request: Request, file: UploadFile = File(...)):
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

    suffix = Path(file.filename).suffix.lower()
    if suffix != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    doc_id = str(uuid.uuid4())
    save_path = _UPLOAD_DIR / f"{doc_id}{suffix}"
    db = SessionLocal()

    try:
        logger.info("Upload received: filename=%s content_type=%s", file.filename, file.content_type)

        with save_path.open("wb") as buf:
            file_size = 0
            while chunk := file.file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > MAX_UPLOAD_MB * 1024 * 1024:
                    raise HTTPException(
                        status_code=413,
                        detail=f"PDF exceeds the {MAX_UPLOAD_MB} MB upload limit.",
                    )
                if file_size == len(chunk) and not chunk.startswith(b"%PDF-"):
                    raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF.")
                buf.write(chunk)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded PDF is empty.")
        logger.info("PDF saved to disk: path=%s size_bytes=%s", save_path, file_size)

        try:
            raw_text = extract_text(save_path)
        except Exception as exc:
            logger.exception("PDF extraction failed for '%s'", file.filename)
            raise HTTPException(status_code=422, detail="Could not extract text from this PDF.") from exc
        finally:
            save_path.unlink(missing_ok=True)
        logger.info("PyMuPDF extraction complete: characters=%d", len(raw_text))
        if not raw_text or not raw_text.strip():
            raise HTTPException(status_code=400, detail="No extractable text found in PDF")

        try:
            sentences = split_sentences(raw_text)
        except Exception as exc:
            logger.exception("Sentence splitting failed for '%s'", file.filename)
            raise HTTPException(status_code=500, detail="Could not segment the extracted PDF text.") from exc
        logger.info("Sentence splitting complete: sentence_count=%d", len(sentences))
        if not sentences:
            raise HTTPException(
                status_code=400,
                detail="No meaningful sentences found in the document.",
            )

        emb_service = _get_embedding_service(request)
        logger.info("Generating embeddings for %d sentences", len(sentences))
        try:
            embeddings = emb_service.embed(sentences)
        except Exception as exc:
            logger.exception("Embedding failed for '%s'", file.filename)
            raise HTTPException(status_code=503, detail="The embedding model could not process this PDF.") from exc
        logger.info("Embeddings complete: shape=%s", getattr(embeddings, "shape", None))

        try:
            faiss_svc = get_faiss_service(dimension=emb_service.embedding_dimension)
            faiss_svc.add_document(doc_id, sentences, embeddings)
        except Exception as exc:
            logger.exception("FAISS indexing failed for '%s'", file.filename)
            raise HTTPException(status_code=500, detail="Could not index the extracted PDF text.") from exc
        logger.info("FAISS index built: total_vectors=%d", faiss_svc.total_vectors)

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

        documents = db.query(Document).order_by(Document.upload_time.asc()).all()
        for old_doc in documents[:-MAX_STORED_DOCUMENTS]:
            faiss_svc.remove_document(old_doc.id)
            db.delete(old_doc)
        if len(documents) > MAX_STORED_DOCUMENTS:
            db.commit()

        response_payload = {
            "id": doc_id,
            "filename": file.filename,
            "status": "ready",
            "num_chunks": len(sentences),
            "file_size_bytes": file_size,
            "message": f"Successfully processed and indexed {len(sentences)} text chunks.",
        }
        logger.info("Upload response returned: id=%s num_chunks=%d", doc_id, len(sentences))
        return response_payload

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Upload pipeline failed for '%s'", file.filename)
        db.rollback()
        try:
            error_doc = Document(
                id=doc_id,
                filename=file.filename or "unknown",
                content_type=file.content_type,
                status="error",
                error_message=str(exc),
            )
            db.add(error_doc)
            db.commit()
        except Exception:
            logger.exception("Failed to persist upload error record for '%s'", file.filename)
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}") from exc
    finally:
        save_path.unlink(missing_ok=True)
        db.close()
