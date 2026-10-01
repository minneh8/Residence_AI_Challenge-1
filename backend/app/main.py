import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import AnomalyRequest, AnomalyResponse, FeatureRequest, PredictionRequest, PredictionResponse
from .services.feature_extractor import extract_features
from .services.predictor import Predictor

app = FastAPI(title='DUAT API', version='1.2.0')
origins = [origin.strip() for origin in os.getenv('DUAT_CORS_ORIGINS', '*').split(',') if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

predictor = Predictor()


@app.get('/health')
def health():
    return {'status': 'ok', 'pipelines': predictor.registry.status()}


@app.get('/pipelines')
def pipelines():
    return {
        'available': predictor.registry.available(),
        'supported': ['svm', 'kmeans', 'dbscan', 'isolation_forest'],
        'status': predictor.registry.status(),
    }


@app.post('/features')
def features(request: FeatureRequest):
    return {'features': extract_features(request.text)}


@app.post('/predict', response_model=PredictionResponse)
def predict(request: PredictionRequest):
    try:
        return predictor.predict(request.text, request.pipeline, request.features)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail='Erro interno ao classificar a notícia.') from error


@app.post('/anomaly', response_model=AnomalyResponse)
def anomaly(request: AnomalyRequest):
    try:
        return predictor.anomaly(request.text, request.pipeline, request.features)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail='Erro interno ao analisar anomalia.') from error
