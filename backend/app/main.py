from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .schemas import AnalysisRequest, AnalysisResponse
from .services.analysis_service import AnalysisService

app = FastAPI(title="DUAT API", version="2.0.0")
service = AnalysisService()


@app.get("/health")
def health():
    return {"status": "ok", "service": "duat"}


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):
    try:
        return service.analyze(request.text, request.user_evaluation)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
