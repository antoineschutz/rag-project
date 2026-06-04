# RAG Evaluation -- Q&A Pairs by Difficulty

Question-answer pairs for each document in the corpus, ordered by how hard it is for the **loader + retriever** to surface the correct answer. Use these as demo scripts and as the basis for future evaluation harnesses (roadmap items G and R).

## Corpus

| File | Format |
|---|---|
| `data/rag_lewis2020.pdf` | PDF, two-column |
| `data/attention_is_all_you_need.pdf` | PDF, two-column |
| `data/bert_devlin2018.pdf` | PDF, two-column |
| `data/realm_guu2020.pdf` | PDF, two-column |
| `data/rag_design_notes.md` | Markdown |
| `data/qa_benchmark_report.docx` | DOCX |

---

## Capability Taxonomy

| Capability | Description | Main bottleneck |
|---|---|---|
| **Plain prose** | Continuous paragraphs of running text. Clean in md/docx; minor encoding artifacts (hyphenation, ligatures) in PDFs. | None at md/docx level; minor in PDF |
| **Tables** | Structured rows and columns with headers. Trivial in md (pipe syntax) and docx (XML). In PDFs, pypdf loses column-header relationships; pdfplumber required. | PDF table extraction |
| **Code blocks** | Fenced code or pseudo-code. Trivially parsed in md. Rarely appears in PDFs; monospace font detection is unreliable. | Retrieval: query must match surrounding prose, not the code literal |
| **Mathematical equations** | Formulae typeset as LaTeX glyphs or rendered bitmaps. Surrounding prose is extractable; the formula itself comes out as garbled symbols even with pdfplumber. | Formula rendering; partial recovery only |
| **Multi-column reading order** | Two-column academic PDFs are read line-by-line left-to-right by pypdf, interleaving both columns. pdfplumber recovers correct column-by-column order. | pypdf column collapse; V3-H required |
| **Cross-document retrieval** | Questions whose answer requires combining specific facts from two separate documents. The retriever must surface chunks from both; neither document alone is sufficient. | Retrieval precision across sources + LLM synthesis |

---

## Q&A Pairs

### Level 1 -- Plain prose, flat formats (md / docx)
No parsing challenge. High retrieval confidence: the text is clean and the answer is in a single contiguous chunk.

| # | Question | Answer | Source |
|---|---|---|---|
| 1 | Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`? | The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline. | rag_design_notes.md |
| 2 | How much did adding source attribution to the RAG prompt reduce hallucination? | From 11/47 (23%) to 3/47 (6%) | rag_design_notes.md |
| 3 | Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP? | Above approximately 100,000 chunks | rag_design_notes.md |
| 4 | Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA? | NQ has longer, more paraphrastic questions with low lexical overlap between question and passage. | qa_benchmark_report.docx |
| 5 | What generator model do RAG-Token and RAG-Sequence use? | BART-large | qa_benchmark_report.docx |

---

### Level 2 -- Tables in markdown / docx
Table parsing is trivial in these formats. Retrieval is straightforward: the table values appear verbatim in extracted text.

| # | Question | Answer | Source |
|---|---|---|---|
| 6 | What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve? | 0.743 | rag_design_notes.md |
| 7 | Which embedding model achieves the highest top-5 EM, and what is the score? | `bge-base-en-v1.5` at 0.787 | rag_design_notes.md |
| 8 | What is the query latency of IndexFlatIP vs IndexIVF? | IndexFlatIP: 4 ms, IndexIVF: 1 ms | rag_design_notes.md |
| 9 | What NQ Exact Match does RAG-Sequence achieve in the benchmark report? | 44.5 EM | qa_benchmark_report.docx |
| 10 | What NQ EM does DPR achieve with top-5 vs top-10 retrieval? | 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain | qa_benchmark_report.docx |
| 11 | Which system achieves the highest TriviaQA EM in the benchmark report? | RAG-Sequence at 68.2 EM | qa_benchmark_report.docx |

---

### Level 3 -- Code blocks in markdown
Parsing is trivial. Retrieval challenge: the answer is a specific numeric literal inside a fenced code block, so the query must match the surrounding prose context, not the code itself.

| # | Question | Answer | Source |
|---|---|---|---|
| 12 | What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values? | `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50` | rag_design_notes.md |
| 13 | What token overlap percentage does the current chunking configuration use? | 39% (50 overlap tokens out of 128 max) | rag_design_notes.md |

---

### Level 4 -- Plain prose in PDFs (abstract, introduction, single-column sections)
PDF encoding is messier than markdown (hyphenation artifacts, ligature substitution), but single-column prose sections are still reliably extractable with pypdf.

| # | Question | Answer | Source |
|---|---|---|---|
| 14 | What is the difference between RAG-Token and RAG-Sequence? | RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token. | rag_lewis2020.pdf |
| 15 | What retriever does the RAG model use? | Dense Passage Retrieval (DPR) with a bi-encoder | rag_lewis2020.pdf |
| 16 | What two pre-training tasks does BERT use? | Masked Language Modeling (MLM) and Next Sentence Prediction (NSP) | bert_devlin2018.pdf |
| 17 | What percentage of input tokens are masked in BERT's MLM objective? | 15% | bert_devlin2018.pdf |
| 18 | What type of masking does REALM use during pre-training, and why? | Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge. | realm_guu2020.pdf |
| 19 | What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers? | (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies | attention_is_all_you_need.pdf |

---

### Level 5 -- Tables in PDFs
The critical extraction challenge. pypdf returns table cells as whitespace-separated tokens with no delimiters, losing column-header relationships. pdfplumber is needed for correct extraction. To be valid tests at this level, the answers must appear exclusively in a table and not be restated in the prose anywhere else in the document.

| # | Question | Answer | Source |
|---|---|---|---|
| 20 | What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French? | 41.29 | attention_is_all_you_need.pdf |
| 21 | What is the training cost of the base Transformer model in floating point operations? | 3.3 x 10^18 FLOPs | attention_is_all_you_need.pdf |
| 22 | What is the QQP score achieved by BERT-LARGE on the GLUE benchmark? | 72.1 | bert_devlin2018.pdf |
| 23 | What Exact Match score does REALM achieve on NaturalQuestions Open? | 40.4 EM | realm_guu2020.pdf |
| 24 | What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.? | 44.5 EM | rag_lewis2020.pdf |

---

### Level 6 -- Multi-column reading order in PDFs
These questions target content in the body of two-column conference papers where pypdf's column-collapse produces garbled output. With pypdf, the answer chunks may exist in the index but with corrupted surrounding context, degrading retrieval ranking. pdfplumber fixes the reading order.

| # | Question | Answer | Source |
|---|---|---|---|
| 25 | How many attention heads and what model dimension does the Transformer base model use? | 8 heads, d_model = 512 | attention_is_all_you_need.pdf |
| 26 | What feed-forward network dimension does the Transformer base model use? | d_ff = 2048 | attention_is_all_you_need.pdf |
| 27 | What is BERT-LARGE's hidden size and number of attention heads? | Hidden size 1024, 16 attention heads | bert_devlin2018.pdf |

---

### Level 7 -- Equations in PDFs
Math is typeset as glyphs or rendered bitmaps. Even pdfplumber cannot reconstruct a LaTeX expression reliably. Retrieval may find the right chunk via prose context, but the answer requires interpreting the partial formula.

| # | Question | Answer | Source |
|---|---|---|---|
| 28 | What scaling factor does scaled dot-product attention apply before the softmax? | 1/sqrt(d_k): divide by the square root of the key dimension | attention_is_all_you_need.pdf |
| 29 | How does REALM compute the probability of retrieving document z given input x? | p(z\|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS). | realm_guu2020.pdf |

---

### Level 8 -- Cross-document retrieval
The retriever must surface relevant chunks from two different documents, and the LLM must synthesise them. Neither document alone is sufficient to answer.

| # | Question | Answer | Sources |
|---|---|---|---|
| 30 | How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open? | RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG. | rag_lewis2020.pdf + realm_guu2020.pdf |
| 31 | How many more attention heads does BERT-BASE have compared to the base Transformer model? | BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4. | bert_devlin2018.pdf + attention_is_all_you_need.pdf |
| 32 | How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions? | RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions. | rag_lewis2020.pdf + realm_guu2020.pdf |

---

## Summary

| Level | Capability | Pairs | Bottleneck |
|---|---|---|---|
| 1 | Plain prose, md/docx | 5 | None |
| 2 | Tables in md/docx | 6 | None |
| 3 | Code blocks in md | 2 | Retrieval match |
| 4 | Prose in PDFs | 6 | Encoding artifacts |
| 5 | Tables in PDFs | 5 | pypdf to pdfplumber required |
| 6 | Multi-column layout | 3 | pypdf column collapse |
| 7 | Equations in PDFs | 2 | Formula rendering; partial |
| 8 | Cross-document retrieval | 3 | Retrieval precision + synthesis |

**Total: 32 pairs across 6 documents and 6 capability types.**

Levels 1-3 work with the current pypdf stack. Levels 4-6 improve significantly with V3-H (pdfplumber). Levels 7-8 represent the current ceiling of text-only RAG.
