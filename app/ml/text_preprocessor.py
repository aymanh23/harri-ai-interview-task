from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
class TextPreprocessor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        # accept Series/list/array → return list[str]
        s = pd.Series(X, dtype="object")
        return s.apply(self._clean).tolist()
    @staticmethod
    def _clean(t: str) -> str:
        t = str(t).lower().strip()
        return t