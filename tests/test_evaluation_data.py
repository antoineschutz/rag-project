from src.evaluation.qa_pairs import QA_PAIRS

REQUIRED_KEYS = {"id", "level", "question", "expected", "source", "keywords"}


def test_qa_pairs_shape_and_ids():
    assert len(QA_PAIRS) == 32
    assert [q["id"] for q in QA_PAIRS] == list(range(1, 33))  # unique + contiguous
    for q in QA_PAIRS:
        assert REQUIRED_KEYS <= set(q)
        assert isinstance(q["keywords"], list)


def test_keyword_scored_subset_is_29():
    # questions with non-empty keywords form the accuracy_29 metric
    assert sum(1 for q in QA_PAIRS if q["keywords"]) == 29
