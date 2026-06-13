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


# Keep the last N messages (about 3 exchanges) in chat prompts so prompt size stays bounded
# no matter how long the conversation gets.
MAX_HISTORY_MESSAGES = 6


def _format_history(history: list[dict[str, str]], max_messages: int = MAX_HISTORY_MESSAGES) -> str:
    """Render the last `max_messages` turns as 'User: ...' / 'Assistant: ...' lines."""
    labels = {"user": "User", "assistant": "Assistant"}
    return "\n".join(
        f"{labels.get(m['role'], m['role'].title())}: {m['content']}"
        for m in history[-max_messages:]
    )


def build_prompt_condense(history: list[dict[str, str]], question: str) -> str:
    return f"""Given the conversation so far and a follow-up question, rewrite the follow-up as a
standalone question that can be understood without the conversation. Resolve pronouns and
references using the history. If the follow-up is already standalone, return it unchanged.
Do not answer it.

Conversation:

{_format_history(history)}

Follow-up question: {question}

Standalone question:

"""


def build_prompt_no_rag_chat(history: list[dict[str, str]], query: str) -> str:
    return f"""Answer the question below. If you are unsure, say so.

Conversation so far:

{_format_history(history)}

Question:

{query}

Answer:

"""


def build_prompt_rag_chat(history: list[dict[str, str]], query: str, contexts: list[str]) -> str:
    context_text = "\n\n".join(contexts)
    return f"""Answer the question below. Use the context when it is relevant; it may contain
information you do not have. If the context does not contain the answer, answer from
your own knowledge instead and begin that part with "From general knowledge:".
If you are unsure, say so.

Conversation so far:

{_format_history(history)}

Context:

{context_text}

Question:

{query}

Answer:

"""
