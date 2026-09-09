"""
Part 1 (Website side): Crawl the ZAIO website and extract clean text.

Uses requests + BeautifulSoup (pure Python, no headless browser needed) since
zaio.io is server-rendered (Next.js) and returns full HTML on first load.
If a future page requires JS execution to reveal content, swap this module's
`_fetch_html` for a Playwright/Puppeteer-based fetch -- the rest of the
pipeline (cleaning, chunking, metadata) stays identical.
"""
import os
import re
import time
import hashlib
import json
from dataclasses import dataclass
from typing import List, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    import lxml  # noqa: F401
    _PARSER = "lxml"
except ImportError:
    # Falls back to Python's built-in parser if lxml isn't installed/importable
    # (e.g. missing/broken wheel on some Windows setups). Slightly slower but
    # requires no extra dependency.
    _PARSER = "html.parser"

from app.config import (
    ZAIO_BASE_URL,
    ZAIO_SEED_PATHS,
    ZAIO_MAX_PAGES,
    WEB_CACHE_DIR,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ZaioRAGBot/1.0; "
        "+https://www.zaio.io) StudentHandbookAssistant"
    )
}

# Tags/classes that are almost always boilerplate (nav, headers, footers, scripts)
BOILERPLATE_TAGS = ["nav", "header", "footer", "script", "style", "noscript", "svg", "form"]
BOILERPLATE_ID_CLASS_HINTS = [
    "nav", "navbar", "menu", "footer", "header", "cookie", "breadcrumb",
    "sidebar", "social", "share-buttons",
]


@dataclass
class WebPage:
    url: str
    title: str
    text: str


def crawl_zaio_site(
    base_url: str = ZAIO_BASE_URL,
    seed_paths: List[str] = None,
    max_pages: int = ZAIO_MAX_PAGES,
    use_cache: bool = True,
    delay_seconds: float = 0.5,
) -> List[WebPage]:
    """
    Breadth-first crawl of the ZAIO site starting from a set of seed paths,
    following same-domain links up to `max_pages`. Returns cleaned page text.
    """
    seed_paths = seed_paths or ZAIO_SEED_PATHS
    os.makedirs(WEB_CACHE_DIR, exist_ok=True)

    to_visit: List[str] = [urljoin(base_url, p) for p in seed_paths]
    visited: Set[str] = set()
    pages: List[WebPage] = []
    domain = urlparse(base_url).netloc

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        url = _normalize_url(url)
        if url in visited:
            continue
        visited.add(url)

        html = _fetch_html(url, use_cache=use_cache)
        if html is None:
            continue

        page = _extract_clean_page(url, html)
        if page and len(page.text) > 80:  # skip near-empty pages
            pages.append(page)

        # discover more same-domain links
        for link in _extract_links(html, url):
            if urlparse(link).netloc == domain and link not in visited:
                if _is_content_like(link):
                    to_visit.append(link)

        time.sleep(delay_seconds)  # be polite

    return pages


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def _is_content_like(url: str) -> bool:
    """Skip obvious non-content links (assets, mail, tel, external apps, anchors)."""
    lowered = url.lower()
    skip_markers = [
        "mailto:", "tel:", "#", ".png", ".jpg", ".jpeg", ".svg", ".pdf",
        ".zip", ".ico", "/app/login", "discord.gg", "trustpilot.com",
        "facebook.com", "instagram.com", "linkedin.com", "youtube.com",
        "x.com", "threads.com", "applications.zaio.io",
    ]
    return not any(m in lowered for m in skip_markers)


def _fetch_html(url: str, use_cache: bool = True, timeout: int = 15) -> str:
    cache_path = _cache_path_for(url)
    if use_cache and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        html = resp.text
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html)
        return html
    except requests.RequestException as e:
        print(f"[web_crawler] failed to fetch {url}: {e}")
        return None


def _cache_path_for(url: str) -> str:
    h = hashlib.sha256(url.encode()).hexdigest()[:24]
    return os.path.join(WEB_CACHE_DIR, f"{h}.html")


def _extract_links(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, _PARSER)
    links = []
    for a in soup.find_all("a", href=True):
        links.append(urljoin(base_url, a["href"]))
    return links


def _extract_clean_page(url: str, html: str) -> WebPage:
    """Remove nav/header/footer/script boilerplate and return the main text."""
    soup = BeautifulSoup(html, _PARSER)

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url

    # Prefer a <main> region if present, else fall back to <body>
    main = soup.find("main") or soup.body or soup

    for tag_name in BOILERPLATE_TAGS:
        for tag in main.find_all(tag_name):
            if not getattr(tag, "decomposed", False):
                tag.decompose()

    for tag in main.find_all(True):
        if getattr(tag, "decomposed", False):
            continue  # already removed as a child of a previously decomposed tag
        id_class = " ".join([tag.get("id") or ""] + (tag.get("class") or [])).lower()
        if any(hint in id_class for hint in BOILERPLATE_ID_CLASS_HINTS):
            tag.decompose()

    text = main.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()

    return WebPage(url=url, title=title, text=text)


if __name__ == "__main__":
    pages = crawl_zaio_site(max_pages=10, use_cache=True)
    print(f"Crawled {len(pages)} pages")
    for p in pages[:3]:
        print(f"\n{p.url}  ({p.title})\n{p.text[:200]}...")
