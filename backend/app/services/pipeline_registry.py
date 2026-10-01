from pathlib import Path
from typing import Any

import joblib

PIPELINES = ('svm', 'kmeans', 'dbscan', 'isolation_forest')
MODEL_DIR = Path(__file__).resolve().parents[1] / 'models'


class PipelineRegistry:
    def __init__(self):
        self.models: dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        self.models.clear()
        for name in PIPELINES:
            path = MODEL_DIR / f'{name}.joblib'
            if path.exists():
                self.models[name] = joblib.load(path)

    def available(self) -> list[str]:
        return list(self.models.keys())

    def is_loaded(self, name: str) -> bool:
        return name in self.models

    def get(self, name: str) -> Any:
        return self.models.get(name)

    def status(self) -> dict:
        return {name: self.is_loaded(name) for name in PIPELINES}
