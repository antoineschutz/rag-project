# reranking

**backend:** ollama · **model:** phi3

| Parameter | no rerank | rerank |
|-----------|--------|--------|
| retriever | dense | dense |
| embed_model | all-MiniLM-L6-v2 | all-MiniLM-L6-v2 |
| rerank | False | True |
| top_k | 15 | 15 |
| no_rag | False | False |

---

## Q1 · Level 1

**Question:** Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?  
**Expected:** The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| The decision to choose `all-MiniLM-L6-v2` as the default was based on a balance between performance and efficiency for local, single-user pipelines where latency is critical. Although there were only minor quality gains of about 0.35%, choosing this model meant accepting these in exchange to avoid significant increases in latency — specifically from around 18ms with `all-MiniLM-L6-v2` down to roughly half that at approximately 9ms when compared to the more resource-intensive but slightly better performing option, which had about a .05 quality gap.<br><br> | The decision to select `all-MiniLM-L6-v2` (denoted in the context with an all-caps name) was based on a tradeoff between latency and quality of translations for single user local pipelines. Despite having similar performance metrics, it offered slightly better translation accuracy while maintaining lower average latency—only 18 milliseconds compared to `bge-base-en-v1.5`, which had an increased average latency by about three times (around 57 ms as per the context). Therefore, because a significant quality gap of only around 0.4 points did not justify this increase in latency for local use cases where speed is essential, `all-MiniLM-L6-v2` was chosen as the default model configuration. |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| Adding explicit source attribution reduced hallucinations from 23% on the eval set to 6%. | Adding 'Source: {source}' before each passage reduced hallucinations from 11 out of 47 (23%) on the eval set for BART, and there is no comparative data provided in the context to quantify this reduction specifically for RAG models. However, it's noted that adding source attribution helped reduce hallucinations with an effect observed when training RoBERTa-based classifiers by 2.7%. |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| FAISS IVF becomes worthwhile over IndexFlatIP when the number of chunks exceeds approximately 100,000. Below this threshold, other factors such as a smaller corpus size or less complex queries may not justify the transition to FAISS with an Inverse Document Frequency (IVF) index despite its potential for faster query speeds. | Over ~100,000 chunks of contextual embeddings produced by REALM-BERT. |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| no rerank | rerank |
|---|---|
| The gap between BM25's performance and that of dense retrieval systems like DPR (Dense Passage Retrieval) can be attributed to the nature of questions posed in each dataset. NaturalQuestions consists mainly of longer, more paraphrastic queries where lexical overlap with potential answer passages is often low. This makes it difficult for BM25, which relies on word overlaps between query and passage terms, hence falling significantly behind DPR that uses a bi-encoder trained specifically on the NQ dataset to better understand contextual relevance regardless of direct lexical overlap. | The context provided suggests that the performance discrepancy between BM25 and DPR across different datasets can be attributed to the nature of questions in each dataset. NQ's longer, more paraphrastic questions with low lexical overlap make dense retrieval methods like DPR advantageous as they rely on capturing broader contextual information rather than direct keyword matches that BM25 focuses on. The nuanced and diverse linguistic expressions present in TriviaQA's question format may better align with the capabilities of sparse lexical baselines like BM25, explaining its relative performance strength there compared to DPR. Additionally, dense retrieval systems tend to require more comprehensive training data that captures a wider variety of answer phrasings and contextual subtleties, which might not be as thoroughly represented in the NQ dataset for this specific comparison within the provided text. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| no rerank | rerank |
|---|---|
| BART-large | BART (Bidirectional and Auto-regressive Transformer) models are used as generators in both RAG-Token and RAG-Sequence. The BART large pretrained model serves as the basis for generating responses, which is then fine-tuned with specific tasks using a top-k truncated approach to generate text based on context provided by input sequences and retrieved documents when necessary.<br><br> |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| 0.743 | The all-MiniLM-L6-v2 model achieves a top-5 exact match (EM) score of 0.743 on the test set for SQuAD v2.0 as indicated in Table 1 within the provided context. This information is directly extracted from the given data, which states "all-MiniLM-L6-v2 \| Top-5 EM: 0.743" followed by a reference to table number and score format (Exact Match scores on the test split of each benchmark). There's no need for further research as the answer is clearly provided in this context. |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| BERT (Single) - Top Leaderboard System with Highest Score of F1 = 87.3% | The Transformer achieves better BLEU scores than previous state-of-the-art models on English to German and English to French newstest2014 tests at a fraction of the training cost. However, there's no specific top score mentioned in EM for any particular embedding model within this context. The exact numbers provided (e.g., 68.2 vs 68.0 on TriviaQA) are from RAG models and not an individual embedded model like Transformer or BERT as stated elsewhere, but given the available information, it is unclear which specific embedding technique within those systems leads to this score without further details being provided in another part of context that has been cut off. |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| The query latency for `IndexFlatIP` and `IndexIVF (nlist=32)` are both recorded at 4 milliseconds. However, it's important to note that while the IVF index has a slightly lower top-5 EM score of 0.736 compared to IndexFlatIP’s 0.743, and is built in about half the time (1.1 seconds for `IndexIVF` vs 0.8 seconds), it provides an additional speed advantage during querying as per the context provided above:<br><br>"FAISS \| IndexIVF ... Query latency (ms) \| --------------\|-------------------\|<br>\| FAISS \| IndexFlatIP     \|   0.743      \|       0.8         \| 4            \|<br>\| FAISS \| IndexIVF (nlist=32)\|  0.736    \|      1.1          \| --------------\|" | IndexFlatIP has a query latency of 4 ms, while IndexIVF (nlist=32) has a query latency of just 1 ms. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| no rerank | rerank |
|---|---|
| RAG-Sequence achieves a score of 41.5 EM on Natural Questions (NQ) according to Table 2 mentioned in the context. However, it's important to note that this information is provided as part of an invented benchmark report and not actual experimental results from research papers or studies conducted by Lewis et al. | In the context provided above regarding RAG and QA systems' performance on different datasets (NQ, TriviaQA, WQ, CT), it is stated that "RAG-Sequence reaches identical NQ Exact Match scores of 44.5." Therefore, the answer to your question is:<br><br>**Answer: A score of 44.5 EM on Natural Questions (NQ) benchmark was achieved by RAG-Sequence models as per Table I in the document provided above. However, it's important to note that this figure seems misplaced within an incorrect context since "EM" typically stands for Exact Match and not mentioned earlier in relation with NQ scores specifically. Nonetheless, assuming EM is indeed what was intended by 'EM on Natural Questions (NQ)', the score achieved would be 44.5 based solely on this excerpt's information.** |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| no rerank | rerank |
|---|---|
| For NaturalQuestions (NQ), when using the Document Passage Retrieval (DPR) system, achieving a score of 44.5 Exact Match (EM) by considering only the top-5 retrieved documents shows RAG's ability to retrieve relevant information efficiently for this task. When expanding to consider just the top-10 retrievals before applying any fine-tuning, we find that DPR achieves a higher NQ EM score of 48%, demonstrating an improvement in results when more potential documents are considered during pre-training and not only relying on the most relevant document. | DPR achieves an exact match of 69% on NaturalQuestions (NQ) when using the top-5 retrieval, and a slightly lower score of around 47% for the top-10 retrieval. It's important to note that these results are specific to DPR with its BERT encoders used as query and document representations; they do not directly apply to RAG models which may have different performance characteristics due to their distinct architecture, especially in terms of using a pretrained large language model for generation after retrieval. Additionally, since the numbers were invented for this synthetic benchmark scenario, these specific percentages are hypothetical and would require actual experimentation with real data to verify. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| no rerank | rerank |
|---|---|
| The QANet ensemble model achieved the highest TriviaQA Exact Match (EM) score, which was not explicitly stated but can be inferred to have outperformed other systems mentioned for this specific task. Since no numerical EM value is provided in the context for individual models or ensembles on TriviaQA, we refer back to the benchmark test results section where it lists human performance at 82.3 EM and mentions several model performances without directly stating which has the highest score:<br>- Ensemble (NLNet) - 86.0 EM<br>- Published BiDAF+ELMo Single System - not provided in numerical form but implied to have better results than BM25 since it's compared favorably with DPR on NQ, which suggests good performance across benchmarks and by the naming convention (Single) implies a less complex system.<br>- RAG Token Model/RAG Sequence System - 68.0 EM for TriviaQA specifically is mentioned but does not specify if this outperforms Ensemble's score of 86.0. Human performance, however, tops at 91.2 EM on the same platform.<br>- BERT Single Model and RAG Sequence System - no explicit scores given for these models with respect to TriviaQA in the text provided.<br><br>Given that ensembles generally tend to perform better than single systems due to their combined strengths, it is reasonable to assume that the QANet ensemble model achieved a high EM score on TriviaQA; however, without specific numbers or comparisons stating "highest," we can't definitively say which system had the highest. Human performance would typically be considered as the gold standard but was not part of this retriever ablation study since humans are excluded from comparison with systems in Table 2 (the provided context). | RAG-Sequence model achieved the highest Exact Match (EM) score for TriviaQA, as per Table 3 of the provided text. The exact value given is an F1 of 68.2 and EM was not directly reported but can be inferred to match this high F1 due to its strong performance in ensemble systems which are generally expected to perform well across various metrics including Exact Match (EM). |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| The final `CHUNK_MAX_TOKENS` value is 128, while the `CHUNK_OVERLAP` value is set to 50. These values were determined empirically as part of optimizing the chunking strategy for better precision in retrieving relevant tokens from a text corpus using FAISS indexing and embeddings with Tiktoken accumulation approach. | Final configuration parameters as per the context provided:<br>- CHUNK_MAX_TOKENS = 128 tokens.<br>- CHUNK_OVERLAP = 50 tokens. |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| 15% | The provided context mentions a "uniform masking rate of 15%" for LM masking applied after WordPiece tokenization during training with BERT. This indicates that there is no specific mention or information about any particular percentage overlap between tokens used in the chunking configuration within this text, except implied by character split methods and sentence splits which deal directly with word boundaries but are not quantified in terms of percentages for overlap herein. Therefore, based on the given context alone:<br><br>The token overlap percentage is 0% because there's no special consideration mentioned that would result in a non-zero overlap between tokens when WordPiece tokenization and subsequent LM masking are applied as described. |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| no rerank | rerank |
|---|---|
| The primary distinction lies in their approach to handling retrieved documents. In RAG-Token, a different latent document can be drawn for each token of the target sequence allowing content from various documents when producing an answer during generation process; whereas, in RAG-Sequence model uses same retrieved document throughout and marginalizes over it using top-K approximation to generate the complete sequence. Thus both models differ in their treatment and integration of external knowledge into text completion tasks. | The main difference lies in their decoding process at test time for sequence generation tasks, like Jeopardy question generation. The RAG-Token model can draw a different latent document (representing retrieved information) to generate each target token and then marginalize the probabilities accordingly from top K documents using BERT as an encoder. On the other hand, in the RAG-Sequence model, all generated tokens share one common set of learned retriever embeddings which are used to approximate a seq2seq probability distribution for generating complete sequences with autoregressive decoding at test time - this involves considering both document content and previously predicted output. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| no rerank | rerank |
|---|---|
| The RAG model uses DPR (Dense Passage Retrieval) as its retriever, which is based on a bi-encoder architecture using BERT for document and query encoding. The specific implementation of DPR mentioned in the context initializes with Document Re-Ranking from KVR-Reader [25]. | DPR (Dense Passage Retrieval) |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| no rerank | rerank |
|---|---|
| The context provided does not specify which two particular pre-training tasks BERT uses as it only mentions that during its training phase for unlabeled data over different pre-training tasks, the model learns representations such as A/B and sentence embeddings. These may be components of various combinations of pre-training objectives used in practice but without a specific reference to two defined distinct ones within this text, it is not possible to determine which exactly they are from the context given alone. | BERT uses a masked language model (MLM) task, where some percentage of the tokens in each sequence are randomly masked and then predicted by the model during training. In addition to this MLM objective, BERT also employs Next Sentence Prediction (NSP), which is an auxiliary pre-training task that aims at learning the relationship between pairs of sentences. During NSP fine-tuning, given two pieces of text as input, the model predicts whether the second sentence is the subsequent sentence in the original document or not. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| no rerank | rerank |
|---|---|
| 15% | 15% |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| no rerank | rerank |
|---|---|
| REALM uses salient span masking for its pre-training. This strategy is used to focus on examples that require world knowledge because it targets specific tokens within the text such as "United Kingdom" or "July 1969." These are considered salient spans, which by their nature would benefit from retrieving relevant documents containing this information during training since they pose problems requiring external context for accurate prediction of masked words. | REALM uses salient span masking for the language model (MLM) task. This technique focuses on injecting inductive biases to guide the model towards retrieving relevant world knowledge when needed while predicting missing tokens in input sentences, which are critical to understanding queries that require such external information. Unlike BERT's random token or SpanBERT’s span masking—which may not sufficiently direct models toward needing external documents for solving specific types of questions—REALM explicitly uses contextually salient spans like "United Kingdom" and "July 1969", which likely require additional knowledge to predict, thus aiding in more targeted world knowledge retrieval. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| 1. Self-attention allows the model to learn dependencies without regard to their distance in the input sequence, which can capture long-range interactions more effectively than RNNs that process data sequentially from left to right or vice versa. This is because self-attention mechanisms compute a representation of each position by attending over all positions simultaneously within a single attention layer.<br><br>2. Self-attention layers have constant computational complexity regardless of the sequence length, making them more parallelizable and thus faster for training on modern GPUs compared to RNNs that increase their sequential computation time with longer input sequences (O(n) operations). This advantage becomes significant in cases where d < n as it's most often encountered.<br><br>3. Self-attention mechanisms have been shown empirically, especially within the Transformer model context by Vaswani et al., to yield more interpretable models due to attention distributions that can clearly indicate which parts of the input sequence influence each output position and how syntactic and semantic structure are learned in representation learning tasks. | The authors of the study highlighted several advantages, which include quicker training speed compared to architectures based on recurrent or convolutional layers; enhanced interpretability from more transparently structured attention distributions that can reveal how different heads learn diverse tasks and even show dependencies related to syntactic and semantic structures in sentences. Furthermore, self-attention mechanisms allow each position within the sequence (like a token of words) to attend over all positions directly above or below it without being constrained by sequential processing limitations as seen with RNNs' O(n) complexity on long sequences; this capability is crucial for capturing longer range dependencies effectively. |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| The document does not provide specific information about the BLEU score achieved by ConvS2S Ensemble on WMT 2014 English-to-French. The text only mentions that our best Transformer model outperformed all previously reported single models, at a fraction of their training cost without specifying scores for ensembles or other architectures like ConvS2S. | The Transformer (big) model achieved a new state-of-the-art BLEU score of 41.8 on the WMT 2014 English-to-French translation task after training for 3.5 days using eight P100 GPUs, as stated in "System Dev Test EM F1 EM F1 Top Leaderboard Systems (Dec 10th, 2suit) Human - - 82.3 91.2 #1 Ensemble - nlnet - - 86.0 91.7 #2 Ensemble - QANet - - 85.6 - 85.8 R.M." However, this context does not explicitly mention a score for ConvS2S Ensemble on the WMT English-to-French task; therefore, based solely on this text, we do not have information regarding its performance specific to that metric and language direction combination. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| To calculate the training cost in floating-point operations (FLOPs) for a given model, we would typically multiply three factors together as mentioned in the context provided. However, since specific details such as single-precision FLOP calculations per operation or sustained GPU capacity are not explicitly stated within this particular extraction of text from your document other than an estimate reference [5], I can't calculate it directly without additional data. To provide a precise answer with the information given here would be speculative at best, and potentially inaccurate if we don’t rely on appropriate benchmarks or estimates for GPU FLOP computations during training of Transformer models. | To estimate the number of floating-point operations used to train a model, we would need more specific information regarding which GPUs were used and their respective sustained single-precision floating-point capacity. Since this detail is not provided directly in the context given above, I cannot provide an exact figure based solely on that text. However, if you're looking for general guidance on how to calculate such operations using typical parameters (time taken for training steps and number of GPUs), it can be estimated as follows:<br><br>1. Determine or estimate the sustained single-precision floating-point capacity per second of a P100 GPU, which is roughly 2 GFLOPS/GPU according to various sources (for more accurate estimations specific hardware spec sheets would need to reference). As we do not have this figure here and assuming for illustration purposes it's around that value.<br><br>2. Calculate the total number of seconds taken in training, which is 100,000 steps * step time (here assumed as 0.4 seconds per step = 40,000 seconds).<br><br>3. Multiply this by the single-precision floating point capacity for each GPU and then multiply that number by the total GFLOPS/GPU to get an estimate of operations performed during training (not accounting dropout or model size intricacies): 8 P100s * sustained FP32 throughput per GPU.<br><br>With specific numbers from reliable sources, we could provide a precise answer; however, given the provided context, this is not possible without assumptions. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| no rerank | rerank |
|---|---|
| The provided context does not explicitly mention a QQP score for BERT-LARGE obtained from the GLUE benchmark. However, it states that "on official leaderboard10, GLUE BERT obtains a score LARGE of 80.5." Since this is likely referring to BERT's performance on the task within the larger context of all tasks in GLUE (not specifically QQP), and given that scores are not differentiated by specific tasks beyond stating an overall "LARGE" classification, it is impossible to accurately determine the exact score for just the QQP.<br><br>To obtain this figure if available elsewhere or from a leaderboard archive directly would be necessary as of my last knowledge update in April 2023. | Based on Table 3 provided in the context, the LARGE model of BERT achieves an accuracy score (for question answering) of 91.8% on the QQP task within the GLUE benchmark. The exact figure is not given for this particular metric since it's traditionally measured with F1 scores rather than raw accuracies, but based on context clues and similar results in other tasks like SQuAD v2.0 (which shows a high score of 93.2%), we can infer that BERT-LARGE would achieve an accuracy close to this benchmark for the QQP task as well, provided it follows the trend shown by its performance on similar natural language understanding tasks within GLUE. However, without explicit data in Table 3 regarding a raw score specifically for question answering (as opposed to F1), we cannot directly confirm that figure but can anticipate competitive results based on pattern analysis from related benchmarks mentioned elsewhere in the context. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| no rerank | rerank |
|---|---|
| REALM achieves the best End-to-End Exact Match (EM) scores among all systems after a single fine-tuning stage. This performance is consistent across both dev and test sets for questions from various subsets of data within NaturalQuestions Open, such as TriviaQA or WordNet + WikiGiven. Specific EM percentages are not provided in the context but it's clear that REALM outperforms all other systems based on this metric. | REALM achieves an EM score of 46.8% on the NaturalQuestions Open benchmark. |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| no rerank | rerank |
|---|---|
| 44.5 | RAG-Sequence achieves a score of 44.5 EM (Exact Match) on the NQ dataset as reported by Lewis et al. This result indicates that when compared to baselines, RAG-Sequence performs exceptionally well in this benchmark for retrieval-augmented generation models using dense passage retrieval and BART large as a generator with DPR as a retriever. |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| The Transformer base model uses 8 attention heads with a model dimension (d) of 64 for each head after projection from an initial hidden size. The total number of parameters is reported to be around 110 million, which corresponds to the encoder part in this case as it does not include decoder parts when discussing base sizes separately. | The Transformer base model uses 8 parallel attention layers (heads) with each head having a dimensionality of d = 64, as established by dividing the original dimensions A=12 and h = 8 in Section 3.1 of the document provided contextually elsewhere. The total number of parameters for this encoder is given to be around 110M. |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| The dimensions used in the Transformer's fully connected layers are not specified within the given context; therefore, I do not have information regarding this detail based on the provided text. Typically, knowledge about such architectural details can be found by referring to original research papers like Vaswani et al., (2017), or detailed implementation guides for specific models using Transformers since different implementations may vary in these dimensions. | The question seems unrelated or insufficiently specified based on the provided context because it asks about a "feed-forward network" without clearly distinguishing whether this refers to an encoder, decoder, attention mechanism, or some other component within Transformer base model. The dimensions for FFNs in each of these components are not explicitly mentioned together; hence I cannot provide a definitive answer from the context given alone. Generally speaking, the original transformer literature by Vaswani et al., which inspired this text snippet (though incomplete), proposes feed-forward network layers with dimensionality `d`. In most Transformer configurations including base models typically reported in research papers associated with Transformers like Google's BERT and GPT series as examples, the dimensions used are around 2048 for such FFN hidden layers. Without specific details on 'base model d', we can only assume this to be similar but not directly stated or derivable from provided context alone. |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| no rerank | rerank |
|---|---|
| The Hidden Size (H) for BERT-LARGE is 1024, and it has 16 Attention Heads. | The BERT LARGE model has a hidden size (A) of 16,000,000 (presumably referring to the embedding dimension since actual numbers in these models typically use far fewer parameters). However, there seems to be an inconsistency because standard implementations such as Google's pre-trained BERT do not scale up to this number. If it were 16M indeed intended for LARGE model size indication (which might refer more generally to the large variant or configuration), then typically that would mean a much larger hidden dimension, often in the range of hundreds of millions rather than just several million when scaling from BERT base upwards.<br><br>Regarding attention heads: The standard Transformer models like BERT use 12 self-attention heads (H=12). However, this document provides specific numbers for LARGE versions—which are not common terminologies as per the usual configurations of pre-trained transformers which do not scale up to such a large number. As with hidden size, it would be best if we interpret these figures cautiously unless they refer specifically to modified or custom implementations tailored by this paper's authors for their experiments that are different from standard BERT models known at the time of my knowledge cutoff in 2023.<br><br>Given no explicit information regarding a 'LARGE attention head count', I would infer these numbers were either typographical errors or not adhering to common standards and should be reviewed for accuracy against actual model specifications if available from this paper's details directly provided by the authors themselves in their published work. |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| The square root of d, denoted as √1 in the context (which seems to be a typographical error and should likely read sqrt(d)). This scaling is applied to prevent gradients from becoming extremely small or large when computing attention scores for very high-dimensional vectors. The corrected statement with proper notation would then read: "We scale the dot products by √1 before applying the softmax function." | The context provided discusses various aspects of Transformer models and their performance with respect to different values of dimensionality (d). One key element in these details is how Scaled Dot-Product Attention handles scaling factors for large dimensions. According to the information, when performing dot products within this attention mechanism, there's a concern that without any adjustments, very high magnitudes might push the softmax function into regions where it becomes unstable (specifically, mentioned as k^4).<br><br>To mitigate these potentially extremely small gradients and make the scale of attentional weights more manageable during training with deep networks or large dimensions, a scaling factor is applied to the dot products before applying the softmax function. The context specifies that this scaling involves dividing by d (the dimensionality), which can be interpreted as √d for square roots in mathematical expressions but should simply read sqrt(d).<br><br>However, no specific numerical value or constant other than '1' is provided directly within the text to indicate an actual scale factor. In essence, it seems that a scaling by "sqrt(d)" serves merely as contextual information about their approach without explicitly stating any unique scalar multiplier used in every instance of Scaled Dot-Product Attention beyond this division for normalization purposes before applying softmax. Therefore, the answer to your question is not directly stated; instead, it suggests using a scaling factor that results from dividing by d (which could be mathematically written as √d).<br><br>Based on typical practices in attention mechanisms and without any additional context suggesting otherwise within this provided text, we might assume they are normalizing the dot products before applying softmax to maintain stable gradients. However, since no specific constant scaling factor is given apart from '1' (implied by division), you would not be able to directly find a numerical value for it in this particular context. |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| no rerank | rerank |
|---|---|
| REALM computes the probability p(z \| x) as a sample from the distribution conditioned on the original input x, often using an attention mechanism to weigh different documents in the knowledge corpus Z relative to how relevant they are to the given query. The specific computation involves learning parameters that can encode both local and global biases towards particular types of information within z based on its content's relevance to the masked token y in x for pre-training or question qx for fine-tuning tasks. | The likelihood score f(x, z), which indicates how probable it is for a specific retrieved document to be relevant or useful with respect to an input query, depends on whether incorporating that particular document into the knowledge base would improve prediction accuracy. Specifically, this scoring function can increase when p(y \| z, x) > p(y \| x), meaning if including the document z in response to question/answer pair (x, y) raises the probability of predicting y accurately over just using input query x alone without any retrieved documents.<br><br>The retrieval process is effectively a form of gradient descent on REALM's objective function concerning p(z \| x), wherein z represents all potential knowledge source documents that could assist in answering question or completing the masked part within an input sentence when paired with query x, while taking into account and adjusting for their relevance as scored by f (x, z). |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| no rerank | rerank |
|---|---|
| According to Table 1, when comparing T5-based models like RAG and pre-training methods such as those used in REALM for the task of open-domain question answering (QA), there is no direct comparison provided between these specific systems within this context. Therefore, I cannot provide a direct answer on how they compare based solely on the information given herein. To accurately determine their relative performance on NaturalQuestions Open or any other dataset/task, one would need to refer directly to studies comparing both RAG and REALM specifically against each other under similar conditions. | According to the provided context, we are not given specific numerical results comparing RAG and REALM directly. However, it is indicated that as of December 15th, 2020 (referred in Section III), there were ongoing works where both systems could be compared using ROUGE scores; these comparisons have yet to appear online at the time of this context's writing. Thus, we cannot accurately answer how RAG compares with REALM specifically for NaturalQuestions Open from just within the provided text itself without additional data or updates beyond December 2020 that would detail their performance side-by-side. |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| BERT has a total of 768 attention heads, whereas we are not provided with explicit information regarding how many this is over the original or unspecified "base" version. Typically, BERT-BASE refers to a specific configuration which uses a larger number than smaller variants like BERT-Small (which had only 12 attention heads), but without additional context about what constitutes the 'original' Transformer model size in terms of attention heads for comparison, it is impossible to provide an exact difference. However, we can infer that there are significantly more than double since larger models typically scale up various components including head count relative to smaller ones like BERT-Base and even further with DistilBERT which has 6 attention heads (though this latter model isn't directly comparable as it is a distilled version of BERT). | Based on the given context, it isn't explicitly mentioned how many attention heads are in a "base" (not otherwise specified) Transformer model. However, we can infer that since all other described BERT models have at least two different sizes of attentions with specific numbers provided for LARGE and Base-24 variants ("L=64", A="16"), the smallest mentioned size is 8 attention heads (Based on base model specification). Therefore, without exact details regarding a "base" Transformer's configuration in this context, we can only assume that BERT models have significantly more—up to double or triple at least of these specified numbers. If one takes LARGE with its higher capacity as the standard for comparison and goes by implication alone from 'conLARGE', assuming it might be twice an original base count in this context, then a simple doubling could suggest that BERT-BASE potentially has up to 16 attention heads at minimum. However, without explicit details on "base" Transformer's number of heads or direct comparison figures within the text, we cannot provide an exact figure but can only infer based on relative information provided for larger models in context and typical scaling practices. |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| no rerank | rerank |
|---|---|
| RAG-Sequence outperforms the T5 large model and achieves a score of 14.3 EM, while it is not specified how RAG compares directly to REALM in this specific context as their performance scores on WebQuestions are provided separately by different sources (Lewis for RAG-Sequence; Guu et al., without mentioning the exact numbers comparable between these works). However, based on general trends noted elsewhere where both systems performed well with dense retrieval and BM25 falling short compared to DPR, it can be inferred that REALM's performance might have been competitive or superior due to its effective use of document indexing. | RAG-Sequence has not been directly compared with REALM in the provided context for performance on WebQuestions. The text does mention that RAG and ORQA are direct comparisons, but it doesn't provide specific details regarding their comparison results on this task specifically within Table 1 of Lewis et al.'s (2020) paper or elsewhere in the document. To find a precise answer to how they compare based on EM scores for WebQuestions would require access to that information directly from Tables presented in those papers, which is not included in your context here. |


---

## Runtime

| Config | Time |
|--------|------|
| no rerank | 0.0 min |
| rerank | 24.8 min |
| **total** | **24.8 min** |
