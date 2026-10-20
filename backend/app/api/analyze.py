"""NLI analysis endpoint — run premise/hypothesis inference."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ..models.nli_model import get_nli_model
from ..services.risk_service import assess_risk

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyze"])
NLI_BATCH_SIZE = 16


class NLIRequest(BaseModel):
    """Request body for NLI analysis."""
    premise: str = Field(..., min_length=1, description="The context or statement text.")
    hypothesis: str = Field(..., min_length=1, description="The claim to verify against the premise.")


class NLIBatchRequest(BaseModel):
    pairs: list[NLIRequest] = Field(..., min_length=1, max_length=64)


class NLIScore(BaseModel):
    entailment: float
    neutral: float
    contradiction: float


class NLIResponse(BaseModel):
    """Response body for NLI analysis."""
    label: str
    confidence: float
    scores: NLIScore
    premise: str
    hypothesis: str
    category: Optional[str] = None
    risk: Optional[str] = None


def _get_nli_model(request: Request):
    model = getattr(request.app.state, "nli_model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="NLI model is not ready.")
    return model


def _to_response(request: NLIRequest, result: dict) -> NLIResponse:
    risk_assessment = (
        assess_risk(request.premise, request.hypothesis, result["confidence"])
        if result["label"].lower() == "contradiction"
        else {}
    )
    return NLIResponse(
        label=result["label"],
        confidence=result["confidence"],
        scores=NLIScore(**result["scores"]),
        premise=request.premise,
        hypothesis=request.hypothesis,
        category=risk_assessment.get("category"),
        risk=risk_assessment.get("risk"),
    )


@router.post("/analyze", response_model=NLIResponse)
def analyze_nli(payload: NLIRequest, request: Request):
    """Run Natural Language Inference on a premise/hypothesis pair.

    Returns the predicted relationship (entailment / neutral / contradiction)
    along with per-class confidence scores.
    """
    try:
        return _to_response(payload, _get_nli_model(request).predict(payload.premise, payload.hypothesis))

    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        logger.exception("NLI analysis failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@router.post("/analyze/batch", response_model=list[NLIResponse])
def analyze_nli_batch(payload: NLIBatchRequest, request: Request):
    """Analyze multiple premise/hypothesis pairs in model batches of 16."""
    try:
        model = _get_nli_model(request)
        pairs = [(pair.premise, pair.hypothesis) for pair in payload.pairs]
        results = model.predict_batch(pairs, batch_size=NLI_BATCH_SIZE)
        return [
            _to_response(pair, result)
            for pair, result in zip(payload.pairs, results)
        ]
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        logger.exception("Batched NLI analysis failed")
        raise HTTPException(status_code=500, detail="Batch analysis failed.") from exc
