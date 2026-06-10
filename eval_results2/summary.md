# Eval Summary — Round 2

**backend:** ollama · **model:** phi3 · **32 questions across 8 levels**

Scoring is manual (Yes = the expected key fact/value is stated correctly; No = wrong, missing, refused, or off-topic). For the wide sweeps, `✗` = phi3 produced off-topic garbage (context overload) and `—` = phi3 returned an empty answer.

---

## rag_vs_norag

| Q | Level | RAG | no-RAG | Notes |
|---|---|---|---|---|
| Q1 | L1 | No | No | RAG garbles the numbers (says latency drops 18→9ms); no-RAG refuses. Neither states the 4.4pt/3x tradeoff. |
| Q2 | L1 | Yes | No | RAG: 23%→6%. no-RAG refuses (no access to study). |
| Q3 | L1 | Yes | No | RAG: ~100,000 chunks. no-RAG refuses. |
| Q4 | L1 | Yes | No | RAG: paraphrastic / low lexical overlap. no-RAG rambles and gets the direction muddled. |
| Q5 | L1 | Yes | No | RAG: BART-large. no-RAG invents an MLM-based generator. |
| Q6 | L2 | Yes | No | RAG: 0.743. no-RAG refuses. |
| Q7 | L2 | No | No | RAG cites BERT F1 87.3% (wrong row). no-RAG can't. |
| Q8 | L2 | No | No | RAG says both are 4ms (should be 4 / 1). no-RAG can't. |
| Q9 | L2 | No | No | RAG gives 41.5 (DPR value, not RAG-Seq 44.5). no-RAG refuses. |
| Q10 | L2 | No | No | RAG gives 44.5/48% (wrong). no-RAG can't. |
| Q11 | L2 | No | No | RAG picks QANet ensemble (wrong). no-RAG can't. |
| Q12 | L3 | Yes | No | RAG: 128 / 50. no-RAG refuses. |
| Q13 | L3 | No | No | RAG says 15% (confused with MLM rate). no-RAG can't. |
| Q14 | L4 | Yes | No | RAG distinguishes per-token vs per-sequence correctly. no-RAG treats tokens/sequences as generic concepts. |
| Q15 | L4 | Yes | No | RAG: DPR bi-encoder. no-RAG thinks "RAG" is a dog breed. |
| Q16 | L4 | No | Yes | RAG says "A/B" (wrong). no-RAG correctly states MLM + NSP from parametric knowledge. |
| Q17 | L4 | Yes | Yes | RAG: 15%. no-RAG: 15–20% (includes 15%). |
| Q18 | L4 | Yes | No | RAG: salient span masking. no-RAG invents "relational entity linking". |
| Q19 | L4 | No | No | RAG gets complexity+parallelism but swaps "path length" for "interpretable". no-RAG misses complexity+path length. |
| Q20 | L5 | No | No | Both fail (ConvS2S EN-FR BLEU 41.29). |
| Q21 | L5 | No | No | Both fail to extract FLOPs. |
| Q22 | L5 | No | No | RAG gives 80.5 (overall, not QQP). no-RAG can't. |
| Q23 | L5 | No | No | Both fail (REALM 40.4 EM). |
| Q24 | L5 | Yes | No | RAG: 44.5 EM. no-RAG can't. |
| Q25 | L6 | No | Yes | RAG says 8 heads d=64 but never states d_model=512. no-RAG: 8 heads, 512. |
| Q26 | L6 | No | Yes | RAG: not specified. no-RAG: 2048 (four times 512). |
| Q27 | L6 | Yes | No | RAG: H=1024, 16 heads. no-RAG: 12 heads (wrong). |
| Q28 | L7 | No | Yes | RAG: √1 (garbled). no-RAG: 1/sqrt(d_k). |
| Q29 | L7 | No | No | Both vague, no MIPS / inner-product formula. |
| Q30 | L8 | No | No | Both fail to compare RAG vs REALM. |
| Q31 | L8 | No | No | RAG: 768 heads (wrong). no-RAG: muddled. |
| Q32 | L8 | No | No | Both fail the cross-paper WebQuestions comparison. |

| Config | Correct | Success Rate |
|---|---|---|
| RAG (baseline) | 12 | 37% |
| no-RAG | 5 | 16% |

---

## retrieval

| Q | Level | dense | bm25 | hybrid-rrf | Notes |
|---|---|---|---|---|---|
| Q1 | L1 | No | Yes | No | bm25 alone cites the 4.4pt gap + 3x latency. dense/hybrid garble the numbers. |
| Q2 | L1 | Yes | Yes | Yes | All retrieve 23%→6%. |
| Q3 | L1 | Yes | Yes | Yes | All: ~100,000 chunks. |
| Q4 | L1 | Yes | Yes | Yes | All explain paraphrastic / low lexical overlap. |
| Q5 | L1 | Yes | Yes | Yes | All name BART-large (hybrid muddles in GPT2 but states BART large). |
| Q6 | L2 | Yes | No | Yes | dense/hybrid: 0.743. bm25 says the score isn't given. |
| Q7 | L2 | No | No | No | All wrong (bge-base 0.787 never retrieved). |
| Q8 | L2 | No | Yes | Yes | dense says both 4ms; bm25/hybrid correctly give 4 / 1. |
| Q9 | L2 | No | Yes | Yes | dense gives 41.5; bm25/hybrid give 44.5. |
| Q10 | L2 | No | No | No | None give 41.5→43.2 / +1.7. |
| Q11 | L2 | No | Yes | Yes | dense picks QANet; bm25/hybrid: RAG-Sequence 68.2. |
| Q12 | L3 | Yes | No | Yes | bm25 gives 128 but omits the overlap value. |
| Q13 | L3 | No | No | No | All wrong (39%); answers are 15% / garbled. |
| Q14 | L4 | Yes | No | No | dense distinguishes the two; bm25/hybrid muddle the decoding difference. |
| Q15 | L4 | Yes | Yes | No | dense/bm25 name DPR; hybrid mis-describes it as a cross-encoder reader. |
| Q16 | L4 | No | Yes | Yes | dense says "A/B"; bm25/hybrid: MLM + NSP. |
| Q17 | L4 | Yes | Yes | Yes | All: 15%. |
| Q18 | L4 | Yes | Yes | Yes | All: salient span masking. |
| Q19 | L4 | No | No | No | None give all three reasons (path length missing). |
| Q20 | L5 | No | No | No | All fail (41.29). |
| Q21 | L5 | No | No | No | All fail to extract FLOPs. |
| Q22 | L5 | No | No | No | All fail (QQP 72.1). |
| Q23 | L5 | No | No | No | All wrong (40.4); answers 38.5% / 46.8%. |
| Q24 | L5 | Yes | Yes | No | dense/bm25: 44.5. hybrid: 48.2 (wrong). |
| Q25 | L6 | No | No | No | All give 8 heads d=64, none state d_model=512. |
| Q26 | L6 | No | No | Yes | hybrid: d_ff=2048. dense/bm25 say it's not specified. |
| Q27 | L6 | Yes | No | No | dense: H=1024, 16 heads. bm25/hybrid hallucinate 16,000. |
| Q28 | L7 | No | No | No | All garbled (√1). |
| Q29 | L7 | No | No | No | None give the inner-product / MIPS formula. |
| Q30 | L8 | No | No | No | All fail. |
| Q31 | L8 | No | No | No | All fail. |
| Q32 | L8 | No | No | No | All fail. |

| Config | Correct | Success Rate |
|---|---|---|
| dense | 12 | 37% |
| bm25 | 13 | 41% |
| hybrid-rrf | 13 | 41% |

---

## reranking

| Q | Level | no rerank | rerank | Notes |
|---|---|---|---|---|
| Q1 | L1 | No | Yes | rerank surfaces the chunk with 57ms / 3x; no-rerank garbles the numbers. |
| Q2 | L1 | Yes | No | rerank states 11/47 (23%) but never gives →3/47 (6%), confuses with 2.7%. |
| Q3 | L1 | Yes | Yes | Both: ~100,000 chunks. |
| Q4 | L1 | Yes | Yes | Both: paraphrastic / low lexical overlap. |
| Q5 | L1 | Yes | Yes | Both name BART large. |
| Q6 | L2 | Yes | Yes | Both: 0.743. |
| Q7 | L2 | No | No | Both wrong. |
| Q8 | L2 | No | Yes | rerank: 4 / 1 ms. no-rerank says both 4ms. |
| Q9 | L2 | No | Yes | rerank: 44.5. no-rerank: 41.5. |
| Q10 | L2 | No | No | Both fail (rerank: 69%/47%). |
| Q11 | L2 | No | Yes | rerank: RAG-Sequence 68.2. no-rerank picks QANet. |
| Q12 | L3 | Yes | Yes | Both: 128 / 50. |
| Q13 | L3 | No | No | Both wrong (15% / 0%). |
| Q14 | L4 | Yes | Yes | Both distinguish per-token vs per-sequence. |
| Q15 | L4 | Yes | Yes | Both: DPR. |
| Q16 | L4 | No | Yes | rerank: MLM + NSP. no-rerank says "A/B". |
| Q17 | L4 | Yes | Yes | Both: 15%. |
| Q18 | L4 | Yes | Yes | Both: salient span masking. |
| Q19 | L4 | No | No | Neither gives all three reasons. |
| Q20 | L5 | No | No | rerank gives 41.8 (Transformer-big, not ConvS2S). |
| Q21 | L5 | No | No | Both fail. |
| Q22 | L5 | No | No | rerank guesses 91.8% (wrong). |
| Q23 | L5 | No | No | rerank: 46.8% (wrong). |
| Q24 | L5 | Yes | Yes | Both: 44.5. |
| Q25 | L6 | No | No | Both give d=64, neither states d_model=512. |
| Q26 | L6 | No | Yes | rerank names 2048 (hedged); no-rerank says not specified. |
| Q27 | L6 | Yes | No | no-rerank: H=1024, 16 heads. rerank hallucinates 16M / 12 heads. |
| Q28 | L7 | No | No | Both garbled (√1 / √d). |
| Q29 | L7 | No | No | Neither gives MIPS / inner product. |
| Q30 | L8 | No | No | Both fail. |
| Q31 | L8 | No | No | Both fail. |
| Q32 | L8 | No | No | Both fail. |

| Config | Correct | Success Rate |
|---|---|---|
| no rerank | 12 | 37% |
| rerank | 16 | 50% |

---

## fusion

| Q | Level | hybrid-rrf | hybrid-weighted | Notes |
|---|---|---|---|---|
| Q1 | L1 | No | No | rrf garbles (18 vs 21ms); weighted rambles and reverses the latency direction. |
| Q2 | L1 | Yes | Yes | Both: 23%→6%. |
| Q3 | L1 | Yes | Yes | Both: ~100,000 chunks. |
| Q4 | L1 | Yes | Yes | Both: paraphrastic / low lexical overlap. |
| Q5 | L1 | Yes | No | rrf states BART large; weighted says "BART" with a wrong expansion, no "large". |
| Q6 | L2 | Yes | No | rrf: 0.743. weighted says it's not provided. |
| Q7 | L2 | No | No | Both wrong (46.9 / E9). |
| Q8 | L2 | Yes | Yes | Both: 4 / 1 ms. |
| Q9 | L2 | Yes | Yes | Both: 44.5. |
| Q10 | L2 | No | No | Both fail. |
| Q11 | L2 | Yes | No | rrf: RAG-Sequence. weighted picks BERT Single (wrong). |
| Q12 | L3 | Yes | Yes | Both: 128 / 50. |
| Q13 | L3 | No | No | Both wrong (15% / 50%). |
| Q14 | L4 | No | No | Neither clearly states RAG-Sequence reuses one document. |
| Q15 | L4 | No | Yes | weighted: DPR bi-encoder. rrf mis-describes as cross-encoder reader. |
| Q16 | L4 | Yes | Yes | Both: MLM + NSP. |
| Q17 | L4 | Yes | Yes | Both: 15%. |
| Q18 | L4 | Yes | Yes | Both: salient span masking. |
| Q19 | L4 | No | No | rrf vague; weighted refuses. |
| Q20 | L5 | No | No | Both fail. |
| Q21 | L5 | No | No | Both fail. |
| Q22 | L5 | No | No | Both fail. |
| Q23 | L5 | No | No | rrf: 46.8%, weighted: 38.5% (both wrong). |
| Q24 | L5 | No | Yes | weighted: 44.5. rrf: 48.2 (wrong). |
| Q25 | L6 | No | No | Both give d=64, neither states d_model=512. |
| Q26 | L6 | Yes | No | rrf: d_ff=2048. weighted says not specified. |
| Q27 | L6 | No | No | rrf: 16,000 dims. weighted swaps to "hidden 16, 1024 heads". |
| Q28 | L7 | No | Yes | weighted: d^(-0.5) = 1/sqrt(d). rrf: √1 (garbled). |
| Q29 | L7 | No | No | Neither gives MIPS / inner product. |
| Q30 | L8 | No | No | Both fail. |
| Q31 | L8 | No | No | Both fail. |
| Q32 | L8 | No | No | Both fail (weighted reverses the result). |

| Config | Correct | Success Rate |
|---|---|---|
| hybrid-rrf | 13 | 41% |
| hybrid-weighted | 12 | 37% |

---

## embed_model

| Q | Level | MiniLM | bge-small | e5-small | bge-base | bge-large | Notes |
|---|---|---|---|---|---|---|---|
| Q1 | L1 | No | No | No | No | Yes | Only bge-large states the 0.743 vs 0.787 (=4.4pt) gap as the reason; others garble the numbers. |
| Q2 | L1 | Yes | Yes | Yes | Yes | Yes | All: 23%→6%. |
| Q3 | L1 | Yes | Yes | Yes | Yes | Yes | All: ~100,000 chunks. |
| Q4 | L1 | Yes | Yes | No | No | Yes | MiniLM/bge-small/bge-large explain low overlap; e5/bge-base ramble or reverse it. |
| Q5 | L1 | Yes | Yes | No | Yes | No | MiniLM/bge-small/bge-base say BART-large; e5 says "Seq2Seq", bge-large says BART (no "large"). |
| Q6 | L2 | Yes | Yes | Yes | Yes | Yes | All: 0.743. |
| Q7 | L2 | No | No | No | No | No | All wrong (0.787 never retrieved). |
| Q8 | L2 | No | Yes | Yes | Yes | Yes | MiniLM says both 4ms; the four larger embedders give 4 / 1. |
| Q9 | L2 | No | No | Yes | Yes | No | e5/bge-base: 44.5. Others give 41.5 / 45.2. |
| Q10 | L2 | No | No | No | No | No | None give 41.5→43.2 / +1.7. |
| Q11 | L2 | No | Yes | No | No | No | Only bge-small names RAG-Sequence at 68.2. |
| Q12 | L3 | Yes | No | No | Yes | Yes | MiniLM/bge-base/bge-large: 128 / 50. bge-small derails into cache talk; e5 omits overlap. |
| Q13 | L3 | No | No | No | No | No | All wrong (15% / 50%). |
| Q14 | L4 | Yes | No | Yes | No | Yes | MiniLM/e5/bge-large distinguish the two; bge-small/bge-base muddle it. |
| Q15 | L4 | Yes | Yes | No | Yes | Yes | Four name DPR; e5 only says "pre-trained BERT encoder". |
| Q16 | L4 | No | Yes | No | No | Yes | bge-small/bge-large: MLM + NSP. Others say "A/B" or only MLM. |
| Q17 | L4 | Yes | Yes | Yes | Yes | Yes | All: 15%. |
| Q18 | L4 | Yes | Yes | Yes | Yes | Yes | All: salient span masking. |
| Q19 | L4 | No | No | No | No | Yes | Only bge-large gives complexity + parallelism + long-range dependencies. |
| Q20 | L5 | No | No | No | No | Yes | Only bge-large retrieves 41.29 (the table-extraction fix paying off). |
| Q21 | L5 | No | No | No | No | No | All fail (FLOPs). |
| Q22 | L5 | No | No | No | No | No | All fail (QQP 72.1). |
| Q23 | L5 | No | No | No | No | No | All wrong (40.4). |
| Q24 | L5 | Yes | No | No | No | No | Only MiniLM: 44.5. Others hallucinate higher scores. |
| Q25 | L6 | No | No | No | No | No | All give d=64, none state d_model=512. |
| Q26 | L6 | No | No | No | No | No | None state d_ff=2048. |
| Q27 | L6 | Yes | Yes | No | No | No | MiniLM/bge-small: H=1024, 16 heads. Others swap or garble. |
| Q28 | L7 | No | Yes | No | No | No | Only bge-small clearly divides by sqrt(d_k). |
| Q29 | L7 | No | Yes | No | No | No | Only bge-small describes inner-product + top-k retrieval. |
| Q30 | L8 | No | No | No | No | No | All fail. |
| Q31 | L8 | No | No | No | No | No | All fail. |
| Q32 | L8 | No | No | No | No | No | All fail. |

| Config | Correct | Success Rate |
|---|---|---|
| all-MiniLM-L6-v2 | 12 | 37% |
| bge-small-en-v1.5 | 14 | 44% |
| e5-small-v2 | 8 | 25% |
| bge-base-en-v1.5 | 10 | 31% |
| bge-large-en-v1.5 | 14 | 44% |

---

## top_k

`✗` = phi3 emitted off-topic garbage; `—` = empty answer. From k=40 up, the retrieved context (k × ~128 tokens) overflows phi3 and the answers collapse.

| Q | Level | k=5 | k=15 | k=20 | k=30 | k=40 | k=60 | k=80 | k=100 | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | L1 | No | No | No | No | ✗ | — | — | — | None state the 4.4pt/3x tradeoff. |
| Q2 | L1 | Yes | Yes | Yes | Yes | ✗ | — | — | — | k=5–30 all give 23%→6%; collapses at k≥40. |
| Q3 | L1 | Yes | Yes | Yes | No | ✗ | — | — | — | k=30 drifts to "597K / millions". |
| Q4 | L1 | Yes | Yes | Yes | No | ✗ | — | — | — | k=30 loses the low-overlap point. |
| Q5 | L1 | No | Yes | Yes | No | ✗ | — | — | — | k=5/k=30 say "BART" without "large". |
| Q6 | L2 | No | Yes | Yes | Yes | ✗ | — | — | — | 0.743 is out of the top-5 for k=5. |
| Q7 | L2 | No | No | No | No | ✗ | — | — | — | Universally failed. |
| Q8 | L2 | No | No | Yes | No | ✗ | — | — | — | Only k=20 cleanly gives 4 / 1 ms. |
| Q9 | L2 | No | No | Yes | No | ✗ | — | — | — | Only k=20: 44.5. |
| Q10 | L2 | No | No | No | No | ✗ | — | — | — | None give the +1.7 breakdown. |
| Q11 | L2 | No | No | No | No | ✗ | — | — | — | None name RAG-Sequence 68.2. |
| Q12 | L3 | Yes | Yes | No | No | ✗ | — | — | — | k=20 already garbles this. |
| Q13 | L3 | No | No | No | No | ✗ | — | — | — | Universally failed (39%). |
| Q14 | L4 | No | Yes | Yes | No | ✗ | — | — | — | k=5 says they are equivalent. |
| Q15 | L4 | Yes | Yes | Yes | No | ✗ | — | — | — | DPR named through k=20. |
| Q16 | L4 | No | No | No | No | ✗ | — | — | — | None cleanly give MLM + NSP. |
| Q17 | L4 | Yes | Yes | Yes | No | ✗ | — | — | — | 15% through k=20. |
| Q18 | L4 | Yes | Yes | Yes | No | ✗ | — | — | — | Salient span through k=20. |
| Q19 | L4 | No | No | Yes | No | ✗ | — | — | — | Only k=20 gives all three reasons. |
| Q20 | L5 | No | No | No | No | ✗ | — | — | — | Failed (41.29). |
| Q21 | L5 | No | No | No | No | ✗ | — | — | — | Failed (FLOPs). |
| Q22 | L5 | No | No | No | No | ✗ | — | — | — | Failed (QQP). |
| Q23 | L5 | No | No | No | No | ✗ | — | — | — | Failed (40.4). |
| Q24 | L5 | No | Yes | No | No | ✗ | — | — | — | Only k=15: 44.5 (k=20 gives 28.9). |
| Q25 | L6 | No | No | No | No | ✗ | — | — | — | None state d_model=512. |
| Q26 | L6 | No | No | Yes | No | ✗ | — | — | — | Only k=20: d_ff=2048. |
| Q27 | L6 | No | Yes | No | No | ✗ | — | — | — | Only k=15: H=1024, 16 heads. |
| Q28 | L7 | Yes | No | Yes | No | ✗ | — | — | — | k=5/k=20 give 1/sqrt(d_k); k=15 garbles it. |
| Q29 | L7 | No | No | No | No | ✗ | — | — | — | None give MIPS. |
| Q30 | L8 | No | No | No | No | ✗ | — | — | — | Failed. |
| Q31 | L8 | No | No | No | No | ✗ | — | — | — | Failed. |
| Q32 | L8 | No | No | No | No | ✗ | — | — | — | Failed. |

| Config | Correct | Success Rate |
|---|---|---|
| top_k = 5 | 8 | 25% |
| top_k = 15 | 12 | 37% |
| top_k = 20 | 14 | 44% |
| top_k = 30 | 2 | 6% |
| top_k = 40 | 0 | 0% |
| top_k = 60 | 0 | 0% |
| top_k = 80 | 0 | 0% |
| top_k = 100 | 0 | 0% |

> **Context-overload threshold.** k=20 is the peak. At k=30 only the two easiest factual questions survive; at k=40 every answer is off-topic gibberish; at k≥60 phi3 returns empty strings — the prompt has exceeded its context window.

---

## chunk_max_tokens

`✗` = off-topic garbage; `—` = empty. At top_k=15, chunk size multiplies the context (15 × tokens), so 256/512/1024 overload phi3 the same way high top_k does.

| Q | Level | 64 | 128 | 256 | 512 | 1024 | Notes |
|---|---|---|---|---|---|---|---|
| Q1 | L1 | No | No | ✗ | ✗ | — | Neither small size states the tradeoff. |
| Q2 | L1 | Yes | Yes | ✗ | ✗ | — | 256 gives a wrong "8/40 (19%)". |
| Q3 | L1 | Yes | Yes | ✗ | ✗ | — | ~100,000 at 64/128. |
| Q4 | L1 | Yes | Yes | ✗ | ✗ | — | Low overlap at 64/128. |
| Q5 | L1 | Yes | Yes | ✗ | ✗ | — | BART-large at 64/128. |
| Q6 | L2 | No | Yes | ✗ | ✗ | — | 64 splits the table and misses 0.743. |
| Q7 | L2 | No | No | ✗ | ✗ | — | Universally failed. |
| Q8 | L2 | No | No | ✗ | ✗ | — | 64 says both 4ms. |
| Q9 | L2 | Yes | No | ✗ | ✗ | — | 64 retrieves 44.5; 128 gives 41.5. |
| Q10 | L2 | No | No | ✗ | ✗ | — | None give the +1.7 breakdown. |
| Q11 | L2 | No | No | ✗ | ✗ | — | Neither names RAG-Sequence 68.2. |
| Q12 | L3 | Yes | Yes | ✗ | ✗ | — | 128 / 50 at both small sizes. |
| Q13 | L3 | No | No | ✗ | ✗ | — | Universally failed (39%). |
| Q14 | L4 | No | Yes | ✗ | ✗ | — | 64 garbles the distinction. |
| Q15 | L4 | Yes | Yes | ✗ | ✗ | — | DPR at 64/128. |
| Q16 | L4 | No | No | ✗ | ✗ | — | Neither cleanly gives MLM + NSP. |
| Q17 | L4 | Yes | Yes | ✗ | ✗ | — | 15% at 64/128. |
| Q18 | L4 | Yes | Yes | ✗ | ✗ | — | Salient span at 64/128. |
| Q19 | L4 | No | No | ✗ | ✗ | — | Path length missing. |
| Q20 | L5 | No | No | ✗ | ✗ | — | Failed (41.29). |
| Q21 | L5 | No | No | ✗ | ✗ | — | Failed (FLOPs). |
| Q22 | L5 | No | No | ✗ | ✗ | — | Failed (QQP). |
| Q23 | L5 | No | No | ✗ | ✗ | — | 64 hallucinates 93.87%. |
| Q24 | L5 | No | Yes | ✗ | ✗ | — | 64 gives 69.4%; 128: 44.5. |
| Q25 | L6 | No | No | ✗ | ✗ | — | Neither states d_model=512. |
| Q26 | L6 | Yes | No | ✗ | ✗ | — | 64 gives d_ff=2048; 128 says not specified. |
| Q27 | L6 | No | No | ✗ | ✗ | — | Neither: 1024 / 16. |
| Q28 | L7 | Yes | No | ✗ | ✗ | — | 64 gives 1/sqrt(d); 128 garbles √1. |
| Q29 | L7 | No | No | ✗ | ✗ | — | Neither gives MIPS. |
| Q30 | L8 | No | No | ✗ | ✗ | — | Failed. |
| Q31 | L8 | No | No | ✗ | ✗ | — | Failed. |
| Q32 | L8 | No | No | ✗ | ✗ | — | Failed. |

| Config | Correct | Success Rate |
|---|---|---|
| chunk_max_tokens = 64 | 11 | 34% |
| chunk_max_tokens = 128 | 12 | 37% |
| chunk_max_tokens = 256 | 0 | 0% |
| chunk_max_tokens = 512 | 0 | 0% |
| chunk_max_tokens = 1024 | 0 | 0% |

> 64 and 128 are interchangeable in overall score, but they hit *different* questions: 64 wins Q9/Q26/Q28 (more, smaller, individually-retrievable chunks), 128 wins Q6/Q14/Q24 (relevant sentence kept intact). 256+ collapses entirely from context overload.

---

## Per-question correctness across all configs

**Deduplication note:** there are **21 unique configs**. The canonical baseline (dense · MiniLM · top_k=15 · tokens=128 · no-rerank) appears in **six** dimensions — as `RAG`, `dense`, `no rerank`, `all-MiniLM-L6-v2`, `top_k=15`, and `tokens=128` — and is counted **once**. `hybrid-rrf` appears in both `retrieval` and `fusion` and is counted once. The 21 configs: baseline, no-RAG, bm25, hybrid-rrf, hybrid-weighted, rerank, bge-small, e5-small, bge-base, bge-large, top_k∈{5,20,30,40,60,80,100}, tokens∈{64,256,512,1024}.

| Q | Level | Configs correct (of 21) | What happened |
|---|---|---|---|
| Q1 | L1 | 3 | Only bm25, rerank, and bge-large recover the 0.787-vs-0.743 (4.4pt) reasoning; everyone else garbles the latency numbers. |
| Q2 | L1 | 12 | Easy lookup (11/47 → 3/47). Fails only on no-RAG, rerank, and the overloaded high-k / large-chunk configs. |
| Q3 | L1 | 12 | ~100,000 chunks — simple numeric lookup; fails on no-RAG and overloaded configs. |
| Q4 | L1 | 10 | Paraphrastic / low-overlap explanation; e5, bge-base, and several configs ramble or reverse it. |
| Q5 | L1 | 8 | "BART-large" is right but configs frequently drop "large" or invent an expansion. |
| Q6 | L2 | 9 | 0.743 lives in a table; only mid-range configs (not k=5, not the large chunks) retrieve the right row. |
| Q7 | L2 | 0 | **Universal failure.** bge-base at 0.787 requires reading the correct embedding-table row — no config does. |
| Q8 | L2 | 9 | IndexFlatIP 4ms / IndexIVF 1ms — the baseline conflates them; bm25/hybrid/bigger embedders separate them. |
| Q9 | L2 | 8 | 44.5 EM; many configs retrieve the DPR value (41.5) instead. |
| Q10 | L2 | 0 | **Universal failure.** Needs two table rows (41.5→43.2, +1.7); never retrieved together. |
| Q11 | L2 | 4 | RAG-Sequence at 68.2 — most configs name the wrong system. |
| Q12 | L3 | 8 | 128 / 50 from config comments; fails when the chunking config dilutes or overloads context. |
| Q13 | L3 | 0 | **Universal failure.** 39% requires arithmetic (50/128); phi3 answers 15% or 50%. |
| Q14 | L4 | 5 | Per-token vs per-sequence; most configs conflate the two. |
| Q15 | L4 | 10 | DPR bi-encoder — named reliably except where context is overloaded. |
| Q16 | L4 | 7 | MLM + NSP; the dense baseline systematically says "A/B", but bm25/hybrid/rerank/bge models get it. |
| Q17 | L4 | 13 | 15% masking rate — the single most reliably answered question. |
| Q18 | L4 | 12 | Salient span masking — well-described in the source. |
| Q19 | L4 | 2 | Three Transformer advantages; only bge-large and k=20 give all three (path length is the usual casualty). |
| Q20 | L5 | 1 | EN-FR BLEU 41.29 — only bge-large finds the (now correctly extracted) table cell. |
| Q21 | L5 | 0 | **Universal failure.** Training FLOPs 3.3×10¹⁸ — never retrieved. |
| Q22 | L5 | 0 | **Universal failure.** QQP 72.1 — the GLUE-table chunk is never retrieved. |
| Q23 | L5 | 0 | **Universal failure.** REALM 40.4 EM — table chunk never retrieved (REALM table has no rules at all). |
| Q24 | L5 | 4 | NQ EM 44.5 — appears more often than other figures; baseline, bm25, weighted, rerank get it. |
| Q25 | L6 | 1 | 8 heads + d_model=512 needs two facts combined; only no-RAG (from parametric knowledge) states 512. |
| Q26 | L6 | 5 | d_ff=2048 — found by no-RAG, hybrid-rrf, rerank, k=20, tokens=64. |
| Q27 | L6 | 2 | BERT-LARGE 1024 / 16 — most configs swap hidden size and head count; only baseline and bge-small are clean. |
| Q28 | L7 | 6 | 1/sqrt(d_k) — answered by no-RAG, weighted, bge-small, k=5, k=20, tokens=64; most others write √1 / √d. |
| Q29 | L7 | 1 | REALM retrieval probability — only bge-small describes inner-product + top-k retrieval. |
| Q30 | L8 | 0 | **Universal failure.** Cross-paper RAG-vs-REALM comparison — needs two PDFs at once. |
| Q31 | L8 | 0 | **Universal failure.** Head-count difference (12 − 8 = 4) — needs two-row lookup + subtraction. |
| Q32 | L8 | 0 | **Universal failure.** Cross-paper WebQuestions comparison. |

---

## Runtime

| Dimension | Total |
|-----------|-------|
| rag_vs_norag | 13.2 min |
| retrieval | 29.3 min |
| fusion | 16.5 min |
| reranking | 24.8 min |
| embed_model | 185.6 min |
| top_k | 162.4 min |
| chunk_max_tokens | 167.5 min |
| **TOTAL** | **599.2 min (~10.0 h)** |

Per-config (uncached) highlights: bge-large 68.2 min (7.6× the cached MiniLM baseline), rerank 24.8 min (~46 s/question), top_k=30 32.8 min (the slowest still-functional run), chunk_max_tokens=512 47.2 min. Notably, tokens=1024 (22.7 min) and the empty top_k≥60 runs are *fast* — phi3 burns little time generating empty / truncated output once the context overflows.

---

## Headline findings

1. **phi3's context window is the binding constraint.** Every knob that adds context to the prompt — higher `top_k`, larger `chunk_max_tokens`, or (to a lesser degree) reranking — eventually collapses output quality. Safe operating point: **top_k = 15–20, chunk_max_tokens = 128**.
2. **Embedding model barely matters, except bge-large.** MiniLM, bge-small, e5, and bge-base land within a few points; bge-large pulls ahead (14/32) mainly by recovering the table questions Q1/Q19/Q20 — a benefit of the booktabs extraction fix, not the embedder alone. It costs 7.6× the runtime.
3. **Reranking helps modestly (12 → 16) but for 24.8 min.** It re-surfaces a handful of table answers (Q1/Q8/Q9/Q11) the plain dense ranking buried.
4. **Five questions are unwinnable for every config:** Q7, Q10, Q13, Q21, Q22, Q23, Q30–Q32 — all either deep-table lookups (Q7/Q21/Q22/Q23), arithmetic (Q13/Q31), or cross-document synthesis (Q10/Q30/Q32) that phi3 cannot do regardless of retrieval.

---

## best-combined run (per-dimension winners stacked)

**Config:** RAG · retriever=hybrid · fusion=rrf · rerank=True · embed=bge-small-en-v1.5 · top_k=20 · chunk_max_tokens=128. Runtime: 33.2 min. (Prompts were ~2,600–3,050 tokens — under the 4096 `num_ctx` cap, so this run was *not* truncated.)

| Q | Question | best-combined answer | Correct |
|---|---|---|---|
| Q1 | MiniLM chosen over bge-base — why? | 0.4-pt gap (0.743 vs 0.761) didn't justify a threefold latency increase | No |
| Q2 | Source attribution → hallucination reduction? | 11/47 (23%) → 3/47 (6%) | Yes |
| Q3 | Corpus size where FAISS IVF pays off? | Above ~100,000 chunks | Yes |
| Q4 | Why BM25 trails DPR more on NQ than TriviaQA? | NQ has longer, paraphrastic questions with lower lexical overlap | Yes |
| Q5 | Generator for RAG-Token/Sequence? | BART-large | Yes |
| Q6 | MiniLM top-5 EM? | 0.743 | Yes |
| Q7 | Highest top-5 EM model + score? | "RAG-Sequence with 81.7 EM" | No |
| Q8 | Query latency IndexFlatIP vs IndexIVF? | 4 ms for both | No |
| Q9 | RAG-Sequence NQ EM? | RAG-Token & RAG-Sequence reach identical NQ EM (44.5) | Yes |
| Q10 | DPR NQ EM top-5 vs top-10? | Says the document gives no specific numbers | No |
| Q11 | Highest TriviaQA EM system? | Rambles; lands on "Ours BERT 78.7", can't decide | No |
| Q12 | Final CHUNK_MAX_TOKENS / CHUNK_OVERLAP? | 128 / 50 | Yes |
| Q13 | Token overlap percentage? | Says the percentage isn't specified | No |
| Q14 | RAG-Token vs RAG-Sequence? | Token: different doc per token; Sequence: one doc throughout | Yes |
| Q15 | What retriever does RAG use? | Pre-trained neural retriever based on DPR | Yes |
| Q16 | BERT's two pre-training tasks? | MLM + NSP | Yes |
| Q17 | % tokens masked in MLM? | 15% | Yes |
| Q18 | REALM masking type + why? | Salient span masking (e.g. "United Kingdom", "July 1969") | Yes |
| Q19 | Three reasons for self-attention? | Parallelization, constant ops / path length, interpretability | Yes |
| Q20 | ConvS2S Ensemble EN-FR BLEU? | Says 41.8 (wrong table row) | No |
| Q21 | Base Transformer training FLOPs? | Gives a formula (480x), no figure | No |
| Q22 | BERT-LARGE QQP score? | 86.2 | No |
| Q23 | REALM NQ-Open EM? | 46.8 EM | No |
| Q24 | RAG-Sequence NQ EM (Lewis)? | 44.5 | Yes |
| Q25 | Transformer base heads + d_model? | 8 heads, head size 64 (never states d_model=512) | No |
| Q26 | Transformer base d_ff? | Claims the dimension isn't specified | No |
| Q27 | BERT-LARGE hidden size + heads? | Hidden size 1024, 16 heads | Yes |
| Q28 | Scaled dot-product scaling factor? | √(1/d) = 1 / sqrt(d) | Yes |
| Q29 | How REALM computes p(z\|x)? | Embeddings + cross-attention; no MIPS / inner-product | No |
| Q30 | RAG vs REALM on NQ-Open? | Not quoted; "best performance retrieving 5 docs" | No |
| Q31 | BERT-BASE vs base Transformer head diff? | BERT has 12 heads; exact difference "not specified" | No |
| Q32 | RAG-Sequence vs REALM on WebQuestions? | RAG beats BM25 by 18 EM; vs REALM not detailed | No |

**Success rate: 16/32 = 50%** (baseline in the same run: 12/32 = 37%).
