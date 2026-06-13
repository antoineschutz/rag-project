def build_prompt_hyde(query: str) -> str:
    return f"""Write a short paragraph that directly answers the following question.
Do not include the question itself. If unsure, make a plausible attempt.

Question: {query}

Passage:

"""


def build_prompt_no_rag(query: str) -> str:
    # Mirrors build_prompt_rag minus the context block, so RAG vs no-RAG differs only by retrieval.
    return f"""Answer the question below. If you are unsure, say so.

Question:

{query}

Answer:

"""


def build_prompt_judge(question: str, expected: str, answer: str) -> str:
    return f"""You are grading a short factual answer against a reference answer.

Question: {question}
Reference answer: {expected}
Candidate answer: {answer}

Does the candidate state the key fact(s) of the reference answer correctly? Ignore style, extra detail, and hedging. Reply with a single word: YES or NO."""


def build_prompt_rag(query: str, contexts: list[str]) -> str:
    context_text = "\n\n".join(contexts)
    return f"""Answer the question below. Use the context when it is relevant; it may contain
information you do not have. If the context does not contain the answer, answer from
your own knowledge instead and begin that part with "From general knowledge:".
If you are unsure, say so.

Context:

{context_text}

Question:

{query}

Answer:

"""
