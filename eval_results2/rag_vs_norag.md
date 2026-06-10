# rag_vs_norag

**backend:** ollama · **model:** phi3

| Parameter | RAG (baseline) | no-RAG |
|-----------|--------|--------|
| retriever | dense | — |
| embed_model | all-MiniLM-L6-v2 | — |
| rerank | False | — |
| top_k | 15 | — |
| no_rag | False | True |

---

## Q1 · Level 1

**Question:** Why was `all-MiniLM-L6-v2` chosen as the default embedding model over `bge-base-en-v1.5`?  
**Expected:** The 4.4-point quality gap did not justify a 3x latency increase (18 ms vs 57 ms) for a local, single-user pipeline.  
**Source:** `rag_design_notes.md`

| RAG (baseline) | no-RAG |
|---|---|
| The decision to choose `all-MiniLM-L6-v2` as the default was based on a balance between performance and efficiency for local, single-user pipelines where latency is critical. Although there were only minor quality gains of about 0.35%, choosing this model meant accepting these in exchange to avoid significant increases in latency — specifically from around 18ms with `all-MiniLM-L6-v2` down to roughly half that at approximately 9ms when compared to the more resource-intensive but slightly better performing option, which had about a .05 quality gap.<br><br> | To provide an accurate response to why 'all-MiniLM-L6-v2' was selected as a better alternative for creating embeddings compared to 'bge-base-en-v1.5', one would need detailed knowledge of the specific characteristics and performance metrics associated with both models, such as their architecture details, speed, efficiency in various tasks, accuracy on benchmarks, etc.<br><br>If I lack this information or if it is not publicly available, then my response should be: "I don't have enough verified data to accurately compare 'all-MiniLM-L6-v2' with 'bge-base-en-v1.5', specifically regarding their usage for creating embeddings." |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| RAG (baseline) | no-RAG |
|---|---|
| Adding explicit source attribution reduced hallucinations from 23% on the eval set to 6%. | As an AI developed by Microsoft with a focus on providing information and guidance rather than specific historical data or proprietary research findings, I do not have access to real-time databases regarding studies conducted after my last update. However, in the context of improving hallucination rates within language models like GPT (Generative Pre-trained Transformer), incorporating source attributions can be significant as it helps ground responses and reduce fabricated output by clearly indicating where information is drawn from or suggesting that inferences are made beyond provided data.<br><br>To get precise figures on the reduction of hallucination rates with this approach, one would typically refer to research papers or experimental results specific to a particular implementation like RAG (Representations from AuGments), since these models can vary in design and output behavior based on their training and mechanisms for source attribution. To find such quantifiable impacts, I recommend reviewing the relevant scientific literature directly associated with that model's development or reaching out to researchers who specialize in this area of study if you seek detailed empirical results beyond my current knowledge cutoff date (2023). |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| RAG (baseline) | no-RAG |
|---|---|
| FAISS IVF becomes worthwhile over IndexFlatIP when the number of chunks exceeds approximately 100,000. Below this threshold, other factors such as a smaller corpus size or less complex queries may not justify the transition to FAISS with an Inverse Document Frequency (IVF) index despite its potential for faster query speeds. | To provide an accurate response to this question, I would need specific data or benchmarks comparing FAISS (an efficient similarity search and clustering algorithm) against IndexFlatIP in terms of corpus size. Without empirical studies or documented findings that detail the performance trade-offs between these two indexing methods at various dataset sizes, it's not possible to accurately determine above what corpus size does FAISS IVF become worthwhile over IndexFlatIP solely based on available information up until my knowledge cutoff in 2023. If you have access to such data or studies, I recommend consulting the latest research papers for insights into this question as benchmarks can change with advancements in technology and algorithms. |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| RAG (baseline) | no-RAG |
|---|---|
| The gap between BM25's performance and that of dense retrieval systems like DPR (Dense Passage Retrieval) can be attributed to the nature of questions posed in each dataset. NaturalQuestions consists mainly of longer, more paraphrastic queries where lexical overlap with potential answer passages is often low. This makes it difficult for BM25, which relies on word overlaps between query and passage terms, hence falling significantly behind DPR that uses a bi-encoder trained specifically on the NQ dataset to better understand contextual relevance regardless of direct lexical overlap. | BM25 and DPR (Diverse Passage Retrieval) are two different information retrieval models, while their performance can vary based on the dataset they're applied to. In general terms, BM25 performs well across various datasets because it leverages term frequency-inverse document frequency weighting in its calculations which helps determine relevance of documents and thus ranking them accordingly for a given query. However, DPR may have specific characteristics that can make it perform better on some types of questions or within certain contexts due to how diverse passages are retrieved and ranked based on their pertinence to the question at hand as well as diversity criteria which might be more aligned with NaturalQuestions' nature requiring understanding multiple document snippets simultaneously.<br><br>TriviaQA, conversely, appears to have questions that rely heavily on textual comprehension across different passages; hence a model like BM25 could perform better because it is based purely upon the statistical likelihood of terms within documents being relevant without needing an understanding of passage interrelation. This can make DPR less effective in this scenario as its performance hinges on identifying diverse, yet related information across multiple passages and drawing connections between them which might be more complex than what TriviaQA requires for a correct answer.<br><br>In summary: BM25 may fall behind DPR at NaturalQuestions because these questions likely demand an understanding of relationships among different text snippets where the strengths of diversity retrieval (DPR) are put to better use, while on datasets like TriviaQA that don't require as complex passage relation comprehension for answers, BM25’s simplicity in matching query terms with document relevance is sufficient and often superior.<br><br>It should be noted that without specific research or experimental results directly comparing these models within the same context of NaturalQuestions versus TriviaQA datasets, this answer provides a general understanding based on typical strengths associated with each model type across various information retrieval tasks. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| RAG (baseline) | no-RAG |
|---|---|
| BART-large | Both RAG-Token and RAG-Sequence utilize a variant of the Masked Language Model (MLM) architecture designed specifically for retrieval augmented generation. The core technology is based on pretraining with large datasets through self-supervised learning, where they learn to fill in masked tokens by predicting them using context from both documents and retrieved passages relevant to the given input text or task at hand. This ability allows RAG models not only to understand but also generate coherent content that is informed and augmented with external knowledge sources effectively integrated during pretraining, such as when dealing with tasks requiring document retrievals like question answering or summarization. However, specific proprietary variations of generators within these systems might have different nuances for handling context integration and text generation depending on the exact implementation details which can vary across models from various providers in this space (e.g., Google's PaLM). |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| RAG (baseline) | no-RAG |
|---|---|
| 0.743 | I'm sorry, but I cannot provide real-time or specific proprietary information such as the exact match scores of particular models like 'all-MiniLM-L6-v2'. Access to this kind of data typically requires API access from a service that provides these metrics. However, if you have general knowledge about machine learning model performance evaluations on standard benchmarks and datasets, I'd be happy to discuss the factors involved in determining such scores! |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| RAG (baseline) | no-RAG |
|---|---|
| BERT (Single) - Top Leaderboard System with Highest Score of F1 = 87.3% | The provided context does not contain specific information about different embedding models or their corresponding Top-5 Error Rates (EM). Therefore, I am unable to determine which embedding model has achieved the highest top-5 EM from this passage. If you could provide additional details regarding these models and metrics outside of the text given above, it would be possible for me to offer a more precise answer. |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| RAG (baseline) | no-RAG |
|---|---|
| The query latency for `IndexFlatIP` and `IndexIVF (nlist=32)` are both recorded at 4 milliseconds. However, it's important to note that while the IVF index has a slightly lower top-5 EM score of 0.736 compared to IndexFlatIP’s 0.743, and is built in about half the time (1.1 seconds for `IndexIVF` vs 0.8 seconds), it provides an additional speed advantage during querying as per the context provided above:<br><br>"FAISS \| IndexIVF ... Query latency (ms) \| --------------\|-------------------\|<br>\| FAISS \| IndexFlatIP     \|   0.743      \|       0.8         \| 4            \|<br>\| FAISS \| IndexIVF (nlist=32)\|  0.736    \|      1.1          \| --------------\|" | I apologize, but I currently do not have access to real-time or specific data regarding query latency for different indexing techniques like 'IndexFlatIP' and 'IndexIVF'. Query performance can vary based on many factors such as hardware, workload characteristics, dataset size, distribution of values within the index, and more. To obtain accurate figures, one would typically need to conduct benchmarking tests under controlled conditions that simulate real-world use cases or refer to published research in relevant scientific papers where these methods have been compared empirically. If you're looking for such information specifically related to 'IndexFlatIP' versus 'IndexIVF', it may be best to consult the latest academic literature, industry benchmarks, and whitepapers from database vendors specializing in distributed systems or machine learning infrastructures that often provide performance comparisons of their technologies. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| RAG (baseline) | no-RAG |
|---|---|
| RAG-Sequence achieves a score of 41.5 EM on Natural Questions (NQ) according to Table 2 mentioned in the context. However, it's important to note that this information is provided as part of an invented benchmark report and not actual experimental results from research papers or studies conducted by Lewis et al. | Unfortunately, without specific details or a reference to an actual Benchmark Report discussing RAG-Sequence and its performance on an exact match task using Neural Question Generation (NQ) models from Microsoft Research, I cannot provide accurate information. Typically, in such benchmarks, the accuracy is measured by comparing the generated questions with predefined correct answers or gold standard responses provided within a dataset to evaluate how well NLP systems perform similar tasks that involve question generation and understanding context for exact matches.<br><br>However, if you have access to this report, please look up sections discussing RAG-Sequence's performance on an Exact Match task using the Neural Question Generation system from Microsoft Research (NQ). You should find a paragraph detailing its accuracy score or result within that benchmark study which would give precise information about how well it performed in generating questions for exact matches. |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| RAG (baseline) | no-RAG |
|---|---|
| For NaturalQuestions (NQ), when using the Document Passage Retrieval (DPR) system, achieving a score of 44.5 Exact Match (EM) by considering only the top-5 retrieved documents shows RAG's ability to retrieve relevant information efficiently for this task. When expanding to consider just the top-10 retrievals before applying any fine-tuning, we find that DPR achieves a higher NQ EM score of 48%, demonstrating an improvement in results when more potential documents are considered during pre-training and not only relying on the most relevant document. | NQ EM stands for Normalized Query Exact Match scores in information retrieval systems like Dialogue Pair Reconstruction (DPR). The question seems to be asking about the performance improvement that DPR provides when comparing a top-5 recall with a higher standard such as top-10. In general, aiming beyond just returning an exact match and considering more results can enhance user satisfaction by providing alternative options close in relevance. However, without specific data from studies or benchmarks on how exactly DPR improves NQ EM for this comparison, I'm unable to provide a detailed answer regarding the improvement metric (e.g., percentage points increase).<br><br>Moreover, it is essential to note that while top-10 retrieval may offer users more choices and seem like an advantageous approach in certain cases where exact matches are rare or nonexistent, aiming for too many results can overwhelm the user with irrelevant information. The optimal balance between recall (top N) should thus be contextually determined based on task requirements, query nature, data availability, etc. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| RAG (baseline) | no-RAG |
|---|---|
| The QANet ensemble model achieved the highest TriviaQA Exact Match (EM) score, which was not explicitly stated but can be inferred to have outperformed other systems mentioned for this specific task. Since no numerical EM value is provided in the context for individual models or ensembles on TriviaQA, we refer back to the benchmark test results section where it lists human performance at 82.3 EM and mentions several model performances without directly stating which has the highest score:<br>- Ensemble (NLNet) - 86.0 EM<br>- Published BiDAF+ELMo Single System - not provided in numerical form but implied to have better results than BM25 since it's compared favorably with DPR on NQ, which suggests good performance across benchmarks and by the naming convention (Single) implies a less complex system.<br>- RAG Token Model/RAG Sequence System - 68.0 EM for TriviaQA specifically is mentioned but does not specify if this outperforms Ensemble's score of 86.0. Human performance, however, tops at 91.2 EM on the same platform.<br>- BERT Single Model and RAG Sequence System - no explicit scores given for these models with respect to TriviaQA in the text provided.<br><br>Given that ensembles generally tend to perform better than single systems due to their combined strengths, it is reasonable to assume that the QANet ensemble model achieved a high EM score on TriviaQA; however, without specific numbers or comparisons stating "highest," we can't definitively say which system had the highest. Human performance would typically be considered as the gold standard but was not part of this retriever ablation study since humans are excluded from comparison with systems in Table 2 (the provided context). | The document provided does not contain sufficient information to determine which specific question-answering (QA) system achieved the highest Exact Match (EM) score on TriviaQA. To answer this, one would need access to detailed results from a benchmark report that measures EM scores among various QA systems for their performance on the TriviaQA dataset. |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| RAG (baseline) | no-RAG |
|---|---|
| The final `CHUNK_MAX_TOKENS` value is 128, while the `CHUNK_OVERLAP` value is set to 50. These values were determined empirically as part of optimizing the chunking strategy for better precision in retrieving relevant tokens from a text corpus using FAISS indexing and embeddings with Tiktoken accumulation approach. | I'm sorry, but I can't provide current or specific values for parameters like `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP`. These would typically be defined within a particular codebase to control aspects of text processing. To find these constants in your context, you should look into the source files where they are set or consult with someone who has knowledge about them if it's part of an established system or protocol. |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| RAG (baseline) | no-RAG |
|---|---|
| 15% | As an AI developed by Microsoft without real-time or future updates beyond my last training data in April 2023, I do not have access to specific software configurations such as "current chunking configurations." Chunk size and overlap percentages can vary widely depending on the purpose of tokenization (e.g., natural language processing tasks) and the requirements set by developers or system architects for a given application. To determine this percentage, one would typically need information about how these parameters were defined in your specific chunking setup as it pertains to handling tokens within that configuration. Without access to those details or real-time data from systems beyond my last update, I cannot provide an accurate answer regarding the current token overlap percentages used by a particular system's chunker. |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| The primary distinction lies in their approach to handling retrieved documents. In RAG-Token, a different latent document can be drawn for each token of the target sequence allowing content from various documents when producing an answer during generation process; whereas, in RAG-Sequence model uses same retrieved document throughout and marginalizes over it using top-K approximation to generate the complete sequence. Thus both models differ in their treatment and integration of external knowledge into text completion tasks. | RAG (Residual Attention Guided) Token models are designed to improve upon BERT by focusing on salient context when generating responses in tasks like QA or summarization. There isn't a widely recognized distinction between "RAG-Token" and "RAG-Sequence," but I can explain the general differences you would find in RAG technology related to tokens vs sequences:<br><br>1. **Tokens** refer to individual pieces of text, often corresponding to words or subword units (like WordPiece). A token model like a transformer might encode each word into vectors before applying attention mechanisms for tasks such as translation, summarization, etc. <br>   <br>2. **Sequences** are related but more comprehensive; they could be entire documents that the language model has to process end-to-end using self-attention without needing intermediate tokens explicitly encoded in a vector format priorly (except for subword units which might still play an essential role). Sequence models can leverage longer contexts and work with more extensive text inputs.<br><br>To be specific, if we're talking about RAG technology: <br>- A **RAG Token** model could imply using a pretrained language model (like BERT) as the foundation for understanding tokens within an input sequence before incorporating attention mechanisms that specifically focus on salient information relevant to downstream tasks. It would likely utilize techniques like byte pair encoding or WordPiece tokenization and apply self-attention layers, possibly in conjunction with a language model pretrained end-to-end on the task of interest (for example, using SQuAD for question answering).<br>  <br>- A **RAG Sequence** approach would involve taking entire sequences as input without first breaking them down into tokens explicitly. It could use an architecture that inherently understands text sequentially and applies attention mechanisms at various levels to capture the salient information within larger context, possibly using techniques like sparse transformers for efficient processing of longer texts or documents in tasks such as summarization where understanding long-range dependencies is crucial.<br><br>In practical implementations: <br>A RAG Token model might be employed when fine-tuning on specific QA datasets to leverage the pretrained BERT's robustness and adapt its focus using attention guided by relevance in context for answering questions, while a Sequence approach would work directly with larger text inputs like full passages or longer documents without breaking them down into tokens explicitly. This method might be preferred when dealing with tasks where understanding the document-level coherence is essential (e.g., long-form summarization).<br><br>However, these distin0ctions are hypothetical because RAG as a technology doesn't specifically define such subcategories in its nomenclature; typically, we refer to it more broadly with respects like input length or specific fine-tuning objectives. It is essential always to check the latest research for updates on language model terminologies and applications since this field evolves rapidly. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| The RAG model uses DPR (Dense Passage Retrieval) as its retriever, which is based on a bi-encoder architecture using BERT for document and query encoding. The specific implementation of DPR mentioned in the context initializes with Document Re-Ranking from KVR-Reader [25]. | I apologize, but I do not have current information on a specific dog breed that any named "RAG" model uses as a retriever. It's possible there might be confusion with unrelated subjects or acronyms since in the context of machine learning and AI models like RAG (Representations from Augmenting Signal for Generative eXplaining), dogs are not typically discussed; instead, these concepts usually refer to computational algorithms. Could you please provide more details or clarify if "RAG model" refers to a specific technology, framework, or concept related to dog breeds? |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| The context provided does not specify which two particular pre-training tasks BERT uses as it only mentions that during its training phase for unlabeled data over different pre-training tasks, the model learns representations such as A/B and sentence embeddings. These may be components of various combinations of pre-training objectives used in practice but without a specific reference to two defined distinct ones within this text, it is not possible to determine which exactly they are from the context given alone. | The first task is Masked Language Modeling (MLM), where some percentage of input tokens are randomly masked and the model aims to predict those masked words. The second task is Next Sentence Prediction, which requires models to learn whether two sentences appear in that order within a document. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| 15% | Typically, around 15% to 20% of input tokens are randomly masked for each token during training with the Masked Language Modeling (MLM) objective on the pre-trained BERT model. However, this can vary based on specific configurations and versions used in research or application settings. |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| REALM uses salient span masking for its pre-training. This strategy is used to focus on examples that require world knowledge because it targets specific tokens within the text such as "United Kingdom" or "July 1969." These are considered salient spans, which by their nature would benefit from retrieving relevant documents containing this information during training since they pose problems requiring external context for accurate prediction of masked words. | REALM (Relation-Aware Entity Linking) uses a specific form of attention mechanism called 'relational' or 'entity pairwise relational reasoning' as its primary approach to mask certain information. This technique is employed during pre-training for the purpose of learning entity representations with context, which helps in understanding and linking real-world entities within text data more effectively.<br><br>The reason REALM uses this particular type of attention mechanism lies in enhancing the model's ability to handle ambiguity and disambiguation issues often found in natural language processing tasks like Entity Linking (EL). By focusing on contextual relationships between pairs of words, specifically when one is an entity name and the other provides a hint about its identity or role within that text, REALM can learn more accurate representations for entities. This relational mask allows it to better distinguish relevant information from irrelevant details in large unstructured datasets like Wikipedia dumps used during pre-training.<br><br>Additionally, this method of attention mechanism helps reduce the need for human annotation while preserving high performance on entity linking tasks post fine-tuning or testing, making REALM a more efficient and scalable approach to handle massive language data with numerous entities without overfitting concerns that often accompany end-to-end training methods. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| 1. Self-attention allows the model to learn dependencies without regard to their distance in the input sequence, which can capture long-range interactions more effectively than RNNs that process data sequentially from left to right or vice versa. This is because self-attention mechanisms compute a representation of each position by attending over all positions simultaneously within a single attention layer.<br><br>2. Self-attention layers have constant computational complexity regardless of the sequence length, making them more parallelizable and thus faster for training on modern GPUs compared to RNNs that increase their sequential computation time with longer input sequences (O(n) operations). This advantage becomes significant in cases where d < n as it's most often encountered.<br><br>3. Self-attention mechanisms have been shown empirically, especially within the Transformer model context by Vaswani et al., to yield more interpretable models due to attention distributions that can clearly indicate which parts of the input sequence influence each output position and how syntactic and semantic structure are learned in representation learning tasks. | According to Vaswani et al.'s paper on Transformers (published in "Attention is All You Need" - https://arxiv.org/abs/1706.03762), they argue that self-attention mechanisms outperform recurrent layers for the following reasons:<br><br>1. Parallelization and computational efficiency – Self-attention allows all positions in a sequence to be attended simultaneously, unlike RNNs which process one item at a time sequentially due to their inherent recursive nature. This parallel processing of sequences leads to significantly improved speed during training and inference times when using self-attention mechanisms as opposed to recurrent layers (Section 4).<br><br>2. Long-range dependencies – Self-attention is not limited by the vanishing gradient problem which can hamper RNNs' ability to model long sequence data effectively, while allowing direct representation of relationships between any pair in a set regardless of their distance within that set for capturing contextual information more efficiently (Section 3).<br><br>3. Flexibility and ease of implementation – Self-attention allows flexibly using multiple input elements at different positions simultaneously to produce an output without relying on the sequential processing model which can be a cumbersome task in RNNs, especially when dealing with complex sequence data (Section 4). The authors also mention that self-attention mechanisms do not require unfolding for each time step like recurrent layers and are easier to implement as they only need linear operations at most.<br><br>Please note this is a summarized response from the original paper, which contains more detailed discussions on these topics in sections 3, 4 & 5 respectively (https://arxiv.org/abs/1706.03762). |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| The document does not provide specific information about the BLEU score achieved by ConvS2S Ensemble on WMT 2014 English-to-French. The text only mentions that our best Transformer model outperformed all previously reported single models, at a fraction of their training cost without specifying scores for ensembles or other architectures like ConvS2S. | I apologize, but I do not have specific data regarding the BLEU scores achieved by ConvS2S Ensemble or any particular model in that domain. To obtain this information accurately, one should refer to WMT (Workshop on Statistical Machine Translation) benchmark results for the year mentioned. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| To calculate the training cost in floating-point operations (FLOPs) for a given model, we would typically multiply three factors together as mentioned in the context provided. However, since specific details such as single-precision FLOP calculations per operation or sustained GPU capacity are not explicitly stated within this particular extraction of text from your document other than an estimate reference [5], I can't calculate it directly without additional data. To provide a precise answer with the information given here would be speculative at best, and potentially inaccurate if we don’t rely on appropriate benchmarks or estimates for GPU FLOP computations during training of Transformer models. | Unfortunately, I cannot provide an accurate number for the total computational complexity or FLOPs (floating-point operations) required by a specific implementation of a Base Transformer without more context. The training cost can vary significantly depending on various factors such as model size, depth and width, batch size used during training, data augmentation techniques applied if any, hardware utilized for computation, optimization algorithms employed etc. Moreover, since there is no universally standard "base" transformer with a definitive specification mentioned in the context of AI or machine learning literature up to my knowledge cutoff date (2023), I can't provide an exact figure without more precise details regarding which Base Transformer model you are referring to. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| The provided context does not explicitly mention a QQP score for BERT-LARGE obtained from the GLUE benchmark. However, it states that "on official leaderboard10, GLUE BERT obtains a score LARGE of 80.5." Since this is likely referring to BERT's performance on the task within the larger context of all tasks in GLUE (not specifically QQP), and given that scores are not differentiated by specific tasks beyond stating an overall "LARGE" classification, it is impossible to accurately determine the exact score for just the QQP.<br><br>To obtain this figure if available elsewhere or from a leaderboard archive directly would be necessary as of my last knowledge update in April 2023. | I apologize, but I do not have access to real-time or live databases including specific scores from model evaluations like those of BERT models. However, as of my last update in April 2023, a common reference was that pretrained language models such as BERT achieved varying degrees of performance on the GLUE benchmark, often exceeding human baselines and setting new records for natural language understanding tasks across diverse datasets and domains at their introduction. For an accurate score obtained by BERT-LARGE specifically, I recommend referring directly to a reliable source like Google Scholar or looking up scientific papers that report such experiments conducted on the GLUE benchmark dataset. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| REALM achieves the best End-to-End Exact Match (EM) scores among all systems after a single fine-tuning stage. This performance is consistent across both dev and test sets for questions from various subsets of data within NaturalQuestions Open, such as TriviaQA or WordNet + WikiGiven. Specific EM percentages are not provided in the context but it's clear that REALM outperforms all other systems based on this metric. | I apologize, but I do not have access to real-time databases or specific scores for models such as REALM (Reference Augmented Language Model) from the Nature Quarterly of Science Communication. If you are referring to a particular benchmark score on an open dataset like NaturalQuestions Open, it's essential first to verify if there is accurate and updated information available in scientific literature or database repositories regarding such specific scores for AI models including REALM. |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| 44.5 | RATER (Relevance Aware Text Generator) and its method called REALM have been demonstrated to produce state-of-the-art results for the task of extractive summarization according to research conducted by Lewis, Liu et al. However, there is no direct mention in their study about RAG-Sequence specifically achieving an "Exact Match" on NaturalQuestions within this context. If such a claim or result were documented elsewhere from the same group's work (or potentially other sources), I would be able to provide that information accurately after proper verification of credible references. Since no specific match score for RAG-Sequence is mentioned, my response reflecting data directly found within Lewis et al.'s NaturalQuestions study cannot include this metric unless additional context or a different paper confirms it. |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| The Transformer base model uses 8 attention heads with a model dimension (d) of 64 for each head after projection from an initial hidden size. The total number of parameters is reported to be around 110 million, which corresponds to the encoder part in this case as it does not include decoder parts when discussing base sizes separately. | The original Transformer base model introduced by Vaswani et al. uses eight attention heads with a model dimension (hidden size) of 512 for each head. However, this can vary in different versions and adaptations of the Transformer architecture. For example, BERT's transformer has ten multi-headed self-attentions where all dimensions are set to 768 while RoBERTa modifies certain hyperparameters including attention heads count based on their experimental configurations. |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| The dimensions used in the Transformer's fully connected layers are not specified within the given context; therefore, I do not have information regarding this detail based on the provided text. Typically, knowledge about such architectural details can be found by referring to original research papers like Vaswani et al., (2017), or detailed implementation guides for specific models using Transformers since different implementations may vary in these dimensions. | The original version of the Transformer (see paper Attention is All You Need by Vaswani et al., arXiv:1706.03762) uses a feed-forward network within each encoder and decoder layer with dimensionality set to four times that used in the model's multi-head attention mechanism, which defaults to 512 for most configurations of Transformer models such as BERT or GPT-2 (see paper "BERT: Pre-training of deep bidirectional transformers for language understanding," Vaswani et al., arXiv:1810.04397). However, this specific value can be adjusted depending on the particular model variant being used and its intended application or computational constraints; thus without additional context it is safer to say that common Transformer models typically use feed-forward network dimensions of 2048 (i.e., four times 512) within their encoders and decoders, but this should be confirmed for a specific model variant in question if needed. |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| The Hidden Size (H) for BERT-LARGE is 1024, and it has 16 Attention Heads. | BERT-LARGE has a hidden size (also known as the model size or embedding dimension) that can vary based on its specific configuration. However, commonly referenced large models like Google's Megatron-Turing NLG have configurations with larger sizes than BERT typically offers—ranging in millions of parameters rather than tens to hundreds of thousands within a standard BERT variant (BertBase or BertLarge). As for the number of attention heads, this also depends on specific implementations. In traditional BERT models like RoBERTa-large and BioBERT versions, there are usually 12 self-attention layers with 12 multi-head self-attentions in each layer (hence a total of around 144 attention heads). However, since the original document you're referring to doesn't specify BERT-LARGE by its name alone or provide these details directly within this text exchange, I cannot give an exact answer. If we assume that "BERT-LARGE" refers to a significantly large variant of Google’s Megatron models rather than the original Transformer from Google AI's paper (which BERT is based on), it might have 12 attention heads across its layers, but please confirm the model specification for precise details. |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| The square root of d, denoted as √1 in the context (which seems to be a typographical error and should likely read sqrt(d)). This scaling is applied to prevent gradients from becoming extremely small or large when computing attention scores for very high-dimensional vectors. The corrected statement with proper notation would then read: "We scale the dot products by √1 before applying the softmax function." | The scaling factor applied in Scaled Dot-Product Attention is the inverse square root of the dimensionality of key vectors (or query and value vectors since they are interchangeable). Therefore, if we denote \(d_k\) as the dimension of keys (and similar for queries), then each score calculated before applying softmax would be scaled by \(\frac{1}{\sqrt{d_k}}\). |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| REALM computes the probability p(z \| x) as a sample from the distribution conditioned on the original input x, often using an attention mechanism to weigh different documents in the knowledge corpus Z relative to how relevant they are to the given query. The specific computation involves learning parameters that can encode both local and global biases towards particular types of information within z based on its content's relevance to the masked token y in x for pre-training or question qx for fine-tuning tasks. | REALM uses a language model to calculate probabilities for different sequences based on their likelihood according to learned patterns in data. Specifically, it computes P(z\|x) using its underlying neural network and pre-trained knowledge from related tasks or domains (if applicable). The exact mathematical details would depend on the implementation of REALM within a given system but generally involves evaluating probabilities based on transitions between tokens as per their contextual likelihood. However, without specific documentation or source code for REALM's algorithms and mechanisms at hand indicating its methods to calculate P(z\|x), I am unable to provide an explicit process used by REALM itself. |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| According to Table 1, when comparing T5-based models like RAG and pre-training methods such as those used in REALM for the task of open-domain question answering (QA), there is no direct comparison provided between these specific systems within this context. Therefore, I cannot provide a direct answer on how they compare based solely on the information given herein. To accurately determine their relative performance on NaturalQuestions Open or any other dataset/task, one would need to refer directly to studies comparing both RAG and REALM specifically against each other under similar conditions. | I cannot provide a comparison between RAG and REALM based solely on the references "Lewis 2020" for RAG and "Guu 2020" for REALM regarding their performance or characteristics since I have not accessed these specific articles. To accurately compare models like RAG (Large Language Model) developed by Lewis et al., with another model such as REALM proposed by Guo et al., one would need to review the methodologies, results presented in each paper and assess aspects like accuracy, efficiency, data requirements, robustness against diverse question types on benchmarks or real-world datasets. If these articles were available, I could summarize their findings with respect to NaturalQuestions Open based on empirical evidence provided by both studies. |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| BERT has a total of 768 attention heads, whereas we are not provided with explicit information regarding how many this is over the original or unspecified "base" version. Typically, BERT-BASE refers to a specific configuration which uses a larger number than smaller variants like BERT-Small (which had only 12 attention heads), but without additional context about what constitutes the 'original' Transformer model size in terms of attention heads for comparison, it is impossible to provide an exact difference. However, we can infer that there are significantly more than double since larger models typically scale up various components including head count relative to smaller ones like BERT-Base and even further with DistilBERT which has 6 attention heads (though this latter model isn't directly comparable as it is a distilled version of BERT). | BERT-BASE has four times as many multi-head self-attention mechanisms in each layer when compared to a standard transformer base, specifically using 12 layers with 12 attention heads each. So if we consider the number of individual head units (rather than separate models), BERT would have `4 * num_layers` more as it scales up from what might be considered "base" level Transformer setups which typically involve fewer, singular attentional mechanisms per layer and overall lesser numbers of layers. |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| RAG (baseline) | no-RAG |
|---|---|
| RAG-Sequence outperforms the T5 large model and achieves a score of 14.3 EM, while it is not specified how RAG compares directly to REALM in this specific context as their performance scores on WebQuestions are provided separately by different sources (Lewis for RAG-Sequence; Guu et al., without mentioning the exact numbers comparable between these works). However, based on general trends noted elsewhere where both systems performed well with dense retrieval and BM25 falling short compared to DPR, it can be inferred that REALM's performance might have been competitive or superior due to its effective use of document indexing. | As of my knowledge cutoff in March 2023, a direct comparison between the models RAG-Sequence and REALM specifically regarding their performance on "WebQuestions" as outlined by Lewis (2020) and Guu et al. (2020), respectively, is not explicitly documented or readily available in existing literature up to that point. Both methods represent significant advancements within the field of natural language processing for generating responses based on limited contexts, but their specific performances have not been directly contrasted against each other solely within WebQuestions tasks as reported by these authors at this time. Therefore, I do not possess concrete information regarding how they compare in that regard up to my last update. |


---

## Runtime

| Config | Time |
|--------|------|
| RAG (baseline) | 9.0 min |
| no-RAG | 4.1 min |
| **total** | **13.2 min** |
