from fastapi import APIRouter, Depends

from app.db.db_connection import get_db

router = APIRouter(prefix="/api/v1/db", tags=["db"])


@router.get("/test-db")
def test_db(db=Depends(get_db)):
    return {
        "message": "Conexión cargada correctamente",
        "db_type": type(db).__name__,
    }
