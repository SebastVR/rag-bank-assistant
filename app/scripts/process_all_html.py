import glob
import hashlib
import json
import os
import re

from app.scraping.cleaner import HtmlCleaner
from app.scraping.parser import HtmlParser


def resolve_html_dir() -> str:
    candidates = [
        "/app/debug/pages",  # ruta montada en docker-compose
        "app/debug/pages",  # ruta local desde la raiz del repo
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path
    raise FileNotFoundError("No se encontro el directorio de HTMLs scrapeados")


HTML_DIR = resolve_html_dir()

# Encuentra todos los archivos HTML descargados
html_files = glob.glob(os.path.join(HTML_DIR, "bbva_*.html"))

parser = HtmlParser()
cleaner = HtmlCleaner()


unique_hashes = set()
unique_docs = {}

for html_path in html_files:
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    # Extraer la URL real de la página web (og:url o canonical)
    source_url = None
    og_url_match = re.search(
        r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\']([^"\']+)["\']', html
    )
    if og_url_match:
        source_url = og_url_match.group(1)
    else:
        canonical_match = re.search(
            r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', html
        )
        if canonical_match:
            source_url = canonical_match.group(1)
    # Usa el nombre del archivo como base_url temporal
    base_url = f"file://{os.path.abspath(html_path)}"
    parsed_page = parser.parse(html, base_url=base_url)
    cleaned_html = cleaner.clean_html(html)
    clean_text = cleaner.clean_parsed_page(parsed_page, cleaned_html)
    # Deduplicar por hash de texto limpio
    doc_hash = hashlib.md5(clean_text.encode("utf-8")).hexdigest()
    if doc_hash not in unique_hashes:
        unique_hashes.add(doc_hash)
        file_key = os.path.splitext(os.path.basename(html_path))[0]
        unique_docs[file_key] = {
            "file": os.path.basename(html_path),
            "title": parsed_page.title,
            "headings": parsed_page.headings,
            "text": clean_text,
            "url": getattr(parsed_page, "url", base_url),
            "source_url": source_url,
        }

print(f"Total HTMLs procesados: {len(html_files)}")
print(f"Documentos únicos (por hash de texto): {len(unique_docs)}")
for k, doc in list(unique_docs.items())[:3]:
    print("\n--- Ejemplo de documento ---")
    print(f"Clave: {k}")
    print(f"Archivo: {doc['file']}")
    print(f"Título: {doc['title']}")
    print(f"Headings: {doc['headings']}")
    print(f"Texto (primeros 500 chars): {doc['text'][:500]}")


# Guardar todos los documentos únicos en un archivo JSON para análisis posterior
def resolve_json_dir() -> str:
    candidates = [
        "/app/debug/json",  # ruta montada en docker-compose
        "app/debug/json",  # ruta local desde la raiz del repo
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path
    os.makedirs(candidates[1], exist_ok=True)
    return candidates[1]


JSON_DIR = resolve_json_dir()
output_path = os.path.join(JSON_DIR, "html_docs_unicos.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(unique_docs, f, ensure_ascii=False, indent=2)
print(f"\nTodos los documentos únicos se guardaron en {output_path}")
