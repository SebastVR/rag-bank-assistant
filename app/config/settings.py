from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "app/.env"),
        case_sensitive=False,
        extra="ignore",
    )

    # General
    app_name: str
    app_env: str
    app_host: str
    app_port: int

    # Scraping
    scraper_base_url: str
    scraper_allowed_domain: str
    scraper_max_pages: int
    scraper_timeout: int
    scraper_user_agent: str

    # Storage
    raw_data_path: str
    processed_data_path: str


settings = Settings()
