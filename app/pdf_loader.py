"""
Part 1 (PDF side): Load the Student Handbook and extract text, page by page,
so every chunk we produce later can be traced back to a page number.
"""
from dataclasses import dataclass
from typing import List
from pypdf import PdfReader


@dataclass
class PageText:
    page_number: int   # 1-indexed, human-friendly
    text: str


def load_handbook_pages(pdf_path: str) -> List[PageText]:
    """Extract raw text from every page of the handbook PDF."""
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        cleaned = _clean_pdf_text(raw)
        if cleaned.strip():
            pages.append(PageText(page_number=i, text=cleaned))
    return pages


def _clean_pdf_text(text: str) -> str:
    """Light cleanup: collapse excess whitespace/newlines introduced by PDF extraction."""
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    joined = " ".join(lines)
    while "  " in joined:
        joined = joined.replace("  ", " ")
    return joined.strip()


if __name__ == "__main__":
    import sys
    from app.config import HANDBOOK_PDF_PATH

    path = sys.argv[1] if len(sys.argv) > 1 else HANDBOOK_PDF_PATH
    pages = load_handbook_pages(path)
    print(f"Extracted {len(pages)} non-empty pages from {path}")
    for p in pages[:2]:
        print(f"\n--- Page {p.page_number} ---\n{p.text[:300]}...")
