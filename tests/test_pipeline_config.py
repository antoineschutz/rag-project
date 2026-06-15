from dataclasses import asdict

from src.config import BASE, BEST, NO_RAG, PRESETS, PipelineConfig, as_config_dict


def test_base_is_all_defaults():
    assert BASE == PipelineConfig()
    assert BASE.retriever == "dense"
    assert BASE.top_k == 15
    assert BASE.embed_model == "all-MiniLM-L6-v2"
    assert BASE.no_rag is False


def test_best_and_no_rag_values():
    assert BEST.retriever == "hybrid"
    assert BEST.rerank is True
    assert BEST.top_k == 20
    assert BEST.embed_model == "BAAI/bge-small-en-v1.5"
    assert NO_RAG.no_rag is True


def test_presets_registry():
    assert set(PRESETS) == {
        "no-rag", "no-rag-gpt", "baseline", "best", "gpt",
        "llama3.1-8b", "no-rag-llama3.1-8b",
        "lightweight", "bm25", "hybrid", "hyde", "faiss",
    }
    # baseline is literally the default pipeline; best/no-rag are the variants
    assert PRESETS["baseline"] is BASE
    assert PRESETS["best"] is BEST
    assert PRESETS["no-rag"] is NO_RAG


def test_as_config_dict_flattens_pipelineconfig():
    d = as_config_dict(BEST)
    assert isinstance(d, dict)
    assert d["retriever"] == "hybrid"
    assert d["top_k"] == 20
    # a full flatten: every PipelineConfig field is present
    assert set(d) == set(asdict(PipelineConfig()))


def test_as_config_dict_passes_dicts_through_unchanged():
    d = {"retriever": "bm25"}
    assert as_config_dict(d) is d


def test_pipelineconfig_is_frozen_and_hashable():
    # frozen so PRESETS values and IndexParams keys are usable as dict keys
    assert hash(BASE) == hash(PipelineConfig())
