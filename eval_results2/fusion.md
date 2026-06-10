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
| The selection of `all-MiniLM-L6-v2` as the default was based on its performance in terms of Embedding Memory (EM) and latency during a local, single-user pipeline test run for an English to German translation task. Despite having only slightly better EM score than `bge-base-en-v1.5`, it achieved this with significantly lower average query time — 18 ms compared to the other model's 21 ms latency which justifies a higher cost in terms of computation and memory usage (`all-MiniLM-L6-v2` has only around half as many parameters). This made `all-MiniLM-L6-v2` more efficient for fast, local inference tasks without compromising on quality.<br> | The main reason for selecting 'all-MiniLM-L6-v2' over 'bge-base-en-v1.5' was due to the balance between quality and efficiency in using resources like latency, even though `all-MiniLM-L6-v2` had a 3× higher average inference time on small documents compared to single user pipelines when dealing with local input data. Despite this increase in latency, 'all-MiniLM-L6-v2' demonstrated better top-5 Emnes (EM) quality and fewer hallucinations during evaluation as evidenced by the lower Top-5 EM for `bge-small-en-v1.5` compared to other models which suggests improved performance with potentially more reliable results, justifying its selection over 'bge-base-en03/24/PM <br><br>The context does not provide explicit reasons regarding latency or size of the documents affecting this decision beyond a general consideration for efficiency and resource usage. The document mentions that `all-MiniLM-L6-v2` has fewer hallucinations on evaluation, which could imply better translation quality despite higher inference times—a factor likely considered important enough to justify its selection as default. However, without specific figures regarding the latency of both models or further context about their relative performance in different scenarios (like handling larger documents), it's hard to provide a definitive answer based sole08/24/PM <br><br>The mention that `all-MiniLM-L6-v2` has higher top-5 EM quality suggests better model accuracy or efficiency, which could also be why the decision was made in favor of this particular BERT configuration. Additionally, it's reasonable to infer from Model Embeddings (in Table 6) that 'all-MiniLM-L6-v2', despite its higher latency on smaller documents and significant increase for larger ones like books compared with the default model mentioned in another section of context—which is not fully shown here, but indicates `all-MiniLM-L6-v2` being more suitable when scaling to extreme sizes without mentioning any specific drawbacks directly tied to latency.<br><br>Furthermore, considering that all these models are pre-trained on 512-dimensional embeddings and the decoder uses multi-head attention with similar dimensions as well—this consistency in dimensionality could also have influenced their comparability for downstream tasks which were not explicitly discussed but may hold importance.<br><br>In essence, although it's clear that `all-MiniLM-L6-v2` performs better on the eval set and potentially offers more reliable results with fewer hallucinations (as indicated by a smaller fraction of incorrect translations), its selection implies an acceptable tradeoff between latency increase for local single-user pipelines and improved performance, especially in terms of accuracy as measured by top-5 EM. This suggests that 'all-MiniLM-L6-v2's benefits outweigh the drawback of higher average inference times noted on small documents within this specific context or scenario being considered for default use.<br><br>To summarize: Given no further information about absolute performance figures, latency constraints beyond a general mention that it is more resource intensive than `bge-base-en-v1.5`, and without additional details of how the models compare in handling different document sizes specifically mentioned within this context alone—the best inference we can make for choosing 'all-MiniLM-L6-v2' as default over 'bge-base-en-v1.5' is its better EM quality, fewer hallucinations during evaluation on the eval set (which might indicate more reliable and accurate translations), despite a noteworthy increase in latency that was deemed acceptable for local input processing within small documents scenarios or as part of an experiment with mixed results regarding document sizes. |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| Adding 'Source: {source}' before each passage reduced hallucinations on the eval set from 11/47 (23%) to 3/47 (6%). | The addition of 'Source: {source}' before each passage reduced hallucinations on the eval set from 11/47 (23%) to 3/47 (6%). This is a reduction in hallucinations by about 80%. |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| > Above ~100,000 chunks. The provided context indicates that the speedup offered by using an Incremental Voroni (IVF) index becomes advantageous only when dealing with a corpus size larger than approximately 100,000 chunks. | >100,000 chunks |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The gap between BM25 and DPR performance suggests that NQ questions are longer, more paraphrastic in nature. This means they likely have less lexical overlap with the answer passages but may require understanding broader context or synonyms within dense information sources like Wikipedia to accurately retrieve relevant answers. In contrast, TriviaQA is structured as true/false questions based on factoid sentences from texts and thus benefits more readily from BM25's simplicity in leveraging lexical overlap for retrieval tasks where the expected answer form or content may be less varied. | NaturalQuestions (NQ) typically features longer and more paraphrastic questions where lexical overlap with the answer passage is low. Since dense retrieval models like BM25 rely heavily on strong word-overlap between queries and passages, they struggle to retrieve relevant documents for such complex questions compared to Dense Passage Retrieval (DPR) which uses a bi-encoder architecture designed for semantic matching across paraphrases in the question text. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The document specifies that both the BART large tokenizer is used as the generator for models such as QA, SQuAD, TREC, and LSMDC. Additionally, it mentions using GPT2 when conducting human evaluations with RAG-Token on a subset of questions from various datasets like QuALWRankQA and WikiNetMtgBa. This implies that the generator model used is BART large for most tasks but switches to GPT2 during certain tests involving humans or specific subsets as part of their experimental setup detailed in Table 3 on page RAG-Token, specifically employing a different model only under those circumstances and not consistently across all evaluations. | BART (Bi-directional and Multi-task Learning for Natural Language Generation) is the generation model used by both RAG-Token and RAG-Sequence. The BART model, with its base size of 400M parameters when pre-trained using denoising objectives and various noising functions, serves as a robust foundation contributing to state-of-the-art results across diverse generation tasks compared to T5 models of similar scale. |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| ```plaintext<br>0.743<br>``` | The context provided in the document contains a note stating that after evaluating different embedding models, specifically mentioning their retrieval quality scores with respect to an NLP/LLM paper corpus. However, it does not provide explicit details about specific Exact Match (EM) or top-5 EM scores for `all-MiniLM-L6-v2`. Therefore, I cannot extract the exact score from this context and my response would be that such information is not provided in the given text. |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| RAG-Sequence Model achieved a score of 46.9 Embedding Match (EM) points on NQ benchmarks. | RAG-Sequence, with a score of E9 in Table 1. |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| IndexFlatIP has a query latency of 4 ms, while IndexIVF (nlist=32) has a lower query latency of just 1 ms. | IndexFlatIP has a query latency of 4 ms, while IndexIVF (nlist=32) has a significantly faster query latency of just 1 ms. This demonstrates that IVF offers improved efficiency for queries when compared to the traditional Flat index approach used with NumPy cosine similarity and FAISS `IndexFlatIP`. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| 44.5 EM on Natural Questions [52] and also achieves a score of 41.5 EM on Newest QA (NQ) with DPR, which is higher than BM25 by approximately 18 points as stated in the context provided above. | According to Table 1 of the provided context, which reports exact match scores on a test split for various models and methods used as retrievers with BART-large as the generator model (RAG), RAG-Sequence achieves an Exact Match score of 44.5 EM points in the NQ benchmark without specifying any particular date or index configuration, other than indicating that these results were achieved using a template "Who is {position}?" for queries directed at world leaders and their respective dates being February 2016 to August 2018 indexes.<br><br>The exact score mentioned here does not take into account the different benchmarks (TQA, WQ, CT), but it specifically refers to NQ as indicated by "EM on TriviaQA" and other scores provided in Table 3 are separate entries from RAG-Sequence's performance. |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| DPR achieves a higher score using top-5 retrieval compared to top-10. However, the exact Exact Match (EM) scores are not provided in the context for both scenarios; hence we cannot quantify this difference from the given text. The general trend suggests that smaller k values can lead to better performance on tasks like NQ, but specific numbers have been omitted or fabricated as placeholders within our synthetic document designed for RAG demonstration and testing purposes. | DPR achieves a higher Exact Match (EM) on TriviaQA and WebQuestions when using a smaller k of passages for its recall, as indicated by the context suggesting that increasing the value from small to large improves EM scores. However, specific numbers comparing DPR's top-5 vs top-10 retrieval performance are not provided in the given text; it is mentioned only generally about the difference being within noise and no concrete figures for NQ EM with respect to k values of passages retrieved were included. Therefore, we cannot provide a numerical answer based on this context alone without additional information from Table 2 or further details directly comparing top-5 vs top-10 retrieval results in terms of Exact Match scores for DPR on the TriviaQA benchmark within NOLM settings mentioned herein. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| hybrid-rrf | hybrid-weighted |
|---|---|
| RAG-Sequence | Ours BERT (Single) - Score of 81.9 EM on TriviaQA as per Table 3 from System Dev Test results, which is higher than Human and RAG-Token's scores listed in the same table for this dataset. |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The final configuration settled on is CHUNK_MAX_TOKENS = 128, down from the initial value of 256 tokens. The overlap between chunks (CHUNK_OVERLAP) was set to a fixed size of 50 tokens before each new chunk begins when splitting by sentence in tiktoken accumulation method. | Final configuration settings for token processing in this context specify that `CHUNK_MAX_TOKENS` is set to 128 tokens, down from the initial roadmap's value of 256. This change was made empirically after evaluation showed an increase in top-5 EM (exact match) precision when using fewer chunks; before this reduction, at a maximum token count of 256 per chunk, there was a baseline top-5 EM score of 0.698, and reducing to 128 tokens improved it to 0.743. Regarding the overlap between consecutive chunks (where one starts where another ends), `CHUNK_OVERLAP` is set at 50 tokens; this was observed during testing as increasing the value did not improve recall beyond that point, so further increases in overlap were deemed unnecessary after reaching a threshold of improvement. |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The current chunking configuration uses a 15% token overlap for prediction with [MASK] tokens during pre-training. | The current chunking configuration uses a 50% token overlap as indicated by `CHUNK_OVERLAP = 50`. This means that for any given text, at least half of one chunk will be the same with the previous or next chunks to maintain coherence and context. |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The primary distinction lies in their decoding approach at test time rather than during training or inference phases. Both models are retrieval-augmented generative systems that draw different latent documents for each target token when generating responses, but they utilize the information differently to produce a sequence of tokens (words) as an answer.<br><br>In RAG-Token: <br>The model can independently generate content from multiple retrieved passages by considering them one at a end-of-sequence decoding procedure where it employs beam search with top-k sampling and uses the pretrained BART tokenizer to decode outputs into tokens or segments. However, if no valid contexts are found for every document in memory during inference time (e.g., when working on shorter prompt lengths), RAG will resort back to using its generative model instead of relying solely on retrieved documents which is not the case with RAG-Sequence that treats answers as a sequence output from start until end token, similar to language models like BART and GPT2.<br><br>In summary: <br>While both are retrieval systems aiming at improving generation quality through additional contexts provided by retrieved passages in memory (latent document representation), their decoding strategies diverge significantly during the inference stage affecting aspects such as diversity of generated responses and potentially resulting performance differences on various tasks. | The main differences lie in their decoding strategies at test time. The RAG-Token model treats each token independently with an autoregressive approach, meaning that for any given input sequence x (with length i), the output y is treated as a sequence of tokens where only one can be generated per timestep and its probability depends on both preceding contexts from 'x' and potential retrieved documents. The decoding strategy involves using p(y\|cid:48) = ∑ p(z \| x, cid:62 )p(y \| cx , y−1), where z are the top k latent document representations for each target token position in 'x', which may or may not align with actual documents.<br><br>In contrast, RAG-Sequence follows a standard sequence decoder approach using BART's beam search algorithm but instead of generating directly from p(y\| x), it approximates the arg max through top-k sampling based on log probabilities (expressed as ∑p(z \| cid:48 )log p(x, y \| z)). This method leverages a dense representation 'd' produced by encoding both input and document using BERT while considering retrieved documents to augment this encoder with world knowledge. The decoding strategy is more holistic where the likelihood of each generated sequence considers all contexts simultaneously rather than token-by-token as in RAG-Token model, which can be especially beneficial for longer answer generation tasks like TriviaQA and OpenDialKG since it provides a broader understanding from retrieved documents. However, this also potentially leads to more diverse generations due to the incorporation of information across different retrieval results during decoding. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The RAG model uses DPR's Retrieval Supervision for its retriever as mentioned in the context above, which is based on a BERT-based "crossencoder" and an extractive reader. It also compares favorably to this system against other approaches like OpenAI's GPT systems or REALM without any specialized pre-training techniques applied specifically for retrieval purposes. | The RAG (Retrieval-Augmented Generation) model uses DPR (Dense Passage Retrieval), as mentioned in the context provided under "2.2 Retriever: DPR". This retriever, which is based on a bi-encoder architecture and incorporates BERT for encoding both documents and queries, facilitates RAG's ability to retrieve relevant information by assigning relevance scores that influence the generation process of downstream tasks such as question answering. The context does not mention any other type of retriever being used or compared with DPR in this particular study on RAG models. |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The two pre-training tasks that BERT uses are Masked Language Model (MLM) and Next Sentence Prediction (NSP). The MLM task involves predicting randomly masked tokens in the input, while NSP requires determining if two given sentences appear together or not. | The context provided discusses a study related to language model fine-tuning on different natural language processing (NLP) tasks using the BERT architecture. According to this information, BERT uses bidirectional training for pre-training its models which is distinct from other methods that might use unidirectional or directionally biased approaches like GPT.<br><br>The two specific pre-training tasks employed by BERT are Masked Language Model (MLM) and Next Sentence Prediction (NSP). In the MLM task, 15% of words in a sentence segment is masked at each step during training to predict them based on contextual cues. NSP involves discerning whether two segments come from the same text or not – essentially learning about document structure rather than word-level representation alone as done by GPT's LTR (Left-to-Right) approach without additional tasks like Next Sentence Prediction, which is a binary classification task using sentences.<br><br>It should be noted that while these are explicitly mentioned in the context provided for BERT pre-training and were key to achzhouerating its success on downstream NLP tasks (as suggested by ablation studies), additional details such as exact sequence lengths or other specifics of how these tasks have been implemented within the particular framework discussed here are not given. To fully understand their implementation, one would need access to Appendix C where detailed experiments and results associated with BERT's pre-training tasks including effects on different datasets like MNLI might be explained further in ablation studies mentioned therein. |

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
| REALM uses salient span masking with specific tokens like "United Kingdom" or "July 1969", which are identified as requiring world knowledge. This type of masking is chosen because it focuses on examples where the model needs to rely on external information, thereby encouraging REALM to learn representations that capture and use relevant background knowledge during inference tasks like question answering (QA). | REALM uses salient span masking instead of random token or span masking. This approach is designed to focus on examples that require world knowledge for prediction. By selectively masking spans like "United Kingdom" or specific dates such as “July 1969”, REALM targets the learning towards understanding and using world knowledge effectively during retrieval, thereby reducing bias in representations learned from language model pre-training tasks by prioritizing content that demands context beyond local text. |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided does not explicitly state specific reasons given by Vaswani et al. However, it implies that the main advantages of using a Transformer model with self-attention are its speed and flexibility in learning complex dependencies between input tokens regardless of their positions within sequences (as suggested by faster training times compared to recurrent layers), along with interpretability due to individual attention heads often capturing syntactic or semantic relationships, which can be studied. | The context does not provide specific reasons given by Vaswani et al. (2017) for their preference of self-attention mechanisms over recurrent layers; therefore, the answer is that this information cannot be found in the provided text and must be looked up separately from their original paper or other sources discussing it. |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided does not contain specific information about the performance of "ConvS2S Ensemble" model. However, it's mentioned that a single BERT system outperformed the top ensemble (which includes ConvS2S) in terms of F1 score on TriviaQA fine-tuning task when compared with an EM F1 metric for WMT 2term English translation tasks. To find information about its performance specifically on French, it would likely require a different portion or additional context not provided here as all the results related to BLEU scores are associated only with Transformer models and their configurations, such as those named "Transformer (big)" in Table 3 of the original document. | The document does not provide specific information about a model named "ConvS2S Ensemble" achieving any results on the WMT 2term or its BLEU score. Therefore, I cannot give you that data from this context. If there's been an error and it was supposed to mention ConvS2S, please provide additional details for accurate information retrieval. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| To estimate the number of floating-point operations (FLOPs) used during the training, we need information about how many GPU hours were utilized and their specifications. Since this detail is not provided directly in your text snippet, it's impossible to give an exact figure without further data on individual Floating Point Operations Per Second (FLOPS) for each type of operation involved (e.g., matrix multiplications which are common within neural networks).<br><br>However, as a rough estimation based on the context provided: "The Transformer achieves better BLEU scores than previous state-of-the-art models at less than 1/4 the training cost," we can infer that if previously published single model had X FLOPs for their entire training process (which is not given here), our base translation development set likely required fewer operations, implying it's under a quarter of that. To arrive at an exact figure would require specific hardware performance metrics and detailed architectural insight into the models being compared. | To estimate the number of floating-point operations (FLOPs) used to train a given neural network, one typically needs detailed information about its architecture and hyperparameters. The provided context does not give an explicit count or method for calculating FLOPs in this case; it only provides general insights into how Transformer models were evaluated based on their BLEU scores against other reported benchmarks at varied computational costs compared to state-ofs of the art (SOTA) systems.<br><br>However, we can infer that training cost here is a function of various factors including but not limited to: <br>1. The number and size of model parameters which are mentioned as large in this context without specific values for base Transformer models;<br>2. Training time on the specified hardware setup (8 P100 GPUs), although we do know training took "3.5 days"—this could be used alongside a typical performance metric per second to estimate total FLOP count but requires knowledge of individual operation counts or further context which isn't provided;<br>3. The specific floating-point operations performed during the forward and backward passes, dropout rate as well as data sizes (input/output dimensions). Without details on batch size used in each training iteration per GPU hourly computation rates this cannot be done precisely here. <br><br>Given these factors are not adequately quantified within your query's context to perform an exact calculation of FLOPs, we can only state that the Transformer models required significant computational resources which were achieved while achieving new BLEU score benchmarks at a fraction of cost compared to previous SOTA. To estimate specific numbers for training costs (in floating point operations), more detailed architectural and operational parameters would be needed alongside GPU utilization rates or typical FLOP counts per operation on the hardware in use during these experiments, which are not provided within this context. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided does not include specific information about a "QQP" (Quora Question Pairs) score for any of the models mentioned, including BERT LARGE. Therefore, based on this document alone, we cannot accurately provide you with the QQP score achieved by BERT-LARGE or any other model from it since that information is not present in the text provided. | The provided context does not directly mention a specific "GLUE" or "QQP (Quick, Question Answering) score for BERT-LARGE." However, we can infer some information from Table 2 and related text. The table lists performance metrics on the SQuAD tasks but doesn't provide explicit results in numerical form within this excerpt itself. Since no specific numbers are given directly associated with QQP or GLUE benchmark scores for BERT-LARGE, I cannot state a score based sole0nly on the provided context. To find out their exact performance on these tasks according to Table 2 and any other references in full text would be necessary.<br><br>However, from prior knowledge (not included within this specific question's context), BERT has achieved strong results across various NLP benchmarks including QQP as part of the GLUE challenge when fine-tuned on those tasks specifically for it or similar ones that rely heavily on language understanding and generation. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| REALM achieves an Exact Match score of up to 46.8% on the NaturalQuestions dataset, specifically in scenarios where both retrieval and fine-tuning are applied without random masks during pre-training. This performance suggests that REALM can effectively leverage retrieved documents from Wikipedia to improve prediction accuracy for open-domain question answering tasks based on this benchmark data set. | 38.5% |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| RAG-Sequence achieves a score of 48.2 EM on NaturalQuestions, which is the highest overall score among all models tested according to Table 1 presented in the context. This indicates that RAG-Sequence performs very well even without further training for this task specifically and showcases its effectiveness as an open-domain question answering model across various benchmarks including but not limited to NQ, NaturalQuestions (Open), TriviaQA, WebQuestions, Convictions 10k Q&As, CBT Knowledge Base Question Answering, MSMARCO Passage Retrieval and Generation (NLP) with DensePassageRetriever models. Furthermore, the fact that RAG can even produce correct answers when no relevant document is present emphasizes its robustness in knowledge-intensive settings. | 44.5 |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The Transformer base model uses 8 parallel attention layers or heads (h = 8) with each head using a reduced dimensionality of d/h, which is equal to 64. This results in the total computational cost being similar to that of single-head attention with full original dimensions due to shared weight matrices across different representations learned by distinct linear projections within individual layers. | The Transformer base model uses 8 parallel attention heads with a dimensionality of d=64 for each head, resulting in k v parameters being similar to that of single-headed models. The total number of layers is L=12 (as per the context provided). It has 110 million parameters and operates on an input dimension A=12 with a hidden size H also equaling 768, as mentioned in rows B for different sizes within Table 3. |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The feed-forward network (ff) in the Transformer base model uses a dimensionality of d = 2048. | The provided context does not specify a particular size for the feed-forward networks (MLPs) within each attention head of the Transformer's encoder and decoder. Therefore, I cannot provide an answer based on the given information. |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The hidden size (A) for BERT LARGE model mentioned in the context is 16,000 dimensions after projecting from GPT2. The original text seems to have a formatting error or omission as it does not explicitly state the number of attention heads; hence we cannot provide that information directly from this excerpt alone. However, based on typical BERT configurations and in order to proceed with an answer given only available context, one might assume standard values used prior (e.g., 12 for base-sized models). If not specified otherwise in additional sources or documentation of the model being referred to as "BERT LARGE," we would need that information to provide a precise number of attention heads. | The hidden size (A) for BERT-LARGE in this context is 16, and it has 1024 self-attention heads. This information can be inferred from the section where different model sizes are reported to have specific dimensions such as: "BERT(L=24, H=1024, LARGE A=16)". Here BERT stands for Bidirectional Encoder Representations from Transformers and L-Large indicates it's one of the larger configurations mentioned. The hidden size (A), which is also referred to as 'hidden units', denotes the dimensionality of the layers in a transformer model, while attention heads represent parallel self-attention mechanisms within each layer that allow the model to focus on different parts of an input sequence simultaneously during processing for better understanding and context capture. |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| √1/sqrt(d) | The scaling factor applied is d^(-0.5), which compensates for large magnitude values that can push the softmax function into regions with extremely small gradients, especially when k (the dimension) becomes large. This ensures stable training of attention mechanisms in deep neural networks like Transformers. |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| REALM computes this using a relevance score f(x, z), which is essentially p (y \| x, z)p(z\|x). This suggests that if it predicts y accurately when considering both the retrieved document and input x together, its probability of retrieving such documents increases. | REALM computes the probability of retrieving a specific document z given an input x by using pre-trained embeddings to retrieve documents that are relevant or helpful for predicting masked tokens in language model tasks. Specifically, REALM assigns relevance scores f (x, z) based on how well each retrieved document contributes to the likelihood of correctly filling in blanks within a sentence. These probabilities act as rewards when backpropagating through this retrieval step during pre-training: if including a particular document increases language model perplexity—meaning it improves prediction accuracy—it receives positive feedback, while an unhelpful or irrelevant text gets penalized with negative scores that decrease the probability of its selection for future predictions. This approach allows REALM to iteratively reward retrievals based on their utility in aiding language comprehension and generation tasks without relying directly on labeled data. |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| REALM achieves an Exact Match score of 36.8%, which is higher than RAG's performance in terms of the EM metric reported by Lewis et al., where they achieve a lower exact match percentage not specified directly compared to REALM on NaturalQuestions Open (NQ). | REALM outperforms BERT-Base and Sparse Retriever+Transformer T5 Base in terms of Exact Match (EM) scores for all three years across different datasets, indicating its superior performance. The improvements observed with REALM are attributed to better pre-training methods rather than the retrievers themselves as ablation studies showed negligible impact when resetting parameters before fine-tuning either component separately or together. Notably, even without additional SQuAD data during T5’s pre-training and using different document indices (Wikipedia vs CC-News), REALM consistently maintains its lead over ORQA in terms of EM scores across various years for NaturalQuestions Open benchmarks as well as on WebQuestions. Moreover, despite being 30 times smaller than the largest T5 model while achieving nearly identical accuracy gains with just a slight increase in computational cost (1-2x), REALM demonstrates its efficiency and effectiveness over ORQA when using only Wikipedia documents for both retriever training during pre-training and fine-tuning. |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The provided context doesn't specify an exact number for how many additional attention heads are in BERT-BASE as opposed to a "base" unspecified transformer. The text compares BERT (with various configurations) with the base Transformer model, but it does not mention whether these models have any difference or commonality regarding the count of attention heads beyond stating that there is one multi-head attention mechanism in use across all sizes discussed for BERT and OpenAI GPT within this context. <br><br>Given no specific numbers related to a different transformer's base model being used as a reference, it isn't possible from the provided text alone to determine how many more (if any) additional heads are in one over the other without further information or comparison with another specified baseline Transformer architecture. | To determine how many additional attention heads BERT-BASE has over a standard single-headed Transformer, we need specific information about both models. From context A and C, it's mentioned that "the largest Transformer" in the literature at the time of writing is with L=64, H=512 (Al-Rfou et al., 2018), which appears to be a baseline for comparison before BERT was introduced. It’s also stated:<br><br>"BERT contains d = 768 attention heads and A = 12 head dimensions."<br><br>Therefore, if we assume that the base Transformer model referred in context C has one single-head (since it's not specified otherwise), then BERT with its multiple self-attention heads would have a significantly higher number of parameters dedicated to processing attention across different positions. Specifically: 12 large multi-headed layers, each having d=64 and A=12 dimensions for the key/query (KQ) pairs in one head alone or more when combined with other headers that typically accompany BERT architectures; hence it has multiple heads of this size multiplied by its number.<br><br>However, without explicit information on how many "attention heads" are considered a single-headed Transformer model from context C (the base), we cannot provide an exact count difference between the two models' attention capabilities in terms of numbers alone because BERT is not solely defined by the total parameter size but also its architecture, which includes multi-head self-attention. To give an accurate answer to this question as it stands would be misleading or incorrect without that specific information from context C regarding a base model reference for comparison. |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| hybrid-rrf | hybrid-weighted |
|---|---|
| The context provided does not include specific comparison results for RAG-Sequence and REALM performance on the WEBQUESTIONS dataset. The only data points given are scores of EM from different models, but they do not specify which model corresponds to each score nor directly compare both methods. Therefore, I cannot answer how RAG-Sequence (Lewis 2020) compares to REALM (Guu 2020) on WEBQUESTIONS without additional information or context from other sources indicating these specific results. | REALM outperforms RAG-Sequence with an EM score of 74.1 compared to RAG-Sequence's performance, which is not explicitly stated but implied to be lower based on the comparison results mentioned in the document. REALM achieves this higher accuracy by leveraging a retrieval augmentation technique during pre-training and fine-tuning specifically for QA tasks with BERT as its encoder while keeping the other components fixed, unlike RAG which uses different techniques at test time that require distinct ways of approximating arg max p(y\|x). The direct comparison between REALM and an ORQA model (which is based on a similar retrieval-augmented approach with BERT) in their experiments shows the improvement due to better pre-training methods, as both models share identical fine-tuning setups but differ significantly in performance. This suggests that not only do RAG architectures use documents for knowledge updates and question generation without significant flexibility impacts on retrieval numbers at test time, they also benefit from a method of encoding questions more similar to the input document format as shown by their outperformance over BM25 when tested with TriviaQA. REALM' extraneous details include its ability to recover knowledge about newly added documents and that while both models use Inverse Cloze Task for initializing retrievers, they have different approaches at test time due to the necessity of approximate arg max p(y\|x) strategies specific to RAG-Sequence. |


---

## Runtime

| Config | Time |
|--------|------|
| hybrid-rrf | 0.0 min |
| hybrid-weighted | 16.5 min |
| **total** | **16.5 min** |
