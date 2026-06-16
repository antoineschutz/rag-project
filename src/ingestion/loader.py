import logging
from pathlib import Path

import docx
import pdfplumber
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph

from src.ingestion.pdf_tables import _extract_page_text
from src.ingestion.table_verbalize import _markdown_table_facts, _table_to_markdown

logger = logging.getLogger(__name__)


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
            logger.warning("Skipping %s: %s", path.name, e)
    return documents


def load_documents(folder_path: str) -> list[dict[str, str]]:
    """Load all supported documents (PDF, Markdown, text, DOCX) from folder_path."""
    return (
        load_pdfs(folder_path)
        + load_markdown(folder_path)
        + load_txt(folder_path)
        + load_docx(folder_path)
    )
