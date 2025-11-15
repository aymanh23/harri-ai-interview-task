from typing import Dict, Any
import joblib
import numpy as np
from app.settings import settings

class IntentClassifier:
    def __init__(self, model_path: str | None = None):
        self.model_path = str(model_path or settings.model_path)
        self.pipeline = None
        self.label_names: list[str] | None = None

    def load(self):
        if self.pipeline is None:
            bundle = joblib.load(self.model_path)
            if isinstance(bundle, dict) and "pipeline" in bundle:
                self.pipeline = bundle["pipeline"]
                self.label_names = bundle.get("label_names")
            else:
                self.pipeline = bundle
        return self

    def predict(self, text: str, prob_threshold: float = 0.1) -> Dict[str, Any]:
        # Predict probabilities 
        proba = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_

        # Build (intent, prob) pairs
        results = list(zip(classes, map(float, proba)))
        results.sort(key=lambda x: x[1], reverse=True)

        # Extract top class and its probability
        top_label, top_prob = results[0]

        # return oos directly if its the top intent and dominates other probabilities
        if top_label == "out_of_scope"  and top_prob > 0.5:
            return {
                "intents": ["out_of_scope"],
                "probabilities": [round(top_prob, 3)],
            }

        # Otherwise, filter OOS out of the list
        filtered = [(cls, p) for cls, p in results if cls != "out_of_scope"]

        # Keep only above threshold, fallback to top intent if none qualify
        selected = [(cls, p) for cls, p in filtered if p >= prob_threshold]
        if not selected:
            top_idx = int(np.argmax(proba))
            selected = [(classes[top_idx], float(proba[top_idx]))]

        # Prepare result
        intents = [cls for cls, _ in selected]
        probs = [round(p, 3) for _, p in selected]

        return {
            "intents": intents,
            "probabilities": probs,
        }

classifier = IntentClassifier().load()
