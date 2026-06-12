"""Scoring for benchmark answers: keyword matching and an LLM-as-judge.

`score_answer` is the deterministic headline metric (every keyword must appear).
`judge_answer` is an independent second opinion from a separate judge model.
"""

from src.llm.client import LLMClient
from src.prompts.templates import build_prompt_judge


def score_answer(answer: str, keywords: list[str]) -> bool:
    """True if every keyword appears (case-insensitively) as a substring of answer."""
    haystack = answer.lower()
    return all(kw.lower() in haystack for kw in keywords)


def judge_answer(question: str, expected: str, answer: str, client: LLMClient) -> bool:
    """Ask the judge LLM whether `answer` conveys the key fact(s) of `expected`."""
    prompt = build_prompt_judge(question, expected, answer)
    return client.generate(prompt).strip().upper().startswith("Y")
