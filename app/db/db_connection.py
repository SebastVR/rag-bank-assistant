from typing import Any, Generator

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config.settings import settings

Base = declarative_base()


POSTGRES_URL = (
    f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)

engine = create_engine(
    POSTGRES_URL,
    echo=settings.debug,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db_session() -> Generator[Session, None, None]:
    db = None
    try:
        db = SessionLocal()
        yield db
    except OperationalError:
        if db:
            db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Base de datos PostgreSQL no disponible",
        )
    finally:
        if db:
            db.close()


class SupabaseSingleton:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is not None:
            return cls._client

        try:
            from supabase import create_client
        except ImportError:
            raise RuntimeError(
                "El paquete 'supabase' no está instalado. Ejecuta: pip install supabase"
            )

        if not settings.supabase_url or not settings.supabase_service_key:
            raise RuntimeError(
                "SUPABASE_URL y SUPABASE_SERVICE_KEY deben estar configurados en producción."
            )

        cls._client = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )
        return cls._client


def get_db() -> Generator[Any, None, None]:
    """
    Dependencia principal para FastAPI.

    APP_ENV=dev  -> PostgreSQL local con SQLAlchemy
    APP_ENV=prod -> Supabase
    """

    env = settings.app_env.lower()

    if env == "dev":
        yield from get_db_session()

    elif env == "prod":
        yield SupabaseSingleton.get_client()

    else:
        raise RuntimeError(f"APP_ENV inválido: {settings.app_env}. Usa 'dev' o 'prod'.")
