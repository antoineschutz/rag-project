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
from src.prompts.templates import (
    build_prompt_rag,
    build_prompt_no_rag,
    build_prompt_rag_chat,
    build_prompt_no_rag_chat,
)
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)


def _prepare(
    retriever: Retriever | None,
    rp: RetrievalParams,
    gp: GenerationParams,
    reranker: Reranker | None,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Run retrieval/rerank/HyDE and build the prompt.

    Returns {"chunks": [...], "hyde_doc": str | None, "standalone_query": str | None,
    "prompt": str, "llm": LLMClient}. Shared by answer_query and answer_query_stream so the two
    differ only in how they call the LLM. When `gp.no_rag` is set, retrieval is skipped (chunks
    empty, hyde_doc None) and `retriever` may be None; otherwise a None retriever is a caller bug
    and raises.

    When `history` is given, the question is first condensed into a standalone query (which feeds
    retrieval, HyDE, and rerank) and the answer prompt carries the recent history. standalone_query
    is set only when condensing actually changed the question, else None. With no history the path
    is identical to the single-shot pipeline.
    """
    llm = LLMClient(backend=gp.backend or env.LLM_BACKEND, model=gp.model, num_ctx=gp.num_ctx)

    if gp.no_rag:
        prompt = build_prompt_no_rag_chat(history, rp.query) if history else build_prompt_no_rag(rp.query)
        return {"chunks": [], "hyde_doc": None, "standalone_query": None, "prompt": prompt, "llm": llm}

    if retriever is None:
        raise ValueError(
            "answer_query requires a retriever when gp.no_rag is False; "
            "build one with build_index() or set no_rag=True."
        )

    # Condense a context-dependent follow-up into a standalone query before retrieval/HyDE/rerank.
    if history:
        from src.memory.condense import condense_question
        standalone = condense_question(history, rp.query, llm)
    else:
        standalone = rp.query

    retrieval_k = rp.top_k * 3 if rp.rerank else rp.top_k

    # Under HyDE the retrieval text is a hypothetical answer passage; retrievers embed it
    # internally, so the same string feeds every backend (both arms of the hybrid).
    if rp.hyde:
        from src.hyde.hyde import generate_hypothetical_doc
        retrieval_text = generate_hypothetical_doc(standalone, llm)
        hyde_doc = retrieval_text
    else:
        retrieval_text = standalone
        hyde_doc = None

    if isinstance(retriever, RetrieverHybrid):
        results = retriever.retrieve(retrieval_text, top_k=retrieval_k, source=rp.source, fusion=rp.fusion, alpha=rp.alpha)
    else:
        results = retriever.retrieve(retrieval_text, top_k=retrieval_k, source=rp.source)

    if rp.rerank:
        results = (reranker or Reranker()).rerank(standalone, results, top_k=rp.top_k)

    contexts = [r["text"] for r in results]
    prompt = build_prompt_rag_chat(history, rp.query, contexts) if history else build_prompt_rag(rp.query, contexts)
    standalone_out = standalone if (history and standalone != rp.query) else None
    return {
        "chunks": results, "hyde_doc": hyde_doc, "standalone_query": standalone_out,
        "prompt": prompt, "llm": llm,
    }


def answer_query(
    retriever: Retriever | None,
    rp: RetrievalParams,
    gp: GenerationParams,
    reranker: Reranker | None = None,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Answer one query, either from the model alone (no-RAG) or over a built retriever.

    Returns {"answer": str, "chunks": [...], "hyde_doc": str | None, "standalone_query": str | None}
    (empty chunks and hyde_doc=None for the no-RAG path; hyde_doc holds the generated passage when
    HyDE ran; standalone_query holds the condensed follow-up when `history` changed it). `reranker`
    is injected for reuse; built lazily when None.
    """
    prep = _prepare(retriever, rp, gp, reranker, history)
    return {
        "answer": prep["llm"].generate(prep["prompt"]),
        "chunks": prep["chunks"],
        "hyde_doc": prep["hyde_doc"],
        "standalone_query": prep["standalone_query"],
    }


def answer_query_stream(
    retriever: Retriever | None,
    rp: RetrievalParams,
    gp: GenerationParams,
    reranker: Reranker | None = None,
    history: list[dict[str, str]] | None = None,
) -> Iterator[dict[str, Any]]:
    """Answer one query, streaming the response token by token.

    Retrieval/rerank/HyDE (and the history condense step) finish first, then generation streams.
    Yields exactly one meta event {"type": "meta", "chunks": [...], "hyde_doc": str | None,
    "standalone_query": str | None} followed by one {"type": "token", "text": str} per chunk.
    """
    prep = _prepare(retriever, rp, gp, reranker, history)
    yield {
        "type": "meta", "chunks": prep["chunks"],
        "hyde_doc": prep["hyde_doc"], "standalone_query": prep["standalone_query"],
    }
    for delta in prep["llm"].generate_stream(prep["prompt"]):
        yield {"type": "token", "text": delta}
