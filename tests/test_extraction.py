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


def test_pdf_table_chunk():
    # Q20: "What BLEU score did ConvS2S Ensemble achieve on WMT 2014 EN-FR?" → 41.29
    chunks = chunk_documents(load_pdfs("data"))
    aiayn_chunks = [c for c in chunks if c["source"] == "attention_is_all_you_need.pdf"]
    assert _any_chunk_contains(aiayn_chunks, "ConvS2S Ensemble", "41.29")


def test_pdf_table_markdown():
    # Q25-adjacent: Transformer base model (Table 3, bordered → pdfplumber extracts as Markdown)
    # "| 6 512 2048 8 ..." proves the table row survived as structured Markdown, not raw text
    chunks = chunk_documents(load_pdfs("data"))
    aiayn_chunks = [c for c in chunks if c["source"] == "attention_is_all_you_need.pdf"]
    assert _any_chunk_contains(aiayn_chunks, "| 6 512", "2048")


def test_realm_two_column_phrase_intact():
    # Known phrase from realm_guu2020.pdf that was garbled before the two-column fix.
    # Checks that column-split extraction produces coherent, non-interleaved text.
    chunks = chunk_documents(load_pdfs("data"))
    realm_chunks = [c for c in chunks if c["source"] == "realm_guu2020.pdf"]
    assert _any_chunk_contains(realm_chunks, "salient span masking")


def test_realm_no_column_interleaving():
    # Checks that the specific garbled fragment from the two-column bug is gone.
    # The old extractor would emit "usperformance-based ing a signal" (words from two
    # columns merged mid-word). After the fix this pattern must not appear.
    chunks = chunk_documents(load_pdfs("data"))
    realm_chunks = [c for c in chunks if c["source"] == "realm_guu2020.pdf"]
    assert not any("usperformance-based" in c["text"] for c in realm_chunks)



    
def test_attention_is_all_you_need_sentence_1(): # 6.1 paragraph 2 
    chunks = chunk_documents(load_pdfs("data"))
    src_chunks = [c for c in chunks if c["source"] == "attention_is_all_you_need.pdf"]
    sentence = "On the WMT 2014 English-to-French translation task, our big model achieves a BLEU score of 41.0"
    assert any(sentence in c["text"] for c in src_chunks)


def test_attention_is_all_you_need_sentence_2(): # 3.1 paragraph 1
    chunks = chunk_documents(load_pdfs("data"))
    src_chunks = [c for c in chunks if c["source"] == "attention_is_all_you_need.pdf"]
    sentence = "The encoder is composed of a stack of N = 6 identical layers."
    assert any(sentence in c["text"] for c in src_chunks)

def test_attention_is_all_you_need_sentence_3(): #3.2.1 paragrah 1 
    chunks = chunk_documents(load_pdfs("data"))
    src_chunks = [c for c in chunks if c["source"] == "attention_is_all_you_need.pdf"]
    sentence = 'We call our particular attention "Scaled Dot-Product Attention"'
    assert any(sentence in c["text"] for c in src_chunks)


def test_attention_is_all_you_need_sentence_4():  # 3.2.2 paragrah 4
    chunks = chunk_documents(load_pdfs("data"))
    src_chunks = [c for c in chunks if c["source"] == "attention_is_all_you_need.pdf"]
    sentence = "In this work we employ h = 8 parallel attention layers, or heads."
    assert any(sentence in c["text"] for c in src_chunks)

def test_attention_is_all_you_need_sentence_5():  #3.2.2 paragraph 3 
    chunks = chunk_documents(load_pdfs("data"))
    src_chunks = [c for c in chunks if c["source"] == "attention_is_all_you_need.pdf"]
    sentence = "Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions."
    assert any(sentence in c["text"] for c in src_chunks)
