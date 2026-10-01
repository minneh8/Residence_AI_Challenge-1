from pathlib import Path
from typing import Optional

import joblib
import pandas as pd

from .feature_extractor import FEATURE_NAMES, extract_features

MODEL_PATH = Path(__file__).resolve().parents[1] / 'models' / 'duat_model.joblib'


class Predictor:
    def __init__(self):
        self.model = None
        if MODEL_PATH.exists():
            self.model = joblib.load(MODEL_PATH)

    @property
    def model_loaded(self) -> bool:
        return self.model is not None

    def _fallback(self, features: dict[str, float]) -> tuple[int, float]:
        score = 0.5
        score += min(features['sensacionalismo_proporcao'] * 4.0, 0.2)
        score += min(features['emotividade'] * 0.2, 0.2)
        score += min(features['modais_proporcao'] * 0.5, 0.1)
        score -= min(features['fontes_proporcao'] * 0.5, 0.1)
        fake_probability = float(min(max(score, 0.01), 0.99))
        return int(fake_probability >= 0.5), fake_probability

    def predict(self, text: str, supplied_features: Optional[dict[str, float]] = None) -> dict:
        features = supplied_features or extract_features(text)
        missing = [name for name in FEATURE_NAMES if name not in features]
        if missing:
            raise ValueError(f'Features ausentes: {", ".join(missing)}')
        features = {name: float(features[name]) for name in FEATURE_NAMES}

        if self.model is not None:
            frame = pd.DataFrame([[features[name] for name in FEATURE_NAMES]], columns=FEATURE_NAMES)
            label = int(self.model.predict(frame)[0])
            probabilities = self.model.predict_proba(frame)[0]
            classes = list(self.model.classes_)
            fake_probability = float(probabilities[classes.index(0)])
            true_probability = float(probabilities[classes.index(1)])
        else:
            label, fake_probability = self._fallback(features)
            true_probability = 1.0 - fake_probability

        confidence = max(fake_probability, true_probability)
        explanation = []
        if features['sensacionalismo_proporcao'] > 0:
            explanation.append('Foram detectados termos sensacionalistas.')
        if features['fontes_proporcao'] == 0:
            explanation.append('Não foram identificados termos associados a fontes.')
        if features['emotividade'] > 0.05:
            explanation.append('O texto apresenta sinais de emotividade ou ênfase.')
        if not explanation:
            explanation.append('A classificação foi baseada nas características textuais extraídas.')

        return {
            'label': label,
            'classification': 'fake' if label == 0 else 'true',
            'fake_probability': round(fake_probability, 6),
            'true_probability': round(true_probability, 6),
            'confidence': round(confidence, 6),
            'features': features,
            'explanation': explanation,
            'model_loaded': self.model_loaded,
        }
