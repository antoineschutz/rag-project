# best

**backend:** ollama · **model:** phi3

| Parameter | best-combined | baseline |
|-----------|--------|--------|
| retriever | hybrid | dense |
| embed_model | BAAI/bge-small-en-v1.5 | all-MiniLM-L6-v2 |
| fusion | rrf | — |
| alpha | 0.5 | — |
| rerank | True | False |
| top_k | 20 | 15 |
| no_rag | False | False |
| chunk_max_tokens | 128 | — |

---

## Q1 · Level 1

**Question:** Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?  
**Expected:** The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.  
**Source:** `rag_design_notes.md`

| best-combined | baseline |
|---|---|
| The primary reason for selecting `all-MiniLM-L6-v2` (alias Decision) over `bge-base-en-v1.5` as the default embedding model is that despite a significant quality gap of only .4 points in terms of top-5 EM on the eval set, which fell to 0.743 for our choice versus 0.761 for Base_En V1 (as stated directly under 'Chunking Configuration'), it did not justify a threefold latency increase when considering local, single-user pipeline efficiency and computational resources constraints such as using Google Cloud TPUs mentioned in the context about model speedup comparisons between `IndexFlatIP` or `IndexIVF`. This decision reflects an optimization tradeoff where minimizing retrieval time is given priority over a slight increase in embedding quality. | The decision to choose `all-MiniLM-L6-v2` as the default was based on a balance between performance and efficiency for local, single-user pipelines where latency is critical. Although there were only minor quality gains of about 0.35%, choosing this model meant accepting these in exchange to avoid significant increases in latency — specifically from around 18ms with `all-MiniLM-L6-v2` down to roughly half that at approximately 9ms when compared to the more resource-intensive but slightly better performing option, which had about a .05 quality gap.<br><br> |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| best-combined | baseline |
|---|---|
| By adding 'Source: {source}' before each passage, hallucinations on the eval set decreased from 11/47 (23%) instances to just 3/47 (6%). This reduction illustrates that explicit source attribution significantly curtails model-generated content not grounded in provided evidence. | Adding explicit source attribution reduced hallucinations from 23% on the eval set to 6%. |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| best-combined | baseline |
|---|---|
| The document suggests that at a current corpus size (~4,200 chunks), the speedup from using IVF is irrelevant. However, it states that above ~100,000 chunks or roughly 386M tokens in total, FAISS and specifically IndexIVF becomes worthwhile due to significant query time improvements. Therefore, for FAISS with an IVF index type to be considered beneficial over the IndexFlatIP setup based on speed alone, a corpus size of approximately 100,000 chunks or more is required. | FAISS IVF becomes worthwhile over IndexFlatIP when the number of chunks exceeds approximately 100,000. Below this threshold, other factors such as a smaller corpus size or less complex queries may not justify the transition to FAISS with an Inverse Document Frequency (IVF) index despite its potential for faster query speeds. |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| best-combined | baseline |
|---|---|
| The gap between BM25 and DPR performance on NQ as compared to TriviaQA can be attributed mainly due to the inherent characteristics of these datasets. The dataset for NQ is longer, paraphrastic questions with lower lexical overlap between question and answer passage, which requires more sophisticated retrieval systems that are capable of understanding contextual nuances in text similar to DPR's dense passages methodology; whereas TriviaQA has shorter, simpler sentences where keywords often have high lexical overlap leading BM25 performing relatively better. | The gap between BM25's performance and that of dense retrieval systems like DPR (Dense Passage Retrieval) can be attributed to the nature of questions posed in each dataset. NaturalQuestions consists mainly of longer, more paraphrastic queries where lexical overlap with potential answer passages is often low. This makes it difficult for BM25, which relies on word overlaps between query and passage terms, hence falling significantly behind DPR that uses a bi-encoder trained specifically on the NQ dataset to better understand contextual relevance regardless of direct lexical overlap. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| best-combined | baseline |
|---|---|
| BART-large | BART-large |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| best-combined | baseline |
|---|---|
| 0.743 | 0.743 |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| best-combined | baseline |
|---|---|
| ```json<br>{"answer": "RAG-Sequence with a score of 81.7 EM"}<br>``` | BERT (Single) - Top Leaderboard System with Highest Score of F1 = 87.3% |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| best-combined | baseline |
|---|---|
| 4 ms for both IndexFlatIP and IndexIVF | The query latency for `IndexFlatIP` and `IndexIVF (nlist=32)` are both recorded at 4 milliseconds. However, it's important to note that while the IVF index has a slightly lower top-5 EM score of 0.736 compared to IndexFlatIP’s 0.743, and is built in about half the time (1.1 seconds for `IndexIVF` vs 0.8 seconds), it provides an additional speed advantage during querying as per the context provided above:<br><br>"FAISS \| IndexIVF ... Query latency (ms) \| --------------\|-------------------\|<br>\| FAISS \| IndexFlatIP     \|   0.743      \|       0.8         \| 4            \|<br>\| FAISS \| IndexIVF (nlist=32)\|  0.736    \|      1.1          \| --------------\|" |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| best-combined | baseline |
|---|---|
| In the benchmark report, it is stated that "RAG-Token and RAG-Sequence reach identical NQ EM (44.5)." This indicates that both models achieved an Exact Match score of 44.5 on the NaturalQuestions (NQ) dataset in the reported evaluation context. | RAG-Sequence achieves a score of 41.5 EM on Natural Questions (NQ) according to Table 2 mentioned in the context. However, it's important to note that this information is provided as part of an invented benchmark report and not actual experimental results from research papers or studies conducted by Lewis et al. |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| best-combined | baseline |
|---|---|
| The document doesn't provide specific numbers for how dense passage retrieval (DPR) performs on NaturalQuestions (NQ) using a top-10 versus a top-5 retrieval approach. It does, however, mention that with the DPR model and an initial setup of considering only top-5 documents, it achieves higher performance than when restricted to just top-5 or even more extensive recall strategies like exhaustive search (top-k(p(·\|x))). To get exact numbers for a comparison between using top-5 vs. top-10 retrieval with the DPR system on NQ, one would need additional data from experiments that specifically tested these scenarios as mentioned in "Table 2" of their study or similar benchmarks where such comparisons were made. | For NaturalQuestions (NQ), when using the Document Passage Retrieval (DPR) system, achieving a score of 44.5 Exact Match (EM) by considering only the top-5 retrieved documents shows RAG's ability to retrieve relevant information efficiently for this task. When expanding to consider just the top-10 retrievals before applying any fine-tuning, we find that DPR achieves a higher NQ EM score of 48%, demonstrating an improvement in results when more potential documents are considered during pre-training and not only relying on the most relevant document. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| best-combined | baseline |
|---|---|
| The RAG-Sequence model achieves the highest Exact Match (EM) score on Natural Questions [52], which is substantially higher compared to other systems, indicating strong open-domain QA performance. However, for TriviaQA, CuratedTrec and MS-MARCO are not directly comparable with RAG models due to different data preprocessing conventions mentioned in the context provided—CuratedTrec answers given as regular expressions were filtered out because they did not occur within top 1000 documents. The highest EM score achieved on TriviaQA is by the system Ours BERT (Single) with a score of 78.7, which suggests that it performs strongly against other systems including MS-MARCO and Jeop0dy question generation approaches mentioned in passing within the context without specific scores given for these latter models as they are not directly benchmarked on TriviaQA EM results according to this particular document excerpt.<br><br>However, since RAG-Sequence is explicitly compared with CuratedTrec (CT) and MS-MARCO systems using F1 score rather than the Exact Match for which CT's performance was mentioned as 74.8 on TriviaQA—just slightly lesser than Ours BERT’s EM of 78.7, without direct comparison to RAG models in terms of these specific metrics within this context provided and no scores given directly against them by the RAG-Sequence model —it is not definitively clear from the excerpt which system has achieved the highest TriviaQA performance purely based on EM score since MS-MARCO's F1 results are mentioned but their exact EM counterpart isn’t specified. The best answer, with given information within this context to directly compare against RAG models for a specific dataset (TriviaQA), is Ours BERT which scores 78.7 on TriviaQA; however, without additional data or direct comparison metrics provided in the document excerpt specifically relating MS-MARCO's EM score to that of RAG systems for this benchmarking context (TriviaQA), we cannot conclusively state which system achieves the highest performance. | The QANet ensemble model achieved the highest TriviaQA Exact Match (EM) score, which was not explicitly stated but can be inferred to have outperformed other systems mentioned for this specific task. Since no numerical EM value is provided in the context for individual models or ensembles on TriviaQA, we refer back to the benchmark test results section where it lists human performance at 82.3 EM and mentions several model performances without directly stating which has the highest score:<br>- Ensemble (NLNet) - 86.0 EM<br>- Published BiDAF+ELMo Single System - not provided in numerical form but implied to have better results than BM25 since it's compared favorably with DPR on NQ, which suggests good performance across benchmarks and by the naming convention (Single) implies a less complex system.<br>- RAG Token Model/RAG Sequence System - 68.0 EM for TriviaQA specifically is mentioned but does not specify if this outperforms Ensemble's score of 86.0. Human performance, however, tops at 91.2 EM on the same platform.<br>- BERT Single Model and RAG Sequence System - no explicit scores given for these models with respect to TriviaQA in the text provided.<br><br>Given that ensembles generally tend to perform better than single systems due to their combined strengths, it is reasonable to assume that the QANet ensemble model achieved a high EM score on TriviaQA; however, without specific numbers or comparisons stating "highest," we can't definitively say which system had the highest. Human performance would typically be considered as the gold standard but was not part of this retriever ablation study since humans are excluded from comparison with systems in Table 2 (the provided context). |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| best-combined | baseline |
|---|---|
| Final configuration is set to have `CHUNK_MAX_TOKENS = 128`, which indicates a maximum token limit per chunk, while the overlap between chunks has been fine-tuned to be `CHUNK_OVERLAP = 50` tokens. | The final `CHUNK_MAX_TOKENS` value is 128, while the `CHUNK_OVERLAP` value is set to 50. These values were determined empirically as part of optimizing the chunking strategy for better precision in retrieving relevant tokens from a text corpus using FAISS indexing and embeddings with Tiktoken accumulation approach. |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| best-combined | baseline |
|---|---|
| The provided context does not specify the exact token overlap percentage used by the current chunking configuration explicitly. It mentions that `CHUNK_OVERLAP` is set to a specific value but doesn't state what this number represents in terms of percentages directly related to token overlap within chunks themselves. Instead, it refers to sentence-level overlaps with retrieval documents when using the tiktoken accumulation strategy and does not provide direct information regarding word or token overlap percentage inside individual chunks during chunking for language model training. Therefore, without additional context indicating that `CHUNK_OVERLAP` pertains directly to tokens within a single chunk (e.g., "10% of the text in each 128-token max span is overlapped with adjacent chunks"), we cannot infer this information from the provided text alone. | 15% |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| best-combined | baseline |
|---|---|
| The key distinction lies in how they utilize retrieved documents. The RAG-Token model generates a different latent document for each target token, effectively marginalizing over multiple potential sources to choose content when producing an answer. Conversely, the RAG-Sequence approach treats all tokens within a generated sequence as conditioned on reading from and recalling information in one retrieved document throughout generation of that entire sequence. | The primary distinction lies in their approach to handling retrieved documents. In RAG-Token, a different latent document can be drawn for each token of the target sequence allowing content from various documents when producing an answer during generation process; whereas, in RAG-Sequence model uses same retrieved document throughout and marginalizes over it using top-K approximation to generate the complete sequence. Thus both models differ in their treatment and integration of external knowledge into text completion tasks. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| best-combined | baseline |
|---|---|
| The RAG model uses a pre-trained neural retriever based on DPR. The details about this retriever are not explicitly mentioned in the provided context, but we can infer that it is designed to work well with language generation tasks and has been trained using datasets like Natural Questions and TriviaQA. | The RAG model uses DPR (Dense Passage Retrieval) as its retriever, which is based on a bi-encoder architecture using BERT for document and query encoding. The specific implementation of DPR mentioned in the context initializes with Document Re-Ranking from KVR-Reader [25]. |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| best-combined | baseline |
|---|---|
| The two pre-training tasks that BERT uses are the Masked Language Model (MLM) and Next Sentence Prediction (NSP). The MLM task masks some of the tokens from the input, with a probability of 15%, and requires predicting the original vocabulary ID of these masked words based solely on context. On the other hand, NSP is not explicitly described in detail within this instruction excerpt but implies an additional pre-training task that helps BERT understand text pairs or sentences as a whole by learning which sentences follow each other naturally. These two tasks together enable deep bidirectional representations and are pivotal to BERT's success across various NLP benchmarks. | The context provided does not specify which two particular pre-training tasks BERT uses as it only mentions that during its training phase for unlabeled data over different pre-training tasks, the model learns representations such as A/B and sentence embeddings. These may be components of various combinations of pre-training objectives used in practice but without a specific reference to two defined distinct ones within this text, it is not possible to determine which exactly they are from the context given alone. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| best-combined | baseline |
|---|---|
| 15% of all WordPiece tokens in each sequence are randomly masked during pre-training for the Masked Language Model (MLM) task. However, a small portion, only about 10%, is replaced with another random token at training time instead of always using [MASK]. | 15% |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| best-combined | baseline |
|---|---|
| REALM uses salient span masking as well as random token masking for the language model (MLM) task to better focus on problems that require world knowledge. This is because some MLM spans only require local context whereas others, which involve factual information like "United Kingdom" or specific historical events such as “July 1969”, rely heavily on external knowledge not present in the immediate text vicinity and thus necessitate a more targeted approach to masking. | REALM uses salient span masking for its pre-training. This strategy is used to focus on examples that require world knowledge because it targets specific tokens within the text such as "United Kingdom" or "July 1969." These are considered salient spans, which by their nature would benefit from retrieving relevant documents containing this information during training since they pose problems requiring external context for accurate prediction of masked words. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| best-combined | baseline |
|---|---|
| 1. Self-attention mechanisms connect all positions with constant operations, improving parallelization and speed during training as opposed to the O(n) sequential operations required by recurrent layers.<br><br>2. The computational complexity of self-attention grows only linearly between any two input or output positions in contrast to logarithmically for ConvS2S with increased difficulty learning dependencies between distant signals due to path length, which is not an issue for the Transformer model since it keeps this at a constant number of operations.<br><br>3. Multi-head attention allows different heads within self-attention layers to learn diverse aspects or tasks (e.g., syntactic and semantic structures in sentences), adding interpretability to models with potential benefits across various sequence transduction tasks, something that cannot be achieved as directly using recurrent layers. | 1. Self-attention allows the model to learn dependencies without regard to their distance in the input sequence, which can capture long-range interactions more effectively than RNNs that process data sequentially from left to right or vice versa. This is because self-attention mechanisms compute a representation of each position by attending over all positions simultaneously within a single attention layer.<br><br>2. Self-attention layers have constant computational complexity regardless of the sequence length, making them more parallelizable and thus faster for training on modern GPUs compared to RNNs that increase their sequential computation time with longer input sequences (O(n) operations). This advantage becomes significant in cases where d < n as it's most often encountered.<br><br>3. Self-attention mechanisms have been shown empirically, especially within the Transformer model context by Vaswani et al., to yield more interpretable models due to attention distributions that can clearly indicate which parts of the input sequence influence each output position and how syntactic and semantic structure are learned in representation learning tasks. |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| best-combined | baseline |
|---|---|
| The document does not provide specific information about the BLEU scores achieved by ConvS2SEnsemble specifically for the WMT 2eneral-to-French translation task on the provided text. However, it mentions that ConvS2SEnssembly (ConvS2S Ensemble) achieves a top score of 41.8 BLEU after training in an English-to-French context with just one model's parameters and without dropout rate P = 0.3 applied, as per the original Transformer (big) mentioned later on Table 2 which is not explicitly part of ConvS2SEnssemble but rather a separate big transformer model based architecture from Google Brain paper by Carless et al., referenced in [9]. Since "ConvS2SEnsemble" isn't directly discussed with WMT-specific scores, the BLEU score achieved using its approach on this task is not provided. | The document does not provide specific information about the BLEU score achieved by ConvS2S Ensemble on WMT 2014 English-to-French. The text only mentions that our best Transformer model outperformed all previously reported single models, at a fraction of their training cost without specifying scores for ensembles or other architectures like ConvS2S. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| best-combined | baseline |
|---|---|
| To estimate the number of floating point operations used to train the base Transformer model, we multiply together the given values for each component involved in computing this figure. These components are the training time (10 minutes per checkpoint), an average of eight GPUs' sustained single-precision FP throughput capacity as stated on page 5 of our paper ("...about [8] to a value we estimate here."—assuming that one P100 can produce 'x' operations in a second, then the total number would be:<br><br>Total Operations = Training Time * Number of GPUs * Single-Precision FP Capacity per GPU<br>                      = 60 minutes/checkpoint * (8 checkpoints) * x ops/sec.gpu * seconds/minute<br><br>The precise figure for 'x' isn’t provided in your context, so we can only provide the formula rather than a specific number of operations: Total Operations = 480x | To calculate the training cost in floating-point operations (FLOPs) for a given model, we would typically multiply three factors together as mentioned in the context provided. However, since specific details such as single-precision FLOP calculations per operation or sustained GPU capacity are not explicitly stated within this particular extraction of text from your document other than an estimate reference [5], I can't calculate it directly without additional data. To provide a precise answer with the information given here would be speculative at best, and potentially inaccurate if we don’t rely on appropriate benchmarks or estimates for GPU FLOP computations during training of Transformer models. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| best-combined | baseline |
|---|---|
| 86.2 | The provided context does not explicitly mention a QQP score for BERT-LARGE obtained from the GLUE benchmark. However, it states that "on official leaderboard10, GLUE BERT obtains a score LARGE of 80.5." Since this is likely referring to BERT's performance on the task within the larger context of all tasks in GLUE (not specifically QQP), and given that scores are not differentiated by specific tasks beyond stating an overall "LARGE" classification, it is impossible to accurately determine the exact score for just the QQP.<br><br>To obtain this figure if available elsewhere or from a leaderboard archive directly would be necessary as of my last knowledge update in April 2023. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| best-combined | baseline |
|---|---|
| 46.8 EM Score | REALM achieves the best End-to-End Exact Match (EM) scores among all systems after a single fine-tuning stage. This performance is consistent across both dev and test sets for questions from various subsets of data within NaturalQuestions Open, such as TriviaQA or WordNet + WikiGiven. Specific EM percentages are not provided in the context but it's clear that REALM outperforms all other systems based on this metric. |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| best-combined | baseline |
|---|---|
| Rag-Sequence achieves an Exact Match score of 44.5 on NaturalQuestions as per the information provided by Lewis et al. | 44.5 |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| best-combined | baseline |
|---|---|
| The Transformer base model uses 8 parallel attention heads (h = 8) with a head size of d = 64, resulting from dividing the original hidden size A by the number of heads. The total parameter count for this model is approximately 110 million parameters when considering BERT-BASE's equivalent setting in terms of dimensions and scale. | The Transformer base model uses 8 attention heads with a model dimension (d) of 64 for each head after projection from an initial hidden size. The total number of parameters is reported to be around 110 million, which corresponds to the encoder part in this case as it does not include decoder parts when discussing base sizes separately. |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| best-combined | baseline |
|---|---|
| The question seems to be based on a misunderstanding. The provided text discusses various aspects of attention mechanisms and transformer models but doesn't specify dimensions for any feed-forward networks within these contexts, except mentioning the dimensionality `d` in sublayers as part of the Transformer model architecture itself. There are details regarding different sizes (L=12 or L=24) with corresponding hidden size A and attention heads H which do provide information about dimensions but not directly relating to a feed-forward network's specific dimension within these models unless further context is given in other parts of the document that aren’t included here.<br><br>To answer questions on Transformer model variations, you would need details like different sizes for encoder and decoder layers (L), hidden size A, or attention heads H; however, they are not directly asking about feed-forward network dimensions within these contexts but rather discussing the overall architecture's flexibility in terms of layer counts. | The dimensions used in the Transformer's fully connected layers are not specified within the given context; therefore, I do not have information regarding this detail based on the provided text. Typically, knowledge about such architectural details can be found by referring to original research papers like Vaswani et al., (2017), or detailed implementation guides for specific models using Transformers since different implementations may vary in these dimensions. |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| best-combined | baseline |
|---|---|
| HIDDEN SIZE: 1024<br><br>NUMBER OF ATTENTION HEADS: 16 | The Hidden Size (H) for BERT-LARGE is 1024, and it has 16 Attention Heads. |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| best-combined | baseline |
|---|---|
| The scaling factor applied is \( \sqrt{1/d} \) or equivalently, "one divided by the square root of d." This compensates for large values in high-dimensional dot products. | The square root of d, denoted as √1 in the context (which seems to be a typographical error and should likely read sqrt(d)). This scaling is applied to prevent gradients from becoming extremely small or large when computing attention scores for very high-dimensional vectors. The corrected statement with proper notation would then read: "We scale the dot products by √1 before applying the softmax function." |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| best-combined | baseline |
|---|---|
| REALM computes the probability of retrieving document z, denoted as p(z \| x), by using a knowledge retrieval function that assigns relevance scores to documents based on their similarity to the query. The model employs an embedding mechanism for both the input sequence and retrieved documents. These embeddings are used in conjunction with a Transformer architecture specifically trained for this task, which allows REALM to perform rich cross-attention between x and z before making predictions. This process inherently rewards retrievals that lead to more accurate prediction of masked tokens by comparing the marginalized probability p(y \| x) when conditioning on retrieved documents versus without them (p(y \| ∅, x)). | REALM computes the probability p(z \| x) as a sample from the distribution conditioned on the original input x, often using an attention mechanism to weigh different documents in the knowledge corpus Z relative to how relevant they are to the given query. The specific computation involves learning parameters that can encode both local and global biases towards particular types of information within z based on its content's relevance to the masked token y in x for pre-training or question qx for fine-tuning tasks. |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| best-combined | baseline |
|---|---|
| As per the provided context, which states that Table 3 shows results for NaturalQuestions-Open after ablating critical components of REALM. The specific numbers or performance metrics comparing RAG to REALM are not directly quoted from this summary; however, it is mentioned that “our system gets the overall best performance while only retrieving 5 documents.” This suggests a strong competitive edge for RAG on NaturalQuestions-Open in terms of effective document retrieval and presumably related accuracy or efficiency metrics. | According to Table 1, when comparing T5-based models like RAG and pre-training methods such as those used in REALM for the task of open-domain question answering (QA), there is no direct comparison provided between these specific systems within this context. Therefore, I cannot provide a direct answer on how they compare based solely on the information given herein. To accurately determine their relative performance on NaturalQuestions Open or any other dataset/task, one would need to refer directly to studies comparing both RAG and REALM specifically against each other under similar conditions. |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| best-combined | baseline |
|---|---|
| Bert has multiple times as many (12) attention heads than a single head transformer, effectively increasing it by an order of magnitude in terms of parallelism over traditional unidirectional models. The exact number is not specified here but given that BERT's scale and complexity are substantially higher, the difference must be significant. | BERT has a total of 768 attention heads, whereas we are not provided with explicit information regarding how many this is over the original or unspecified "base" version. Typically, BERT-BASE refers to a specific configuration which uses a larger number than smaller variants like BERT-Small (which had only 12 attention heads), but without additional context about what constitutes the 'original' Transformer model size in terms of attention heads for comparison, it is impossible to provide an exact difference. However, we can infer that there are significantly more than double since larger models typically scale up various components including head count relative to smaller ones like BERT-Base and even further with DistilBERT which has 6 attention heads (though this latter model isn't directly comparable as it is a distilled version of BERT). |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| best-combined | baseline |
|---|---|
| RAG-Sequence achieves a higher Exact Match score compared to BM25 baseline by 18 EM points on NQ, while the comparison between RAG-Sequence and REALM is not explicitly detailed in terms of direct scores or performance metrics for WebQuestions. However, since both models are evaluated using similar techniques (like inverse cloze probing), we can infer that they employ a comparable approach to knowledge retrieval from corpuses like Wikipedia. As such, the comparison would largely depend on their effectiveness at leveraging this retrieved information during QA tasks specific to WebQuestions datasets and benchmarks within these settings. | RAG-Sequence outperforms the T5 large model and achieves a score of 14.3 EM, while it is not specified how RAG compares directly to REALM in this specific context as their performance scores on WebQuestions are provided separately by different sources (Lewis for RAG-Sequence; Guu et al., without mentioning the exact numbers comparable between these works). However, based on general trends noted elsewhere where both systems performed well with dense retrieval and BM25 falling short compared to DPR, it can be inferred that REALM's performance might have been competitive or superior due to its effective use of document indexing. |


---

## Runtime

| Config | Time |
|--------|------|
| best-combined | 33.2 min |
| baseline | 0.0 min |
| **total** | **33.2 min** |
