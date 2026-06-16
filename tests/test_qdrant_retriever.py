import numpy as np
import pytest

from src.retrieval.retriever_qdrant import RetrieverQdrant


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
QUERY = EMBEDDINGS[2:3]  # shape (1, DIM), identical to doc 2

# Uses a real in-process Qdrant (":memory:") client, no server. Exercises the vector-level
# seam (_retrieve_vec) directly with synthetic embeddings, like test_retrieval.py.


@pytest.fixture
def qdrant_retriever():
    return RetrieverQdrant(DOCS, EMBEDDINGS)


def test_retrieve_ranking(qdrant_retriever):
    results = qdrant_retriever._retrieve_vec(QUERY, top_k=5)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_top_k(qdrant_retriever):
    results = qdrant_retriever._retrieve_vec(QUERY, top_k=3)
    assert len(results) == 3


def test_retrieve_score_keys(qdrant_retriever):
    results = qdrant_retriever._retrieve_vec(QUERY, top_k=2)
    for r in results:
        assert "text" in r
        assert "source" in r
        assert "score" in r


def test_retrieve_best_match_2d_query(qdrant_retriever):
    # (1, dim) query, as Embedder.embed_query returns; the squeeze must handle it
    results = qdrant_retriever._retrieve_vec(QUERY, top_k=1)
    assert results[0]["text"] == "about birds"


def test_retrieve_best_match_1d_query(qdrant_retriever):
    # flat (dim,) query; locks the other branch of the ndim squeeze
    results = qdrant_retriever._retrieve_vec(QUERY[0], top_k=1)
    assert results[0]["text"] == "about birds"


def test_source_filter_single(qdrant_retriever):
    results = qdrant_retriever._retrieve_vec(QUERY, top_k=5, source="a.pdf")
    assert {r["source"] for r in results} == {"a.pdf"}


def test_source_filter_multiple(qdrant_retriever):
    results = qdrant_retriever._retrieve_vec(QUERY, top_k=5, source=["a.pdf", "c.pdf"])
    assert {r["source"] for r in results} <= {"a.pdf", "c.pdf"}
    assert results[0]["source"] == "c.pdf"  # the exact match still ranks first within the filter
