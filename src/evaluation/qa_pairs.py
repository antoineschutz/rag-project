"""The benchmark question set, shared by scripts/benchmark.py and the API evaluate path."""

from typing import Any

# ---------------------------------------------------------------------------
# Q/A pairs: fill in question / expected / source before running
# Level distribution: L1×5, L2×6, L3×2, L4×6, L5×5, L6×3, L7×2, L8×3
#
# `keywords`: lowercase substrings the auto-scorer (scripts/benchmark.py)
# checks for, case-insensitively, with AND semantics: an answer scores correct
# only if EVERY listed substring is present. An empty list ([]) means the
# question is excluded from automatic scoring (pure-prose answers that string
# matching can't judge); Q4, Q14, Q19 are dropped on that basis, leaving 29
# keyword-scored questions (accuracy_29). The LLM-as-judge safeguard runs
# alongside to catch keyword false positives/negatives.
# ---------------------------------------------------------------------------
QA_PAIRS: list[dict[str, Any]] = [
    # Level 1: plain prose, md/docx
    {"id": 1,  "level": 1, "question": "Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?", "expected": "The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.", "source": "rag_design_notes.md", "keywords": ["4.4"]},
    {"id": 2,  "level": 1, "question": "How much did adding source attribution to the RAG prompt reduce hallucination?", "expected": "From 11/47 (23%) to 3/47 (6%)", "source": "rag_design_notes.md", "keywords": ["23%", "6%"]},
    {"id": 3,  "level": 1, "question": "Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?", "expected": "Above approximately 100,000 chunks", "source": "rag_design_notes.md", "keywords": ["100,000"]},
    {"id": 4,  "level": 1, "question": "Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?", "expected": "NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.", "source": "qa_benchmark_report.docx", "keywords": []},
    {"id": 5,  "level": 1, "question": "What generator model do RAG-Token and RAG-Sequence use?", "expected": "BART-large", "source": "qa_benchmark_report.docx", "keywords": ["bart"]},
    # Level 2: tables in md/docx
    {"id": 6,  "level": 2, "question": "What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?", "expected": "0.743", "source": "rag_design_notes.md", "keywords": ["0.743"]},
    {"id": 7,  "level": 2, "question": "Which embedding model achieves the highest top-5 EM, and what is the score?", "expected": "`bge-base-en-v1.5` at 0.787", "source": "rag_design_notes.md", "keywords": ["bge-base", "0.787"]},
    {"id": 8,  "level": 2, "question": "What is the query latency of IndexFlatIP vs IndexIVF?", "expected": "IndexFlatIP: 4 ms, IndexIVF: 1 ms", "source": "rag_design_notes.md", "keywords": ["4 ms", "1 ms"]},
    {"id": 9,  "level": 2, "question": "What NQ Exact Match does RAG-Sequence achieve in the benchmark report?", "expected": "44.5 EM", "source": "qa_benchmark_report.docx", "keywords": ["44.5"]},
    {"id": 10, "level": 2, "question": "What NQ EM does DPR achieve with top-5 vs top-10 retrieval?", "expected": "41.5 (top-5) to 43.2 (top-10), a 1.7-point gain", "source": "qa_benchmark_report.docx", "keywords": ["41.5", "43.2"]},
    {"id": 11, "level": 2, "question": "Which system achieves the highest TriviaQA EM in the benchmark report?", "expected": "RAG-Sequence at 68.2 EM", "source": "qa_benchmark_report.docx", "keywords": ["68.2"]},
    # Level 3: code blocks in md
    {"id": 12, "level": 3, "question": "What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?", "expected": "`CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`", "source": "rag_design_notes.md", "keywords": ["128", "50"]},
    {"id": 13, "level": 3, "question": "What token overlap percentage does the current chunking configuration use?", "expected": "39% (50 overlap tokens out of 128 max)", "source": "rag_design_notes.md", "keywords": ["39%"]},
    # Level 4: prose in PDFs
    {"id": 14, "level": 4, "question": "What is the difference between RAG-Token and RAG-Sequence?", "expected": "RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.", "source": "rag_lewis2020.pdf", "keywords": []},
    {"id": 15, "level": 4, "question": "What retriever does the RAG model use?", "expected": "Dense Passage Retrieval (DPR) with a bi-encoder", "source": "rag_lewis2020.pdf", "keywords": ["dpr"]},
    {"id": 16, "level": 4, "question": "What two pre-training tasks does BERT use?", "expected": "Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)", "source": "bert_devlin2018.pdf", "keywords": ["masked language", "next sentence"]},
    {"id": 17, "level": 4, "question": "What percentage of input tokens are masked in BERT's MLM objective?", "expected": "15%", "source": "bert_devlin2018.pdf", "keywords": ["15%"]},
    {"id": 18, "level": 4, "question": "What type of masking does REALM use during pre-training, and why?", "expected": "Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.", "source": "realm_guu2020.pdf", "keywords": ["salient span"]},
    {"id": 19, "level": 4, "question": "What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?", "expected": "(1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies", "source": "attention_is_all_you_need.pdf", "keywords": []},
    # Level 5: tables in PDFs
    {"id": 20, "level": 5, "question": "What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?", "expected": "41.29", "source": "attention_is_all_you_need.pdf", "keywords": ["41.29"]},
    {"id": 21, "level": 5, "question": "What is the training cost of the base Transformer model in floating point operations?", "expected": "3.3 x 10^18 FLOPs", "source": "attention_is_all_you_need.pdf", "keywords": ["3.3"]},
    {"id": 22, "level": 5, "question": "What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?", "expected": "72.1", "source": "bert_devlin2018.pdf", "keywords": ["72.1"]},
    {"id": 23, "level": 5, "question": "What Exact Match score does REALM achieve on NaturalQuestions Open?", "expected": "40.4 EM", "source": "realm_guu2020.pdf", "keywords": ["40.4"]},
    {"id": 24, "level": 5, "question": "What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?", "expected": "44.5 EM", "source": "rag_lewis2020.pdf", "keywords": ["44.5"]},
    # Level 6: multi-column layout
    {"id": 25, "level": 6, "question": "How many attention heads and what model dimension does the Transformer base model use?", "expected": "8 heads, d_model = 512", "source": "attention_is_all_you_need.pdf", "keywords": ["512"]},
    {"id": 26, "level": 6, "question": "What feed-forward network dimension does the Transformer base model use?", "expected": "d_ff = 2048", "source": "attention_is_all_you_need.pdf", "keywords": ["2048"]},
    {"id": 27, "level": 6, "question": "What is BERT-LARGE's hidden size and number of attention heads?", "expected": "Hidden size 1024, 16 attention heads", "source": "bert_devlin2018.pdf", "keywords": ["1024", "16"]},
    # Level 7: equations in PDFs
    {"id": 28, "level": 7, "question": "What scaling factor does scaled dot-product attention apply before the softmax?", "expected": "1/sqrt(d_k): divide by the square root of the key dimension", "source": "attention_is_all_you_need.pdf", "keywords": ["square root"]},
    {"id": 29, "level": 7, "question": "How does REALM compute the probability of retrieving document z given input x?", "expected": "p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).", "source": "realm_guu2020.pdf", "keywords": ["inner product"]},
    # Level 8: cross-document retrieval
    {"id": 30, "level": 8, "question": "How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?", "expected": "RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.", "source": "rag_lewis2020.pdf + realm_guu2020.pdf", "keywords": ["44.5", "40.4"]},
    {"id": 31, "level": 8, "question": "How many more attention heads does BERT-BASE have compared to the base Transformer model?", "expected": "BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.", "source": "bert_devlin2018.pdf + attention_is_all_you_need.pdf", "keywords": ["12", "8"]},
    {"id": 32, "level": 8, "question": "How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?", "expected": "RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.", "source": "rag_lewis2020.pdf + realm_guu2020.pdf", "keywords": ["45.2", "40.7"]},
]
