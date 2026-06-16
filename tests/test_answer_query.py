import pytest

from src.config import GenerationParams, RetrievalParams
from src.llm.client import LLMClient
from src.pipeline import answer_query
from src.retrieval.retriever_hybrid import RetrieverHybrid


@pytest.fixture
def prompts(monkeypatch):
    """Stub LLM generation (no Ollama); record the prompts it was given."""
    seen: list[str] = []

    def fake_generate(self, prompt: str) -> str:
        seen.append(prompt)
        return "GENERATED"

    monkeypatch.setattr(LLMClient, "generate", fake_generate)
    return seen


class _Retriever:
    """Non-hybrid retriever that records its retrieve() calls."""

    def __init__(self, results=None):
        self.results = results or [{"text": "ctx-a", "source": "a", "score": 0.9}]
        self.calls: list[dict] = []

    def retrieve(self, query, top_k, source=None):
        self.calls.append({"query": query, "top_k": top_k, "source": source})
        return self.results


class _Hybrid(RetrieverHybrid):
    """Passes the isinstance(..., RetrieverHybrid) check; records fusion/alpha/source."""

    def __init__(self):
        self.results = [{"text": "ctx-h", "source": "h", "score": 1.0}]
        self.calls: list[dict] = []

    def retrieve(self, query, top_k, source=None, *, fusion=None, alpha=None):
        self.calls.append({"query": query, "top_k": top_k, "source": source, "fusion": fusion, "alpha": alpha})
        return self.results


def test_no_rag_skips_retrieval(prompts):
    out = answer_query(None, RetrievalParams(query="q"), GenerationParams(no_rag=True))
    assert out["chunks"] == []
    assert out["answer"] == "GENERATED"


def test_rag_without_retriever_raises(prompts):
    # no_rag is False but no retriever was supplied -> caller bug, must not silently no-rag
    with pytest.raises(ValueError):
        answer_query(None, RetrievalParams(query="q"), GenerationParams(no_rag=False))


def test_rag_returns_chunks_and_grounds_the_prompt(prompts):
    ret = _Retriever()
    out = answer_query(ret, RetrievalParams(query="what is X?"), GenerationParams())
    assert out["chunks"] == ret.results
    assert ret.calls[0]["query"] == "what is X?"
    assert "ctx-a" in prompts[-1]  # retrieved context fed into the RAG prompt


def test_rerank_widens_pool_then_trims(prompts):
    ret = _Retriever(results=[{"text": f"c{i}", "source": "s", "score": 1.0} for i in range(30)])

    class FakeReranker:
        def __init__(self):
            self.called = None

        def rerank(self, query, results, top_k):
            self.called = (query, len(results), top_k)
            return results[:top_k]

    rr = FakeReranker()
    out = answer_query(ret, RetrievalParams(query="q", top_k=5, rerank=True), GenerationParams(), reranker=rr)
    assert ret.calls[0]["top_k"] == 15  # retrieval_k = top_k * 3
    assert rr.called == ("q", 30, 5)  # reranker sees the full pool, returns top_k
    assert len(out["chunks"]) == 5


def test_hybrid_receives_fusion_and_alpha(prompts):
    h = _Hybrid()
    answer_query(h, RetrievalParams(query="q", fusion="weighted", alpha=0.7), GenerationParams())
    assert h.calls[0]["fusion"] == "weighted"
    assert h.calls[0]["alpha"] == 0.7


def test_source_forwarded_to_retriever(prompts):
    ret = _Retriever()
    answer_query(ret, RetrievalParams(query="q", source=["a.pdf"]), GenerationParams())
    assert ret.calls[0]["source"] == ["a.pdf"]


def test_source_forwarded_to_hybrid(prompts):
    h = _Hybrid()
    answer_query(h, RetrievalParams(query="q", source="a.pdf"), GenerationParams())
    assert h.calls[0]["source"] == "a.pdf"


def test_hyde_replaces_retrieval_text(prompts):
    ret = _Retriever()
    answer_query(ret, RetrievalParams(query="real query", hyde=True), GenerationParams())
    # the retriever embeds the generated hypothetical doc, not the raw query
    assert ret.calls[0]["query"] == "GENERATED"
