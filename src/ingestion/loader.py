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
    """Reconstruct paragraph text from word dicts; returns (top_bucket, line_text) pairs sorted by top position.

    Within each top bucket words are sorted by x0 so that superscripts and
    descenders (which have slightly different top values) are placed in reading
    order rather than the order they happen to be sorted by top.
    """
    if not words:
        return []
    lines: dict[int, list[dict]] = {}
    for w in words:
        key = round(w["top"] / 3) * 3
        lines.setdefault(key, []).append(w)
    return [
        (k, " ".join(w["text"] for w in sorted(lines[k], key=lambda w: w["x0"])))
        for k in sorted(lines)
    ]


def _find_column_split(words: list[dict], page_width: float) -> float | None:
    """Find the x-coordinate of the gutter between two columns, or None if no clear gap exists.

    Builds a histogram of word x-centre positions in 2-point bins across the
    middle 30–70% of the page width, then locates the longest consecutive run
    of near-empty bins that has non-empty bins on both sides (the actual gutter).
    Returns the midpoint of that run, or None if no such gap is found.
    """
    search_lo = page_width * 0.30
    search_hi = page_width * 0.70
    bin_width = 2.0
    n_bins = int((search_hi - search_lo) / bin_width) + 1
    counts = [0] * n_bins

    for w in words:
        xc = (w["x0"] + w["x1"]) / 2
        if search_lo <= xc <= search_hi:
            b = min(int((xc - search_lo) / bin_width), n_bins - 1)
            counts[b] += 1

    if not any(counts):
        return None

    max_count = max(counts)
    if max_count == 0:
        return None

    # A bin is "empty" when it has <= 10% of the peak density
    threshold = max_count * 0.10
    empty = [c <= threshold for c in counts]

    # Find all runs of consecutive empty bins that are flanked by non-empty bins
    best_run_len = 0
    best_run_mid = -1
    i = 0
    while i < n_bins:
        if empty[i]:
            j = i
            while j < n_bins and empty[j]:
                j += 1
            # Run is i..j-1; flanked on left (i>0 and not empty[i-1]) and right (j<n_bins and not empty[j])
            left_ok = i > 0 and not empty[i - 1]
            right_ok = j < n_bins and not empty[j]
            if left_ok and right_ok and (j - i) > best_run_len:
                best_run_len = j - i
                best_run_mid = (i + j) / 2
            i = j
        else:
            i += 1

    if best_run_mid < 0:
        return None

    # Real column gutters are at least ~6 pt wide; narrower gaps are word-spacing noise.
    if best_run_len * bin_width < 6:
        return None

    split_candidate = search_lo + best_run_mid * bin_width

    # Reject splits that are too far from the horizontal centre of the word
    # distribution.  A real two-column gutter sits near the midpoint; a
    # spurious gap found inside a single-column text block can land anywhere.
    x_centers = [(w["x0"] + w["x1"]) / 2 for w in words]
    x_min, x_max = min(x_centers), max(x_centers)
    text_half_width = (x_max - x_min) / 2
    text_center = x_min + text_half_width
    if text_half_width > 0 and abs(split_candidate - text_center) > text_half_width * 0.25:
        return None

    return split_candidate


def _find_footnote_top(page: pdfplumber.pdf.Page) -> float:
    """Return the y-coordinate of the top of the footnote zone, or page.height if none detected.

    Detects the horizontal separator rule that LaTeX draws between body and footnotes:
    a short horizontal line in the bottom 40% of the page.
    """
    separator_lines = [
        l for l in page.lines
        if l["height"] < 2
        and l["top"] > page.height * 0.60
        and (l["x1"] - l["x0"]) > page.width * 0.10
    ]
    if separator_lines:
        return min(l["top"] for l in separator_lines)
    return page.height


def _extract_page_text(page: pdfplumber.pdf.Page) -> str:
    """Extract one pdfplumber page: bordered tables as Markdown, body text in reading-column order, headers prefixed ##."""
    # Phase 1: tables
    tables = page.find_tables()
    table_bboxes = [t.bbox for t in tables]
    table_mds = [_table_to_markdown(t.extract()) for t in tables]

    footnote_top = _find_footnote_top(page)

    # Phase 2: body text (words outside table regions and above footnote zone)
    all_words = page.extract_words(x_tolerance=1)
    body_words = [
        w for w in all_words
        if not any(_word_in_bbox(w, bb) for bb in table_bboxes)
        and w["top"] < footnote_top
    ]

    if body_words:
        split_x = _find_column_split(body_words, page.width)
        two_column = split_x is not None

        if two_column:
            assert split_x is not None
            left_words = sorted(
                [w for w in body_words if (w["x0"] + w["x1"]) / 2 < split_x],
                key=lambda w: (w["top"], w["x0"]),
            )
            right_words = sorted(
                [w for w in body_words if (w["x0"] + w["x1"]) / 2 >= split_x],
                key=lambda w: (w["top"], w["x0"]),
            )
            keyed_lines = _words_to_text(left_words) + _words_to_text(right_words)
        else:
            body_words_sorted = sorted(body_words, key=lambda w: (w["top"], w["x0"]))
            keyed_lines = _words_to_text(body_words_sorted)

        # Phase 3: header labelling — match chars by y-position bucket, not text substring
        non_table_chars = [
            c for c in page.chars
            if not any(_word_in_bbox(c, bb) for bb in table_bboxes)
            and c["top"] < footnote_top
        ]
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
