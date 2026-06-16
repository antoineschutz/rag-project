"""Shared answer loop for the eval and benchmark scripts.

Answers a question set under one pipeline config, serving from the LLM answer cache
and building the retrieval index lazily on the first cache miss. An optional `on_event`
callback reports progress so callers can print in their own format.
"""

from collections.abc import Callable
from typing import Any

from src.config import split_config
from src.config.params import IndexParams
from src.pipeline import answer_query
from src.retrieval.factory import build_index
from src.utils.answer_cache import AnswerCache

# on_event(event, qa, index_params): event is "cached", "build", or "generate".
# index_params is set only for "build", None otherwise.
OnEvent = Callable[[str, dict[str, Any], IndexParams | None], None]


def _parse_sources(source: str) -> list[str]:
    """Split a QA pair's source field into filenames; a compound 'a.pdf + b.pdf' -> [a, b]."""
    return [s.strip() for s in source.split("+") if s.strip()]


def answer_for_config(
    questions: list[dict[str, Any]],
    cfg: dict[str, Any],
    cache: AnswerCache,
    *,
    fresh: bool = False,
    use_source: bool = False,
    on_event: OnEvent | None = None,
) -> list[str]:
    """Answer each question under one config, returning answers aligned with `questions`.

    Cached answers are reused unless `fresh` is set, which regenerates and refreshes the
    cache. The index is built lazily and skipped for an all-cached run or a no_rag config.

    When `use_source` is set, each question's labeled `source` is injected as a retrieval
    filter (the oracle source-filter experiment). Since source is a RetrievalParams knob (not
    an IndexParams one), the shared index is unchanged; only the per-question filter and the
    answer-cache key differ, so filtered answers cache separately from the unfiltered run.
    """
    retriever: Any | None = None
    index_built = False
    answers: list[str] = []

    for qa in questions:
        q_cfg = cfg
        if use_source and qa.get("source"):
            q_cfg = {**cfg, "source": _parse_sources(qa["source"])}
        key = AnswerCache.key(qa["question"], q_cfg)
        cached = cache.get(key)
        if not fresh and cached is not None:
            if on_event is not None:
                on_event("cached", qa, None)
            answers.append(cached)
            continue

        index_params, rp, gp = split_config(q_cfg, qa["question"])
        if not index_built:
            if not gp.no_rag:
                if on_event is not None:
                    on_event("build", qa, index_params)
                retriever = build_index(index_params)
            index_built = True

        if on_event is not None:
            on_event("generate", qa, None)
        answer = answer_query(retriever, rp, gp)["answer"]
        cache.set(key, answer)
        answers.append(answer)

    return answers
