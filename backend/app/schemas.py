from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field

PipelineName = Literal[
    'svm', 'kmeans', 'dbscan', 'isolation_forest',
    'pipeline_kmeans_duat', 'duat_dbscan_isolation_forest',
]


class FeatureRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=200000)


class PredictionRequest(FeatureRequest):
    pipeline: PipelineName = 'svm'
    features: Optional[Dict[str, float]] = None


class PredictionResponse(BaseModel):
    pipeline: str
    label: Optional[int] = None
    classification: str
    fake_probability: Optional[float] = None
    true_probability: Optional[float] = None
    confidence: Optional[float] = None
    features: Dict[str, float]
    explanation: list[str]
    model_loaded: bool
    details: Optional[dict] = None


class AnomalyRequest(FeatureRequest):
    pipeline: Literal['dbscan', 'isolation_forest', 'duat_dbscan_isolation_forest'] = 'duat_dbscan_isolation_forest'
    features: Optional[Dict[str, float]] = None


class AnomalyResponse(BaseModel):
    pipeline: str
    anomaly: bool
    score: Optional[float] = None
    cluster: Optional[int] = None
    features: Dict[str, float]
    model_loaded: bool
    details: Optional[dict] = None
