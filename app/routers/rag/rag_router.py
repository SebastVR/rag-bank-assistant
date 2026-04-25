from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.celery_worker.tasks import (
    process_pdf_file_task,
    process_pending_ingestion_task,
    vectorize_html_document_task,
)
from app.db.db_connection import SessionLocal
from app.models.document_file import DocumentFile
from app.services.rag.rag_query_service import RagQueryService

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])


class RagQuestionRequest(BaseModel):
    question: str = Field(..., min_length=3)
    use_rerank: bool = True


@router.post("/ingestion/pending")
def trigger_pending_ingestion(limit: int = 20):
    task = process_pending_ingestion_task.delay(limit=limit)
    return {
        "message": "Pending ingestion task dispatched",
        "task_id": task.id,
        "limit": limit,
    }


@router.post("/ingestion/files/{document_file_id}")
def trigger_pdf_ingestion(document_file_id: int):
    task = process_pdf_file_task.delay(document_file_id=document_file_id)
    return {
        "message": "PDF ingestion task dispatched",
        "task_id": task.id,
        "document_file_id": document_file_id,
    }


@router.post("/ingestion/html/{scraped_document_id}")
def trigger_html_ingestion(scraped_document_id: int):
    task = vectorize_html_document_task.delay(scraped_document_id=scraped_document_id)
    return {
        "message": "HTML ingestion task dispatched",
        "task_id": task.id,
        "scraped_document_id": scraped_document_id,
    }


@router.post("/query")
def rag_query(request: RagQuestionRequest):
    service = RagQueryService()
    return service.answer(question=request.question, use_rerank=request.use_rerank)


# --- Celery/status: Consultar estado de procesamiento de PDF ---
@router.get("/status/files/{document_file_id}")
def get_pdf_file_status(document_file_id: int):
    db = SessionLocal()
    try:
        file_row = db.get(DocumentFile, document_file_id)
        if not file_row:
            return {"status": "not_found", "document_file_id": document_file_id}
        return {
            "document_file_id": file_row.id,
            "status": file_row.status,
            "error_message": file_row.error_message,
            "summary": file_row.summary,
            "file_path": file_row.file_path,
            "processed_at": file_row.processed_at,
        }
    finally:
        db.close()
