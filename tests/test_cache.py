import pytest

from src.utils import cache as cache_mod


@pytest.fixture
def tmp_cache_dir(monkeypatch, tmp_path):
    """Point env.CACHE_DIR at a throwaway dir so tests never touch the real ./cache/."""
    d = tmp_path / "cache"
    monkeypatch.setattr(cache_mod.env, "CACHE_DIR", str(d))
    return d


def test_cache_paths_slug_sanitizes_model_and_chunk(tmp_cache_dir):
    paths = cache_mod.cache_paths("BAAI/bge-small-en-v1.5", 128)
    # "/" and ":" are escaped, chunk size appended
    assert paths.dir.name == "BAAI__bge-small-en-v1.5__128"
    assert paths.dir.parent == tmp_cache_dir
    assert paths.dir.exists()  # created on access
    assert paths.embeddings.name == "embeddings.npy"


def test_cache_paths_distinct_per_model_and_chunk(tmp_cache_dir):
    a = cache_mod.cache_paths("m", 128)
    b = cache_mod.cache_paths("m", 256)  # different chunk size
    c = cache_mod.cache_paths("other", 128)  # different model
    assert len({a.dir, b.dir, c.dir}) == 3  # coexist instead of overwriting


def test_clear_all_cache_removes_the_dir(tmp_cache_dir):
    cache_mod.cache_paths("m", 128)  # creates a subdir
    assert tmp_cache_dir.exists()
    cache_mod.clear_all_cache()
    assert not tmp_cache_dir.exists()
