from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pandas as pd


def _load_external_extractor() -> Any:
    candidates = [
        Path("extracao_features.py"),
        Path("backend/extracao_features.py"),
        Path(__file__).resolve().parents[3] / "extracao_features.py",
    ]
    for path in candidates:
        if path.exists():
            spec = importlib.util.spec_from_file_location("duat_external_extraction", path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
    return None


def extract_raw(text: str) -> pd.DataFrame:
    module = _load_external_extractor()
    if module is None or not hasattr(module, "montar_dataset"):
        raise FileNotFoundError(
            "extracao_features.py não encontrado. Instale o artefato de extração do DUAT."
        )
    return module.montar_dataset(pd.DataFrame({"texto": [text]}), verbose=False)


def normalize_with_reference(raw: pd.DataFrame, reference: pd.DataFrame):
    module = _load_external_extractor()
    if module is None or not hasattr(module, "padronizar_dataframe"):
        raise FileNotFoundError("padronizar_dataframe não está disponível no extrator DUAT.")
    combined = pd.concat([reference, raw], ignore_index=True)
    normalized = module.padronizar_dataframe(combined, verbose=False)
    return normalized.iloc[[-1]].reset_index(drop=True), normalized.iloc[:-1].reset_index(drop=True)
