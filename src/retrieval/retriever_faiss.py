import logging
from typing import Any

import faiss
import numpy as np

from src.config import config

logger = logging.getLogger(__name__)


class RetrieverFAISS:
    def __init__(self, chunked_docs: list[dict[str, str]], doc_embeddings: np.ndarray) -> None:
        self.docs = chunked_docs
        vectors = doc_embeddings.astype("float32")
        faiss.normalize_L2(vectors)
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    @classmethod
    def from_index(cls, chunked_docs: list[dict[str, str]], index: faiss.IndexFlatIP) -> "RetrieverFAISS":
        obj = cls.__new__(cls)
        obj.docs = chunked_docs
        obj.index = index
        return obj

    def retrieve(self, query_embedding: np.ndarray, top_k: int = config.TOP_K) -> list[dict[str, Any]]:
        query = np.array(query_embedding, dtype="float32")
        if query.ndim == 1:
            query = query.reshape(1, -1)
        faiss.normalize_L2(query)
        scores, indices = self.index.search(query, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            results.append({
                "text": self.docs[idx]["text"],
                "source": self.docs[idx]["source"],
                "score": float(score),
            })
            logger.debug("%.4f | %s | %d chars", score, self.docs[idx]["text"], len(self.docs[idx]["text"]))

        return results
