"""Configuration settings for DocuLens backend."""
import os

# Hugging Face model repository ID for the fine-tuned NLI model.
# Can be overridden via the HF_MODEL_ID environment variable.
HF_MODEL_ID: str = os.getenv("HF_MODEL_ID", "Abhimanyu125047/doculens-nli")
