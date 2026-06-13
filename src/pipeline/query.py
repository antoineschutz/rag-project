"""Query-phase orchestration: retrieve, rerank, and generate for one query.

`answer_query` is the second half of the two-phase pipeline; the first half,
`build_index` (src/retrieval/factory.py), builds the retriever. A caller builds the
param groups (src/config/params.py), builds the index once, then calls answer_query
per query.
"""

import logging
from collections.abc import Iterator
from typing import Any

from src.config import GenerationParams, RetrievalParams, env
from src.reranker.reranker import Reranker
from src.retrieval.factory import Retriever
from src.retrieval.retriever_hybrid import RetrieverHybrid
from src.prompts.templates import build_prompt_rag, build_prompt_no_rag
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)


def _prepare(
    retriever: Retriever | None,
    rp: RetrievalParams,
    gp: GenerationParams,
    reranker: Reranker | None,
) -> tuple[list[dict[str, Any]], str | None, str, LLMClient]:
    """Run retrieval/rerank/HyDE and build the prompt; return (chunks, hyde_doc, prompt, llm).

    Shared by answer_query and answer_query_stream so the two differ only in how they call the
    LLM. When `gp.no_rag` is set, retrieval is skipped (chunks empty, hyde_doc None) and
    `retriever` may be None; otherwise a None retriever is a caller bug and raises.
    """
    llm = LLMClient(backend=gp.backend or env.LLM_BACKEND, model=gp.model, num_ctx=gp.num_ctx)

    if gp.no_rag:
        return [], None, build_prompt_no_rag(rp.query), llm

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
        hyde_doc = retrieval_text
    else:
        retrieval_text = rp.query
        hyde_doc = None

    if isinstance(retriever, RetrieverHybrid):
        results = retriever.retrieve(retrieval_text, top_k=retrieval_k, fusion=rp.fusion, alpha=rp.alpha)
    else:
        results = retriever.retrieve(retrieval_text, top_k=retrieval_k)

    if rp.rerank:
        results = (reranker or Reranker()).rerank(rp.query, results, top_k=rp.top_k)

    contexts = [r["text"] for r in results]
    return results, hyde_doc, build_prompt_rag(rp.query, contexts), llm


def answer_query(
    retriever: Retriever | None,
    rp: RetrievalParams,
    gp: GenerationParams,
    reranker: Reranker | None = None,
) -> dict[str, Any]:
    """Answer one query, either from the model alone (no-RAG) or over a built retriever.

    Returns {"answer": str, "chunks": list[{"text", "source", "score"}], "hyde_doc": str | None}
    (empty chunks and hyde_doc=None for the no-RAG path; hyde_doc holds the generated passage when
    HyDE ran). `reranker` is injected for reuse; built lazily when None.
    """
    chunks, hyde_doc, prompt, llm = _prepare(retriever, rp, gp, reranker)
    return {"answer": llm.generate(prompt), "chunks": chunks, "hyde_doc": hyde_doc}


def answer_query_stream(
    retriever: Retriever | None,
    rp: RetrievalParams,
    gp: GenerationParams,
    reranker: Reranker | None = None,
) -> Iterator[dict[str, Any]]:
    """Answer one query, streaming the response token by token.

    Retrieval/rerank/HyDE finish first, then generation streams. Yields exactly one meta event
    {"type": "meta", "chunks": [...], "hyde_doc": str | None} followed by one
    {"type": "token", "text": str} per generated chunk.
    """
    chunks, hyde_doc, prompt, llm = _prepare(retriever, rp, gp, reranker)
    yield {"type": "meta", "chunks": chunks, "hyde_doc": hyde_doc}
    for delta in llm.generate_stream(prompt):
        yield {"type": "token", "text": delta}
