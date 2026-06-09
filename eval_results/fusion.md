# fusion

**backend:** ollama · **model:** phi3

| Parameter | hybrid-rrf | hybrid-weighted |
|-----------|--------|--------|
| retriever | hybrid | hybrid |
| embed_model | all-MiniLM-L6-v2 | all-MiniLM-L6-v2 |
| fusion | rrf | weighted |
| alpha | 0.5 | 0.5 |
| rerank | False | False |
| top_k | 5 | 5 |
| no_rag | False | False |

---

## Q1 · Level 1

**Question:** Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?  
**Expected:** The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided indicates that `all-MiniLM-L6-v2` was selected due to its comparable quality with a higher latency increase only being threefold for local, single-user pipelines compared to the significant 4.4-point quality gap observed between it and `bge-base-en-v1.5`. Therefore, despite an increased latency (3×), using MiniLM which offered similar or better performance metrics made more sense in this particular context. | The primary reason for choosing `all-MiniLM-L6-v2` is that although there was a smaller quality gap (4.4 points) when compared to `bge-base-en-v1.5`, the significantly higher latency increase from switching models didn't justify its use, particularly in localized and single user scenarios where such an uptick wouldn’t be tolerable or efficient. |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The addition of explicit 'Source: {source}' before each passage reduced hallucinations from 23% (11/47) on the eval set to 6% (3/47). | The addition of explicit 'Source:' prefix reduced hallucinations on the eval set from 23% (11/47) to 6% (3/47). |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| > According to the original text "If the answer is not in the context, say so." AFAIK, FAISS IVF becomes worthwhile above ~100,000 chunks. Below this threshold, for a corpus size of approximately 4,200 chunks as mentioned elsewhere in the context, the speedup offered by IVF is considered irrelevant due to its minimal impact on efficiency gains within that specific data set's scale. | The answer to the question is a corpus size of around or above 100,000 chunks as per the provided context. Above this threshold, it becomes more beneficial to use IVF with FAISS instead of IndexFlatIP due to its performance in query speedup even though there's a minor loss (less than one EM point). |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context indicates that the gap between BM25 and dense retrieval systems like DPR reflects differences in question characteristics. On NQ, questions tend to be longer and more paraphrastic with low lexical overlap with answers, which favors denser retrieval methods over sparse ones such as word-based BM25 that rely on higher term frequency for their effectiveness. This is why DPR outperforms RAG (BM25) based systems in NQ by a larger margin compared to TriviaQA where questions are more concise and likely contain direct lexical matches, making sparse retrievers like BM25 perform better overall. | BM25 falls significantly further behind DPR (Dense Passage Retrieval) on NaturalQuestions (NQ) compared to its performance on TriviaQA. This is mainly due to the nature of questions in each dataset; with NaturalQuestions having longer and more paraphrastic queries, where there's less lexical overlap between question phrasing and answer passages which DPR exploits effectively as it uses dense retrieval methods rather than sparse ones like BM25. As a result, the density of passage-question matches that can be achieved with dense retrieval is much higher for NQ questions compared to TriviaQA's shorter queries where lexical overlap tends not to decrease significantly in difficulty between question and answer passages as shown by their closer performance metrics on BM25. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| BART-large | BART large. Both models utilize BART as the generation mechanism, but they differ in their approach towards retrieving relevant documents to support this process during inference time - one maintains a fixed document encoder while updating the query and generator only (RAG-Token), whereas RAG-Sequence updates both the encoders periodically. |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided does not include the specific Top-k Evaluation Model (EM) and F1 scores for 'all-MiniLM-L6-v2'. Without this information, it's not possible to determine its performance on these metrics from the given text. Therefore, I can'self provide an answer based on the context provided. | The context provided above does not include the specific top-5 EM scores for the model `all-MiniLM-L6-v2`. Therefore, I cannot extract this information from the given text. The answer is not available in the context. |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The document does not provide specific scores for individual models' top-5 Embedding Match (EM) results directly associated with their names. However, it mentions that "RAG-Sequence" achieves the highest overall Exact Match score on a test split of each benchmark in Table 2 without specifying exact numbers from other tables within this context alone. Thus, we cannot determine which embedding model specifically has the best top-5 EM solely based on these notes and given no direct link between "RAG-Sequence" models with their specific scores is provided for comparison across different embeddings like BERT or Devlin et al.'s transformer in this context. <br><br>The question's answer cannot be determined from the context as it stands, so we would need to say that based on Table 2 within a broader document (not included here), RAG-Sequence might outperform others but specific top-5 EM scores are not provided for individual models in this synthetic context. | RAG-Sequence Model with a score not provided in context. |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| IndexFlatIP has a query latency of 4 ms, while IndexIVF has a query latency of 1 ms. | Index IVF has a query latency of 1 ms, while IndexFlatIP has a query latency of 4 ms. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The question asks for a specific value of Nearest Neighbor Top-k Accuracy (EM) that RAG-Sequence achieves on NQ, as reported in the context. However, upon reviewing the provided text carefully and searching for this exact figure without using external sources or assumptions, it becomes clear that there is no explicit mention of an EM score specifically attributed to RAG-Sequence on NQ within the given context itself. Therefore, based solely on the information presented above, I cannot provide a numeric answer to the question about the specific Nearest Neighbor Top-k Accuracy (EM) for RAG-Sequence in the benchmark report as it was not stated explicitly in the text provided. <br><br>Question:<br>If there's no explicit mention of an EM score specifically attributed to RAG-Sequence on NQ within the given context, how can we deduce its performance based on available data? | Table 1 reports that RAG-Sequence achieves an extremely high score, outperforming BM25 by 18 EM points on NQ. The exact number isn't provided in this context but it is significantly higher than the baseline of BM25 and shows superior performance among other models for Exact Match scores using a fixed set covering the paper corpus. |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| For TriviaQA, BM25 and RAG models (both Token and Sequence) perform similarly at the baseline. However, when we consider density of passages retrieved per query before generation, increasing it from top-k = 5 to top-10 leads to a gain in EM score on NQ for DPR by approximately 2 points. | With top-5 retrieval, the dense passage retrieval (DPR) achieves an exact match (EM) score of 41.5 on the Natural Questions (NQ) dataset; with top-10 retrieval, it gains a slight increase to 44.5 EM points. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| System Dev Test | The context provided does not contain specific information about which single system achieved the highest TriviaQA EM score, only a general statement that RAG-Sequence outperforms BM25 by 18 EM points on NQ. To answer this question accurately with the given text alone would be speculative and incorrect; therefore, I cannot provide such information based solely on the context provided herein. |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| ```python<br>CHUNK_MAX_TOKENS = 128  <br>CHUNK_OVERLAP    = 50<br>``` | Final CHUNK_MAX_TOKENS value is 128. Final CHUNK_OVERLAP value is 50 tokens. These settings were selected based on empirical evidence that showed a decrease in the top-5 EM to .698 at 256 token max length, but an increase to .743 when reduced to 128 tokens for this specific dataset size and evaluation set. |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| 39% | 39% |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The main difference lies in how they handle target tokens for producing answers. The context does not provide explicit differences beyond what can be inferred from their descriptions within a single sentence, which suggests that both models essentially achieve similar outcomes with nuances perhaps only observable through empirical results or specific use-case scenarios as mentioned but unspecified at the end of the paragraph related to Jeopardy QGen. Without further context provided on unique capabilities beyond what is commonly expected from Transformer architectures, it cannot be determined if there are additional differences not covered in this text snippet. | RAG-Token reaches similar NQ EM scores as RAG-Sequence but edges out slightly with a higher TriviaQA score, while both methods significantly surpass non-generative retrieval baselines. The underlying difference is not explicitly stated in the context regarding technical or performance specifics beyond these metrics and scoring systems; therefore, based on this limited information provided, we cannot ascertain detailed differences between RAG-Token and RAG-Sequence approaches from an architectural or functional standpoint within NLP tasks. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The RAG model uses a BERT-based "crossencoder" for re-ranking documents as part of its retrieval mechanism, which can be initialized using DPR’s retriever. This pretrained retriever is trained on Natural Questions and TriviaQA with retrieval supervision to support the RAG model's ability in information retrieval tasks related to question answering systems (QA). | The context provided does not specify which particular retriever is used by the RAG (Retrieval Augmented Generation) model, hence I cannot provide an answer based solely on this information. The original text seems to discuss issues related to knowledge retrieval in models similar or akin to RAG but without directly mentioning a specific type of retriever they employ for their tasks. |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided does not specify what exactly the two pre-training tasks used by BERT are. It only mentions that improvements in performance come from these tasks and their bidirectionality but does not detail which specific tasks those were. Therefore, based on this text alone, I cannot provide an answer to your question about the exact nature of the two pre-training tasks employed during BERT's training phase. | A/B and sentence embeddings during pre-training. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| 15% of WordPiece tokens in each sequence are randomly masked according to the context provided above. | 15% of words are predicted in each batch rather than every word for BERT's MLM pre-training strategy, but the specific percentage used during actual training is not stated explicitly. The paper mentions that different strategies with varying probabilities were tested (80%, 10%, and 10%), which includes masking a certain portion of input tokens at random as part of their experimentation process for MLM pre-training, but it doesn't provide an exact percentage applicable to all instances. |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| Salient span masking; because it focuses on examples that require world knowledge to predict the tokens in those spans which are often terms or concepts like "United Kingdom" or dates such as "July 1969". This strategy aims at guiding the model towards meaningful retrievals by concentrating on scenarios where local context is insufficient and external information becomes crucial. | REALM uses salient span masking because it enables better incorporation of world knowledge into language model training by explicitly exposing the role of this external information. This approach likely contributes to its performance improvements compared to other models that rely on different types of token or span masking, although specific results are not given in the context provided. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| 1. Self-attention provides an alternative representation of inputs without sequential dependencies, which can capture long range interactions between words effectively in natural language processing tasks like machine translation.<br><br>2. In terms of computational complexity and speed during training for specific applications (e.g., when sequence length is smaller than the dimensionality), self-attention layers are faster compared to recurrent layers that require O(n) sequential operations, where 'n' represents the number of elements in a sequence.<br><br>3. Self-attention can produce more interpretable models as it provides insight into how different words influence each other within an input sentence via attention distributions during model inference. | 1. Self-attention is faster than recurrent layers when sequence length n is smaller than representation dimensionality d, which frequently occurs in sentence representations used by state-of-the-art models in machine translations like word-piece and byte pair representations.<br>2. A self-attention layer connects all positions with a constant number of sequentially executed operations regardless of sequence length or complexity of input sequences, leading to consistent computational efficiency across different inputs.<br>3. Self-attention layers allow the model not only to learn dependencies between elements within an individual sequence but also capture bidirectional context by processing concatenated text pairs as one single sentence using self-attention in place of separate encoding and cross-attention stages, thus simplifying the pipeline for tasks involving two sequences (e.g., question answering). |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context does not provide this information directly, but it implies that our models outperformed all previously published single models at less than a quarter of the training cost. However, without specific BLEU score numbers for ConvS2S Ensemble in WMT 2014 English-to-French tasks from the context provided, we cannot accurately answer this question based on the given information alone. | The context does not provide the specific BLEU score achieved by ConvS2S Ensemble on WMT 2014 English-to-French translation task. Therefore, I cannot answer this question based on the provided information alone. The given table only specifies that it was surpassed with a Transformer (base model) which had a BLEU score of 38.1 and did not directly mention ConvS2S Ensemble's performance in English-to-French translation task for WMT 2014 data specifically. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The text does not provide specific information about the total number of floating-point operations used to train the base Transformer model directly. However, it mentions that they estimate this by multiplying several factors related to training (time taken, number of GPUs used, and sustained single-precision FP capacity per GPU). Since these values are not given explicitly for the baseline transformer in question, we cannot calculate or provide an exact figure without additional data. | To calculate the number of floating point operations for the base model's training, let's first estimate the total available single-precision (32-bit) FLOP capacity of an Nvidia P100 GPU. According to research by Dally et al., a P100 can sustain approximately 56 GFLOPS under Full Load conditions [4]. However, for this calculation and based on the information provided in Table 2 (which we are assuming contains relevant data), let's assume that each training step uses roughly half of full load capacity.<br><br>Here is how you calculate it:<br>- Each P100 GPU has a sustained single-precision FLOP rate of around 56 GFLOPS, and there are eight such GPUs used in the training process for one epoch (3.5 days): \(8 \times 56\) GB/sec = \(448\) GB/sec or \(270,720,000\) FLOP operations per second<br>- At a pace of ~1 checkpoint every minute: \(270,720,000 \times 1 \) checkpoint / min \(\approx\) \(270,720,000\) FLOPS for one epoch (64 steps)<br>- Assuming the base model uses a lesser number of parameters and hence fewer operations: Let's assume it is around halfway between this value (\(135.360 \times 10^6\)) and our big Transformer, so \(270,720,000 / 2 = 135,360,000\) FLOP operations for one epoch of training<br>- The total number of floating point operations is then: Number of checkpoints \(\times\) Operations per checkpoint. So with \(20\) such checkpoints (assuming they are not too long to run), the base model requires approximately \(135,360,000 \times 20 = 2,707,200,000 \) FLOP operations for training<br><br>Therefore, we estimate that our Transformer-based machine translation system uses roughly 2.7 billion floating point operations to train the base model on English-to-French data using eight P100 GPUs within a span of three and a half days. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context does not provide a specific QQP score for BERT-LARGE. It states that F1 scores are reported for tasks including QQP but only provides overall accuracy improvement percentages and model comparison results with OpenAI GPT without task-specific details like the exact performance on QQP. | The context does not provide specific scores for individual tasks such as QQP within the table of results. However, it states that "F1 scores are reported for [...], accuracy is also scored for other tasks." In regards to BERT-LARGE's performance on MNLI (which seems most relevant given its mention), we know from the text: "BERT obtains a 4.6% absolute accuracy improvement," and it gets an overall score LARGE of 80.5 on GLUE, compared to OpenAI GPT’s lower benchmark result as stated in their leaderboard entry with a score BASE (not explicitly mentioned but implied). Since the specific QQP performance isn't provided separately from MNLI results and no additional scores are given for accuracy or F1 across other tasks besides this mention, it is not possible to directly extract the exact QQP score achieved by BERT-LARGE based solely on the information in the text. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The provided context does not include specific numbers regarding the exact match scores achieved by REALM on the NaturalQuestions dataset after pre-training with its retrieval and encoder components. Therefore, I do not have this information based on the current context. | 38.2 |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| On Natural Questions, according to Table 1 of their study by Lewis et al., RAG-Sequence achieves an EM score significantly lower than BM25 and substantially below the performance mentioned for a hybrid parametric/nonparametric model. However, as exact figures are not provided in the context directly related to Natural Questions' scores achieved with respect to their own models (ragging), we can infer that while RAG-Sequence performs well on NQ by outperforming BM25 and other baselines mentioned, it does not explicitly mention a score of 28.9 EM for this particular dataset within the provided context. Therefore, I cannot provide an exact number solely based on this specific passage without additional information from Lewis et al.'s publication or related studies directly discussing RAG-Sequence's performance metrics specifically against Natural Questions (NQ). | The context provided does not contain information about the performance of RAG-Sequence specifically on the NaturalQuestions dataset as part of Lewis et al.'s work, hence I do not have this data from the given context. |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The Transformer base model uses 768 attention heads with a model dimension of 12 times the hidden size, A (since H is given as 768 when A=12). So if we denote dmodel as 'A', then each head has a dimensionality \( \frac{d_{model}}{H} = \frac{A}{768} \), assuming that this division results in an integer value, which must be true given the context. | The context provided doesn't specify a unique "Transformer base" with fixed numbers of attention heads (H) and dimensions for each head size (d). However, it mentions two sizes of models available in terms of layers (L), hidden size (A), and number of self-attention heads. One is BERT which uses 12 encoder/decoder stacks or Transformer blocks with a total parameter count of about 110M when having an embedding dimension A=12, H=768, using sinusoidal position encoding PE = (pos,2i) where pos is the position and i varies between dimensions. The other size doubles these parameters to around 340M with L=24 encoder/decoder stacks or Transformer blocks keeping A=16 but increasing H to 1024 using cosine functions for PE = (pos,2i+1). It's not explicitly mentioned which of the two models is referred as "Transformer base," and no specific information about a singular baseline model with fixed attention heads or dimensions has been provided. Hence I can only infer that there are at least these configurations without an exact number specified in this context for any single 'base' Transformer configuration regarding H, d, A size used consistently across both the 110M and 340M models as presented here. |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided discusses various aspects of the Transformer's multi-head attention and its applications but does not explicitly mention the dimensions of any feed-forward networks within the model itself. Typically, in transformer architectures like BERT (Base version), a feed-forward network is employed on top of each residual block after self-attention layers; these FFNs usually have two dense linear transformations with GELU activation and ReLU activation functions for added nonlinearity as seen in the original Transformer paper by Vaswani et al. (2017). However, without specific details given about feed-forward network dimensions within this particular text snippet of context on multi-head attention applications or variations in model size options provided at the end, we cannot directly extract FFN dimension information from it. Therefore, based on only the available context, I do not have enough information to state what feed-forward network dimensions are used by Transformer base models like BERT for this question's answer explicitly. | The context provided does not specify dimensions for any feed-forward networks within a Transformer base model. Instead, it mentions varying "base model size" and lists several configurations without details on their internal structure beyond layer count (L), hidden state dimension (A), and attention heads (H). Therefore, the answer cannot be determined from the given context. |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The BERT LARGE model has a hidden size (A) of 16,384 when using Ensemble + TriviaQA. It also uses 25 or more self-attention heads in its Transformer blocks to process information. This configuration contributes significantly to the substantial improvement observed across all tasks compared to BERT Base models with fewer parameters. | The BERT-LARGE model has a hidden size (A) of 16 and uses 4 attention heads as denoted by 'H=4'. However, there seems to be some confusion in the text regarding numbers. The original table or document might have different figures for these parameters that aren't clearly stated here but based on this context BERT-LARGE should ideally refer to a model with larger dimensions compared to its smaller counterparts as suggested by 'LARGE'. |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The scaling factor applied is the square root of the dimensionality (denoted as 'k' in the text), so for each element, it divides by the square root of k. In formula terms, this would be represented as division by sqrt(k). Therefore, before applying softmax to obtain weights on values in scaled dot-product attention, one applies a scaling factor which is 1 divided by the square root of 'k'. | The scaling factor applied is the inverse square root of the dimension d, specifically \( \sqrt{1/d} \) or \( (1/\sqrt{k}) \) if we assume k to represent dimensionality. This is done in order to avoid extremely small gradients during training when the dot products become large magnitudes due to larger dimensions without scaling, as mentioned with a factor of 4. |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| REALM computes this as p(z \| x), which represents a distribution over possible documents that could be retrieved, conditioned on the original query or text. It is not explicitly stated how REALM calculates these probabilities within the context provided; it simply models them during pre-training using gradient descent with respect to knowledge retriever parameters θ and evaluating their contribution through a relevance score f(x, z). | REALM computes the probability as p(z \| x), which is treated as a latent variable and marginalized over to obtain p(y \|x) = p(y \| z, x) p(z \| x). The specific computation for retrieving document z given input x involves running an additional forward pass where it multiplies the generator probability with p (z\|x) across η beams. This is part of REALM's Thorough Decoding procedure to estimate probabilities more efficiently, especially in longer sequences. |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided does not directly compare the performance of RAG and REALM specifically on the NaturalQuestions dataset in terms of their scores. Therefore, I do not have information about how they perform relative to each other based on this specific data source within the given text. If there are details elsewhere that provide such a comparison outside of the provided context, please specify those references for an accurate assessment. | <br>The context provided doesn't include specific comparative results between RAG and REALM on the NaturalQuestions dataset or any other named datasets. Therefore, I cannot answer how they compare based solely on this information. If there were details in the text regarding their performance against each other using a similar benchmark like OpenNaturalQuestions, it would be mentioned here; since that's not the case, we don't have enough data to make an assessment from the provided context alone. |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context doesn't provide specific numbers for how many attention heads are used by the standard (base) Transformer model in comparison to BERT-BASE. Therefore, I cannot answer this question based on the provided text. To find this information, we would typically refer back to prior details about transformer architectures or consult additional resources not included within this context. | The context provided doesn't specify how many attention heads are in the "base Transformer model." Therefore, it is impossible to determine from this text alone. The only information about different numbers of self-attention heads within BERT models mentioned here indicates that their count varies (L=12 with H=768 and A=12 for one size; L=24 with H=1024, A=16 for another). Without the exact number from a base Transformer model as reference in this text, I cannot provide an answer.<br> |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The provided context does not include specific comparison results between RAG-Sequence and REALM on the WebQuestions dataset. Therefore, I cannot provide a direct answer based on this information alone. To obtain these details, additional sources or studies comparing their performance specifically on WebQuestions would be necessary. | The context provided doesn't contain specific information about how RAG-Sequence compares to REALM on WebQuestions. Therefore, I cannot answer this question based on the given context. |
