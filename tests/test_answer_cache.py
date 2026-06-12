import json

from src.utils.answer_cache import AnswerCache


def test_key_is_order_independent_and_distinguishing():
    # same content, different key order -> same key (json sort_keys)
    assert AnswerCache.key("q", {"a": 1, "b": 2}) == AnswerCache.key("q", {"b": 2, "a": 1})
    # query and cfg both contribute to identity
    assert AnswerCache.key("q1", {"a": 1}) != AnswerCache.key("q2", {"a": 1})
    assert AnswerCache.key("q", {"a": 1}) != AnswerCache.key("q", {"a": 2})


def test_get_set_and_persistence(tmp_path):
    p = tmp_path / "answers.json"
    cache = AnswerCache(p)
    key = AnswerCache.key("q", {"retriever": "dense"})

    assert cache.get(key) is None
    cache.set(key, "hello")
    assert cache.get(key) == "hello"

    # a fresh instance reads the persisted file
    assert AnswerCache(p).get(key) == "hello"
    assert json.loads(p.read_text())[key] == "hello"


def test_missing_file_starts_empty(tmp_path):
    cache = AnswerCache(tmp_path / "does_not_exist.json")
    assert cache.get("anything") is None


def test_set_creates_parent_dirs(tmp_path):
    p = tmp_path / "sub" / "dir" / "answers.json"
    AnswerCache(p).set("k", "v")
    assert p.exists()
