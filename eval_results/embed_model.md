# embed_model

**backend:** ollama · **model:** phi3

| Parameter | all-MiniLM-L6-v2 | bge-small-en | e5-small |
|-----------|--------|--------|--------|
| retriever | dense | dense | dense |
| embed_model | all-MiniLM-L6-v2 | BAAI/bge-small-en-v1.5 | intfloat/e5-small-v2 |
| rerank | False | False | False |
| top_k | 5 | 5 | 5 |
| no_rag | False | False | False |

---

## Q1 · Level 1

**Question:** Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?  
**Expected:** The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The choice of `all-MiniLM-L6-v2` over `bge-base-en-v1.5` was primarily due to the fact that, despite a quality gap of only 4.4 points (as per EM scores), using `bge-base-en-v1.5` would have led to three times higher latency in a local single-user pipeline setting on Ubuntu systems with an Intel i7 CPU and NVIDIA GTX TITAN GPU, whereas the latencies of all tested models (including MiniLM) were within 0.3 seconds or less for this configuration. | The primary reason, based on context given, is that despite a slight quality gap of just about 4.4 points with BGE-Base En V1.5 (Bilingual Generative Encoder), the MiniLM model (`all-MiniLM-L6-v2`) was chosen as it maintained better latency which does not require increasing by three times like `bge-base-en-v1.5` in a local, single-user pipeline setting. | The context provided reveals that although there is only a minor quality gap of about 4.4 points between `all-MiniLM-L6-v2` and `bge-base-en-v1.5`, the latter model experiences significantly higher latency, specifically three times as long on average (3×), which does not justify its use for a local, single-user pipeline where performance is essential. |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| Adding 'Source: {source}' before each passage reduced hallucinations on the eval set from 23% (11/47) to 6% (3/47). | By adding 'Source: {source}' before each passage, hallucinations on the eval set were reduced from a rate of 23% (11/47 instances) down to 6% (3/47 instances). This change indicates that explicitly attributing source information significantly decreased the frequency of hallucinations in RAG models. | Adding 'Source: {source}' before each passage reduced hallucinations from 11/47 (23%) to 3/47 (6%). |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context provided indicates that at the current corpus size of approximately 4,200 chunks, the speedup gained by using IVF in place of `IndexFlatIP` is not significant. FAISS's IndexIVF becomes worthwhile above roughly 100,000 chunks according to this context. | 100,000 chunks or above. | <br>FAISS only becomes worthwhile above ~100,000 chunks. |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The gap between BM25's performance on NQ compared to its performance on TriviaQA can be attributed to the nature of questions in each dataset. In NaturalQuestions, many questions are longer and more paraphrastic with low lexical overlap with their answer passages, which presents a challenge for sparse retrieval models like BM25 that rely heavily on keyword matching. Dense Passage Retrieval (DPR), using a bi-encoder trained specifically to identify dense semantic matches in the text, is better suited to handle such questions as it does not solely depend on lexical cues but rather captures deeper contextual relevance between passages and answers. Conversely, TriviaQA contains shorter queries with more apparent answer phrases that likely benefit from BM25's keyword-focused retrieval strategy, thus leveling the playing field for sparse retrievers like BM25 against dense ones such as DPR in this context. | The context doesn't provide a specific reason for why BM25 falls significantly behind DPR on NQ compared to its performance on TriviaQA. However, it does mention that the gap may reflect NQ's longer and more paraphrastic questions with low lexical overlap between answer passages, suggesting this could be one of the reasons for the discrepancy in results. | BM25 falls significantly shorter in scores compared to dense retrieval methods such as DPR, due primarily because of the lexical overlap between questions and their corresponding answers. In datasets like NQ where the gap is wider (34 points), BM25's performance drops notably when contrasted with its results on TriviaQA which only shows a 0.7-point EM difference favoring DPR, suggesting that retriever recall significantly impacts outcomes at smaller top-k values in NQ compared to other datasets like WebQuestions and TriviaQA where this gap is not as pronounced (2 points). |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| BART (Bidirectional and Auto-Regressive Transformer) models are used by both the RAG-Token and RAG-Sequence generators. The context suggests that these BART based generators incorporate a retriever component as part of their architecture, which is trained in conjunction with them to enhance performance on various tasks like MS MARCO Jeopardy QGen 89.6% accuracy for the top model used by RAG-Sequence and similar results are achieved using RAG-Token models when compared directly within this context's figures or tables (not provided here). However, without specific references to these performances in Table 5 regarding distinct ngram diversity comparison between different generators including BART based ones with each other and non-BART baselines like GPT2XL, we can only infer that RAG models operate on top of a BART framework. | BART | BART-large |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context provided does not include the exact match scores for any models, including `all-MiniLM-L6-v2`. Therefore, I do not have this information. | 0.743 | The table in the context shows that `all-MiniLM-L6-v2` achieves a top-5 EM (Exact Match) score of 0.743 on the evaluation set covering the NLP/LLM paper corpus. |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context does not provide information about which specific embedding model achieved the highest Top-5 Exact Match (EM) or any scoring details. It only discusses various aspects of RAG pipeline design without giving explicit benchmark numbers for different models' performances within this particular document. Therefore, we cannot determine from the provided text alone which embedding model has the best top-5 EM score and what that score is. | Ours BERT with a top-5 EM of 81.9. | The question seems to be asking about a specific scoring metric called "top-5 EM," which typically refers to the accuracy of retrieving the correct answer within the top five retrieved items. However, based on this context alone there's no direct mention of an embedding model achieving the highest score for any particular evaluation metrics such as 'top-5 EM'. We are given information about various models and their parameters but not specific scores or accuracies tied to these details in relation to top-5 EM. Therefore, I do not have enough information to answer this question based on the provided context alone. |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| IndexFlatIP has a query latency of 34 ms, while IndexIVF (nlist=32) reduces it to 1 ms. | Query latency for both IndexFlatIP and IndexIVF (with nlist=32) is 1 ms, as they produce identical results in exact search. However, it's worth noting that even though the query speedup might seem advantageous at first glance due to its "4×" value mentioned near IVF benchmarks, this improvement becomes irrelevant with a current corpus size of around ~4,200 chunks as per the context provided. | Query latency for `IndexFlatIP` and `IndexIVF (nlist=32)` are respectively 4 ms and 1 ms. This indicates that IVF offers a significantly faster query response time compared to the flat indexing method used in FAISS, which can be an important factor depending on real-time requirements of search applications. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context provided does not contain specific information regarding what RAG-Sequence achieves with respect to the NQ Exact Match metric within a benchmark report. Therefore, I cannot extract this data from the given text. | RAG-Sequence achieves an overall score of more than 41.5 EM points on the NQ dataset according to Table 1 and Section "Main Results" from the context provided above. This suggests that RAG-Sequence outperforms BM25 by a significant margin, as it exceeds this benchmark point while using dense retrieval techniques like DPR instead of traditional ranking methods such as BM25. | 48.5 EM (without using any information from beyond "RAG-Token and RAG-Sequence reach identical NQ EM") or according to the context, it achieved an exact match score of 44.5 on the test split for NQ benchmarks as shown in Table 1 under Main Results in their report. |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| Dense Passage Retrieval (DPR) achieves an Exact Match score of 41.5 EM on the NQ benchmark using a top-5 retrieval strategy and improves to 44.5 EM when utilizing a top-10 retrieval approach. | With top-5 retrieval, Dense Passage Retrieval (DPR) achieves an Exact Match (EM) score of 41.5 on NQ; when the number of retrieved passages increases to top-10, there is a gain in EM points by 1.7, resulting in a total EM score of 43.2 for DPR on NQ with this larger retrieval setting. | The context provided does not specify the exact numbers for DPR's performance on NQ using a top-5 versus top-10 retrieval. Therefore, I cannot provide an answer based on this information alone. The gap in EM points between different sizes of k suggests that there is some benefit to increasing k from 5 to 10 passages, but the precise impact on DPR's NQ EM performance isn't given explicitly in the text provided. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The question asks about a specific performance metric, Exact Match (EM), on the dataset called TriviaQA. However, based on the context provided regarding various systems and their performances across different datasets, it's clear that there is no explicit mention of which system achieved the highest EM score specifically for TriviaQA in this benchmark report. As such, I cannot provide an answer from the given information. The statement "the question cannot be answered based on the context" applies here. | Ensemble - QANet with an exact match score of 84.5 on TriviaQA according to Table 2 from the "System Dev Test" results provided within the context. | The Single - MIR-MRC (F-Net) System achieves an Exact Match score of 78.0 on TriviaQA, which is noted as being higher than other mentioned systems including BERT when used alone and the Published unet ensemble system in their respective categories according to Table 2 from the context provided. |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The final 'CHUNK_MAX_TOKENS' value is 128, while 'CHUNK_OVERLAP' has a set value of 50. These configurations were selected based on empirical testing to balance precision and recall for the specific corpus size used in their experiments. | ```python<br>CHUNK_MAX_TOKENS = 128   # changed from 256 in V2-D after eval; smaller chunks improved precision<br>CHUNK_OVERLAP    = 50    # 39% overlap; higher values did not improve recall beyond this point<br>``` | Final configuration for token budget is CHUNK_MAX_TOKENS = 128. The value of overlap set to be CHUNK_OVERLAP=50 tokens. These were empirically determined based on their impact on precision and recall, specifically around the corpus size which was approximately 4,200 chunks in total at this token budget for a good balance between them as per provided context. |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| 39% | The current chunking configuration uses a 50% token overlap percentage. | The current chunking configuration uses a token overlap of 39%. |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| RAG-Token processes sequences of text as discrete tokens, while RAG-Sequence operates on entire sequences of text without breaking them into tokens. They are equivalent when targeting a sequence class with length one because in this case the token and sequence representations merge together leading to no functional difference between using either model for that specific task. | The context does not explicitly state a difference between RAG-Token and RAG-Sequence; rather, it implies they are equivalent when considering a target class as a sequence of length one. This equivalence suggests that both models perform the same retrieval process using DPR for documents followed by BART-large generation, even if their operational context differs slightly based on how you view or treat the single token/class as input data. | RAG-Sequence has a higher Edge Measure on TriviaQA (68.2 vs 68.0) as compared to RAG-Token, suggesting that they perform similarly in terms of retrieval recall at small k values but have minor differences within noise for most evaluation budgets. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The Retrieval component of the Replicated Hierarchical Attention mechanism (RAG) uses Dense Passage Retrieval (DPR), which follows a bi-encoder architecture. The document representation is produced by encoding documents with BERT, and query representations are also created using BERT based on queries inputted to it. | The RAG model uses DPR (Dense Passage Retrieval) as its retriever. | The original context does not provide specific information about which type of retriever is utilized by the RAG (Representations from A Question) model itself, but it mentions that "RAG-Token and RAG-Sequence are retrieval-augmented generation models using BART-large as the generator and DPR as the retriever." This implies that within these specific variants of RAG developed by Lewis et al. (2020), a component based on the DistilBERT Retrieval model for Natural Questions is used, which in turn uses Google's T5+SSM pre-trained retriever as its base technology before being fine-tuned to work with DPR's methodology. So while RAG doesn't directly use a single named "retriever," it incorporates techniques from the BERT and DistilBERT models, which are originally used for natural language understanding tasks such as question answering on datasets like Natural Questions (NQ) and TriviaQA. |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| A/B and sentence embeddings during pre-training. | Masked language models and learning bidirectional representations from unlabeled text by jointly conditioning on both left and right contexts in all layers. | The context doesn't provide specific details on which two pre-training tasks BERT uses. It only mentions that it is trained over different pre-training tasks without specifying them. Therefore, based on the provided context, I can't accurately answer this question. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| 15% of tokens are predicted and thus effectively masked. However, only 84 words are replaced with [MASK] across the entire dataset for actual training on this task as per standard procedure mentioned before Masking strategies section which states that MLM model makes predictions in each batch but replaces just around 15% of tokens at a time | 15% | In BERT's MLM objective, 15% of input tokens are uniformly masked for pre-training purposes. This rate is specifically chosen and consistently applied as per the context provided above which indicates that no special consideration was given to partial word pieces during this process. |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| REALM uses salient span masking for its pre-training task because it finds that both the encoder and retriever benefit from this scheme when they are trained separately but performing better in unison. It aims to improve upon random token or span masking by focusing on predicting original values of [MASK] tokens with specific loss functions related to language modeling, as seen in Devlin et al.'s BERT approach (MLM) and SpanBERT's proposal for using entire salient spans. | REALM uses salient span masking during its pre-training phase to focus on problems that require world knowledge for prediction. This is done because not all MLM spans only need local context; some are related directly with the realm of "world" and cannot be predicted solely from immediate textual cues, hence they needed an extra 'inductive bias' in form of salient span masking to improve performance during retrieval-augmented language model tasks. | REALM uses Salient Span Masking. The reason behind this approach is to focus the model's attention on examples that require world knowledge for predicting the missing tokens. By masking spans like "United Kingdom" or "July 1969," REALM encourages its learning process towards understanding and retrieving meaningful information from millions of documents, which in turn enhances performance particularly when fine-tuned on tasks requiring a deep comprehension of the world knowledge. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| 1. Self-attention has shorter paths between positions, making it easier to learn long-range dependencies in the data; and thus requiring fewer sequential operations compared with a Recurrent layer which requires O(n) sequential operations for sequences of length n - resulting in faster computational complexity when sequence lengths are smaller than representation dimensionality.<br>2. Self-attention can yield more interpretable models, as evidenced by attention distributions from the model and presented examples discussed towards the end of their paper. <br>3. Their Transformer architecture uses self-attention which they motivate with its advantages over existing approaches like [17, 18] & [9]. | 1. Self-attention allows extrapolation to sequence lengths longer than those encountered during training, potentially mitigating the vanishing gradient problem in Recurrent Neural Networks (RNN).<br>2. It might be computationally more efficient as separable convolution can make self-attention complexity equal to a combination of self-attention and point-wise feedforward layer—the approach taken by their model, which has similar computational cost to recurrent layers despite the general trend towards higher expense with increased sequence length.<br>3. Self-attention could yield more interpretable models as individual attention heads learn different tasks within a sentence pair translation task in ways related to syntactic and semantic structure of sentences (as inferred from examining attention distributions). <br><br>Please note that while the text mentions benefits regarding efficiency, computational cost is not explicitly stated for all three reasons. The context indicates potential but does not definitively state self-attention's universally better performance across these aspects in every scenario or model design. | 1. Self-Attention requires fewer sequential operations than Recurrent Layers, making it computationally faster when the sequence length is smaller than the representation dimensionality.<br><br>2. Short paths in a network make learning long-range dependencies easier; self-attention layers connect all positions with constant number of sequentially executed operations. <br><br>3. Self-Attention could yield more interpretable models, as it allows inspection of attention distributions and these can clearly learn to perform different tasks related to sentence structure. |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context does not provide information about ConvS2S Ensemble's performance on the WMT 2014 English-to-French task. Therefore, I cannot provide that specific BLEU score based on this text alone. | The context does not provide the specific BLEU score achieved by ConvS2S Ensemble on WMT 2014 English-to-French. Therefore, I cannot answer this question based on the given information. | The context does not provide this information. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The provided context does not explicitly state the number of floating-point operations (FLOPs) used to train the base Transformer model. However, it mentions that we estimate this by multiplying several factors related to training setup and hardware specifications but doesn't provide any direct figures for these calculations in relation to just the baseline transformer cost itself within given parameters or configurations listed above (64x512x8@20M FLOPs/i s, etc.). To find this information without additional context or data not provided would be impossible. | The context does not provide explicit information on the total number of floating-point operations used for training a single instance or parameter count directly to calculate this, but it provides enough data points to estimate an approximate range. For example, Vaswani et al.'s Transformer model uses about `235M = 235 * 10^6` parameters and trains on eight GPUs over 3.5 days for roughly `(8*24*3.5)/(79)*235*(4+2) = ~2,176,000 MFLOPs`.<br>However, without a specific definition of the "training cost" in terms of floating point operations per token or sequence length within this context, it is impossible to provide an exact figure for just one instance. If we interpret training costs solely based on parameters and GPU usage alone (ignoring factors like network architecture intricacies), then using our provided estimate: <br>- Base Transformer's parameter count = `235M` from Al-Rfou et al., but this could differ in other versions. If we take it as a base case, the approximate training cost would be around ~168,000 MFLOPs (assuming similar hardware and time to train). This is calculated assuming all parameters are used once during forward pass of each token: `235M*4*(L+input length + 50)` considering input sequence lengths.<br>This approximation would be a best guess without more specific details about the exact computation mechanisms in terms of MFLOPs per parameter, or how often they are used within training iterations etc., and should therefore not considered as an absolute number but rather indicative range for comparison purposes only. | The context does not provide specific information on the number of floating point operations for the training cost of the Transformer models, only mentioning that mixed precision was used during the process. Therefore, I cannot extract this data from the given text and must say that such a detail is not provided in the context. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context does not provide a specific QQP (Quality Question Pairs) score for BERT-LARGE on the GLUE benchmark. It only mentions that F1 scores are reported for tasks like QQP, but it doesn't give an actual accuracy figure or score from Table 6 which is referenced later in discussing results across all selected tasks and datasets. | The context does not provide specific information regarding a "QQP" (Quality Question Pairs) metric for BERT's performance. However, it mentions that the overall LARGE score of BERT-LARGE on the GLUE benchmark is 80.5 points higher than OpenAI GPT as per the official leaderboard10 and also notes a significant outperformance over prior state-of-the-art models across various tasks in the GLUE task set, which includes QQP (among other datasets). Since BERT's score is significantly high on the overall benchmark but not explicitly stated for individual subtasks like QQP within this text snippet, we cannot determine its exact LARGE score achieved specifically for the QQP dataset. | The context provided does not contain specific information about the question answering (QQP) task score for BERT-LARGE. Therefore, I cannot provide this answer based on the given text. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The exact match scores for REALM are not provided within the context given above. Therefore, I cannot provide that information based solely on this text snippet. | The context provided does not contain specific information regarding the exact match (EM) score that REALM achieves on NaturalQuestions-Open. Therefore, I do not have this data based on the given text. | The provided context does not explicitly state the exact match scores that REALM achieves on NATURALQUESTIONS-OPEN. Therefore, I cannot provide that specific information based solely on the given text. |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| Unfortunately, I cannot provide the exact match score for RAG-Sequence from Lewis et al.'s work as it is not mentioned in the provided context. The information about Exact Match scores specifically pertaining to NaturalQuestions and RAG-Sequence by Lewis et al. has not been included here. | 45.7 EM points higher than BM25 baseline, but specific score not mentioned for NQ benchmark within provided context. | RAG-Sequence achieves an Exact Match score of 68.2% on the test split for NaturalQuestions according to the context provided by Lewis et al. (2020). |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context does not provide explicit information about how many attention heads are used in the baseline or any specifics regarding variations of the Transformer's dimensions. It refers to using d = d / h, where both 'd' and 'h' denote dimension sizes related to keys (k), queries (q), and values (v) within each head but doesn’t specify their exact numbers for attention heads or model dimensions directly in terms of layers L, hidden size A, and the number of self-attention heads H. To answer this question accurately, more specific details from the context are required. | The Transformer uses 8 parallel attention layers (heads) with a model dimension of d = d / h = 64. | The context indicates that there is a single head with an input/output dimensionality denoted as d for each of these 'heads'. However, it's not explicitly mentioned how many such unique attention heads are employed in total within the Transformer base model. Despite this lack of specific numbers regarding multiple distinctive attention mechanisms (or "heads"), we can deduce that there is a conceptual head or set of parallelized computations occurring through self-attention layers, which operate on vectors with dimensionality d = 64 in the Transformer base model. The exact number of such 'heads' isn't stated directly within this given context. |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context provided discusses variations in a Transformer-based model and mentions dimensions such as "L", "A" (the number of layers, hidden size), but it doesn't specifically state what feed-forward network dimension is used. Therefore, I cannot provide an answer based on the given context. | The Transformer base model uses a feed-forward network with dimensions of [512, 2048]. | The provided context does not specify the dimensions of any feed-forward networks used in the Transformer base models, thus I do not have this information based on the given text. |
