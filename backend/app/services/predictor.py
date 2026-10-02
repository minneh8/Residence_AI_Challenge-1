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

    @staticmethod
    def _is_svm_bundle(model: Any) -> bool:
        return isinstance(model, dict) and all(key in model for key in ('model', 'scaler', 'tfidf', 'feature_names'))

    def _svm_frame(self, text: str, features: dict[str, float], bundle: dict) -> pd.DataFrame:
        numeric_names = bundle.get('numeric_features') or [name for name in bundle['feature_names'] if not name.startswith('tfidf_')]
        tfidf_names = bundle.get('tfidf_features') or [name for name in bundle['feature_names'] if name.startswith('tfidf_')]
        numeric_values = [[features[name] for name in numeric_names]]
        numeric_scaled = bundle['scaler'].transform(numeric_values)
        numeric_df = pd.DataFrame(numeric_scaled, columns=numeric_names)
        tfidf_values = bundle['tfidf'].transform([text]).toarray()
        tfidf_df = pd.DataFrame(tfidf_values, columns=tfidf_names)
        frame = pd.concat([numeric_df, tfidf_df], axis=1)
        return frame[bundle['feature_names']]

    @staticmethod
    def _prediction(model: Any, frame: pd.DataFrame) -> int:
        if not hasattr(model, 'predict'):
            raise ValueError('O pipeline não possui predict.')
        return int(model.predict(frame)[0])

    @staticmethod
    def _probabilities(model: Any, frame: pd.DataFrame):
        if not hasattr(model, 'predict_proba'):
            return None, None
        probabilities = model.predict_proba(frame)[0]
        classes = list(model.classes_)
        return (
            float(probabilities[classes.index(0)]) if 0 in classes else None,
            float(probabilities[classes.index(1)]) if 1 in classes else None,
        )

    def predict(self, text: str, pipeline: str, supplied: Optional[dict[str, float]] = None) -> dict:
        canonical = self.registry.canonical(pipeline)
        model = self.registry.get(pipeline)
        features = self._features(text, supplied)

        if canonical == 'svm':
            if not self._is_svm_bundle(model):
                raise ValueError('svm_bundle.joblib não possui o formato de bundle esperado.')
            frame = self._svm_frame(text, features, model)
            estimator = model['model']
            label = self._prediction(estimator, frame)
            fake, true = self._probabilities(estimator, frame)
            return {
                'pipeline': pipeline,
                'label': label,
                'classification': 'fake' if label == 0 else 'true',
                'fake_probability': fake,
                'true_probability': true,
                'confidence': max(fake, true) if fake is not None and true is not None else None,
                'features': features,
                'explanation': ['SVM executado com scaler e embedding TF-IDF do bundle.'],
                'model_loaded': True,
                'details': {'feature_count': len(model['feature_names'])},
            }

        if canonical == 'pipeline_kmeans_duat':
            label = self._prediction(model, pd.DataFrame([features]))
            return {
                'pipeline': pipeline,
                'label': label,
                'classification': f'cluster_{label}',
                'fake_probability': None,
                'true_probability': None,
                'confidence': None,
                'features': features,
                'explanation': ['K-Means executado; o rótulo representa o cluster identificado.'],
                'model_loaded': True,
                'details': {'cluster': label},
            }

        if canonical == 'duat_dbscan_isolation_forest':
            return self.combined(text, pipeline, features)

        raise ValueError(f'Pipeline desconhecido: {pipeline}')

    def combined(self, text: str, pipeline: str, features: dict[str, float]) -> dict:
        model = self.registry.get('duat_dbscan_isolation_forest')
        dbscan = self._find(model, ('dbscan', 'DBSCAN', 'clusterer', 'clustering', 'modelo_dbscan'))
        isolation = self._find(model, ('isolation_forest', 'isolation', 'forest', 'modelo_isolation_forest'))
        if dbscan is None or isolation is None:
            raise ValueError('O artefato combinado precisa expor DBSCAN e Isolation Forest.')

        frame = pd.DataFrame([features])
        cluster = int(dbscan.predict(frame)[0])
        isolation_prediction = int(isolation.predict(frame)[0])
        score = float(isolation.decision_function(frame)[0]) if hasattr(isolation, 'decision_function') else None
        anomaly = cluster == -1 or isolation_prediction == -1
        return {
            'pipeline': pipeline,
            'label': None,
            'classification': 'anomaly' if anomaly else 'normal',
            'fake_probability': None,
            'true_probability': None,
            'confidence': None,
            'features': features,
            'explanation': ['DBSCAN e Isolation Forest executados juntos.'],
            'model_loaded': True,
            'details': {
                'dbscan': {'cluster': cluster, 'anomaly': cluster == -1},
                'isolation_forest': {'prediction': isolation_prediction, 'anomaly': isolation_prediction == -1, 'score': score},
            },
        }

    def anomaly(self, text: str, pipeline: str, supplied: Optional[dict[str, float]] = None) -> dict:
        features = self._features(text, supplied)
        result = self.combined(text, pipeline, features)
        details = result['details']
        return {
            'pipeline': pipeline,
            'anomaly': result['classification'] == 'anomaly',
            'score': details['isolation_forest']['score'],
            'cluster': details['dbscan']['cluster'],
            'features': features,
            'model_loaded': True,
            'details': details,
        }
