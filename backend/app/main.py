from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import AnalysisRequest, AnalysisResponse
from .services.analysis_service import AnalysisService

app = FastAPI(title="DUAT API", version="2.0.3")

_default_origins = {
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5500",
    "null",
}
_extra_origins = {
    origin.strip().rstrip("/")
    for origin in os.getenv("DUAT_CORS_ORIGINS", "").split(",")
    if origin.strip()
}
_allowed_origins = sorted(_default_origins | _extra_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = AnalysisService()


@app.get("/health")
def health():
    return {"status": "ok", "service": "duat", "cors_origins": _allowed_origins}


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):
    try:
        return service.analyze(request.text, request.user_evaluation)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/features")
def features_legacy(request: AnalysisRequest):
    try:
        result = service.analyze(request.text, request.user_evaluation)
        return {
            "features": result["features"],
            "profile": result["profile"],
            "priority_criteria": result["priority_criteria"],
            "out_of_range_features": result["out_of_range_features"],
            "svm": result["svm"],
            "comparison": result["comparison"],
            "class_comparison": result["class_comparison"],
            "warnings": result["warnings"],
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
