import logging
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi

from src.config import BASE
from src.ingestion.loader import load_documents
from src.chunking.chunk import chunk_documents
from src.retrieval._filter import filter_by_source, normalize_sources

logger = logging.getLogger(__name__)


class RetrieverBM25:
    """BM25 lexical retriever — no embeddings, purely token-based."""

    def __init__(self, chunked_docs: list[dict[str, str]]) -> None:
        """Build BM25 index from tokenized chunk texts."""
        self.chunked_docs = chunked_docs
        tokenized = [doc["text"].lower().split() for doc in chunked_docs]
        self.bm25 = BM25Okapi(tokenized)
        logger.info("BM25 index built over %d chunks.", len(chunked_docs))

    def retrieve(
        self,
        query: str,
        top_k: int = BASE.top_k,
        source: str | list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return top_k chunks ranked by BM25 score for the given query string.

        With a source filter, the full ranking is computed then non-matching sources are
        dropped before taking top_k.
        """
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        ranked = np.argsort(scores)[::-1]
        if normalize_sources(source) is None:
            ranked = ranked[:top_k]
        results = [
            {
                "text": self.chunked_docs[i]["text"],
                "source": self.chunked_docs[i]["source"],
                "score": float(scores[i]),
            }
            for i in ranked
        ]
        return filter_by_source(results, source)[:top_k]


def build_bm25_retriever(
    data_path: str,
    chunk_max_tokens: int | None = None,
) -> RetrieverBM25:
    """Load and chunk documents, then build a BM25 index. No embeddings or cache needed."""
    docs = load_documents(data_path)
    chunked = chunk_documents(docs, chunk_max_tokens=chunk_max_tokens)
    return RetrieverBM25(chunked)
