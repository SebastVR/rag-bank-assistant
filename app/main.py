from fastapi import FastAPI

from app.config.settings import settings
from app.routers.scraping.scraping_router import router as scraping_router

api = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="RAG Banking Assistant with Web Scraping",
)

api.include_router(scraping_router)


@api.get("/")
def root():
    return {
        "message": "RAG Bank Assistant API is running",
        "app_name": settings.app_name,
    }


@api.get("/health")
def health_check():
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "scraper_base_url": settings.scraper_base_url,
        "allowed_domain": settings.scraper_allowed_domain,
    }
