from typing import Optional

import pandas as pd

from .feature_extractor import FEATURE_NAMES, extract_features
from .pipeline_registry import PipelineRegistry


class Predictor:
    def __init__(self):
        self.registry = PipelineRegistry()

    @property
    def model_loaded(self) -> bool:
        return bool(self.registry.available())

    def _features(self, text: str, supplied: Optional[dict[str, float]]) -> dict[str, float]:
        features = supplied or extract_features(text)
        missing = [name for name in FEATURE_NAMES if name not in features]
        if missing:
            raise ValueError(f'Features ausentes: {", ".join(missing)}')
        return {name: float(features[name]) for name in FEATURE_NAMES}

    def _frame(self, features: dict[str, float]) -> pd.DataFrame:
        return pd.DataFrame([[features[name] for name in FEATURE_NAMES]], columns=FEATURE_NAMES)

    def _fallback(self, features: dict[str, float]) -> tuple[int, float]:
        score = 0.5
        score += min(features['sensacionalismo_proporcao'] * 4.0, 0.2)
        score += min(features['emotividade'] * 0.2, 0.2)
        score -= min(features['fontes_proporcao'] * 0.5, 0.1)
        probability = min(max(score, 0.01), 0.99)
        return int(probability >= 0.5), float(probability)

    def predict(self, text: str, pipeline: str, supplied: Optional[dict[str, float]] = None) -> dict:
        features = self._features(text, supplied)
        model = self.registry.get(pipeline)
        if model is None:
            label, fake_probability = self._fallback(features)
            true_probability = 1.0 - fake_probability
            loaded = False
        else:
            frame = self._frame(features)
            label = int(model.predict(frame)[0])
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(frame)[0]
                classes = list(model.classes_)
                fake_probability = float(probabilities[classes.index(0)])
                true_probability = float(probabilities[classes.index(1)])
            else:
                fake_probability = None
                true_probability = None
            loaded = True

        confidence = None if fake_probability is None else max(fake_probability, true_probability)
        explanation = ['Resultado gerado pelo pipeline selecionado.']
        if not loaded:
            explanation.append('Pipeline ainda não carregado; foi usado o fallback de desenvolvimento.')

        return {
            'pipeline': pipeline,
            'label': label,
            'classification': 'fake' if label == 0 else 'true',
            'fake_probability': fake_probability,
            'true_probability': true_probability,
            'confidence': confidence,
            'features': features,
            'explanation': explanation,
            'model_loaded': loaded,
        }

    def anomaly(self, text: str, pipeline: str, supplied: Optional[dict[str, float]] = None) -> dict:
        features = self._features(text, supplied)
        model = self.registry.get(pipeline)
        frame = self._frame(features)
        if model is None:
            return {
                'pipeline': pipeline,
                'anomaly': False,
                'score': None,
                'cluster': None,
                'features': features,
                'model_loaded': False,
            }

        prediction = int(model.predict(frame)[0])
        score = float(model.decision_function(frame)[0]) if hasattr(model, 'decision_function') else None
        if pipeline == 'dbscan':
            anomaly = prediction == -1
            cluster = prediction
        else:
            anomaly = prediction == -1
            cluster = None

        return {
            'pipeline': pipeline,
            'anomaly': anomaly,
            'score': score,
            'cluster': cluster,
            'features': features,
            'model_loaded': True,
        }
