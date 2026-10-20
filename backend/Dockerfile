FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm || echo "spaCy model download failed; runtime sentencizer fallback will be used"

ARG HF_MODEL_ID=Abhimanyu125047/doculens-nli
ENV HF_MODEL_ID=${HF_MODEL_ID} \
    HF_HOME=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence_transformers \
    DATA_DIR=/app/data

RUN --mount=type=secret,id=HF_TOKEN,required=false \
    if [ -f /run/secrets/HF_TOKEN ]; then export HF_TOKEN="$(cat /run/secrets/HF_TOKEN)"; fi && \
    python -c 'import os; from sentence_transformers import SentenceTransformer; from transformers import AutoModelForSequenceClassification, AutoTokenizer; token = os.getenv("HF_TOKEN"); auth = {"token": token} if token else {}; SentenceTransformer("all-MiniLM-L6-v2", device="cpu", **auth); model_id = os.environ["HF_MODEL_ID"]; AutoTokenizer.from_pretrained(model_id, **auth); AutoModelForSequenceClassification.from_pretrained(model_id, **auth)'

COPY app ./app

EXPOSE 8000

CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"