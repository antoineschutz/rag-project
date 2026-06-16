import logging
from typing import Any

from src.config import BASE
from src.embeddings.embed import Embedder
from src.retrieval.retriever_cosine import RetrieverCosine, build_cosine_retriever
from src.retrieval.retriever_bm25 import RetrieverBM25, build_bm25_retriever
from src.retrieval.retriever_faiss import RetrieverFAISS, build_faiss_retriever
from src.retrieval.retriever_qdrant import RetrieverQdrant, build_qdrant_retriever

logger = logging.getLogger(__name__)


class RetrieverHybrid:
    """Fuses dense and BM25 results via RRF or weighted sum."""

    def __init__(
        self,
        dense: RetrieverCosine | RetrieverFAISS | RetrieverQdrant,
        bm25: RetrieverBM25,
        fusion: str = "rrf",
        alpha: float = 0.5,
        k: int = 60,
    ) -> None:
        """Store sub-retrievers and fusion settings."""
        self.dense = dense
        self.bm25 = bm25
        self.fusion = fusion
        self.alpha = alpha
        self.k = k

    def retrieve(
        self,
        query: str,
        top_k: int = BASE.top_k,
        source: str | list[str] | None = None,
        *,
        fusion: str | None = None,
        alpha: float | None = None,
    ) -> list[dict[str, Any]]:
        """Return top_k chunks by fusing dense and BM25 candidate pools.

        The same query string feeds both arms: the dense sub-retriever embeds it, BM25
        tokenizes it. fusion/alpha override the instance defaults for this call (they are
        per-query knobs, not baked into the index). An optional source filter is forwarded
        into both arms so each pool is filtered before fusion.
        """
        fusion = fusion if fusion is not None else self.fusion
        alpha = alpha if alpha is not None else self.alpha
        pool = top_k * 3
        dense_results = self.dense.retrieve(query, top_k=pool, source=source)
        bm25_results = self.bm25.retrieve(query, top_k=pool, source=source)
        if fusion == "rrf":
            return self._fuse_rrf(dense_results, bm25_results, top_k)
        return self._fuse_weighted(dense_results, bm25_results, top_k, alpha)

    def _fuse_rrf(
        self,
        dense_results: list[dict[str, Any]],
        bm25_results: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Reciprocal Rank Fusion: score = Σ 1/(k + rank) across both lists."""
        dense_rank = {r["text"]: i + 1 for i, r in enumerate(dense_results)}
        bm25_rank = {r["text"]: i + 1 for i, r in enumerate(bm25_results)}

        seen: dict[str, dict[str, str]] = {}
        for r in dense_results + bm25_results:
            if r["text"] not in seen:
                seen[r["text"]] = {"text": r["text"], "source": r["source"]}

        fused = []
        for text, meta in seen.items():
            score = 0.0
            if text in dense_rank:
                score += 1.0 / (self.k + dense_rank[text])
            if text in bm25_rank:
                score += 1.0 / (self.k + bm25_rank[text])
            fused.append({**meta, "score": score})

        fused.sort(key=lambda x: x["score"], reverse=True)
        return fused[:top_k]

    def _fuse_weighted(
        self,
        dense_results: list[dict[str, Any]],
        bm25_results: list[dict[str, Any]],
        top_k: int,
        alpha: float,
    ) -> list[dict[str, Any]]:
        """Weighted sum fusion with per-query min-max normalisation."""
        def _minmax(results: list[dict[str, Any]]) -> dict[str, float]:
            if not results:
                return {}
            scores = [r["score"] for r in results]
            lo, hi = min(scores), max(scores)
            denom = hi - lo if hi != lo else 1.0
            return {r["text"]: (r["score"] - lo) / denom for r in results}

        dense_norm = _minmax(dense_results)
        bm25_norm = _minmax(bm25_results)

        seen: dict[str, dict[str, str]] = {}
        for r in dense_results + bm25_results:
            if r["text"] not in seen:
                seen[r["text"]] = {"text": r["text"], "source": r["source"]}

        fused = []
        for text, meta in seen.items():
            score = (
                alpha * dense_norm.get(text, 0.0)
                + (1 - alpha) * bm25_norm.get(text, 0.0)
            )
            fused.append({**meta, "score": score})

        fused.sort(key=lambda x: x["score"], reverse=True)
        return fused[:top_k]


def build_hybrid_retriever(
    data_path: str,
    embedder: Embedder,
    store: str = "numpy",
    index_type: str = "flat",
    fusion: str = "rrf",
    alpha: float = 0.5,
    k: int = 60,
    chunk_max_tokens: int | None = None,
) -> RetrieverHybrid:
    """Build a hybrid retriever combining a dense backend and BM25."""
    if store == "faiss":
        dense = build_faiss_retriever(data_path, embedder, index_type=index_type, chunk_max_tokens=chunk_max_tokens)
    elif store == "qdrant":
        dense = build_qdrant_retriever(data_path, embedder, chunk_max_tokens=chunk_max_tokens)
    else:
        dense = build_cosine_retriever(data_path, embedder, chunk_max_tokens=chunk_max_tokens)
    bm25 = build_bm25_retriever(data_path, chunk_max_tokens=chunk_max_tokens)
    return RetrieverHybrid(dense, bm25, fusion=fusion, alpha=alpha, k=k)
