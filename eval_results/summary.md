# Eval Summary

**backend:** ollama · **model:** phi3 · **32 questions across 8 levels**

---

## rag_vs_norag

| Q | Level | RAG | no-RAG | Notes |
|---|---|---|---|---|
| Q1 | L1 | Yes | No | RAG correctly identifies the 4.4pt gap and 3x latency tradeoff. no-RAG speculates vaguely about model selection without grounding. |
| Q2 | L1 | Yes | No | RAG retrieves exact numbers (11/47 → 3/47). no-RAG says it needs specific study data and refuses. |
| Q3 | L1 | Yes | No | RAG correctly answers ~100,000 chunks. no-RAG goes off-topic, confuses FAISS IVF with IPUMS. |
| Q4 | L1 | Yes | No | RAG correctly explains paraphrastic questions with low lexical overlap. no-RAG speculates about domain knowledge without hitting the key point. |
| Q5 | L1 | Yes | No | RAG: BART-large. no-RAG invents a "Momento architecture." |
| Q6 | L2 | No | No | RAG says the score is not in context. no-RAG hallucinates about GLUE benchmark scores. |
| Q7 | L2 | No | No | RAG confuses with BERT F1 leaderboard scores. no-RAG talks about CLIP image captioning. |
| Q8 | L2 | No | No | RAG says 34ms for IndexFlatIP (wrong). no-RAG says these are unfamiliar terms. |
| Q9 | L2 | No | No | RAG answers 41.5% (DPR score, not RAG-Sequence). no-RAG refuses. |
| Q10 | L2 | No | No | RAG says 44.2% with no top-5/top-10 breakdown. no-RAG can't answer. |
| Q11 | L2 | No | No | RAG answers "System Dev Test - BERT (Single)." no-RAG can't answer. |
| Q12 | L3 | Yes | No | RAG retrieves both values (128, 50) with correct reasoning. no-RAG says it needs more context. |
| Q13 | L3 | No | No | RAG confuses chunk overlap with LM masking rate (15%). no-RAG can't answer. |
| Q14 | L4 | Yes | No | RAG correctly distinguishes per-token vs per-sequence document usage. no-RAG misuses "RAG tokens/sequences" as generic concepts. |
| Q15 | L4 | No | No | RAG mentions DPR and bi-encoder but concludes "exact name of DPR not provided." no-RAG says it doesn't know what RAG is. |
| Q16 | L4 | No | Yes | RAG says "MASK and UNMASK strategies" (wrong). no-RAG correctly states MLM and NSP from parametric knowledge. |
| Q17 | L4 | Yes | No | RAG: 15%. no-RAG: 30-40% (wrong). |
| Q18 | L4 | Yes | No | RAG correctly describes salient span masking with named entities and dates. no-RAG confuses with a fabricated "REVERB" model. |
| Q19 | L4 | No | No | RAG gets complexity and parallelism but replaces "path length" with "easier to interpret." no-RAG also misses at least one of the three. |
| Q20 | L5 | No | No | RAG retrieves 26.36 (ConvS2S EN-DE score, not EN-FR). no-RAG refuses. |
| Q21 | L5 | No | No | RAG confuses the BLEU score (41.8) with FLOPs. no-RAG can't answer. |
| Q22 | L5 | No | No | RAG says QQP not mentioned in context. no-RAG can't answer. |
| Q23 | L5 | No | No | RAG says score not directly stated. no-RAG can't answer. |
| Q24 | L5 | Yes | No | RAG: 44.5 EM exactly. no-RAG can't answer. |
| Q25 | L6 | No | No | RAG says 8 heads d=64 (implies 512 but never states it). no-RAG says 12 heads with 512 dimensions. |
| Q26 | L6 | No | No | RAG says dimensions (1024, 4096). no-RAG also wrong. |
| Q27 | L6 | No | No | RAG swaps H and A: "hidden size 16, 1024 heads." no-RAG similarly confused. |
| Q28 | L7 | No | Yes | RAG says sqrt(1/d) (ambiguous phrasing). no-RAG correctly writes 1/sqrt(d_k). |
| Q29 | L7 | No | No | RAG is very vague, no formula, no mention of MIPS. no-RAG mentions cosine similarity (wrong mechanism). |
| Q30 | L8 | No | No | RAG says not enough info across the two papers. no-RAG can't answer. |
| Q31 | L8 | No | No | RAG gives completely wrong head counts. no-RAG says "11 more." |
| Q32 | L8 | No | No | RAG says not in context. no-RAG cites fictional arXiv papers with wrong conclusions. |

| Config | Correct | Success Rate |
|---|---|---|
| RAG (baseline) | 10 | 31% |
| no-RAG | 2 | 6% |

---

## retrieval

| Q | Level | dense | bm25 | hybrid-rrf | Notes |
|---|---|---|---|---|---|
| Q1 | L1 | Yes | Yes | No | dense and bm25 both get the 4.4pt/3x latency reasoning. hybrid-rrf hallucinates about "4x fewer parameters." |
| Q2 | L1 | Yes | Yes | Yes | All three retrieve the exact numbers. |
| Q3 | L1 | Yes | Yes | Yes | All three answer ~100,000 chunks correctly. |
| Q4 | L1 | Yes | Yes | Yes | All three correctly explain the paraphrastic/lexical overlap reason. |
| Q5 | L1 | Yes | Yes | No | dense and bm25: BART-large. hybrid-rrf says "BART (Bottom-Up Approximately)" — wrong expansion. |
| Q6 | L2 | No | No | Yes | dense and bm25 say the score is not in context. hybrid-rrf retrieves 0.743 correctly. |
| Q7 | L2 | No | No | No | All three wrong. dense talks about BERT leaderboard, bm25 says RAG-Token at 41.8 EM, hybrid-rrf can't determine from context. |
| Q8 | L2 | No | Yes | Yes | dense gives wrong latency (34ms). bm25 and hybrid-rrf correctly say 4ms and 1ms. |
| Q9 | L2 | No | No | Yes | dense and bm25 answer 41.5 EM (DPR score). hybrid-rrf correctly retrieves 44.5. |
| Q10 | L2 | No | No | No | All three fail to give the 41.5/43.2/1.7 breakdown. |
| Q11 | L2 | No | No | No | All three wrong. dense says BERT Single, bm25 says BERT Single, hybrid-rrf can't answer for TriviaQA specifically. |
| Q12 | L3 | Yes | No | Yes | dense and hybrid-rrf get both values. bm25 only mentions 128 and leaves OVERLAP unspecified. |
| Q13 | L3 | No | No | No | dense confused with 15% masking. bm25 says 15%. hybrid-rrf says 50%. All wrong. |
| Q14 | L4 | Yes | No | No | dense correctly distinguishes the two. bm25 describes pointer networks (wrong). hybrid-rrf says they are equivalent (wrong). |
| Q15 | L4 | No | Yes | No | dense mentions DPR but hedges. bm25 directly says DPR. hybrid-rrf doesn't name a specific retriever. |
| Q16 | L4 | No | No | No | All three fail. dense says MASK/UNMASK, bm25 and hybrid-rrf infer MLM from context but are unclear about NSP. |
| Q17 | L4 | Yes | Yes | Yes | All three: 15%. |
| Q18 | L4 | Yes | Yes | Yes | All three correctly describe salient span masking. |
| Q19 | L4 | No | No | No | All three get partial credit at best — none give all three reasons exactly as stated in the paper. |
| Q20 | L5 | No | No | No | dense: 26.36. bm25: 40.56. hybrid-rrf: 40.46. All wrong (expected 41.29). |
| Q21 | L5 | No | No | No | All three fail to extract the FLOPs figure. |
| Q22 | L5 | No | No | No | All three fail. |
| Q23 | L5 | No | No | No | All three fail. |
| Q24 | L5 | Yes | Yes | No | dense and bm25: 44.5 EM. hybrid-rrf says "48 EM points higher than BM25" (wrong). |
| Q25 | L6 | No | No | No | dense: 8 heads d=64 (implicit). bm25: B=6 heads (wrong). hybrid-rrf: 8 heads d=64. None explicitly state d_model=512. |
| Q26 | L6 | No | Yes | Yes | dense: (1024, 4096) wrong. bm25 and hybrid-rrf correctly say d_ff=2048. |
| Q27 | L6 | No | No | No | All three swap H and A or give wrong values entirely. |
| Q28 | L7 | No | No | No | dense: sqrt(1/d) (ambiguous). bm25: √1/sqrt(dk) (ambiguous). hybrid-rrf: sqrt(1/d). None write 1/sqrt(d_k) cleanly. |
| Q29 | L7 | No | No | No | All three vague or wrong. No formula, no MIPS. |
| Q30 | L8 | No | No | No | All three fail. hybrid-rrf hallucinates scores (53 vs 47.6). |
| Q31 | L8 | No | No | No | All three give wrong head counts. |
| Q32 | L8 | No | No | No | All three fail to compare the two papers. |

| Config | Correct | Success Rate |
|---|---|---|
| dense | 10 | 31% |
| bm25 | 11 | 34% |
| hybrid-rrf | 10 | 31% |

---

## reranking

| Q | Level | no rerank | rerank | Notes |
|---|---|---|---|---|
| Q1 | L1 | Yes | No | no-rerank correct. rerank hallucinates reversed scores (says bge scores 0.783 vs MiniLM 0.787). |
| Q2 | L1 | Yes | Yes | Both retrieve the exact numbers. |
| Q3 | L1 | Yes | Yes | Both: ~100,000 chunks. |
| Q4 | L1 | Yes | Yes | Both correctly explain paraphrastic/lexical overlap. |
| Q5 | L1 | Yes | No | no-rerank: BART-large. rerank says "BART (Bidirectional and Auto-Regressive Transformer)" — wrong expansion. |
| Q6 | L2 | No | No | no-rerank says not in context. rerank buries 0.743 in a long confusing answer with wrong caveats. |
| Q7 | L2 | No | No | Both wrong. no-rerank talks about BERT F1. rerank says RAG Token at 0.743. |
| Q8 | L2 | No | No | no-rerank: 34ms (wrong). rerank says both IndexFlatIP and IndexIVF are 4ms (wrong). |
| Q9 | L2 | No | No | no-rerank: 41.5%. rerank: 44.0 (close but wrong). |
| Q10 | L2 | No | No | Both fail to give 41.5/43.2 breakdown. |
| Q11 | L2 | No | Yes | no-rerank: "BERT (Single)." rerank correctly answers RAG-Token and RAG-Sequence both at 68.2 EM. |
| Q12 | L3 | Yes | Yes | Both retrieve 128 and 50 with reasoning. |
| Q13 | L3 | No | No | no-rerank confused with 15% masking. rerank also confused (says 85% tokens retained). Both wrong. |
| Q14 | L4 | Yes | No | no-rerank correctly distinguishes the two models. rerank says RAG-Sequence "uses all top-k collectively" (wrong). |
| Q15 | L4 | No | Yes | no-rerank hedges. rerank clearly states "bi-encoder based on DPR." |
| Q16 | L4 | No | Yes | no-rerank: MASK/UNMASK. rerank correctly states MLM and NSP with good explanations. |
| Q17 | L4 | Yes | Yes | Both: 15%. |
| Q18 | L4 | Yes | Yes | Both correctly describe salient span masking. |
| Q19 | L4 | No | No | Both get partial credit but neither gives the exact three from the paper. |
| Q20 | L5 | No | No | no-rerank: 26.36. rerank: 7.7. Both wrong. |
| Q21 | L5 | No | No | Both fail. |
| Q22 | L5 | No | No | Both fail. |
| Q23 | L5 | No | No | Both fail. rerank says 41.5 EM (wrong, that's DPR). |
| Q24 | L5 | Yes | Yes | Both: 44.5 EM. |
| Q25 | L6 | No | No | Both say 8 heads d=64 but neither explicitly states d_model=512. |
| Q26 | L6 | No | No | no-rerank: (1024, 4096). rerank says d=512 (wrong). |
| Q27 | L6 | No | Yes | no-rerank swaps H and A. rerank correctly states H=1024, A=16. |
| Q28 | L7 | No | No | no-rerank: sqrt(1/d). rerank: √d (wrong sign). |
| Q29 | L7 | No | No | Both vague, no formula, no MIPS. |
| Q30 | L8 | No | No | Both fail. rerank compares retriever quality indirectly rather than giving scores. |
| Q31 | L8 | No | No | Both wrong. |
| Q32 | L8 | No | No | Both fail. |

| Config | Correct | Success Rate |
|---|---|---|
| no rerank | 10 | 31% |
| rerank | 11 | 34% |

---

## fusion

| Q | Level | hybrid-rrf | hybrid-weighted | Notes |
|---|---|---|---|---|
| Q1 | L1 | No | Yes | rrf hallucinates about "4x fewer parameters." weighted correctly mentions 3x latency tradeoff. |
| Q2 | L1 | Yes | Yes | Both retrieve exact numbers. |
| Q3 | L1 | Yes | Yes | Both: ~100,000 chunks. |
| Q4 | L1 | Yes | Yes | Both correctly explain the paraphrastic/lexical overlap reason. |
| Q5 | L1 | No | No | rrf: "BART (Bottom-Up Approximately)." weighted gives a long confusing answer involving both BERT and BART. Both wrong. |
| Q6 | L2 | Yes | No | rrf: 0.743. weighted says "78.0" and goes off-track. |
| Q7 | L2 | No | No | Both fail. rrf mentions BM25+DPR hypothetically. weighted says score not in document. |
| Q8 | L2 | Yes | No | rrf: 4ms and 1ms correctly. weighted says "both around 4ms" (wrong). |
| Q9 | L2 | Yes | Yes | Both correctly retrieve 44.5. |
| Q10 | L2 | No | No | Both fail to give the 41.5/43.2/1.7 breakdown. |
| Q11 | L2 | No | No | Both fail. rrf can't answer for TriviaQA. weighted says BERT single. |
| Q12 | L3 | Yes | Yes | Both retrieve 128 and 50 correctly. |
| Q13 | L3 | No | No | Both say 50%. Wrong (expected 39%). |
| Q14 | L4 | No | No | rrf says they are equivalent. weighted mentions decoding differences but gets RAG-Sequence wrong. |
| Q15 | L4 | No | Yes | rrf doesn't name a specific retriever. weighted says "DPR...bi-encoder architecture." |
| Q16 | L4 | No | No | Both infer MLM and NSP without stating them directly from the context. |
| Q17 | L4 | Yes | Yes | Both: 15%. |
| Q18 | L4 | Yes | Yes | Both correctly describe salient span masking. weighted adds correct SpanBERT context. |
| Q19 | L4 | No | No | Both get 2/3 reasons but miss "path length between long-range dependencies." |
| Q20 | L5 | No | No | rrf: 40.46. weighted says score not in context. Both wrong. |
| Q21 | L5 | No | No | Both fail to extract FLOPs. |
| Q22 | L5 | No | No | Both fail. |
| Q23 | L5 | No | No | rrf cannot determine from context. weighted says 38.5 (wrong). |
| Q24 | L5 | No | Yes | rrf says "48 EM points higher than BM25" (wrong framing). weighted: 44.5 EM. |
| Q25 | L6 | No | No | Both say 8 heads d=64 but neither explicitly states d_model=512. |
| Q26 | L6 | Yes | No | rrf: 2048 inner-layer dimension. weighted says d=4096 (wrong). |
| Q27 | L6 | No | No | rrf: "hidden size 16, 8 heads" (swapped). weighted: "hidden size 16, 32 heads" (both wrong). |
| Q28 | L7 | No | No | rrf: sqrt(1/d). weighted says scaling factor is "1" (completely wrong). |
| Q29 | L7 | No | No | rrf describes the marginalization but no formula and no MIPS. weighted also vague. |
| Q30 | L8 | No | No | rrf hallucinates 53 vs 47.6. weighted says not enough info. |
| Q31 | L8 | No | No | Both fail. |
| Q32 | L8 | No | No | rrf mentions 61.7 EM (hallucinated). weighted says REALM outperforms RAG (reversed). |

| Config | Correct | Success Rate |
|---|---|---|
| hybrid-rrf | 10 | 31% |
| hybrid-weighted | 10 | 31% |

---

## embed_model

| Q | Level | MiniLM | bge-small | e5-small | Notes |
|---|---|---|---|---|---|
| Q1 | L1 | Yes | Yes | No | MiniLM and bge-small get it right. e5-small says MiniLM "outperformed bge" — reversed. |
| Q2 | L1 | Yes | Yes | Yes | All three retrieve exact numbers. |
| Q3 | L1 | Yes | Yes | Yes | All three: ~100,000 chunks. |
| Q4 | L1 | Yes | Yes | Yes | All three correctly explain paraphrastic/lexical overlap. |
| Q5 | L1 | Yes | Yes | No | MiniLM and bge-small: BART-large. e5-small says "BERT and BART large." |
| Q6 | L2 | No | Yes | Yes | MiniLM says not in context. bge-small and e5-small retrieve 0.743. |
| Q7 | L2 | No | No | No | All three wrong. e5-small says MiniLM is highest with 0.743 (expected bge-base at 0.787). |
| Q8 | L2 | No | No | Yes | MiniLM: 34ms (wrong). bge-small partially infers 4ms only. e5-small clearly states 4ms and 1ms. |
| Q9 | L2 | No | Yes | Yes | MiniLM: 41.5%. bge-small and e5-small: 44.5 EM. |
| Q10 | L2 | No | Yes | No | MiniLM: no breakdown. bge-small: correctly gives 41.5, 43.2, 1.7-point gain. e5-small: 69.2% (hallucinated). |
| Q11 | L2 | No | No | Yes | MiniLM: BERT Single. bge-small: BERT (68.2) — wrong system. e5-small correctly says RAG-Sequence at 68.2. |
| Q12 | L3 | Yes | Yes | Yes | All three retrieve 128 and 50. |
| Q13 | L3 | No | No | No | MiniLM confused with 15%. bge-small and e5-small say 50%. All wrong. |
| Q14 | L4 | Yes | No | Yes | MiniLM and e5-small correctly distinguish the models. bge-small describes pointer networks (wrong). |
| Q15 | L4 | No | Yes | No | MiniLM hedges. bge-small says "DPR (Dual Encoder Retrieval)." e5-small doesn't identify a specific named retriever. |
| Q16 | L4 | No | Yes | No | MiniLM: MASK/UNMASK. bge-small correctly names MLM and NSP. e5-small goes off-topic with MNLI NER. |
| Q17 | L4 | Yes | Yes | Yes | All three: 15%. |
| Q18 | L4 | Yes | Yes | Yes | All three correctly describe salient span masking. |
| Q19 | L4 | No | No | No | All three get 2/3 reasons at best — none give the exact paper formulation. |
| Q20 | L5 | No | No | No | MiniLM: 26.36. bge-small says not in context. e5-small: 26.36 (from table). All wrong. |
| Q21 | L5 | No | No | No | All three fail. |
| Q22 | L5 | No | No | No | All three fail. |
| Q23 | L5 | No | No | No | MiniLM: not stated. bge-small: not stated. e5-small: 76.8% (hallucinated). |
| Q24 | L5 | Yes | No | No | MiniLM: 44.5 EM. bge-small: 48.1% (wrong). e5-small: 45.2 (wrong). |
| Q25 | L6 | No | Yes | No | MiniLM: 8 heads d=64 (implicit). bge-small explicitly states 8 heads, d=64, total 100M params. e5-small says "12 heads 768" (BERT config). |
| Q26 | L6 | No | No | No | MiniLM: (1024, 4096). bge-small: d=512 (wrong). e5-small: 4096. All wrong. |
| Q27 | L6 | No | Yes | Yes | MiniLM swaps H and A. bge-small and e5-small correctly state H=1024, A=16. |
| Q28 | L7 | No | No | No | MiniLM: sqrt(1/d). bge-small: √d (wrong). e5-small: √d. All fail to write 1/sqrt(d_k). |
| Q29 | L7 | No | No | No | All three vague, no formula, no MIPS. |
| Q30 | L8 | No | No | No | All three fail. e5-small hallucinates 89.6% vs REALM. |
| Q31 | L8 | No | No | No | All three fail. |
| Q32 | L8 | No | No | No | All three fail. MiniLM says not in context. bge-small says RAG approaches SOTA without specifics. |

| Config | Correct | Success Rate |
|---|---|---|
| all-MiniLM-L6-v2 | 10 | 31% |
| bge-small-en-v1.5 | 15 | 47% |
| e5-small-v2 | 12 | 38% |

---

## top_k

| Q | Level | k=5 | k=15 | k=20 | Notes |
|---|---|---|---|---|---|
| Q1 | L1 | Yes | Yes | Yes | All three correctly explain the 4.4pt/3x latency tradeoff. |
| Q2 | L1 | Yes | Yes | Yes | All three retrieve exact numbers. |
| Q3 | L1 | Yes | Yes | Yes | All three: ~100,000 chunks. |
| Q4 | L1 | Yes | Yes | Yes | All three correctly explain paraphrastic/lexical overlap. |
| Q5 | L1 | No | Yes | No | k=5 says BART but doesn't commit. k=15: BART-large. k=20 says "BART (Bayesian Autoregressive Transformer)" — wrong expansion. |
| Q6 | L2 | No | No | Yes | k=5 and k=15 say not in context. k=20 retrieves 0.743. |
| Q7 | L2 | No | No | No | All three fail. None retrieve bge-base-en-v1.5 at 0.787. |
| Q8 | L2 | No | No | No | k=5 gets IVF=1ms but not FlatIP=4ms. k=15: 34ms (wrong). k=20: 34ms (wrong). |
| Q9 | L2 | No | No | Yes | k=5 and k=15 fail. k=20: 44.5 EM. |
| Q10 | L2 | Yes | No | No | k=5 correctly derives 41.5, 43.2, and the 1.7-point gain. k=15 and k=20 fail. |
| Q11 | L2 | No | No | No | k=5 says no specific info. k=15: BERT Single. k=20: "Human System." All wrong. |
| Q12 | L3 | Yes | Yes | Yes | All three correctly retrieve 128 and 50. |
| Q13 | L3 | No | No | No | k=5: 50%. k=15 confused with LM masking. k=20: 15%. All wrong. |
| Q14 | L4 | No | Yes | No | k=5 says they are equivalent. k=15 correctly distinguishes the two. k=20 gives a confused mixed description. |
| Q15 | L4 | Yes | No | No | k=5 correctly identifies DPR bi-encoder. k=15 hedges. k=20 mentions DPR but muddles the explanation. |
| Q16 | L4 | No | No | Yes | k=5 and k=15 fail. k=20 clearly states "Masked LM and Next Sentence Prediction." |
| Q17 | L4 | Yes | Yes | Yes | All three: 15%. |
| Q18 | L4 | No | Yes | Yes | k=5 describes salient span masking but misses named entities/dates. k=15 and k=20 both correct. |
| Q19 | L4 | No | No | Yes | k=5 and k=15 get 2/3 reasons. k=20 gives all three correctly: complexity, parallelism, path length. |
| Q20 | L5 | No | No | No | k=5 says context doesn't specify. k=15: 26.36. k=20: 83.2 (hallucinated). All wrong. |
| Q21 | L5 | No | No | No | All three fail. k=5 guesses 41.8 billion (confuses BLEU and FLOPs). |
| Q22 | L5 | No | No | No | All three fail. |
| Q23 | L5 | No | No | No | All three fail. |
| Q24 | L5 | No | Yes | Yes | k=5 says not in context. k=15 and k=20: 44.5 EM. |
| Q25 | L6 | No | No | Yes | k=5 confused by BERT configs. k=15: 8 heads d=64 (implicit). k=20 explicitly states 8 heads, h×d=512. |
| Q26 | L6 | No | No | No | k=5 says not specified. k=15: (1024, 4096). k=20 vague. All wrong. |
| Q27 | L6 | No | No | Yes | k=5 and k=15 swap H and A. k=20 correctly states H=1024, A=16. |
| Q28 | L7 | No | No | No | k=5 says "square root of one." k=15: sqrt(1/d). k=20: √1/sqrt(d). All ambiguous or wrong. |
| Q29 | L7 | No | No | No | All three vague, no formula, no MIPS. |
| Q30 | L8 | No | No | No | All three fail. |
| Q31 | L8 | No | No | No | All three fail. |
| Q32 | L8 | No | No | No | All three fail. |

| Config | Correct | Success Rate |
|---|---|---|
| top_k = 5 | 8 | 25% |
| top_k = 15 | 10 | 31% |
| top_k = 20 | 14 | 44% |

---

## Overall Takeaways

**What moves the needle:**
- **Embed model** is the biggest lever — bge-small (47%) beats MiniLM (31%) by 16 points. It retrieves the right chunks for table and benchmark questions that MiniLM misses entirely.
- **top_k** is equally important — k=20 (44%) beats k=5 (25%) by 19 points. The model can use wider context especially for table and equation questions.

**What doesn't move the needle:**
- **Retrieval method** (dense/bm25/hybrid) is within ±3% — no meaningful difference at this corpus size.
- **Reranking** gives +3% at most, within noise.
- **Fusion strategy** (rrf vs weighted) makes zero difference.

**Per-question difficulty across all configs:**

There are 11 unique configs (deduplication note: the dense baseline appears in 4 dimensions — rag_vs_norag "RAG", retrieval "dense", reranking "no-rerank", embed_model "MiniLM" — counted once; hybrid-rrf appears in both retrieval and fusion — counted once).

| Q | Level | Correct | % | What happened |
|---|---|---|---|---|
| Q1 | L1 | 7/11 | 64% | Answered correctly by most RAG configs; hybrid-rrf, rerank, and e5-small all fabricate reversed scores or wrong comparisons. |
| Q2 | L1 | 10/11 | 91% | Easy retrieval — exact numbers (11/47 → 3/47) present verbatim in the text. Only no-RAG fails. |
| Q3 | L1 | 10/11 | 91% | ~100,000 chunks is a simple numerical lookup. Only no-RAG fails (goes off-topic entirely). |
| Q4 | L1 | 10/11 | 91% | "Paraphrastic questions with low lexical overlap" — well-explained in the source text, easy to retrieve. Only no-RAG misses it. |
| Q5 | L1 | 4/11 | 36% | "BART-large" is correct but the model often appends a wrong expansion ("Bottom-Up Approximately", "Bidirectional and Auto-Regressive"). Only dense, bm25, bge-small, k=15 answer cleanly. |
| Q6 | L2 | 4/11 | 36% | Score (0.743) appears in a table; most configs say it's not in context. Only hybrid-rrf, bge-small, e5-small, k=20 retrieve the right chunk. |
| Q7 | L2 | 0/11 | 0% | Best EM model (bge-base-en-v1.5 at 0.787) requires reading a comparison table row — every config either hallucinates or retrieves the wrong row. |
| Q8 | L2 | 3/11 | 27% | Requires distinguishing IndexFlatIP (4ms) from IndexIVFFlat (1ms). Most configs conflate them or give 34ms. Only bm25, hybrid-rrf, e5-small answer correctly. |
| Q9 | L2 | 5/11 | 45% | 44.5 EM is in the text, but many configs retrieve the DPR score (41.5) instead. Only hybrid-rrf, hybrid-weighted, bge-small, e5-small, k=20 get it right. |
| Q10 | L2 | 2/11 | 18% | Requires comparing two table rows (41.5 → 43.2, +1.7). Very few configs retrieve both rows together. Only bge-small and k=5 succeed. |
| Q11 | L2 | 2/11 | 18% | TriviaQA score for a specific system — most configs name the wrong system. Only rerank and e5-small retrieve RAG-Sequence at 68.2 correctly. |
| Q12 | L3 | 9/11 | 82% | max_tokens=128, overlap=50 — present literally in config comments, easy to retrieve. Only no-RAG and bm25 (which misses the overlap value) fail. |
| Q13 | L3 | 0/11 | 0% | Overlap percentage (39%) — every config either says 50% (confuses token overlap count with a ratio) or hallucinates 15%. The computation is never done correctly. |
| Q14 | L4 | 3/11 | 27% | Distinguishing RAG-Token (per-token marginalization) from RAG-Sequence (full document, one pass) — most configs conflate them or get the direction wrong. Only dense, e5-small, k=15 succeed. |
| Q15 | L4 | 5/11 | 45% | "DPR bi-encoder" — many configs mention DPR but hedge or describe it incorrectly. bm25, rerank, hybrid-weighted, bge-small, k=5 all name it clearly. |
| Q16 | L4 | 4/11 | 36% | MLM and NSP — the dense baseline systematically says "MASK/UNMASK." no-RAG answers from parametric knowledge. Configs that retrieve the BERT pretraining section (rerank, bge-small, k=20) answer correctly. |
| Q17 | L4 | 10/11 | 91% | 15% masking rate — very explicit in the text. Only no-RAG fails (answers 30-40%). |
| Q18 | L4 | 9/11 | 82% | Salient span masking — well-described in the source. Only no-RAG (hallucinated "REVERB") and k=5 (too little context) fail. |
| Q19 | L4 | 1/11 | 9% | Three Transformer advantages: complexity, parallelism, path length — almost every config replaces "path length" with something else. Only k=20 (wider context) gives all three. |
| Q20 | L5 | 0/11 | 0% | EN-FR BLEU (41.29) — every config retrieves the wrong cell from a multi-language results table (often returning the EN-DE score 26.36). |
| Q21 | L5 | 0/11 | 0% | Training FLOPs (3.3×10^18) — never found. Most configs confuse it with the BLEU score column in the same table. |
| Q22 | L5 | 0/11 | 0% | QQP accuracy (72.1) — the chunk containing this cell is never retrieved; model says it's not in context across all configs. |
| Q23 | L5 | 0/11 | 0% | SQuAD 1.1 EM (40.4) — same issue as Q22; benchmark table chunk is not retrieved by any config. |
| Q24 | L5 | 6/11 | 55% | NQ EM (44.5) — appears more frequently in the text than other benchmark figures. dense, bm25, rerank, hybrid-weighted, k=15, k=20 all retrieve it. |
| Q25 | L6 | 2/11 | 18% | BERT-BASE: 8 heads, d_model=512 — requires combining two separate facts (h=8, d_k=64 → total 512). Most configs state one but not both explicitly. Only bge-small and k=20 make the inference clearly. |
| Q26 | L6 | 2/11 | 18% | d_ff=2048 — appears in the Transformer architecture table. Most configs retrieve the wrong row or column. Only bm25 and hybrid-rrf find it. |
| Q27 | L6 | 4/11 | 36% | BERT-LARGE: H=1024, A=16 — the model systematically swaps hidden size and number of heads across most configs. rerank, bge-small, e5-small, k=20 get it right. |
| Q28 | L7 | 1/11 | 9% | Attention scaling factor (1/√d_k) — requires parsing a LaTeX-style formula. Almost every config writes it ambiguously or wrong. Only no-RAG answers from parametric knowledge. |
| Q29 | L7 | 0/11 | 0% | REALM marginalization formula and MIPS — never retrieved in any config. The relevant chunk appears not to land in top-k for any retriever. |
| Q30 | L8 | 0/11 | 0% | Cross-paper comparison (RAG vs DPR scores) — requires synthesizing facts from two separate PDFs simultaneously. No config succeeds. |
| Q31 | L8 | 0/11 | 0% | Head count difference (BERT-LARGE 16 − BERT-BASE 8 = 4) — requires reading two rows from the architecture table and subtracting. No config succeeds. |
| Q32 | L8 | 0/11 | 0% | Cross-paper REALM vs RAG comparison (45.2 vs 40.7, +4.5) — requires cross-document retrieval. Every config hallucinates or refuses. |
