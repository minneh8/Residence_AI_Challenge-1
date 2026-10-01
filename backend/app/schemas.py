from typing import Dict, Optional

from pydantic import BaseModel, Field


class FeatureRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=200000)


class PredictionRequest(FeatureRequest):
    features: Optional[Dict[str, float]] = None


class PredictionResponse(BaseModel):
    label: int
    classification: str
    fake_probability: float
    true_probability: float
    confidence: float
    features: Dict[str, float]
    explanation: list[str]
    model_loaded: bool
