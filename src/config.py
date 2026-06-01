from dataclasses import dataclass


@dataclass
class RAGConfig:
    DATA_PATH: str = "./data/"
    EMBED_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_MAX_TOKENS: int = 128
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 15
    LLM_BACKEND: str = "ollama"
    OLLAMA_MODEL: str = "phi3"
    OPENAI_MODEL: str = "gpt-4o-mini"
    CACHE_DIR: str = "./cache/"
    FAISS_INDEX_PATH: str = "./cache/faiss.index"
    SQLITE_DB_PATH: str = "./cache/chunks.db"


config = RAGConfig()
