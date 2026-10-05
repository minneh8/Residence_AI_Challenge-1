from pathlib import Path
from typing import Optional

import pandas as pd

from .feature_extractor import FEATURES, extract_raw_features


class ReferenceService:
    def __init__(self):
        self.reference_path = Path(__file__).resolve().parents[2] / 'reference' / 'referencia_bruta.csv'
        self.reference: Optional[pd.DataFrame] = None
        self._load()

    def _load(self):
        if self.reference_path.exists():
            self.reference = pd.read_csv(self.reference_path)

    @property
    def available(self) -> bool:
        return self.reference is not None and all(name in self.reference.columns for name in FEATURES)

    def normalize_news(self, text: str):
        if not self.available:
            raise ValueError('Referência DUAT ausente. Coloque backend/reference/referencia_bruta.csv com as 16 features.')
        raw = extract_raw_features(text)
        combined = pd.concat([self.reference[FEATURES], pd.DataFrame([raw])], ignore_index=True)
        normalized = combined.copy()
        for feature in FEATURES:
            minimum = combined[feature].min()
            maximum = combined[feature].max()
            normalized[feature] = 0.0 if maximum == minimum else (combined[feature] - minimum) / (maximum - minimum)
        return raw, normalized.iloc[[-1]].reset_index(drop=True), normalized.iloc[:-1].reset_index(drop=True)
