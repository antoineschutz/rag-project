"""Build the retriever for a given IndexParams.

Dispatches on the retriever type (dense / bm25 / hybrid) and, for dense, the store
(numpy / faiss), returning the matching built retriever. Together with answer_query
(src/pipeline/query.py) this forms the two-phase pipeline: build the index, then query it.
"""

from src.embeddings.embed import Embedder
from src.config import IndexParams
from src.retrieval.retriever_bm25 import RetrieverBM25, build_bm25_retriever
from src.retrieval.retriever_cosine import RetrieverCosine, build_cosine_retriever
from src.retrieval.retriever_faiss import RetrieverFAISS, build_faiss_retriever
from src.retrieval.retriever_hybrid import RetrieverHybrid, build_hybrid_retriever

Retriever = RetrieverBM25 | RetrieverCosine | RetrieverFAISS | RetrieverHybrid


def build_index(params: IndexParams, embedder: Embedder | None = None) -> Retriever:
    """Build the retriever described by params.

    `embedder` lets a caller reuse an already-loaded model across indexes (the API and
    eval scripts do this); when None and a dense backend is needed, one is created from
    params.embed_model. fusion/alpha are intentionally not passed: they are per-query
    arguments to retrieve(), not index-defining.
    """
    if params.retriever == "bm25":
        return build_bm25_retriever(params.data_path, chunk_max_tokens=params.chunk_max_tokens)

    embedder = embedder or Embedder(model_name=params.embed_model)

    if params.retriever == "hybrid":
        return build_hybrid_retriever(
            params.data_path, embedder, params.store, params.index_type,
            chunk_max_tokens=params.chunk_max_tokens,
        )
    if params.store == "faiss":
        return build_faiss_retriever(
            params.data_path, embedder, index_type=params.index_type,
            chunk_max_tokens=params.chunk_max_tokens,
        )
    return build_cosine_retriever(
        params.data_path, embedder, chunk_max_tokens=params.chunk_max_tokens,
    )
