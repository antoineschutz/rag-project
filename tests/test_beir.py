import pytest

pytest.importorskip("pytrec_eval")  # eval-only dep; skip when not installed (e.g. base CI)

from src.evaluation.beir import evaluate, retrieve_all
from src.retrieval.retriever_bm25 import RetrieverBM25


def test_perfect_ranking_scores_one():
    qrels = {"q1": {"d1": 1}, "q2": {"d2": 1, "d3": 1}}
    run = {"q1": {"d1": 0.9, "d9": 0.1}, "q2": {"d2": 0.9, "d3": 0.8, "d9": 0.1}}
    m = evaluate(qrels, run, k_values=(1, 10))
    assert m["ndcg@10"] == 1.0
    assert m["mrr"] == 1.0
    assert m["recall@100"] == 1.0


def test_missing_relevant_lowers_recall():
    qrels = {"q1": {"d1": 1, "d2": 1}}
    run = {"q1": {"d1": 0.9}}  # retrieved one of the two relevant docs
    m = evaluate(qrels, run, k_values=(10,))
    assert m["recall@100"] == 0.5


def test_retrieve_all_maps_results_to_doc_ids():
    corpus = {
        "d1": "neural networks trained with gradient descent",
        "d2": "a recipe for cooking pasta",
        "d3": "deep learning optimization methods",
    }
    docs = [{"text": t, "source": did} for did, t in corpus.items()]
    run = retrieve_all(RetrieverBM25(docs), {"q1": "gradient descent neural networks"}, top_k=3)
    assert set(run["q1"]).issubset(set(corpus))  # results are doc ids
    assert "d1" in run["q1"]  # the relevant doc is retrieved
