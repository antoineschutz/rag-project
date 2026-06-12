"""Tests for the /evaluate endpoint.

The endpoint lazily does `from src.evaluation.benchmark import run_benchmark`. These tests
patch `run_benchmark` on that module (rather than replacing the import) so the real import
still runs, which also guards against that module path breaking, while stubbing out the
actual benchmark so no LLM or MLflow call happens. TestClient is built without `with`, so
the app lifespan (warmup) does not fire.
"""

from typing import Any

from fastapi.testclient import TestClient

import src.evaluation.benchmark as benchmark_mod
from src.api import server


def _fake_report(config_name: str) -> dict[str, Any]:
    """A minimal report dict matching EvaluateResponse."""
    return {
        "config_name": config_name,
        "config": {"retriever": "hybrid"},
        "n_scored": 29,
        "correct": 20,
        "accuracy_29": 20 / 29,
        "fresh": False,
        "latency_s": None,
        "judge": False,
        "score_judge": None,
        "judge_disagreements": None,
        "results": [{"id": 1, "correct": True}],
    }


def test_evaluate_preset_calls_run_benchmark(monkeypatch):
    calls: dict[str, Any] = {}

    def fake_run_benchmark(label: str, cfg: Any, fresh: bool = False, judge: bool = False) -> dict[str, Any]:
        calls.update(label=label, fresh=fresh, judge=judge)
        return _fake_report(label)

    monkeypatch.setattr(benchmark_mod, "run_benchmark", fake_run_benchmark)

    client = TestClient(server.app)  # no `with`: lifespan/_warmup does not run
    resp = client.post("/evaluate", json={"name": "best"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["config_name"] == "best"
    assert body["accuracy_29"] == 20 / 29
    assert calls == {"label": "best", "fresh": False, "judge": False}


def test_evaluate_forwards_fresh_and_judge(monkeypatch):
    calls: dict[str, Any] = {}

    def fake_run_benchmark(label: str, cfg: Any, fresh: bool = False, judge: bool = False) -> dict[str, Any]:
        calls.update(fresh=fresh, judge=judge)
        return _fake_report(label)

    monkeypatch.setattr(benchmark_mod, "run_benchmark", fake_run_benchmark)

    client = TestClient(server.app)
    resp = client.post("/evaluate", json={"name": "best", "fresh": True, "judge": True})

    assert resp.status_code == 200
    assert calls == {"fresh": True, "judge": True}


def test_evaluate_inline_config_uses_custom_label(monkeypatch):
    captured: dict[str, Any] = {}

    def fake_run_benchmark(label: str, cfg: Any, fresh: bool = False, judge: bool = False) -> dict[str, Any]:
        captured.update(label=label, cfg=cfg)
        return _fake_report(label)

    monkeypatch.setattr(benchmark_mod, "run_benchmark", fake_run_benchmark)

    client = TestClient(server.app)
    resp = client.post("/evaluate", json={"name": "", "config": {"retriever": "bm25"}})

    assert resp.status_code == 200
    assert captured["label"] == "custom"
    assert captured["cfg"] == {"retriever": "bm25"}


def test_evaluate_known_preset_wins_over_inline_config(monkeypatch):
    # Regression: a known preset `name` must win and the inline `config` be ignored, so the
    # Swagger placeholder config cannot silently shadow the preset (and collide cache keys).
    captured: dict[str, Any] = {}

    def fake_run_benchmark(label: str, cfg: Any, fresh: bool = False, judge: bool = False) -> dict[str, Any]:
        captured.update(label=label, cfg=cfg)
        return _fake_report(label)

    monkeypatch.setattr(benchmark_mod, "run_benchmark", fake_run_benchmark)

    client = TestClient(server.app)
    resp = client.post(
        "/evaluate",
        json={"name": "best", "config": {"additionalProp1": {}}},
    )

    assert resp.status_code == 200
    assert captured["label"] == "best"
    assert captured["cfg"] is server.PRESETS["best"]


def test_evaluate_unknown_preset_returns_400():
    client = TestClient(server.app)
    resp = client.post("/evaluate", json={"name": "does-not-exist"})

    assert resp.status_code == 400
    assert "Unknown preset" in resp.json()["detail"]
