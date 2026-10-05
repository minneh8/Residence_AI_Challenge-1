from __future__ import annotations

import logging
from pathlib import Path

import joblib
import numpy as np

from ..core.constants import FEATURES, LABEL_NAMES, NAMES, PROFILE_NAMES
from .feature_extractor import extract_raw, normalize_with_reference
from .profile_service import build_priority_results, class_comparison, detect_profile
from .reference_service import ReferenceService
from .svm_service import predict

logger = logging.getLogger("uvicorn.error")
ROOT = Path(__file__).resolve().parents[3]


def resolve_artifact(name: str) -> Path:
    candidates = [Path.cwd() / name, ROOT / name, ROOT / "backend" / name]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


class AnalysisService:
    def __init__(self):
        self.reference_service = ReferenceService()
        self.kmeans_path = resolve_artifact("pipeline_kmeans_duat.joblib")
        if not self.kmeans_path.exists():
            self.kmeans_path = resolve_artifact("backend/app/models/pipeline_kmeans_duat.joblib")
        self.svm_path = resolve_artifact("svm_bundle.joblib")
        if not self.svm_path.exists():
            self.svm_path = resolve_artifact("backend/app/models/svm_bundle.joblib")
        self._kmeans = None
        self._svm = None

    @property
    def kmeans(self):
        if self._kmeans is None:
            self._kmeans = joblib.load(self.kmeans_path)
        return self._kmeans

    @property
    def svm(self):
        if self._svm is None:
            self._svm = joblib.load(self.svm_path)
        return self._svm

    def analyze(self, text: str, user_evaluation: str):
        try:
            reference_raw = self.reference_service.load()
            raw = extract_raw(text)
            row, reference = normalize_with_reference(raw, reference_raw)
            profile, mapping, clusters = detect_profile(self.kmeans, row, reference)
            mask = np.array([mapping[c] == profile for c in clusters])
            profile_reference = reference[mask].reset_index(drop=True)
            profile_labels = reference_raw["rotulo"].to_numpy()[mask] if "rotulo" in reference_raw.columns else None
            criteria = build_priority_results(profile, row, profile_reference)
            out_of_range = [feature for feature in FEATURES if raw[feature].iloc[0] < reference_raw[feature].min() or raw[feature].iloc[0] > reference_raw[feature].max()]
            texts = reference_raw["texto"] if "texto" in reference_raw.columns else None
            svm_label, distance, confidence = predict(self.svm, row, text, reference, texts)
            classes = class_comparison(profile, row, profile_reference, profile_labels)
            user_label = {"v": 1, "f": 0, "n": None}[user_evaluation]
            agreement = None if user_label is None else user_label == svm_label
            return {
                "word_count": len(text.split()),
                "short_text_warning": len(text.split()) < 50,
                "profile": {"key": profile, "name": PROFILE_NAMES[profile]},
                "features": [{"name": f, "label": NAMES[f], "raw_value": float(raw[f].iloc[0]), "scaled_value": float(row[f].iloc[0])} for f in FEATURES],
                "priority_criteria": criteria,
                "out_of_range_features": out_of_range,
                "svm": {"prediction": LABEL_NAMES[svm_label], "label": svm_label, "decision_distance": distance, "confidence_level": confidence},
                "comparison": {"user_evaluation": "não sei" if user_label is None else LABEL_NAMES[user_label], "model_evaluation": LABEL_NAMES[svm_label], "agreement": agreement, "message": "O DUAT não é um verificador de fatos; revise fontes confiáveis antes de decidir ou compartilhar."},
                "class_comparison": classes,
                "warnings": ["O resultado é contexto para a decisão, não um veredito.", "O DUAT analisa estilo textual e não verifica os fatos do conteúdo."],
            }
        except Exception:
            logger.exception("Falha durante a análise DUAT")
            raise
