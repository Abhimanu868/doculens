"""Semantic search endpoint — query indexed documents via FAISS."""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.embedding_service import EmbeddingService
from ..services.faiss_service import get_faiss_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["search"])

_embedding_service: Optional[EmbeddingService] = None


def _get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


class SearchRequest(BaseModel):
    """Request body for semantic search."""
    query: str = Field(..., min_length=1, description="Natural-language search query.")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results to return.")
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
async def search_documents(request: SearchRequest):
    """Search indexed documents using semantic similarity.

    Embeds the query, searches the FAISS index, and returns the most similar
    document chunks ranked by cosine similarity score.
    """
    try:
        emb_service = _get_embedding_service()
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

    except Exception as exc:
        logger.exception("Search failed for query: %s", request.query)
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}") from exc
