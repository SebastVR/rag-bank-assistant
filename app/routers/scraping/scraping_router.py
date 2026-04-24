from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.controllers.scraping.scraping_controller import (
    get_processed_document,
    list_processed_documents,
    process_scraped_html,
    run_crawl,
)

router = APIRouter(prefix="/api/v1/scraping", tags=["scraping"])


class CrawlRequest(BaseModel):
    base_url: str | None = Field(default=None)
    allowed_domain: str | None = Field(default=None)
    max_pages: int | None = Field(default=None, ge=1, le=500)
    timeout: int | None = Field(default=None, ge=5, le=120)


@router.post("/crawl")
def crawl_site(payload: CrawlRequest):
    """
    Inicia el crawling para el dominio especificado y guarda los HTMLs bajo el prefijo correspondiente en S3.
    """
    try:
        return run_crawl(
            base_url=payload.base_url,
            allowed_domain=payload.allowed_domain,
            max_pages=payload.max_pages,
            timeout=payload.timeout,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process")
def process_html_documents(
    allowed_domain: str = Query(..., description="Dominio a procesar, e.g. bbva.com.co")
):
    """
    Procesa los HTMLs scrapeados bajo el prefijo correspondiente al dominio en S3.
    """
    try:
        return process_scraped_html(allowed_domain=allowed_domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
def get_processed_documents(
    allowed_domain: str = Query(
        ..., description="Dominio a consultar, e.g. bbva.com.co"
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    q: str | None = Query(default=None, min_length=1),
):
    try:
        return list_processed_documents(
            allowed_domain=allowed_domain, limit=limit, offset=offset, q=q
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{doc_id}")
def get_processed_document_by_id(
    doc_id: str,
    allowed_domain: str = Query(
        ..., description="Dominio a consultar, e.g. bbva.com.co"
    ),
):
    try:
        return get_processed_document(doc_id, allowed_domain=allowed_domain)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
