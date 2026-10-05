from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from ..core.constants import FEATURES
from .feature_extractor import _load_external_extractor

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REFERENCE_DIR = ROOT / "backend" / "reference"
DEFAULT_CACHE_PATH = DEFAULT_REFERENCE_DIR / "referencia_bruta.csv"
DEFAULT_DATASET_PATH = ROOT / "dataset_duat_final.csv"


def resolve_path(value: str | None, default: Path) -> Path:
    if value:
        path = Path(value).expanduser()
        if path.is_absolute():
            return path
        candidates = [ROOT / path, ROOT / "backend" / path, Path.cwd() / path]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return ROOT / path
    return default


def _is_valid_cache(data: pd.DataFrame) -> bool:
    return all(feature in data.columns for feature in FEATURES) and len(data) > 0


class ReferenceService:
    def __init__(self):
        self.dataset_path = resolve_path(os.getenv("DUAT_DATASET_PATH"), DEFAULT_DATASET_PATH)
        self.cache_path = resolve_path(os.getenv("DUAT_REFERENCE_CACHE"), DEFAULT_CACHE_PATH)
        self._reference: pd.DataFrame | None = None

    def _load_cache(self) -> pd.DataFrame | None:
        if not self.cache_path.exists():
            return None
        data = pd.read_csv(self.cache_path)
        if not _is_valid_cache(data):
            raise ValueError(f"Cache DUAT inválido: faltam features em {self.cache_path}")
        return data

    def _build_cache(self) -> pd.DataFrame:
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset DUAT não encontrado. Procurado em: {self.dataset_path}")
        data = pd.read_csv(self.dataset_path)
        data.columns = data.columns.str.strip()
        missing = [column for column in FEATURES if column not in data.columns]
        if missing and "texto" not in data.columns:
            raise ValueError(f"Dataset sem texto e sem features obrigatórias: {missing}")
        feature_frame = data[[column for column in FEATURES if column in data.columns]].apply(pd.to_numeric, errors="coerce")
        normalized = len(feature_frame.columns) == len(FEATURES) and bool((feature_frame.max(axis=0, skipna=True) <= 1.0001).all())
        if normalized:
            if "texto" not in data.columns:
                raise ValueError("Dataset normalizado sem coluna texto; não é possível criar a referência bruta.")
            module = _load_external_extractor()
            if module is None or not hasattr(module, "montar_dataset"):
                raise FileNotFoundError("Extrator DUAT necessário para criar a referência bruta.")
            data = module.montar_dataset(data[["texto"] + (["rotulo"] if "rotulo" in data.columns else [])], verbose=False)
        elif missing:
            raise ValueError(f"Dataset sem as 16 features do DUAT. Colunas ausentes: {missing}")
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.cache_path.with_suffix(self.cache_path.suffix + ".tmp")
        data.to_csv(temporary, index=False)
        os.replace(temporary, self.cache_path)
        return data

    def load(self) -> pd.DataFrame:
        if self._reference is not None:
            return self._reference
        cached = self._load_cache()
        self._reference = cached if cached is not None else self._build_cache()
        return self._reference
