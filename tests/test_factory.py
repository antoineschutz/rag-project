import pytest

from src.config import IndexParams
from src.retrieval import factory


@pytest.fixture
def stub_builders(monkeypatch):
    """Replace the four build_* functions with markers so we test only the dispatch."""
    calls: dict[str, tuple] = {}

    def maker(name):
        def f(*args, **kwargs):
            calls[name] = (args, kwargs)
            return f"{name}-retriever"
        return f

    monkeypatch.setattr(factory, "build_bm25_retriever", maker("bm25"))
    monkeypatch.setattr(factory, "build_cosine_retriever", maker("cosine"))
    monkeypatch.setattr(factory, "build_faiss_retriever", maker("faiss"))
    monkeypatch.setattr(factory, "build_hybrid_retriever", maker("hybrid"))
    monkeypatch.setattr(factory, "build_qdrant_retriever", maker("qdrant"))
    monkeypatch.setattr(factory, "Embedder", lambda model_name=None: f"embedder:{model_name}")
    return calls


def test_bm25_needs_no_embedder(stub_builders):
    assert factory.build_index(IndexParams(retriever="bm25")) == "bm25-retriever"
    assert "cosine" not in stub_builders and "faiss" not in stub_builders


def test_dense_numpy_dispatch(stub_builders):
    assert factory.build_index(IndexParams(retriever="dense", store="numpy")) == "cosine-retriever"


def test_dense_faiss_dispatch(stub_builders):
    assert factory.build_index(IndexParams(retriever="dense", store="faiss")) == "faiss-retriever"


def test_dense_qdrant_dispatch(stub_builders):
    assert factory.build_index(IndexParams(retriever="dense", store="qdrant")) == "qdrant-retriever"


def test_hybrid_dispatch(stub_builders):
    assert factory.build_index(IndexParams(retriever="hybrid")) == "hybrid-retriever"


def test_hybrid_forwards_store(stub_builders):
    factory.build_index(IndexParams(retriever="hybrid", store="qdrant"))
    args, _ = stub_builders["hybrid"]
    assert "qdrant" in args  # store is forwarded into the hybrid builder's dense arm


def test_creates_embedder_when_none_passed(stub_builders):
    factory.build_index(IndexParams(retriever="dense", embed_model="some-model"))
    args, _ = stub_builders["cosine"]
    assert "embedder:some-model" in args


def test_reuses_passed_embedder(stub_builders):
    factory.build_index(IndexParams(retriever="dense"), embedder="MY_EMB")
    args, _ = stub_builders["cosine"]
    assert "MY_EMB" in args  # passed-in embedder used, not a freshly built one
