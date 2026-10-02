from typing import Any, Optional

import pandas as pd

from .feature_extractor import FEATURE_NAMES, extract_features
from .pipeline_registry import PipelineRegistry


class Predictor:
    def __init__(self):
        self.registry = PipelineRegistry()

    @staticmethod
    def validate_news_text(text: str) -> None:
        words = text.split()
        if len(words) < 40:
            raise ValueError('Texto curto demais para análise jornalística; use pelo menos 40 palavras.')
        if len(text) < 250:
            raise ValueError('Texto curto demais para análise jornalística; use pelo menos 250 caracteres.')

    def _features(self, text: str, supplied: Optional[dict[str, float]]) -> dict[str, float]:
        features = supplied or extract_features(text)
        missing = [name for name in FEATURE_NAMES if name not in features]
        if missing:
            raise ValueError(f'Features ausentes: {", ".join(missing)}')
        return {name: float(features[name]) for name in FEATURE_NAMES}

    @staticmethod
    def _is_svm_bundle(model: Any) -> bool:
        return isinstance(model, dict) and all(key in model for key in ('model', 'scaler', 'tfidf', 'feature_names'))

    def _svm_frame(self, text: str, features: dict[str, float], bundle: dict) -> pd.DataFrame:
        numeric_names = bundle.get('numeric_features') or [name for name in bundle['feature_names'] if not name.startswith('tfidf_')]
        tfidf_names = bundle.get('tfidf_features') or [name for name in bundle['feature_names'] if name.startswith('tfidf_')]
        numeric_df = pd.DataFrame(bundle['scaler'].transform([[features[name] for name in numeric_names]]), columns=numeric_names)
        tfidf_df = pd.DataFrame(bundle['tfidf'].transform([text]).toarray(), columns=tfidf_names)
        return pd.concat([numeric_df, tfidf_df], axis=1)[bundle['feature_names']]

    def predict(self, text: str, pipeline: str, supplied: Optional[dict[str, float]] = None) -> dict:
        self.validate_news_text(text)
        canonical = self.registry.canonical(pipeline)
        model = self.registry.get(pipeline)
        features = self._features(text, supplied)
        if canonical != 'svm':
            raise ValueError('Este endpoint de classificação está configurado para o bundle SVM. Use o endpoint específico do pipeline.')
        if not self._is_svm_bundle(model):
            raise ValueError('svm_bundle.joblib não possui o formato esperado.')

        frame = self._svm_frame(text, features, model)
        estimator = model['model']
        label = int(estimator.predict(frame)[0])
        fake, true = None, None
        if hasattr(estimator, 'predict_proba'):
            probabilities = estimator.predict_proba(frame)[0]
            classes = list(estimator.classes_)
            fake = float(probabilities[classes.index(0)]) if 0 in classes else None
            true = float(probabilities[classes.index(1)]) if 1 in classes else None
        score = float(estimator.decision_function(frame)[0]) if hasattr(estimator, 'decision_function') else None
        mapping = model.get('label_mapping', {'0': 'fake', '1': 'true'})
        classification = mapping.get(str(label), 'unknown')
        return {
            'pipeline': pipeline, 'label': label, 'classification': classification,
            'fake_probability': fake, 'true_probability': true,
            'confidence': max(fake, true) if fake is not None and true is not None else None,
            'decision_score': score, 'input_valid': True, 'label_mapping': mapping,
            'features': features,
            'explanation': ['SVM executado com scaler, embedding TF-IDF e mapeamento salvo no bundle.'],
            'model_loaded': True,
            'details': {'feature_count': len(model['feature_names'])},
        }
