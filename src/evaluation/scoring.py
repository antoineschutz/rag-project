"""Scoring for benchmark answers: keyword matching and an LLM-as-judge.

`score_answer` is the deterministic headline metric (every keyword must appear).
`judge_answer` is an independent second opinion from a separate judge model.
"""

from src.llm.client import LLMClient
from src.prompts.templates import build_prompt_judge


def score_answer(answer: str, keywords: list[str | list[str]]) -> bool:
    """True if every keyword appears (case-insensitively) as a substring of answer.

    A keyword slot may be a single string (which must appear) or a list of alternatives
    (any one of which satisfies the slot). The alternatives let a concept be written in more
    than one valid surface form, e.g. ["square root", "sqrt", "√"], so a correct answer
    is not marked wrong just for choosing the symbol over the words.
    """
    haystack = answer.lower()

    def present(slot: str | list[str]) -> bool:
        if isinstance(slot, list):
            return any(alt.lower() in haystack for alt in slot)
        return slot.lower() in haystack

    return all(present(slot) for slot in keywords)


def judge_answer(question: str, expected: str, answer: str, client: LLMClient) -> bool:
    """Ask the judge LLM whether `answer` conveys the key fact(s) of `expected`."""
    prompt = build_prompt_judge(question, expected, answer)
    return client.generate(prompt).strip().upper().startswith("Y")
