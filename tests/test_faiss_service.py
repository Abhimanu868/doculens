import numpy as np

from backend.app.services.faiss_service import FAISSService


def test_loaded_index_can_search(tmp_path):
    service = FAISSService(dimension=3, index_dir=tmp_path)
    service.add_document(
        "doc-1",
        ["matching chunk", "other chunk"],
        np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32),
    )

    restored_service = FAISSService(dimension=3, index_dir=tmp_path)
    results = restored_service.search(np.array([1.0, 0.0, 0.0]), top_k=1)

    assert len(results) == 1
    assert results[0]["text"] == "matching chunk"
    assert results[0]["score"] == 1.0