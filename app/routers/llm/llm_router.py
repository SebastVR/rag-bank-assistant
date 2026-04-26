from __future__ import annotations

import os
from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.controllers.llm.model_management_controller import (
    activate_llm_model,
    activate_llm_model_by_id,
    list_llm_model_options,
    upload_llm_model,
)
from app.db.db_connection import get_db
from app.schemas.llm import ActivateModelByIdRequest, ActivateModelRequest
from app.services.llm.runtime_config_service import get_runtime_llm_config

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])


@router.post("/models/upload")
async def upload_model(
    file: UploadFile = File(...),
    provider: str = Form(default="llama_cpp"),
    model_name: str | None = Form(default=None),
    input_token_cost: float = Form(default=2.5),
    output_token_cost: float = Form(default=5.0),
    set_as_active: bool = Form(default=True),
    db=Depends(get_db),
):
    try:
        normalized_provider = provider.strip().lower()
        if normalized_provider != "llama_cpp":
            raise HTTPException(
                status_code=400,
                detail="/models/upload solo soporta provider=llama_cpp (.gguf)",
            )

        if not file.filename:
            raise HTTPException(status_code=400, detail="filename es requerido")

        ext = os.path.splitext(file.filename)[1].lower()
        if ext != ".gguf":
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten archivos .gguf",
            )

        binary = await file.read()
        if not binary:
            raise HTTPException(status_code=400, detail="Archivo vacio")

        resolved_model_name = model_name or os.path.splitext(file.filename)[0]
        result = upload_llm_model(
            db=db,
            file_name=file.filename,
            file_bytes=binary,
            provider=normalized_provider,
            model_name=resolved_model_name.strip(),
            input_token_cost=Decimal(str(input_token_cost)),
            output_token_cost=Decimal(str(output_token_cost)),
            set_as_active=set_as_active,
        )
        return {
            "message": "Model uploaded successfully",
            **result,
        }
    except HTTPException:
        raise
    except TypeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/active")
def get_active_model(db=Depends(get_db)):
    try:
        return get_runtime_llm_config(db)
    except TypeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/options")
def get_model_options(provider: str | None = None, db=Depends(get_db)):
    try:
        runtime = get_runtime_llm_config(db)
        options = list_llm_model_options(db=db, provider=provider)
        options["active"] = {
            "provider": runtime.get("llm_provider"),
            "model_name": runtime.get("llm_model_name"),
            "model_path": runtime.get("llm_model_path"),
        }
        return options
    except TypeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/activate")
def activate_model(payload: ActivateModelRequest, db=Depends(get_db)):
    try:
        result = activate_llm_model(
            db=db,
            provider=payload.provider,
            model_name=payload.model_name,
            model_path=payload.model_path,
            set_as_active=payload.set_as_active,
        )
        return {
            "message": "Model activation processed",
            **result,
        }
    except TypeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/activate/by-id")
def activate_model_by_id(payload: ActivateModelByIdRequest, db=Depends(get_db)):
    try:
        result = activate_llm_model_by_id(
            db=db,
            language_model_id=payload.language_model_id,
            set_as_active=payload.set_as_active,
        )
        return {
            "message": "Model activation processed",
            **result,
        }
    except TypeError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
