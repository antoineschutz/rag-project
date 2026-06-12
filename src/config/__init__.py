"""Configuration and parameter system.

Three concerns live here: the environment config (env), the pipeline config schema and named
presets (PipelineConfig, BASE/BEST/NO_RAG, PRESETS), and the per-lifetime param groups
(IndexParams / RetrievalParams / GenerationParams). They are re-exported here so callers can
`from src.config import env, BASE, PRESETS, IndexParams, ...` without knowing the submodule layout.
"""

from src.config.env import RAGEnvConfig, env
from src.config.pipeline import BASE, BEST, NO_RAG, PRESETS, PipelineConfig, as_config_dict
from src.config.params import GenerationParams, IndexParams, RetrievalParams, split_config

__all__ = [
    "RAGEnvConfig",
    "env",
    "PipelineConfig",
    "BASE",
    "BEST",
    "NO_RAG",
    "PRESETS",
    "as_config_dict",
    "IndexParams",
    "RetrievalParams",
    "GenerationParams",
    "split_config",
]
