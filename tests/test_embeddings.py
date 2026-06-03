import pytest

from src.embeddings.embed import Embedder


@pytest.fixture(scope="module")
def embedder():
    return Embedder()


@pytest.fixture(scope="module")
def dim(embedder):
    return embedder.embed_query("probe").shape[1]


def test_embed_documents_shape(embedder, dim):
    result = embedder.embed_documents(["hello", "world", "foo"])
    assert result.shape == (3, dim)


def test_embed_query_shape(embedder, dim):
    result = embedder.embed_query("hello")
    assert result.shape == (1, dim)


def test_embed_documents_empty(embedder, dim):
    result = embedder.embed_documents([])
    assert result.shape[0] == 0
