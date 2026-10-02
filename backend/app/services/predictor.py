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
        all_features = bundle['feature_names']
        numeric_names = bundle.get('numeric_features') or [name for name in all_features if not name.startswith('tfidf_')]
        numeric_names = [name for name in numeric_names if name not in {'types_proporcao', 'num_palavras'}]
        tfidf_names = bundle.get('tfidf_features') or [name for name in all_features if name.startswith('tfidf_')]
        missing = [name for name in numeric_names if name not in features]
        if missing:
            raise ValueError(f'O bundle exige features removidas: {", ".join(missing)}. Gere um novo bundle sem types_proporcao e num_palavras.')
        numeric_df = pd.DataFrame(bundle['scaler'].transform([[features[name] for name in numeric_names]]), columns=numeric_names)
        tfidf_df = pd.DataFrame(bundle['tfidf'].transform([text]).toarray(), columns=tfidf_names)
        frame = pd.concat([numeric_df, tfidf_df], axis=1)
        expected = [name for name in all_features if name not in {'types_proporcao', 'num_palavras'}]
        return frame[expected]

    def predict(self, text: str, pipeline: str, supplied: Optional[dict[str, float]] = None) -> dict:
        self.validate_news_text(text)
        if self.registry.canonical(pipeline) != 'svm':
            raise ValueError('Use o endpoint específico do pipeline selecionado.')
        model = self.registry.get(pipeline)
        if not self._is_svm_bundle(model):
            raise ValueError('svm_bundle.joblib não possui o formato esperado.')
        features = self._features(text, supplied)
        frame = self._svm_frame(text, features, model)
        estimator = model['model']
        label = int(estimator.predict(frame)[0])
        fake = true = None
        if hasattr(estimator, 'predict_proba'):
            probabilities = estimator.predict_proba(frame)[0]
            classes = list(estimator.classes_)
            fake = float(probabilities[classes.index(0)]) if 0 in classes else None
            true = float(probabilities[classes.index(1)]) if 1 in classes else None
        score = float(estimator.decision_function(frame)[0]) if hasattr(estimator, 'decision_function') else None
        mapping = model.get('label_mapping', {'0': 'fake', '1': 'true'})
        return {'pipeline': pipeline, 'label': label, 'classification': mapping.get(str(label), 'unknown'), 'fake_probability': fake, 'true_probability': true, 'confidence': max(fake, true) if fake is not None and true is not None else None, 'decision_score': score, 'input_valid': True, 'label_mapping': mapping, 'features': features, 'explanation': ['SVM executado sem types_proporcao e num_palavras.'], 'model_loaded': True, 'details': None}
