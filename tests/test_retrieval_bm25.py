import pytest

from src.retrieval.retriever_bm25 import RetrieverBM25

DOCS = [
    {"text": "The cat sat on the mat", "source": "a.txt"},
    {"text": "Dogs are loyal and friendly animals", "source": "b.txt"},
    {"text": "Neural networks learn from data using gradient descent", "source": "c.txt"},
    {"text": "The cat chased the dog across the yard", "source": "d.txt"},
    {"text": "Gradient descent optimizes neural network weights", "source": "e.txt"},
]


@pytest.fixture
def retriever() -> RetrieverBM25:
    return RetrieverBM25(DOCS)


def test_ranking_is_descending(retriever: RetrieverBM25) -> None:
    results = retriever.retrieve("cat mat", top_k=5)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_top_k_respected(retriever: RetrieverBM25) -> None:
    for k in (1, 3, 5):
        assert len(retriever.retrieve("cat", top_k=k)) == k


def test_best_match(retriever: RetrieverBM25) -> None:
    results = retriever.retrieve("gradient descent neural network", top_k=5)
    top_sources = {results[0]["source"], results[1]["source"]}
    assert top_sources == {"c.txt", "e.txt"}


def test_result_keys(retriever: RetrieverBM25) -> None:
    results = retriever.retrieve("dog", top_k=1)
    assert set(results[0].keys()) == {"text", "source", "score"}
