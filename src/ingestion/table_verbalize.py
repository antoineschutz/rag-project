import re


def _table_to_markdown(table: list[list[str | None]]) -> str:
    """Convert a pdfplumber nested-list table to a GitHub-flavoured Markdown table string."""
    rows = []
    for i, row in enumerate(table):
        cells = [str(c or "").replace("\n", " ").strip() for c in row]
        rows.append("| " + " | ".join(cells) + " |")
        if i == 0:
            rows.append("| " + " | ".join(["---"] * len(cells)) + " |")
    return "\n".join(rows)


def _is_number_token(t: str) -> bool:
    """True for a token that starts a number (allows leading '[', '(', sign), e.g. 40.4, [20], (79k."""
    t = t.strip()
    return bool(re.match(r"^[\[\(]?[-+]?\d", t)) and any(ch.isdigit() for ch in t)


def _clean_number_cell(cell: str) -> bool:
    """True if a rebuilt cell is a single bare number (the signal that a column aligned cleanly)."""
    return _is_number_token(cell) and len(cell.split()) == 1


# Benchmark column abbreviations expanded in verbalized facts so a fact written with the table's
# short label ("NQ") still matches a question that uses the full name ("NaturalQuestions").
_COL_EXPANSIONS = {
    "NQ": "NaturalQuestions NQ", "WQ": "WebQuestions WQ", "TQA": "TriviaQA TQA",
    "CT": "CuratedTrec CT", "EM": "Exact Match EM", "QQP": "QQP",
    "EN-DE": "English-German EN-DE", "EN-FR": "English-French EN-FR",
}
_UNITS = {"ms", "s", "%", "M", "B", "FLOPs"}


def _expand_label(label: str) -> str:
    # Drop a trailing example-count that PDF headers append to a metric name ("QQP 363k" -> "QQP").
    label = re.sub(r"\s+\d[\d.]*[km]?\s*$", "", label.strip()).strip()
    return _COL_EXPANSIONS.get(label, label)


def _fact_pair(label: str, value: str) -> str:
    """Render one "<column> <value>" pair, moving a unit from the column label onto the value so
    "Query latency (ms)" + "4" reads as "Query latency 4 ms" (the form a question expects)."""
    label, value = label.strip(), value.strip()
    m = re.search(r"\(([^)]+)\)\s*$", label)
    if m and m.group(1) in _UNITS:
        return f"{_expand_label(label[:m.start()].strip())} {value} {m.group(1)}"
    return f"{_expand_label(label)} {value}"


def _verbalize_grid(grid: list[list[str]], caption: str) -> str:
    """Turn a rebuilt grid into one self-contained sentence per data row.

    A row stated as "<caption>. <row label>: <col> <value>, ..." embeds as a focused chunk,
    unlike the dense table which mixes every model and number together.
    """
    header = grid[0]
    data = grid[1:]
    prefix = f"{caption} " if caption else ""
    width = len(header)

    # Label column = most DISTINCT non-numeric cells. Distinct, not just any text, avoids picking
    # a constant column ("FAISS, FAISS") over the discriminating one ("IndexFlatIP, IndexIVF").
    def name_count(j: int) -> int:
        return len({row[j].strip() for row in data if j < len(row) and row[j].strip() and not _is_number_token(row[j])})
    name_col = max(range(width), key=name_count)

    def row_label(row: list[str]) -> str:
        parts = [row[c].strip() for c in (0, name_col) if c < len(row) and row[c].strip()]
        return " ".join(dict.fromkeys(parts))  # dedupe while keeping order

    lines = []
    # One fact per row (answers a single-cell lookup).
    for row in data:
        label = row_label(row)
        pairs = [
            _fact_pair(header[j], row[j])
            for j in range(1, width)
            if j != name_col and j < len(row) and row[j].strip() and header[j].strip()
        ]
        if label and pairs:
            lines.append(f"{prefix}{label}: " + ", ".join(pairs) + ".")
    # One fact per metric column (answers compare/argmax: two systems' value for one metric
    # in a single chunk).
    for j in range(1, width):
        col = header[j].strip()
        if not col or j == name_col:
            continue
        pairs = [
            f"{row_label(row)} {row[j].strip()}"
            for row in data
            if row_label(row) and j < len(row) and _clean_number_cell(row[j].strip())
        ]
        if len(pairs) >= 2:
            lines.append(f"{prefix}{_expand_label(col)}: " + ", ".join(pairs) + ".")
    return "\n".join(lines)


def _markdown_table_facts(text: str) -> list[str]:
    """Verbalize each GitHub-style Markdown table in `text` into one fact per row/column.

    The nearest preceding heading is used as the caption.
    """
    facts: list[str] = []
    lines = text.split("\n")
    heading = ""
    i = 0
    while i < len(lines):
        if re.match(r"^\s{0,3}#{1,6}\s+\S", lines[i]):
            heading = lines[i].lstrip("# ").strip()
        if lines[i].lstrip().startswith("|"):
            start = i
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                i += 1
            block = lines[start:i]
            rows = [[c.strip() for c in row.strip().strip("|").split("|")] for row in block]
            rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]  # drop separator
            if len(rows) >= 3:
                facts += [f for f in _verbalize_grid(rows, heading).split("\n") if f.strip()]
            continue
        i += 1
    return facts
