from src.prompts.templates import build_prompt_no_rag, build_prompt_rag


def test_no_rag_contains_query():
    prompt = build_prompt_no_rag("What is gravity?")
    assert "What is gravity?" in prompt


def test_no_rag_empty_query():
    prompt = build_prompt_no_rag("")
    assert isinstance(prompt, str)


def test_rag_contains_query():
    prompt = build_prompt_rag("What is gravity?", ["context"])
    assert "What is gravity?" in prompt


def test_rag_contains_contexts():
    prompt = build_prompt_rag("query", ["first context", "second context"])
    assert "first context" in prompt
    assert "second context" in prompt


def test_rag_contexts_joined():
    prompt = build_prompt_rag("query", ["ctx1", "ctx2"])
    assert "ctx1\n\nctx2" in prompt
