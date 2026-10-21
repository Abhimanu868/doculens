"""DocuLens Backend — FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import torch

from .api import analyze, documents, search, upload
from .database.session import init_db
from .models.nli_model import get_nli_model
from .services.embedding_service import EmbeddingService
from .services.faiss_service import get_faiss_service
from .services.text_service import get_spacy_nlp
from .utils.config import CORS_ORIGINS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DocuLens backend")
    torch.set_num_threads(1)
    try:
        init_db()
        logger.info("Database initialized")
        get_spacy_nlp()
        logger.info("spaCy model loaded")
        app.state.embedding_service = EmbeddingService()
        logger.info("Sentence-transformer model loaded")
        app.state.nli_model = get_nli_model()
        logger.info("NLI model loaded")
        get_faiss_service(dimension=app.state.embedding_service.embedding_dimension)
        logger.info("Models loaded")
    except Exception:
        logger.exception("Backend startup failed")
        raise

    yield


app = FastAPI(
    title="DocuLens API",
    description="Intelligent document analysis and search platform.",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(search.router)
app.include_router(documents.router)


@app.get("/")
async def root():
    return {"service": "DocuLens API", "status": "ok", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok"}
