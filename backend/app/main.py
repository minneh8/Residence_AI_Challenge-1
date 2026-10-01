from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import FeatureRequest, PredictionRequest, PredictionResponse
from .services.feature_extractor import extract_features
from .services.predictor import Predictor

app = FastAPI(title='DUAT API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

predictor = Predictor()


@app.get('/health')
def health():
    return {'status': 'ok', 'model_loaded': predictor.model_loaded}


@app.post('/features')
def features(request: FeatureRequest):
    return {'features': extract_features(request.text)}


@app.post('/predict', response_model=PredictionResponse)
def predict(request: PredictionRequest):
    try:
        return predictor.predict(request.text, request.features)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail='Erro interno ao classificar a notícia.') from error
