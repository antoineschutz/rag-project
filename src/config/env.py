from dataclasses import dataclass

from dotenv import load_dotenv

# Load a local .env (if present) into the process environment so keys like OPENAI_API_KEY
# are available. Real environment variables take precedence (override=False by default).
load_dotenv()


@dataclass
class RAGEnvConfig:
    """Environment / infrastructure settings: where data and the cache live, and which
    LLM backend/model to use. These are set once per deployment (could become env vars
    later) and are not per-request pipeline knobs.
    """

    DATA_PATH: str = "./data/"
    CACHE_DIR: str = "./cache/"
    LLM_BACKEND: str = "ollama"
    OLLAMA_MODEL: str = "phi3"
    OPENAI_MODEL: str = "gpt-4o-mini"
    OLLAMA_NUM_CTX: int = 4096  # phi3 supports up to 131072; override via --num-ctx or a config
    # Presets the API warms at startup (loads models + builds indexes) so the first request
    # is not cold. Set to () to disable (e.g. for fast dev / uvicorn --reload startup).
    WARMUP_PRESETS: tuple[str, ...] = ("baseline", "best")


env = RAGEnvConfig()
