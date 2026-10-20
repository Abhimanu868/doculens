import numpy as np
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api import upload as upload_api


class FakeQuery:
    def order_by(self, *args):
        return self

    def all(self):
        return []


class FakeDatabase:
    def __init__(self):
        self.documents = []

    def add(self, document):
        self.documents.append(document)

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

    def query(self, model):
        return FakeQuery()


class FakeEmbeddingService:
    embedding_dimension = 2

    def embed(self, sentences):
        return np.array([[1.0, 0.0]], dtype=np.float32)


class FakeFAISSService:
    total_vectors = 1

    def add_document(self, doc_id, sentences, embeddings):
        pass


def _client():
    app = FastAPI()
    app.include_router(upload_api.router)
    app.state.embedding_service = FakeEmbeddingService()
    return TestClient(app)


def test_upload_rejects_non_pdf(monkeypatch, tmp_path):
    monkeypatch.setattr(upload_api, "_UPLOAD_DIR", tmp_path)

    with _client() as client:
        response = client.post(
            "/api/upload",
            files={"file": ("notes.txt", b"not a pdf", "text/plain")},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "Only PDF files are supported."}


def test_upload_rejects_file_over_configured_limit(monkeypatch, tmp_path):
    monkeypatch.setattr(upload_api, "_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(upload_api, "MAX_UPLOAD_MB", 1)
    monkeypatch.setattr(upload_api, "SessionLocal", FakeDatabase)
    pdf_bytes = b"%PDF-" + (b"x" * (1024 * 1024))

    with _client() as client:
        response = client.post(
            "/api/upload",
            files={"file": ("large.pdf", pdf_bytes, "application/pdf")},
        )

    assert response.status_code == 413
    assert response.json() == {"detail": "PDF exceeds the 1 MB upload limit."}
    assert list(tmp_path.iterdir()) == []


def test_upload_removes_temporary_pdf_after_extraction(monkeypatch, tmp_path):
    monkeypatch.setattr(upload_api, "_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(upload_api, "SessionLocal", FakeDatabase)
    monkeypatch.setattr(upload_api, "split_sentences", lambda text: [text])
    monkeypatch.setattr(upload_api, "get_faiss_service", lambda dimension: FakeFAISSService())
    extracted_paths = []

    def extract_text(path):
        assert path.exists()
        extracted_paths.append(path)
        return "This sentence has enough words for upload tests."

    monkeypatch.setattr(upload_api, "extract_text", extract_text)

    with _client() as client:
        response = client.post(
            "/api/upload",
            files={"file": ("sample.pdf", b"%PDF- sample content", "application/pdf")},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert len(extracted_paths) == 1
    assert not extracted_paths[0].exists()
    assert list(tmp_path.iterdir()) == []
