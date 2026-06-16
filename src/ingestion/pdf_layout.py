import re

import pdfplumber


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
