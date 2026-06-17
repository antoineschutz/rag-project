import pytest

from src.ingestion.loader import load_docx, load_markdown, load_pdfs, load_txt
from src.chunking.chunk import chunk_documents


def _any_chunk_contains(chunks: list[dict[str, str]], *terms: str) -> bool:
    return any(all(t in c["text"] for t in terms) for c in chunks)


@pytest.fixture(scope="session")
def pdf_chunks() -> list[dict[str, str]]:
    return chunk_documents(load_pdfs("data"))


@pytest.fixture(scope="session")
def md_chunks() -> list[dict[str, str]]:
    return chunk_documents(load_markdown("data"))


@pytest.fixture(scope="session")
def docx_chunks() -> list[dict[str, str]]:
    return chunk_documents(load_docx("data"))


def test_load_txt(tmp_path):
    (tmp_path / "note.txt").write_text("plain text body", encoding="utf-8")
    (tmp_path / "blank.txt").write_text("   ", encoding="utf-8")  # whitespace-only is skipped
    (tmp_path / "ignore.md").write_text("not a txt file", encoding="utf-8")
    docs = load_txt(str(tmp_path))
    assert docs == [{"text": "plain text body", "source": "note.txt"}]


def test_md_prose_chunk(md_chunks):
    # Q6: "What top-5 EM score does all-MiniLM-L6-v2 achieve?" → 0.743
    assert _any_chunk_contains(md_chunks, "all-MiniLM-L6-v2", "0.743")


def test_md_table_chunk(md_chunks):
    # Q7: "Which embedding model achieves the highest top-5 EM?" → bge-base-en-v1.5 at 0.787
    assert _any_chunk_contains(md_chunks, "bge-base-en-v1.5", "0.787")


def test_docx_chunk(docx_chunks):
    # Q11: "Which system achieves the highest TriviaQA EM?" → RAG-Sequence at 68.2
    assert _any_chunk_contains(docx_chunks, "RAG-Sequence", "68.2")


def test_pdf_prose_chunk(pdf_chunks):
    # not tied to a specific Q/A pair: checks DPR bi-encoder section is reachable
    rag_chunks = [c for c in pdf_chunks if c["source"] == "rag_lewis2020.pdf"]
    assert _any_chunk_contains(rag_chunks, "document encoder", "query encoder")


def test_pdf_table_chunk(pdf_chunks):
    # Q20: "What BLEU score did ConvS2S Ensemble achieve on WMT 2014 EN-FR?" → 41.29
    aiayn_chunks = [c for c in pdf_chunks if c["source"] == "attention_is_all_you_need.pdf"]
    # pdfplumber x_tolerance=5 merges "ConvS2S" + "Ensemble" into one token; test the key value
    assert _any_chunk_contains(aiayn_chunks, "ConvS2SEnsemble", "41.29")


def test_pdf_table_markdown(pdf_chunks):
    # Q25-adjacent: Transformer base model (Table 3, bordered → pdfplumber extracts as Markdown)
    # "| 6 512 2048 8 ..." proves the table row survived as structured Markdown, not raw text
    aiayn_chunks = [c for c in pdf_chunks if c["source"] == "attention_is_all_you_need.pdf"]
    assert _any_chunk_contains(aiayn_chunks, "| 6 512", "2048")


def test_realm_two_column_phrase_intact(pdf_chunks):
    # Known phrase from realm_guu2020.pdf that was garbled before the two-column fix.
    realm_chunks = [c for c in pdf_chunks if c["source"] == "realm_guu2020.pdf"]
    assert _any_chunk_contains(realm_chunks, "salient span masking")


def test_realm_no_column_interleaving(pdf_chunks):
    # Checks that the specific garbled fragment from the two-column bug is gone.
    realm_chunks = [c for c in pdf_chunks if c["source"] == "realm_guu2020.pdf"]
    assert not any("usperformance-based" in c["text"] for c in realm_chunks)


def test_attention_is_all_you_need_sentence_1(pdf_chunks):  # 6.1 paragraph 2
    src_chunks = [c for c in pdf_chunks if c["source"] == "attention_is_all_you_need.pdf"]
    sentence = "On the WMT 2014 English-to-French translation task, our big model achieves a BLEU score of 41.0"
    assert any(sentence in c["text"] for c in src_chunks)


def test_attention_is_all_you_need_sentence_2(pdf_chunks):  # 3.1 paragraph 1
    src_chunks = [c for c in pdf_chunks if c["source"] == "attention_is_all_you_need.pdf"]
    sentence = "The encoder is composed of a stack of N = 6 identical layers."
    assert any(sentence in c["text"] for c in src_chunks)


def test_attention_is_all_you_need_sentence_3(pdf_chunks):  # 3.2.1 paragraph 1
    src_chunks = [c for c in pdf_chunks if c["source"] == "attention_is_all_you_need.pdf"]
    sentence = 'We call our particular attention "Scaled Dot-Product Attention"'
    assert any(sentence in c["text"] for c in src_chunks)


def test_attention_is_all_you_need_sentence_4(pdf_chunks):  # 3.2.2 paragraph 4
    src_chunks = [c for c in pdf_chunks if c["source"] == "attention_is_all_you_need.pdf"]
    sentence = "In this work we employ h = 8 parallel attention layers, or heads."
    assert any(sentence in c["text"] for c in src_chunks)


def test_attention_is_all_you_need_sentence_5(pdf_chunks):  # 3.2.2 paragraph 3
    src_chunks = [c for c in pdf_chunks if c["source"] == "attention_is_all_you_need.pdf"]
    sentence = "Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions."
    assert any(sentence in c["text"] for c in src_chunks)


def test_bert_sentence_1(pdf_chunks):  # 3.1 paragraph 4
    src_chunks = [c for c in pdf_chunks if c["source"] == "bert_devlin2018.pdf"]
    sentence = "For the pre-training corpus we use the BooksCorpus (800M words) (Zhu et al., 2015) and English Wikipedia (2,500M words)."
    assert any(sentence in c["text"] for c in src_chunks)


def test_bert_sentence_2(pdf_chunks):  # 3.1 paragraph 2
    src_chunks = [c for c in pdf_chunks if c["source"] == "bert_devlin2018.pdf"]
    sentence =  "In all of our experiments, we mask 15% of all WordPiece tokens in each sequence at random."
    assert any(sentence in c["text"] for c in src_chunks)


def test_bert_sentence_3(pdf_chunks):  # 5.1 p2, hard multi column
    src_chunks = [c for c in pdf_chunks if c["source"] == "bert_devlin2018.pdf"]
    sentence = "This does significantly improve results on SQuAD, but the results are still far worse than those of the pretrained bidirectional models."
    assert any(sentence in c["text"] for c in src_chunks)


def test_bert_sentence_4(pdf_chunks):  # IMPORTANT: FOOTNOTE test
    src_chunks = [c for c in pdf_chunks if c["source"] == "bert_devlin2018.pdf"]
    sentence = "and the model could trivially predict the target word in a multi-layered context. In order to train a deep bidirectional"
    assert any(sentence in c["text"] for c in src_chunks)


def test_rag_lewis_sentence_1(pdf_chunks):  # 1 p2
    src_chunks = [c for c in pdf_chunks if c["source"] == "rag_lewis2020.pdf"]
    sentence = "We build RAG models where the parametric memory is a pre-trained seq2seq transformer, and the non-parametric memory is a dense vector index of Wikipedia, accessed with a pre-trained neural retriever."
    assert any(sentence in c["text"] for c in src_chunks)


def test_rag_lewis_sentence_2(pdf_chunks):  # 2.1 p1
    src_chunks = [c for c in pdf_chunks if c["source"] == "rag_lewis2020.pdf"]
    sentence = "The RAG-Sequence model uses the same retrieved document to generate the complete sequence"
    assert any(sentence in c["text"] for c in src_chunks)



def test_rag_lewis_sentence_3(pdf_chunks):  # 4.1
    src_chunks = [c for c in pdf_chunks if c["source"] == "rag_lewis2020.pdf"]
    sentence = " On all four open-domain QA tasks, RAG sets a new state of the art (only on the T5-comparable split for TQA)."
    assert any(sentence in c["text"] for c in src_chunks)


def test_realm_sentence_1(pdf_chunks):
    src_chunks = [c for c in pdf_chunks if c["source"] == "realm_guu2020.pdf"]
    sentence =  "We now describe the two key components: the neural knowledge retriever, which models p(z | x), and the knowledge-augmented encoder, which models p(y | z, x)."
    assert any(sentence in c["text"] for c in src_chunks)


def test_realm_sentence_2(pdf_chunks):
    src_chunks = [c for c in pdf_chunks if c["source"] == "realm_guu2020.pdf"]
    sentence = "In contrast, REALM outperforms the largest T5-11B model while being 30 times smaller."
    assert any(sentence in c["text"] for c in src_chunks)


def test_realm_sentence_3(pdf_chunks):
    src_chunks = [c for c in pdf_chunks if c["source"] == "realm_guu2020.pdf"]
    sentence =  'Our solution is to “refresh” the index by asynchronously re-embedding and re-indexing all documents every several hundred training steps.'
    assert any(sentence in c["text"] for c in src_chunks)
