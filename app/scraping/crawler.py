from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from app.scraping.fetcher import HtmlFetcher


class ScrapedSection(BaseModel):
    heading: str
    content: str


class ScrapedDocument(BaseModel):
    doc_id: str
    source: str
    url: str
    title: str
    category: str = "general"
    content: str
    sections: List[ScrapedSection] = Field(default_factory=list)
    headings: List[str] = Field(default_factory=list)
    internal_links: List[str] = Field(default_factory=list)
    raw_file_path: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


def is_internal_link(href: str, base_domain: str) -> bool:
    if not href:
        return False
    if href.startswith("/") or base_domain in href:
        return True
    return False


def crawl_and_save(
    start_url: str,
    base_domain: str,
    out_dir: str = "/app/debug/pages",
    max_pages: int = 20,
    delay: float = 1.0,
):
    os.makedirs(out_dir, exist_ok=True)
    fetcher = HtmlFetcher()
    visited = set()
    queue = [start_url]
    manifest = []
    page_count = 0

    while queue and page_count < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        try:
            result = fetcher.fetch(url)
        except Exception as e:
            print(f"[ERROR] {url}: {e}")
            continue
        visited.add(url)
        soup = BeautifulSoup(result.html, "lxml")
        title = soup.title.get_text(strip=True) if soup.title else ""
        # Extraer enlaces internos
        links = [a.get("href") for a in soup.find_all("a", href=True)]
        internal_links = []
        for href in links:
            if is_internal_link(href, base_domain):
                full_url = urljoin(start_url, href)
                if (
                    full_url not in visited
                    and full_url not in queue
                    and base_domain in full_url
                ):
                    internal_links.append(full_url)
        # Guardar HTML
        fname = f"bbva_{page_count+1}.html"
        fpath = os.path.join(out_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(result.html)
        # Guardar en manifest
        manifest.append(
            {
                "url": url,
                "title": title,
                "file": fname,
                "internal_links": internal_links,
            }
        )
        # Agregar nuevos enlaces a la cola
        for link in internal_links:
            if (
                link not in visited
                and link not in queue
                and len(queue) + page_count < max_pages
            ):
                queue.append(link)
        page_count += 1
        print(f"[OK] {url} -> {fname} ({len(result.html)} chars)")
        time.sleep(delay)
    # Guardar manifest
    manifest_path = os.path.join(out_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"[DONE] {page_count} pages saved. Manifest: {manifest_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Crawl BBVA site and save HTMLs + manifest."
    )
    parser.add_argument(
        "--start-url", type=str, default="https://www.bbva.com.co/", help="URL inicial"
    )
    parser.add_argument(
        "--base-domain",
        type=str,
        default="bbva.com.co",
        help="Dominio base para filtrar enlaces internos",
    )
    parser.add_argument(
        "--max-pages", type=int, default=20, help="Máximo de páginas a descargar"
    )
    parser.add_argument(
        "--delay", type=float, default=1.0, help="Delay entre requests (segundos)"
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="/app/debug/pages",
        help="Directorio de salida para los HTML y manifest",
    )
    args = parser.parse_args()
    crawl_and_save(
        start_url=args.start_url,
        base_domain=args.base_domain,
        out_dir=args.out_dir,
        max_pages=args.max_pages,
        delay=args.delay,
    )
