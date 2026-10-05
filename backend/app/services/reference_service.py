from pathlib import Path
from typing import Optional

import pandas as pd

from .feature_extractor import FEATURES, extract_raw_features


class ReferenceService:
    def __init__(self):
        base = Path(__file__).resolve().parents[2]
        reference_dir = base / 'reference'
        self.cache_path = reference_dir / 'referencia_bruta.csv'
        self.dataset_candidates = [
            reference_dir / 'dataset_duat_final.csv',
            base / 'dataset_duat_final.csv',
            Path.cwd() / 'dataset_duat_final.csv',
            reference_dir / 'DUAT_datasetv_2_1.csv',
            base / 'DUAT_datasetv_2_1.csv',
            Path.cwd() / 'DUAT_datasetv_2_1.csv',
        ]
        self.reference: Optional[pd.DataFrame] = None
        self._load_or_build()

    def _find_dataset(self) -> Optional[Path]:
        for candidate in self.dataset_candidates:
            if candidate.exists():
                return candidate
        return None

    def _is_raw(self, frame: pd.DataFrame) -> bool:
        return all(feature in frame.columns for feature in FEATURES) and not (
            'texto' in frame.columns and frame[FEATURES].max().max() <= 1.0001
        )

    def _build_from_text(self, frame: pd.DataFrame) -> pd.DataFrame:
        if 'texto' not in frame.columns:
            raise ValueError('O dataset precisa conter a coluna texto para gerar referencia_bruta.csv.')
        rows = []
        for text in frame['texto'].fillna('').astype(str):
            rows.append(extract_raw_features(text))
        reference = pd.DataFrame(rows)
        if 'rotulo' in frame.columns:
            reference['rotulo'] = frame['rotulo'].values
        reference['texto'] = frame['texto'].values
        return reference

    def _load_or_build(self):
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        if self.cache_path.exists():
            self.reference = pd.read_csv(self.cache_path)
            return
        dataset_path = self._find_dataset()
        if dataset_path is None:
            return
        dataset = pd.read_csv(dataset_path)
        dataset.columns = dataset.columns.str.strip()
        if self._is_raw(dataset):
            self.reference = dataset
        else:
            self.reference = self._build_from_text(dataset)
        self.reference.to_csv(self.cache_path, index=False)

    @property
    def available(self) -> bool:
        return self.reference is not None and all(name in self.reference.columns for name in FEATURES)

    def normalize_news(self, text: str):
        if not self.available:
            raise ValueError('Referência ausente: dataset_duat_final.csv não foi encontrado em backend/reference ou na raiz do projeto.')
        raw = extract_raw_features(text)
        combined = pd.concat([self.reference[FEATURES], pd.DataFrame([raw])], ignore_index=True)
        normalized = combined.copy()
        for feature in FEATURES:
            minimum = combined[feature].min()
            maximum = combined[feature].max()
            normalized[feature] = 0.0 if maximum == minimum else (combined[feature] - minimum) / (maximum - minimum)
        return raw, normalized.iloc[[-1]].reset_index(drop=True), normalized.iloc[:-1].reset_index(drop=True)
