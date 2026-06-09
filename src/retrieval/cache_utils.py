import logging
import os
from pathlib import Path

from src.config import config

logger = logging.getLogger(__name__)

_STAMP = "embed_model.txt"


def cache_matches(stamp: str) -> bool:
    """Return True if the on-disk cache stamp matches stamp (model + chunk size)."""
    p = Path(config.CACHE_DIR) / _STAMP
    return p.exists() and p.read_text().strip() == stamp


def write_cache_model(stamp: str) -> None:
    """Write stamp (model + chunk size) to the cache stamp file."""
    (Path(config.CACHE_DIR) / _STAMP).write_text(stamp)


def clear_cache() -> None:
    """Delete all embedding cache files so the next run rebuilds from scratch."""
    for f in [
        config.EMBEDDINGS_PATH,
        config.CHUNKS_PATH,
        config.FAISS_INDEX_PATH,
        config.SQLITE_DB_PATH,
    ]:
        if os.path.exists(f):
            os.remove(f)
    stamp = Path(config.CACHE_DIR) / _STAMP
    if stamp.exists():
        stamp.unlink()
    logger.info("Cache cleared.")
