from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from ..core.constants import FEATURES
from .feature_extractor import _load_external_extractor


ROOT = Path(__file__).resolve().parents[3]


def resolve_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    candidates = [Path.cwd() / path, ROOT / path, ROOT / "backend" / path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


class ReferenceService:
    def __init__(self):
        self.dataset_path = resolve_path(os.getenv("DUAT_DATASET_PATH", "dataset_duat_final.csv"))
        self.cache_path = resolve_path(os.getenv("DUAT_REFERENCE_CACHE", "referencia_bruta.csv"))
        self._reference: pd.DataFrame | None = None

    def load(self) -> pd.DataFrame:
        if self._reference is not None:
            return self._reference
        if self.cache_path.exists():
            self._reference = pd.read_csv(self.cache_path)
            return self._reference
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset DUAT não encontrado. Procurado em: {self.dataset_path}")

        data = pd.read_csv(self.dataset_path)
        data.columns = data.columns.str.strip()
        missing = [column for column in FEATURES if column not in data.columns]
        if missing and "texto" not in data.columns:
            raise ValueError(f"Dataset sem a coluna texto e sem features obrigatórias: {missing}")

        # O dataset também possui colunas textuais como texto, titulo ou categoria.
        # Nunca tente calcular max() nessas colunas: considere somente as 16 features.
        feature_frame = data[[column for column in FEATURES if column in data.columns]].apply(
            pd.to_numeric, errors="coerce"
        )
        numeric_feature_count = int(feature_frame.notna().any(axis=0).sum())
        normalized = numeric_feature_count == len(FEATURES) and bool(
            (feature_frame.max(axis=0, skipna=True) <= 1.0001).all()
        )

        if normalized:
            if "texto" not in data.columns:
                raise ValueError("Dataset normalizado sem coluna texto; não é possível recuperar a escala bruta.")
            module = _load_external_extractor()
            if module is None or not hasattr(module, "montar_dataset"):
                raise FileNotFoundError("Extrator DUAT necessário para recriar a referência bruta.")
            data = module.montar_dataset(
                data[["texto"] + (["rotulo"] if "rotulo" in data.columns else [])],
                verbose=True,
            )
            data.to_csv(self.cache_path, index=False)
        elif missing:
            raise ValueError(f"Dataset sem as 16 features do DUAT. Colunas ausentes: {missing}")

        self._reference = data
        return data
