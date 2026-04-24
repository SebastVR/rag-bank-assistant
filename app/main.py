from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

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


# -------------------------------------------------------------------
# 🔧 Helpers para error handling
# -------------------------------------------------------------------
_CODE_MAP = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    408: "REQUEST_TIMEOUT",
    409: "CONFLICT",
    422: "UNPROCESSABLE_ENTITY",
    429: "TOO_MANY_REQUESTS",
    500: "INTERNAL_SERVER_ERROR",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
    504: "GATEWAY_TIMEOUT",
}


def _msg_for(code: int) -> str:
    return _CODE_MAP.get(code, "ERROR")


def _safe_detail(detail) -> str:
    try:
        return detail if isinstance(detail, str) else str(detail)
    except Exception:
        return "Error"


def _error_payload(code: int, detail: str, request: Request) -> dict:
    return {
        "message": _msg_for(code),
        "detail": _safe_detail(detail),
        "status_code": code,
    }


# -------------------------------------------------------------------
# ❗ Handlers globales de errores
# -------------------------------------------------------------------


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=_error_payload(400, exc.errors(), request),
    )


@api.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = exc.status_code
    defaults = {
        404: f"Route '{request.url.path}' not found.",
        405: f"Method '{request.method}' not allowed for '{request.url.path}'.",
        401: "Authentication required.",
        403: "You do not have permission to access this resource.",
    }
    detail = exc.detail or defaults.get(code, "Request error.")
    return JSONResponse(status_code=code, content=_error_payload(code, detail, request))


@api.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=_error_payload(500, str(exc), request),
    )
