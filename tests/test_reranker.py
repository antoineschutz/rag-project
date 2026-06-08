import pytest

from src.reranker.reranker import Reranker

QUERY = "neural networks and gradient descent"

RESULTS = [
    {"text": "The cat sat on the mat", "source": "a.txt", "score": 0.9},
    {"text": "Dogs are loyal and friendly animals", "source": "b.txt", "score": 0.8},
    {"text": "Neural networks learn from data using gradient descent", "source": "c.txt", "score": 0.3},
    {"text": "The cat chased the dog across the yard", "source": "d.txt", "score": 0.7},
    {"text": "Gradient descent optimizes neural network weights", "source": "e.txt", "score": 0.2},
]


@pytest.fixture(scope="module")
def reranker() -> Reranker:
    return Reranker()


def test_ranking_is_descending(reranker: Reranker) -> None:
    results = reranker.rerank(QUERY, RESULTS, top_k=5)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_top_k_respected(reranker: Reranker) -> None:
    for k in (1, 3, 5):
        assert len(reranker.rerank(QUERY, RESULTS, top_k=k)) == k


def test_scores_replaced(reranker: Reranker) -> None:
    original_scores = {r["text"]: r["score"] for r in RESULTS}
    reranked = reranker.rerank(QUERY, RESULTS, top_k=5)
    for r in reranked:
        assert r["score"] != original_scores[r["text"]]


def test_result_keys(reranker: Reranker) -> None:
    results = reranker.rerank(QUERY, RESULTS, top_k=1)
    assert set(results[0].keys()) == {"text", "source", "score"}
