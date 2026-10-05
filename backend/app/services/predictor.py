from typing import Optional

import numpy as np
import pandas as pd

from .feature_extractor import FEATURES
from .pipeline_registry import PipelineRegistry
from .reference_service import ReferenceService


class Predictor:
    def __init__(self):
        self.registry = PipelineRegistry()
        self.reference = ReferenceService()

    def _bundle_frame(self, normalized: pd.DataFrame, text: str, bundle: dict) -> pd.DataFrame:
        numeric = bundle['scaler'].transform(normalized[FEATURES].astype(float).values)
        tfidf = bundle['tfidf'].transform([text]).toarray()
        return pd.DataFrame(np.hstack([numeric, tfidf]), columns=bundle['feature_names'])

    def analyze(self, text: str) -> dict:
        if len(text.split()) < 50:
            raise ValueError('Use a notícia completa; textos com menos de 50 palavras geram critérios pouco confiáveis.')
        if not self.reference.available:
            raise ValueError('Referência ausente: coloque backend/reference/referencia_bruta.csv.')
        raw, normalized, ref_normalized = self.reference.normalize_news(text)
        kmeans = self.registry.get('pipeline_kmeans_duat')
        svm = self.registry.get('svm')
        if kmeans is None or svm is None:
            raise ValueError('pipeline_kmeans_duat.joblib e svm_bundle.joblib são obrigatórios.')
        cluster = int(kmeans.predict(normalized[FEATURES])[0])
        centers = kmeans.named_steps['kmeans'].cluster_centers_
        verbal_cluster = int(np.argmax(centers[:, FEATURES.index('verbos_proporcao')]))
        profile = 'verbal' if cluster == verbal_cluster else 'nominal'
        ref_clusters = kmeans.predict(ref_normalized[FEATURES])
        mask = np.array([('verbal' if c == verbal_cluster else 'nominal') == profile for c in ref_clusters])
        ref_profile = ref_normalized.loc[mask].reset_index(drop=True)
        frame = self._bundle_frame(normalized, text, svm)
        estimator = svm['model']
        label = int(estimator.predict(frame)[0])
        score = float(estimator.decision_function(frame)[0]) if hasattr(estimator, 'decision_function') else None
        mapping = svm.get('label_mapping', {'0': 'fake', '1': 'true'})
        return {
            'features_raw': raw,
            'features': normalized[FEATURES].iloc[0].to_dict(),
            'profile': profile,
            'cluster': cluster,
            'classification': mapping.get(str(label), 'unknown'),
            'label': label,
            'decision_score': score,
            'model_loaded': True,
            'reference_size': len(ref_normalized),
            'details': {'label_mapping': mapping, 'feature_count': len(FEATURES), 'profile_reference_size': len(ref_profile)},
        }

    def predict(self, text: str, pipeline: str, supplied=None) -> dict:
        return self.analyze(text)
