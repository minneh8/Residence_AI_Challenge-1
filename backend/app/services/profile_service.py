from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.constants import FEATURES, NAMES, PRIORITY_CRITERIA


def percentile(values, value: float) -> float:
    values = np.asarray(values, dtype=np.float64)
    return float(100 * (np.mean(values < value) + 0.5 * np.mean(values == value)))


def status(percentile_value: float) -> str:
    if percentile_value < 25:
        return "abaixo do comum"
    if percentile_value > 75:
        return "acima do comum"
    return "dentro do comum"


def _as_float64(frame: pd.DataFrame) -> np.ndarray:
    return np.ascontiguousarray(frame[FEATURES].astype(np.float64).to_numpy(), dtype=np.float64)


def _prepare_kmeans_dtype(kmeans) -> None:
    estimator = kmeans.named_steps["kmeans"]
    if hasattr(estimator, "cluster_centers_"):
        estimator.cluster_centers_ = np.ascontiguousarray(estimator.cluster_centers_, dtype=np.float64)
    if hasattr(estimator, "_n_threads"):
        estimator._n_threads = 1


def detect_profile(kmeans, scaled_row: pd.DataFrame, scaled_reference: pd.DataFrame):
    _prepare_kmeans_dtype(kmeans)
    centers = np.asarray(kmeans.named_steps["kmeans"].cluster_centers_, dtype=np.float64)
    verbal_index = FEATURES.index("verbos_proporcao")
    verbal_cluster = int(np.argmax(centers[:, verbal_index]))
    mapping = {verbal_cluster: "verbal", 1 - verbal_cluster: "nominal"}
    cluster = int(kmeans.predict(_as_float64(scaled_row))[0])
    ref_clusters = kmeans.predict(_as_float64(scaled_reference))
    return mapping[cluster], mapping, ref_clusters


def build_priority_results(profile, row, reference):
    results = []
    for feature, importance in PRIORITY_CRITERIA[profile]:
        value = float(row[feature].iloc[0])
        p = percentile(reference[feature], value)
        results.append({
            "name": feature,
            "label": NAMES[feature],
            "importance": importance,
            "score": value,
            "percentile": round(p),
            "status": status(p),
            "meaning": "Critério prioritário do perfil de escrita; interprete-o como padrão estilístico, não como prova de veracidade.",
        })
    return results


def class_comparison(profile, row, reference, labels):
    result = []
    if labels is None:
        return result
    labels = np.asarray(labels)
    for feature, _ in PRIORITY_CRITERIA[profile]:
        value_p = percentile(reference[feature], float(row[feature].iloc[0]))
        false_p = percentile(reference[feature][labels == 0], reference.loc[labels == 0, feature].median())
        true_p = percentile(reference[feature][labels == 1], reference.loc[labels == 1, feature].median())
        closer = None if abs(false_p - true_p) < 5 else ("falsa" if abs(value_p - false_p) < abs(value_p - true_p) else "verdadeira")
        result.append({"criterion": feature, "label": NAMES[feature], "closer_to": closer, "false_median_percentile": round(false_p), "true_median_percentile": round(true_p)})
    return result
