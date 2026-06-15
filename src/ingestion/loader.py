import logging
import re
import statistics
from pathlib import Path

import docx
import pdfplumber
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph
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


def _is_plausible_table(rows: list[list]) -> bool:
    """Return True if an extracted table looks like real tabular data and not mis-detected body text.

    Requires at least 3 rows, at least 3 columns, and an average cell length under 80 chars.
    Average (not max) is used because merged cells in booktabs tables can be long,
    but the overall average still stays well below prose sentence lengths.
    """
    if len(rows) < 3 or not rows[0] or len(rows[0]) < 3:
        return False
    cells = [str(c or "") for row in rows for c in row if c]
    if not cells:
        return False
    return (sum(len(c) for c in cells) / len(cells)) < 80


def _column_boundaries_from_words(words: list[dict], page_width: float) -> list[float]:
    """Infer column x-boundaries from word x0 positions using gap detection.

    Uses x_tolerance=5 word groupings; treats gaps > 24 pt as column separators.
    Returns a list of x boundary values suitable for explicit_vertical_lines.
    """
    if not words:
        return []
    xs = sorted({round(w["x0"]) for w in words})
    col_starts = [xs[0]]
    for i in range(1, len(xs)):
        if xs[i] - xs[i - 1] > 24:
            col_starts.append(xs[i])
    if len(col_starts) < 2:
        return []
    x_min = min(w["x0"] for w in words) - 5
    x_max = max(w["x1"] for w in words) + 5
    boundaries = [x_min]
    for i in range(len(col_starts) - 1):
        # Boundary sits in the gap between current column's last x0 and next column's first x0
        boundaries.append((col_starts[i + 1] - 5))
    boundaries.append(x_max)
    return boundaries


def _find_booktabs_tables(page: pdfplumber.pdf.Page) -> list:
    """Detect LaTeX booktabs-style tables that have only horizontal rules and no vertical lines.

    Groups horizontal rules that span >= 55% of page width into table regions,
    then builds explicit vertical column boundaries from data-row word x0 clustering
    (spanning header rows above the first midrule are excluded from column detection).
    """
    page_width = page.width
    wide_rules = sorted(
        [ln for ln in page.lines
         if (ln["x1"] - ln["x0"]) / page_width >= 0.55 and ln["height"] < 2],
        key=lambda ln: ln["top"],
    )
    if len(wide_rules) < 2:
        return []

    # Group consecutive rules within 200 pt of each other into one table region
    groups: list[list[dict]] = []
    current = [wide_rules[0]]
    for rule in wide_rules[1:]:
        if rule["top"] - current[-1]["top"] < 200:
            current.append(rule)
        else:
            groups.append(current)
            current = [rule]
    groups.append(current)

    tables = []
    for group in groups:
        if len(group) < 2:
            continue
        top = group[0]["top"] - 3
        bottom = group[-1]["top"] + 3
        h_lines = [r["top"] for r in group]

        all_words = page.extract_words(x_tolerance=5, y_tolerance=3)
        words_in_region = [w for w in all_words if top < w["top"] < bottom]
        if not words_in_region:
            continue

        # Exclude spanning header rows (above the first midrule) from column detection
        # so multi-column headers don't corrupt the column boundary inference.
        data_top = group[1]["top"] if len(group) > 1 else group[0]["top"]
        data_words = [w for w in words_in_region if w["top"] > data_top]
        col_words = data_words if data_words else words_in_region

        v_lines = _column_boundaries_from_words(col_words, page_width)
        if len(v_lines) < 3:  # need at least 2 columns
            continue

        # Add text-row y-positions as extra horizontal lines so each logical row
        # gets its own table row (booktabs rules only mark section boundaries).
        row_ys = sorted({round(w["top"] / 3) * 3 for w in data_words})
        row_boundaries: list[float] = sorted(set(h_lines))
        for y in row_ys:
            if not any(abs(y - h) < 5 for h in row_boundaries):
                row_boundaries.append(y - 2)
        row_boundaries = sorted(row_boundaries)

        candidates = page.find_tables(table_settings={
            "vertical_strategy": "explicit",
            "horizontal_strategy": "explicit",
            "explicit_vertical_lines": v_lines,
            "explicit_horizontal_lines": row_boundaries,
        })
        for t in candidates:
            if _is_plausible_table(t.extract()):
                tables.append(t)
    return tables


def _find_tables(page: pdfplumber.pdf.Page) -> list:
    """Detect tables: border-based first, then booktabs-style fallback."""
    tables = page.find_tables()
    if not tables:
        tables = _find_booktabs_tables(page)
    return tables


def _repair_notation(text: str) -> str:
    """Rejoin scientific notation and subscripts that pdfplumber shatters into separate tokens.

    Superscript exponents and subscripts sit at a different vertical offset, so the extractor
    splits e.g. "3.3 x 10^18" into "3.3·" and "1018" (often across table cells), and "d_ff" into
    "d ... ff" around the value. Both are rejoined into a single readable token.
    """
    # "3.3· | 1018" or "3.3 · 1018" -> "3.3·10^18"
    text = re.sub(r"(\d[\d.]*)\s*·\s*\|?\s*10(\d+)", r"\1·10^\2", text)
    # "d = 2048. ff" / "d 2048 ff" -> "d_ff = 2048"
    text = re.sub(r"\bd\s*=?\s*(\d{3,5})\.?\s*ff\b", r"d_ff = \1", text)
    return text


def _is_number_token(t: str) -> bool:
    """True for a token that starts a number (allows leading '[', '(', sign), e.g. 40.4, [20], (79k."""
    t = t.strip()
    return bool(re.match(r"^[\[\(]?[-+]?\d", t)) and any(ch.isdigit() for ch in t)


def _clean_number_cell(cell: str) -> bool:
    """True if a rebuilt cell is a single bare number (the signal that a column aligned cleanly)."""
    return _is_number_token(cell) and len(cell.split()) == 1


def _header_alignment_score(band: list[list[dict]], header: list[dict]) -> float:
    """Fraction of band cells that fall as single clean numbers under the header's column anchors.

    A real column-label row makes the numbers below it line up into clean one-number cells; a
    prose line used as a header scatters them, scoring low. Used to pick the header row.
    """
    anchors = [(w["x0"] + w["x1"]) / 2 for w in header]
    if not anchors:
        return 0.0
    clean = total = 0
    for line in band:
        cells = [""] * len(anchors)
        for w in line:
            xc = (w["x0"] + w["x1"]) / 2
            if xc >= anchors[0] - 15:
                k = min(range(len(anchors)), key=lambda a: abs(anchors[a] - xc))
                cells[k] = (cells[k] + " " + w["text"]).strip()
        for c in cells:
            if c.strip():
                total += 1
                clean += _clean_number_cell(c)
    return clean / total if total else 0.0


def _rebuild_table_rows(band: list[list[dict]], header: list[dict]) -> list[list[str]]:
    """Bin each band line's tokens into columns by nearest header anchor; col 0 is the row label.

    Citation markers ([20]) and significance stars (*) sitting next to a value are dropped from
    data cells so a cell like "[20] 40.4" reads as the clean number 40.4.
    """
    anchors = [(w["x0"] + w["x1"]) / 2 for w in header]
    rows = []
    for line in band:
        cells = [""] * (len(anchors) + 1)
        for w in line:
            text = w["text"]
            xc = (w["x0"] + w["x1"]) / 2
            if xc < anchors[0] - 15:
                cells[0] = (cells[0] + " " + text).strip()
            else:
                if re.fullmatch(r"\[\d+\]\*?", text):  # a bare citation marker, not data
                    continue
                k = min(range(len(anchors)), key=lambda a: abs(anchors[a] - xc))
                cells[k + 1] = (cells[k + 1] + " " + text).strip()
        cells = [cells[0]] + [re.sub(r"\*", "", c).strip() for c in cells[1:]]
        rows.append(cells)
    return rows


def _panel_split_x(band: list[list[dict]]) -> float | None:
    """If a band holds two tables printed side by side, return the x of the gap between them.

    Clusters numeric-token x-centres into columns and returns the midpoint of the widest gap
    between adjacent columns when it is unusually wide (> 40 pt), else None.
    """
    xs = sorted((w["x0"] + w["x1"]) / 2 for line in band for w in line if _is_number_token(w["text"]))
    if len(xs) < 4:
        return None
    cols = [[xs[0]]]
    for x in xs[1:]:
        (cols[-1].append(x) if x - cols[-1][-1] < 18 else cols.append([x]))
    centers = [sum(c) / len(c) for c in cols if len(c) >= 2]
    if len(centers) < 4:
        return None
    gaps = [(centers[i + 1] - centers[i], (centers[i] + centers[i + 1]) / 2) for i in range(len(centers) - 1)]
    width, mid = max(gaps)
    return mid if width > 40 else None


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

    The dense markdown table embeds poorly (dominated by every model and number at once), so a
    row stated as "<caption>. <row label>: <col> <value>, ..." gives retrieval a focused chunk
    that matches a question about that one entity and metric.
    """
    header = grid[0]
    data = grid[1:]
    prefix = f"{caption} " if caption else ""
    width = len(header)

    # The label column is the one with the most DISTINCT non-numeric cells (the model/system
    # names). Counting distinct values (not just any text) avoids picking a constant category
    # column ("Backend: FAISS, FAISS") over the discriminating one ("IndexFlatIP, IndexIVF").
    def name_count(j: int) -> int:
        return len({row[j].strip() for row in data if j < len(row) and row[j].strip() and not _is_number_token(row[j])})
    name_col = max(range(width), key=name_count)

    def row_label(row: list[str]) -> str:
        parts = [row[c].strip() for c in (0, name_col) if c < len(row) and row[c].strip()]
        return " ".join(dict.fromkeys(parts))  # dedupe while keeping order

    lines = []
    # One fact per row: "<name>: <col> <value>, ..." (answers a single-cell lookup).
    for row in data:
        label = row_label(row)
        pairs = [
            _fact_pair(header[j], row[j])
            for j in range(1, width)
            if j != name_col and j < len(row) and row[j].strip() and header[j].strip()
        ]
        if label and pairs:
            lines.append(f"{prefix}{label}: " + ", ".join(pairs) + ".")
    # One fact per metric column: "<col>: <name1> <v1>, <name2> <v2>, ..." (answers compare/argmax
    # and puts two systems' value for one metric in a single chunk).
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


def _emit_band_table(
    band: list[list[dict]], header_candidates: list[list[dict]], caption: str
) -> tuple[str, list[str], set[int]] | None:
    """Pick the best-aligned short-token header for a band, rebuild the grid, trim prose rows, and
    return (markdown table, verbalized fact lines, consumed word ids)."""
    stopwords = {"of", "the", "are", "in", "is", "to", "and", "a", "an", "for", "on", "with",
                 "below", "each", "shown", "by", "as", "we", "our", "this", "that", "from"}

    def short_header(h: list[dict]) -> bool:
        # Real column labels are short (NQ, WQ, QQP) and never function words; a caption or prose
        # line picked as the header is longer and full of stopwords.
        if len(h) < 3 or (sum(len(w["text"]) for w in h) / len(h)) > 6:
            return False
        return not any(w["text"].lower() in stopwords for w in h)
    header_candidates = [h for h in header_candidates if short_header(h)]
    if not header_candidates:
        return None
    header = max(header_candidates, key=lambda h: _header_alignment_score(band, h))
    if _header_alignment_score(band, header) < 0.5:
        return None
    rows = _rebuild_table_rows(band, header)
    kept = [r for r in rows if sum(_clean_number_cell(c) for c in r[1:]) >= 2]
    if len(kept) < 4:
        return None
    grid = [[""] + [w["text"] for w in header]] + kept
    consumed = {id(w) for w in header}
    for line, r in zip(band, rows):
        if r in kept:
            consumed.update(id(w) for w in line)
    facts = [f for f in _verbalize_grid(grid, caption).split("\n") if f.strip()]
    return _table_to_markdown(grid), facts, consumed


def _find_whitespace_tables(words: list[dict], caption: str = "") -> list[tuple[str, list[str], set[int]]]:
    """Detect borderless numeric tables (no ruling lines) from word alignment.

    Academic results tables often have no rules, so pdfplumber's line-based detection misses them
    and the cells flatten into prose. This finds a contiguous band of lines that each carry several
    numbers, splits side-by-side panels, picks the short-token label row above whose tokens best
    align to the numeric columns, rebuilds the grid, and trims prose rows that leaked in. Returns
    (text, consumed_word_ids) per table so the caller can drop those words from the prose.
    """
    by_top: dict[int, list[dict]] = {}
    for w in words:
        by_top.setdefault(round(w["top"] / 3) * 3, []).append(w)
    keys = sorted(by_top)
    lines = [sorted(by_top[k], key=lambda w: w["x0"]) for k in keys]

    def ncount(line: list[dict]) -> int:
        return sum(_is_number_token(w["text"]) for w in line)

    tables: list[tuple[str, list[str], set[int]]] = []
    i = 0
    n = len(lines)
    while i < n:
        if ncount(lines[i]) >= 2:
            j = i
            while j < n and ncount(lines[j]) >= 2:
                j += 1
            band = lines[i:j]
            if len(band) >= 4 and any(ncount(b) >= 3 for b in band):
                btop = keys[i]
                above = [
                    sorted(by_top[k], key=lambda w: w["x0"])
                    for k in keys if btop - 70 < k < btop and ncount(by_top[k]) < 2 and len(by_top[k]) >= 2
                ]
                split_x = _panel_split_x(band)
                if split_x is not None:
                    panels = [
                        ([[w for w in ln if (w["x0"] + w["x1"]) / 2 < split_x] for ln in band],
                         [[w for w in h if (w["x0"] + w["x1"]) / 2 < split_x] for h in above]),
                        ([[w for w in ln if (w["x0"] + w["x1"]) / 2 >= split_x] for ln in band],
                         [[w for w in h if (w["x0"] + w["x1"]) / 2 >= split_x] for h in above]),
                    ]
                else:
                    panels = [(band, above)]
                for pband, pabove in panels:
                    pband = [ln for ln in pband if ln]
                    pabove = [h for h in pabove if len(h) >= 3]
                    if len(pband) >= 4:
                        emitted = _emit_band_table(pband, pabove, caption)
                        if emitted:
                            tables.append(emitted)
            i = j
        else:
            i += 1
    return tables


def _extract_page_text(page: pdfplumber.pdf.Page) -> tuple[str, list[str]]:
    """Extract one pdfplumber page. Returns (page_text, table_facts) where page_text holds the
    Markdown tables and body prose in reading order, and table_facts is one verbalized sentence
    per table row/column. The facts are returned separately so each can become its own chunk: a
    focused fact like "BERT-LARGE: GLUE QQP 72.1" then matches an exact-term query on its own."""
    # A nearby "Table N:" line is used as a caption so verbalized rows carry the table's topic.
    page_caption_match = re.search(r"(Table\s+\d+[:.][^\n]{0,60})", page.extract_text() or "")
    caption = page_caption_match.group(1).strip() if page_caption_match else ""
    page_facts: list[str] = []

    # Phase 1: line-detected tables as Markdown, with their rows/columns also verbalized as facts.
    tables = _find_tables(page)
    table_bboxes = [t.bbox for t in tables]
    table_mds = []
    for t in tables:
        grid = [[(c or "").replace("\n", " ").strip() for c in row] for row in t.extract()]
        if len(grid) >= 3:
            page_facts += [f for f in _verbalize_grid(grid, caption).split("\n") if f.strip()]
        table_mds.append(_table_to_markdown(t.extract()))

    footnote_top = _find_footnote_top(page)

    # Phase 2: body text (words outside table regions and above footnote zone)
    all_words = page.extract_words(x_tolerance=1)
    body_words = [
        w for w in all_words
        if not any(_word_in_bbox(w, bb) for bb in table_bboxes)
        and w["top"] < footnote_top
    ]

    # Recover borderless numeric tables the line-based detector missed.
    whitespace_tables = _find_whitespace_tables(body_words, caption)
    consumed_ids = {wid for _, _, ids in whitespace_tables for wid in ids}
    whitespace_table_mds = [md for md, _, _ in whitespace_tables]
    for _, facts, _ in whitespace_tables:
        page_facts += facts
    if consumed_ids:
        body_words = [w for w in body_words if id(w) not in consumed_ids]

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
                sized = [c["size"] for c in line_chars if c.get("size")]
                avg_size = statistics.mean(sized) if sized else 0
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

    parts = table_mds + whitespace_table_mds + ([body_text] if body_text else [])
    return _repair_notation("\n\n".join(parts)), [_repair_notation(f) for f in page_facts]


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
            logger.warning("Skipping %s: %s", path.name, e)
    return documents


def load_pdfs(folder_path: str) -> list[dict[str, str]]:
    """Load all PDFs in folder_path using pdfplumber with table detection and multi-column ordering."""
    documents = []
    for path in Path(folder_path).glob("*.pdf"):
        try:
            pages_text = []
            doc_facts: list[str] = []
            with pdfplumber.open(str(path)) as pdf:
                for page in pdf.pages:
                    page_text, page_facts = _extract_page_text(page)
                    if page_text:
                        pages_text.append(page_text)
                    doc_facts += page_facts
            full_text = "\n\n".join(pages_text).strip()
            documents.append({"text": full_text, "source": path.name})
            # Each verbalized table fact is its own document so it becomes a single focused chunk.
            for fact in doc_facts:
                documents.append({"text": fact, "source": path.name})
        except Exception as e:
            logger.warning("Skipping %s: %s", path.name, e)
    return documents


def _markdown_table_facts(text: str) -> list[str]:
    """Verbalize each GitHub-style Markdown table in `text` into one fact per row/column.

    The nearest preceding heading is used as a caption, so a row like a latency table becomes a
    self-contained, retrievable fact ("... IndexFlatIP: Query latency 4 ms.")."""
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


def load_markdown(folder_path: str) -> list[dict[str, str]]:
    """Load all .md files; each file is one document, and every Markdown table row/column is also
    emitted as its own verbalized fact document so single-cell lookups retrieve a focused chunk."""
    documents = []
    for path in Path(folder_path).glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                documents.append({"text": text, "source": path.name})
                for fact in _markdown_table_facts(text):
                    documents.append({"text": fact, "source": path.name})
        except Exception as e:
            logger.warning("Skipping %s: %s", path.name, e)
    return documents


def load_txt(folder_path: str) -> list[dict[str, str]]:
    """Load all .txt files in folder_path as plain text documents."""
    documents = []
    for path in Path(folder_path).glob("*.txt"):
        try:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                documents.append({"text": text, "source": path.name})
        except Exception as e:
            logger.warning("Skipping %s: %s", path.name, e)
    return documents


def _iter_docx_blocks(document: "docx.document.Document") -> list[DocxParagraph | DocxTable]:
    """Yield the document's paragraphs and tables in body order (python-docx keeps them apart)."""
    blocks: list[DocxParagraph | DocxTable] = []
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            blocks.append(DocxParagraph(child, document))
        elif child.tag.endswith("}tbl"):
            blocks.append(DocxTable(child, document))
    return blocks


def load_docx(folder_path: str) -> list[dict[str, str]]:
    """Load all .docx files in folder_path, preserving headings and tables in reading order.

    Heading/Title paragraphs are emitted as Markdown headings and tables as Markdown tables, so
    the chunker treats them the same as the PDF/Markdown paths (tables stay atomic and inherit
    their section heading).
    """
    documents = []
    for path in Path(folder_path).glob("*.docx"):
        try:
            d = docx.Document(str(path))
            parts: list[str] = []
            for block in _iter_docx_blocks(d):
                if isinstance(block, DocxTable):
                    rows = [[cell.text for cell in row.cells] for row in block.rows]
                    parts.append(_table_to_markdown(rows))
                elif block.text.strip():
                    style = block.style.name if block.style else ""
                    if style.startswith("Heading") or style == "Title":
                        parts.append(f"## {block.text.strip()}")
                    else:
                        parts.append(block.text)
            text = "\n".join(parts)
            if text:
                documents.append({"text": text, "source": path.name})
        except Exception as e:
            logger.warning("Skipping %s — %s", path.name, e)
    return documents


def load_documents(folder_path: str) -> list[dict[str, str]]:
    """Load all supported documents (PDF, Markdown, text, DOCX) from folder_path."""
    return (
        load_pdfs(folder_path)
        + load_markdown(folder_path)
        + load_txt(folder_path)
        + load_docx(folder_path)
    )
