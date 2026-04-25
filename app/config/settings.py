# Límite de chunks por consulta
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="app/.env", extra="ignore")

    # MinIO (local/dev)
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket_name: str

    # AWS S3 (producción)
    aws_region_name: str
    aws_s3_access_key_id: str
    aws_s3_secret_access_key: str
    aws_s3_bucket_name: str

    # General
    app_name: str = "rag-bank-assistant"
    app_env: str = "dev"  # "dev" para local/dev, "prod" para producción
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Celery
    celery_broker_url: str
    celery_backend_url: str
    rabbitmq_default_user: str
    rabbitmq_default_pass: str

    # Scraping
    scraper_base_url: str
    scraper_allowed_domain: str
    scraper_max_pages: int = 10
    scraper_timeout: int = 20
    scraper_user_agent: str

    # Storage
    raw_data_path: str = "data/raw"
    processed_data_path: str = "data/processed"

    # Postgres (para desarrollo y producción)
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int = 5432

    # Supabase (para producción cloud opcional)
    supabase_url: str | None = None
    supabase_service_key: str | None = None
    supabase_attachment_bucket: str | None = None

    # Qdrant (vector store)
    qdrant_host: str  # Host del contenedor Qdrant
    qdrant_port: int  # Puerto HTTP
    qdrant_grpc_port: int  # Puerto gRPC
    qdrant_collection_name: str
    qdrant_max_chunks_retrieved: int  # Límite de chunks por consulta
    qdrant_max_chunks_reranked: int  # Límite de chunks por reordenamiento


settings = Settings()
