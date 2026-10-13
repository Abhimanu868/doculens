"""
NLI Model Inference Wrapper for DocuLens.

Loads a pre-trained / fine-tuned Sequence Classification model from Hugging Face Hub
and performs inference on premise/hypothesis pairs.
"""

import logging
from typing import Any, Dict, Optional

import torch
from huggingface_hub import try_to_load_from_cache
from transformers import AutoModelForSequenceClassification, AutoTokenizer

try:
    from ..utils.config import HF_MODEL_ID
except ImportError:
    import os

    HF_MODEL_ID = os.getenv("HF_MODEL_ID", "Abhimanyu125047/doculens-nli")

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

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_id)
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
        inputs = self.tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)[0]

        scores: Dict[str, float] = {}
        for idx, prob in enumerate(probabilities.tolist()):
            label_name = self.id2label.get(idx, f"label_{idx}").lower()
            scores[label_name] = round(float(prob), 4)

        pred_idx = int(torch.argmax(probabilities).item())
        pred_label = self.id2label.get(pred_idx, f"label_{pred_idx}").lower()
        confidence = round(float(probabilities[pred_idx].item()), 4)

        return {
            "label": pred_label,
            "confidence": confidence,
            "scores": scores,
        }


def get_nli_model(model_id: Optional[str] = None) -> NLIModel:
    """Helper to access the singleton NLIModel instance."""
    return NLIModel(model_id=model_id)
