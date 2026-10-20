"""Environment-backed configuration for the DocuLens backend."""

import os
from pathlib import Path


def _positive_int(name: str, default: int) -> int:
	value = int(os.getenv(name, str(default)))
	if value < 1:
		raise ValueError(f"{name} must be greater than zero")
	return value


HF_MODEL_ID = os.getenv("HF_MODEL_ID", "Abhimanyu125047/doculens-nli")
HF_TOKEN = os.getenv("HF_TOKEN") or None
CORS_ORIGINS = [
	origin.strip().rstrip("/")
	for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
	if origin.strip()
]
MAX_UPLOAD_MB = _positive_int("MAX_UPLOAD_MB", 10)
NLI_CONFIDENCE_THRESHOLD = float(os.getenv("NLI_CONFIDENCE_THRESHOLD", "0.85"))
if not 0.0 <= NLI_CONFIDENCE_THRESHOLD <= 1.0:
	raise ValueError("NLI_CONFIDENCE_THRESHOLD must be between 0 and 1")
RETRIEVAL_TOP_K = _positive_int("RETRIEVAL_TOP_K", 5)
DATABASE_URL = os.getenv("DATABASE_URL") or None
DATA_DIR = Path(
	os.getenv("DATA_DIR", str(Path(__file__).resolve().parents[3] / "data"))
).expanduser()
MAX_STORED_DOCUMENTS = 20
