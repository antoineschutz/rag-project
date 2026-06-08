import logging
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi

from src.config import config
from src.ingestion.loader import load_documents
from src.chunking.chunk import chunk_documents

logger = logging.getLogger(__name__)


class RetrieverBM25:
    """BM25 lexical retriever — no embeddings, purely token-based."""

    def __init__(self, chunked_docs: list[dict[str, str]]) -> None:
        """Build BM25 index from tokenized chunk texts."""
        self.chunked_docs = chunked_docs
        tokenized = [doc["text"].lower().split() for doc in chunked_docs]
        self.bm25 = BM25Okapi(tokenized)
        logger.info("BM25 index built over %d chunks.", len(chunked_docs))

    def retrieve(self, query: str, top_k: int = config.TOP_K) -> list[dict[str, Any]]:
        """Return top_k chunks ranked by BM25 score for the given query string."""
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {
                "text": self.chunked_docs[i]["text"],
                "source": self.chunked_docs[i]["source"],
                "score": float(scores[i]),
            }
            for i in top_indices
        ]


def build_bm25_retriever(data_path: str) -> RetrieverBM25:
    """Load and chunk documents, then build a BM25 index. No embeddings or cache needed."""
    docs = load_documents(data_path)
    chunked = chunk_documents(docs)
    return RetrieverBM25(chunked)
