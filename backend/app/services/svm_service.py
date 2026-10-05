from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.constants import FEATURES


def build_matrix(bundle, numeric_frame: pd.DataFrame, text: list[str]):
    numeric = bundle["scaler"].transform(numeric_frame[FEATURES].astype(float).values)
    tfidf = bundle["tfidf"].transform(pd.Series(text).astype(str)).toarray()
    return np.hstack([numeric, tfidf])


def predict(bundle, row, text: str, reference=None, reference_texts=None):
    matrix = build_matrix(bundle, row, [text])
    label = int(bundle["model"].predict(matrix)[0])
    distance = float(bundle["model"].decision_function(matrix)[0])
    confidence = None
    if reference is not None and reference_texts is not None:
        ref_distances = np.abs(bundle["model"].decision_function(build_matrix(bundle, reference, list(reference_texts))))
        first, second = np.percentile(ref_distances, [33.3, 66.7])
        confidence = "baixa" if abs(distance) < first else ("moderada" if abs(distance) < second else "alta")
    return label, distance, confidence
