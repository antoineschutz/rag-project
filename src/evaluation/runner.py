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


def answer_for_config(
    questions: list[dict[str, Any]],
    cfg: dict[str, Any],
    cache: AnswerCache,
    *,
    fresh: bool = False,
    on_event: OnEvent | None = None,
) -> list[str]:
    """Answer each question under one config, returning answers aligned with `questions`.

    Cached answers are reused unless `fresh` is set, which regenerates and refreshes the
    cache. The index is built lazily and skipped for an all-cached run or a no_rag config.
    """
    retriever: Any | None = None
    index_built = False
    answers: list[str] = []

    for qa in questions:
        key = AnswerCache.key(qa["question"], cfg)
        cached = cache.get(key)
        if not fresh and cached is not None:
            if on_event is not None:
                on_event("cached", qa, None)
            answers.append(cached)
            continue

        index_params, rp, gp = split_config(cfg, qa["question"])
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
