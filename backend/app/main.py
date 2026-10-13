"""DocuLens Backend — FastAPI Application."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import analyze, documents, search, upload
from .database.session import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

app = FastAPI(
    title="DocuLens API",
    description="Intelligent document analysis and search platform.",
    version="0.2.0",
)

# CORS — allow the Next.js frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(search.router)
app.include_router(documents.router)


@app.on_event("startup")
async def startup():
    """Initialize the database tables on server start."""
    init_db()


@app.get("/health")
async def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok"}
