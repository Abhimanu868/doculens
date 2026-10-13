"""Database engine and session management for DocuLens."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# Default SQLite database for local development.
# Set DATABASE_URL env var for PostgreSQL in production.
_DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "data" / "doculens.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_DEFAULT_DB_PATH}")

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    """FastAPI dependency — yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables (idempotent — safe to call on every startup)."""
    # Import models so Base.metadata knows about them
    from . import models as _models  # noqa: F401

    Base.metadata.create_all(bind=engine)
