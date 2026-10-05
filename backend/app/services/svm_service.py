from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.constants import FEATURES


def _numeric_frame(bundle, numeric_frame: pd.DataFrame) -> pd.DataFrame:
    feature_names = list(bundle.get("numeric_features", FEATURES))
    missing = [name for name in feature_names if name not in numeric_frame.columns]
    if missing:
        raise ValueError(f"Features numéricas ausentes para o SVM: {missing}")
    return numeric_frame[feature_names].astype(np.float64)


def build_matrix(bundle, numeric_frame: pd.DataFrame, text: list[str]):
    numeric_input = _numeric_frame(bundle, numeric_frame)
    numeric_scaled = bundle["scaler"].transform(numeric_input)
    numeric_scaled = np.ascontiguousarray(numeric_scaled, dtype=np.float64)
    tfidf = bundle["tfidf"].transform(pd.Series(text, dtype="string").astype(str))
    tfidf_dense = np.ascontiguousarray(tfidf.toarray(), dtype=np.float64)
    matrix = np.hstack([numeric_scaled, tfidf_dense])
    expected = getattr(bundle["model"], "n_features_in_", None)
    if expected is not None and matrix.shape[1] != expected:
        raise ValueError(f"SVM espera {expected} features, mas a API montou {matrix.shape[1]}")
    return np.ascontiguousarray(matrix, dtype=np.float64)


def predict(bundle, row, text: str, reference=None, reference_texts=None):
    matrix = build_matrix(bundle, row, [text])
    label = int(bundle["model"].predict(matrix)[0])
    distance = float(np.asarray(bundle["model"].decision_function(matrix)).reshape(-1)[0])
    confidence = None
    if reference is not None and reference_texts is not None:
        reference_matrix = build_matrix(bundle, reference, list(reference_texts))
        reference_distances = np.abs(np.asarray(bundle["model"].decision_function(reference_matrix)).reshape(-1))
        first, second = np.percentile(reference_distances, [33.3, 66.7])
        confidence = "baixa" if abs(distance) < first else ("moderada" if abs(distance) < second else "alta")
    return label, distance, confidence
