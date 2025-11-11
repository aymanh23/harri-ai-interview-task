from __future__ import annotations
from typing import Dict, Any
import joblib
import numpy as np
from app.config.settings import settings

class IntentClassifier:
    def __init__(self, model_path: str | None = None):
        self.model_path = str(model_path or settings.model_path)
        self.pipeline = None
        self.label_names: list[str] | None = None

    def load(self):
        if self.pipeline is None:
            bundle = joblib.load(self.model_path)
            # support both “pure pipeline” and “dict with meta”
            if isinstance(bundle, dict) and "pipeline" in bundle:
                self.pipeline = bundle["pipeline"]
                self.label_names = bundle.get("label_names")
            else:
                self.pipeline = bundle
        return self

    def predict(self, text: str) -> Dict[str, Any]:
        assert self.pipeline is not None, "Call load() first."
        proba = self.pipeline.predict_proba([text])[0]
        idx = int(np.argmax(proba))
        label = self.pipeline.classes_[idx]
        confidence = float(proba[idx])
        return {"label": str(label), "confidence": confidence, "proba": proba.tolist()}

# singleton
classifier = IntentClassifier().load()
