from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ..core.constants import FEATURES

ROOT = Path(__file__).resolve().parents[3]


def _load_external_extractor() -> Any:
    candidates = [
        ROOT / "backend" / "extracao_features.py",
        ROOT / "extracao_features.py",
        Path.cwd() / "backend" / "extracao_features.py",
        Path.cwd() / "extracao_features.py",
        Path(__file__).resolve().parents[2] / "extracao_features.py",
    ]
    for path in candidates:
        if path.exists():
            spec = importlib.util.spec_from_file_location("duat_external_extraction", path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
    return None


def extractor_locations() -> list[str]:
    return [
        str(ROOT / "backend" / "extracao_features.py"),
        str(ROOT / "extracao_features.py"),
        str(Path.cwd() / "backend" / "extracao_features.py"),
        str(Path.cwd() / "extracao_features.py"),
    ]


def extract_raw(text: str) -> pd.DataFrame:
    module = _load_external_extractor()
    if module is None or not hasattr(module, "montar_dataset"):
        raise FileNotFoundError("extracao_features.py não encontrado. Locais verificados: " + ", ".join(extractor_locations()))
    return module.montar_dataset(pd.DataFrame({"texto": [text]}), verbose=False)


def normalize_with_reference(raw: pd.DataFrame, reference: pd.DataFrame):
    module = _load_external_extractor()
    if module is None or not hasattr(module, "padronizar_dataframe"):
        raise FileNotFoundError("padronizar_dataframe não disponível em extracao_features.py. Locais verificados: " + ", ".join(extractor_locations()))
    combined = pd.concat([reference, raw], ignore_index=True)
    normalized = module.padronizar_dataframe(combined, verbose=False)
    normalized[FEATURES] = normalized[FEATURES].astype(np.float64)
    return normalized.iloc[[-1]].reset_index(drop=True), normalized.iloc[:-1].reset_index(drop=True)
