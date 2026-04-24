from __future__ import annotations

import hashlib
from typing import List
from urllib.parse import urlparse

from app.models.scraped_document import ScrapedDocument, ScrapedSection
from app.scraping.parser import ParsedPage


class DocumentExtractor:
    def build_document(
        self,
        parsed_page: ParsedPage,
        cleaned_text: str,
        raw_file_path: str,
        source_name: str = "bbva",
    ) -> ScrapedDocument:
        doc_id = self._build_doc_id(parsed_page.url)

        sections: List[ScrapedSection] = [
            ScrapedSection(heading=section.heading, content=section.content)
            for section in parsed_page.sections
            if section.heading and section.content
        ]

        category = self._infer_category(
            parsed_page.url, parsed_page.title, cleaned_text
        )

        return ScrapedDocument(
            doc_id=doc_id,
            source=source_name,
            url=parsed_page.url,
            title=parsed_page.title,
            category=category,
            content=cleaned_text,
            sections=sections,
            headings=parsed_page.headings,
            internal_links=parsed_page.internal_links,
            raw_file_path=raw_file_path,
            metadata={
                "domain": urlparse(parsed_page.url).netloc,
                "num_headings": len(parsed_page.headings),
                "num_sections": len(sections),
                "num_internal_links": len(parsed_page.internal_links),
            },
        )

    def _build_doc_id(self, url: str) -> str:
        digest = hashlib.md5(url.encode("utf-8")).hexdigest()
        return f"doc_{digest}"

    def _infer_category(self, url: str, title: str, content: str) -> str:
        text = f"{url} {title} {content}".lower()

        rules = {
            "creditos": [
                "credito",
                "crédito",
                "prestamo",
                "préstamo",
                "libranza",
                "hipotecario",
            ],
            "cuentas": ["cuenta", "ahorros", "corriente"],
            "tarjetas": ["tarjeta", "visa", "mastercard"],
            "servicios_digitales": [
                "app",
                "digital",
                "banca móvil",
                "banca movil",
                "transferencia",
            ],
            "seguros": ["seguro", "asegurado", "protegido"],
            "faq": ["preguntas frecuentes", "faq", "¿", "?"],
        }

        for category, keywords in rules.items():
            if any(keyword in text for keyword in keywords):
                return category

        return "general"
