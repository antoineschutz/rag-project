import re

import nltk
import tiktoken
from nltk.tokenize import sent_tokenize

from src.config import config

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

_TABLE_LINE_RE = re.compile(r"^\s*\|")


def _split_table_blocks(text: str) -> list[tuple[str, str]]:
    """Split text into ('table', ...) and ('prose', ...) segments.

    Lines starting with '|' belong to a markdown table block and are kept
    together as a single atomic segment so the chunker never splits them.
    """
    segments: list[tuple[str, str]] = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if _TABLE_LINE_RE.match(lines[i]):
            start = i
            while i < len(lines) and _TABLE_LINE_RE.match(lines[i]):
                i += 1
            segments.append(("table", "\n".join(lines[start:i])))
        else:
            start = i
            while i < len(lines) and not _TABLE_LINE_RE.match(lines[i]):
                i += 1
            block = "\n".join(lines[start:i]).strip()
            if block:
                segments.append(("prose", block))
    return segments


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
    """Tiktoken-based chunker with overlap, treating markdown table blocks as atomic units.

    Table blocks (lines starting with '|') are never split and are emitted as
    a single chunk regardless of token length. Prose segments follow the normal
    sentence-accumulation logic with overlap carry-over.
    """
    enc = tiktoken.get_encoding("cl100k_base")

    def token_len(s: str) -> int:
        return len(enc.encode(s))

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_tokens: int = 0

    def add_sentence(sentence: str) -> None:
        nonlocal current_chunk, current_tokens
        sentence_tokens = token_len(sentence)

        if sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0
            tokens = enc.encode(sentence)
            for i in range(0, len(tokens), max_tokens):
                chunks.append(enc.decode(tokens[i:i + max_tokens]))
            if overlap_tokens > 0 and tokens:
                overlap = tokens[-overlap_tokens:]
                current_chunk = [enc.decode(overlap)]
                current_tokens = len(overlap)
            return

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

    for seg_type, seg_text in _split_table_blocks(text):
        if seg_type == "table":
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0
            chunks.append(seg_text)
        else:
            for sentence in sent_tokenize(seg_text):
                sentence = sentence.strip()
                if sentence:
                    add_sentence(sentence)

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def chunk_documents(
    docs: list[dict[str, str]],
    chunk_max_tokens: int | None = None,
    overlap_tokens: int | None = None,
) -> list[dict[str, str]]:
    """Apply tiktoken chunking to each document, propagating the source field to every chunk."""
    kwargs: dict = {}
    if chunk_max_tokens is not None:
        kwargs["max_tokens"] = chunk_max_tokens
    if overlap_tokens is not None:
        kwargs["overlap_tokens"] = overlap_tokens
    chunked_docs = []
    for doc in docs:
        for chunk in chunk_text_tiktoken(doc["text"], **kwargs):
            chunked_docs.append({"text": chunk, "source": doc["source"]})
    return chunked_docs
