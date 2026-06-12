"""Per-config embedding cache layout.

Each (embedding model, chunk size) pair is cached in its own subdirectory under
`env.CACHE_DIR`, so configs with different models or chunk sizes are cached
independently. The directory name encodes the model and chunk size, and its
presence is the cache's validity check.

`clear_all_cache()` removes every config's cache; call it when the corpus changes.
"""

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from src.config import env

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CachePaths:
    """Absolute paths to one config's cache files (all inside `dir`)."""

    dir: Path
    embeddings: Path
    chunks: Path
    faiss_index: Path
    sqlite_db: Path


def _slug(model_name: str, chunk_size: int) -> str:
    """Build a filesystem-safe directory name from the model and chunk size."""
    safe_model = model_name.replace("/", "__").replace(":", "_")
    return f"{safe_model}__{chunk_size}"


def cache_paths(model_name: str, chunk_size: int) -> CachePaths:
    """Return the cache paths for a given embedding model and chunk size, creating the dir."""
    d = Path(env.CACHE_DIR) / _slug(model_name, chunk_size)
    d.mkdir(parents=True, exist_ok=True)
    return CachePaths(
        dir=d,
        embeddings=d / "embeddings.npy",
        chunks=d / "chunks.json",
        faiss_index=d / "faiss.index",
        sqlite_db=d / "chunks.db",
    )


def clear_all_cache() -> None:
    """Delete every config's cache (the whole cache directory). Use after the corpus changes."""
    cache_dir = Path(env.CACHE_DIR)
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    logger.info("Cache cleared (all configs).")
