"""In-process memoized caches for the heavy pipeline objects.

Loading a SentenceTransformer embedder or a cross-encoder reranker takes seconds,
so the API caches them across requests instead of rebuilding per call. Built
retrievers are cached too, keyed by the full set of knobs that affect the index.

`reset()` is called by /upload after the corpus changes: it drops the retriever
cache (the indexes are now stale) but keeps the embedder and reranker, which are
data independent and expensive to reload.
"""

import threading

from src.embeddings.embed import Embedder
from src.config import IndexParams
from src.reranker.reranker import Reranker
from src.retrieval.factory import Retriever, build_index

# RLock so get_retriever() can call get_embedder() while holding the lock.
_lock = threading.RLock()
_embedders: dict[str, Embedder] = {}
_retrievers: dict[IndexParams, Retriever] = {}
_reranker: Reranker | None = None


def get_embedder(model_name: str) -> Embedder:
    """Return a cached Embedder for model_name, loading it on first use."""
    with _lock:
        if model_name not in _embedders:
            _embedders[model_name] = Embedder(model_name=model_name)
        return _embedders[model_name]


def get_retriever(params: IndexParams) -> Retriever:
    """Return a cached retriever for these index params, building it on first use.

    IndexParams is frozen, so it serves directly as the cache key. Only index-defining
    knobs are in it (fusion/alpha are per-query and not part of identity), so one hybrid
    index is reused across fusion strategies.
    """
    with _lock:
        if params not in _retrievers:
            emb = None if params.retriever == "bm25" else get_embedder(params.embed_model)
            _retrievers[params] = build_index(params, embedder=emb)
        return _retrievers[params]


def get_reranker() -> Reranker:
    """Return the cached cross-encoder reranker, loading it on first use."""
    global _reranker
    with _lock:
        if _reranker is None:
            _reranker = Reranker()
        return _reranker


def reset() -> None:
    """Drop cached retrievers (called after the corpus changes); keep models loaded."""
    with _lock:
        _retrievers.clear()
