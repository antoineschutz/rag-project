import re
import statistics

import pdfplumber

from src.ingestion.pdf_layout import (
    _column_boundaries_from_words,
    _find_column_split,
    _find_footnote_top,
    _repair_notation,
    _word_in_bbox,
    _words_to_text,
)
from src.ingestion.table_verbalize import (
    _clean_number_cell,
    _is_number_token,
    _table_to_markdown,
    _verbalize_grid,
)


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
