import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import BASE


class Embedder:
    def __init__(self, model_name: str = BASE.embed_model, device: str | None = None) -> None:
        """Load the sentence-transformer embedding model. device=None auto-selects (mps/cuda/cpu)."""
        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device=device)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        """Encode a list of text strings into a (N, dim) embedding matrix."""
        try:
            return np.array(self.model.encode(texts, show_progress_bar=True))
        except MemoryError:
            raise MemoryError(
                f"Out of memory while embedding {len(texts)} documents. "
                "Try reducing chunk_max_tokens in PipelineConfig (src/config/pipeline.py)."
            )

    def embed_query(self, query: str) -> np.ndarray:
        """Encode a single query string into a (1, dim) embedding vector."""
        return self.model.encode([query])
