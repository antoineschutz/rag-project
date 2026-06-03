import tiktoken

from src.chunking.chunk import naive_chunk_text, chunk_text_tiktoken, chunk_documents


def test_naive_empty():
    assert naive_chunk_text("") == []


def test_naive_single_chunk():
    assert len(naive_chunk_text("short text", chunk_size=500)) == 1


def test_naive_overlap():
    # each character is unique so a false overlap can't accidentally pass
    text = "".join(str(i % 10) for i in range(100))
    chunks = naive_chunk_text(text, chunk_size=60, overlap=20)
    assert len(chunks) >= 2
    assert chunks[0][-20:] == chunks[1][:20]


def test_tiktoken_empty():
    assert chunk_text_tiktoken("") == []


def test_tiktoken_max_tokens_respected():
    enc = tiktoken.get_encoding("cl100k_base")
    text = " ".join(["word"] * 500)
    max_tokens = 64
    chunks = chunk_text_tiktoken(text, max_tokens=max_tokens, overlap_tokens=0)
    for chunk in chunks:
        assert len(enc.encode(chunk)) <= max_tokens


def test_tiktoken_overlap():
    enc = tiktoken.get_encoding("cl100k_base")
    # build text long enough to produce at least 2 chunks
    text = " ".join(["word"] * 300)
    overlap_tokens = 16
    max_tokens = 64
    chunks = chunk_text_tiktoken(text, max_tokens=max_tokens, overlap_tokens=overlap_tokens)
    assert len(chunks) >= 2
    # the token content at the start of chunk[1] should appear at the end of chunk[0]
    tokens_0 = enc.encode(chunks[0])
    tokens_1 = enc.encode(chunks[1])
    assert tokens_0[-overlap_tokens:] == tokens_1[:overlap_tokens]


def test_chunk_documents_source_preserved():
    docs = [{"text": "Hello world. " * 50, "source": "doc_a.pdf"}]
    chunks = chunk_documents(docs)
    assert len(chunks) > 0
    assert all(c["source"] == "doc_a.pdf" for c in chunks)


def test_chunk_documents_empty():
    assert chunk_documents([]) == []
