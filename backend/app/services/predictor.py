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
        names = bundle.get('feature_names')
        values = np.hstack([numeric, tfidf])
        if names and len(names) == values.shape[1]:
            return pd.DataFrame(values, columns=names)
        return pd.DataFrame(values)

    def analyze(self, text: str, pipeline: str = 'svm') -> dict:
        if len(text.split()) < 50:
            raise ValueError('Use a notícia completa; textos com menos de 50 palavras geram critérios pouco confiáveis.')
        if not self.reference.available:
            raise ValueError('Referência ausente: dataset_duat_final.csv não foi encontrado em backend/reference ou na raiz do projeto.')
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
        classification = mapping.get(str(label), 'unknown')
        return {
            'pipeline': pipeline,
            'features_raw': raw,
            'features': normalized[FEATURES].iloc[0].to_dict(),
            'profile': profile,
            'cluster': cluster,
            'classification': classification,
            'label': label,
            'fake_probability': None,
            'true_probability': None,
            'confidence': None,
            'decision_score': score,
            'input_valid': True,
            'label_mapping': mapping,
            'explanation': [
                f'Perfil de escrita identificado: {profile}.',
                f'Referência usada: {len(ref_normalized)} notícias; perfil com {len(ref_profile)} notícias.',
                'O decision_score mede a distância relativa à fronteira do SVM e não é uma probabilidade de acerto.',
            ],
            'model_loaded': True,
            'details': {
                'label_mapping': mapping,
                'feature_count': len(FEATURES),
                'profile_reference_size': len(ref_profile),
            },
        }

    def predict(self, text: str, pipeline: str, supplied=None) -> dict:
        return self.analyze(text, pipeline)
