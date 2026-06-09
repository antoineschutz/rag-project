# retrieval

**backend:** ollama · **model:** phi3

| Parameter | dense | bm25 | hybrid-rrf |
|-----------|--------|--------|--------|
| retriever | dense | bm25 | hybrid |
| embed_model | all-MiniLM-L6-v2 | — | all-MiniLM-L6-v2 |
| fusion | — | — | rrf |
| alpha | — | — | 0.5 |
| rerank | False | False | False |
| top_k | 15 | 15 | 15 |
| no_rag | False | False | False |

---

## Q1 · Level 1

**Question:** Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?  
**Expected:** The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The primary reason for selecting `all-MiniLM-L6-v2` as the default is that despite a significant quality gap of approximately 4.4 points, it only resulted in a threefold increase in latency compared to `bge-base-en-v1.5`. This balance between performance and computational cost makes it more suitable for local single-user pipelines where maintaining low latency is crucial. | The choice of `all-MiniLM-L6-v2` over `bge-base-en-v1.5` was based on a tradeoff between quality and efficiency for the REALM framework’s retrieval mechanism in zero-trial knowledge injection (KI) setting with few training trials per example during fine-tuning, as mentioned in "Towards Zero-Shot Fine-tuning of Pre-trained Language Models" by Shao et al. The 4.4-point quality gap that `all-MiniLM-L6-v2` had over `bge-base-en-v1.5` was considered acceptable given the latency increase for a local, single-user pipeline – specifically because there would be only three times higher inference time with 3x more GPU memory usage required by `all-MiniLM-L6-v2`. Therefore, in terms of balancing quality against computational resources and efficiency within this specific scenario, `all-MiniLM-L6-v2` was selected as the default. | The selection of `all-MiniLM-L6-v2` as the default was primarily due to it providing a significant improvement in evaluation metrics without incurring prohibitive latency increases compared to using local, single-user pipelines. Despite having only four times fewer parameters and half the computation cost (with respect to floating point operations) of `bge-base-en-v1.5`, it achieved higher top-5 Embedding Mismatch rates in Perplexity on both Wikipedia and CC-News corpora, indicating superior encoding quality from an information retrieval perspective. The decision was also informed by the fact that this model offered faster loading times (0.3s) when using precomputed embeddings compared to `bge-base-en-v1.5`. |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| Adding 'Source:' before each passage reduced hallucinations on the eval set from 11/47 (23%) to 3/47 (6%). | The addition of explicit 'Source:' attribution before each passage in the RAG prompt template reduced hallucinations from 11/47 (23%) on the eval set down to just 3/47 (6%). This reduction represents a decrease by more than half. | The addition of explicit 'Source: {source}' before each passage in the retrieval context reduced hallucinations on the evaluation set from a rate of 11/47 (23%) down to just 3/47 (6%). This indicates that attributing source information significantly decreased model-generated fabrications. |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| FAISS IVF becomes worthwhile above ~100,000 chunks of text according to the context provided. | Above ~100,000 chunks of context data. | The prompt indicates that at the current corpus size, which is approximately 4200 chunks or tokens, the speedup advantage of using FAISS with an IndexIVF becomes negligible. Therefore, it only becomes worthwhile above roughly 100,000 chunks (or when dealing with significantly larger data). |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The context provided suggests that NQ questions tend to be longer and more paraphrastic, which results in a lower lexical overlap with answer passages. BM25 relies on word overlap as part of its retrieval strategy; hence it struggles compared to DPR, which uses dense passage retrieval techniques better suited for the characteristics of NQ questions where lexical cues are less prominent but context and semantics play a larger role. | NaturalQuestions (NQ) presents questions that are longer and more paraphrastic, where lexical overlap with the answer passage is low. Since BM25 relies heavily on word overlap for retrieval efficiency, it falls behind in scenarios requiring dense semantic understanding like NQ when compared to Dense Passage Retrieval (DPR). | The context provided suggests that the gap between BM25 and DPR is due to the nature of questions in different datasets. On NQ, where queries are longer and more paraphrastic with low lexical overlap with answers, dense retrieval methods like DPR perform significantly better as they can handle such complex search requirements effectively by considering broader document representations beyond simple word overlaps. In contrast, BM25 is a sparse baseline that relies heavily on exact keyword matches and falls short in these more abstract scenarios typical of NQ questions compared to the shorter, entity-centric queries found in TriviaQA datasets where lexical overlap between passages and answers plays a crucial role. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| BART-large. | BART-large | BART (Bottom-Up Approximately) large |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The context provided does not include specific information about a Top-5 EM (Exact Match) score achieved by the model named `all-MiniLM-L6-v2`. Therefore, based on this text alone, I do not have the answer to provide. To find out its performance, one would need additional data or context outside of what is provided here. | As per the context provided, it is not directly mentioned how many points 'all-MiniLM-L6-v2' achieves in terms of top-5 Exact Match score. The document does discuss benchmark scores for various models but doesn't provide a specific number associated with `all-MiniLM-L6-v2`. Therefore, the answer to this question cannot be found in the context provided. | 0.743 |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| BERT Single system performs with an F1 score of 82.3% for Top Leaderboard Systems as reported on December 10th, 2018. While this data doesn't explicitly mention a top-5 EM (Exact Match) benchmark within the provided context, based on inference from the information given and common performance metrics in natural language processing tasks like those presented by leaderboards such as GlueBenchmark or SQuAD for retrieval systems, BERT is likely to achieve high scores. However, since we are specifically asked about top-5 EM without direct data points provided within this context (and assuming a standard of benchmarks wherein the highest score isn't necessarily denoted with F1 but rather exact matches), one may infer from similar performance patterns and typical outcomes that BERT models would excel in such tasks. Therefore, although an exact number for top-5 EM is not stated explicitly here, we can reasonably speculate that it will be high based on the overall positive results of BERT as reported across various benchmarks mentioned elsewhere within this context document or commonly known performance metrics of state-of-the-art models at their peak. | RAG (Retrieval Augmented Generation) - Token has the highest reported Exact Match score of 41.8 EM on NQ benchmark according to Table I in the provided context. It outperforms BM25 by an 18 point margin as stated in Section A and is superior even when compared with DPR, which was specifically mentioned for its density retrieval performance but did not achieve a score surpassing RAG-Token's top EM score on NQ benchmark within the context. | The BM25 retriever combined with DPR has an estimated maximum of a hypothetical best possible performance for RAG pipeline design. However, in terms of actual results from similar systems mentioned in Table 2 (which isn't provided), the highest top-5 Exact Match score achieved by one system is not specified directly within this context snippet and thus cannot be determined accurately based on the information given here. |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| IndexFlatIP has a query latency of 34 ms, while IndexIVF (with nlist=32) and its index are built in just 1 ms. However, it's important to note that the provided context does not explicitly mention if this is measured for both backends or solely for FAISS with IndexIVF since using different indexing types was part of a comparative experiment between NumPy cosine embeddings and FAISS based approaches which also included their respective latencies. | Query latency for `IndexFlatIP` is 4 ms, while for `IndexIVF`, it's reduced to just 1 ms. The substantial improvement in speed when using the IVF index can be attributed to its efficient search algorithms and dimensionality reduction techniques employed during indexing. | IndexFlatIP has a query latency of 4 ms while IndexIVF, when using an nlist size of 32 and pre-trained with FAISS on Theta (θ), reduces the query latency to just 1 ms. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| RAG-Sequence achieves an Exact Match score of 41.5% on the Natural Questions (NQ) dataset according to Table 2 in the main results section, which indicates its performance when using Dense Passage Retrieval (DPR). Note that this is not a direct answer but rather information inferred from context; retriever models and NLP benchmarking are common topics. However, if you're asking about RAG-Sequence's Exact Match score specifically without the influence of other methods like DPR as mentioned in your question, then it achieves an overall Exact Match (EM) score of 83.5% on TriviaQA and is not explicitly stated for NQ alone in this specific context provided. Please verify with additional sources if necessary. | In the benchmark report for NaturalQuestions (NQ), RAG-Sequence achieves an NQ Exact Match score of 41.5 EM points, outperforming BM25 by that margin on this particular dataset. This is a notable achievement as it demonstrates superior performance in retrieval and generation tasks when compared to traditional methods like BM25 using dense passage retrieval with generative models such as RAG-Sequence for question answering purposes. | In the context provided about retrieval-augmented generation models and their performance on various benchmarks including Natural Questions (NQ), Retrieval-Augmented Generation from Lewis et al. (2020) reports that RAG-Sequence achieves an NQ Exact Match score of 44.5. |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| DPR achieves a higher Exact Match (EM) of 44.2% on the NQ dataset when using RAG as the generation model, which is an improvement over its baseline EM performance without this technique detailed in other parts of the context provided. However, there's no direct comparison given for DPR with top-5 vs top-10 retrieval specifically within dense or BM25 systems from NQ to give a precise answer on how their performances differ at these two points directly according to the text above. | <br>The context provided discusses various models and their performances across different tasks but it doesn't specifically mention the exact Exact Match (EM) scores for Dense Passage Retrieval on Natural Questions (NQ) using top-5 vs top-10 retrieval. However, there is a section in Table 2 which might contain relevant information:<br>```markdown<br>\| Backend \| Index type            \| Top-5 EM    \| ...   \| Avg latency (ms) \|<br>\|--------\|----------------------\|--------------\|-------\|-------------------\|<br>\| all-MiniLM-L6-v2      \| 22M         \| 0.743        \|       \|                   \|<br>```<br>This suggests that the DPR model, which is based on RAG architecture as indicated by "rag" in its name and uses MiniLM for parameterization (as it's not explicitly mentioned but can be inferred from common knowledge of similar models), achieves an Exact Match score of 0.743 with top-5 retrieval using the all-MiniLM-L6-v2 configuration on NQ, without specifically mentioning its performance for top-10 retrieval in this context. To find exact scores or differences between Top-5 and Top-10 EM performances, one would have to look at additional information not provided within the given context directly after these lines:<br>```markdown<br>... \| all-mpnet-base-v2       \| 109M        \| ...    \|                   \|<br>\| bge-small-en-v1.5      \| 33M         \| ...     \|                   \|<br>\| all-bart_large-bfdnndrk468pt7drd/2 \| N/A          \| 0.761    \|                \|<br>``` | According to the context provided, when comparing different numbers of passages retrieved per query before generation (top-k), increasing from 5 to 10 can provide a gain in Exact Match score on NQ for Dense Passage Retrieval systems. However, specific EM scores are not given for top-10 retrieval or directly stated as superiority over the best non-generative baseline which is claimed by RAG models. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| System Dev Test - BERT (Single) | The single BERT model outperforms all other systems on both SQuAD and TriviaQA, making it the best performing system according to the provided context. For more specific numbers related to the top models' performance not mentioned in the text, we would need additional information from Table 2 or direct mentions within the document regarding individual model scores for each dataset. As per this narrative, while RAG-Token and RAG-Sequence achieve identical results on NQ with an EM of 44.5 which seems to be equal top result among dense retriever systems, it's mentioned that a single BERT outperforms the ensemble system in terms of F1 score during TriviaQA evaluation without providing specific numerical values other than mentioning they lead by +1.3 EM as individual models. Thus, based on this limited information and considering there is no explicit number given for any model's performance that exceeds what BERT achieves mentioned directly in the context provided:<br><br>Answer: The single BERT system | In the provided context, it is stated that on the NLP/LLM paper corpus evaluation set for embedding model benchmarks, BERT achieved a high top-5 Exact Match score. While this information directly pertains to TriviaQA results within the same document where RAG models are discussed and evaluated primarily in relation to Natural Questions (NQ) data—within our provided text snippet on retriever ablation, it is indicated that "RAG-Sequence achieves the highest overall score, outperforming BM25 by 18 EM points on NQ." Since we are asked about TriviaQA and not Natural Questions specifically in this context, there's no explicit mention of a system achieving top scores for RAG models within the provided text snippet related to TriviaQA results. Therefore, based on my knowledge cutoff date without direct information from Table 1 or further details, I cannot provide an answer regarding which system achieved the highest EM score in this particular benchmark report (TriviaQA). The context does not contain enough specifics about the individual systems' performance solely within TriviaQA. |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| Final configuration of chunking parameters used in Tiktoken accumulation method is as follows:<br>- CHUNK_MAX_TOKENS = 128   # changed from the initial 256 due to empirical evaluation indicating better precision at this token budget.<br>- CHUNK_OVERLAP    = 50    # setting overlap between consecutive chunks for maintaining context continuity across chunk boundaries; higher values did not further improve recall after a certain point of increase in the value, hence chosen as is from empirical results obtained during testing phase which showed no significant improvement beyond this overlapping size. | Final 'CHUNK_MAX_TOKENS' is reduced to 128, while 'CHUNK_OVERLAP' remains unspecified in the context. | Final configuration settings used were:<br>```python<br>CHUNK_MAX_TOKENS = 128   # changed from the roadmap's initial 256 tokens after evaluation showed precision improvement.<br>CHUNK_OVERLAP    = 50    # chosen to maintain approximately a 39% overlap between chunks, as higher values did not improve recall beyond this point. |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The context provided does not specify a particular percentage for the "token overlap" directly; therefore, I cannot provide an exact number from the given text as it stands incomplete and possibly missing information. However, there is mention of "[LM masking] with a uniform masking rate of 15%," which could imply that this method applies to some form of token processing or selection within chunk generation rather than direct overlap between chunks themselves. If you were asking about the percentage used in another process related to tokens not detailed here, please provide additional context so I can give an accurate answer. | 15% | 50% |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The key distinction lies in how they generate responses during sequence generation tasks. The RAG-Token model can draw different latent documents for each target token, allowing it to choose content from several relevant documents when producing an answer. In contrast, the RAG-Sequence Model uses a single retrieved document as one large latent variable and marginalizes over this entire 'document' to generate sequences, treating them similarly to how BERT processes input tokens with shared context across different parts of the text sequence (e.g., [CLS] token). | The primary distinction lies in their decoding process at test time. The RAG-Token model approximates arg max p(y\|x) using a standard beam decoder with transition probability (y \| x, y). In contrast, the RAG-Sequence employs pointer networks to output answer spans directly from input text by employing attention mechanism and learnable start/end tokens. | The context provided does not explicitly state any differences between RAG-Token and RAG-Sequence models; it suggests that they are equivalent when considering the target class as a sequence of length one. However, this equivalence is only in terms of their approach to using both retrieval (DPR) and generation components (BART), with no inherent difference mentioned for other scenarios or benchmarks within the provided context. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The Retrieval Component (p(z\|x)) used in the RAG model, as mentioned within a note indicating that it uses DPR's retriever initialized with documents from NQ. This is clarified by stating "Rag-Sequence and Rag-Token are equivalent" when considering target class as one element sequence or token respectively – emphasizing they both utilize the same underlying technology, which in this case would be a bi-encoder trained on Natural Questions (NQ). The exact name of DPR is not provided within the context. | DPR (Dense Passage Retrieval) | The context discusses various aspects of using and improving the RAG (Retrieval-Augmented Generation) system's retrieval component but doesn't specify a particular named "retriever" that RAG uses. Instead, it mentions learning to retrieve relevant information for tasks as part of its functionality, comparing favorably with DPR’s retriever and highlighting improvements when compared against BM25 without indicating the use of an external specific system. It also discusses running ablations by freezing the retriever during training but doesn't mention using a particular named "retriever." |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| BERT uses MASK and UNMASK strategies as its two pre-training tasks, with different probabilities of using each strategy during MLM (Masked Language Model) training. The left part of the table represents these proportions where BERT might use either the masking or unmasking token to replace a word in a sentence for input into the model's transformer layers. | Mentioned within the context are two specific pre-training tasks used for training BERT, which include Masked Language Model (MLM) and Next Sentence Prediction (NSP). However, as NSP is described to be without an explicit mention in our provided textual excerpt—inferred from "A bidirectional model which is trained using the 'masked LM'..." we do know that MLM was used. It seems there has been a slight mistake or omission; typically for BERT, both Masked Language Model and Next Sentence Prediction tasks are utilized together during pre-training to enhance understanding of context within bidirectionality—which is not explicitly stated in the provided text but commonly known from external sources. If only one task was used as per your question's format strictly based on this excerpt, then MLM would be that single mentioned and acknowledged method for BERT pre-training in this specific passage of context given. | The context provided above mentions that for its pre-training task, BERT uses "two unsupervised tasks," but it doesn't specify what these tasks are within the given text. However, later in Section 3.2 of the original paper on which this excerpt is based (Devlin et al., Vaswani et al., Radford), they define two specific pre-training objectives: Masked Language Modeling (MLM) and Next Sentence Prediction (NSP). Therefore, although not directly stated in the provided context above, BERT uses these two tasks for its pre-training based on standard practices of language model training. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| 15% of input tokens are masked in BERT's MLM objective. | 15% of all WordPiece tokens in each sequence at random are masked for BERT's Masked Language Modeling (MLM) pre-training. | 15% |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| REALM uses a salient span masking scheme that focuses on tokens such as "United Kingdom" or specific dates like “July 1969”. This method ensures the model learns to retrieve examples from documents containing world knowledge, which is crucial since REALM's core strength lies in its ability to use retriever-augmented language models for tasks that require external factual information. | REALM uses salient span masking for its text data input where certain terms that require world knowledge are highlighted. This approach ensures the model focuses on examples that specifically demand external information to make accurate predictions about the masked tokens, thus encouraging meaningful retrievals during pre-training and subsequent inference stages. | REALM uses salient span masking where specific spans requiring world knowledge are identified for masking (e.g., “United Kingdom” or “July 1969”). This method is chosen because it focuses the model on examples that require understanding beyond local context, thereby encouraging learning relevant to broader world knowledge during pre-training. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| 1. Self-attention allows the model to extrapolate to sequence lengths longer than those encountered during training, unlike recurrent layers which struggle with long sequences due to issues like vanishing gradients and difficulties in parallelization on modern hardware architectures such as GPUs or TPUs.  <br>2. In terms of computational complexity, self-attention is faster for the most common case where sequence length n is smaller than representation dimensionality d—this often occurs with sentence representations used in machine translations like word-piece and byte-pair encodings. Recurrent layers require O(n) sequential operations to connect any two positions while a self-attention layer requires constant time regardless of the input size, which makes it more efficient for longer sequences or when dealing with large batches during inference/testing on parallel computing devices.  <br>3. Self-attention could yield models that are easier to interpret since attention distributions can highlight what different parts of inputs contribute towards decisions made by a model—an aspect not as readily available in RNNs where sequential dependencies make it hard to pinpoint specific cause and effect relationships within the input data during backpropagation. | <br>Self-attention is preferred because it connects all positions with a constant number of sequential operations, which can be computationally more efficient than the O(n) requirements when dealing with long sequences. Additionally, self-attention allows for parallel processing across different parts of the input sequence without needing to process them one after another as in recurrent layers. Lastly, it is naturally suited for handling varying lengths and maintains information from all positions simultaneously, which can be beneficial for capturing complex dependencies within data like text sequences. | 1. Self-attention allows connections between all positions with a constant number of operations, which can be computationally efficient compared to the O(n) sequential operations required by recurrent layers when n is larger than d (where n is sequence length and d is representation dimensionality). This efficiency becomes evident particularly in tasks involving variable-length sequences like machine translation.<br><br>2. Self-attention models, such as those using sinusoidal encoding for position information instead of learned embeddings, can generalize to longer unseen sequences better because they do not rely on recurrence and thus avoid issues related to the fixed number of sequential steps in RNNs (recurrent bottlenecks).<br><br>3. The flexibility offered by self-attention mechanisms extends beyond computational efficiency; it also provides interpretability benefits as attention distributions can reveal which parts of an input sequence are most influential for a given output, offering insights into syntactic and semantic structure learning in sentences. |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| ConvS2S Ensemble achieved a BLEU score of 26.36 on the WMT 2014 English-to-French translation task. | The ConvS2S Ensemble achieved a BLEU score of 40.56 on the WMT 2014 English-to-French translation task, as listed in Table 3 under Results and Training Cost (FLOPs) for different models including Transformer ensembles. | ConvS2S Ensemble achieved a BLEU score of 40.46 on the WMT 2014 English-to-French translation task. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| To estimate the number of Floating Point Operations (FLOPs) used for training, we look at Table 2 under "BLEU Training Cost (FLOPs)" and find that the term associated with Transformer (big) is listed as '41.8'. However, this value does not represent FLOP count but rather BLEU score achieved by the model after its training on English-to-German translation tasks. Therefore, based on the information provided in the context, I cannot calculate or determine the exact number of floating point operations used to train the base Transformer model since that specific metric is not given explicitly for it and instead requires an estimate as described: "We estimate the number of floating point operations by multiplying the training time, ...and 5." Without this explicit information on the actual Floating Point Operations count or a direct way to calculate based solely on provided data like GPU capabilities over specific durations (which have been used for other models), it is not possible to provide an answer. The correct response would be that we cannot determine the FLOPs from the given context as there's insufficient information about the training time and the number of operations per second achievable by each GPU in use, which are essential metrics needed alongside with actual numbers on model configuration (layers, heads, etc.) for this estimate. | The context provided does not directly state the exact number of floating-point operations used to train the base Transformer model. However, it mentions that they estimate this by multiplying the training time, the number of GPUs (8), and an estimate of the sustained single-precision floating-point capacity per GPU for a P100 card which was not given in exact numbers but referenced from another work as 25 GFLOPS. Assuming that these details are accurate to our understanding based on external knowledge, one would need additional information or calculations using those mentioned parameters (training time and number of GPUs) alongside the sustained single-precision floating operations per second for a P100 card referenced from other literature not provided in this context. | To find the number of floating point operations required for training a machine learning model, we typically estimate by multiplying several factors that contribute to the computation load. From Table 2 and additional context provided about the big transformer models from Vaswani et al., it's mentioned they used an "estimate" based on GPU sustained capacity which is not explicitly given in numbers for base Transformer model training cost. However, there are hints regarding how this was calculated:<br><br>- Training time multiplied by number of GPUs and the single precision floating point unit estimate per second each GPU can handle continuously without overheating or requiring active cooling mechanisms like fans (not explicitly stated in your context).<br><br>Without explicit numerical values for these factors, I cannot provide a precise answer. If you could supply this information from Table 2 and surrounding text regarding the base Transformer model's computation estimate using typical methods employed by researchers or refer to similar models that would allow me to infer an estimated range of floating point operations used in training based on standard practices for GPU-accelerated machine learning tasks.<br><br>If you have a specific number from Table 2, please share it so I can assist further with the answer calculation! |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The question seems to be based on a misunderstanding of context or numbers provided in the original text, as no specific "GLUE" dataset scores are mentioned for any task named QQP. Instead, there's mention of BERT achieving an absolute accuracy improvement and MNLI score improvements over previous benchmarks. However, without explicit information regarding GLUE's scoring system or how to interpret these results with respect to the specific "GLUE" dataset as a whole for tasks like Quora Question Pairs (QQP), we cannot accurately report BERT-LARGE’s QQP score from this context. <br><br>The answer, therefore: The provided text does not contain information about the GLUE benchmark's specific scores achieved by models on the QQP task; thus such a figure could not be given based solely on these details. | The context does not provide specific scores for BERT-LARGE (BASE) or any other model variants like DistilBERT, RoBERTa, etc., with respect to QQP. It only mentions that BERT achieves a score LARGE of 80.5 on the official leaderboard. To find out about specific scores for BERT-LARGE, we would need additional information not present in this context or access to more recent benchmark results after updating my knowledge base beyond March 2021 cutoff date. | The context does not provide a specific score for the QQP task directly from the provided text, so I cannot say what exactly the exact score was. However, it is mentioned that "For each task, we selected the best fine-tuning learning rate (among 5e-5, 4e-5, 3e-5, and 2e-5) on the Dev set," which implies BERT achieved a high accuracy score for QQP by optimizing its hyperparameters. To find the exact number representing the best obtained fine-tuned result specifically for QQP from GLUE using BERT LARGE models (or any model size), we would need to refer to external sources, such as reports or leaderboards mentioned in Section 4 Experiments and Appendix A of the context. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The exact match (EM) scores are not provided in the context for individual components like Encoder or Retriever separately; however, it mentions that after ablating critical components of REALM and reporting end-to-end results as well as EM before any fine-tuning, there is a significant improvement. Specifically, by retrieving 5 documents instead of only 20, the system achieves its overall best performance on NaturalQuestions Open with an increase in accuracy from baseline ORQA scores when not resetting parameters to their initial states and feeding them into fine-tuning post REALM pre-training. The exact match score for such a retrieval situation isn't directly stated, thus the answer would be 'not provided.' | REALM achieves an Exact Match (EM) score of 38.2 on the test split of NaturalQuestions Open benchmark. | The context provided earlier mentions various scores for different systems, but it doesn't directly mention the specific exact match (EM) score that REALM achieves on the NaturalQuestions dataset. Instead, you can see results from other benchmarks and baselines like ORQA or BERT with their respective EM scores in relation to Open-Domain Question Answering Systems as outlined below:<br><br>330m BERT 31.8 - (No exact match score given)<br>110m BERT 31.6 - (No exact match score given, negative implication of performance loss)<br>110m MLM (-) - Insufficient information to determine EM score as it's not provided and the symbol "-" implies that there is no significant improvement over baseline or even a potential decrease in performance after fine-tuning. <br>330m REALM (46.8, 42.9 for different contexts) - These are scores achieved by REALM on some benchmark tests and seem to be the best among BERT models mentioned; however, they pertain to a separate dataset or test as denoted in their respective descriptions within parentheses.<br>330m ICT+BERT (36.4 30.1 for different contexts) - Scores achieved by this model on some benchmark tests where the first number represents EM and the second is presumably another metric like F1 score, which also shows REALM's competitive performance against BERT-based models; however, these do not directly relate to NaturalQuestions.<br>NaturalQuestions 39.2 - This appears to be a single system result for NQ from Roberts et al., with no specification of whether it was before or after applying REALM's pre-training technique but is the highest EM score in comparison within that specific section regarding Open-Domain QA benchmarks, implying superior performance among those listed.<br><br>Based on this information and without a direct mention of an exact match (EM) score for REALM specifically on NaturalQuestions from your original text snippet provided or invented results which are not to be considered in our context herein, we cannot accurately state the EM score that REALM achieves solely based upon NaturalQuestions-Open. |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| 44.5 EM on Natural Questions [52] | 44.5 EM | 48 EM points higher than BM25, outperforming it by more than double the margin as shown in Table 1 of their paper (Lewis et al., 2020). While exact figures for NaturalQuestions aren't provided within this context specifically about RAG-Sequence’s performance on NQ or other benchmarks like TriviaQA, and WebQuestions, we can infer from Table 1 that the scores are likely in a similar range since all these models aim to achieve high Exact Match (EM) scores across different datasets. |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The Transformer base model uses 8 attention heads with each having a dimension of d=64 after dividing by h (where h is also equal to 8). This results in an effective multi-headed attention mechanism within the single-layer encoder and decoder. | The Transformer base model uses a total of B = 6 attention heads with H=8 (where each head has d/H or 64 dimensions) in all tasks. The overall hidden size A is large, at about 1024-dimensional vectors for the transformer models mentioned as Base and Large. | The Transformer base model uses 8 parallel attention layers (heads) with each head having a dimensionality of d = 64 after dividing by h. The total number of parameters for the encoder is around 100 million, and since these are primarily due to self-attention mechanisms in transformers, this implies that one or several base models might share similar dimensions regarding their attention heads; however, without explicit context from Table 3 (which isn't provided here), I can only infer the specifics of BERT mentioned later.<br><br><br>As for a reference to an academic paper providing foundational knowledge on Transformers and multi-headed self-attention mechanisms: Vaswani et al.'s "Attention Is All You Need" (2017), is widely recognized as the seminal work introducing transformers. The original arXiv version of this paper can be accessed at https://arxiv.org/abs/1706.03760, and a more accessible Google Scholar link for citations in various works related to Transformers is provided here: https://scholar.google.com/citations?view_as_sources=1&q=Transformer%2C+multi-headed+self-attention |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The Transformer base model uses a feed-forward neural network with dimensions (1024, 4096). | The Transformer base model uses a feed-forward network with dimensions d_ff = 2048, which can be calculated from the formula \(d\_ff = d\_model \times 4\), where \(d\_model\) is typically set to 512 in larger models. | The dimension of the feed-forward network in the Transformer base model is 2048 for each layer's inner-layer, with an overall dimensionality d = 512. The output from this pointwise convolutional networks has its size rescaled by a factor sqrt(d). Hence it results to having dimensions of (model*sqrt)x and y in the final two dense layers before the softmax layer that outputs predicted next-token probabilities. |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The BERT-LARGE model has a hidden size (A) of 16 and uses 1024 self-attention heads. It also contains approximately 340 million parameters in total for the encoder, as stated with "BASE A=16, Total Parameters=340M." | BERT-LARGE has a hidden size (A) of 16,000 and uses 32 self-attention heads. The total parameters for this model are approximately 405 million due to its large scale architecture which includes more layers, larger hidden sizes per layer, and additional attention heads compared to the base BERT model. | The BERT LARGE model has a hidden size (A) of 16 and utilizes 8 attention heads, as denoted by the notation "BERT (L=24, H=1024, A=16)" within the provided context. The term 'H' refers to the number of self-attention heads in each Transformer block or layer ('L') of BERT LARGE. |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The square root of the inverse number of dimensions (sqrt(1/d)) as a scaling factor is applied to the dot products before applying the softmax function in Scaled Dot-Product Attention. This counteracts diminishing gradients for large values of 'k' when the product dimension grows larger, facilitating stable training dynamics. | √1/sqrt(dk) | sqrt(1/d) |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| REALM computes this probability by modeling it as a distribution p(z \| x), which is sampled during pre-training and fine-tuning. The specific calculation for how REALM derives the retrieval probabilities isn't directly provided in the context, but based on common practices of similar models like BERT, this probability likely reflects relevance scores that document z has with input x before any fine-tuning is applied to improve it further. | REALM computes this by using a Transformer model that takes as input an amalgamation of texts from documents it has retrieved based on query x and the original text. Specifically, REALM joins together parts of the title z (z) and body y (y) with [MASK] tokens embedded within the concatenated string representing these inputs to predict what word should fill each masked spot in the joined input sequence – essentially learning which documents are most helpful for answering a given query. The probability p(z \| x), or likelihood of retrieving document z based on input x, is implicitly learned as part of this process since it depends on how well these retrieved texts help predict y when conditioning on both original and retrieved inputs in the joined sequence that feeds into Transformer layers for cross-attention processing. | To calculate the likelihood of selecting a particular document \(z\) from the knowledge corpus \(Z\), based on an initial query or context provided by \(x\), REALM employs a learned probability distribution represented as p(z \| x). This is achieved through its pre-training objective, which includes parameters that are refined during both retrieval and prediction steps. <br><br>The process involves modeling the document selection step with an expectation over all possible documents \(Z\), yielding the marginalized likelihood of choosing any given document to retrieve as p(y \| x) = \(\sum_{z \in Z} P(y \| z, x)P(z\|x)\). This reflects REALM's approach to considering each potential retrieved document and its relevance in informing the prediction for the masked word \(y\), while simultaneously accounting for the inherent uncertainty of not having perfect prior knowledge about which documents are relevant. |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The context provided gives a detailed comparison between two systems, RAG and REALM. However, the specific performance metrics of these models on the NaturalQuestions-Open benchmark are not directly stated in the given text excerpts from different research papers or documents. To accurately answer this question about their comparative performance on that particular dataset would require additional information specifically mentioning results from experiments conducted with both systems on NaturalQuestions Open, which is absent within these contexts. Therefore, based on the provided texts alone, we do not have sufficient information to compare RAG and REALM' fairness scores directly for this specific task.<br> | The provided context does not contain specific comparison results between RAG and REALM models on the NaturalQuestions dataset for open questions. Therefore, it is impossible to provide an answer based solely on this text. To obtain accurate information about how these two systems perform relative to each other on that benchmark, one would need access to their actual experimental outcomes reported in a peer-reviewed publication or relevant research findings not included in the given context. | RAG achieves a score of 53 EM, while REALM scores only 47.6 EM on this task. Therefore, RAG outperforms REALM in the context of Natural Questions dataset for open-domain QA tasks based on these numbers provided by Lewis (2020) and Guu (2softly). |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| Bert-Base has 7 and Bert-Large has 5, so BERT-Base has 2 more attention heads than a baseline single-headed or non-Transformer based model. However, since we are comparing to the base Transformer mentioned in Vaswani et al.'s original paper which uses d = 64 / h and typically employs one head (when not explicitly mentioning multiple), BERT'sem attention heads could be considered as having substantially more complexity per computationally independent unit, but we can say it has at least two additional full-fledged multi-headed units over a single traditional Transformer. | 12 attention heads for BERT and an unspecified number less than or equal to that count (since it's not explicitly stated) for the base Transformer model. The exact difference cannot be determined from the given context without knowing the specific architecture of the reference "base" model in terms of attention heads before comparing with BERT-BASE, which has 12 such heads. | BERT has significantly larger numbers of self-attention heads (12) when applied to tasks like input representation, as well as in various other applications. While we do not directly compare it with a single head 'base' Transformer within the context given because BERT is an entirely different architecture from baseline transformers discussed earlier towards end of page 4 and later on into section "Experiments". However, since there are no specific numbers provided about base model in this particular text for direct comparison regarding attention heads with BERT-BASE we can't accurately determine the number difference. The context mentions that increasing self-attention capacity appears to aid performance but does not quantify it here explicitly when compared directly to a 'base Transformer'. To answer questions like these, one would typically refer back to specific details or numbers in earlier sections of such papers which are unfortunately missing from this provided text snippet. Therefore I cannot give an exact number for how many more attention heads BERT-BASE has over the base model within your context here without further information on what is considered 'base' size and structure by comparison standard used during experiments mentioned at the beginning or end of said paper, typically found in the introduction section discussing baseline models. |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| Both systems demonstrate strong performance on the Natural Questions dataset, but specific comparison scores are not directly provided in the context. To accurately determine how RAG-Sequence compares to REALM on WebQuestions specifically for this task, one would need additional data that is not present within the given text. It's suggested however that both models perform well and even though details about their performance differences or similarities are missing from the context provided, they seem competitive based on overall scores mentioned in relation to other benchmarks like TriviaQA and Natural Questions for different systems. | REALM achieved a score of **15** EM, while the context doesn't provide explicit results for RAG-Sequence. However, considering that in Table 4 REALM scored higher than MIPS (8) and BART Seq2Seq TriviaQA baseline (7), which is another retriever-augmented model, one might infer that if both were compared on WebQuestions as per the context provided, RAG-Sequence could potentially perform better or at least comparably to REALM. Yet since no direct comparison score for RAG-Sequence in this specific task has been mentioned, it's not possible to provide a concrete answer from the given text alone. | RAG-Sequence achieves a score of 61.7 EM, while the context does not provide explicit results for RAG-Sequence's performance on WebQuestions using REALM training methods or otherwise. Therefore, based solely on this specific comparison metric (WebQuestions), we do not have enough information to assess their relative performances as pertains to that dataset and task within the provided context. <br><br>--- |
