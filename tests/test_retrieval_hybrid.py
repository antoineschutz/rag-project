import numpy as np
import pytest

from src.retrieval.retriever import Retriever
from src.retrieval.retriever_bm25 import RetrieverBM25
from src.retrieval.retriever_hybrid import RetrieverHybrid

DOCS = [
    {"text": "The cat sat on the mat", "source": "a.txt"},
    {"text": "Dogs are loyal and friendly animals", "source": "b.txt"},
    {"text": "Neural networks learn from data using gradient descent", "source": "c.txt"},
    {"text": "The cat chased the dog across the yard", "source": "d.txt"},
    {"text": "Gradient descent optimizes neural network weights", "source": "e.txt"},
]

DIM = 5
EMBEDDINGS = np.eye(len(DOCS), DIM, dtype=np.float32)
# Query embedding identical to doc at index 2 (c.txt)
QUERY_EMBEDDING = EMBEDDINGS[2:3]


@pytest.fixture
def dense() -> Retriever:
    return Retriever(DOCS, EMBEDDINGS)


@pytest.fixture
def bm25() -> RetrieverBM25:
    return RetrieverBM25(DOCS)


@pytest.fixture
def hybrid_rrf(dense: Retriever, bm25: RetrieverBM25) -> RetrieverHybrid:
    return RetrieverHybrid(dense, bm25, fusion="rrf")


@pytest.fixture
def hybrid_weighted(dense: Retriever, bm25: RetrieverBM25) -> RetrieverHybrid:
    return RetrieverHybrid(dense, bm25, fusion="weighted", alpha=0.5)


def test_rrf_ranking(hybrid_rrf: RetrieverHybrid) -> None:
    results = hybrid_rrf.retrieve("neural network gradient descent", QUERY_EMBEDDING, top_k=5)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_weighted_ranking(hybrid_weighted: RetrieverHybrid) -> None:
    results = hybrid_weighted.retrieve("neural network gradient descent", QUERY_EMBEDDING, top_k=5)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_rrf_top_k(hybrid_rrf: RetrieverHybrid) -> None:
    for k in (1, 3, 5):
        assert len(hybrid_rrf.retrieve("cat", QUERY_EMBEDDING, top_k=k)) == k


def test_weighted_top_k(hybrid_weighted: RetrieverHybrid) -> None:
    for k in (1, 3, 5):
        assert len(hybrid_weighted.retrieve("cat", QUERY_EMBEDDING, top_k=k)) == k


def test_rrf_result_keys(hybrid_rrf: RetrieverHybrid) -> None:
    results = hybrid_rrf.retrieve("cat", QUERY_EMBEDDING, top_k=1)
    assert set(results[0].keys()) == {"text", "source", "score"}


def test_rrf_boosts_overlap(dense: Retriever, bm25: RetrieverBM25) -> None:
    # c.txt ranks #1 in dense (QUERY_EMBEDDING matches it exactly) and top-2 in BM25
    # for the query "neural network gradient descent" — it should win the fused ranking
    retriever = RetrieverHybrid(dense, bm25, fusion="rrf")
    results = retriever.retrieve("neural network gradient descent", QUERY_EMBEDDING, top_k=5)
    assert results[0]["source"] == "c.txt"
