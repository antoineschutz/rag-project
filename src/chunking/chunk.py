import re

import nltk
import tiktoken
from nltk.tokenize import sent_tokenize

from src.config import BASE

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

_TABLE_LINE_RE = re.compile(r"^\s*\|")
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S")
_MAX_HEADING_CHARS = 80


def _last_heading(block: str) -> str | None:
    """Return the last markdown heading in a prose block, capped to a short prefix.

    Whitespace-collapsed PDF extraction can merge a heading and its whole paragraph onto one
    line that still starts with '##'; without the cap the entire paragraph would be treated as
    the heading and prepended to following tables, producing huge chunks.
    """
    found = None
    for line in block.split("\n"):
        if _HEADING_RE.match(line):
            h = line.strip()
            found = h[:_MAX_HEADING_CHARS].rstrip() if len(h) > _MAX_HEADING_CHARS else h
    return found


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
    max_tokens: int = BASE.chunk_max_tokens,
    overlap_tokens: int = BASE.chunk_overlap,
) -> list[str]:
    """Tiktoken-based chunker with overlap, treating markdown table blocks as atomic units.

    Tables are never split. If a table fits in the current chunk alongside
    surrounding prose (title before, description after), it stays in the same
    chunk. If not, the current chunk is flushed first and the table starts a
    fresh one. Prose segments follow the normal sentence-accumulation logic
    with overlap carry-over.
    """
    overlap_tokens = min(overlap_tokens, max_tokens // 2)
    enc = tiktoken.get_encoding("cl100k_base")

    def token_len(s: str) -> int:
        return len(enc.encode(s))

    def flush_chunk(parts: list[str]) -> str:
        # Preserve newlines when the chunk contains a table block.
        if any("\n" in p for p in parts):
            return "\n\n".join(p.strip() for p in parts if p.strip())
        return " ".join(parts)

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_tokens: int = 0

    def add_sentence(sentence: str) -> None:
        nonlocal current_chunk, current_tokens
        sentence_tokens = token_len(sentence)

        if sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append(flush_chunk(current_chunk))
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
            chunks.append(flush_chunk(current_chunk))
            if overlap_tokens > 0:
                flat_tokens = enc.encode(flush_chunk(current_chunk))
                overlap = flat_tokens[-overlap_tokens:]
                current_chunk = [enc.decode(overlap), sentence]
                current_tokens = len(overlap) + sentence_tokens
            else:
                current_chunk = [sentence]
                current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    def _table_header(lines: list[str]) -> tuple[list[str], int]:
        """Leading lines to repeat on each split piece: any ## heading, the column header
        row, and the | --- | separator. Returns (header_lines, index where data rows start)."""
        hdr: list[str] = []
        i = 0
        while i < len(lines) and not lines[i].lstrip().startswith("|"):
            hdr.append(lines[i])
            i += 1
        if i < len(lines):  # column header row
            hdr.append(lines[i])
            i += 1
        if i < len(lines) and not lines[i].replace("|", "").replace("-", "").replace(":", "").strip():
            hdr.append(lines[i])  # separator row (| --- | --- |)
            i += 1
        return hdr, i

    def add_table(table_text: str, heading: str | None) -> None:
        nonlocal current_chunk, current_tokens
        # A table on its own is just pipes and numbers; prepend the section heading so the
        # chunk carries the topic words (e.g. "Embedding Model Benchmarks") that queries match.
        if heading and heading not in table_text:
            table_text = f"{heading}\n{table_text}"
        table_tokens = token_len(table_text)

        # Real tables stay atomic up to a generous cap so comparison queries see every row and
        # single-row lookups keep their header. Only oversized tables (long results tables, or
        # mis-detected figure grids) are split row by row, repeating the header on each piece so
        # a bare row like "| BERT LARGE | 72.1 |" keeps its "| QQP |" column label.
        table_max = max_tokens * 4
        if table_tokens > table_max:
            if current_chunk:
                chunks.append(flush_chunk(current_chunk))
                current_chunk = []
                current_tokens = 0
            lines = table_text.split("\n")
            hdr, body_i = _table_header(lines)
            hdr_text = "\n".join(hdr)
            hdr_tokens = token_len(hdr_text)
            piece = list(hdr)
            piece_tokens = hdr_tokens
            for row in lines[body_i:]:
                row_tokens = token_len(row)
                if piece_tokens + row_tokens > max_tokens and len(piece) > len(hdr):
                    chunks.append("\n".join(piece))
                    piece = list(hdr)
                    piece_tokens = hdr_tokens
                piece.append(row)
                piece_tokens += row_tokens
            if len(piece) > len(hdr):
                chunks.append("\n".join(piece))
            return

        if current_tokens + table_tokens > max_tokens:
            if current_chunk:
                chunks.append(flush_chunk(current_chunk))
                current_chunk = []
                current_tokens = 0
        current_chunk.append(table_text)
        current_tokens += table_tokens
        # Flush immediately if the table alone already fills the budget.
        if current_tokens >= max_tokens:
            chunks.append(flush_chunk(current_chunk))
            current_chunk = []
            current_tokens = 0

    heading: str | None = None
    for seg_type, seg_text in _split_table_blocks(text):
        if seg_type == "table":
            add_table(seg_text, heading)
        else:
            found = _last_heading(seg_text)
            if found:
                heading = found
            for sentence in sent_tokenize(seg_text):
                sentence = sentence.strip()
                if sentence:
                    add_sentence(sentence)

    if current_chunk:
        chunks.append(flush_chunk(current_chunk))
    return chunks


def chunk_documents(
    docs: list[dict[str, str]],
    chunk_max_tokens: int | None = None,
    overlap_tokens: int | None = None,
) -> list[dict[str, str]]:
    """Apply tiktoken chunking to each document, propagating the source field to every chunk."""
    kwargs: dict[str, int] = {}
    if chunk_max_tokens is not None:
        kwargs["max_tokens"] = chunk_max_tokens
    if overlap_tokens is not None:
        kwargs["overlap_tokens"] = overlap_tokens
    chunked_docs = []
    for doc in docs:
        for chunk in chunk_text_tiktoken(doc["text"], **kwargs):
            chunked_docs.append({"text": chunk, "source": doc["source"]})
    return chunked_docs
