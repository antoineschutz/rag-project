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
| The decision to choose `all-MiniLM-L6-v2` as the default was based on a balance between performance and efficiency for local, single-user pipelines where latency is critical. Although there were only minor quality gains of about 0.35%, choosing this model meant accepting these in exchange to avoid significant increases in latency — specifically from around 18ms with `all-MiniLM-L6-v2` down to roughly half that at approximately 9ms when compared to the more resource-intensive but slightly better performing option, which had about a .05 quality gap.<br><br> | The decision to choose `all-MiniLM-L6-v2` over `bge-base-en-v1.5` was based on a tradeoff between quality and latency, as well as considering the size of each model's parameters. Although `all-MiniLM-L6-v2` had only 4.4 points less top-5 EM for question generation compared to `bge-base-en-v1.5`, it also resulted in a significant reduction in latency—from about three times longer, or around triple the number of steps required during fine-tuning on RAG prompts (which is 3× more than what BERT's size typically requires). Additionally, both models had roughly equivalent parameter counts after accounting for pruning and chunking. Therefore, `all-MiniLM-L6-v2` was selected as it provides a better balance of quality with acceptable latency without significantly increasing the model’ end parameters count compared to using only 3× the size or steps that BERT would have required alone. | The selection of `all-MiniLM-L6-v2` as the default was based on its performance in terms of Embedding Memory (EM) and latency during a local, single-user pipeline test run for an English to German translation task. Despite having only slightly better EM score than `bge-base-en-v1.5`, it achieved this with significantly lower average query time — 18 ms compared to the other model's 21 ms latency which justifies a higher cost in terms of computation and memory usage (`all-MiniLM-L6-v2` has only around half as many parameters). This made `all-MiniLM-L6-v2` more efficient for fast, local inference tasks without compromising on quality.<br> |

## Q2 · Level 1

**Question:** How much did adding source attribution to the RAG prompt reduce hallucination?  
**Expected:** From 11/47 (23%) to 3/47 (6%)  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| Adding explicit source attribution reduced hallucinations from 23% on the eval set to 6%. | The addition of explicit 'Source:' prefixes before each passage in the context reduced hallucinations on the eval set from 11 instances (23%) to just 3 instances (6%). | Adding 'Source: {source}' before each passage reduced hallucinations on the eval set from 11/47 (23%) to 3/47 (6%). |

## Q3 · Level 1

**Question:** Above what corpus size does FAISS IVF become worthwhile over IndexFlatIP?  
**Expected:** Above approximately 100,000 chunks  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| FAISS IVF becomes worthwhile over IndexFlatIP when the number of chunks exceeds approximately 100,000. Below this threshold, other factors such as a smaller corpus size or less complex queries may not justify the transition to FAISS with an Inverse Document Frequency (IVF) index despite its potential for faster query speeds. | <br>Over ~100,000 chunks. | > Above ~100,000 chunks. The provided context indicates that the speedup offered by using an Incremental Voroni (IVF) index becomes advantageous only when dealing with a corpus size larger than approximately 100,000 chunks. |

## Q4 · Level 1

**Question:** Why does BM25 fall further behind DPR on NaturalQuestions than on TriviaQA?  
**Expected:** NQ has longer, more paraphrastic questions with low lexical overlap between question and passage.  
**Source:** `qa_benchmark_report.docx`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The gap between BM25's performance and that of dense retrieval systems like DPR (Dense Passage Retrieval) can be attributed to the nature of questions posed in each dataset. NaturalQuestions consists mainly of longer, more paraphrastic queries where lexical overlap with potential answer passages is often low. This makes it difficult for BM25, which relies on word overlaps between query and passage terms, hence falling significantly behind DPR that uses a bi-encoder trained specifically on the NQ dataset to better understand contextual relevance regardless of direct lexical overlap. | NaturalQuestions (NQ) questions are longer, more paraphrastic and have less lexical overlap with the answer passage compared to TriviaQA. As a result, dense retrieval systems like DPR that use embedding models capable of capturing semantic similarities perform better on NQ than BM25 which relies on word overlap for matching passages. | The gap between BM25 and DPR performance suggests that NQ questions are longer, more paraphrastic in nature. This means they likely have less lexical overlap with the answer passages but may require understanding broader context or synonyms within dense information sources like Wikipedia to accurately retrieve relevant answers. In contrast, TriviaQA is structured as true/false questions based on factoid sentences from texts and thus benefits more readily from BM25's simplicity in leveraging lexical overlap for retrieval tasks where the expected answer form or content may be less varied. |

## Q5 · Level 1

**Question:** What generator model do RAG-Token and RAG-Sequence use?  
**Expected:** BART-large  
**Source:** `qa_benchmark_report.docx`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| BART-large | BART-large | The document specifies that both the BART large tokenizer is used as the generator for models such as QA, SQuAD, TREC, and LSMDC. Additionally, it mentions using GPT2 when conducting human evaluations with RAG-Token on a subset of questions from various datasets like QuALWRankQA and WikiNetMtgBa. This implies that the generator model used is BART large for most tasks but switches to GPT2 during certain tests involving humans or specific subsets as part of their experimental setup detailed in Table 3 on page RAG-Token, specifically employing a different model only under those circumstances and not consistently across all evaluations. |

## Q6 · Level 2

**Question:** What top-5 Exact Match score does `all-MiniLM-L6-v2` achieve?  
**Expected:** 0.743  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| 0.743 | The document indicates that the default decision was to select `all-MiniLM-L6-v2`. However, it doesn't specify the top-5 Exact Match score achieved by this model. The context provided does not contain numerical data on its performance metrics specifically for a 'top-5 Exact Match'. To find that information within this document or elsewhere is beyond what was explicitly stated in the given text. | ```plaintext<br>0.743<br>``` |

## Q7 · Level 2

**Question:** Which embedding model achieves the highest top-5 EM, and what is the score?  
**Expected:** `bge-base-en-v1.5` at 0.787  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| BERT (Single) - Top Leaderboard System with Highest Score of F1 = 87.3% | RAG-Sequence uses a bi-encoder trained on NQ to achieve this result. The exact match (EM) scores are not provided in numerical terms within your text; instead, it states that RAG-Sequence outperforms BM25 by achieving higher top-5 EM points. However, since the specific numbers for these metrics aren't included directly after discussing RAG-Sequence’s performance on NQ benchmarks (wherein this model is stated to have achieved its highest scores), and your context does not provide a distinct score beyond comparative statements about outperformance relative to BM25, it would be impossible from the provided text alone to definitively identify an exact top-score among RAG models without further numerical data. To answer with precision based on this document's content as given in December 2021 or any later updates beyond my knowledge cutoff date: one should refer back to Table 1 (as mentioned but not provided) for the specific scores. | RAG-Sequence Model achieved a score of 46.9 Embedding Match (EM) points on NQ benchmarks. |

## Q8 · Level 2

**Question:** What is the query latency of IndexFlatIP vs IndexIVF?  
**Expected:** IndexFlatIP: 4 ms, IndexIVF: 1 ms  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The query latency for `IndexFlatIP` and `IndexIVF (nlist=32)` are both recorded at 4 milliseconds. However, it's important to note that while the IVF index has a slightly lower top-5 EM score of 0.736 compared to IndexFlatIP’s 0.743, and is built in about half the time (1.1 seconds for `IndexIVF` vs 0.8 seconds), it provides an additional speed advantage during querying as per the context provided above:<br><br>"FAISS \| IndexIVF ... Query latency (ms) \| --------------\|-------------------\|<br>\| FAISS \| IndexFlatIP     \|   0.743      \|       0.8         \| 4            \|<br>\| FAISS \| IndexIVF (nlist=32)\|  0.736    \|      1.1          \| --------------\|" | IndexFlatIP has a query latency of 4 ms while IndexIVF has a query latency of 1 ms. | IndexFlatIP has a query latency of 4 ms, while IndexIVF (nlist=32) has a lower query latency of just 1 ms. |

## Q9 · Level 2

**Question:** What NQ Exact Match does RAG-Sequence achieve in the benchmark report?  
**Expected:** 44.5 EM  
**Source:** `qa_benchmark_report.docx`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| RAG-Sequence achieves a score of 41.5 EM on Natural Questions (NQ) according to Table 2 mentioned in the context. However, it's important to note that this information is provided as part of an invented benchmark report and not actual experimental results from research papers or studies conducted by Lewis et al. | In the benchmark report, RAG-Sequence achieves an Exact Match score of 44.5 on the NQ dataset. This indicates that for a significant portion of questions where multiple potential answers are retrieved based on their similarity to each question (Top-k), at least one correct answer is within these top predictions in terms of textual match, thereby leading to this high EM score. | 44.5 EM on Natural Questions [52] and also achieves a score of 41.5 EM on Newest QA (NQ) with DPR, which is higher than BM25 by approximately 18 points as stated in the context provided above. |

## Q10 · Level 2

**Question:** What NQ EM does DPR achieve with top-5 vs top-10 retrieval?  
**Expected:** 41.5 (top-5) to 43.2 (top-10), a 1.7-point gain  
**Source:** `qa_benchmark_report.docx`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| For NaturalQuestions (NQ), when using the Document Passage Retrieval (DPR) system, achieving a score of 44.5 Exact Match (EM) by considering only the top-5 retrieved documents shows RAG's ability to retrieve relevant information efficiently for this task. When expanding to consider just the top-10 retrievals before applying any fine-tuning, we find that DPR achieves a higher NQ EM score of 48%, demonstrating an improvement in results when more potential documents are considered during pre-training and not only relying on the most relevant document. | With a maximum context window, RAG achieves an Exact Match score (EM) of only around 42% on Trivia Questions. This low performance is mainly due to the fact that there are questions in this dataset where some paragraphs contain two different correct answers; without additional reasoning from language models, it's hard for DPR-based systems alone to discern which one applies given just a sentence or phrase as input query context.<br><br>To improve on TriviaQA performance using RAG and other retrievers (retrieval augmented generation), we conduct ablation studies with varying numbers of top retrieved passages before feeding them into BART-large for response selection, alongside experiments comparing dense passage retriever systems against baseline sentence embeddings like PubMed.<br><br>DPR achieves an EM score only around 42% on Trivia Questions when using a maximum context window of about four paragraphs (i.e., top five passages). We hypothesize that expanding the retrieval size would benefit generation performance, but empirically observe diminishing returns beyond ~7 retrieved documents with an EM score improvement from 42% to roughly 45%.<br><br>The following table details our results for various combinations of passage counts and dense retriever backends on Trivia Questions (NQ):<br>```markdown<br>\| Retrieval Backend \| Top-k        \| P@1         \| EM    \| QP @90   \| RT     \| 3W F1    \| MRT      \| IGDRM(Lwl/E)m_DPR                                \| SOTA Dense Passage Retrieval (NQ; [26])       \|<br>\|------------------\|--------------\|-------------\|-------\|----------\|--------\|----------\|----------\|-----------------------------------------------\|--------------------------------------------\|<br>\| PubMed           \| Top 10        \| ~85%@3       \| -     \| -        \| No.9   \| N/A      \| Yes; nope \| Not Applicable                                \| DPR (26 points EM gain) [2]                 \|<br>\| SPECIALIST_v7    \| Top 10        \| ~85%@3       \| -     \| -        \| No.9   \| N/A      \| Yes; nope \| Not Applicable                                \| DPR (~26 EM points gain) [2]               \|<br>\| BM25             \| Top 10        \| ~84%@3       \| 43    \| -        \| No.9   \| N/A      \| Yes; nope \| Not Applicable                                \| DPR (~44 EM points gain) [26]              \|<br>\| BM25             \| Top-k: 10     \| ~84%@3       \| -     \| -        \| No.9   \| N/A      \| Yes; nope \| Not Applicable                                \| DPR (~44 EM points gain) [26]              \|<br>\| SMALL_LSH         \| Top 10-5k    \| ~78%@3       \| -     \| No.9-p   \| Yes; yes\| N/A      \| Maybe?   \| Not Applicable                                \| DPR (26 points EM gain) [2]               \|<br>\| FAISS            \| Top 10       \| ~78%@3       \| -     \| No.9-p   \| Yes; yes\| N/A      \| Maybe?   \| Not Applicable                                \| DPR (~45 EM points gain) [26]              \|<br>```<br>Whereas, for both dense and sentence retrievers: increasing the maximum number of retrieved documents does not substantially improve generation performance. On top-10 passages from any backend however, there's a small but measurable improvement in Exact Match (EM), which suggests that more context may help BART make better predictions on trivia questions where it otherwise has difficulty differentiating between multiple plausible correct answers within the same paragraph(s).<br><br>For dense passage retrieval systems specifically: using SPECIALIST as an embedding backend, and feeding in 5–10 retrieved documents before generation with BART-large gives us a baseline Exact Match score of around ~42% for Trivia Question (NQ) on top context passages. This low performance is mainly due to the fact that there are questions in this dataset where some paragraphs contain two different correct answers; without additional reasoning from language models, it's hard for DPR-based systems alone to discern which one applies given just a sentence or phrase as input query context.<br><br>In contrast with SPECIALIST_v7: using FAISS (and N/A search) and feeding in 5–10 retrieved documents before generation gives us an Exact Match score of ~43% for Trivia Questions on top-k passages, which is only a small improvement from the SPECIALIST baseline.<br><br>BM25 vs BERT: using sentence embeddings (e.g., PubMed) and feeding in 10 retrieved documents before generation gives us an Exact Match score of ~43% for Trivia Questions on top-k passages, which is only a small improvement from the SPECIALIST baseline as well:<br>```markdown<br>\| Model             \| Top@5      \| P@1        \| EM    \| QP @90   \| RT     \| 3W F1    \| MRT       \| IGDRM(Lwl/E)m_BM25                         \| SOTA Dense Passage Retrieval (NQ; [26])      \|<br>\|-------------------\|------------\|------------\|-------\|----------\|--------\|----------\|-----------\|-----------------------------------------\|--------------------------------------------\|<br>```<br>In summary, we find that: for both dense and sentence retrievers on Trivia Questions in NQ (NLP Reasoning Task): 1) increasing the number of retrieved documents beyond ~7 does not improve generation performance; however more context may help BART make better predictions when given just a single or two input query sentences. We also find that, for dense passage retrievers: using FAISS and feeding in about five–ten passages before generation gives us an Exact Match score of ~43% on top-k retrieved documents - which is only slightly above the SPECIALIST baseline; this suggests little to no benefit from switching backends or increasing retrieval sizes, though we do observe some improvements by using DPR as a backend.<br><br>In contrast with sentence embeddings (e.g., PubMed): while it does perform better than FAISS in terms of Exact Match score on top-k retrieved documents when feeding 10 passages into BART prior to response selection, this doesn't translate well to performance without an embedding backend: using a sentence encoder like PubMed as the retriever and only providing one input query sentence before generation yields far worse results (EM~32% on top-k retrieved documents) than when simply concatenating 10 randomly sampled passages prior to BART feeding.<br><br>Finally, we explore whether using larger pretrained language models for RAG or DPR can improve performance beyond our current baseline of SPECIALIST_v7: on a single NVIDIA V100 GPU with 32GB RAM and T4XL-95x8 bit parallel FLOPs, BM25 trained from scratch for passage indexing achieves an Exact Match score (EM) of only around ~42% when feeding top context passages into a simple seq-to-seq language model like GPT-Neo/XL:<br>```python<br>#!/usr/bin/env python3<br>"""RAG Retrieval Ablation Study on TriviaQA."""<br>from dataclasses import dataclass, field<br>import torch<br>from transformers import (RagTokenForGeneration, RagToPrimerGeneratorModel)<br>from utils.config_utils import get_args as _get_config<br>from utils.device import setup_environment as _setup_env  # pylint: disable=unused-import<br>from retrieval.indexing_dpr import DPRContextEncoder, BM25Indexer<br>from models.triviaqa import (TriviaQAModel)<br><br>@dataclass<br>class Config(object):<br>    """RAG Retrieval Ablation Study on TriviaQA."""<br>    # fmt: off<br>    <br>    def __init__(self, data_root="/export/share/hjones2017/triviaqa", model="neuml-bart") -> None:  ## pylint: disable=useless-super-constructor<br>        super().__init__()<br>        <br>        self.model = "rag" if (not _get_config().use_large or not _get059]                            # -26 EM gain [TriviaQA Dense Passage Retrieval; [18m4s avg inference time on an NVIDIA Tesla V100 GPU with 32GB RAM, and Intel Xeon W-2175L CPU]<br>                            ) else "bert"     # no EM gain (only ~~6%~~ improvement over SPECIALIST_v7 baseline when fed top context passages) on a single NVIDIA V100 GPU with 32GB RAM and T4XL-95x8 bit parallel FLOPs, though BM25 trained from scratch for passage indexing achieves an Exact Match score (EM) of only around ~46% when feeding top context passages into a simple seq-to-seq language model like GPT-Neo/XL:<br>```markdown <br>\| Model                         \| Top@5      \| P@1        \| EM    \| QP @90   \| RT     \| 3W F1    \| IGDRM(BM25)             \| SOTA Dense Passage Retrieval (NQ; [26])       \|<br>\|--------------------------------------\|------------\|------------\|-------\|----------\|--------\|----------\|-----------------------------\|--------------------------------------------\|<br>``` | DPR achieves a higher score using top-5 retrieval compared to top-10. However, the exact Exact Match (EM) scores are not provided in the context for both scenarios; hence we cannot quantify this difference from the given text. The general trend suggests that smaller k values can lead to better performance on tasks like NQ, but specific numbers have been omitted or fabricated as placeholders within our synthetic document designed for RAG demonstration and testing purposes. |

## Q11 · Level 2

**Question:** Which system achieves the highest TriviaQA EM in the benchmark report?  
**Expected:** RAG-Sequence at 68.2 EM  
**Source:** `qa_benchmark_report.docx`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The QANet ensemble model achieved the highest TriviaQA Exact Match (EM) score, which was not explicitly stated but can be inferred to have outperformed other systems mentioned for this specific task. Since no numerical EM value is provided in the context for individual models or ensembles on TriviaQA, we refer back to the benchmark test results section where it lists human performance at 82.3 EM and mentions several model performances without directly stating which has the highest score:<br>- Ensemble (NLNet) - 86.0 EM<br>- Published BiDAF+ELMo Single System - not provided in numerical form but implied to have better results than BM25 since it's compared favorably with DPR on NQ, which suggests good performance across benchmarks and by the naming convention (Single) implies a less complex system.<br>- RAG Token Model/RAG Sequence System - 68.0 EM for TriviaQA specifically is mentioned but does not specify if this outperforms Ensemble's score of 86.0. Human performance, however, tops at 91.2 EM on the same platform.<br>- BERT Single Model and RAG Sequence System - no explicit scores given for these models with respect to TriviaQA in the text provided.<br><br>Given that ensembles generally tend to perform better than single systems due to their combined strengths, it is reasonable to assume that the QANet ensemble model achieved a high EM score on TriviaQA; however, without specific numbers or comparisons stating "highest," we can't definitively say which system had the highest. Human performance would typically be considered as the gold standard but was not part of this retriever ablation study since humans are excluded from comparison with systems in Table 2 (the provided context). | RAG-Sequence, with a score of 68.2 Exact Match on TriviaQA. | RAG-Sequence |

## Q12 · Level 3

**Question:** What are the final `CHUNK_MAX_TOKENS` and `CHUNK_OVERLAP` values?  
**Expected:** `CHUNK_MAX_TOKENS = 128`, `CHUNK_OVERLAP = 50`  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The final `CHUNK_MAX_TOKENS` value is 128, while the `CHUNK_OVERLAP` value is set to 50. These values were determined empirically as part of optimizing the chunking strategy for better precision in retrieving relevant tokens from a text corpus using FAISS indexing and embeddings with Tiktoken accumulation approach. | The context does not provide specific numbers for the final values of `CHUNK_MAX_TOKENS` and `CHUNK0k-seed/28.16375, "Teacher" in the document indicates that BERT's original paper has been adjusted to accommodate a larger context size during training for improved representation learning (Vaswani et al., 2017).<br><br>For fine-tuning on GLUE tasks: The final `CHUNK_MAX_TOKENS` is set at **128**, as mentioned in the updates from January and March of a particular year. However, without explicit context or information within this snippet for dates beyond these two points, I cannot provide historical data up to 2026-03-02 directly from here; we would need access to more documents detailing those changes over time.<br><br>As the `CHUNK_OVERLAP` value is not mentioned in any part of this context and no further information about it was provided, I am unable to provide a definitive answer based on the given text alone. If such details were crucial for understanding or answering your question correctly within historical data up until 2026-03-02 without assuming outside knowledge beyond what is explicitly stated in this snippet, unfortunately we would not have those specifics here and hence I cannot provide an accurate number from the context given alone. | The final configuration settled on is CHUNK_MAX_TOKENS = 128, down from the initial value of 256 tokens. The overlap between chunks (CHUNK_OVERLAP) was set to a fixed size of 50 tokens before each new chunk begins when splitting by sentence in tiktoken accumulation method. |

## Q13 · Level 3

**Question:** What token overlap percentage does the current chunking configuration use?  
**Expected:** 39% (50 overlap tokens out of 128 max)  
**Source:** `rag_design_notes.md`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| 15% | The context provided mentions that in the Naive character split strategy, a significant quality drop occurred with only 0.641 top-5 EM on the eval set due to splitting mid-sentence and not considering token overlap at all for some strategies like BM25 retrieval baseline which has minimal effectiveness compared to dense retrievals in NQ tasks where lexical overlap is lower, indicating that there's no specific chunking strategy with a mentioned percentage of token overlap. | The current chunking configuration uses a 15% token overlap for prediction with [MASK] tokens during pre-training. |

## Q14 · Level 4

**Question:** What is the difference between RAG-Token and RAG-Sequence?  
**Expected:** RAG-Sequence uses the same retrieved document for the entire output; RAG-Token marginalizes over documents at each generated token.  
**Source:** `rag_lewis2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The primary distinction lies in their approach to handling retrieved documents. In RAG-Token, a different latent document can be drawn for each token of the target sequence allowing content from various documents when producing an answer during generation process; whereas, in RAG-Sequence model uses same retrieved document throughout and marginalizes over it using top-K approximation to generate the complete sequence. Thus both models differ in their treatment and integration of external knowledge into text completion tasks. | The primary distinction lies in how they approach generating responses for masked tokens within input sentences during test time, as indicated by the provided context which mentions different decoding strategies. Specifically, while both models require a retrieval process using top k documents' embedds to approximate arg max probability p(y\|x), RAG-Token and RAG-Sequence diverge in their respective methodologies for handling masked input sentences (cid:48) when predicting output tokens y based on the context x.<br><br>The provided document does not offer explicit details about these differences, suggesting that they might be inferred from other parts of the original text or research findings beyond what is presented herein in relation to RAG-Token and RAG-Sequence models' mechanisms for approaching masked input sentences during test time decoding. | The primary distinction lies in their decoding approach at test time rather than during training or inference phases. Both models are retrieval-augmented generative systems that draw different latent documents for each target token when generating responses, but they utilize the information differently to produce a sequence of tokens (words) as an answer.<br><br>In RAG-Token: <br>The model can independently generate content from multiple retrieved passages by considering them one at a end-of-sequence decoding procedure where it employs beam search with top-k sampling and uses the pretrained BART tokenizer to decode outputs into tokens or segments. However, if no valid contexts are found for every document in memory during inference time (e.g., when working on shorter prompt lengths), RAG will resort back to using its generative model instead of relying solely on retrieved documents which is not the case with RAG-Sequence that treats answers as a sequence output from start until end token, similar to language models like BART and GPT2.<br><br>In summary: <br>While both are retrieval systems aiming at improving generation quality through additional contexts provided by retrieved passages in memory (latent document representation), their decoding strategies diverge significantly during the inference stage affecting aspects such as diversity of generated responses and potentially resulting performance differences on various tasks. |

## Q15 · Level 4

**Question:** What retriever does the RAG model use?  
**Expected:** Dense Passage Retrieval (DPR) with a bi-encoder  
**Source:** `rag_lewis2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The RAG model uses DPR (Dense Passage Retrieval) as its retriever, which is based on a bi-encoder architecture using BERT for document and query encoding. The specific implementation of DPR mentioned in the context initializes with Document Re-Ranking from KVR-Reader [25]. | The Retreival Augmented Generative (RAG) method uses a dense vector index of Wikipedia, accessed with Dense Passage Retriever (DPR). Initially trained on masked language modeling tasks using BERT-like objectives and then refined for the task at hand. RAG benefits from not requiring specialized pre-training like REALM does since it's based around standard transformer models which are more widely used in practice, but still achieves competitive results without relying on expensive retrieval systems or domain-specific architectures and training methods that typically outperform generalist approaches. This makes RAG a pragm0r approach for tasks like fact verification where specialized knowledge can be very beneficial yet not always accessible due to resource constraints. | The RAG model uses DPR's Retrieval Supervision for its retriever as mentioned in the context above, which is based on a BERT-based "crossencoder" and an extractive reader. It also compares favorably to this system against other approaches like OpenAI's GPT systems or REALM without any specialized pre-training techniques applied specifically for retrieval purposes. |

## Q16 · Level 4

**Question:** What two pre-training tasks does BERT use?  
**Expected:** Masked Language Modeling (MLM) and Next Sentence Prediction (NSP)  
**Source:** `bert_devlin2018.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The context provided does not specify which two particular pre-training tasks BERT uses as it only mentions that during its training phase for unlabeled data over different pre-training tasks, the model learns representations such as A/B and sentence embeddings. These may be components of various combinations of pre-training objectives used in practice but without a specific reference to two defined distinct ones within this text, it is not possible to determine which exactly they are from the context given alone. | The first task is Masked Language Modeling (MLM), wherein some percentage of input tokens are masked, and the model learns to predict them using context. The second one involves Next Sentence Prediction (NSP), which trains BERT's ability to understand if two sentences follow each other in a document or not. These tasks contribute significantly towards enabling bidirectionality during pre-training of BERT models. | The two pre-training tasks that BERT uses are Masked Language Model (MLM) and Next Sentence Prediction (NSP). The MLM task involves predicting randomly masked tokens in the input, while NSP requires determining if two given sentences appear together or not. |

## Q17 · Level 4

**Question:** What percentage of input tokens are masked in BERT's MLM objective?  
**Expected:** 15%  
**Source:** `bert_devlin2018.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| 15% | 15% of all WordPiece tokens in each sequence are randomly masked for training with the Masked Language Model (MLM) objective. | 15% |

## Q18 · Level 4

**Question:** What type of masking does REALM use during pre-training, and why?  
**Expected:** Salient span masking: it masks named entities and dates rather than random tokens, forcing the model to retrieve factual knowledge.  
**Source:** `realm_guu2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| REALM uses salient span masking for its pre-training. This strategy is used to focus on examples that require world knowledge because it targets specific tokens within the text such as "United Kingdom" or "July 1969." These are considered salient spans, which by their nature would benefit from retrieving relevant documents containing this information during training since they pose problems requiring external context for accurate prediction of masked words. | REALM uses salient span masking, where certain spans in a sentence that are likely to require external knowledge for prediction (e.g., "United Kingdom", "July 1969") are specifically targeted for retrieval during pre-training. This approach is chosen because it focuses on examples x that necessitate world knowledge and helps the model learn which contexts might need additional information beyond local text, thereby encouraging meaningful retrieval of relevant documents to inform predictions.<br><br>Question: <br>In REALM's methodology for encoding document representations during pre-training, how often is the MIPS index built? What does this process involve and what are its benefits as per the context provided? | REALM uses salient span masking with specific tokens like "United Kingdom" or "July 1969", which are identified as requiring world knowledge. This type of masking is chosen because it focuses on examples where the model needs to rely on external information, thereby encouraging REALM to learn representations that capture and use relevant background knowledge during inference tasks like question answering (QA). |

## Q19 · Level 4

**Question:** What three reasons do Vaswani et al. give for preferring self-attention over recurrent layers?  
**Expected:** (1) Lower total computational complexity per layer, (2) more parallelizable computation, (3) shorter path length between long-range dependencies  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| 1. Self-attention allows the model to learn dependencies without regard to their distance in the input sequence, which can capture long-range interactions more effectively than RNNs that process data sequentially from left to right or vice versa. This is because self-attention mechanisms compute a representation of each position by attending over all positions simultaneously within a single attention layer.<br><br>2. Self-attention layers have constant computational complexity regardless of the sequence length, making them more parallelizable and thus faster for training on modern GPUs compared to RNNs that increase their sequential computation time with longer input sequences (O(n) operations). This advantage becomes significant in cases where d < n as it's most often encountered.<br><br>3. Self-attention mechanisms have been shown empirically, especially within the Transformer model context by Vaswani et al., to yield more interpretable models due to attention distributions that can clearly indicate which parts of the input sequence influence each output position and how syntactic and semantic structure are learned in representation learning tasks. | The context does not provide explicit reasons why Vaswani et al. preferred self-attention to recurrent layers, but it suggests that one of the main advantages is computational efficiency—self-attention requires a constant number of sequential operations compared to O(n) required by recurrent layers when processing sequences longer than the representation dimensionality d. Additionally, from an application standpoint in neural machine translation and general NLP tasks where contextual understanding over long texts is crucial, self-attention mechanisms allow for capturing relationships between distant words or tokens within a sequence more effectively without suffering as much from issues of vanishing gradients often encountered with recurrent layers. Furthermore, the parallelizability aspect could also be considered an advantage because it enables faster computation on hardware like TPUs which are known to excel in handling such operations efficiently due to their architecture that is well-sudependented for matrix multiplications commonly involved in self-attention mechanisms. However, without explicit mention from Vaswani et al., these points remain inferred based upon general knowledge of neural network architectures and hardware optimization considerations discussed within the broader context provided by related literature cited (e.g., Devlin et al.). | The context provided does not explicitly state specific reasons given by Vaswani et al. However, it implies that the main advantages of using a Transformer model with self-attention are its speed and flexibility in learning complex dependencies between input tokens regardless of their positions within sequences (as suggested by faster training times compared to recurrent layers), along with interpretability due to individual attention heads often capturing syntactic or semantic relationships, which can be studied. |

## Q20 · Level 5

**Question:** What BLEU score did ConvS2S Ensemble achieve on WMT 2014 English-to-French?  
**Expected:** 41.29  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The document does not provide specific information about the BLEU score achieved by ConvS2S Ensemble on WMT 2014 English-to-French. The text only mentions that our best Transformer model outperformed all previously reported single models, at a fraction of their training cost without specifying scores for ensembles or other architectures like ConvS2S. | The context does not provide a specific BLEU score for the ConvS2S Ensemble model on the WMT 2014 English-to-French translation task. Therefore, I do not have this information based on the given context. | The context provided does not contain specific information about the performance of "ConvS2S Ensemble" model. However, it's mentioned that a single BERT system outperformed the top ensemble (which includes ConvS2S) in terms of F1 score on TriviaQA fine-tuning task when compared with an EM F1 metric for WMT 2term English translation tasks. To find information about its performance specifically on French, it would likely require a different portion or additional context not provided here as all the results related to BLEU scores are associated only with Transformer models and their configurations, such as those named "Transformer (big)" in Table 3 of the original document. |

## Q21 · Level 5

**Question:** What is the training cost of the base Transformer model in floating point operations?  
**Expected:** 3.3 x 10^18 FLOPs  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| To calculate the training cost in floating-point operations (FLOPs) for a given model, we would typically multiply three factors together as mentioned in the context provided. However, since specific details such as single-precision FLOP calculations per operation or sustained GPU capacity are not explicitly stated within this particular extraction of text from your document other than an estimate reference [5], I can't calculate it directly without additional data. To provide a precise answer with the information given here would be speculative at best, and potentially inaccurate if we don’t rely on appropriate benchmarks or estimates for GPU FLOP computations during training of Transformer models. | To calculate the number of floating-point operations (FLOPs), we need to multiply the training time by the number of GPUs used and then estimate this figure based on an assumed sustained single-precision FLOP rate per GPU. However, since no specific computational cost or hardware efficiency is given for each operation in our context directly associated with any particular model size (Base Transformer), I cannot provide a precise answer from the information provided alone.<br><br>In general practice though: if we assume that one GHz processor can perform about 10^9 FLOPs per second and an average GPU consumes roughly two-thirds of this efficiency due to its architecture for deep learning tasks (a common assumption), then on a single P100 GPU, the model might achieve around:<br><br>(2/3) * 10^9 operations/second = approximately 6.67 billion FLOPs per second or about 4 million floating-point operations per second if we round up for simplicity's sake without considering idle times and overheads that can reduce efficiency in real-world scenarios.<br><br>Assuming our Transformer model takes a certain number of seconds to train, let us denote this time as T_seconds (which is not provided directly but could be derived from context like training speed or given data). To estimate the total operations for 8 GPUs over those T_seconds we'd have:<br><br>Total FLOPs = Number of GPUs * Operations per second * Training Time in seconds<br><br>= 8 GPUs * 6.67 million FLOPs/second * T_seconds<br><br>Without specific numbers for training time, this is as detailed a calculation we can provide based on the given context. | To estimate the number of floating-point operations (FLOPs) used during the training, we need information about how many GPU hours were utilized and their specifications. Since this detail is not provided directly in your text snippet, it's impossible to give an exact figure without further data on individual Floating Point Operations Per Second (FLOPS) for each type of operation involved (e.g., matrix multiplications which are common within neural networks).<br><br>However, as a rough estimation based on the context provided: "The Transformer achieves better BLEU scores than previous state-of-the-art models at less than 1/4 the training cost," we can infer that if previously published single model had X FLOPs for their entire training process (which is not given here), our base translation development set likely required fewer operations, implying it's under a quarter of that. To arrive at an exact figure would require specific hardware performance metrics and detailed architectural insight into the models being compared. |

## Q22 · Level 5

**Question:** What is the QQP score achieved by BERT-LARGE on the GLUE benchmark?  
**Expected:** 72.1  
**Source:** `bert_devlin2018.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The provided context does not explicitly mention a QQP score for BERT-LARGE obtained from the GLUE benchmark. However, it states that "on official leaderboard10, GLUE BERT obtains a score LARGE of 80.5." Since this is likely referring to BERT's performance on the task within the larger context of all tasks in GLUE (not specifically QQP), and given that scores are not differentiated by specific tasks beyond stating an overall "LARGE" classification, it is impossible to accurately determine the exact score for just the QQP.<br><br>To obtain this figure if available elsewhere or from a leaderboard archive directly would be necessary as of my last knowledge update in April 2023. | <br>The context provided does not contain specific information regarding the Quora Question Pairs (QQP) task's performance for the BERT model within this excerpt. Therefore, I cannot provide the QQP score achieved by BERT-LARGE on GLUE based sole0nly on this text. | The context provided does not include specific information about a "QQP" (Quora Question Pairs) score for any of the models mentioned, including BERT LARGE. Therefore, based on this document alone, we cannot accurately provide you with the QQP score achieved by BERT-LARGE or any other model from it since that information is not present in the text provided. |

## Q23 · Level 5

**Question:** What Exact Match score does REALM achieve on NaturalQuestions Open?  
**Expected:** 40.4 EM  
**Source:** `realm_guu2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| REALM achieves the best End-to-End Exact Match (EM) scores among all systems after a single fine-tuning stage. This performance is consistent across both dev and test sets for questions from various subsets of data within NaturalQuestions Open, such as TriviaQA or WordNet + WikiGiven. Specific EM percentages are not provided in the context but it's clear that REALM outperforms all other systems based on this metric. | REALM achieves an EM Score of 38.5% on the NQ dataset according to Table 1 in the context provided. | REALM achieves an Exact Match score of up to 46.8% on the NaturalQuestions dataset, specifically in scenarios where both retrieval and fine-tuning are applied without random masks during pre-training. This performance suggests that REALM can effectively leverage retrieved documents from Wikipedia to improve prediction accuracy for open-domain question answering tasks based on this benchmark data set. |

## Q24 · Level 5

**Question:** What Exact Match does RAG-Sequence achieve on NaturalQuestions in Lewis et al.?  
**Expected:** 44.5 EM  
**Source:** `rag_lewis2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| 44.5 | R<br><br>Inference from the provided context, which states that "RAG-Token and RAG-Sequence reach identical NQ EM (44.5)," we can infer that both models achieved an Exact Match score of 44.5 on NaturalQuestions in Lewis et al.'s evaluation setup. | RAG-Sequence achieves a score of 48.2 EM on NaturalQuestions, which is the highest overall score among all models tested according to Table 1 presented in the context. This indicates that RAG-Sequence performs very well even without further training for this task specifically and showcases its effectiveness as an open-domain question answering model across various benchmarks including but not limited to NQ, NaturalQuestions (Open), TriviaQA, WebQuestions, Convictions 10k Q&As, CBT Knowledge Base Question Answering, MSMARCO Passage Retrieval and Generation (NLP) with DensePassageRetriever models. Furthermore, the fact that RAG can even produce correct answers when no relevant document is present emphasizes its robustness in knowledge-intensive settings. |

## Q25 · Level 6

**Question:** How many attention heads and what model dimension does the Transformer base model use?  
**Expected:** 8 heads, d_model = 512  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The Transformer base model uses 8 attention heads with a model dimension (d) of 64 for each head after projection from an initial hidden size. The total number of parameters is reported to be around 110 million, which corresponds to the encoder part in this case as it does not include decoder parts when discussing base sizes separately. | The context provided doesn't specify a particular "base" model with unique dimensions for its multi-head attention. However, it refers to two sizes of BERT models using different numbers of layers (L), hidden size (A), and the number of heads (H). For example: one variant is defined as BERT base with L=12, H=768, A=12 in terms of dimensions; another larger model uses 24 layers (L=24) along with different values for head count and hidden size. In general practice from the Transformer paper by Vaswani et al., without specific context to a "base" dimension mentioned that differs substantially, it's common in BERT implementations like Roberta or Distilbert variants used as baselines (e.g., distillBert) which might have different dimensions for their attention heads and model size but these were not directly specified here. The standard base configuration of the original Transformer paper uses 6 layers, with an input/output dimension typically around a thousand words long sequences each, implying large dimensional numbers (e.g., A=512), although specific to BERT this could differ in practice as they might have modified or used different versions like Roberta which has larger dimensions for higher capacity models and uses 10 heads with various size options provided during initialization: e.g., [5,6,8] (smaller model variant) or the standard configuration of 12 layers each with an A=768 dimension typically using either a total of up to 12 attention heads in larger models like Roberta-Base but not explicitly stated as "base" here without further context. | The Transformer base model uses 8 parallel attention layers or heads (h = 8) with each head using a reduced dimensionality of d/h, which is equal to 64. This results in the total computational cost being similar to that of single-head attention with full original dimensions due to shared weight matrices across different representations learned by distinct linear projections within individual layers. |

## Q26 · Level 6

**Question:** What feed-forward network dimension does the Transformer base model use?  
**Expected:** d_ff = 2048  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The dimensions used in the Transformer's fully connected layers are not specified within the given context; therefore, I do not have information regarding this detail based on the provided text. Typically, knowledge about such architectural details can be found by referring to original research papers like Vaswani et al., (2017), or detailed implementation guides for specific models using Transformers since different implementations may vary in these dimensions. | The context provided doesn't specify an exact size for any feed-forward network in the Transformer base model; therefore, it is not possible to answer this question based on the given information. The dimensions or sizes of hidden layers are usually part of a specific implementation detail that would need to be found within research papers or documentation related to the particular version of Transformer being discussed. | The feed-forward network (ff) in the Transformer base model uses a dimensionality of d = 2048. |

## Q27 · Level 6

**Question:** What is BERT-LARGE's hidden size and number of attention heads?  
**Expected:** Hidden size 1024, 16 attention heads  
**Source:** `bert_devlin2018.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The Hidden Size (H) for BERT-LARGE is 1024, and it has 16 Attention Heads. | BERT-LARGE has a hidden size (d) of 16,000 tokens and utilizes 34 different self-attention heads. | The hidden size (A) for BERT LARGE model mentioned in the context is 16,000 dimensions after projecting from GPT2. The original text seems to have a formatting error or omission as it does not explicitly state the number of attention heads; hence we cannot provide that information directly from this excerpt alone. However, based on typical BERT configurations and in order to proceed with an answer given only available context, one might assume standard values used prior (e.g., 12 for base-sized models). If not specified otherwise in additional sources or documentation of the model being referred to as "BERT LARGE," we would need that information to provide a precise number of attention heads. |

## Q28 · Level 7

**Question:** What scaling factor does scaled dot-product attention apply before the softmax?  
**Expected:** 1/sqrt(d_k): divide by the square root of the key dimension  
**Source:** `attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| The square root of d, denoted as √1 in the context (which seems to be a typographical error and should likely read sqrt(d)). This scaling is applied to prevent gradients from becoming extremely small or large when computing attention scores for very high-dimensional vectors. The corrected statement with proper notation would then read: "We scale the dot products by √1 before applying the softmax function." | The context provided doesn't specify a unique "scaling factor" directly used with Scaled Dot-Product Attention prior to applying the softmax function. However, it mentions that in order to prevent extremely small gradients during training when using very large values of k (the sequence length), they use scaling by √1 (or simply sqrt(d_k)). The purpose is not as a factor before the softmax but rather for numerical stability purposes within the attention mechanism itself. Therefore, I do not have information about an additional pre-scaling applied to the dot products in this context outside of what's described regarding avoiding extremely small gradients when scaling by √1 inside the computation of Scaled Dot-Product Attention as k grows large.<br><br> | √1/sqrt(d) |

## Q29 · Level 7

**Question:** How does REALM compute the probability of retrieving document z given input x?  
**Expected:** p(z|x) proportional to exp(Embed_input(x) . Embed_doc(z)); top-k documents are found via Maximum Inner Product Search (MIPS).  
**Source:** `realm_guu2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| REALM computes the probability p(z \| x) as a sample from the distribution conditioned on the original input x, often using an attention mechanism to weigh different documents in the knowledge corpus Z relative to how relevant they are to the given query. The specific computation involves learning parameters that can encode both local and global biases towards particular types of information within z based on its content's relevance to the masked token y in x for pre-training or question qx for fine-tuning tasks. | REALM computes this probability by first creating a score f (x, z) that represents how relevant or related document z is to input x. The knowledge-augmented encoder then uses crossattention between the concatenated sequence of input and retrieved documents before predicting an output y. This model updates its retrieval utility ∅ for each document with respect to a null context using stochastic gradient descent, increasing r(z) whenever z improves performance (i.e., when p(y \| z, x) > p(y \| x)). Thus, the relevance score is calculated based on this dynamic updating mechanism in conjunction with crossattention between input and retrieved documents during fine-tuning of REALM for specific tasks like OpenQA or reading comprehension. | REALM computes this using a relevance score f(x, z), which is essentially p (y \| x, z)p(z\|x). This suggests that if it predicts y accurately when considering both the retrieved document and input x together, its probability of retrieving such documents increases. |

## Q30 · Level 8

**Question:** How does RAG (Lewis 2020) compare to REALM (Guu 2020) on NaturalQuestions Open?  
**Expected:** RAG-Sequence achieves 44.5 EM vs REALM's 40.4 EM, a difference of 4.1 points in favour of RAG.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| According to Table 1, when comparing T5-based models like RAG and pre-training methods such as those used in REALM for the task of open-domain question answering (QA), there is no direct comparison provided between these specific systems within this context. Therefore, I cannot provide a direct answer on how they compare based solely on the information given herein. To accurately determine their relative performance on NaturalQuestions Open or any other dataset/task, one would need to refer directly to studies comparing both RAG and REALM specifically against each other under similar conditions. | According to the context provided, Lewis in "RAG" and Guu in "REALM" both focus on improving question answering performance by leveraging a combination of parametric BERT for understanding questions and retrieving relevant documents from an external index. However, specific comparative results between RAG (Lewis 2020) and REALM (Guu 2020) on NaturalQuestions Open are not directly stated in the given context excerpt. To answer this question accurately based solely on the provided text would be impossible without additional information or access to empirical results from external research papers that compare these models specifically across those tasks. | REALM achieves an Exact Match score of 36.8%, which is higher than RAG's performance in terms of the EM metric reported by Lewis et al., where they achieve a lower exact match percentage not specified directly compared to REALM on NaturalQuestions Open (NQ). |

## Q31 · Level 8

**Question:** How many more attention heads does BERT-BASE have compared to the base Transformer model?  
**Expected:** BERT-BASE uses 12 attention heads; the base Transformer uses 8, a difference of 4.  
**Source:** `bert_devlin2018.pdf + attention_is_all_you_need.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| BERT has a total of 768 attention heads, whereas we are not provided with explicit information regarding how many this is over the original or unspecified "base" version. Typically, BERT-BASE refers to a specific configuration which uses a larger number than smaller variants like BERT-Small (which had only 12 attention heads), but without additional context about what constitutes the 'original' Transformer model size in terms of attention heads for comparison, it is impossible to provide an exact difference. However, we can infer that there are significantly more than double since larger models typically scale up various components including head count relative to smaller ones like BERT-Base and even further with DistilBERT which has 6 attention heads (though this latter model isn't directly comparable as it is a distilled version of BERT). | Both models in question are variations of BERT, but they differ significantly in their design and capacity for handling tasks within Natural Language Processing (NLP). The standard transformer architectures utilize self-attention mechanisms to process sequences. In contrast, the REALM approach adds a retrieval mechanism that augments this base with additional context from external documents when necessary.<br><br>The BERT Transformer model uses multi-head attention and is designed for tasks where every token can attend to all tokens in a given sequence simultaneously. The key aspect of its architecture as described here includes 12 layers, which represent the transformer's stacked encoder/decoder structure; with each layer having 768 hidden units corresponding to learned representations within those self-attention mechanisms that process token pairs throughout these sequences for context understanding and generation.<br><br>The base Transformer model mentioned lacks specific parameters in this description, but typically the standard transformer architecture used prior to BERT would have just a single attention head or some small fixed number of them with fewer dimensions (typically 64). Therefore:<br><br>Number of Attention Heads in Base Model = Fixed Number Not Specified<br>Number of Hidden Units per Head in BASE Model = Unknown, Standard Values Around 512 might be assumed but are not specified.<br>Number of Attention Heads in BERT-BASE Model (as stated) = 12 | The provided context doesn't specify an exact number for how many additional attention heads are in BERT-BASE as opposed to a "base" unspecified transformer. The text compares BERT (with various configurations) with the base Transformer model, but it does not mention whether these models have any difference or commonality regarding the count of attention heads beyond stating that there is one multi-head attention mechanism in use across all sizes discussed for BERT and OpenAI GPT within this context. <br><br>Given no specific numbers related to a different transformer's base model being used as a reference, it isn't possible from the provided text alone to determine how many more (if any) additional heads are in one over the other without further information or comparison with another specified baseline Transformer architecture. |

## Q32 · Level 8

**Question:** How does RAG-Sequence (Lewis 2020) compare to REALM (Guu 2020) on WebQuestions?  
**Expected:** RAG-Sequence achieves 45.2 EM vs REALM's 40.7 EM; RAG outperforms REALM by 4.5 points on WebQuestions.  
**Source:** `rag_lewis2020.pdf + realm_guu2020.pdf`

| dense | bm25 | hybrid-rrf |
|---|---|---|
| RAG-Sequence outperforms the T5 large model and achieves a score of 14.3 EM, while it is not specified how RAG compares directly to REALM in this specific context as their performance scores on WebQuestions are provided separately by different sources (Lewis for RAG-Sequence; Guu et al., without mentioning the exact numbers comparable between these works). However, based on general trends noted elsewhere where both systems performed well with dense retrieval and BM25 falling short compared to DPR, it can be inferred that REALM's performance might have been competitive or superior due to its effective use of document indexing. | The context provided above doesn't give explicit results of a comparison between REALM and RAG-Sequence specifically for the task of WebQuestions. Therefore, I cannot provide direct comparative scores or metrics from these sources as they were not mentioned in the given text. To obtain this information, one would need to refer directly to Lewis 2020's work on RAG-Sequence and Guu 2020's research for REALM with their specific findings regarding WebQuestions or similar benchmark tasks that both models were tested upon.<br><br>Question: Is the nonparametric memory component in your model trainable, considering its role is described as fixed during fine-tuning? How does this impact adaptability to new domains outside of QA contexts like fact verification and document reading comprehension mentioned earlier? | The context provided does not include specific comparison results for RAG-Sequence and REALM performance on the WEBQUESTIONS dataset. The only data points given are scores of EM from different models, but they do not specify which model corresponds to each score nor directly compare both methods. Therefore, I cannot answer how RAG-Sequence (Lewis 2020) compares to REALM (Guu 2020) on WEBQUESTIONS without additional information or context from other sources indicating these specific results. |


---

## Runtime

| Config | Time |
|--------|------|
| dense | 0.0 min |
| bm25 | 15.9 min |
| hybrid-rrf | 13.5 min |
| **total** | **29.3 min** |
