from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from app.models.scraped_document import ScrapedDocument


class ScrapingStorage:
    def __init__(self, raw_dir: str, processed_dir: str) -> None:
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def save_raw_html(self, url: str, html: str) -> str:
        file_name = self._build_safe_name(url, extension="html")
        file_path = self.raw_dir / file_name
        file_path.write_text(html, encoding="utf-8")
        return str(file_path)

    def save_processed_document(self, document: ScrapedDocument) -> str:
        file_name = self._build_safe_name(document.url, extension="json")
        file_path = self.processed_dir / file_name
        file_path.write_text(
            json.dumps(document.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return str(file_path)

    def _build_safe_name(self, url: str, extension: str) -> str:
        parsed = urlparse(url)
        domain = parsed.netloc.replace(".", "_")
        path = parsed.path.strip("/").replace("/", "_") or "home"
        return f"{domain}__{path}.{extension}"
