"""Tests for streaming generation across the LLM client, the pipeline, and the /query/stream API.

No Ollama/OpenAI or heavy models run: the backend SDK, the LLM client, and the pipeline setup
are stubbed so only the streaming wiring (generators and NDJSON framing) is exercised.
"""

import json
import types

from fastapi.testclient import TestClient

from src.api import server
from src.config import GenerationParams, RetrievalParams
from src.llm.client import LLMClient
from src.pipeline import answer_query_stream


def _fake_ollama_chat(deltas):
    """Build a fake ollama.chat that streams `deltas` as message-content chunks."""
    def chat(model, messages, options, stream):
        assert stream is True
        for d in deltas:
            yield types.SimpleNamespace(message=types.SimpleNamespace(content=d))
    return chat


def test_generate_stream_yields_deltas(monkeypatch):
    import ollama
    monkeypatch.setattr(ollama, "chat", _fake_ollama_chat(["Hel", "lo", " world"]))
    client = LLMClient(backend="ollama", model="x")
    assert list(client.generate_stream("p")) == ["Hel", "lo", " world"]


def test_generate_joins_the_stream(monkeypatch):
    import ollama
    monkeypatch.setattr(ollama, "chat", _fake_ollama_chat(["Hel", "lo", " world"]))
    client = LLMClient(backend="ollama", model="x")
    assert client.generate("p") == "Hello world"


def test_generate_stream_skips_empty_deltas(monkeypatch):
    import ollama
    monkeypatch.setattr(ollama, "chat", _fake_ollama_chat(["a", "", None, "b"]))
    client = LLMClient(backend="ollama", model="x")
    assert list(client.generate_stream("p")) == ["a", "b"]


class _Retriever:
    """Minimal non-hybrid retriever returning a fixed result."""

    def __init__(self):
        self.results = [{"text": "ctx-a", "source": "a", "score": 0.9}]

    def retrieve(self, query, top_k):
        return self.results


def test_answer_query_stream_meta_then_tokens(monkeypatch):
    def fake_stream(self, prompt):
        yield from ["A", "B"]

    monkeypatch.setattr(LLMClient, "generate_stream", fake_stream)
    ret = _Retriever()
    events = list(answer_query_stream(ret, RetrievalParams(query="q"), GenerationParams()))

    assert events[0] == {"type": "meta", "chunks": ret.results, "hyde_doc": None, "standalone_query": None}
    assert [e["text"] for e in events[1:]] == ["A", "B"]
    assert all(e["type"] == "token" for e in events[1:])


def test_query_stream_endpoint_frames_meta_and_tokens(monkeypatch):
    def fake_stream(retriever, rp, gp, reranker=None, history=None):
        yield {"type": "meta", "chunks": [{"text": "c", "source": "s", "score": 1.0}], "hyde_doc": None}
        yield {"type": "token", "text": "Hel"}
        yield {"type": "token", "text": "lo"}

    monkeypatch.setattr(server, "_build_pipeline", lambda q, cfg: (None, None, None, None))
    monkeypatch.setattr(server, "answer_query_stream", fake_stream)

    client = TestClient(server.app)
    resp = client.post("/query/stream", json={"query": "q", "config": "best"})

    assert resp.status_code == 200
    lines = [json.loads(ln) for ln in resp.text.splitlines() if ln]
    assert lines[0]["type"] == "meta"
    assert "config" in lines[0]  # the endpoint injects the resolved config into the meta event
    assert lines[0]["chunks"] == [{"text": "c", "source": "s", "score": 1.0}]
    assert [ln["text"] for ln in lines[1:]] == ["Hel", "lo"]


def test_query_stream_endpoint_reports_midstream_error(monkeypatch):
    def boom(retriever, rp, gp, reranker=None, history=None):
        yield {"type": "meta", "chunks": [], "hyde_doc": None}
        raise RuntimeError("kaboom")

    monkeypatch.setattr(server, "_build_pipeline", lambda q, cfg: (None, None, None, None))
    monkeypatch.setattr(server, "answer_query_stream", boom)

    client = TestClient(server.app)
    resp = client.post("/query/stream", json={"query": "q", "config": "best"})

    assert resp.status_code == 200
    lines = [json.loads(ln) for ln in resp.text.splitlines() if ln]
    assert lines[-1]["type"] == "error"
    assert "kaboom" in lines[-1]["detail"]
