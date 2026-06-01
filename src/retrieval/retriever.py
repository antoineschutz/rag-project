import logging
from typing import Any

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.config import config

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, chunked_docs: list[dict[str, str]], doc_embeddings: np.ndarray) -> None:
        self.docs = chunked_docs
        self.embeddings = doc_embeddings

    def retrieve(self, query_embedding: np.ndarray, top_k: int = config.TOP_K) -> list[dict[str, Any]]:
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for i in top_indices:
            results.append({
                "text": self.docs[i]["text"],
                "source": self.docs[i]["source"],
                "score": float(similarities[i])
            })

        for r in results:
            logger.debug("%.4f | %s | %d chars", r["score"], r["text"], len(r["text"]))

        return results
