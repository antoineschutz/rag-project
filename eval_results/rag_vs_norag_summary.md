# Eval Summary — RAG vs no-RAG

**Config:** dense retriever · all-MiniLM-L6-v2 · top_k=5 · no rerank

---

## Overall scores

| System | ✓ Success | ~ Partial | ✗ Failure | Success rate |
|--------|:---------:|:---------:|:---------:|:------------:|
| RAG    | 11        | 4         | 17        | 34%          |
| no-RAG | 3         | 2         | 27        | 9%           |

---

## Per-question results

| Q  | Level | Source                        | Question (short)                                  | RAG | no-RAG |
|----|-------|-------------------------------|---------------------------------------------------|:---:|:------:|
| 1  | 1     | rag_design_notes.md           | Why MiniLM over bge-base?                         | ✓   | ✗      |
| 2  | 1     | rag_design_notes.md           | Hallucination reduction from source attribution   | ✓   | ✗      |
| 3  | 1     | rag_design_notes.md           | FAISS IVF breakeven corpus size                   | ✓   | ✗      |
| 4  | 1     | qa_benchmark_report.docx      | Why BM25 lags DPR more on NQ than TriviaQA        | ✓   | ✗      |
| 5  | 1     | qa_benchmark_report.docx      | Generator model in RAG-Token / RAG-Sequence       | ~   | ✗      |
| 6  | 2     | rag_design_notes.md           | MiniLM top-5 EM score                             | ✗   | ✗      |
| 7  | 2     | rag_design_notes.md           | Best embedding model + score                      | ✗   | ✗      |
| 8  | 2     | rag_design_notes.md           | IndexFlatIP vs IndexIVF latency                   | ✓   | ✗      |
| 9  | 2     | qa_benchmark_report.docx      | RAG-Sequence NQ EM (benchmark report)             | ✗   | ✗      |
| 10 | 2     | qa_benchmark_report.docx      | DPR NQ EM top-5 vs top-10                         | ~   | ✗      |
| 11 | 2     | qa_benchmark_report.docx      | Highest TriviaQA EM system                        | ✗   | ✗      |
| 12 | 3     | rag_design_notes.md           | Final CHUNK_MAX_TOKENS and CHUNK_OVERLAP          | ✓   | ✗      |
| 13 | 3     | rag_design_notes.md           | Token overlap percentage                          | ✗   | ✗      |
| 14 | 4     | rag_lewis2020.pdf             | Difference between RAG-Token and RAG-Sequence     | ✗   | ✗      |
| 15 | 4     | rag_lewis2020.pdf             | Retriever used in RAG                             | ✓   | ✗      |
| 16 | 4     | bert_devlin2018.pdf           | BERT's two pre-training tasks                     | ✗   | ✓      |
| 17 | 4     | bert_devlin2018.pdf           | MLM masking percentage                            | ~   | ✓      |
| 18 | 4     | realm_guu2020.pdf             | REALM masking type and rationale                  | ~   | ✗      |
| 19 | 4     | attention_is_all_you_need.pdf | Three reasons for self-attention over recurrence  | ✓   | ~      |
| 20 | 5     | attention_is_all_you_need.pdf | ConvS2S Ensemble BLEU on WMT14 En-Fr              | ✗   | ✗      |
| 21 | 5     | attention_is_all_you_need.pdf | Transformer base training cost in FLOPs           | ✗   | ✗      |
| 22 | 5     | bert_devlin2018.pdf           | BERT-LARGE QQP score on GLUE                      | ✗   | ✗      |
| 23 | 5     | realm_guu2020.pdf             | REALM EM on NaturalQuestions Open                 | ✗   | ✗      |
| 24 | 5     | rag_lewis2020.pdf             | RAG-Sequence NQ EM (Lewis et al.)                 | ✗   | ✗      |
| 25 | 6     | attention_is_all_you_need.pdf | Transformer base: heads and d_model               | ✗   | ✓      |
| 26 | 6     | attention_is_all_you_need.pdf | Transformer base FFN dimension                    | ✗   | ✗      |
| 27 | 6     | bert_devlin2018.pdf           | BERT-LARGE hidden size and attention heads        | ✓   | ✗      |
| 28 | 7     | attention_is_all_you_need.pdf | Scaling factor in dot-product attention           | ✓   | ~      |
| 29 | 7     | realm_guu2020.pdf             | How REALM computes p(z\|x)                        | ✗   | ✗      |
| 30 | 8     | rag_lewis2020 + realm_guu2020 | RAG vs REALM on NQ Open (cross-doc)               | ✗   | ✗      |
| 31 | 8     | bert_devlin2018 + attention   | BERT-BASE vs Transformer attention head count     | ✗   | ✗      |
| 32 | 8     | rag_lewis2020 + realm_guu2020 | RAG-Sequence vs REALM on WebQuestions (cross-doc) | ✗   | ✗      |

---

## By difficulty level

| Level | Questions | RAG ✓ | RAG ~ | RAG ✗ | no-RAG ✓ | no-RAG ~ | no-RAG ✗ |
|-------|-----------|:-----:|:-----:|:-----:|:--------:|:--------:|:--------:|
| 1     | Q1–Q5     | 4     | 1     | 0     | 0        | 0        | 5        |
| 2     | Q6–Q11    | 2     | 1     | 3     | 0        | 0        | 6        |
| 3     | Q12–Q13   | 1     | 0     | 1     | 0        | 0        | 2        |
| 4     | Q14–Q19   | 2     | 2     | 2     | 2        | 1        | 3        |
| 5     | Q20–Q24   | 0     | 0     | 5     | 0        | 0        | 5        |
| 6     | Q25–Q27   | 1     | 0     | 2     | 1        | 0        | 2        |
| 7     | Q28–Q29   | 1     | 0     | 1     | 0        | 1        | 1        |
| 8     | Q30–Q32   | 0     | 0     | 3     | 0        | 0        | 3        |

RAG is strong through L3, competitive at L4, then collapses at L5+.  
no-RAG only scores at L4 and L6 on facts baked into parametric memory (BERT, Transformer architecture).

---

## By source document

| Source                        | Q count | RAG ✓ | RAG ~ | RAG ✗ | no-RAG ✓ | no-RAG ~ | no-RAG ✗ |
|-------------------------------|---------|:-----:|:-----:|:-----:|:--------:|:--------:|:--------:|
| rag_design_notes.md           | 8       | 6     | 0     | 2     | 0        | 0        | 8        |
| qa_benchmark_report.docx      | 5       | 2     | 1     | 2     | 0        | 0        | 5        |
| rag_lewis2020.pdf             | 4       | 1     | 0     | 3     | 0        | 0        | 4        |
| bert_devlin2018.pdf           | 5       | 2     | 1     | 2     | 2        | 1        | 2        |
| realm_guu2020.pdf             | 3       | 0     | 1     | 2     | 0        | 0        | 3        |
| attention_is_all_you_need.pdf | 6       | 1     | 1     | 4     | 1        | 1        | 4        |
| cross-doc (2 sources)         | 3       | 0     | 0     | 3     | 0        | 0        | 3        |

RAG retrieves `rag_design_notes.md` well (75% success). PDFs are harder — especially cross-doc questions where context from two files must be combined.

---

## Failure patterns

| Pattern | Description | Affected questions |
|---------|-------------|-------------------|
| **Missing chunk** | The relevant passage was not retrieved at top-5 | Q6, Q7, Q9, Q11, Q20–Q24 |
| **Correct method, wrong detail** | RAG retrieves related context but answers imprecisely | Q5 (BART not BART-large), Q10 (top-5 only), Q13 (50% vs 39%), Q17 |
| **Context absent, no fallback** | RAG says "not in context"; no-RAG also fails | Q29, Q30, Q31, Q32 |
| **no-RAG wins from memory** | Well-known facts not needing retrieval | Q16, Q17, Q25 (BERT/Transformer architecture basics) |
| **Cross-doc reasoning** | Answer requires combining two retrieved sources | Q30, Q31, Q32 — both systems fail entirely |

---

## Key takeaways

- **RAG is clearly better overall** (34% vs 9% success rate), especially for project-specific facts.
- **L1–L3 is RAG's sweet spot**: direct design decisions and config values from `rag_design_notes.md` are reliably retrieved.
- **L5 is a cliff**: specific numerical benchmarks (BLEU, FLOPs, per-task GLUE scores) are not retrieved at top-5. Likely a chunk granularity or top-k issue.
- **PDFs are harder than markdown/docx**: retrieval quality drops noticeably for `.pdf` sources, possibly due to extraction quality.
- **Cross-doc questions (L8) fail 100%**: the pipeline has no mechanism to fuse evidence across multiple retrieved passages from different documents.
- **no-RAG beats RAG only on L4 architecture facts** (BERT, Transformer) that are saturated in the LLM's parametric memory — these would not benefit from retrieval regardless.
