import pytest

from src.config import IndexParams
from src.api import state


@pytest.fixture(autouse=True)
def clear_caches():
    """The state caches are module-level; reset them around every test."""
    state._embedders.clear()
    state._retrievers.clear()
    state._reranker = None
    yield
    state._embedders.clear()
    state._retrievers.clear()
    state._reranker = None


def test_get_embedder_memoizes_per_model(monkeypatch):
    built = []

    class FakeEmbedder:
        def __init__(self, model_name):
            built.append(model_name)
            self.model_name = model_name

    monkeypatch.setattr(state, "Embedder", FakeEmbedder)

    a = state.get_embedder("m1")
    b = state.get_embedder("m1")
    assert a is b and built == ["m1"]  # loaded once, reused

    c = state.get_embedder("m2")
    assert c is not a and built == ["m1", "m2"]


def test_get_retriever_memoizes_by_index_params(monkeypatch):
    builds = []
    monkeypatch.setattr(state, "build_index", lambda params, embedder=None: builds.append(params) or object())
    monkeypatch.setattr(state, "get_embedder", lambda m: "emb")

    r1 = state.get_retriever(IndexParams(retriever="dense"))
    r2 = state.get_retriever(IndexParams(retriever="dense"))  # equal (frozen) params -> cache hit
    assert r1 is r2 and len(builds) == 1

    r3 = state.get_retriever(IndexParams(retriever="bm25"))
    assert r3 is not r1 and len(builds) == 2


def test_bm25_retriever_skips_embedder(monkeypatch):
    seen = {}
    monkeypatch.setattr(state, "build_index", lambda params, embedder=None: seen.update(embedder=embedder) or object())
    monkeypatch.setattr(state, "get_embedder", lambda m: pytest.fail("bm25 must not load an embedder"))

    state.get_retriever(IndexParams(retriever="bm25"))
    assert seen["embedder"] is None


def test_get_reranker_is_singleton(monkeypatch):
    built = []
    monkeypatch.setattr(state, "Reranker", lambda: built.append(1) or object())
    a = state.get_reranker()
    b = state.get_reranker()
    assert a is b and len(built) == 1


def test_reset_clears_retrievers_but_keeps_embedders(monkeypatch):
    monkeypatch.setattr(state, "Embedder", lambda model_name: object())
    monkeypatch.setattr(state, "build_index", lambda params, embedder=None: object())

    state.get_embedder("m")
    state.get_retriever(IndexParams(retriever="dense"))
    assert state._embedders and state._retrievers

    state.reset()
    assert state._retrievers == {}  # stale indexes dropped
    assert state._embedders  # expensive models kept
