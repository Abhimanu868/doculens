import asyncio
from types import SimpleNamespace

from backend.app.api.search import SearchRequest, search_documents


class FakeEmbeddingService:
    embedding_dimension = 2

    def embed(self, texts):
        self.texts = texts
        return [[0.25, 0.75]]


class FakeFAISSService:
    def search(self, query_embedding, top_k, doc_id_filter):
        return [
            {
                "doc_id": "doc-1",
                "chunk_index": 0,
                "text": "A matching document sentence.",
                "score": 0.9,
            }
        ]


def test_search_reuses_startup_embedding_service(monkeypatch):
    embedding_service = FakeEmbeddingService()
    faiss_service = FakeFAISSService()
    http_request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(embedding_service=embedding_service)
        )
    )
    monkeypatch.setattr(
        "backend.app.api.search.get_faiss_service",
        lambda dimension: faiss_service,
    )

    response = asyncio.run(
        search_documents(SearchRequest(query="payment terms"), http_request)
    )

    assert embedding_service.texts == ["payment terms"]
    assert response.total == 1
    assert response.results[0].doc_id == "doc-1"