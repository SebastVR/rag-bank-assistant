# import io

# from celery.utils.log import get_task_logger

# from app.celery_worker.celery_config import celery_app
# from app.config.config import settings
# from app.controllers.answer_controller import generate_all_answer_by_project_id
# from app.controllers.file_controller import process_document
# from app.db.db_connection import SessionWriter
# from app.models.document import Document, DocumentStatus
# from app.services.s3_utils import get_file_from_s3

# LLM_NAME = settings.llm_name

# logger = get_task_logger(__name__)


# @celery_app.task(
#     name="proposals.process_file_task",
#     queue="proposals",
#     acks_late=True,
# )
# def process_file_task(document_id, file_key, file_extension):
#     logger.info(f"Processing file with id: {document_id}")

#     db = SessionWriter()
#     document = db.get(Document, document_id)
#     if not document:
#         logger.error(f"Document with id {document_id} not found.")
#         raise ValueError(f"Document with id {document_id} not found")

#     try:
#         # Descargar archivo desde S3
#         logger.info(f"Downloading file from S3: {file_key}")
#         file_data = get_file_from_s3(file_key)

#         # Procesar documento
#         text, abstract = process_document(document_id, file_data, file_extension, db)
#         document.summary = abstract
#         document.status = DocumentStatus.processed
#         db.commit()
#         db.refresh(document)
#         logger.info(f"Document {document_id} processed successfully.")
#     except Exception as e:
#         document.status = DocumentStatus.failed
#         db.commit()
#         db.refresh(document)
#         logger.error(f"Error processing document {document_id}: {e}")


# @celery_app.task(
#     name="proposals.generate_report_task",
#     queue="proposals",  # 👈 fuerza cola
#     acks_late=True,  # opcional: robustez ante caídas
# )
# def generate_report_task(project_id, questionnaire_id):
#     """Generate a report for a specific project and questionnaire."""
#     logger.info(
#         f"Generating report for project {project_id} and questionnaire {questionnaire_id}"
#     )

#     db = SessionWriter()
#     generate_all_answer_by_project_id(db, project_id, questionnaire_id)
