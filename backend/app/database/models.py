"""SQLAlchemy ORM models for DocuLens."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from .session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    """Represents an uploaded document and its processing state."""

    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(512), nullable=False)
    content_type = Column(String(128), nullable=True)
    upload_time = Column(DateTime(timezone=True), default=_utcnow)
    status = Column(String(32), default="processing")  # processing | ready | error
    num_pages = Column(Integer, default=0)
    num_chunks = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    extracted_text = Column(Text, default="")
    error_message = Column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "filename": self.filename,
            "content_type": self.content_type,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "status": self.status,
            "num_pages": self.num_pages,
            "num_chunks": self.num_chunks,
            "file_size_bytes": self.file_size_bytes,
            "error_message": self.error_message,
        }
