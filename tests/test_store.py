import pytest

from src.store.sqlite_store import ChunkStore


CHUNKS = [
    {"text": "first chunk", "source": "doc.pdf"},
    {"text": "second chunk", "source": "doc.pdf"},
    {"text": "third chunk", "source": "other.pdf"},
]


@pytest.fixture
def store(tmp_path):
    return ChunkStore(str(tmp_path / "test.db"))


def test_exists_false_on_empty_db(store):
    assert store.exists() is False


def test_exists_true_after_save(store):
    store.save(CHUNKS)
    assert store.exists() is True


def test_save_and_load_roundtrip(store):
    store.save(CHUNKS)
    loaded = store.load()
    assert loaded == CHUNKS


def test_save_overwrites(store):
    store.save(CHUNKS)
    store.save(CHUNKS[:1])
    assert store.load() == CHUNKS[:1]


def test_load_order_preserved(store):
    store.save(CHUNKS)
    loaded = store.load()
    assert [c["text"] for c in loaded] == [c["text"] for c in CHUNKS]
