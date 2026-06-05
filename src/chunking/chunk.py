import nltk
import tiktoken
from nltk.tokenize import sent_tokenize

from src.config import config

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)


def naive_chunk_text(text: str, chunk_size: int = 500, overlap: int = 20) -> list[str]:
    """Split text into fixed-size character chunks with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def chunk_text(text: str, chunk_size: int = 500, min_chunk_size: int = 300) -> list[str]:
    """Split text into sentence-aware chunks bounded by character count."""
    sentences = sent_tokenize(text)
    chunks = []
    current = []
    current_len = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if current_len + len(sentence) > chunk_size:
            if current_len >= min_chunk_size:
                chunks.append(" ".join(current))
                current = [sentence]
                current_len = len(sentence)
            else:
                current.append(sentence)
                current_len += len(sentence)
        else:
            current.append(sentence)
            current_len += len(sentence)

    if current:
        chunks.append(" ".join(current))
    return chunks


def chunk_text_tiktoken(
    text: str,
    max_tokens: int = config.CHUNK_MAX_TOKENS,
    overlap_tokens: int = config.CHUNK_OVERLAP,
) -> list[str]:
    """Like chunk_text but uses tiktoken token counts instead of character counts, with overlap carry-over between chunks."""
    enc = tiktoken.get_encoding("cl100k_base")

    def token_len(text: str) -> int:
        return len(enc.encode(text))

    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = token_len(sentence)

        if sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0
            tokens = enc.encode(sentence)
            for i in range(0, len(tokens), max_tokens):
                chunk_tokens = tokens[i:i + max_tokens]
                chunks.append(enc.decode(chunk_tokens))
            continue

        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            if overlap_tokens > 0:
                flat_tokens = enc.encode(" ".join(current_chunk))
                overlap = flat_tokens[-overlap_tokens:]
                current_chunk = [enc.decode(overlap), sentence]
                current_tokens = len(overlap) + sentence_tokens
            else:
                current_chunk = [sentence]
                current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def chunk_documents(docs: list[dict[str, str]]) -> list[dict[str, str]]:
    """Apply tiktoken chunking to each document, propagating the source field to every chunk."""
    chunked_docs = []
    for doc in docs:
        for chunk in chunk_text_tiktoken(doc["text"]):
            chunked_docs.append({"text": chunk, "source": doc["source"]})
    return chunked_docs
