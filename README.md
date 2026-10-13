# DocuLens

Intelligent document analysis and semantic search platform powered by modern NLP.

---

## Problem

Organizations drown in unstructured documents — PDFs, reports, contracts, research papers.
Finding specific information across thousands of pages is slow, error-prone, and often requires
domain expertise. Traditional keyword search misses context and nuance.

## Solution

**DocuLens** applies transformer-based NLP models to:

1. **Parse & extract** text and structure from diverse document formats (PDF, DOCX, etc.).
2. **Semantically index** content using sentence embeddings and FAISS for sub-second similarity search.
3. **Answer questions** over your document corpus with retrieval-augmented generation (RAG).
4. **Summarise & classify** documents automatically, surfacing key insights without manual review.

## Architecture

> _Placeholder — architecture diagram and detailed description coming in Phase 2._

```
┌────────────┐      ┌──────────────┐      ┌───────────────┐
│  Frontend   │◄────►│  FastAPI API  │◄────►│  PostgreSQL   │
│  (Next.js)  │      │  (Python 3.11)│      │  + FAISS idx  │
└────────────┘      └──────┬───────┘      └───────────────┘
                           │
                    ┌──────▼───────┐
                    │  ML Pipeline  │
                    │  transformers │
                    │  spaCy, etc.  │
                    └──────────────┘
```

## Model

The NLI model was fine-tuned on Google Colab (GPU) and is hosted on Hugging Face Hub at `Abhimanyu125047/doculens-nli` (configured via `HF_MODEL_ID`, e.g., `YOUR_USERNAME/doculens-nli`); the application loads it directly via the transformers library — no local training is required to run the app.

## Setup


### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional, for containerised dev)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**.  
Health check: `GET /health` → `{"status": "ok"}`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at **http://localhost:3000**.

### Docker Compose (full stack)

```bash
docker-compose up --build
```

## License

MIT
