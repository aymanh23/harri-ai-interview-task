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

    def predict(self, text: str, prob_threshold: float = 0.1) -> Dict[str, Any]:
        assert self.pipeline is not None, "Call load() first."

        # 1️⃣ Predict probabilities
        proba = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_

        # 2️⃣ Build (intent, prob) pairs
        results = list(zip(classes, map(float, proba)))
        results.sort(key=lambda x: x[1], reverse=True)

        # 3️⃣ Extract OOS probability (if exists)
        oos_prob = dict(results).get("out_of_scope", 0.0)
        top_label, top_prob = results[0]

        # 4️⃣ Soft OOS override
        if top_label == "out_of_scope" :
            return {
                "intents": ["out_of_scope"],
                "probabilities": [round(oos_prob, 3)],
            }

        # 5️⃣ Otherwise, filter OOS out of the list
        filtered = [(cls, p) for cls, p in results if cls != "out_of_scope"]

        # 6️⃣ Keep only above threshold, fallback to top intent if none qualify
        selected = [(cls, p) for cls, p in filtered if p >= prob_threshold]
        if not selected:
            top_idx = int(np.argmax(proba))
            selected = [(classes[top_idx], float(proba[top_idx]))]

        # 7️⃣ Prepare response
        intents = [cls for cls, _ in selected]
        probs = [round(p, 3) for _, p in selected]

        return {
            "intents": intents,
            "probabilities": probs,
        }

# singleton
classifier = IntentClassifier().load()
