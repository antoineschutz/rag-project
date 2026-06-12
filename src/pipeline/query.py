"""Query-phase orchestration: retrieve, rerank, and generate for one query.

`answer_query` is the second half of the two-phase pipeline; the first half,
`build_index` (src/retrieval/factory.py), builds the retriever. A caller builds the
param groups (src/config/params.py), builds the index once, then calls answer_query
per query.
"""

import logging
from typing import Any

from src.config import GenerationParams, RetrievalParams, env
from src.reranker.reranker import Reranker
from src.retrieval.factory import Retriever
from src.retrieval.retriever_hybrid import RetrieverHybrid
from src.prompts.templates import build_prompt_rag, build_prompt_no_rag
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)


def answer_query(
    retriever: Retriever | None,
    rp: RetrievalParams,
    gp: GenerationParams,
    reranker: Reranker | None = None,
) -> dict[str, Any]:
    """Answer one query, either from the model alone (no-RAG) or over a built retriever.

    When `gp.no_rag` is set, retrieval is skipped and `retriever` may be None. Otherwise a
    retriever is required (a None retriever with no_rag=False is a caller bug and raises).
    Returns {"answer": str, "chunks": list[{"text", "source", "score"}]} (empty chunks for
    the no-RAG path). `reranker` is injected for reuse; built lazily when None.
    """
    llm = LLMClient(backend=gp.backend or env.LLM_BACKEND, model=gp.model, num_ctx=gp.num_ctx)

    if gp.no_rag:
        return {"answer": llm.generate(build_prompt_no_rag(rp.query)), "chunks": []}

    if retriever is None:
        raise ValueError(
            "answer_query requires a retriever when gp.no_rag is False; "
            "build one with build_index() or set no_rag=True."
        )

    retrieval_k = rp.top_k * 3 if rp.rerank else rp.top_k

    # Under HyDE the retrieval text is a hypothetical answer passage; retrievers embed it
    # internally, so the same string feeds every backend (both arms of the hybrid).
    if rp.hyde:
        from src.hyde.hyde import generate_hypothetical_doc
        retrieval_text = generate_hypothetical_doc(rp.query, llm)
    else:
        retrieval_text = rp.query

    if isinstance(retriever, RetrieverHybrid):
        results = retriever.retrieve(retrieval_text, top_k=retrieval_k, fusion=rp.fusion, alpha=rp.alpha)
    else:
        results = retriever.retrieve(retrieval_text, top_k=retrieval_k)

    if rp.rerank:
        results = (reranker or Reranker()).rerank(rp.query, results, top_k=rp.top_k)

    contexts = [r["text"] for r in results]
    answer = llm.generate(build_prompt_rag(rp.query, contexts))
    return {"answer": answer, "chunks": results}
