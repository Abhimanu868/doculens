from typing import Any, Optional, Sequence, Union
from threading import Lock

import numpy as np
from sentence_transformers import SentenceTransformer

from ..utils.config import HF_TOKEN


class EmbeddingService:
    """Service for generating sentence embeddings and computing vector similarities

    using SentenceTransformers (default: 'all-MiniLM-L6-v2').
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None,
    ) -> None:
        """Initialize the EmbeddingService and load the model into memory once.

        Args:
            model_name: HuggingFace model identifier or local model path.
            device: Optional device ('cpu', 'cuda', 'mps'). Defaults to auto-detection.
        """
        self.model_name = model_name
        self.device = device
        auth = {"token": HF_TOKEN} if HF_TOKEN else {}
        self.model = SentenceTransformer(model_name, device=device, **auth)
        self._dimension = self.model.get_sentence_embedding_dimension()
        self._inference_lock = Lock()

    @property
    def embedding_dimension(self) -> int:
        """Dimensionality of the generated embeddings."""
        return self._dimension

    def embed(self, sentences: list[str]) -> np.ndarray:
        """Generate dense vector embeddings for a list of sentences.

        Args:
            sentences: List of input sentence strings.

        Returns:
            np.ndarray: 2D numpy array of shape (num_sentences, embedding_dimension).
        """
        if not sentences:
            return np.empty((0, self._dimension), dtype=np.float32)

        with self._inference_lock:
            embeddings = self.model.encode(
                sentences,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        return np.asarray(embeddings, dtype=np.float32)

    @staticmethod
    def cosine_similarity(
        vec_a: Union[np.ndarray, Sequence[float]],
        vec_b: Union[np.ndarray, Sequence[float]],
    ) -> float:
        """Compute the cosine similarity between two 1D embedding vectors.

        Args:
            vec_a: First embedding vector.
            vec_b: Second embedding vector.

        Returns:
            Cosine similarity score as a float between -1.0 and 1.0.
        """
        a = np.asarray(vec_a, dtype=np.float32).flatten()
        b = np.asarray(vec_b, dtype=np.float32).flatten()

        if a.shape != b.shape:
            raise ValueError(
                f"Vectors must have the same dimension. Got {a.shape} and {b.shape}."
            )

        norm_a = float(np.linalg.norm(a))
        norm_b = float(np.linalg.norm(b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        similarity = float(np.dot(a, b) / (norm_a * norm_b))
        return float(np.clip(similarity, -1.0, 1.0))
