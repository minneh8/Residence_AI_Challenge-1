from pathlib import Path
from typing import Any

import joblib

MODEL_DIR = Path(__file__).resolve().parents[1] / 'models'
ARTIFACTS = {
    'svm': 'svm_bundle.joblib',
    'pipeline_kmeans_duat': 'pipeline_kmeans_duat.joblib',
    'duat_dbscan_isolation_forest': 'duat_dbscan_isolation_forest.joblib',
}
ALIASES = {
    'kmeans': 'pipeline_kmeans_duat',
    'dbscan': 'duat_dbscan_isolation_forest',
    'isolation_forest': 'duat_dbscan_isolation_forest',
}


class PipelineRegistry:
    def __init__(self):
        self.models: dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        self.models.clear()
        for name, filename in ARTIFACTS.items():
            path = MODEL_DIR / filename
            if path.exists():
                self.models[name] = joblib.load(path)

    def canonical(self, name: str) -> str:
        return ALIASES.get(name, name)

    def available(self) -> list[str]:
        return list(self.models.keys())

    def supported(self) -> list[str]:
        return list(ARTIFACTS.keys())

    def is_loaded(self, name: str) -> bool:
        return self.canonical(name) in self.models

    def get(self, name: str) -> Any:
        return self.models.get(self.canonical(name))

    def status(self) -> dict[str, bool]:
        return {name: name in self.models for name in ARTIFACTS}
