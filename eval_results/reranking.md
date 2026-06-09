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
| The primary reason for selecting `all-MiniLM-L6-v2` as the default is that despite a significant quality gap of approximately 4.4 points, it only resulted in a threefold increase in latency compared to `bge-base-en-v1.5`. This balance between performance and computational cost makes it more suitable for local single-user pipelines where maintaining low latency is crucial. | The selection of `all-MiniLM-L6-v2` as the default was primarily due to its superior quality on top-5 exact match (EM) score, which is a measure for retrieval accuracy where higher scores indicate better performance. Specifically, while there was only a slight difference in EM with `bge-base-en-v1.5` scoring 0.783 compared to `all-MiniLM-L6-v2` at 0.787 on the evaluation set, this small margin did not justify switching models given that doing so would increase latency by approximately threefold from an average of about 21ms for `bge-base-en-v1.5` to around 64ms for `all-MiniLM-L6-v2`. Hence, the decision favored maintaining a balance between quality and efficiency in latency times, favoring local single-user pipelines where immediate response is crucial but with minimal sacrifice on overall performance metrics such as EM scores. |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| Adding 'Source:' before each passage reduced hallucinations on the eval set from 11/47 (23%) to 3/47 (6%). | The addition of explicit source attribution ('Source: {source}') before each passage in the RAG prompt template reduced hallucinations on the eval set from 11/47 instances (23%) to just 3/47 instances (6%). This represents a significant decrease, indicating that specifying sources can help anchor the context and reduce model misattributions or ignoring of provided information. |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| FAISS IVF becomes worthwhile above ~100,000 chunks of text according to the context provided. | Over ~100,000 chunks of context data. |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| no rerank | rerank |
|---|---|
| The context provided suggests that NQ questions tend to be longer and more paraphrastic, which results in a lower lexical overlap with answer passages. BM25 relies on word overlap as part of its retrieval strategy; hence it struggles compared to DPR, which uses dense passage retrieval techniques better suited for the characteristics of NQ questions where lexical cues are less prominent but context and semantics play a larger role. | The gap between the performance of BM25 and DPR (Dense Passage Retrieval) suggests that NQ questions are longer, more paraphrastic, and have lower lexical overlap with their corresponding answer passages. Since dense retrieval systems like DPR rely on fine-grained document matching to identify relevant information for answering a question, the characteristics of queries in which BM25 falls short indicate challenges that might not be present or as pronounced in TriviaQA questions.<br><br>In essence, NQ's open and variable nature means there is less direct lexical cues available within its passages for answer retrieval systems like BM25 to exploit effectively. DPR uses a bi-encoder approach with richer contextual embeddings from language models that likely capture deeper semantic connections between the questions and answers, thus performing better on such diverse datasets as NQ by identifying relevant information through more sophisticated understanding of paraphrastic content where lexical overlap is minimal.<br><br>On TriviaQA, despite being an open-domain QA dataset with facts that can be challenging to retrieve due to their less frequent nature and reliance on external knowledge sources like Wikipedia dumps or the internet at large scale (with approximately 21 million passages), BM25 might perform better because it doesn't heavily rely on lexical cues, potentially benefiting from higher overlap with answer texts. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| no rerank | rerank |
|---|---|
| BART-large. | BART (Bidirectional and Auto-Regressive Transformer) |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| The context provided does not include specific information about a Top-5 EM (Exact Match) score achieved by the model named `all-MiniLM-L6-v2`. Therefore, based on this text alone, I do not have the answer to provide. To find out its performance, one would need additional data or context outside of what is provided here. | The context provided earlier mentions that the model `all-MiniLM-L6-v2` achieves a Top-5 EM of **0.743** on their evaluation set for NLP/LLM paper corpus when using bm_token as the retriever strategy, with this score being associated specifically to RAG (Retrieval Augmented Generation) models and not just any MiniLM configuration or L6 variant. Thus, if we are strictly following information about `all-MiniLM-L6-v2` in relation to a standard evaluation without mention of the specific augmentation strategy like 'RAG', it's challenging to provide an exact match score directly from this text because its results pertain only when used within that context. However, since no different EM scores for `all-MiniLM-L6-v2` are provided in relation to standard benchmark evaluation outside of the RAG setup with bm_token retriever strategy or without specifying a particular augmentation method like 'RAG', we cannot definitively answer this question. |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| BERT Single system performs with an F1 score of 82.3% for Top Leaderboard Systems as reported on December 10th, 2018. While this data doesn't explicitly mention a top-5 EM (Exact Match) benchmark within the provided context, based on inference from the information given and common performance metrics in natural language processing tasks like those presented by leaderboards such as GlueBenchmark or SQuAD for retrieval systems, BERT is likely to achieve high scores. However, since we are specifically asked about top-5 EM without direct data points provided within this context (and assuming a standard of benchmarks wherein the highest score isn't necessarily denoted with F1 but rather exact matches), one may infer from similar performance patterns and typical outcomes that BERT models would excel in such tasks. Therefore, although an exact number for top-5 EM is not stated explicitly here, we can reasonably speculate that it will be high based on the overall positive results of BERT as reported across various benchmarks mentioned elsewhere within this context document or commonly known performance metrics of state-of-the-art models at their peak. | The RAG Token retrieval backend achieves the highest Top-5 Exact Match (EM) score of 0.743 on a fixed evaluation set covering the NLP/LLM paper corpus for dense retrievals using sine and cosine functions as positional encodings with d . model dimensionality equal to 2048 in BERT-style Transformers, according to Table 1 which is discussed under "Embeddings." |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| IndexFlatIP has a query latency of 34 ms, while IndexIVF (with nlist=32) and its index are built in just 1 ms. However, it's important to note that the provided context does not explicitly mention if this is measured for both backends or solely for FAISS with IndexIVF since using different indexing types was part of a comparative experiment between NumPy cosine embeddings and FAISS based approaches which also included their respective latencies. | - IndexFlatIP has a query latency of 4 ms.<br><br>- IndexIVF, specifically when using `nlist=32`, also trades EM points for faster speed and thus shares the same query latency of 4 ms with IndexFlatIP. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| no rerank | rerank |
|---|---|
| RAG-Sequence achieves an Exact Match score of 41.5% on the Natural Questions (NQ) dataset according to Table 2 in the main results section, which indicates its performance when using Dense Passage Retrieval (DPR). Note that this is not a direct answer but rather information inferred from context; retriever models and NLP benchmarking are common topics. However, if you're asking about RAG-Sequence's Exact Match score specifically without the influence of other methods like DPR as mentioned in your question, then it achieves an overall Exact Match (EM) score of 83.5% on TriviaQA and is not explicitly stated for NQ alone in this specific context provided. Please verify with additional sources if necessary. | RAG-Sequence achieves a score of 44.0 EM on Natural Questions according to Table 1 from the provided context. |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| no rerank | rerank |
|---|---|
| DPR achieves a higher Exact Match (EM) of 44.2% on the NQ dataset when using RAG as the generation model, which is an improvement over its baseline EM performance without this technique detailed in other parts of the context provided. However, there's no direct comparison given for DPR with top-5 vs top-10 retrieval specifically within dense or BM25 systems from NQ to give a precise answer on how their performances differ at these two points directly according to the text above. | The context provided above does not include specific details about how many instances of questions fall into these categories, nor the exact values for RAG's and REALM' end performance. Therefore, I cannot directly answer your question based on this text alone without assuming additional information from external sources or data that is not presented in the given context. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| no rerank | rerank |
|---|---|
| System Dev Test - BERT (Single) | The RAG-Token and RAG-Sequence models achieve the same highest score on TriviaQA, both reaching an Exact Match (EM) of 68.2 as per the context provided. |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| Final configuration of chunking parameters used in Tiktoken accumulation method is as follows:<br>- CHUNK_MAX_TOKENS = 128   # changed from the initial 256 due to empirical evaluation indicating better precision at this token budget.<br>- CHUNK_OVERLAP    = 50    # setting overlap between consecutive chunks for maintaining context continuity across chunk boundaries; higher values did not further improve recall after a certain point of increase in the value, hence chosen as is from empirical results obtained during testing phase which showed no significant improvement beyond this overlapping size. | The final `CHUNK_MAX_TOKENS` value is set to 128, as it was found empirically that at this token budget the top-5 EM improved from 0.698 (at a max of 256 tokens) up to 0.743 when reduced down to 128 tokens for corpus size around ~4,200 chunks total in V2 after an evaluation run that took place on **January 15th** and another one where the `CHUNK_MAX_TOKENS` were changed which also happened simultaneously. The final `CHUNK_OVERLAP` value is set to 50, as it was determined through empirical testing that higher values do not improve recall beyond this overlap point for chunks of approximately 128 tokens in size on a corpus with about 4,200 total chunks. |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| no rerank | rerank |
|---|---|
| The context provided does not specify a particular percentage for the "token overlap" directly; therefore, I cannot provide an exact number from the given text as it stands incomplete and possibly missing information. However, there is mention of "[LM masking] with a uniform masking rate of 15%," which could imply that this method applies to some form of token processing or selection within chunk generation rather than direct overlap between chunks themselves. If you were asking about the percentage used in another process related to tokens not detailed here, please provide additional context so I can give an accurate answer. | The current chunking configuration uses a uniform masking rate of 15% for LM masking after WordPiece tokenization, which implies that there is an overlap of 85% tokens from the original text. However, this does not directly indicate what percentage of overlapping word pieces might be included within those chunks since partial word pieces are considered without special consideration in the configuration described. |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| no rerank | rerank |
|---|---|
| The key distinction lies in how they generate responses during sequence generation tasks. The RAG-Token model can draw different latent documents for each target token, allowing it to choose content from several relevant documents when producing an answer. In contrast, the RAG-Sequence Model uses a single retrieved document as one large latent variable and marginalizes over this entire 'document' to generate sequences, treating them similarly to how BERT processes input tokens with shared context across different parts of the text sequence (e.g., [CLS] token). | The primary difference lies in how they utilize retrieved documents for generation. The RAG-Token model draws a different latent document for each target token during decoding, which allows it to select content from several relevant documents when producing an answer. In contrast, the RAG-Sequence uses all top-k retrieved articles as one single input and treats them collectively while generating complete sequences. Thus, both models use retrieval components but differ in their approach towards utilizing document information for text generation tasks like question answering or JeoptermQGen. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| no rerank | rerank |
|---|---|
| The Retrieval Component (p(z\|x)) used in the RAG model, as mentioned within a note indicating that it uses DPR's retriever initialized with documents from NQ. This is clarified by stating "Rag-Sequence and Rag-Token are equivalent" when considering target class as one element sequence or token respectively – emphasizing they both utilize the same underlying technology, which in this case would be a bi-encoder trained on Natural Questions (NQ). The exact name of DPR is not provided within the context. | The RAG model uses a bi-encoder based on DPR (Dense Passage Retrieval) as its retriever. |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| no rerank | rerank |
|---|---|
| BERT uses MASK and UNMASK strategies as its two pre-training tasks, with different probabilities of using each strategy during MLM (Masked Language Model) training. The left part of the table represents these proportions where BERT might use either the masking or unmasking token to replace a word in a sentence for input into the model's transformer layers. | Masked Language Model (MLM) and Next Sentence Prediction (NSP). The MLM task involves masking some percentage of the input tokens at random and then predicting those masked tokens. This encourages the model to understand context from both left and right sides of a sentence simultaneously due to its bidirectional nature, which is not possible in traditional one-direction models. NSP helps improve BERT's understanding over long sequences by learning whether two segments come from the same document or paragraph during fine-tuning on specific tasks that benefit from this property. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| no rerank | rerank |
|---|---|
| 15% of input tokens are masked in BERT's MLM objective. | 15% |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| no rerank | rerank |
|---|---|
| REALM uses a salient span masking scheme that focuses on tokens such as "United Kingdom" or specific dates like “July 1969”. This method ensures the model learns to retrieve examples from documents containing world knowledge, which is crucial since REALM's core strength lies in its ability to use retriever-augmented language models for tasks that require external factual information. | REALM uses salient span masking during pre-training to focus on examples that require world knowledge for prediction. This method is used because some MLM spans only need local context while others demand information beyond the text itself - which could be retrieved from a structured document source such as Wikipedia or BERT's RoBERTa (devlin2019letter). Salient span masking helps REALM to concentrate on learning representations that are meaningful and require understanding of world knowledge, thereby improving performance. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| 1. Self-attention allows the model to extrapolate to sequence lengths longer than those encountered during training, unlike recurrent layers which struggle with long sequences due to issues like vanishing gradients and difficulties in parallelization on modern hardware architectures such as GPUs or TPUs.  <br>2. In terms of computational complexity, self-attention is faster for the most common case where sequence length n is smaller than representation dimensionality d—this often occurs with sentence representations used in machine translations like word-piece and byte-pair encodings. Recurrent layers require O(n) sequential operations to connect any two positions while a self-attention layer requires constant time regardless of the input size, which makes it more efficient for longer sequences or when dealing with large batches during inference/testing on parallel computing devices.  <br>3. Self-attention could yield models that are easier to interpret since attention distributions can highlight what different parts of inputs contribute towards decisions made by a model—an aspect not as readily available in RNNs where sequential dependencies make it hard to pinpoint specific cause and effect relationships within the input data during backpropagation. | 1. Self-attention allows every position in a sequence to attend to all positions, which is not possible with standard RNNs that have shorter dependencies due to limited sequential operations required by the model architecture (O(n) for each operation). This makes self-attention more efficient and capable of learning longer-range dependencies.<br><br>2. Self-attention layers are faster than recurrent ones, especially as sequence length increases beyond typical training lengths in NLP tasks because they don't require sequential computation across time steps—a limitation inherent to RNNs (O(n) operations). <br><br>3. The Transformer model with self-attention can be trained significantly faster than models based on recurrent or convolutional layers, which is a practical benefit in terms of computational resources and training times required for large datasets such as WMT 2014 English-German dataset used by the authors. |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| ConvS2S Ensemble achieved a BLEU score of 26.36 on the WMT 2014 English-to-French translation task. | According to the context provided, ConvS2S Ensemble achieved a BLEU score of 7.7 for the WMT 2014 English-to-French translation task. However, it is worth noting that this data point seems disconnected from Table 3 where scores are mentioned in relation to Transformer models (both big and base). Therefore, I cannot confirm if ConvS2S Ensemble's score was explicitly stated for the French dataset or even its exact BLEU score. To accurately answer your question based on this context alone would require speculation beyond the information given. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| To estimate the number of Floating Point Operations (FLOPs) used for training, we look at Table 2 under "BLEU Training Cost (FLOPs)" and find that the term associated with Transformer (big) is listed as '41.8'. However, this value does not represent FLOP count but rather BLEU score achieved by the model after its training on English-to-German translation tasks. Therefore, based on the information provided in the context, I cannot calculate or determine the exact number of floating point operations used to train the base Transformer model since that specific metric is not given explicitly for it and instead requires an estimate as described: "We estimate the number of floating point operations by multiplying the training time, ...and 5." Without this explicit information on the actual Floating Point Operations count or a direct way to calculate based solely on provided data like GPU capabilities over specific durations (which have been used for other models), it is not possible to provide an answer. The correct response would be that we cannot determine the FLOPs from the given context as there's insufficient information about the training time and the number of operations per second achievable by each GPU in use, which are essential metrics needed alongside with actual numbers on model configuration (layers, heads, etc.) for this estimate. | The provided context does not directly state the number of floating-point operations (FLOPs) used to train the base Transformer model specifically for English-to-German or English-to-French tasks. However, it mentions that they estimate training costs by multiplying time taken, GPU count, and sustained single-precision FLOP capacity of each GPU:<br><br>"We estimate the number of floating point operations used to train a model by multiplying the training time, the number of GPUs used, and an estimate of the sustained single-precision floating-point capacity of each GPU."<br><br>As we don't have specific numbers for these variables in this context (time taken is 12 hours totaling 4000 steps which would be about 96 minutes or roughly ~8.33 hours, and there are eight P100 GPUs), the actual FLOP count isn't provided directly herein; it can only be estimated with additional data on how many floating-point operations a single P100 performs per second (FPSS).<br><br>Hence, without this information or more detailed context from elsewhere in their work that would allow for such an estimate, I cannot provide the exact FLOP count used to train the base Transformer model. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| no rerank | rerank |
|---|---|
| The question seems to be based on a misunderstanding of context or numbers provided in the original text, as no specific "GLUE" dataset scores are mentioned for any task named QQP. Instead, there's mention of BERT achieving an absolute accuracy improvement and MNLI score improvements over previous benchmarks. However, without explicit information regarding GLUE's scoring system or how to interpret these results with respect to the specific "GLUE" dataset as a whole for tasks like Quora Question Pairs (QQP), we cannot accurately report BERT-LARGE’s QQP score from this context. <br><br>The answer, therefore: The provided text does not contain information about the GLUE benchmark's specific scores achieved by models on the QQP task; thus such a figure could not be given based solely on these details. | The context provided does not include specific information about a QQP (Qualifications Question and Position) score obtained by BERT-LARGE. The scores mentioned in Table 1 correspond to different tasks within the GLUE challenge, but without explicit mention of the QQP task or its associated score for BERT models on that leaderboard as of December 10th, 2018, I cannot provide this information based solely on the provided context. Therefore, my response is: The answer cannot be determined from the given context. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| no rerank | rerank |
|---|---|
| The exact match (EM) scores are not provided in the context for individual components like Encoder or Retriever separately; however, it mentions that after ablating critical components of REALM and reporting end-to-end results as well as EM before any fine-tuning, there is a significant improvement. Specifically, by retrieving 5 documents instead of only 20, the system achieves its overall best performance on NaturalQuestions Open with an increase in accuracy from baseline ORQA scores when not resetting parameters to their initial states and feeding them into fine-tuning post REALM pre-training. The exact match score for such a retrieval situation isn't directly stated, thus the answer would be 'not provided.' | REALM achieves an Exact Match score of not explicitly mentioned in the provided context. However, it is noted that RAG-Sequence reaches a high EM point difference over BM25 by scoring higher than other models with their retrieved documents on NaturalQuestions Open; specifically for NQ where REALM scores 41.5 while DPR scored significantly lower at 26.5 points (though the exact score of 41.5 is attributed to RAG-Sequence). |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| no rerank | rerank |
|---|---|
| 44.5 EM on Natural Questions [52] | Rag-Sequence achieves an Exact Match score of 44.5 on the test split of NaturalQuestions, according to Table 1 reported in the context. This indicates that it has a high level of accuracy when compared against other models or baselines used for this task within the study by Lewis et al., although exact performance figures beyond RAG-Sequence are not provided directly next to NQ results; hence we have no basis from which to compare further improvements if there were any. |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| The Transformer base model uses 8 attention heads with each having a dimension of d=64 after dividing by h (where h is also equal to 8). This results in an effective multi-headed attention mechanism within the single-layer encoder and decoder. | The Transformer base model uses 8 parallel attention layers (heads) with each head having a dimension of d = 64, as per the context given. The total number of parameters for this encoder is not directly mentioned in relation to the size but it's implied that because there are fewer heads and smaller dimensions compared to other configurations, it might result in lower parameter count; however, without explicit figures provided in your text for model sizes corresponding with these numbers of attention layers or head counts. |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| The Transformer base model uses a feed-forward neural network with dimensions (1024, 4096). | The input and output layers are both fed through a position-wise fully connected feed-forward network of dimensionality d = 512. This is indicated in two places within the context provided, specifically at points (3) with dimensions "6 512" referring to model size parameters including hidden dimension 'd' for attention heads and encoder/decoder layers respectively, as well as point (4) which lists feed-forward network features directly following the dimensionality. |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| no rerank | rerank |
|---|---|
| The BERT-LARGE model has a hidden size (A) of 16 and uses 1024 self-attention heads. It also contains approximately 340 million parameters in total for the encoder, as stated with "BASE A=16, Total Parameters=340M." | Hidden Size (H): 1024<br>Number of Attention Heads (A): 16 |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| The square root of the inverse number of dimensions (sqrt(1/d)) as a scaling factor is applied to the dot products before applying the softmax function in Scaled Dot-Product Attention. This counteracts diminishing gradients for large values of 'k' when the product dimension grows larger, facilitating stable training dynamics. | The square root of the dimensionality \( \sqrt{d} \) |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| no rerank | rerank |
|---|---|
| REALM computes this probability by modeling it as a distribution p(z \| x), which is sampled during pre-training and fine-tuning. The specific calculation for how REALM derives the retrieval probabilities isn't directly provided in the context, but based on common practices of similar models like BERT, this probability likely reflects relevance scores that document z has with input x before any fine-tuning is applied to improve it further. | REALM computes this likelihood by modeling it as p(z \| x), which is considered a latent variable and marginalized over all possible documents to calculate the overall likelihood of generating y. The computation involves taking into account both retrieval performance (relevance score) f(x, z) for document z given input x and updating this probability based on whether or not using that particular retrieved document results in better prediction accuracy than expected from random sampling alone. |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| no rerank | rerank |
|---|---|
| The context provided gives a detailed comparison between two systems, RAG and REALM. However, the specific performance metrics of these models on the NaturalQuestions-Open benchmark are not directly stated in the given text excerpts from different research papers or documents. To accurately answer this question about their comparative performance on that particular dataset would require additional information specifically mentioning results from experiments conducted with both systems on NaturalQuestions Open, which is absent within these contexts. Therefore, based on the provided texts alone, we do not have sufficient information to compare RAG and REALM' fairness scores directly for this specific task.<br> | Table 3 in the provided context indicates that after ablating critical components of REALM, specifically related to retrieval quality and language model pre-training steps used by RAG during its own training phase for NQ dataset (using DPR's retriever), their performance becomes nearly equivalent. This suggests that despite having different methodologies—one being non-parametric with a bi-encoder using documents as memory, while the other is parametric focusing on language model pre-training—both RAG and REALM are strong contenders in this specific task for NaturalQuestions Open dataset when their retriever components' performance aligns closely. |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| no rerank | rerank |
|---|---|
| Bert-Base has 7 and Bert-Large has 5, so BERT-Base has 2 more attention heads than a baseline single-headed or non-Transformer based model. However, since we are comparing to the base Transformer mentioned in Vaswani et al.'s original paper which uses d = 64 / h and typically employs one head (when not explicitly mentioning multiple), BERT'sem attention heads could be considered as having substantially more complexity per computationally independent unit, but we can say it has at least two additional full-fledged multi-headed units over a single traditional Transformer. | The provided context doesn't specify an exact number of additional attention heads that BERT-BASE has over a "base" Transformer model. However, it is mentioned in Table 3 (not directly included in our current text but referenced) that increasing the number of attention heads can lead to better performance while keeping computation constant using dot product instead of multi-head self-attention mechanisms. This implies there's an increase from a single head mechanism seen in simpler models, which is standard for many Transformer variants before BERT was introduced; but without exact figures or reference points given, we cannot determine the precise number of additional heads used by BERT-BASE compared to unspecified "base" model. To answer this question accurately with numbers would require consulting Table 3 directly from Vaswani et al., as alluded in our context. |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| no rerank | rerank |
|---|---|
| Both systems demonstrate strong performance on the Natural Questions dataset, but specific comparison scores are not directly provided in the context. To accurately determine how RAG-Sequence compares to REALM on WebQuestions specifically for this task, one would need additional data that is not present within the given text. It's suggested however that both models perform well and even though details about their performance differences or similarities are missing from the context provided, they seem competitive based on overall scores mentioned in relation to other benchmarks like TriviaQA and Natural Questions for different systems. | The context provided doesn't include specific comparison results between RAG-Sequence and REALM on the WebQuestions dataset. As such, I cannot provide a direct answer from the given information alone. To obtain this data, one would need to refer directly to Table 1 of Lewis et al. (2020) or related experimental findings where these two models were evaluated head-to-head on that specific task. |
