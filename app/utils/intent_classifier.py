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

    # def predict(self, text: str, prob_threshold: float = 0.1) -> Dict[str, Any]:
    #     assert self.pipeline is not None, "Call load() first."

    #     # Predict probabilities
    #     proba = self.pipeline.predict_proba([text])[0]
    #     classes = self.pipeline.classes_

    #     # Build (intent, prob) pairs
    #     results = list(zip(classes, map(float, proba)))
    #     results.sort(key=lambda x: x[1], reverse=True)

    #     # Extract OOS probability (if exists)
    #     oos_prob = dict(results).get("out_of_scope", 0.0)
    #     top_label, top_prob = results[0]

    #     # Soft OOS override
    #     if top_label == "out_of_scope" :
    #         return {
    #             "intents": ["out_of_scope"],
    #             "probabilities": [round(oos_prob, 3)],
    #         }

    #     # Otherwise, filter OOS out of the list
    #     filtered = [(cls, p) for cls, p in results if cls != "out_of_scope"]

    #     # Keep only above threshold, fallback to top intent if none qualify
    #     selected = [(cls, p) for cls, p in filtered if p >= prob_threshold]
    #     if not selected:
    #         top_idx = int(np.argmax(proba))
    #         selected = [(classes[top_idx], float(proba[top_idx]))]

    #     # Prepare result
    #     intents = [cls for cls, _ in selected]
    #     probs = [round(p, 3) for _, p in selected]

    #     return {
    #         "intents": intents,
    #         "probabilities": probs,
    #     }

    def predict(self, text: str, prob_threshold: float | None = None) -> Dict[str, Any]:
        assert self.pipeline is not None, "Call load() first."

        if prob_threshold is None:
            prob_threshold = settings.min_confidence  # e.g. 0.55

        proba = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_

        # --- basic stats ---
        idx_sorted = np.argsort(proba)[::-1]
        top1_idx = int(idx_sorted[0])
        top2_idx = int(idx_sorted[1]) if len(classes) > 1 else top1_idx
        top1_prob = float(proba[top1_idx])
        top2_prob = float(proba[top2_idx])
        margin = top1_prob - top2_prob

        # where is out_of_scope in the class list?
        oos_label = "out_of_scope"
        oos_idx = None
        for i, c in enumerate(classes):
            if c == oos_label:
                oos_idx = i
                break

        # ---- OOS handling ----
        # Configurable thresholds
        oos_floor = getattr(settings, "oos_min_prob", 0.35)    # minimum prob to trust OOS
        oos_margin = getattr(settings, "oos_min_margin", 0.15) # how much higher than next intent

        if oos_idx is not None:
            oos_prob = float(proba[oos_idx])

            # Case 1: model clearly says "out_of_scope"
            if (top1_idx == oos_idx and oos_prob >= oos_floor and margin >= oos_margin):
                return {
                    "intents": [oos_label],
                    "probabilities": [round(oos_prob, 3)],
                }

        # Case 2: nothing is confident enough → treat as OOS too
        if top1_prob < prob_threshold:
            return {
                "intents": [oos_label],
                 "probabilities": [round(top1_prob, 3)],
            }

        # ---- normal multi–intent selection ----
        selected = []
        for cls, p in zip(classes, proba):
            p_float = float(p)
            if p_float >= prob_threshold and cls != oos_label:
                selected.append((cls, p_float))

        # if somehow nothing passes threshold but top1 already checked > prob_threshold,
        # just include top1 (unless it's oos, which we already handled)
        if not selected:
            top_label = str(classes[top1_idx])
            if top_label != oos_label:
                selected = [(top_label, top1_prob)]

        selected.sort(key=lambda x: x[1], reverse=True)

        intents = [cls for cls, _ in selected]
        probs = [round(p, 3) for _, p in selected]

        return {
            "intents": intents,
            "probabilities": probs,
        }



classifier = IntentClassifier().load()
