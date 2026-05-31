from sentence_transformers import SentenceTransformer

import numpy as np

from src.config import config


class Embedder:

    def __init__(self, model_name=config.EMBED_MODEL):

        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        try:
            return np.array(self.model.encode(texts, show_progress_bar=True))
        except MemoryError:
            raise MemoryError(
                f"Out of memory while embedding {len(texts)} documents. "
                "Try reducing CHUNK_MAX_TOKENS in src/config.py."
            )

    def embed_query(self, query):

        return self.model.encode([query])