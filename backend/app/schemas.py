from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

Evaluation = Literal["v", "f", "n"]

class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1)
    user_evaluation: Evaluation = "n"

class FeatureResult(BaseModel):
    name: str
    label: str
    raw_value: float
    scaled_value: float

class CriterionResult(BaseModel):
    name: str
    label: str
    importance: float
    score: float
    percentile: float
    status: str
    meaning: str

class SVMResult(BaseModel):
    prediction: Literal["falsa", "verdadeira"]
    label: Literal[0, 1]
    decision_distance: float
    confidence_level: Literal["baixa", "moderada", "alta"] | None

class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    word_count: int
    short_text_warning: bool
    profile: dict
    features: list[FeatureResult]
    priority_criteria: list[CriterionResult]
    out_of_range_features: list[str]
    svm: SVMResult
    comparison: dict
    class_comparison: list[dict]
    warnings: list[str]
