# embed_model

**backend:** ollama · **model:** phi3

| Parameter | all-MiniLM-L6-v2 | bge-small-en | e5-small |
|-----------|--------|--------|--------|
| retriever | dense | dense | dense |
| embed_model | all-MiniLM-L6-v2 | BAAI/bge-small-en-v1.5 | intfloat/e5-small-v2 |
| rerank | False | False | False |
| top_k | 15 | 15 | 15 |
| no_rag | False | False | False |

---

## Q1 · Level 1

**Question:** Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?  
**Expected:** The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The primary reason for selecting `all-MiniLM-L6-v2` as the default is that despite a significant quality gap of approximately 4.4 points, it only resulted in a threefold increase in latency compared to `bge-base-en-v1.5`. This balance between performance and computational cost makes it more suitable for local single-user pipelines where maintaining low latency is crucial. | The primary reason for selecting `all-MiniLM-L6-v2` as the default was its balanced performance between quality and latency. Although there was a 4.4 point gap in top-5 EM (Exact Match) rate, this difference did not justify a threefold increase in latency when considering it for use on local single-user pipelines where such significant delays could be detrimental to user experience or system efficiency. In contrast, `bge-base-en-v1.5` had lower top-5 EM but also exhibited higher and increasing latencies as the model size grew, implying that its performance benefits were not enough to outweigh these additional costs in a local setup. | The decision to select `all-MiniLM-L6-v2` as the default was based on its performance, where it outperformed `bge-base-en-v1.5` by a small margin but justified this choice because of significantly better retrieval quality and acceptable latency increases compared to other models in the evaluation set. |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| Adding 'Source:' before each passage reduced hallucinations on the eval set from 11/47 (23%) to 3/47 (6%). | Adding explicit 'Source:' prefixes before each passage reduced hallucinations from a rate of 23% on the eval set down to just 6%. This indicates that nearly half of the potential hallucinations were avoided by clearly attributing retrieved contexts. | Adding 'Source:' before each passage reduced hallucinations on the eval set by half, from 11/47 (23%) to 3/47 (6%). |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| FAISS IVF becomes worthwhile above ~100,000 chunks of text according to the context provided. | FAISS IVF becomes worthwhile above ~100,000 chunks according to the provided context. Above this threshold in terms of chunk size and corpus volume, FAISS with an Inverse-index (IVF) type index provides significant advantages like a speedup for queries at the cost of a slight EM drop compared to IndexFlatIP which does not require such large data sizes for its benefits to be realized. | 100,000 chunks |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context provided suggests that NQ questions tend to be longer and more paraphrastic, which results in a lower lexical overlap with answer passages. BM25 relies on word overlap as part of its retrieval strategy; hence it struggles compared to DPR, which uses dense passage retrieval techniques better suited for the characteristics of NQ questions where lexical cues are less prominent but context and semantics play a larger role. | The gap between BM25's performance on NQ versus TriviaQA can be attributed to the nature of questions and answers in each dataset. In TriviaQA, the questions are shorter and more straightforward with a higher likelihood of lexical overlap between them and potential answer candidates from Wikipedia passages. This makes it easier for BM25's word-based scoring system to find relevant documents that can provide accurate information directly without much parsing or understanding beyond surface-level semantics - which suits the simpler, more straightforward questions in TriviaQA well.<br><br>On the other hand, NaturalQuestions (NQ) features long and complex questions often requiring a broader context for an appropriate answer, as they are based on real user interactions with OpenWebSearch API over time during 2014-2015 [7]. These types of queries tend to be more open-ended or paraphrastic where the lexical overlap between questions and answers is notably low. In these scenarios, a dense retriever like DPR (Dense Passage Retrieval), which uses deep learning methods such as bi-encoder architecture trained on large datasets, can create embeddings that better capture nuances in language semantics and thus find more relevant documents even when lexical overlap is minimal. This results in BM25 being outperformed by DPR on NQ because of its simpler scoring mechanism's difficulty to navigate the complexity within these longer questions without explicit context or semantic understanding cues, unlike with TriviaQA where it performs strongly due to a better match between retrieval and content. | The gap between BM25 and DPR performance likely stems from differences in question complexity across the datasets. As mentioned, NQ questions tend to be longer and more paraphrasitical with lower lexical overlap to answer passages due to their open-domain nature which includes a wide array of topics unrelated directly by language cues alone. DPR leverages dense passage retrieval that can handle such diverse linguistic structures better, providing higher EM scores on NQ because it relies more heavily on understanding the context and semantics beyond simple word overlap - aspects where traditional BM25 might struggle due to its focus on lexical matching rather than semantic comprehension. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| BART-large. | BART-large | The RAG-Token and RAG-Sequence models utilize BART (Bayroque Advanced Regression Transformer) as the generation mechanism, endowed with a pre-trained transformer model for generating text sequences. Specifically mentioned in the context is that they use "BERT" and "BART large." |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context provided does not include specific information about a Top-5 EM (Exact Match) score achieved by the model named `all-MiniLM-L6-v2`. Therefore, based on this text alone, I do not have the answer to provide. To find out its performance, one would need additional data or context outside of what is provided here. | 0.743 | The table indicates that the all-MiniLM-L6-v2 model achieves a top-5 EM score of 0.743 on the evaluation set. |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| BERT Single system performs with an F1 score of 82.3% for Top Leaderboard Systems as reported on December 10th, 2018. While this data doesn't explicitly mention a top-5 EM (Exact Match) benchmark within the provided context, based on inference from the information given and common performance metrics in natural language processing tasks like those presented by leaderboards such as GlueBenchmark or SQuAD for retrieval systems, BERT is likely to achieve high scores. However, since we are specifically asked about top-5 EM without direct data points provided within this context (and assuming a standard of benchmarks wherein the highest score isn't necessarily denoted with F1 but rather exact matches), one may infer from similar performance patterns and typical outcomes that BERT models would excel in such tasks. Therefore, although an exact number for top-5 EM is not stated explicitly here, we can reasonably speculate that it will be high based on the overall positive results of BERT as reported across various benchmarks mentioned elsewhere within this context document or commonly known performance metrics of state-of-the-art models at their peak. | The RAG (Representations from Tasks with Gating) sequence method achieves the highest top-5 EM score of 38.0 on NQ as per Table 6 in the original text provided by a human reader, but this information is not explicitly mentioned within your given context directly about BERT models' scores or their performances at different retrieval methods and configurations like dense retriever ablation study (Table 2) nor detailed discussion of top-k performance. Since no specific system named "RAG sequence method" with a score of 38.0 EM is mentioned in the provided context, it suggests that this answer cannot be extracted from your given text alone and would require external knowledge or data not included within the provided information to confirm its accuracy. If we assume all systems listed are relevant here (as per Table 6), then BERT LARGE using DPR as a retriever seems closest in spirit but without an explicit mention of top-5 EM for dense, it's impossible to give this exact score based on the provided context alone. | all-MiniLM-L6-v2 with a top-5 Exact Match (EM) of 0.743. |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| IndexFlatIP has a query latency of 34 ms, while IndexIVF (with nlist=32) and its index are built in just 1 ms. However, it's important to note that the provided context does not explicitly mention if this is measured for both backends or solely for FAISS with IndexIVF since using different indexing types was part of a comparative experiment between NumPy cosine embeddings and FAISS based approaches which also included their respective latencies. | The context provided does not include specific data comparing the query latencies between IndexFlatIP and IndexIVF directly in tabular form or clear numerical values. However, it suggests that using FAISS with an IndexIVF configuration offers a significant speed advantage during queries when compared to the traditional `IndexFlatIP` used as Default:<br>- For `IndexFlatIP`: The query latency is 4 ms (from Table in Prompt Template Design).<br>- Though not explicitly provided for IVF, it's implied that IndexIVF offers a substantial improvement with only a reported ~0.7 EM points loss which suggests faster queries - specifically around the "1" mark as mentioned at one point without giving exact milliseconds but indicating superior performance due to 4× query speedup (from Context).<br><br>Without direct data on IVF's latency, it is reasonable to infer that IndexIVF provides a lower or similar query latency compared to IndexFlatIP based on the context’s implication of improved efficiency and without considering other trade-offs mentioned. To give an exact figure would require additional information not provided in this specific text snippet. | Query latency for `IndexFlatIP` is 4 ms while it's only 1 ms for `IndexIVF`. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| RAG-Sequence achieves an Exact Match score of 41.5% on the Natural Questions (NQ) dataset according to Table 2 in the main results section, which indicates its performance when using Dense Passage Retrieval (DPR). Note that this is not a direct answer but rather information inferred from context; retriever models and NLP benchmarking are common topics. However, if you're asking about RAG-Sequence's Exact Match score specifically without the influence of other methods like DPR as mentioned in your question, then it achieves an overall Exact Match (EM) score of 83.5% on TriviaQA and is not explicitly stated for NQ alone in this specific context provided. Please verify with additional sources if necessary. | RAG-Sequence achieves a score of 44.5 EM on Natural Questions (NQ) according to Table 3 and Context provided under "Main Results". This is reportedly substantially higher than some existing hybrid models, as it indicates strong open-domain question answering performance by the RAG-Sequence model in this context. | 44.5 EM (Exact Match) score on the NLP/LLM paper corpus test set using top-5 retrieved documents for retrieval quality measurement. |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| DPR achieves a higher Exact Match (EM) of 44.2% on the NQ dataset when using RAG as the generation model, which is an improvement over its baseline EM performance without this technique detailed in other parts of the context provided. However, there's no direct comparison given for DPR with top-5 vs top-10 retrieval specifically within dense or BM25 systems from NQ to give a precise answer on how their performances differ at these two points directly according to the text above. | Dense Passage Retrieval (DPR) achieves an Exact Match (EM) of approximately 41.5 and 43.2 on the NQ benchmark for top-k = 5 and k=10 respectively, indicating a slight EM gain with increased retrieval recall at larger k values. | DPR achieves an NQ Exact Match of 69.2% using a top-5 retrieval and maintains at least the same performance or slightly higher (44.5 EM) with a top-10 retrieval since more options are considered, which may include relevant documents that fall outside the top five but within ten retrieved passages. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| System Dev Test - BERT (Single) | Ours BERT (Single model outperforms top ensemble systems) with a score of 68.2 on TriviaQA. | RAG-Sequence with an F1 score of 68.2 on TriviaQA. |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| Final configuration of chunking parameters used in Tiktoken accumulation method is as follows:<br>- CHUNK_MAX_TOKENS = 128   # changed from the initial 256 due to empirical evaluation indicating better precision at this token budget.<br>- CHUNK_OVERLAP    = 50    # setting overlap between consecutive chunks for maintaining context continuity across chunk boundaries; higher values did not further improve recall after a certain point of increase in the value, hence chosen as is from empirical results obtained during testing phase which showed no significant improvement beyond this overlapping size. | Final configuration is set with `CHUNK_MAX_TOKENS = 128`, down from an initial value of 256. The selected overlap between chunks, or the number of tokens that are common to adjacent query and context embedd0ding them in shorter sequences (up to a token budget) was set at `CHUNK_OVERLAP = 50`. These empirical values were determined after testing different configurations on an evaluation set. | Final `CHUNK_MAX_TOKENS`: 128 tokens  <br>Final `CHUNK_OVERLAP`: 50 tokens |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context provided does not specify a particular percentage for the "token overlap" directly; therefore, I cannot provide an exact number from the given text as it stands incomplete and possibly missing information. However, there is mention of "[LM masking] with a uniform masking rate of 15%," which could imply that this method applies to some form of token processing or selection within chunk generation rather than direct overlap between chunks themselves. If you were asking about the percentage used in another process related to tokens not detailed here, please provide additional context so I can give an accurate answer. | The current chunking configuration uses a 50% token overlap as indicated by `CHUNK_OVERLAP` which is set to 50 in the provided context. This means that each new chunk overlaps with the previous one by half of its tokens, or more precisely, it shares at least 25 tokens (since exactly 50% would mean an overlap of 50). | The current chunking configuration uses a 50% token overlap as indicated by `CHUNK_OVERLAP` set to 50 in the provided context. This means that when new chunks are created, there is an expectation of overlapping tokens (e.g., words or subwords) with previously generated chunks by about half for consistency and coherence during sequential chunk generation tasks such as text completion or summarization within a document retrieval system like REALM. |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The key distinction lies in how they generate responses during sequence generation tasks. The RAG-Token model can draw different latent documents for each target token, allowing it to choose content from several relevant documents when producing an answer. In contrast, the RAG-Sequence Model uses a single retrieved document as one large latent variable and marginalizes over this entire 'document' to generate sequences, treating them similarly to how BERT processes input tokens with shared context across different parts of the text sequence (e.g., [CLS] token). | The main differences are as follows: The first significant distinction lies in their generation process during test time. To approximate arg max p(y\|x), both models require different methods. For RAG-Token, this involves treating the model like a standard autoregressive seq2seq generator with transition probability of (y \| x, y) being derived from top k retrieved documents and their corresponding probabilities. On the other hand, for RAG-Sequence we can select diverse latent document representations at each target token without marginalizing over them as in RAG-Token approach which allows multiple content sources during generation process when producing an answer or response.<br><br>In addition to this difference between handling documents and generating responses lies another notable distinction: Diversity of generated outputs, according to the study findings, is higher for RAG-Sequence compared to RAG-Token models in all tasks examined across MS MARCO benchmarks including Jeopardy Question Generation (JeQG) wherein both these generative techniques outperform BART.<br><br>Lastly while evaluating performance on various open domain question answering and jeopardy generation tasks, the study revealed that RAG-Token model performs slightly better than its counterpart - RAG-Sequence in terms of Exact Match score (EM) for Open MS MARCO NLG task but gets beaten by both models when they are compared to each other on JeoQGen benchmark.<br><br>Overall, the difference between these two types lies primarily within their generation methods and output diversity characteristics as well as specific performance outcomes in various tasks across different domains of open domain question answering or jeopardy-style questions. | RAG-Token uses different retrieved documents for predicting each target token, whereas RAG-Sequence utilizes a single retrieved document to generate the complete sequence. In essence, while both models use an external retriever (DPR) and encoder-decoder mechanism (BART), they differ in how they leverage the retrieved information during text generation for tasks like Jeopardy question generation or open-domain QA. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The Retrieval Component (p(z\|x)) used in the RAG model, as mentioned within a note indicating that it uses DPR's retriever initialized with documents from NQ. This is clarified by stating "Rag-Sequence and Rag-Token are equivalent" when considering target class as one element sequence or token respectively – emphasizing they both utilize the same underlying technology, which in this case would be a bi-encoder trained on Natural Questions (NQ). The exact name of DPR is not provided within the context. | The DPR (Dual Encoder Retrieval) system. | The context provided doesn't specify an exact name for a particular "retriever" used by RAG models, but it mentions that there are pre-trained neural retrievers available and also references using DPR’s retriever. It implies the use of general-purpose techniques like BM25 or systems similar to these rather than mentioning a specific named "retriever". |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| BERT uses MASK and UNMASK strategies as its two pre-training tasks, with different probabilities of using each strategy during MLM (Masked Language Model) training. The left part of the table represents these proportions where BERT might use either the masking or unmasking token to replace a word in a sentence for input into the model's transformer layers. | The text states that BERT uses a masked language model task as one of its unsupervised pre-training tasks and also employs a next sentence prediction task to jointly pretrain representations for pairs of texts. These two pre-training methods enable the creation of deep bidirectional Transformer models, which are foundational in understanding BERT's performance across various natural language processing (NLP) tasks. | Both A and B are correct, but since I must choose one based on the context provided earlier which specifically mentions MNLI NER as a task that can benefit from feature extraction using fixed features extracted via BERT's pre-trained model layers without retraining it for different masking strategies during MLM (Masked Language Model) training, option A is more relevant. However, if the question had not specified MNLI NER, both options would be valid as BERT uses two main tasks: Masked Linguistic Input and Next Sentence Prediction. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| 15% of input tokens are masked in BERT's MLM objective. | 15% | 15% |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| REALM uses a salient span masking scheme that focuses on tokens such as "United Kingdom" or specific dates like “July 1969”. This method ensures the model learns to retrieve examples from documents containing world knowledge, which is crucial since REALM's core strength lies in its ability to use retriever-augmented language models for tasks that require external factual information. | REALM uses salient span masking as its strategy for token masking in the language model pre-training stage. This approach is specifically designed to focus on tokens that require world knowledge or context beyond local cues within a text sequence. By identifying and masking important spans such as proper nouns like "United Kingdom" or specific dates like "July 1969," REALM ensures the model pays more attention during training to these salient pieces of information, which are often pivotal for understanding real-world knowledge. Salient span masking helps align pre-training with scenarios where world knowledge plays a critical role in language comprehension and generation. | REALM uses salient span masking to focus on examples requiring world knowledge for prediction as it helps direct the model towards meaningful retrievals. Salient spans include terms like "United Kingdom" or dates such as "July 1969". The idea is that by targeting these types of tokens, which often depend on external information rather than just local context, REALM can better learn representations useful for tasks requiring world knowledge and understanding. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| 1. Self-attention allows the model to extrapolate to sequence lengths longer than those encountered during training, unlike recurrent layers which struggle with long sequences due to issues like vanishing gradients and difficulties in parallelization on modern hardware architectures such as GPUs or TPUs.  <br>2. In terms of computational complexity, self-attention is faster for the most common case where sequence length n is smaller than representation dimensionality d—this often occurs with sentence representations used in machine translations like word-piece and byte-pair encodings. Recurrent layers require O(n) sequential operations to connect any two positions while a self-attention layer requires constant time regardless of the input size, which makes it more efficient for longer sequences or when dealing with large batches during inference/testing on parallel computing devices.  <br>3. Self-attention could yield models that are easier to interpret since attention distributions can highlight what different parts of inputs contribute towards decisions made by a model—an aspect not as readily available in RNNs where sequential dependencies make it hard to pinpoint specific cause and effect relationships within the input data during backpropagation. | 1. Self-attention allows the network to extrapolate to sequence lengths longer than those encountered during training, which is not as straightforward with RNNs that are prone to vanishing gradients when dealing with long sequences.<br><br>2. The self-attention layer offers a fixed computational complexity for any pair of input and output positions regardless of their distance in the network, unlike recurrent layers where processing distant inputs requires exponentially more computations due to sequential dependencies that need resolving over time steps (i.e., O(n^2) operations).<br><br>3. Self-attention mechanisms can learn different tasks within individual attention heads and potentially provide models with better interpretability by examining the learned representations, as opposed to recurrent layers which may not offer such transparent insights into their internal state dynamics or decision processes between time steps. | 1. Self-attention can be faster to train on tasks like machine translation compared to architectures with recurrent or convolutional layers, as demonstrated by their new state of the art results on WMT English-German and -French benchmarks.<br><br>2. The Transformer architecture based solely on self-attention allows each position in a sequence to attend directly to all other positions within that same layer (encoder or decoder), which is beneficial for learning dependencies without regard to their distance along the input or output sequences, as opposed to recurrent layers where information must propagate sequentially.<br><br>3. Self-attention mechanisms can potentially lead to more interpretable models due to attention distributions offering insights into what parts of a sequence are deemed important by different heads in multi-head self-attention configurations when applied during tasks like machine translation or language modeling, as seen with their analysis on various NLP datasets. |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| ConvS2S Ensemble achieved a BLEU score of 26.36 on the WMT 2014 English-to-French translation task. | The provided context does not contain specific information about the BLEU score achieved by ConvS2S Ensemble on the WMT 2014 English-to-French task. The table in the original text lists various models and their performance metrics, but it is missing this data for ConvS2S Ensemble with respect to French translation or any specific scores related to ensembles mentioned next to its entry without an associated BLEU score directly stated. To answer such a question accurately based on the context given would require assuming information that isn't present in the text, which is not permitted according to the instructions provided. Therefore, we must say that this detail cannot be found within the provided context. | The context does not provide the specific BLEU score achieved by ConvS2S Ensemble. Instead, it states that "ConvS2S Ensemble [9] 26.36 on Transformer (base model) but did not mention its own individual performance apart from being part of an ensemble which scored a certain way alongside the base and big models' performances. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| To estimate the number of Floating Point Operations (FLOPs) used for training, we look at Table 2 under "BLEU Training Cost (FLOPs)" and find that the term associated with Transformer (big) is listed as '41.8'. However, this value does not represent FLOP count but rather BLEU score achieved by the model after its training on English-to-German translation tasks. Therefore, based on the information provided in the context, I cannot calculate or determine the exact number of floating point operations used to train the base Transformer model since that specific metric is not given explicitly for it and instead requires an estimate as described: "We estimate the number of floating point operations by multiplying the training time, ...and 5." Without this explicit information on the actual Floating Point Operations count or a direct way to calculate based solely on provided data like GPU capabilities over specific durations (which have been used for other models), it is not possible to provide an answer. The correct response would be that we cannot determine the FLOPs from the given context as there's insufficient information about the training time and the number of operations per second achievable by each GPU in use, which are essential metrics needed alongside with actual numbers on model configuration (layers, heads, etc.) for this estimate. | The text does not provide explicit information about the number of Floating Point Operations (FLOPs) used to train the base transformer model. To calculate this, we would need additional data such as training time and GPU specifications which are provided for different models but not explicitly mentioned in relation to our baseline Transformer model's FLOP cost. | To estimate the number of floating-point operations (FLOPs), we need to know two things from the context provided and some assumptions about GPU capabilities. However, since there's no explicit mention of FLOPs or specific hardware specs in this part of your input that could allow us to calculate it precisely using standard benchmarking formulas for NVIDIA P100 GPUs—which typically have a sustained capacity around 39 GFLOPS (Giga-flops) under full load with no additional computations such as model parallelism or multi-head attention in Transformers, we can make an educated guess based on the information provided.<br><br>The paper mentions that each training step takes about 0.4 seconds and they used a hyperparameter setting which consists of different dimensions: N=16 tokens for batch size (k), embedding dimension d=512, number of attention heads e.g., ff_size in hidden states h=32 (this is model-specific notation that likely stands for the feedforward network's input feature map size but can be interpreted as a simplified way to represent overall memory and computation demands).<br><br>The base Transformer uses 512-dimensional embeddings, has an encoder/decoder with respective dimensions of d=512 and h=32. Since we don't have the exact details about attention mechanisms or feedforward computations (ff_size), let’s assume a ff_size similar to 4 times smaller than 'h', which is common in literature, so ff_size = 8.<br><br>To get an estimate of FLOPs per training step for just the self-attention mechanism component: N * d^2 (for one head) + N*d^2*(D/H)^2 to compute attention scores and then output projection which equals in total, about half as many operations since we're considering a simplified view of feedforward computation.<br><br>However, without specific data on the number of tokens 'N', actual sequence length or GPU utilization rates during training (which are not provided), this remains an estimate grounded more in general Transformer architecture and standard GPU capabilities than precise figures from your source text. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The question seems to be based on a misunderstanding of context or numbers provided in the original text, as no specific "GLUE" dataset scores are mentioned for any task named QQP. Instead, there's mention of BERT achieving an absolute accuracy improvement and MNLI score improvements over previous benchmarks. However, without explicit information regarding GLUE's scoring system or how to interpret these results with respect to the specific "GLUE" dataset as a whole for tasks like Quora Question Pairs (QQP), we cannot accurately report BERT-LARGE’s QQP score from this context. <br><br>The answer, therefore: The provided text does not contain information about the GLUE benchmark's specific scores achieved by models on the QQP task; thus such a figure could not be given based solely on these details. | The provided context does not specify an exact QQP score for BERT-LARGE on the GLUE benchmark; it only indicates that higher F1 scores are reported. To find this information, one would need to refer directly to Table 6 mentioned in the text or access detailed documentation of our experiment results and methodology if available elsewhere. | The exact numeric value for the QQP (Quick, Question Answering) score obtained by BERT-LARGE on the GLUE benchmark isn't explicitly provided in the given context. However, we can infer from Table 2 and Table 3 that it outperforms other systems listed which have scores of approximately:<br><br>OpenAI GPT (Quick): Not directly specified for QQP but OpenAI's general performance on GLUE benchmark was close to BERT-LARGE in some tasks.<br>BiLSTM+ELMo+Attn (Quick): 76.4/76.1 indicates a lower score than that of BERT-LARGE for QQP, although exact numbers aren't provided specifically for QQP but can be assumed to perform similarly on other tasks as well since they share the same methodology and data set (GLUE).<br>BERT Single Layer: 71.2/83.1 suggests a good score across different datasets including Quick, although it is not directly stated which specific dataset corresponds with these numbers for QQP in particular case here; nonetheless, we see that BERT consistently outperforms the baseline systems mentioned by significant margins on various GLUE tasks overall.<br><br>In summary, while there isn't a direct score provided for BERT-LARGE specifically on Quick (as it relates to QQP), its performance is implied to be quite high based on how often and significantly it outperforms the listed systems across other datasets within GLUE as well. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The exact match (EM) scores are not provided in the context for individual components like Encoder or Retriever separately; however, it mentions that after ablating critical components of REALM and reporting end-to-end results as well as EM before any fine-tuning, there is a significant improvement. Specifically, by retrieving 5 documents instead of only 20, the system achieves its overall best performance on NaturalQuestions Open with an increase in accuracy from baseline ORQA scores when not resetting parameters to their initial states and feeding them into fine-tuning post REALM pre-training. The exact match score for such a retrieval situation isn't directly stated, thus the answer would be 'not provided.' | The provided context in the instructions is missing direct information about an "Exact Match" (EM) score achieved by REALM on NaturalQuestions-Open. Therefore, I cannot provide this specific numerical answer based solenerly on the given text and say that it is not mentioned. To find out the Exact Match score for REALM on this dataset in a real scenario, one would typically refer to an experimental results section of relevant research or documentation where such performance metrics are reported. | REALM achieves an EM score of 76.8% for the task NaturalQuestions-Open as reported in Table 1. However, this number should be understood within a hypothetical context where these numbers do not exist in reality since they are invented benchmarks mentioned at the beginning of the report summary provided by "viXra." |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| 44.5 EM on Natural Questions [52] | 48.1% | 45.2 |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The Transformer base model uses 8 attention heads with each having a dimension of d=64 after dividing by h (where h is also equal to 8). This results in an effective multi-headed attention mechanism within the single-layer encoder and decoder. | The Transformer base model uses 8 parallel attention layers (h=8) with each head having a dimension of d=64 for both keys, queries, and values. The total number of parameters in this encoder is 100M. | The baseline Transformer uses 12 attention heads with each head having a dimensionality of 768, resulting in a total hidden size (model dimension) for this configuration being 8,960. This is part of the larger BERTBASE model which has overall parameters of 110 million and consists of L=12 layers, H=768 attention heads with dimensionality A=12 each, amounting to a total parameter count of 340 million when scaled up for the much larger BERT large (BertLARGE) model. |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The Transformer base model uses a feed-forward neural network with dimensions (1024, 4096). | The dimension used by the Transformer base model for its fully connected feed-forward networks is d = 512. This dimensionality applies to both input and output embeddings as well as internal representations within each layer of the encoder, decoder, and self-attention mechanism throughout the architecture. | The feed-forward network in the Transformer base model uses dimensions of 4096 each, as indicated by "256 (d_model)" followed by another number that is not explicitly mentioned for this specific layer. However, considering typical usage patterns where a smaller dimension might be chosen for bottleneck layers and larger ones before or after it in the feed-forward network of transformers, one could infer dimensions around 4096 are likely used within the multi-layered structure. This inference is based on provided context that does not specify individual layer dimensions but discusses overall model size (256M parameters). |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The BERT-LARGE model has a hidden size (A) of 16 and uses 1024 self-attention heads. It also contains approximately 340 million parameters in total for the encoder, as stated with "BASE A=16, Total Parameters=340M." | The Hidden Size (H) for BERT-LARGE is 1024, and it has 16 Attention Heads. The total parameter count also aligns with this larger model being at 340M parameters in size as described previously. | The BERT LARGE model has a hidden size (H) of 1024 and uses 16 attention heads (A=16). |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The square root of the inverse number of dimensions (sqrt(1/d)) as a scaling factor is applied to the dot products before applying the softmax function in Scaled Dot-Product Attention. This counteracts diminishing gradients for large values of 'k' when the product dimension grows larger, facilitating stable training dynamics. | The square root of d (√d). This is done to prevent the softmax function's gradients from becoming extremely small when the dot products grow large in magnitude, especially for larger values of k and d. The scaling factor specifically mentioned in this context relates directly to dealing with the extreme gradient issue during backpropagation within deep learning models employing attention mechanisms like Transformer networks. | The square root of the dimension d (√d) as a scaling factor is applied to the dot products before the softmax function in Scaled Dot-Product Attention. This step helps prevent the softmax function from having extremely small gradients when dealing with large magnitude dot products, which can occur for larger values of k or dimensionality d. The specific formula used in this context involves dividing each dot product by √d prior to applying the softmax function. |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| REALM computes this probability by modeling it as a distribution p(z \| x), which is sampled during pre-training and fine-tuning. The specific calculation for how REALM derives the retrieval probabilities isn't directly provided in the context, but based on common practices of similar models like BERT, this probability likely reflects relevance scores that document z has with input x before any fine-tuning is applied to improve it further. | REALM computes the probability p(z \| x) using a sample from an unsupervised pre-training corpus. The specific method used is not detailed in the provided context, but it typically involves estimating this conditional distribution as part of REALM's parameter learning process during retrieval-augmented language modeling tasks such as masked language modeling and Open-QA fine-tuning. | REALM computes the probability of retrieving a specific document z, given an input x, using what is termed as p(z \| x). This computation models the likelihood that document z would be retrieved by treating it as a latent variable. It's important to note that this process does not directly compute probabilities but rather provides expectations for retrieval outcomes during pre-training phases, which are later used in further computations like p(y \| x). |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| The context provided gives a detailed comparison between two systems, RAG and REALM. However, the specific performance metrics of these models on the NaturalQuestions-Open benchmark are not directly stated in the given text excerpts from different research papers or documents. To accurately answer this question about their comparative performance on that particular dataset would require additional information specifically mentioning results from experiments conducted with both systems on NaturalQuestions Open, which is absent within these contexts. Therefore, based on the provided texts alone, we do not have sufficient information to compare RAG and REALM' fairness scores directly for this specific task.<br> | RAG performs better than REALM in the benchmarks provided, with performance metrics such as Rouge-L and F1 scores being higher for RAG. However, it is not explicitly stated which metric or context to use when comparing their performances on NaturalQuestions Open specifically. Given that both systems seem effective according to available data snippets but without concrete comparative figures in the provided context for this specific setting alone, we cannot definitively conclude how they stack up against each other solely based on these details. To accurately compare RAG and REALM's performances directly from NaturalQuestions Open benchmarking results, one would need to reference detailed scores or findings that specifically address their performance in those tests separately rather than inferring it indirectly through broader statements about the systems’ capabilities as mentioned elsewhere. Therefore, I can only say based on provided information they seem competitive without specifying which is better for NaturalQuestions Open. | RAG-Token outperforms REALM with a score of 89.6% against REALM's performance at the time, which was not explicitly stated in the provided context for all benchmarks and tasks; however, it is suggested that RAG models are competitive or on par across various domains since both versions perform favorably when compared to BART based on Q-BLEU metrics. |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| Bert-Base has 7 and Bert-Large has 5, so BERT-Base has 2 more attention heads than a baseline single-headed or non-Transformer based model. However, since we are comparing to the base Transformer mentioned in Vaswani et al.'s original paper which uses d = 64 / h and typically employs one head (when not explicitly mentioning multiple), BERT'sem attention heads could be considered as having substantially more complexity per computationally independent unit, but we can say it has at least two additional full-fledged multi-headed units over a single traditional Transformer. | Bert (base) has 12 attention heads while a typical encoder might only use one or two, thus having potentially up to twelve times as many. However, without specific information about what "typical" entails in this context and considering that the Transformer's self-attention is not strictly limited by layer depth but rather allowed for extension via additional layers (as seen with BERT), we cannot calculate an exact multiple difference between them based on attention heads alone. | BERT (L=12, H=768, A=12) has 12 attention heads while standard models like Al-Rfou et al. (2018)'s largest found in the literature have only 2 attention heads each with a total of 235M parameters including an encoder and decoder both having d = d / h = 64 size, which would imply it has fewer than BERT-BASE's head count. Therefore, if we consider just these two models for comparison on the basis of number of attention heads alone (assuming no other model with a different structure is compared), then theoretically, BERT could have an unlimited amount more "heads" because standard Transformer sizes are not specified as having 12 or fewer. However, if we take into account that each head in the base models has A=8 heads (since their total attention mechanism size with two sets of encoder and decoder is divided by four due to d / h = 64), then BERT-BASE would have exactly twice as many because it has a single model without this division, but still within its architecture. So we can say that in terms of the number of "heads" or parallel attention mechanisms provided for computation at any given layer (considering only these two models and ignoring potential differences due to other architectural aspects), BERT-BASE provides twice as many - 12 heads, while traditional Transformer foundations like Al-Rfou et al. provide a head count of A=8 divided by both encoder and decoder layers (4 attention mechanisms per layer). |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| all-MiniLM-L6-v2 | bge-small-en | e5-small |
|---|---|---|
| Both systems demonstrate strong performance on the Natural Questions dataset, but specific comparison scores are not directly provided in the context. To accurately determine how RAG-Sequence compares to REALM on WebQuestions specifically for this task, one would need additional data that is not present within the given text. It's suggested however that both models perform well and even though details about their performance differences or similarities are missing from the context provided, they seem competitive based on overall scores mentioned in relation to other benchmarks like TriviaQA and Natural Questions for different systems. | The context provided indicates that Lewis et al. (2020) created retrieval-augmented generation models using BART and DPR, which they evaluated against the benchmark of REALM by Guu et al. While exact numbers or results for RAG-Sequence on WebQuestions relative to REALM are not directly provided in the context above, it is mentioned that "RAG approaches state-of-the-art model performance," outperforming both BART and non-generative retrieval baselines across various benchmarks. However, a specific comparison with ReaLm on WebQuestions isn't explicitly stated within this provided text; thus, without additional context or data from the original research paper by Lewis et al., we cannot definitively conclude how RAG-Sequence compares to REALM specifically for the task of answering questions using information solely from Wikipedia passages. | The context provided only mentions the performance of these models in various benchmarks for question answering and generation tasks, but it does not include specific comparative results between RAG-Sequence from Lewis et al. (2020) and REALM by Guu et al. (2020) on WebQuestions specifically. Therefore, based on the given information alone, we cannot determine how these two models compare to each other in this particular task. |
