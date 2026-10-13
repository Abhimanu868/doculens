"""NLI analysis endpoint — run premise/hypothesis inference."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..models.nli_model import get_nli_model
from ..services.risk_service import assess_risk

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyze"])


class NLIRequest(BaseModel):
    """Request body for NLI analysis."""
    premise: str = Field(..., min_length=1, description="The context or statement text.")
    hypothesis: str = Field(..., min_length=1, description="The claim to verify against the premise.")


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


@router.post("/analyze", response_model=NLIResponse)
async def analyze_nli(request: NLIRequest):
    """Run Natural Language Inference on a premise/hypothesis pair.

    Returns the predicted relationship (entailment / neutral / contradiction)
    along with per-class confidence scores.
    """
    try:
        model = get_nli_model()
        result = model.predict(request.premise, request.hypothesis)
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

    except Exception as exc:
        logger.exception("NLI analysis failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
