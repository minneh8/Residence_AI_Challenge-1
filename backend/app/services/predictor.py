from typing import Any, Optional

import pandas as pd

from .feature_extractor import FEATURE_NAMES, extract_features
from .pipeline_registry import PipelineRegistry


class Predictor:
    def __init__(self):
        self.registry = PipelineRegistry()

    def _features(self, text: str, supplied: Optional[dict[str, float]]) -> dict[str, float]:
        features = supplied or extract_features(text)
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

    @staticmethod
    def _is_svm_bundle(model: Any) -> bool:
        return isinstance(model, dict) and all(key in model for key in ('model', 'scaler', 'tfidf', 'feature_names'))

    def _bundle_frame(self, text: str, features: dict[str, float], bundle: dict) -> pd.DataFrame:
        numeric_names = bundle.get('numeric_features') or [name for name in bundle['feature_names'] if not name.startswith('tfidf_')]
        tfidf_names = bundle.get('tfidf_features') or [name for name in bundle['feature_names'] if name.startswith('tfidf_')]
        numeric_values = [[features[name] for name in numeric_names]]
        numeric_scaled = bundle['scaler'].transform(numeric_values)
        numeric_df = pd.DataFrame(numeric_scaled, columns=numeric_names)
        tfidf_matrix = bundle['tfidf'].transform([text]).toarray()
        tfidf_df = pd.DataFrame(tfidf_matrix, columns=tfidf_names)
        frame = pd.concat([numeric_df, tfidf_df], axis=1)
        return frame[bundle['feature_names']]

    @staticmethod
    def _predict(model: Any, frame: pd.DataFrame):
        if not hasattr(model, 'predict'):
            raise ValueError('O modelo SVM não possui predict.')
        return int(model.predict(frame)[0])

    @staticmethod
    def _probabilities(model: Any, frame: pd.DataFrame):
        if not hasattr(model, 'predict_proba'):
            return None, None
        probabilities = model.predict_proba(frame)[0]
        classes = list(model.classes_)
        fake = float(probabilities[classes.index(0)]) if 0 in classes else None
        true = float(probabilities[classes.index(1)]) if 1 in classes else None
        return fake, true

    def predict(self, text: str, pipeline: str, supplied: Optional[dict[str, float]] = None) -> dict:
        canonical = self.registry.canonical(pipeline)
        model = self.registry.get(pipeline)
        if canonical == 'svm' and self._is_svm_bundle(model):
            features = self._features(text, supplied)
            frame = self._bundle_frame(text, features, model)
            estimator = model['model']
            label = self._predict(estimator, frame)
            fake_probability, true_probability = self._probabilities(estimator, frame)
            confidence = None if fake_probability is None or true_probability is None else max(fake_probability, true_probability)
            return {
                'pipeline': pipeline,
                'label': label,
                'classification': 'fake' if label == 0 else 'true',
                'fake_probability': fake_probability,
                'true_probability': true_probability,
                'confidence': confidence,
                'features': features,
                'explanation': ['SVM executado com scaler e embedding TF-IDF do bundle.'],
                'model_loaded': True,
                'details': {'feature_count': len(model['feature_names']), 'tfidf_feature_count': len(model.get('tfidf_features', []))},
            }

        raise ValueError('Pipeline não suportado ou artefato incompatível com o formato esperado.')
