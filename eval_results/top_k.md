# top_k

**backend:** ollama · **model:** phi3

| Parameter | top_k=5 | top_k=15 | top_k=20 |
|-----------|--------|--------|--------|
| retriever | dense | dense | dense |
| embed_model | all-MiniLM-L6-v2 | all-MiniLM-L6-v2 | all-MiniLM-L6-v2 |
| rerank | False | False | False |
| top_k | 5 | 15 | 20 |
| no_rag | False | False | False |

---

## Q1 · Level 1

**Question:** Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?  
**Expected:** The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.  
**Source:** `rag_design_notes.md`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The decision to choose `all-MiniLM-L6-v2` as the default embedding model was due to it only having a slightly smaller quality score (by about 4 points) compared to `bge-base-en-v1.5`. However, this small difference in translation and summarization tasks did not justify sacrificing speed - specifically latency that would be three times higher for the local single-user pipeline with MiniLM-L6 when using bge's base model as a reference point on `bge-base-en-v1.5`. | The primary reason for selecting `all-MiniLM-L6-v2` as the default is that despite a significant quality gap of approximately 4.4 points, it only resulted in a threefold increase in latency compared to `bge-base-en-v1.5`. This balance between performance and computational cost makes it more suitable for local single-user pipelines where maintaining low latency is crucial. | The decision to select `all-MiniLM-L6-v2` as the default was driven by its balance of quality and efficiency for local, single-user pipelines in English-to-German translation tasks on a small scale dataset. While there is only a minimal point difference between both models (4.4 points gap), choosing `all-MiniLM-L6-v2` meant the 3× latency increase was justified by not significantly hurting retrieval quality, which remains high at top-5 EM of 0.743 on the eval set when compared to `bge-base-en-v1.5`. |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| Adding 'Source: {source}' before each passage reduced hallucinations on the eval set from 23% (11 out of 47) to 6% (3 out of 47). | Adding 'Source:' before each passage reduced hallucinations on the eval set from 11/47 (23%) to 3/47 (6%). | Adding 'Source: {source}' before each passage reduced hallucinations on the eval set from 11/47 (23%) to 3/47 (6%). This indicates a reduction of approximately 17 percentage points in hallucination. |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| At the current context, with ~4200 chunks total at a chunk length of 128 tokens each (~52kB per document), IVF becomes worthwhile above approximately 100,000 chunks. Below this threshold, IndexFlatIP is kept as default due to its performance advantages for the given corpus size range which appears optimal around 100–150 tokens in length based on empirical testing noted towards the end of context regarding top-5 EM scores and query latencies between different indexing methods. | FAISS IVF becomes worthwhile above ~100,000 chunks of text according to the context provided. | The prompt indicates that FAISS's Incremental and Approximate Nearest Neighbor (IVF) search becomes more valuable than `IndexFlatIP` when the corpus size is above approximately 100,000 chunks. This conclusion comes from empirical results where at a chunk size of ~4,200 tokens for each chunk in an English Wikipedia-like corpus (~38M words), using IVF trades away about 0.7 EM points to achieve queries that are roughly four times faster than those answered by `IndexFlatIP`. |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context provided suggests that the performance discrepancy between BM25 and DPR across different datasets is due to NQ's longer, more paraphrastic questions with low lexical overlap. This indicates retrieval recall issues at small k-values for dense passages on such a dataset where fine-grained context matching becomes crucial. | The context provided suggests that NQ questions tend to be longer and more paraphrastic, which results in a lower lexical overlap with answer passages. BM25 relies on word overlap as part of its retrieval strategy; hence it struggles compared to DPR, which uses dense passage retrieval techniques better suited for the characteristics of NQ questions where lexical cues are less prominent but context and semantics play a larger role. | Natural Questions (NQ) questions are typically longer and more open-ended, often requiring understanding of broader context or synthesis from multiple documents. This contrasts with the shorter, paraphrastic nature of most NQ answers that can be directly extracted without in-depth reading comprehension. DPR's dense retriever performs well on this type of question due to its ability to retrieve and re-rank passages for relevance using BERT embeddings, which is less necessary when lexical overlap with an answer passage exists as it does more frequently in TriviaQA (TQA). Furthermore, the longer nature of NQ questions might reduce retriever recall at small k values, suggesting that a dense retrieval system like DPR can compensate better for this issue. Thus, BM25's performance drop on NQ compared to its relative gain in TriviaQA is likely due to these factors combined with the specific nature of each dataset. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| Both RAG-Token and RAG-Sequence models utilize BART as their underlying sequence generation model, not directly mentioned in the context but is a common practice for such architectures. The original text mainly discusses how these two variants of RAG handle information retrieval differently during generations without specifying that they are using BART underneath them. | BART-large. | BART (Bayesian Autoregressive Transformer) |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context provided does not contain the exact information needed to answer this question regarding the Top-5 Exact Match (EM) score for 'all-MiniLM-L6-v2'. Therefore, I cannot provide an answer based on the given text. | The context provided does not include specific information about a Top-5 EM (Exact Match) score achieved by the model named `all-MiniLM-L6-v2`. Therefore, based on this text alone, I do not have the answer to provide. To find out its performance, one would need additional data or context outside of what is provided here. | 0.743 |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| According to the provided context about RAG Pipeline Design Notes for a synthetic document created for testing purposes, there are no specific details given regarding which particular embedding model achieved the highest top-5 Exact Match (EM) score. Therefore, I cannot extract this information from the text. The answer is not present in the context. | BERT Single system performs with an F1 score of 82.3% for Top Leaderboard Systems as reported on December 10th, 2018. While this data doesn't explicitly mention a top-5 EM (Exact Match) benchmark within the provided context, based on inference from the information given and common performance metrics in natural language processing tasks like those presented by leaderboards such as GlueBenchmark or SQuAD for retrieval systems, BERT is likely to achieve high scores. However, since we are specifically asked about top-5 EM without direct data points provided within this context (and assuming a standard of benchmarks wherein the highest score isn't necessarily denoted with F1 but rather exact matches), one may infer from similar performance patterns and typical outcomes that BERT models would excel in such tasks. Therefore, although an exact number for top-5 EM is not stated explicitly here, we can reasonably speculate that it will be high based on the overall positive results of BERT as reported across various benchmarks mentioned elsewhere within this context document or commonly known performance metrics of state-of-the-art models at their peak. | BERT Single system performs with a Top Leaderboard (Top) F1 score of 81.9% for maximum path lengths in Table 1 provided in the document context. However, it's important to note that while BERT achieves high EM and top-5 exact match rates according to this leaderboard data presented at Dec 10th, 2018, a higher F1 score is not directly mentioned for these metrics within the extracted text snippet provided above. |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| Index IVF has a query latency of 1 ms, while Index Flat IP also yields approximately similar results but with slightly higher index build time. However, to get an exact match between both indices on the same hardware would require repeating identical measurements for fair comparison; hence these values are not directly comparable from just this context. | IndexFlatIP has a query latency of 34 ms, while IndexIVF (with nlist=32) and its index are built in just 1 ms. However, it's important to note that the provided context does not explicitly mention if this is measured for both backends or solely for FAISS with IndexIVF since using different indexing types was part of a comparative experiment between NumPy cosine embeddings and FAISS based approaches which also included their respective latencies. | - IndexFlatIP has a query latency of 34 ms.<br><br>- IndexIVF (nlist=32) has a query latency of 1 ms. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context provided does not contain specific information about what NQ Exact Match scores were achieved by RAG-Sequence in a benchmark report, so I cannot answer this question based on the given text. | RAG-Sequence achieves an Exact Match score of 41.5% on the Natural Questions (NQ) dataset according to Table 2 in the main results section, which indicates its performance when using Dense Passage Retrieval (DPR). Note that this is not a direct answer but rather information inferred from context; retriever models and NLP benchmarking are common topics. However, if you're asking about RAG-Sequence's Exact Match score specifically without the influence of other methods like DPR as mentioned in your question, then it achieves an overall Exact Match (EM) score of 83.5% on TriviaQA and is not explicitly stated for NQ alone in this specific context provided. Please verify with additional sources if necessary. | 44.5 EM on Natural Questions [52] |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| With top-5 retrieval, Dense Passage Retrieval (DPR) achieves an Exact Match (EM) score of 41.5 on the NQ benchmark. When increasing the top-k to include the top 10 passages retrieved per query before generation, there is a gain in EM performance by 1.7 points, resulting in a new EM score for DPR. This suggests that retrieval recall may be more of an issue when fewer relevant documents are considered (small k). However, since exact numbers weren't provided other than the gains and specific benchmarks, we can calculate them as follows:<br><br>Top-5 Retrieval Em on NQ: 41.5 EM points  <br>Increase with Top-10 retrieval: Gain of 1.7 points from top-k increase  <br>New Exact Match (EM) score for DPR at k=10 on NQ = 41.5 + 1.7 = 43.2 EM points | DPR achieves a higher Exact Match (EM) of 44.2% on the NQ dataset when using RAG as the generation model, which is an improvement over its baseline EM performance without this technique detailed in other parts of the context provided. However, there's no direct comparison given for DPR with top-5 vs top-10 retrieval specifically within dense or BM25 systems from NQ to give a precise answer on how their performances differ at these two points directly according to the text above. | DPR achieves an Exact Match score of 44.5 for the NaturalQuestions dataset when using a top-k approach and doesn't specify exact numbers between different k values in the provided text, so we can only infer that it performs above baseline (BM25 EM on NQ is not given but stated to be weak). To understand DPR’s performance specifically for top-5 vs. top-10 retrieval, one would need additional data from Table 6 or other sections of the study mentioned in the text, which are not provided herein. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context provided does not specify which single or ensemble systems achieved the highest Exact Match (EM) on TriviaQA. It only mentions that BM25 retrieval is a strong baseline and gives its EM without comparing it to others, while dense retrieval performs better than BM25 but their exact numbers are also not provided for comparison with other systems in the benchmark report. The context does mention Ours (BERT) achieves an 81.9 F1 on TriviaQA, but this is a different metric and cannot be directly compared to EM without further information about how they relate or which system uses both techniques together if that's relevant for comparison. Therefore, the answer based on the provided context would be that there isn’t enough specific information given in the text regarding other systems achieving higher TriviaQA EM scores than BM25. | System Dev Test - BERT (Single) | Human System |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The final `CHUNK_MAX_TOKENS` value is 128 tokens, while the final `CHUNK_OVERLAP` value is set to 50. These values were selected based on empirical testing and are detailed in point B of the context provided above. | Final configuration of chunking parameters used in Tiktoken accumulation method is as follows:<br>- CHUNK_MAX_TOKENS = 128   # changed from the initial 256 due to empirical evaluation indicating better precision at this token budget.<br>- CHUNK_OVERLAP    = 50    # setting overlap between consecutive chunks for maintaining context continuity across chunk boundaries; higher values did not further improve recall after a certain point of increase in the value, hence chosen as is from empirical results obtained during testing phase which showed no significant improvement beyond this overlapping size. | Final `CHUNK_MAX_TOKENS`: 128  <br>Final `CHUNK_OVERLAP`: 50  <br> |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| 50% | The context provided does not specify a particular percentage for the "token overlap" directly; therefore, I cannot provide an exact number from the given text as it stands incomplete and possibly missing information. However, there is mention of "[LM masking] with a uniform masking rate of 15%," which could imply that this method applies to some form of token processing or selection within chunk generation rather than direct overlap between chunks themselves. If you were asking about the percentage used in another process related to tokens not detailed here, please provide additional context so I can give an accurate answer. | The document mentions that an embedding model was trained with a uniform masking rate of 15% for BERT, which implies this is the token overlap used in their chunking configuration. |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context provided does not explicitly state a difference between RAG-Token and RAG-Sequence when considering them equivalent as target sequences of length one for certain tasks. Instead, it suggests that they can be used interchangeably in such scenarios without indicating any inherent differences other than their representation form (token vs sequence). | The key distinction lies in how they generate responses during sequence generation tasks. The RAG-Token model can draw different latent documents for each target token, allowing it to choose content from several relevant documents when producing an answer. In contrast, the RAG-Sequence Model uses a single retrieved document as one large latent variable and marginalizes over this entire 'document' to generate sequences, treating them similarly to how BERT processes input tokens with shared context across different parts of the text sequence (e.g., [CLS] token). | The main difference lies in their approach to generating responses based on input sequences for tasks like Jeopardy question generation. The RAG models can operate under two different configurations, either considering all tokens as a single target sequence (RAG-Token) or treating each token within the task's contextual representation ([CLS]) independently and in parallel across multiple retrieved documents to form separate responses for each input token when generating outputs (RAG-Sequence).<br><br>In RAG-Token, every time an output is generated during training using a given document z as reference, all other tokens are drawn from the same pool of documents. On the contrary, with the approach in RAG-Sequence, there’s no uniformity among the retrieved sets for different input tokens within one task scenario; instead, each token receives separate and potentially unique background information to maintain contextually relevant responses that align better with factual accuracy or specific details pertinent to Jeopardy questions. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The Retrieval Component of the RAG (Representations from Augmented GPT-3) Model uses DPR (Dense Passage Retrieval). The specific architecture used is based on a bi-encoder design where document representations are produced by encoding documents using BERT and query representations are also generated using BERT. This dense representation of the document then interacts with the encoded input for retrieval purposes, effectively identifying relevant passages that could be useful in answering or generating responses to given inputs. | The Retrieval Component (p(z\|x)) used in the RAG model, as mentioned within a note indicating that it uses DPR's retriever initialized with documents from NQ. This is clarified by stating "Rag-Sequence and Rag-Token are equivalent" when considering target class as one element sequence or token respectively – emphasizing they both utilize the same underlying technology, which in this case would be a bi-encoder trained on Natural Questions (NQ). The exact name of DPR is not provided within the context. | The Retrieval-Augmented Generation (RAG) model utilizes DPR as its retriever component, which stands for Densely Connected Matching Network. The document provided mentions that "DPR [26]" serves as the foundation for RAG's p(z\|x) function within this pipeline design note section of a synthetic document created specifically to demonstrate and test different aspects of RAG models, though it is noted at the beginning of the context not to confuse with real experimental results. |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context provided discusses various aspects of fine-tuning and ablating certain procedures for BERT, but it doesn't specifically mention what the two unsupervised pre-training tasks are that BERT uses. Without this information being explicitly stated in the text given, we cannot determine from the current context alone. | BERT uses MASK and UNMASK strategies as its two pre-training tasks, with different probabilities of using each strategy during MLM (Masked Language Model) training. The left part of the table represents these proportions where BERT might use either the masking or unmasking token to replace a word in a sentence for input into the model's transformer layers. | The question deals with a specific detail in the provided context, which is about the types of unsupervised pre-training tasks used by BERT (Bidirectional Encoder Representations from Transformers). The answer can be directly extracted as follows:<br><br>Answer: Masked LM and Next Sentence Prediction. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| 15% of words are predicted in each batch rather than every word. | 15% of input tokens are masked in BERT's MLM objective. | 15% of all WordPiece tokens in each sequence are randomly chosen for prediction during training, as per BERT's pre-training methodology. |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| REALM uses salient span masking for its pre-training tasks because it involves predicting the original value (the actual text) from a given context where specific tokens are replaced with [MASK] placeholders. This approach directly aligns with REALM's objective of utilizing relevant spans to enhance understanding and representation within encoder outputs for improved question answering performance during finetuning, as opposed to using random token or span masking methods which do not specifically target salient information in the text. | REALM uses a salient span masking scheme that focuses on tokens such as "United Kingdom" or specific dates like “July 1969”. This method ensures the model learns to retrieve examples from documents containing world knowledge, which is crucial since REALM's core strength lies in its ability to use retriever-augmented language models for tasks that require external factual information. | REALM uses salient span masking where it specifically targets spans containing world knowledge or important entities. This is chosen to focus the model's learning on examples that require external information for correct predictions, effectively directing REALM towards solving problems with a need for factual recall rather than just language understanding based solely on local context. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| 1. Self-attention connects all positions with a constant number of operations, unlike recurrent layers which require O(n) sequential operations based on the sequence length n. This makes computations faster for certain lengths and dimensionalities of sequences commonly found in sentence representations used in machine translations like word-piece or byte-pair encoded inputs where dimension d is often larger than sequence length n, as mentioned towards the end of the context.<br><br>2. The self-attention mechanism can yield more interpretable models by inspecting attention distributions which provide insights into how different parts of an input affect each other during processing - a benefit not highlighted for recurrent or convolutional layers in this particular model architecture design choice. <br><br>3. Shorter maximum path lengths between any two positions make it easier to learn long-range dependencies, suggesting that self-attention mechanisms are more efficient and effective at managing such relationships within data sequences compared to other types of networks like recurrent ones under certain conditions as mentioned in the context regarding computational complexity comparison. | 1. Self-attention allows the model to extrapolate to sequence lengths longer than those encountered during training, unlike recurrent layers which struggle with long sequences due to issues like vanishing gradients and difficulties in parallelization on modern hardware architectures such as GPUs or TPUs.  <br>2. In terms of computational complexity, self-attention is faster for the most common case where sequence length n is smaller than representation dimensionality d—this often occurs with sentence representations used in machine translations like word-piece and byte-pair encodings. Recurrent layers require O(n) sequential operations to connect any two positions while a self-attention layer requires constant time regardless of the input size, which makes it more efficient for longer sequences or when dealing with large batches during inference/testing on parallel computing devices.  <br>3. Self-attention could yield models that are easier to interpret since attention distributions can highlight what different parts of inputs contribute towards decisions made by a model—an aspect not as readily available in RNNs where sequential dependencies make it hard to pinpoint specific cause and effect relationships within the input data during backpropagation. | 1. The total computational complexity per layer is reduced in self-attention mechanisms, making them more efficient compared to RNNs with O(n^2) operations versus O(n).<br><br>2. Self-attention allows for parallel computation because it requires a constant number of sequential operations regardless of sequence length (O(1)), while recurrent layers have complexity that grows linearly or logarithmically with the input size, depending on whether they are unidirectional RNNs or bidirectional ones.<br><br>3. Learning long-range dependencies is more manageable in self-attention as it ensures a shorter path length between any two positions within the network (O(n)), which helps to learn these dependencies better than other layer types that may struggle with longer paths due to their sequential nature or increased complexity with input size. |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context does not provide information about a ConvS2S Ensemble's performance on the WMT 2014 English-to-French task. It only mentions that our big model achieved a BLEU score of 41.0, outperforming all previously published single models at less than one-quarter the training cost of the previous state-of-the-art model. | ConvS2S Ensemble achieved a BLEU score of 26.36 on the WMT 2014 English-to-French translation task. | ConvS2S Ensemble achieved a BLEU score of 83.2 (rounded to 83.2 in the original text) on WMT 2014 English-to-French translation task, as per Table 2 provided above. This result represents an improvement over previous single models and ensembles for this specific language pair. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| To estimate the number of floating-point operations (FLOPs) used to train a particular version of a neural network, we typically use information about its architecture and size. According to Table 2 from Vaswani et al., which compares various model architectures on translation quality and training costs in terms of FLOPs, the base Transformer has been estimated with approximately 41.8 billion floating-point operations for training (referencing rows labeled 'Transformer' under Model EN-DE). | To estimate the number of Floating Point Operations (FLOPs) used for training, we look at Table 2 under "BLEU Training Cost (FLOPs)" and find that the term associated with Transformer (big) is listed as '41.8'. However, this value does not represent FLOP count but rather BLEU score achieved by the model after its training on English-to-German translation tasks. Therefore, based on the information provided in the context, I cannot calculate or determine the exact number of floating point operations used to train the base Transformer model since that specific metric is not given explicitly for it and instead requires an estimate as described: "We estimate the number of floating point operations by multiplying the training time, ...and 5." Without this explicit information on the actual Floating Point Operations count or a direct way to calculate based solely on provided data like GPU capabilities over specific durations (which have been used for other models), it is not possible to provide an answer. The correct response would be that we cannot determine the FLOPs from the given context as there's insufficient information about the training time and the number of operations per second achievable by each GPU in use, which are essential metrics needed alongside with actual numbers on model configuration (layers, heads, etc.) for this estimate. | To estimate the number of floating-point operations (FLOPs) used to train a particular variant of the Transformer, we need information about its size and hardware specifications during training. The given context provides details for three different configurations at varying sizes but does not explicitly give their FLOP estimates or directly state how many are required for each configuration.<br><br>However, it is mentioned that "the number of floating-point operations used to train a model by multiplying the training time, the number of GPUs used, and an estimate of the sustained single-precision floating-point capacity of each GPU 5." Since we have only one specific mention regarding total FLOP costs for different configurations (235M parameters) but without providing their respective sizes or details on how they relate to training time/GPU usage - which are crucial components in calculating the actual number of operations.<br><br>Despite this lack, if any configuration was stated as having a specific cost relative to other models and hardware used (e.g., "235M parameters"), we could use these costs or ratios for estimations by analogy, assuming similar efficiencies in the usage per parameter between different configurations when trained under identical conditions on comparable GPUs with analogous capacities for single-precision floating-point operations (FLOPs).<br><br>Since no explicit number is provided within this context, we are unable to provide a direct answer from the given information alone. However, if you can give any additional data points regarding training times and hardware specifications or ratios of FLOP costs between different configurations when trained under similar conditions on comparable GPUs with analogous capacities for single-precision floating-point operations (FLOPs), we could then attempt to estimate the number. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context does not provide a specific QQP score for BERT-LARGE on the GLUE benchmark, so I do not have that information. | The question seems to be based on a misunderstanding of context or numbers provided in the original text, as no specific "GLUE" dataset scores are mentioned for any task named QQP. Instead, there's mention of BERT achieving an absolute accuracy improvement and MNLI score improvements over previous benchmarks. However, without explicit information regarding GLUE's scoring system or how to interpret these results with respect to the specific "GLUE" dataset as a whole for tasks like Quora Question Pairs (QQP), we cannot accurately report BERT-LARGE’s QQP score from this context. <br><br>The answer, therefore: The provided text does not contain information about the GLUE benchmark's specific scores achieved by models on the QQP task; thus such a figure could not be given based solely on these details. | According to the context provided in Table 2 under "GLUE Test results, scored by the evaluation server," BERT (Large) obtained an average accuracy of LARGE from five random restarts of fine-tuning on selected GLUE tasks. The exact score is not specified for QQP; however, it does mention that a model with this size ("LARGE") achieved 4.6% absolute improvement over prior state of the art specifically in MNLI and SQuAD benchmarks as stated elsewhere in the text. To obtain an accurate answer regarding BERT-LARGE's QQP score, one would need to refer directly to Table 2 where it details GLUE scores for different tasks including QQP (if provided). Since that data isn’t explicitly mentioned here and cannot be inferred from other context given in the text or standard benchmark results available up until my last update knowledge cutoff in early 2023, I am unable to provide a specific number. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context provided does not include specific scores or results for the exact match of REALM on NaturalQuestions-Open benchmarks, so I cannot provide that information based on this text. | The exact match (EM) scores are not provided in the context for individual components like Encoder or Retriever separately; however, it mentions that after ablating critical components of REALM and reporting end-to-end results as well as EM before any fine-tuning, there is a significant improvement. Specifically, by retrieving 5 documents instead of only 20, the system achieves its overall best performance on NaturalQuestions Open with an increase in accuracy from baseline ORQA scores when not resetting parameters to their initial states and feeding them into fine-tuning post REALM pre-training. The exact match score for such a retrieval situation isn't directly stated, thus the answer would be 'not provided.' | REALM achieves a higher exact match rate compared to ORQA after ablating critical components of REALM, as presented in Table 2. However, the specific numerical Exact Match score for REALM is not provided directly in the context given; hence we cannot provide an exact number from this information alone. To determine the actual numeric value achieved by REALM on NaturalQuestions Open using TF-IDF and BM25 as evaluation metrics before applying any fine-tuning, one would need to refer to Table 2 of Raffel et al., which is not included in your context snippet. |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context provided does not include information about RAG-Sequence's performance with respect to exact match (EM) metrics, such as the one for the NaturalQuestions dataset used by Lewis et al., specifically concerning a year or timeframe when this result was achieved. Therefore, I cannot provide that detail based on the given text alone. | 44.5 EM on Natural Questions [52] | 44.5 EM points |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context provided doesn't explicitly state how many attention heads or the specific dimensions of a single "base" Transformer model uses, as it discusses results for two different BERT-based models with varying numbers of layers (L), hidden sizes (A), and self-attention heads (H). The first mentioned configuration has 12 layers, 768 hidden size, and 6 attention heads. However, the subsequent configurations vary in these parameters without explicitly designating a single "base" model's dimensions or head count from which to directly answer your question within this specific context provided. | The Transformer base model uses 8 attention heads with each having a dimension of d=64 after dividing by h (where h is also equal to 8). This results in an effective multi-headed attention mechanism within the single-layer encoder and decoder. | The Transformer base model uses 8 attention heads with each head having a model dimension of d = 64, where \( h \times d \) equals to 512. This is derived from dividing the total hidden size A (which is also referred to as D in Vaswani et al., 2017) by the number of heads for this particular base model configuration mentioned earlier in the context. |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The provided context does not explicitly mention the dimensions of the feed-forward networks used in the Transformer base models tested by Zhou et al. (2018). It only provides details about variations, parameters counts for different sizes of BERT variants and other transformer experiments but lacks specific information on individual model dimension configurations within these investigations. Therefore, we cannot determine from the context given what feed-forward network dimensions are used in their base models. | The Transformer base model uses a feed-forward neural network with dimensions (1024, 4096). | The dimensions used in the feed-forward networks of the Transformer base model are not specified directly. However, it is implied that there might be a discrep0n as typical hidden size 'd' from encoder/decoder layers (512) does suggest potential dimension for FFN input and output. The standard practice in models like BERT has been to design the feed-forward networks with twice the dimensionality of the attention heads, so we could assume that it might be 64, considering a single head size is mentioned as being half (2). Still without explicit information given in this context for 'd' directly related to FFN layers within Transformer base model. |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context does not provide specific information about a "BERT-LARGE" model with distinct attributes such as the exact hidden size or the precise number of self-attention heads, only that there are models denoted as BERT and LARGE. The closest reference given in this regard is to two sizes:<br><br>1. A smaller version (BASE) which has a parameter count between 105M - 124M with certain hidden size `A=12` and number of heads `H`. However, the exact numbers for layers or attention heads are not explicitly stated as they only provide average accuracies across tasks.<br><br>2. A larger version (LARGE) which has a parameter count between 336M - 408M with certain hidden size and number of self-attention heads also denoted `A=16` and the total parameters mentioned as "Large BERT" without further specifics on layers or attention heads.<br><br>Without more detailed information, we cannot accurately provide these details for a hypothetical "BERT-LARGE". | The BERT-LARGE model has a hidden size (A) of 16 and uses 1024 self-attention heads. It also contains approximately 340 million parameters in total for the encoder, as stated with "BASE A=16, Total Parameters=340M." | The hidden size for the LARGE version of BERT is 1024, and it has 16 attention heads. These parameters are specifically chosen to increase model capacity in hopes of improving performance on various tasks, as noted from multiple references including a specific exploration found within Section 5.2 regarding different sizes' effects on task accuracy. |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The scaling factor applied by Scaled Dot-Product Attention before the softmax is square root of one (1). However, this context seems to contain a typographical error or incomplete information because it mentions "scaled dot products by ." The intended scale might be related but not clearly specified in the provided text. Therefore, based on available context, I cannot provide an exact numeric scaling factor beyond acknowledging that some form of scaling is used prior to applying softmax with very small gradients being a concern for large k d values as mentioned in the passage. | The square root of the inverse number of dimensions (sqrt(1/d)) as a scaling factor is applied to the dot products before applying the softmax function in Scaled Dot-Product Attention. This counteracts diminishing gradients for large values of 'k' when the product dimension grows larger, facilitating stable training dynamics. | √1/sqrt(d) |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| REALM computes this using a probabilistic model where it samples p(z \| x), which represents drawing documents from knowledge corpus Z conditioned on an input question/sentence. This process models the likelihood of retrieving specific useful information in response to a given query or context provided by 'x'. | REALM computes this probability by modeling it as a distribution p(z \| x), which is sampled during pre-training and fine-tuning. The specific calculation for how REALM derives the retrieval probabilities isn't directly provided in the context, but based on common practices of similar models like BERT, this probability likely reflects relevance scores that document z has with input x before any fine-tuning is applied to improve it further. | REALM computes the probability p(z \| x) as a sample from this distribution during pre-training and fine-tuning tasks. It represents how likely it is to retrieve document z when provided with an input example x, which helps in augmenting language model predictions by incorporating relevant external knowledge documents retrieved through its unsupervised learning mechanism based on the relevance score f(x, z). |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The context provided doesn't directly compare the performance of RAG and REALM models on the NaturalQuestions dataset. However, it does mention that ORQA is used as a point of comparison for both systems in their similarity to one another. Since we do not have explicit comparative results or metrics between RAG-Sequence/RAG-Token and REALM on this specific task within the context given, I can't provide an accurate answer based on that information alone. If there are external sources comparing these models directly with NaturalQuestions Open dataset performance details available outside of this text snippet, those would need to be consulted for a precise comparison result. | The context provided gives a detailed comparison between two systems, RAG and REALM. However, the specific performance metrics of these models on the NaturalQuestions-Open benchmark are not directly stated in the given text excerpts from different research papers or documents. To accurately answer this question about their comparative performance on that particular dataset would require additional information specifically mentioning results from experiments conducted with both systems on NaturalQuestions Open, which is absent within these contexts. Therefore, based on the provided texts alone, we do not have sufficient information to compare RAG and REALM' fairness scores directly for this specific task.<br> | According to the context, both papers report results for natural language question answering tasks using their respective models. However, Lewis's paper presents RAG-Sequence and RAG-Token as new state of the art performers across different open-domain QA benchmarks (NaturalQuestions Open among others). In contrast, Guu et al.'s study does not directly compare REALM to RAG in this context. Instead, they aimed at improving pre-training methods and found that their method outperformed ORQA by fine-tuning identical setups with different training data (X = Wikipedia vs Z = Wikipedia). To get an accurate comparison of the performance between RAG from Lewis 2020's study and REALM from Guu et al.'s work specifically on NaturalQuestions Open, we would need to refer directly to their experimental results or tables within these papers.<br><br>The provided context does not include a direct numerical evaluation table comparing both models side by side for the exact task of answering natural questions using open-domain QA datasets like NQ (Natural Questions). Thus, based on this specific information alone from the given text snippets, we cannot accurately determine how RAG compares to REALM in terms of performance on NaturalQuestions Open. |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| BERT-BASE has a total of 768 attention heads, while the provided context doesn't specify an exact number for the base Transformer model. However, given that we know about BERT models which use multi-head attention with d = h = 64 and have different numbers (12 or 24) of layers L and a variable hidden size A ranging from 12 to 16 in this context, it's implied there is at least one self-attention head. Since BERT models fundamentally operate with multiple attention heads for parallel processing within each layer (typically upwards of the number mentioned), we can infer that a single head would be highly insufficient and thus traditionally employ 12 or more, as per common configurations in similar architectures like standard BERT. As such, if there is indeed only one self-attention head at maximum for any given layer (which was implied to have been reduced due to the smaller dimensions), then even with a single attention head across all layers of 12 or more - as would be common in many variations prior optimization and scaling adjustments mentioned elsewhere, like GPT's constrained self-attention – BERT models likely employ significantly higher numbers compared to any baseline Transformer model not explicitly detailed here. In this context without an exact number for the base Transformer head count provided directly afterward or earlier in the text cited above (as per Vaswani et al., 2017), we cannot specify a precise difference but can assert that BERT-BASE, with its configuration of multi-head attention and multiple layers across it significantly surpasses traditional single-headed Transformer models. For an accurate answer detailing the exact number more than one head in the base model if there was such specification within Vaswani et al., 2017 or another source cited, we cannot give a precise figure without that specific context being present here. | Bert-Base has 7 and Bert-Large has 5, so BERT-Base has 2 more attention heads than a baseline single-headed or non-Transformer based model. However, since we are comparing to the base Transformer mentioned in Vaswani et al.'s original paper which uses d = 64 / h and typically employs one head (when not explicitly mentioning multiple), BERT'sem attention heads could be considered as having substantially more complexity per computationally independent unit, but we can say it has at least two additional full-fledged multi-headed units over a single traditional Transformer. | BERT-BASE has a total of 768 attention heads, while mentioning that it uses multi-head attention in three different ways without explicitly stating how many this would be over its "base" counterpart. This appears to present an oversight or mistake as the question seems incomplete and asks for comparison data not provided directly within the context given.<br><br>To accurately answer, we can assume a hypothetical base Transformer model might have 8 attention heads (from Table 3 rows of B), then compare it with the actual number in BERT-BASE which is stated as having 768 total attention heads. The difference would be:<br><br>768 - 8 = 752 more attention heads |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| top_k=5 | top_k=15 | top_k=20 |
|---|---|---|
| The provided context does not contain direct comparison results between RAG-Sequence and REALM on the specific task of answering WebQuestions. Therefore, I cannot provide a comparison based on this information alone. | Both systems demonstrate strong performance on the Natural Questions dataset, but specific comparison scores are not directly provided in the context. To accurately determine how RAG-Sequence compares to REALM on WebQuestions specifically for this task, one would need additional data that is not present within the given text. It's suggested however that both models perform well and even though details about their performance differences or similarities are missing from the context provided, they seem competitive based on overall scores mentioned in relation to other benchmarks like TriviaQA and Natural Questions for different systems. | Rag-Sequence outperforms the state of the art, including LEAF and ORQA. However, its performance is slightly behind that of RAG compared across all tasks mentioned in Table 1. It's important to note from the context provided that although both models have achieved strong open-domain QA (ODQA) results without specialized pre-training techniques like salient span masking or extensive external knowledge corpus, their exact numerical comparison on WebQuestions specifically is not directly stated in the given text. |
