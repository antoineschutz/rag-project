from src.api import server


def test_warmup_builds_retrievers_and_reranker(monkeypatch):
    built = []
    reranked = []
    monkeypatch.setattr(server.state, "get_retriever", lambda ip: built.append(ip.retriever) or object())
    monkeypatch.setattr(server.state, "get_reranker", lambda: reranked.append(1) or object())
    monkeypatch.setattr(server.env, "WARMUP_PRESETS", ("baseline", "best", "no-rag"))

    server._warmup()

    # baseline (dense) and best (hybrid) get an index; no-rag is skipped (no retrieval)
    assert built == ["dense", "hybrid"]
    # best reranks, baseline does not -> reranker warmed exactly once
    assert len(reranked) == 1


def test_warmup_is_non_fatal(monkeypatch):
    def boom(ip):
        raise RuntimeError("index build failed")

    monkeypatch.setattr(server.state, "get_retriever", boom)
    monkeypatch.setattr(server.env, "WARMUP_PRESETS", ("best",))

    server._warmup()  # must not raise; failure is logged and left to lazy build


def test_warmup_skips_unknown_preset(monkeypatch):
    built = []
    monkeypatch.setattr(server.state, "get_retriever", lambda ip: built.append(ip.retriever) or object())
    monkeypatch.setattr(server.state, "get_reranker", lambda: object())
    monkeypatch.setattr(server.env, "WARMUP_PRESETS", ("does-not-exist", "baseline"))

    server._warmup()

    assert built == ["dense"]  # unknown skipped, baseline still warmed
