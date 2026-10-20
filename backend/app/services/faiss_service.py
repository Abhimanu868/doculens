"""FAISS vector index service for semantic search over document chunks."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import faiss
import numpy as np

from ..utils.config import DATA_DIR

logger = logging.getLogger(__name__)

# Default persistence directory
_DEFAULT_INDEX_DIR = DATA_DIR / "faiss_index"


class FAISSService:
    """Manages a FAISS vector index for document embeddings.

    Uses IndexFlatIP (inner-product on L2-normalized vectors ≡ cosine similarity)
    wrapped in IndexIDMap so we can assign and track our own integer IDs.

    Metadata (doc_id, chunk_index, chunk text) is kept in a parallel dict
    keyed by the same integer ID and persisted as JSON alongside the index.
    """

    def __init__(
        self,
        dimension: int = 384,
        index_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        self.dimension = dimension
        self.index_dir = Path(index_dir) if index_dir else _DEFAULT_INDEX_DIR
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self._index_path = self.index_dir / "index.faiss"
        self._meta_path = self.index_dir / "metadata.json"

        # Internal state
        self._metadata: Dict[int, Dict[str, Any]] = {}
        self._next_id: int = 0

        # Build or load index
        if self._index_path.exists() and self._meta_path.exists():
            self._load()
        else:
            base = faiss.IndexFlatIP(dimension)
            self._index = faiss.IndexIDMap(base)
            logger.info("Created new FAISS index (dim=%d)", dimension)

    # ── Public API ──────────────────────────────────────────────

    @property
    def total_vectors(self) -> int:
        return self._index.ntotal

    def add_document(
        self,
        doc_id: str,
        chunks: List[str],
        embeddings: np.ndarray,
    ) -> List[int]:
        """Add a document's chunks and their embeddings to the index.

        Args:
            doc_id: Unique document identifier.
            chunks: List of text chunks (sentences / paragraphs).
            embeddings: 2-D float32 array of shape (len(chunks), dimension).

        Returns:
            List of FAISS integer IDs assigned to each chunk.
        """
        if embeddings.ndim != 2 or embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Expected embeddings of shape (n, {self.dimension}), "
                f"got {embeddings.shape}"
            )
        if len(chunks) != embeddings.shape[0]:
            raise ValueError(
                f"chunks length ({len(chunks)}) != embeddings rows ({embeddings.shape[0]})"
            )

        # L2-normalize so inner-product == cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normed = (embeddings / norms).astype(np.float32)

        ids = np.arange(self._next_id, self._next_id + len(chunks), dtype=np.int64)
        self._index.add_with_ids(normed, ids)

        for i, fid in enumerate(ids):
            self._metadata[int(fid)] = {
                "doc_id": doc_id,
                "chunk_index": i,
                "text": chunks[i],
            }

        self._next_id += len(chunks)
        self.save()

        logger.info(
            "Indexed %d chunks for document '%s' (total vectors: %d)",
            len(chunks),
            doc_id,
            self.total_vectors,
        )
        return ids.tolist()

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        doc_id_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search the index for the most similar chunks.

        Args:
            query_embedding: 1-D or 2-D float32 query vector.
            top_k: Number of results to return.
            doc_id_filter: Optional — restrict results to a specific document.

        Returns:
            List of dicts with keys: faiss_id, doc_id, chunk_index, text, score.
        """
        if self.total_vectors == 0:
            return []

        qvec = np.asarray(query_embedding, dtype=np.float32)
        if qvec.ndim == 1:
            qvec = qvec.reshape(1, -1)

        # L2-normalize query
        norm = np.linalg.norm(qvec)
        if norm > 0:
            qvec = qvec / norm

        # Avoid FAISS's OpenMP search runtime, which conflicts with PyTorch's on macOS.
        ids = faiss.vector_to_array(self._index.id_map)
        flat_index = faiss.downcast_index(self._index.index)
        vectors = np.stack(
            [flat_index.reconstruct(position) for position in range(self.total_vectors)]
        )
        scores = vectors @ qvec[0]

        ranked_results: List[Tuple[float, Dict[str, Any]]] = []
        for position, fid in enumerate(ids):
            meta = self._metadata.get(int(fid))
            if meta is None or (doc_id_filter and meta["doc_id"] != doc_id_filter):
                continue
            ranked_results.append(
                (
                    float(scores[position]),
                    {
                        "faiss_id": int(fid),
                        "doc_id": meta["doc_id"],
                        "chunk_index": meta["chunk_index"],
                        "text": meta["text"],
                        "score": round(float(scores[position]), 4),
                    },
                )
            )

        ranked_results.sort(key=lambda result: result[0], reverse=True)
        return [result for _, result in ranked_results[:top_k]]

    def remove_document(self, doc_id: str) -> int:
        """Remove all chunks belonging to a document from the index.

        Rebuilds the index without the removed vectors.

        Returns:
            Number of vectors removed.
        """
        ids_to_remove = [
            fid for fid, meta in self._metadata.items() if meta["doc_id"] == doc_id
        ]
        if not ids_to_remove:
            return 0

        stored_ids = faiss.vector_to_array(self._index.id_map)
        flat_index = faiss.downcast_index(self._index.index)
        kept_ids = []
        kept_vectors = []
        for position, fid in enumerate(stored_ids):
            if int(fid) in ids_to_remove:
                continue
            kept_ids.append(int(fid))
            kept_vectors.append(flat_index.reconstruct(position))

        self._index = faiss.IndexIDMap(faiss.IndexFlatIP(self.dimension))
        if kept_ids:
            self._index.add_with_ids(
                np.asarray(kept_vectors, dtype=np.float32),
                np.asarray(kept_ids, dtype=np.int64),
            )

        for fid in ids_to_remove:
            del self._metadata[fid]

        self.save()
        logger.info(
            "Removed %d vectors for document '%s' (total vectors: %d)",
            len(ids_to_remove),
            doc_id,
            self.total_vectors,
        )
        return len(ids_to_remove)

    def get_document_ids(self) -> List[str]:
        """Return unique document IDs currently in the index."""
        return list({meta["doc_id"] for meta in self._metadata.values()})

    # ── Persistence ─────────────────────────────────────────────

    def save(self) -> None:
        """Persist index and metadata to disk."""
        faiss.write_index(self._index, str(self._index_path))
        serializable_meta = {str(k): v for k, v in self._metadata.items()}
        self._meta_path.write_text(
            json.dumps(
                {"next_id": self._next_id, "entries": serializable_meta},
                ensure_ascii=False,
            )
        )

    def _load(self) -> None:
        """Load index and metadata from disk."""
        self._index = faiss.read_index(str(self._index_path))
        raw = json.loads(self._meta_path.read_text())
        self._next_id = raw.get("next_id", 0)
        self._metadata = {int(k): v for k, v in raw.get("entries", {}).items()}
        logger.info(
            "Loaded FAISS index with %d vectors from %s",
            self.total_vectors,
            self.index_dir,
        )


# ── Module-level singleton ──────────────────────────────────────

_faiss_service: Optional[FAISSService] = None


def get_faiss_service(dimension: int = 384) -> FAISSService:
    """Return the module-level FAISSService singleton."""
    global _faiss_service
    if _faiss_service is None:
        _faiss_service = FAISSService(dimension=dimension)
    return _faiss_service
