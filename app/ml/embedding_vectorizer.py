
from sklearn.base import BaseEstimator, TransformerMixin
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler
import pandas as pd
from scipy.sparse import csr_matrix
import numpy as np

class EmbeddingVectorizer(BaseEstimator, TransformerMixin):
    def __init__(self, model_name="all-MiniLM-L6-v2", batch_size=64):
        self.model_name = model_name
        self.batch_size = batch_size
        self.model = SentenceTransformer(model_name)
        self.scaler = StandardScaler(with_mean=False)
    def fit(self, X, y=None):
        texts = pd.Series(X, dtype="object").astype(str).tolist()
        emb = self.model.encode(texts, batch_size=self.batch_size,
                                normalize_embeddings=True, convert_to_numpy=True,
                                show_progress_bar=False)
        self.scaler.fit(emb)
        return self
    def transform(self, X):
        texts = pd.Series(X, dtype="object").astype(str).tolist()
        emb = self.model.encode(texts, batch_size=self.batch_size,
                                normalize_embeddings=True, convert_to_numpy=True,
                                show_progress_bar=False)
        emb = self.scaler.transform(emb)
        return csr_matrix(np.nan_to_num(emb))
