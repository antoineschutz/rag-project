import logging
import re
import statistics
from pathlib import Path

import docx
import pdfplumber
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Normalize extracted text: join hyphens, flatten newlines, split camelCase, remove page markers, collapse whitespace."""
    text = re.sub(r"-\s*\n\s*", "", text)
    text = text.replace("\n", " ")
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"\bPage\s*\d+\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _table_to_markdown(table: list[list[str | None]]) -> str:
    """Convert a pdfplumber nested-list table to a GitHub-flavoured Markdown table string."""
    rows = []
    for i, row in enumerate(table):
        cells = [str(c or "").replace("\n", " ").strip() for c in row]
        rows.append("| " + " | ".join(cells) + " |")
        if i == 0:
            rows.append("| " + " | ".join(["---"] * len(cells)) + " |")
    return "\n".join(rows)


def _word_in_bbox(word: dict, bbox: tuple) -> bool:
    """Return True if the word's centre point falls inside the bounding box (x0, top, x1, bottom)."""
    x_center = (word["x0"] + word["x1"]) / 2
    y_center = (word["top"] + word["bottom"]) / 2
    x0, top, x1, bottom = bbox
    return x0 <= x_center <= x1 and top <= y_center <= bottom


def _words_to_text(words: list[dict]) -> list[tuple[int, str]]:
    """Reconstruct paragraph text from word dicts; returns (top_bucket, line_text) pairs sorted by top position."""
    if not words:
        return []
    lines: dict[int, list[str]] = {}
    for w in words:
        key = round(w["top"] / 3) * 3
        lines.setdefault(key, []).append(w["text"])
    return [(k, " ".join(lines[k])) for k in sorted(lines)]


def _extract_page_text(page: pdfplumber.pdf.Page) -> str:
    """Extract one pdfplumber page: bordered tables as Markdown, body text in reading-column order, headers prefixed ##."""
    # Phase 1: tables
    tables = page.find_tables()
    table_bboxes = [t.bbox for t in tables]
    table_mds = [_table_to_markdown(t.extract()) for t in tables]

    # Phase 2: body text (words outside table regions)
    all_words = page.extract_words(x_tolerance=1)
    body_words = [w for w in all_words if not any(_word_in_bbox(w, bb) for bb in table_bboxes)]

    if body_words:
        midpoint = page.width / 2
        strip_lo, strip_hi = page.width * 0.425, page.width * 0.575
        center_count = sum(1 for w in body_words if strip_lo <= (w["x0"] + w["x1"]) / 2 <= strip_hi)
        two_column = len(body_words) > 20 and center_count / len(body_words) < 0.05

        if two_column:
            left = sorted([w for w in body_words if (w["x0"] + w["x1"]) / 2 < midpoint], key=lambda w: (w["top"], w["x0"]))
            right = sorted([w for w in body_words if (w["x0"] + w["x1"]) / 2 >= midpoint], key=lambda w: (w["top"], w["x0"]))
            keyed_lines = _words_to_text(left) + _words_to_text(right)
        else:
            body_words_sorted = sorted(body_words, key=lambda w: (w["top"], w["x0"]))
            keyed_lines = _words_to_text(body_words_sorted)

        # Phase 3: header labelling — match chars by y-position bucket, not text substring
        non_table_chars = [c for c in page.chars if not any(_word_in_bbox(c, bb) for bb in table_bboxes)]
        if non_table_chars:
            sizes = [c["size"] for c in non_table_chars if c.get("size")]
            median_size = statistics.median(sizes) if sizes else 0
            labelled_lines = []
            for top_key, line in keyed_lines:
                line_chars = [c for c in non_table_chars if abs(round(c["top"] / 3) * 3 - top_key) <= 3]
                avg_size = statistics.mean(c["size"] for c in line_chars) if line_chars else 0
                if avg_size >= median_size * 1.3 and 0 < len(line) < 80:
                    labelled_lines.append("## " + line)
                else:
                    labelled_lines.append(line)
            body_text = "\n".join(labelled_lines)
        else:
            body_text = "\n".join(line for _, line in keyed_lines)

        body_text = re.sub(r"-\s*\n\s*", "", body_text)
        body_text = re.sub(r"\bPage\s*\d+\b", " ", body_text, flags=re.IGNORECASE)
        body_text = re.sub(r"\s+", " ", body_text).strip()
    else:
        body_text = ""

    parts = table_mds + ([body_text] if body_text else [])
    return "\n\n".join(parts)


def load_pdfs_pypdf(folder_path: str) -> list[dict[str, str]]:
    """Load all PDFs in folder_path using pypdf; kept alongside load_pdfs for extraction quality comparison."""
    documents = []
    for path in Path(folder_path).glob("*.pdf"):
        try:
            reader = PdfReader(str(path))
            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                page_text = clean_text(page_text)
                if page_text:
                    pages_text.append(page_text)
            full_text = " ".join(pages_text).strip()
            documents.append({"text": full_text, "source": path.name})
        except Exception as e:
            logger.warning("Skipping %s — %s", path.name, e)
    return documents


def load_pdfs(folder_path: str) -> list[dict[str, str]]:
    """Load all PDFs in folder_path using pdfplumber with table detection and multi-column ordering."""
    documents = []
    for path in Path(folder_path).glob("*.pdf"):
        try:
            pages_text = []
            with pdfplumber.open(str(path)) as pdf:
                for page in pdf.pages:
                    page_text = _extract_page_text(page)
                    if page_text:
                        pages_text.append(page_text)
            full_text = "\n\n".join(pages_text).strip()
            documents.append({"text": full_text, "source": path.name})
        except Exception as e:
            logger.warning("Skipping %s — %s", path.name, e)
    return documents


def load_markdown(folder_path: str) -> list[dict[str, str]]:
    """Load all .md files in folder_path as plain text documents."""
    documents = []
    for path in Path(folder_path).glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                documents.append({"text": text, "source": path.name})
        except Exception as e:
            logger.warning("Skipping %s — %s", path.name, e)
    return documents


def load_docx(folder_path: str) -> list[dict[str, str]]:
    """Load all .docx files in folder_path, joining non-empty paragraphs with newlines."""
    documents = []
    for path in Path(folder_path).glob("*.docx"):
        try:
            d = docx.Document(str(path))
            text = "\n".join(para.text for para in d.paragraphs if para.text.strip())
            if text:
                documents.append({"text": text, "source": path.name})
        except Exception as e:
            logger.warning("Skipping %s — %s", path.name, e)
    return documents


def load_documents(folder_path: str) -> list[dict[str, str]]:
    """Load all supported documents (PDF, Markdown, DOCX) from folder_path."""
    return load_pdfs(folder_path) + load_markdown(folder_path) + load_docx(folder_path)
