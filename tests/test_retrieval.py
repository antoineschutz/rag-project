import numpy as np
import pytest

from src.retrieval.retriever import Retriever
from src.retrieval.retriever_faiss import RetrieverFAISS


DIM = 8

DOCS = [
    {"text": "about cats", "source": "a.pdf"},
    {"text": "about dogs", "source": "b.pdf"},
    {"text": "about birds", "source": "c.pdf"},
    {"text": "about fish", "source": "d.pdf"},
    {"text": "about snakes", "source": "e.pdf"},
]

# embeddings: doc 2 is most similar to the query
EMBEDDINGS = np.eye(len(DOCS), DIM, dtype="float32")
QUERY = EMBEDDINGS[2:3]  # shape (1, DIM) — identical to doc 2


@pytest.fixture
def retriever():
    return Retriever(DOCS, EMBEDDINGS)


@pytest.fixture
def faiss_retriever():
    return RetrieverFAISS(DOCS, EMBEDDINGS)


def test_retrieve_ranking(retriever):
    results = retriever.retrieve(QUERY, top_k=5)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_top_k(retriever):
    results = retriever.retrieve(QUERY, top_k=3)
    assert len(results) == 3


def test_retrieve_score_keys(retriever):
    results = retriever.retrieve(QUERY, top_k=2)
    for r in results:
        assert "text" in r
        assert "source" in r
        assert "score" in r


def test_retrieve_best_match(retriever):
    results = retriever.retrieve(QUERY, top_k=1)
    assert results[0]["text"] == "about birds"


def test_faiss_retrieve_ranking(faiss_retriever):
    results = faiss_retriever.retrieve(QUERY[0], top_k=5)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_faiss_retrieve_top_k(faiss_retriever):
    results = faiss_retriever.retrieve(QUERY[0], top_k=3)
    assert len(results) == 3


def test_faiss_retrieve_best_match(faiss_retriever):
    results = faiss_retriever.retrieve(QUERY[0], top_k=1)
    assert results[0]["text"] == "about birds"
