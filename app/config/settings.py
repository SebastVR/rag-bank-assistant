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
    app_env: str = "dev"  # "dev" para MinIO, "prod" para AWS S3
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Scraping
    scraper_base_url: str
    scraper_allowed_domain: str
    scraper_max_pages: int = 10
    scraper_timeout: int = 20
    scraper_user_agent: str

    # Storage
    raw_data_path: str = "data/raw"
    processed_data_path: str = "data/processed"


settings = Settings()
