"""Database engine and session management for DocuLens."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ..utils.config import DATA_DIR, DATABASE_URL as CONFIGURED_DATABASE_URL

DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = CONFIGURED_DATABASE_URL or f"sqlite:///{DATA_DIR / 'doculens.db'}"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=not DATABASE_URL.startswith("sqlite"),
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
