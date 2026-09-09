"""
Part 1: Build/refresh the combined knowledge base (Student Handbook + ZAIO website).

Usage:
    python build_index.py                # full rebuild (handbook + website)
    python build_index.py --pdf-only     # only re-ingest the handbook
    python build_index.py --web-only     # only re-crawl the website
    python build_index.py --no-cache     # ignore cached HTML, re-fetch pages
"""
import argparse

from app.config import HANDBOOK_PDF_PATH
from app.pdf_loader import load_handbook_pages
from app.web_crawler import crawl_zaio_site
from app.chunker import split_into_chunks
from app.vector_store import KnowledgeBase


def ingest_handbook(kb: KnowledgeBase) -> int:
    print(f"Loading handbook: {HANDBOOK_PDF_PATH}")
    pages = load_handbook_pages(HANDBOOK_PDF_PATH)
    print(f"  -> {len(pages)} pages extracted")

    all_chunks, all_meta = [], []
    for page in pages:
        for chunk in split_into_chunks(page.text):
            all_chunks.append(chunk)
            all_meta.append({
                "source": "Student Handbook",
                "page": page.page_number,
                "url": "",
                "display_source": f"Student Handbook - Page {page.page_number}",
            })

    if all_chunks:
        kb.add_chunks(all_chunks, all_meta)
    print(f"  -> {len(all_chunks)} handbook chunks embedded and stored")
    return len(all_chunks)


def ingest_website(kb: KnowledgeBase, use_cache: bool = True) -> int:
    print("Crawling ZAIO website...")
    pages = crawl_zaio_site(use_cache=use_cache)
    print(f"  -> {len(pages)} pages crawled")

    all_chunks, all_meta = [], []
    for page in pages:
        for chunk in split_into_chunks(page.text):
            all_chunks.append(chunk)
            all_meta.append({
                "source": "ZAIO Website",
                "page": 0,
                "url": page.url,
                "display_source": page.url,
            })

    if all_chunks:
        kb.add_chunks(all_chunks, all_meta)
    print(f"  -> {len(all_chunks)} website chunks embedded and stored")
    return len(all_chunks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-only", action="store_true")
    parser.add_argument("--web-only", action="store_true")
    parser.add_argument("--no-cache", action="store_true", help="ignore cached HTML pages")
    parser.add_argument("--reset", action="store_true", help="wipe the collection before ingesting")
    args = parser.parse_args()

    kb = KnowledgeBase()
    if args.reset:
        print("Resetting existing collection...")
        kb.reset()

    total = 0
    if not args.web_only:
        total += ingest_handbook(kb)
    if not args.pdf_only:
        total += ingest_website(kb, use_cache=not args.no_cache)

    print(f"\nDone. Collection now holds {kb.count()} chunks total (added {total} this run).")


if __name__ == "__main__":
    main()
