import logging
import re
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    text = re.sub(r"-\s*\n\s*", "", text)
    text = text.replace("\n", " ")
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"\bPage\s*\d+\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def load_pdfs(folder_path: str) -> list[dict[str, str]]:
    documents = []
    paths = Path(folder_path).glob("*.pdf")

    for path in paths:
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
