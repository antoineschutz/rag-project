import logging
from typing import Any

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


class Reranker:
    """Cross-encoder re-ranker for two-stage retrieval."""

    def __init__(self, model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        """Load the cross-encoder model."""
        self.model = CrossEncoder(model)
        logger.info("Reranker loaded: %s", model)

    def rerank(
        self,
        query: str,
        results: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Re-score results with the cross-encoder and return top_k by descending score."""
        pairs = [(query, r["text"]) for r in results]
        scores = self.model.predict(pairs)
        reranked = [
            {**r, "score": float(scores[i])}
            for i, r in enumerate(results)
        ]
        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:top_k]
