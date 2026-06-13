import logging

from src.llm.client import LLMClient
from src.prompts.templates import build_prompt_condense

logger = logging.getLogger(__name__)


def condense_question(history: list[dict[str, str]], question: str, llm: LLMClient) -> str:
    """Rewrite a follow-up question into a standalone query using the conversation history.

    Returns `question` unchanged when there is no history. The result is used as the retrieval
    and rerank query so a context-dependent follow-up (e.g. "how does it differ?") still retrieves
    well.
    """
    if not history:
        return question
    standalone = llm.generate(build_prompt_condense(history, question)).strip()
    logger.debug("Condensed question: %r -> %r", question, standalone)
    return standalone
