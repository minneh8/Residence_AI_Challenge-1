from typing import Any, Optional

import pandas as pd

from .feature_extractor import FEATURE_NAMES, extract_features
from .pipeline_registry import PipelineRegistry


class Predictor:
    def __init__(self):
        self.registry = PipelineRegistry()

    def _features(self, text: str, supplied: Optional[dict[str, float]]) -> dict[str, float]:
        features = supplied or extract_features(text)
        missing = [name for name in FEATURE_NAMES if name not in features]
        if missing:
            raise ValueError(f'Features ausentes: {", ".join(missing)}')
        return {name: float(features[name]) for name in FEATURE_NAMES}

    def _frame(self, features: dict[str, float]) -> pd.DataFrame:
        return pd.DataFrame([[features[name] for name in FEATURE_NAMES]], columns=FEATURE_NAMES)

    @staticmethod
    def _find(model: Any, names: tuple[str, ...]) -> Any:
        if isinstance(model, dict):
            for name in names:
                if name in model:
                    return model[name]
        for name in names:
            if hasattr(model, name):
                return getattr(model, name)
        return None

    def _combined_components(self, model: Any) -> tuple[Any, Any]:
        dbscan = self._find(model, ('dbscan', 'DBSCAN', 'clusterer', 'clustering', 'modelo_dbscan'))
        isolation = self._find(model, ('isolation_forest', 'isolation', 'forest', 'modelo_isolation_forest'))
        return dbscan, isolation

    @staticmethod
    def _predict(model: Any, frame: pd.DataFrame) -> Any:
        if not hasattr(model, 'predict'):
            raise ValueError('O artefato não possui o método predict.')
        return model.predict(frame)[0]

    def _fallback(self, features: dict[str, float]) -> tuple[int, float]:
        score = 0.5
        score += min(features['sensacionalismo_proporcao'] * 4.0, 0.2)
        score += min(features['emotividade'] * 0.2, 0.2)
        score -= min(features['fontes_proporcao'] * 0.5, 0.1)
        probability = min(max(score, 0.01), 0.99)
        return int(probability >= 0.5), float(probability)

    def predict(self, text: str, pipeline: str, supplied: Optional[dict[str, float]] = None) -> dict:
        features = self._features(text, supplied)
        canonical = self.registry.canonical(pipeline)
        model = self.registry.get(pipeline)
        if canonical == 'duat_dbscan_isolation_forest':
            return self.combined(text, pipeline, supplied)

        if model is None:
            label, fake_probability = self._fallback(features)
            true_probability = 1.0 - fake_probability
            loaded = False
        else:
            frame = self._frame(features)
            label = int(self._predict(model, frame))
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
        return {
            'pipeline': pipeline,
            'label': label,
            'classification': 'fake' if label == 0 else 'true',
            'fake_probability': fake_probability,
            'true_probability': true_probability,
            'confidence': confidence,
            'features': features,
            'explanation': ['Resultado gerado pelo pipeline selecionado.'],
            'model_loaded': loaded,
            'details': None,
        }

    def combined(self, text: str, pipeline: str = 'duat_dbscan_isolation_forest', supplied: Optional[dict[str, float]] = None) -> dict:
        features = self._features(text, supplied)
        model = self.registry.get('duat_dbscan_isolation_forest')
        if model is None:
            return {
                'pipeline': pipeline, 'label': None, 'classification': 'unavailable',
                'fake_probability': None, 'true_probability': None, 'confidence': None,
                'features': features, 'explanation': ['Artefato combinado ainda não carregado.'],
                'model_loaded': False, 'details': None,
            }

        frame = self._frame(features)
        dbscan, isolation = self._combined_components(model)
        if dbscan is None or isolation is None:
            raise ValueError('O artefato precisa expor DBSCAN e Isolation Forest.')

        dbscan_label = int(self._predict(dbscan, frame))
        isolation_label = int(self._predict(isolation, frame))
        isolation_score = float(isolation.decision_function(frame)[0]) if hasattr(isolation, 'decision_function') else None
        details = {
            'dbscan': {'cluster': dbscan_label, 'anomaly': dbscan_label == -1},
            'isolation_forest': {'prediction': isolation_label, 'anomaly': isolation_label == -1, 'score': isolation_score},
        }
        anomaly = dbscan_label == -1 or isolation_label == -1
        return {
            'pipeline': pipeline, 'label': None,
            'classification': 'anomaly' if anomaly else 'normal',
            'fake_probability': None, 'true_probability': None, 'confidence': None,
            'features': features,
            'explanation': ['DBSCAN e Isolation Forest executados em conjunto.'],
            'model_loaded': True, 'details': details,
        }

    def anomaly(self, text: str, pipeline: str, supplied: Optional[dict[str, float]] = None) -> dict:
        canonical = self.registry.canonical(pipeline)
        if canonical == 'duat_dbscan_isolation_forest':
            combined = self.combined(text, pipeline, supplied)
            details = combined['details'] or {}
            dbscan = details.get('dbscan', {})
            isolation = details.get('isolation_forest', {})
            return {
                'pipeline': pipeline,
                'anomaly': combined['classification'] == 'anomaly',
                'score': isolation.get('score'),
                'cluster': dbscan.get('cluster'),
                'features': combined['features'],
                'model_loaded': combined['model_loaded'],
                'details': details,
            }
        return self.combined(text, pipeline, supplied)
