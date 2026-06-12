from src.config import GenerationParams, IndexParams, RetrievalParams, split_config


def test_from_dict_splits_a_flat_config():
    # A flat config (like a PRESETS entry plus a query) feeds all three groups; each
    # picks only its own fields and ignores the rest.
    flat = {
        "query": "what is RAG?",
        "retriever": "hybrid",
        "embed_model": "BAAI/bge-small-en-v1.5",
        "store": "faiss",
        "chunk_max_tokens": 256,
        "top_k": 20,
        "rerank": True,
        "fusion": "weighted",
        "alpha": 0.7,
        "no_rag": False,
        "backend": "ollama",
        "num_ctx": 8192,
    }

    ip = IndexParams.from_dict(flat)
    assert ip.retriever == "hybrid"
    assert ip.embed_model == "BAAI/bge-small-en-v1.5"
    assert ip.store == "faiss"
    assert ip.chunk_max_tokens == 256

    rp = RetrievalParams.from_dict(flat)
    assert rp.query == "what is RAG?"
    assert rp.top_k == 20
    assert rp.rerank is True
    assert rp.fusion == "weighted"
    assert rp.alpha == 0.7

    gp = GenerationParams.from_dict(flat)
    assert gp.no_rag is False
    assert gp.backend == "ollama"
    assert gp.num_ctx == 8192
    assert gp.model is None  # absent in the flat config, falls back to the default


def test_split_config_builds_three_groups_and_injects_query():
    cfg = {"retriever": "hybrid", "top_k": 20, "no_rag": False, "backend": None}
    ip, rp, gp = split_config(cfg, query="what is RAG?")
    assert ip.retriever == "hybrid"
    assert rp.query == "what is RAG?" and rp.top_k == 20
    assert gp.no_rag is False
    # None values are dropped so the field keeps its default (not None)
    assert gp.backend is None  # default happens to be None, but it came from the default not cfg


def test_split_config_query_arg_overrides_cfg_query():
    ip, rp, gp = split_config({"query": "stale", "retriever": "bm25"}, query="fresh")
    assert rp.query == "fresh"
    assert ip.retriever == "bm25"


def test_defaults_and_to_kwargs_roundtrip():
    ip = IndexParams()
    assert IndexParams.from_dict(ip.to_kwargs()) == ip

    rp = RetrievalParams(query="q")
    assert RetrievalParams.from_dict(rp.to_kwargs()) == rp

    gp = GenerationParams()
    assert GenerationParams.from_dict(gp.to_kwargs()) == gp
