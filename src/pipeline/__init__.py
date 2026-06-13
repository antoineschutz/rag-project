"""Pipeline orchestration: the two-phase entry point.

`build_index` (src/retrieval/factory.py) builds the retriever; `answer_query` runs one query
against it. Both are re-exported here so callers can `from src.pipeline import build_index,
answer_query`.
"""

from src.pipeline.query import answer_query, answer_query_stream
from src.retrieval.factory import build_index

__all__ = ["answer_query", "answer_query_stream", "build_index"]
