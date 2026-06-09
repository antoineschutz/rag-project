# fusion

**backend:** ollama · **model:** phi3

| Parameter | hybrid-rrf | hybrid-weighted |
|-----------|--------|--------|
| retriever | hybrid | hybrid |
| embed_model | all-MiniLM-L6-v2 | all-MiniLM-L6-v2 |
| fusion | rrf | weighted |
| alpha | 0.5 | 0.5 |
| rerank | False | False |
| top_k | 15 | 15 |
| no_rag | False | False |

---

## Q1 · Level 1

**Question:** Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?  
**Expected:** The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The selection of `all-MiniLM-L6-v2` as the default was primarily due to it providing a significant improvement in evaluation metrics without incurring prohibitive latency increases compared to using local, single-user pipelines. Despite having only four times fewer parameters and half the computation cost (with respect to floating point operations) of `bge-base-en-v1.5`, it achieved higher top-5 Embedding Mismatch rates in Perplexity on both Wikipedia and CC-News corpora, indicating superior encoding quality from an information retrieval perspective. The decision was also informed by the fact that this model offered faster loading times (0.3s) when using precomputed embeddings compared to `bge-base-en-v1.5`. | The decision to select `all-MiniLM-L6-v2` as the default was primarily due to a balance between quality and latency, along with resource availability constraints. While there was only a minor improvement in top-k retrieval accuracy (from 0.743 EM for all-MiniLM-L6-v2 to 0.761 EM for bge-base-en-v1.5), this came at the cost of significantly higher latency—a threefold increase when compared directly in a local, single-user pipeline setup (from around 18ms for all-MiniLM-L6-v2 to about 3x that amount for bge-base-en-v1.5). The decision was further influenced by hardware limitations; the `all-MiniLM-L6-v2` model only required a single machine with an available 12GB GPU, whereas running larger models like `bge-base-en-v1.5`, which had more parameters and hence presumably better performance in isolation or across multiple machines, would have been impractical given the setup constraints. Thus, despite not justifying a substantial quality gap for its latency increase on small scale tasks as per this context, `all-MiniLM-L6-v2` was chosen due to these considerations of efficiency and available resources within an embedded system's capacity limitations. |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The addition of explicit 'Source: {source}' before each passage in the retrieval context reduced hallucinations on the evaluation set from a rate of 11/47 (23%) down to just 3/47 (6%). This indicates that attributing source information significantly decreased model-generated fabrications. | The addition of 'Source: {source}' before each passage reduced hallucinations on the eval set from 11/47 (23%) to 3/47 (6%). |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The prompt indicates that at the current corpus size, which is approximately 4200 chunks or tokens, the speedup advantage of using FAISS with an IndexIVF becomes negligible. Therefore, it only becomes worthwhile above roughly 100,000 chunks (or when dealing with significantly larger data). | ~100,000 chunks or larger in context of ~4200 total chunks with a token max of 128. |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided suggests that the gap between BM25 and DPR is due to the nature of questions in different datasets. On NQ, where queries are longer and more paraphrastic with low lexical overlap with answers, dense retrieval methods like DPR perform significantly better as they can handle such complex search requirements effectively by considering broader document representations beyond simple word overlaps. In contrast, BM25 is a sparse baseline that relies heavily on exact keyword matches and falls short in these more abstract scenarios typical of NQ questions compared to the shorter, entity-centric queries found in TriviaQA datasets where lexical overlap between passages and answers plays a crucial role. | NaturalQuestions (NQ) contains longer and more paraphrastic questions where lexical overlap with the answer passage is low, whereas in TriviaQA, answers are often contained within a single sentence of length up to three sentences. Because BM25 relies on word overlap between queries and documents for ranking relevance (as seen from Table 6), it performs well when such overlaps exist but struggles with the longer texts that require understanding paraphrased questions, which is where dense retrievers like DPR excel by using a more sophbotheistic approach to identify relevant information. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| BART (Bottom-Up Approximately) large | BART (Bidirectional and Auto-Regressive Transformer) models are used by both the BERT (Bidirectional Encoder Representations from Transformers), which is fine-tuned for encoding queries, as well as RAG-Token. Additionally, when considering tasks like QA where a complete answer may be provided in one document and hence treated as sequence generation of length one, both the BERT query encoder and generators are used to treat this target class or sentence as p(y\|x) = 1 for that specific input x since it is always correct.<br><br>For RAG-Sequence specifically, during inference (test time), after retrieving top K documents using DPR (Dense Passage Retrieval), the BART model generates a distribution of next output tokens with respect to each document and then marginalizes this across all retrieved docs for normalization before selecting the arg max token. This is consistent whether RAG-Token or RAG-Sequence are being used, but their contexts differ slightly as mentioned above regarding sequence classification tasks versus generating complete answers from a single passage in natural language generation settings like QA. |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| 0.743 | The context provided indicates that the decision to select `all-MiniLM-L6-v2` was made because, despite its slightly lower top-5 Exact Match (EM) score compared to other models on a specific evaluation set covering NLP/LLM paper corpus (top leaderboard entries shown in Table 3), it did not justify the significant latency increase when considering local and single-user pipeline requirements. The exact EM scores for `all-MiniLM-L6-v2` are explicitly mentioned as "78.0" on its respective row, implying that this is a top result among other choices like BERT (Single), which has an even higher score of "81.9". Therefore, the answer to your question, based solely on the context provided and understanding Exact Match scores for `all-MiniLM-L6-v2` specifically in Table 3, is not directly stated regarding top-5 EM but instead provides information about its overall score compared to other systems. However, we can infer from this data that among all options listed (including BERT), the highest top-5 Exact Match score achieved by `all-MiniLM-L6-v2` should be less than or equal to "81.9", as it is not explicitly presented in a separate row for its 5-best match results and only provides an overall performance metric alongside other systems which include BERT (Single). Given the limited context, we cannot provide an exact top-5 Exact Match score from Table 3 directly but can confidently state that `all-MiniLM-L6-v2` performs competitively within this list. For precise figures regarding its top-5 EM performance specifically in a tabulated format, the provided context lacks such direct information for extraction as per your question's framing. |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The BM25 retriever combined with DPR has an estimated maximum of a hypothetical best possible performance for RAG pipeline design. However, in terms of actual results from similar systems mentioned in Table 2 (which isn't provided), the highest top-5 Exact Match score achieved by one system is not specified directly within this context snippet and thus cannot be determined accurately based on the information given here. | The document does not provide a specific number for the top-5 Exact Match (EM) score achieved by any particular embedding model in this context. It mentions various systems' performance on benchmarks with scores but doesn't tie these directly to top-k EM as requested in your question, making it impossible to answer based solely on the provided text. |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| IndexFlatIP has a query latency of 4 ms while IndexIVF, when using an nlist size of 32 and pre-trained with FAISS on Theta (θ), reduces the query latency to just 1 ms. | Query latency for `IndexFlatIP` and NumPy (which also presumably uses a similar indexing strategy as Flat) combined with FAISS to produce results, has an average response time within the range of milliseconds. Specifically, both IndexFlatIP and Faiss IVF variants exhibit query speeds around 4ms when using `all-MiniLM-L6-v2` for embeddings in our context (presuming similar performance). However, without specific numbers provided directly comparing only these two index types from the table data, this answer assumes that both have analogous latencies due to sharing underlying mechanisms with NumPy cosine indexing. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| In the context provided about retrieval-augmented generation models and their performance on various benchmarks including Natural Questions (NQ), Retrieval-Augmented Generation from Lewis et al. (2020) reports that RAG-Sequence achieves an NQ Exact Match score of 44.5. | 44.5 |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| According to the context provided, when comparing different numbers of passages retrieved per query before generation (top-k), increasing from 5 to 10 can provide a gain in Exact Match score on NQ for Dense Passage Retrieval systems. However, specific EM scores are not given for top-10 retrieval or directly stated as superiority over the best non-generative baseline which is claimed by RAG models. | Top-5 Exact Match (EM) for DPR on NQ is not explicitly mentioned in terms of individual scores within the provided context. However, it's indicated that there is a substantial performance difference between using different k values during retrieval before generation—with small top-k suggesting lower recall at this stage and larger k potentially improving EM by 1.7 points on NQ for DPR models (although not explicitly stated as achievement numbers). |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| In the provided context, it is stated that on the NLP/LLM paper corpus evaluation set for embedding model benchmarks, BERT achieved a high top-5 Exact Match score. While this information directly pertains to TriviaQA results within the same document where RAG models are discussed and evaluated primarily in relation to Natural Questions (NQ) data—within our provided text snippet on retriever ablation, it is indicated that "RAG-Sequence achieves the highest overall score, outperforming BM25 by 18 EM points on NQ." Since we are asked about TriviaQA and not Natural Questions specifically in this context, there's no explicit mention of a system achieving top scores for RAG models within the provided text snippet related to TriviaQA results. Therefore, based on my knowledge cutoff date without direct information from Table 1 or further details, I cannot provide an answer regarding which system achieved the highest EM score in this particular benchmark report (TriviaQA). The context does not contain enough specifics about the individual systems' performance solely within TriviaQA. | Our best performing single BERT model outperforms all other systems listed for TriviaQA, reaching an F1 score of 86.9 on that dataset according to Table 3 (despite no specific EM being mentioned in the given context). However, since RAG-Sequence has been specifically noted as achieving a higher overall score than BM25 by 18 EM points and leading ensembling system performance, it implies superiority across benchmarks. But without explicit TriviaQA Exact Match scores provided for systems like DPR or RAG models in the table excerpt given above (and assuming that our single-model setup was indeed evaluated on a separate set of results), we cannot definitively claim which system had the highest EM solely based on this information. The text does not provide an explicit TriviaQA Exact Match score for each model, so I must say "The answer is not in the context." |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| Final configuration settings used were:<br>```python<br>CHUNK_MAX_TOKENS = 128   # changed from the roadmap's initial 256 tokens after evaluation showed precision improvement.<br>CHUNK_OVERLAP    = 50    # chosen to maintain approximately a 39% overlap between chunks, as higher values did not improve recall beyond this point. | The final 'CHUNK_MAX_TOKENS' value is 128, while the 'CHUNK_OVERLAP' value stands at 50. These were empirically determined configurations during model fine-tuning for improved performance on specific tasks and corpus sizes. |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| 50% | 50% |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided does not explicitly state any differences between RAG-Token and RAG-Sequence models; it suggests that they are equivalent when considering the target class as a sequence of length one. However, this equivalence is only in terms of their approach to using both retrieval (DPR) and generation components (BART), with no inherent difference mentioned for other scenarios or benchmarks within the provided context. | The main difference lies in their decoding processes at test time, which requires different methods to approximate arg max p(y\|x). In essence, while both models function similarly during inference for a single target sequence (equivalent as RAG-Token), they are distinct when considering multiple tokens or longer sequences. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context discusses various aspects of using and improving the RAG (Retrieval-Augmented Generation) system's retrieval component but doesn't specify a particular named "retriever" that RAG uses. Instead, it mentions learning to retrieve relevant information for tasks as part of its functionality, comparing favorably with DPR’s retriever and highlighting improvements when compared against BM25 without indicating the use of an external specific system. It also discusses running ablations by freezing the retriever during training but doesn't mention using a particular named "retriever." | The DPR (Document Reader) as described in the context is used by the RAG model for its retrieval component p(z\|x). The document encoder from BERT provides dense embeddings of documents, and a query encoder based on BERT handles queries. Together with an exponential decay function, these components form DPR's bi-encoder architecture to retrieve relevant passages in response to the input text x for generating responses or answers y given by RAG models like RAG-Sequence. |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided above mentions that for its pre-training task, BERT uses "two unsupervised tasks," but it doesn't specify what these tasks are within the given text. However, later in Section 3.2 of the original paper on which this excerpt is based (Devlin et al., Vaswani et al., Radford), they define two specific pre-training objectives: Masked Language Modeling (MLM) and Next Sentence Prediction (NSP). Therefore, although not directly stated in the provided context above, BERT uses these two tasks for its pre-training based on standard practices of language model training. | The context provided mentions that during its pre-training phase, BERT utilizes two specific unsupervised learning tasks. These are not explicitly named in the text; however, it is indicated through an illustration (referred to as A.5) and experimental results within a table labeled "Table 5: Ablation over the pre-training tasks using the BERT architecture" that there were ablation studies performed on these two specific objectives when training with deep bidirectionality enabled by BiLSTM during fine-tuning. While not directly stated in this answer, based on common knowledge of how BERT was introduced and implemented following its original paper (Radford et al., 2018), we can infer that the two pre-training tasks are Masked Language Modeling (MLM) and Next Sentence Prediction (NSP). MLM involves predicting words in a sentence based on context, whereas NSP determines if one sentence logically follows another. This inference is made considering BERT's design to closely compare itself with GPT while also noticing the absence of explicit names for these tasks within this specific text extract provided. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| 15% | 15% |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| REALM uses salient span masking where specific spans requiring world knowledge are identified for masking (e.g., “United Kingdom” or “July 1969”). This method is chosen because it focuses the model on examples that require understanding beyond local context, thereby encouraging learning relevant to broader world knowledge during pre-training. | REALM uses salient span masking introduced by SpanBERT. This method is chosen to focus the model's attention on spans that require world knowledge for correct prediction, which helps in reducing mismatch between training with [MASK] tokens and fine-tuning without them. The purpose of this ablation study was to evaluate different strategies; however, span masking from SpanBERT shows a significant advantage when using REALM pre-training over random token or span masking introduced by BERT or SpanBERT respectively. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| 1. Self-attention allows connections between all positions with a constant number of operations, which can be computationally efficient compared to the O(n) sequential operations required by recurrent layers when n is larger than d (where n is sequence length and d is representation dimensionality). This efficiency becomes evident particularly in tasks involving variable-length sequences like machine translation.<br><br>2. Self-attention models, such as those using sinusoidal encoding for position information instead of learned embeddings, can generalize to longer unseen sequences better because they do not rely on recurrence and thus avoid issues related to the fixed number of sequential steps in RNNs (recurrent bottlenecks).<br><br>3. The flexibility offered by self-attention mechanisms extends beyond computational efficiency; it also provides interpretability benefits as attention distributions can reveal which parts of an input sequence are most influential for a given output, offering insights into syntactic and semantic structure learning in sentences. | 1. Self-attention allows the model to generalize well and learn dependencies between arbitrarily spaced positions in a sequence, which is beneficial when dealing with long sequences common in machine translation tasks (e.g., WMT datasets). This contrasts recurrent layers that have difficulty learning these dependencies due to their sequential nature requiring more operations as the path length increases.<br><br>2. Self-attention can learn short paths of a constant number of operations, which reduces computational complexity and makes it faster when sequence lengths are smaller than representation dimensionality – an advantage especially relevant in sentence representations for machine translation tasks where this condition often holds true (e.g., wordpiece and byte pair encodings).<br><br>3. Self-attention provides better path length connectivity, making the learning of long-range dependencies easier as opposed to recurrent layers that require O(n) operations along a single sequence direction for every position – resulting in shorter paths on average between any two positions compared with recursive approaches like RNNs or LSTM networks. |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| ConvS2S Ensemble achieved a BLEU score of 40.46 on the WMT 2014 English-to-French translation task. | The context provided does not contain specific information about the BLEU score achieved by ConvS2S Ensemble on the WMT 2014 English-to-French task. It only lists various models and their respective scores without specifying which ones are used for that particular language pair or translation direction within this dataset. To answer accurately, one would need to refer directly to results from a study or experiment specifically addressing ConvS2S Ensemble's performance on the WMT 2014 English-to-French task. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| To find the number of floating point operations required for training a machine learning model, we typically estimate by multiplying several factors that contribute to the computation load. From Table 2 and additional context provided about the big transformer models from Vaswani et al., it's mentioned they used an "estimate" based on GPU sustained capacity which is not explicitly given in numbers for base Transformer model training cost. However, there are hints regarding how this was calculated:<br><br>- Training time multiplied by number of GPUs and the single precision floating point unit estimate per second each GPU can handle continuously without overheating or requiring active cooling mechanisms like fans (not explicitly stated in your context).<br><br>Without explicit numerical values for these factors, I cannot provide a precise answer. If you could supply this information from Table 2 and surrounding text regarding the base Transformer model's computation estimate using typical methods employed by researchers or refer to similar models that would allow me to infer an estimated range of floating point operations used in training based on standard practices for GPU-accelerated machine learning tasks.<br><br>If you have a specific number from Table 2, please share it so I can assist further with the answer calculation! | The provided context does not directly state the number of floating-point operations (FLOPs) used for training the base Transformer model, instead it provides information on BLEU scores and other parameters. Therefore, I cannot provide this specific detail from the given text without making assumptions or having access to additional data outside the context provided. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context does not provide a specific score for the QQP task directly from the provided text, so I cannot say what exactly the exact score was. However, it is mentioned that "For each task, we selected the best fine-tuning learning rate (among 5e-5, 4e-5, 3e-5, and 2e-5) on the Dev set," which implies BERT achieved a high accuracy score for QQP by optimizing its hyperparameters. To find the exact number representing the best obtained fine-tuned result specifically for QQP from GLUE using BERT LARGE models (or any model size), we would need to refer to external sources, such as reports or leaderboards mentioned in Section 4 Experiments and Appendix A of the context. | The context does not provide a specific QQP score for BERT-LARGE directly from Table 1 or any other table within the provided text. It is mentioned that there are F1 scores reported for tasks like QQP, but no numerical values were given in this particular excerpt to answer your question accurately. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided earlier mentions various scores for different systems, but it doesn't directly mention the specific exact match (EM) score that REALM achieves on the NaturalQuestions dataset. Instead, you can see results from other benchmarks and baselines like ORQA or BERT with their respective EM scores in relation to Open-Domain Question Answering Systems as outlined below:<br><br>330m BERT 31.8 - (No exact match score given)<br>110m BERT 31.6 - (No exact match score given, negative implication of performance loss)<br>110m MLM (-) - Insufficient information to determine EM score as it's not provided and the symbol "-" implies that there is no significant improvement over baseline or even a potential decrease in performance after fine-tuning. <br>330m REALM (46.8, 42.9 for different contexts) - These are scores achieved by REALM on some benchmark tests and seem to be the best among BERT models mentioned; however, they pertain to a separate dataset or test as denoted in their respective descriptions within parentheses.<br>330m ICT+BERT (36.4 30.1 for different contexts) - Scores achieved by this model on some benchmark tests where the first number represents EM and the second is presumably another metric like F1 score, which also shows REALM's competitive performance against BERT-based models; however, these do not directly relate to NaturalQuestions.<br>NaturalQuestions 39.2 - This appears to be a single system result for NQ from Roberts et al., with no specification of whether it was before or after applying REALM's pre-training technique but is the highest EM score in comparison within that specific section regarding Open-Domain QA benchmarks, implying superior performance among those listed.<br><br>Based on this information and without a direct mention of an exact match (EM) score for REALM specifically on NaturalQuestions from your original text snippet provided or invented results which are not to be considered in our context herein, we cannot accurately state the EM score that REALM achieves solely based upon NaturalQuestions-Open. | 38.5 |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| 48 EM points higher than BM25, outperforming it by more than double the margin as shown in Table 1 of their paper (Lewis et al., 2020). While exact figures for NaturalQuestions aren't provided within this context specifically about RAG-Sequence’s performance on NQ or other benchmarks like TriviaQA, and WebQuestions, we can infer from Table 1 that the scores are likely in a similar range since all these models aim to achieve high Exact Match (EM) scores across different datasets. | 44.5 EM (Exact Match) on NaturalQuestions according to the context provided by Lee et al., not Lewis et al. as it seems like a mix-up with the citation years and paper authors, which can be common in extensive literature reviews due to multiple works being conducted around similar timeframes or related topics that might lead to confusion when citing sources. |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The Transformer base model uses 8 parallel attention layers (heads) with each head having a dimensionality of d = 64 after dividing by h. The total number of parameters for the encoder is around 100 million, and since these are primarily due to self-attention mechanisms in transformers, this implies that one or several base models might share similar dimensions regarding their attention heads; however, without explicit context from Table 3 (which isn't provided here), I can only infer the specifics of BERT mentioned later.<br><br><br>As for a reference to an academic paper providing foundational knowledge on Transformers and multi-headed self-attention mechanisms: Vaswani et al.'s "Attention Is All You Need" (2017), is widely recognized as the seminal work introducing transformers. The original arXiv version of this paper can be accessed at https://arxiv.org/abs/1706.03760, and a more accessible Google Scholar link for citations in various works related to Transformers is provided here: https://scholar.google.com/citations?view_as_sources=1&q=Transformer%2C+multi-headed+self-attention | The Transformer base model uses 8 parallel attention layers, or heads, with each head having a reduced dimension of d = d /h = 64. The total number of parameters for this encoder is about 100 million (k v model). |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The dimension of the feed-forward network in the Transformer base model is 2048 for each layer's inner-layer, with an overall dimensionality d = 512. The output from this pointwise convolutional networks has its size rescaled by a factor sqrt(d). Hence it results to having dimensions of (model*sqrt)x and y in the final two dense layers before the softmax layer that outputs predicted next-token probabilities. | The dimensions for the feed-forward networks in the Transformer base model are both 4096 as indicated by 'd=d' and 'kf = kf'. These represent two separate components within each sublayer of the Transformer, wherein one component has a dimension equal to half the hidden size (i.02 * A) which is 1024 in this case for base model parameters when using dropout with P=0.1 and label smoothing epsilon = 0.1 as given by 'd' and 'kf'. The notation seems inconsistent here, but based on the provided dimensions (64), it appears that they refer to the hidden size divided by four for some components within each sublayer of a Transformer block which would be consistent with typical transformer configurations where such scaling happens. However, without additional context explaining what 'd' and 'kf' specifically represent in this equation, we can only assume standard practices or conventions used elsewhere to interpret the notation as half-hidden size for one part (which is common) leading us to conclude that 2048 was likely intended before dropout. |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The BERT LARGE model has a hidden size (A) of 16 and utilizes 8 attention heads, as denoted by the notation "BERT (L=24, H=1024, A=16)" within the provided context. The term 'H' refers to the number of self-attention heads in each Transformer block or layer ('L') of BERT LARGE. | The Hidden Size (A) for BERT LARGE is 16, and it has a total of 32 Attention Heads. However, this seems to be an inconsistency in the provided context as later on it states that BERT Large should have 1024 hidden units but only 32 attention heads according to another source (OpenAI paper). |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| sqrt(1/d) | The context mentions that a scaling factor of is applied to the dot products, implying there's an intended square root operation due to '√1'. However, since any real number raised to the power of zero equals one and taking this into account for practical implementation where such explicit mention might be considered redundant or potentially misleading in context (as typically no scaling other than 1 would apply directly before a softmax), we can infer that the intended consistent scale factor prior to applying the softmax function is actually '1'. This maintains equal weighting without any additional amplification or diminishment, which seems reasonable as it does not require further information beyond what's provided. |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| To calculate the likelihood of selecting a particular document \(z\) from the knowledge corpus \(Z\), based on an initial query or context provided by \(x\), REALM employs a learned probability distribution represented as p(z \| x). This is achieved through its pre-training objective, which includes parameters that are refined during both retrieval and prediction steps. <br><br>The process involves modeling the document selection step with an expectation over all possible documents \(Z\), yielding the marginalized likelihood of choosing any given document to retrieve as p(y \| x) = \(\sum_{z \in Z} P(y \| z, x)P(z\|x)\). This reflects REALM's approach to considering each potential retrieved document and its relevance in informing the prediction for the masked word \(y\), while simultaneously accounting for the inherent uncertainty of not having perfect prior knowledge about which documents are relevant. | REALM computes the probability p(z \| x) as a sample from the distribution, which is represented in mathematical terms within the context. The exact formulation provided indicates that this computation involves modeling it similarly to how one would learn embeddings for input and output tokens (Embed), but since no specific formula was given apart from an indication of retrieving documents based on their probability relative to Embed, we can't provide a precise mathematical operation used by REALM. It is reasonable to infer that the computation involves similarity measures between x and z within some embedding space defined for this task. |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| RAG achieves a score of 53 EM, while REALM scores only 47.6 EM on this task. Therefore, RAG outperforms REALM in the context of Natural Questions dataset for open-domain QA tasks based on these numbers provided by Lewis (2020) and Guu (2softly). | The question seems to be asking for a comparison between two different systems, presumably used in natural language processing tasks related to open-domain QA. However, the context provided does not contain specific comparative data or results about RAG (Lewis 2nerd_16384) and REALM (Guu 2020) on NaturalQuestions Open as they pertain specifically to that benchmark dataset within the text given. Therefore, I do not have sufficient information from this context alone to answer how these two models compare in terms of their performance on NaturalQuestions-Open.<br><br>That being said, based on other parts of the provided article (not included here), if one looks into external sources such as publication papers by Guu and Lewis or additional benchmarks data related specifically to RAG and REALM systems' performances, that information should contain a comparative analysis between these two models. |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| BERT has significantly larger numbers of self-attention heads (12) when applied to tasks like input representation, as well as in various other applications. While we do not directly compare it with a single head 'base' Transformer within the context given because BERT is an entirely different architecture from baseline transformers discussed earlier towards end of page 4 and later on into section "Experiments". However, since there are no specific numbers provided about base model in this particular text for direct comparison regarding attention heads with BERT-BASE we can't accurately determine the number difference. The context mentions that increasing self-attention capacity appears to aid performance but does not quantify it here explicitly when compared directly to a 'base Transformer'. To answer questions like these, one would typically refer back to specific details or numbers in earlier sections of such papers which are unfortunately missing from this provided text snippet. Therefore I cannot give an exact number for how many more attention heads BERT-BASE has over the base model within your context here without further information on what is considered 'base' size and structure by comparison standard used during experiments mentioned at the beginning or end of said paper, typically found in the introduction section discussing baseline models. | Bert-BASE has 12 layers of transformer, each with 12 multi-head self-attention layers, for a total of 144 head. In comparison, BERT's encoder uses d=64 heads per layer and it is not clear from the provided context how many such models are being discussed as base sizes can vary (with Base having fewer or more). Assuming we refer to Bert-BASE with its standard configuration:<br><br>Given that each transformer block in BERT has 12 self-attention layers, for a total of 144 attention heads when using d=64. Without specific details on the number of head(s) used by the 'base' Transformer model referred to at the beginning ("with 100M parameters"), it is impossible to provide an absolute difference in the count between BERT-BASE and this unspecified base without additional information from either context or prior knowledge about typical models. However, if we assume that "base" refers to a smaller multi-head attention version of Bert (which typically has fewer heads per layer), then there would be less than 144 head in total for BERT's encoder compared to the hypothetical base model—though an exact number cannot be provided. If specific details were given about the architecture and parameters count of this 'base' Transformer, a direct comparison could be made accordingly by calculating how many heads correspond to a 100M parameter set in Bert-BASE using d=64 head size or whichever equivalent model is being compared with BERT. |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| RAG-Sequence achieves a score of 61.7 EM, while the context does not provide explicit results for RAG-Sequence's performance on WebQuestions using REALM training methods or otherwise. Therefore, based solely on this specific comparison metric (WebQuestions), we do not have enough information to assess their relative performances as pertains to that dataset and task within the provided context. <br><br>--- | REALM outperforms the BERT baseline and achieves a score of 64.7 EM, which is higher than RAG-Sequence's performance as noted in other benchmark results where REALM performed strongly across various datasets including WebQuestions (Roberts et al., 2020). |
