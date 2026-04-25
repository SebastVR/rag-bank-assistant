from fastapi import APIRouter, Query

from app.services.db_populate_service import populate_scraped_documents_from_prefix

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/populate-db")
def populate_db(
    prefix: str = Query(
        ..., description="Prefijo S3/carpeta de scraping (ej: bbva_html)"
    ),
):
    """
    Pobla la base de datos usando process_all_html_and_return_json con el prefijo indicado.
    """
    result = populate_scraped_documents_from_prefix(prefix)
    return result
