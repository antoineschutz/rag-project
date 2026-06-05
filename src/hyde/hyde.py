import logging

from src.llm.client import LLMClient
from src.prompts.templates import build_prompt_hyde

logger = logging.getLogger(__name__)


def generate_hypothetical_doc(query: str, llm: LLMClient) -> str:
    """Generate a hypothetical answer passage to use as the retrieval embedding instead of the raw query."""
    prompt = build_prompt_hyde(query)
    doc = llm.generate(prompt)
    logger.debug("HyDE hypothetical doc: %s", doc)
    return doc
