"""Document management endpoints — list, get, and delete documents."""

import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.models import Document
from ..database.session import get_db
from ..services.faiss_service import get_faiss_service
from ..utils.config import DATA_DIR

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["documents"])

_UPLOAD_DIR = DATA_DIR / "uploads"


@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents with their metadata and processing status."""
    docs = db.query(Document).order_by(Document.upload_time.desc()).all()
    return {"documents": [doc.to_dict() for doc in docs], "total": len(docs)}


@router.get("/documents/{doc_id}")
def get_document(doc_id: str, db: Session = Depends(get_db)):
    """Get a single document's full details, including extracted text."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    result = doc.to_dict()
    # Include extracted text for detail view
    result["extracted_text"] = doc.extracted_text or ""
    return result


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Delete a document from the database, FAISS index, and filesystem."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    filename = doc.filename

    # Remove from FAISS index
    try:
        faiss_svc = get_faiss_service()
        removed_count = faiss_svc.remove_document(doc_id)
        logger.info("Removed %d vectors for doc '%s'", removed_count, doc_id)
    except Exception as exc:
        logger.warning("FAISS removal failed for doc '%s': %s", doc_id, exc)

    # Remove uploaded file
    for ext in (".pdf", ".docx"):
        fpath = _UPLOAD_DIR / f"{doc_id}{ext}"
        if fpath.exists():
            fpath.unlink()

    # Remove from database
    db.delete(doc)
    db.commit()

    logger.info("Deleted document '%s' (filename='%s')", doc_id, filename)
    return {"message": f"Document '{filename}' deleted successfully.", "id": doc_id}
