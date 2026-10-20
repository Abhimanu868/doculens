"""Semantic search endpoint — query indexed documents via FAISS."""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ..services.faiss_service import get_faiss_service
from ..utils.config import RETRIEVAL_TOP_K

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["search"])


class SearchRequest(BaseModel):
    """Request body for semantic search."""
    query: str = Field(..., min_length=1, description="Natural-language search query.")
    top_k: int = Field(default=RETRIEVAL_TOP_K, ge=1, le=50, description="Number of results to return.")
    doc_id: Optional[str] = Field(default=None, description="Restrict search to a specific document.")


class SearchResult(BaseModel):
    doc_id: str
    chunk_index: int
    text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int


@router.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest, http_request: Request):
    """Search indexed documents using semantic similarity.

    Embeds the query, searches the FAISS index, and returns the most similar
    document chunks ranked by cosine similarity score.
    """
    try:
        emb_service = getattr(http_request.app.state, "embedding_service", None)
        if emb_service is None:
            raise HTTPException(status_code=503, detail="Embedding model is not ready.")
        query_embedding = emb_service.embed([request.query])[0]

        faiss_svc = get_faiss_service(dimension=emb_service.embedding_dimension)
        results = faiss_svc.search(
            query_embedding,
            top_k=request.top_k,
            doc_id_filter=request.doc_id,
        )

        return SearchResponse(
            query=request.query,
            results=[
                SearchResult(
                    doc_id=r["doc_id"],
                    chunk_index=r["chunk_index"],
                    text=r["text"],
                    score=r["score"],
                )
                for r in results
            ],
            total=len(results),
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Search failed for query: %s", request.query)
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}") from exc
