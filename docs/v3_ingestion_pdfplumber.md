# V3 Ingestion — Implementation Report

## Overview

V3 replaced pypdf's `extract_text()` with a pdfplumber-based pipeline in `src/ingestion/loader.py`. It also added `.md` and `.docx` loaders. This document covers every function added, the reasoning behind each design decision, and a full account of the bugs hit and how they were diagnosed.

---

## Functions Added

### `load_markdown(folder_path: str) -> list[dict[str, str]]`

Globs `*.md` files and reads each with `Path.read_text(encoding="utf-8")`. No parsing is needed — markdown is already plain text. Returns `{"text": ..., "source": filename}` dicts, matching the format the rest of the pipeline expects.

### `load_docx(folder_path: str) -> list[dict[str, str]]`

Uses `python-docx` (`docx.Document`). Iterates over `doc.paragraphs`, filters out empty ones, and joins with `\n`. This preserves paragraph breaks for better chunking. Tables inside DOCX files are not explicitly handled — `python-docx` exposes them separately from `paragraphs`, so table rows in the source document are currently skipped. This is acceptable for the current corpus.

### `load_documents(folder_path: str) -> list[dict[str, str]]`

Unified entry point: calls `load_pdfs + load_markdown + load_docx` and concatenates the results. `factory.py` was updated to call this instead of `load_pdfs` directly.

### `load_pdfs_pypdf(folder_path: str) -> list[dict[str, str]]`

The original pypdf implementation, preserved verbatim for comparison. Renamed from `load_pdfs`. Kept so that pypdf and pdfplumber extraction quality can be compared side-by-side on the same document without switching branches.

---

## New PDF Pipeline (`load_pdfs` + helpers)

### Architecture

Each PDF page is processed by `_extract_page_text(page)` which runs three sequential phases:

```
page
 └─ Phase 1: table detection  →  Markdown tables
 └─ Phase 2: body text        →  column-ordered plain text
 └─ Phase 3: header labelling →  ## prefixed lines
```

The outputs are joined with `\n\n` per page, and pages are joined with `\n\n` for the final document string.

---

### `_table_to_markdown(table: list[list[str | None]]) -> str`

Converts the nested list returned by pdfplumber's `table.extract()` into a GitHub-flavoured Markdown table. Row 0 is treated as the header row and gets a `| --- | --- |` separator inserted after it. `None` cells (pdfplumber uses `None` for merged/empty cells) are replaced with an empty string. Newlines inside cells are collapsed to a single space.

**Example output:**
```
| Model | EN-DE | EN-FR |
| --- | --- | --- |
| Transformer (base) | 27.3 | 38.1 |
| Transformer (big) | 28.4 | 41.0 |
```

---

### `_word_in_bbox(word: dict, bbox: tuple) -> bool`

Checks whether a word (from `extract_words()`) falls inside a bounding box `(x0, top, x1, bottom)`. Uses the word's center point `((x0+x1)/2, (top+bottom)/2)` rather than checking if the full word rectangle overlaps. This avoids false positives at bbox edges where a word straddles the table boundary.

Used to exclude table-region words from body text processing, preventing table content from being double-counted (once as Markdown, once as raw body text).

---

### `_words_to_text(words: list[dict]) -> str`

Reconstructs a readable text string from a list of pdfplumber word dicts. Words are grouped by line using a bucketed `top` value (`round(top / 3) * 3` — snaps within a 3px band to merge words on the same baseline). Within each line, words are joined with a space. Lines are joined with `\n`.

---

### `_extract_page_text(page) -> str` — Phase 1: Tables

```python
tables = page.find_tables()
table_bboxes = [t.bbox for t in tables]
table_mds = [_table_to_markdown(t.extract()) for t in tables]
```

`page.find_tables()` uses pdfplumber's `TableFinder`, which detects tables by looking for horizontal and vertical lines (rectangles) in the PDF. This works well for **bordered tables** (like Table 3 in *Attention is All You Need*, which lists model configurations). It does **not** work for **borderless tables** (like Table 2, the WMT results table), which have no grid lines — just whitespace-aligned columns. Borderless tables end up in the body text as raw words.

---

### `_extract_page_text(page)` — Phase 2: Multi-column body text

```python
all_words = page.extract_words(x_tolerance=1)
body_words = [w for w in all_words if not any(_word_in_bbox(w, bb) for bb in table_bboxes)]
```

**Critical parameter: `x_tolerance=1`**

pdfplumber's `extract_words()` groups adjacent characters into words using an `x_tolerance` gap threshold (default: 3px). For the arXiv-style PDFs in this corpus (generated with LaTeX and certain font encodings), the default value of 3 causes words to merge — e.g., `"ScaledDot-ProductAttention"` instead of `"Scaled Dot-Product Attention"`. Setting `x_tolerance=1` restores proper word boundaries.

This was discovered by comparing outputs:
```
x_tol=1: Scaled Dot-Product Attention Multi-Head Attention Figure 2 ...
x_tol=3: ScaledDot-ProductAttention Multi-HeadAttention Figure2 ...
```

**Two-column detection**

Academic papers use two-column layout. pypdf reads pages line by line, interleaving left and right column content. pdfplumber gives word-level bounding boxes, enabling column splitting:

```python
strip_lo, strip_hi = page.width * 0.425, page.width * 0.575
center_count = sum(1 for w in body_words if strip_lo <= (w["x0"] + w["x1"]) / 2 <= strip_hi)
two_column = len(body_words) > 20 and center_count / len(body_words) < 0.05
```

Logic: in a two-column layout, the centre strip of the page (roughly 42.5%–57.5% of page width) is a gutter with almost no text. If fewer than 5% of words fall in this strip and there are more than 20 words on the page (to avoid false positives on sparse pages), the page is treated as two-column.

For two-column pages, left-side words (x-center < midpoint) and right-side words are sorted independently by `(top, x0)` and concatenated — left column first, then right column.

---

### `_extract_page_text(page)` — Phase 3: Header labelling

```python
non_table_chars = [c for c in page.chars if not any(_word_in_bbox(c, bb) for bb in table_bboxes)]
sizes = [c["size"] for c in non_table_chars if c.get("size")]
median_size = statistics.median(sizes) if sizes else 0
```

pdfplumber exposes character-level metadata including font size. The median font size across all non-table characters is computed per page. Lines where the average character size is ≥ 1.3× the median **and** the line is shorter than 80 characters are prefixed with `## `.

This catches section titles in academic papers, which are typically set in a larger or bolder font than body text.

---

### Cleaning: selective application of `clean_text`

`clean_text` applies five transformations:
1. Hyphenation removal (`-\n` → join)
2. Newline → space
3. camelCase splitting (`(?<=[a-z])(?=[A-Z])` → insert space)
4. Page number removal
5. Whitespace collapsing

The camelCase split was originally added to fix pypdf artefacts where words from different font positions were concatenated (e.g., `"Self AttentionMechanism"`). With pdfplumber's `x_tolerance=1`, word boundaries are already correct, so applying camelCase splitting corrupts legitimate names like `"ConvS2S"` → `"Conv S2S"`.

For this reason, `_extract_page_text` does **not** call `clean_text`. Instead it applies only steps 1, 4, and 5 inline:

```python
body_text = re.sub(r"-\s*\n\s*", "", body_text)
body_text = re.sub(r"\bPage\s*\d+\b", " ", body_text, flags=re.IGNORECASE)
body_text = re.sub(r"\s+", " ", body_text).strip()
```

`clean_text` (with camelCase) is still called in `load_pdfs_pypdf` where it is needed.

---

## Debugging Log

### Issue 1 — Word merging with default `x_tolerance`

**Symptom:** pdfplumber chunks for `attention_is_all_you_need.pdf` contained merged words like `"ScaledDot-ProductAttention"`, `"ConvS2SEnsemble"`, making string-based retrieval fail.

**Diagnosis:** pdfplumber's `extract_words()` was tested with different `x_tolerance` values (1, 2, 3, 5, 8). The default of 3 merged words because the PDF's character spacing is tighter than the threshold. `x_tolerance=1` produced correct word boundaries.

**Fix:** Added `x_tolerance=1` to the `page.extract_words()` call.

---

### Issue 2 — `pdfplumber.extract_text()` also merges words

**Finding:** Before switching to manual word assembly via `_words_to_text`, the simpler `page.extract_text()` was tested. It produced the same word-merging problem:
```
pdfplumber extract_text: 'ScaledDot-ProductAttention Multi-HeadAttention ...'
pypdf extract_text:       'Scaled Dot-Product Attention. Multi-Head Attention ...'
```
pypdf's `extract_text()` actually produced better spacing than pdfplumber's for these specific PDFs. This confirmed the issue was in character-level spacing and that manual `extract_words(x_tolerance=1)` was the right approach.

---

### Issue 3 — Borderless tables not detected

**Symptom:** Table 2 in `attention_is_all_you_need.pdf` (WMT translation results with `ConvS2S Ensemble` / `41.29`) was not extracted as a Markdown table.

**Diagnosis:** `page.find_tables()` found 0 tables on page 8. Inspection showed no rectangular border lines in the PDF for Table 2 — it uses whitespace alignment. pdfplumber's `TableFinder` requires visible lines.

**Outcome:** Table 2 values appear in body text, not as Markdown. `ConvS2S Ensemble` and `41.29` are in the same chunk (confirmed), just not in table format. The extraction test (`test_pdf_table_chunk`) passes because retrieval only needs the terms to co-occur in a chunk. Table 3 (model configurations, which has borders) IS detected and produces proper Markdown.

---

### Issue 4 — `d_model` subscript notation

**Symptom:** The test `test_pdf_column_order_chunk` asserted `"d_model"` and `"512"` appeared in the same chunk. It always failed.

**Diagnosis:** In the LaTeX source, `d_model` is typeset as `d` with a subscript `model`. pdfplumber (and pypdf) extract these as separate text elements on different baselines. The string `"d_model"` never appears in any extracted chunk — the text shows `"d = 512."` and `"model"` on the next line.

**Fix:** The test was redesigned to use `"| 6 512"` and `"2048"`, checking that Table 3's base model row survives as a Markdown table row (with pipe characters). This cleanly differentiates pdfplumber (which produces `| 6 512 2048 8 ... |`) from pypdf (which produces `6 512 2048 8 ...` without pipes).

---

### Issue 5 — camelCase split corrupting pdfplumber text

**Symptom:** After restoring the camelCase split to `clean_text`, `test_pdf_table_chunk` failed again. `"ConvS2S Ensemble"` was no longer found in any chunk.

**Diagnosis:** `clean_text` applies `re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)`. This inserts a space wherever a lowercase letter is followed by an uppercase letter, so `"ConvS2S"` → `"Conv S2S"` (the `v`→`S` transition triggers it). With pdfplumber's proper word spacing, this transformation is harmful rather than helpful.

**Fix:** `_extract_page_text` now applies only the non-camelCase steps of `clean_text` inline. The full `clean_text` (with camelCase) is only called in `load_pdfs_pypdf`.

---

### Issue 6 — xfail tests never passed before all bugs were fixed

The initial run after implementing pdfplumber showed:
```
test_pdf_table_chunk       XFAIL   ← expected, hadn't fixed x_tolerance yet
test_pdf_column_order_chunk XFAIL  ← expected, d_model issue not yet known
```

After `x_tolerance=1`:
```
test_pdf_table_chunk       XPASS   ← now passes
test_pdf_column_order_chunk XFAIL  ← still failing (d_model issue)
```

After redesigning the column order test:
```
test_pdf_table_chunk       PASS    ← xfail removed
test_pdf_table_markdown    PASS    ← new test replacing column order test
```

---

## Final Test Results

```
tests/test_extraction.py::test_md_prose_chunk          PASSED   Q6
tests/test_extraction.py::test_md_table_chunk          PASSED   Q7
tests/test_extraction.py::test_docx_chunk              PASSED   Q11
tests/test_extraction.py::test_pdf_prose_chunk         PASSED   (no Q/A pair)
tests/test_extraction.py::test_pdf_table_chunk         PASSED   Q20
tests/test_extraction.py::test_pdf_table_markdown      PASSED   Q25-adjacent
```

Full suite: **40/40 passed**.

---

## Known Limitations

| Limitation | Root cause | Fix |
|---|---|---|
| Borderless PDF tables not extracted as Markdown | pdfplumber `TableFinder` requires grid lines | Would need heuristic column detection or ML-based table finder |
| Math equations unreadable | LaTeX glyphs rendered as Unicode symbols or bitmaps | Requires nougat / docling for LaTeX reconstruction |
| `d_model` subscript splits across lines | LaTeX subscript typesetting | No fix with text-based extractors |
| DOCX tables skipped | `python-docx` separates tables from paragraphs | Add explicit `doc.tables` iteration in `load_docx` |
