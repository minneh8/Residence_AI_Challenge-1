from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.constants import FEATURES, NAMES, PRIORITY_CRITERIA, PROFILE_NAMES


def percentile(values, value: float) -> float:
    values = np.asarray(values, dtype=float)
    return float(100 * (np.mean(values < value) + 0.5 * np.mean(values == value)))


def status(percentile_value: float) -> str:
    if percentile_value < 25:
        return "abaixo do comum"
    if percentile_value > 75:
        return "acima do comum"
    return "dentro do comum"


def detect_profile(kmeans, scaled_row: pd.DataFrame, scaled_reference: pd.DataFrame):
    centers = kmeans.named_steps["kmeans"].cluster_centers_
    verbal_index = FEATURES.index("verbos_proporcao")
    verbal_cluster = int(np.argmax(centers[:, verbal_index]))
    mapping = {verbal_cluster: "verbal", 1 - verbal_cluster: "nominal"}
    cluster = int(kmeans.predict(scaled_row[FEATURES])[0])
    ref_clusters = kmeans.predict(scaled_reference[FEATURES])
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
