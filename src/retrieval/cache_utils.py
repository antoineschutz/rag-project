import logging
import os
from pathlib import Path

from src.config import config

logger = logging.getLogger(__name__)

_STAMP = "embed_model.txt"


def cache_matches(model_name: str) -> bool:
    """Return True if the on-disk cache was built with model_name."""
    p = Path(config.CACHE_DIR) / _STAMP
    return p.exists() and p.read_text().strip() == model_name


def write_cache_model(model_name: str) -> None:
    """Record which model was used to build the current cache."""
    (Path(config.CACHE_DIR) / _STAMP).write_text(model_name)


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
