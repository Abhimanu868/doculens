"""
NLI Model Inference Wrapper for DocuLens.

Loads a pre-trained / fine-tuned Sequence Classification model from Hugging Face Hub
and performs inference on premise/hypothesis pairs.
"""

import logging
from threading import Lock
from typing import Any, Dict, List, Optional, Sequence, Tuple

import torch
from huggingface_hub import try_to_load_from_cache
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from ..utils.config import HF_MODEL_ID, HF_TOKEN

logger = logging.getLogger(__name__)


class NLIModel:
    """
    Singleton inference wrapper for the DocuLens NLI model.

    Loads the tokenizer and model directly from Hugging Face Hub on first initialization.
    Subsequent calls reuse the existing instance in memory.
    """

    _instance: Optional["NLIModel"] = None

    def __new__(cls, *args, **kwargs) -> "NLIModel":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_id: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return

        self.model_id = model_id or HF_MODEL_ID
        self._inference_lock = Lock()

        # Select inference device: CUDA > MPS (Apple Silicon) > CPU
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        self._load_model()
        self._initialized = True

    def _load_model(self) -> None:
        """Download (if not cached) and load tokenizer and model from Hugging Face Hub."""
        # Check if model weights are already cached locally
        cached_safetensors = try_to_load_from_cache(
            repo_id=self.model_id, filename="model.safetensors"
        )
        cached_bin = try_to_load_from_cache(
            repo_id=self.model_id, filename="pytorch_model.bin"
        )

        if (
            (cached_safetensors is None or not isinstance(cached_safetensors, str))
            and (cached_bin is None or not isinstance(cached_bin, str))
        ):
            logger.info(
                "Downloading model from Hugging Face Hub, this may take a minute... (%s)",
                self.model_id,
            )
            print(
                f"Downloading model from Hugging Face Hub, this may take a minute... ({self.model_id})"
            )
        else:
            logger.info("Loading cached model from Hugging Face Hub (%s)...", self.model_id)

        auth = {"token": HF_TOKEN} if HF_TOKEN else {}
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, **auth)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_id, **auth
        )
        self.model.to(self.device)
        self.model.eval()

        # Parse model's own id2label mapping (dynamically extracted from config)
        raw_id2label = getattr(self.model.config, "id2label", None)
        if raw_id2label:
            self.id2label: Dict[int, str] = {
                int(idx): str(label).lower() for idx, label in raw_id2label.items()
            }
        else:
            # Fallback if id2label is missing
            self.id2label = {0: "entailment", 1: "neutral", 2: "contradiction"}

        logger.info(
            "NLI model successfully loaded on %s with id2label: %s",
            self.device,
            self.id2label,
        )

    def predict(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Run inference on a premise and hypothesis pair.

        Args:
            premise: Context or statement text.
            hypothesis: Proposed relationship or claim.

        Returns:
            dict: {
                "label": "contradiction" | "entailment" | "neutral",
                "confidence": float,
                "scores": {
                    "entailment": float,
                    "neutral": float,
                    "contradiction": float,
                }
            }
        """
        return self.predict_batch([(premise, hypothesis)])[0]

    def predict_batch(
        self,
        pairs: Sequence[Tuple[str, str]],
        batch_size: int = 16,
    ) -> List[Dict[str, Any]]:
        """Run NLI inference in bounded batches to limit peak CPU memory."""
        if not pairs:
            return []
        if batch_size < 1:
            raise ValueError("batch_size must be greater than zero")

        results: List[Dict[str, Any]] = []
        with self._inference_lock:
            for offset in range(0, len(pairs), batch_size):
                batch = pairs[offset : offset + batch_size]
                premises, hypotheses = zip(*batch)
                inputs = self.tokenizer(
                    list(premises),
                    list(hypotheses),
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding=True,
                )
                inputs = {key: value.to(self.device) for key, value in inputs.items()}

                with torch.inference_mode():
                    probabilities = torch.softmax(self.model(**inputs).logits, dim=-1)

                for row in probabilities:
                    scores: Dict[str, float] = {}
                    for idx, probability in enumerate(row.tolist()):
                        label_name = self.id2label.get(idx, f"label_{idx}").lower()
                        scores[label_name] = round(float(probability), 4)

                    pred_idx = int(torch.argmax(row).item())
                    pred_label = self.id2label.get(pred_idx, f"label_{pred_idx}").lower()
                    results.append(
                        {
                            "label": pred_label,
                            "confidence": round(float(row[pred_idx].item()), 4),
                            "scores": scores,
                        }
                    )

        return results


def get_nli_model(model_id: Optional[str] = None) -> NLIModel:
    """Helper to access the singleton NLIModel instance."""
    return NLIModel(model_id=model_id)
