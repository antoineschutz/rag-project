"""Tests for conversation memory: history-aware query condensing in the pipeline.

The LLM is stubbed so `condense_question` (and HyDE) return "GENERATED"; these tests check the
WIRING (when condense runs, what query feeds retrieval/HyDE/rerank, what the prompt contains),
not answer quality. Mirrors the fixtures in test_answer_query.py.
"""

import json

import pytest
from fastapi.testclient import TestClient

from src.api import server
from src.config import GenerationParams, RetrievalParams
from src.llm.client import LLMClient
from src.pipeline import answer_query, answer_query_stream

HISTORY = [
    {"role": "user", "content": "What is RAG-Token?"},
    {"role": "assistant", "content": "RAG-Token marginalizes over documents per token."},
]


@pytest.fixture
def prompts(monkeypatch):
    """Stub LLM generation (no Ollama); record every prompt it was given, return a marker."""
    seen: list[str] = []

    def fake_generate(self, prompt: str) -> str:
        seen.append(prompt)
        return "GENERATED"

    monkeypatch.setattr(LLMClient, "generate", fake_generate)
    return seen


class _Retriever:
    """Non-hybrid retriever that records the query it was asked to retrieve."""

    def __init__(self, results=None):
        self.results = results or [{"text": "ctx-a", "source": "a", "score": 0.9}]
        self.calls: list[dict] = []

    def retrieve(self, query, top_k, source=None):
        self.calls.append({"query": query, "top_k": top_k, "source": source})
        return self.results


def test_no_history_retrieves_with_the_raw_query(prompts):
    # Regression: with no history the path is identical to single-shot (no condense call).
    ret = _Retriever()
    out = answer_query(ret, RetrievalParams(query="what is X?"), GenerationParams())
    assert ret.calls[0]["query"] == "what is X?"
    assert out["standalone_query"] is None
    assert len(prompts) == 1  # only the answer generate; condense did not run
    assert all("Standalone question" not in p for p in prompts)


def test_history_condenses_before_retrieval(prompts):
    ret = _Retriever()
    out = answer_query(
        ret, RetrievalParams(query="how does it differ?"), GenerationParams(), history=HISTORY
    )
    assert ret.calls[0]["query"] == "GENERATED"  # retrieval uses the condensed standalone query
    assert out["standalone_query"] == "GENERATED"  # surfaced because it changed
    assert "Standalone question" in prompts[0]  # the first LLM call was the condense prompt


def test_no_rag_includes_history_and_skips_retrieval(prompts):
    out = answer_query(
        None, RetrievalParams(query="q"), GenerationParams(no_rag=True), history=HISTORY
    )
    assert out["chunks"] == []
    assert out["standalone_query"] is None  # no retrieval, so nothing to condense
    assert len(prompts) == 1  # no condense, just the answer
    assert "Conversation so far" in prompts[-1]
    assert "RAG-Token marginalizes over documents per token." in prompts[-1]


def test_hyde_runs_on_the_condensed_query(prompts):
    ret = _Retriever()
    answer_query(
        ret, RetrievalParams(query="how does it differ?", hyde=True), GenerationParams(),
        history=HISTORY,
    )
    # LLM call order: condense, then HyDE, then the answer.
    assert "Standalone question" in prompts[0]
    assert "Passage:" in prompts[1]  # the HyDE prompt
    assert "GENERATED" in prompts[1]  # HyDE saw the condensed query, not the raw follow-up
    assert "how does it differ?" not in prompts[1]
    assert ret.calls[0]["query"] == "GENERATED"


def test_rerank_uses_the_condensed_query(prompts):
    ret = _Retriever(results=[{"text": f"c{i}", "source": "s", "score": 1.0} for i in range(30)])

    class FakeReranker:
        def __init__(self):
            self.query = None

        def rerank(self, query, results, top_k):
            self.query = query
            return results[:top_k]

    rr = FakeReranker()
    answer_query(
        ret, RetrievalParams(query="how does it differ?", top_k=5, rerank=True),
        GenerationParams(), reranker=rr, history=HISTORY,
    )
    assert rr.query == "GENERATED"  # the cross-encoder scores against the standalone query


def test_history_window_caps_the_turns(prompts):
    long_history = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"msg{i}"} for i in range(20)
    ]
    answer_query(None, RetrievalParams(query="q"), GenerationParams(no_rag=True), history=long_history)
    answer_prompt = prompts[-1]
    assert "msg19" in answer_prompt and "msg14" in answer_prompt  # last 6 messages kept
    assert "msg13" not in answer_prompt and "msg0" not in answer_prompt  # older turns dropped


def test_stream_meta_carries_standalone_query(monkeypatch):
    monkeypatch.setattr(LLMClient, "generate", lambda self, p: "GENERATED")  # condense
    monkeypatch.setattr(LLMClient, "generate_stream", lambda self, p: iter(["A", "B"]))
    ret = _Retriever()
    events = list(
        answer_query_stream(ret, RetrievalParams(query="follow up"), GenerationParams(), history=HISTORY)
    )
    assert events[0]["type"] == "meta"
    assert events[0]["standalone_query"] == "GENERATED"
    assert [e["text"] for e in events if e["type"] == "token"] == ["A", "B"]


# --- API threading (server stubs the pipeline so no models/LLM run) ---

API_HISTORY = [
    {"role": "user", "content": "What is RAG-Token?"},
    {"role": "assistant", "content": "RAG-Token marginalizes per token."},
]


def test_query_endpoint_forwards_history_and_surfaces_standalone(monkeypatch):
    captured: dict = {}

    def fake_answer(retriever, rp, gp, reranker=None, history=None):
        captured["history"] = history
        return {"answer": "A", "chunks": [], "hyde_doc": None, "standalone_query": "STANDALONE"}

    monkeypatch.setattr(server, "_build_pipeline", lambda q, cfg: (None, None, None, None))
    monkeypatch.setattr(server, "answer_query", fake_answer)

    client = TestClient(server.app)
    resp = client.post("/query", json={"query": "how does it differ?", "config": "best", "history": API_HISTORY})

    assert resp.status_code == 200
    assert captured["history"] == API_HISTORY
    assert resp.json()["standalone_query"] == "STANDALONE"


def test_query_endpoint_without_history_passes_none(monkeypatch):
    captured: dict = {}

    def fake_answer(retriever, rp, gp, reranker=None, history=None):
        captured["history"] = history
        return {"answer": "A", "chunks": [], "hyde_doc": None, "standalone_query": None}

    monkeypatch.setattr(server, "_build_pipeline", lambda q, cfg: (None, None, None, None))
    monkeypatch.setattr(server, "answer_query", fake_answer)

    client = TestClient(server.app)
    resp = client.post("/query", json={"query": "q", "config": "best"})

    assert resp.status_code == 200
    assert captured["history"] is None  # omitted history reaches the pipeline as None
    assert resp.json()["standalone_query"] is None


def test_query_stream_endpoint_forwards_history(monkeypatch):
    captured: dict = {}

    def fake_stream(retriever, rp, gp, reranker=None, history=None):
        captured["history"] = history
        yield {"type": "meta", "chunks": [], "hyde_doc": None, "standalone_query": "S"}
        yield {"type": "token", "text": "x"}

    monkeypatch.setattr(server, "_build_pipeline", lambda q, cfg: (None, None, None, None))
    monkeypatch.setattr(server, "answer_query_stream", fake_stream)

    client = TestClient(server.app)
    resp = client.post(
        "/query/stream", json={"query": "q2", "config": "best", "history": API_HISTORY}
    )

    assert resp.status_code == 200
    assert captured["history"] == API_HISTORY
    lines = [json.loads(ln) for ln in resp.text.splitlines() if ln]
    assert lines[0]["standalone_query"] == "S"


def test_invalid_history_role_is_rejected():
    # The Turn model restricts role to user/assistant; a bad role is a 422 at the schema layer.
    client = TestClient(server.app)
    resp = client.post(
        "/query", json={"query": "q", "history": [{"role": "system", "content": "x"}]}
    )
    assert resp.status_code == 422
