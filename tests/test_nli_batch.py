from types import SimpleNamespace
from threading import Lock

import torch

from backend.app.models.nli_model import NLIModel


class FakeTokenizer:
    def __call__(self, premises, hypotheses, **kwargs):
        return {"input_ids": torch.ones((len(premises), 2), dtype=torch.long)}


class FakeModel:
    def __init__(self):
        self.batch_sizes = []

    def __call__(self, input_ids):
        assert torch.is_inference_mode_enabled()
        self.batch_sizes.append(input_ids.shape[0])
        logits = torch.tensor([[2.0, 0.0, 1.0]]).repeat(input_ids.shape[0], 1)
        return SimpleNamespace(logits=logits)


def test_predict_batch_uses_bounded_inference_mode_batches():
    model = object.__new__(NLIModel)
    model.tokenizer = FakeTokenizer()
    model.model = FakeModel()
    model.device = torch.device("cpu")
    model._inference_lock = Lock()
    model.id2label = {0: "entailment", 1: "neutral", 2: "contradiction"}
    pairs = [(f"premise {index}", f"hypothesis {index}") for index in range(17)]

    results = model.predict_batch(pairs)

    assert len(results) == 17
    assert model.model.batch_sizes == [16, 1]
    assert all(result["label"] == "entailment" for result in results)