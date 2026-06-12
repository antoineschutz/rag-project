from src.api.schemas import QueryConfig, QueryRequest


def test_query_request_config_defaults_to_none():
    assert QueryRequest(query="q").config is None


def test_query_request_accepts_preset_name():
    req = QueryRequest(query="q", config="baseline")
    assert req.config == "baseline"  # a bare string stays a string (preset name)


def test_query_request_parses_inline_config():
    req = QueryRequest(query="q", config={"retriever": "bm25", "top_k": 5})
    assert isinstance(req.config, QueryConfig)
    assert req.config.retriever == "bm25"
    assert req.config.top_k == 5


def test_query_config_is_a_partial():
    # only the explicitly-set knob survives exclude_none; the rest fall back downstream
    dumped = QueryConfig(retriever="bm25").model_dump(exclude_none=True)
    assert dumped == {"retriever": "bm25"}
