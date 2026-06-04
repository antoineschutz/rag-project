import pytest

from src.ingestion.loader import load_docx, load_markdown, load_pdfs
from src.chunking.chunk import chunk_documents


def _any_chunk_contains(chunks: list[dict[str, str]], *terms: str) -> bool:
    return any(all(t in c["text"] for t in terms) for c in chunks)


def test_md_prose_chunk():
    # Q6: "What top-5 EM score does all-MiniLM-L6-v2 achieve?" → 0.743
    chunks = chunk_documents(load_markdown("data"))
    assert _any_chunk_contains(chunks, "all-MiniLM-L6-v2", "0.743")


def test_md_table_chunk():
    # Q7: "Which embedding model achieves the highest top-5 EM?" → bge-base-en-v1.5 at 0.787
    chunks = chunk_documents(load_markdown("data"))
    assert _any_chunk_contains(chunks, "bge-base-en-v1.5", "0.787")


def test_docx_chunk():
    # Q11: "Which system achieves the highest TriviaQA EM?" → RAG-Sequence at 68.2
    chunks = chunk_documents(load_docx("data"))
    assert _any_chunk_contains(chunks, "RAG-Sequence", "68.2")


def test_pdf_prose_chunk():
    # not tied to a specific Q/A pair — checks DPR bi-encoder section is reachable
    chunks = chunk_documents(load_pdfs("data"))
    rag_chunks = [c for c in chunks if c["source"] == "rag_lewis2020.pdf"]
    assert _any_chunk_contains(rag_chunks, "document encoder", "query encoder")


@pytest.mark.xfail(reason="requires pdfplumber (H)")
def test_pdf_table_chunk():
    # Q20: "What BLEU score did ConvS2S Ensemble achieve on WMT 2014 EN-FR?" → 41.29
    chunks = chunk_documents(load_pdfs("data"))
    aiayn_chunks = [c for c in chunks if c["source"] == "attention_is_all_you_need.pdf"]
    assert _any_chunk_contains(aiayn_chunks, "ConvS2S Ensemble", "41.29")


@pytest.mark.xfail(reason="requires pdfplumber (H)")
def test_pdf_column_order_chunk():
    # Q25: "How many attention heads and what model dimension does the Transformer base use?" → d_model=512
    chunks = chunk_documents(load_pdfs("data"))
    aiayn_chunks = [c for c in chunks if c["source"] == "attention_is_all_you_need.pdf"]
    assert _any_chunk_contains(aiayn_chunks, "d_model", "512")
