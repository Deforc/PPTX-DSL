from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, FileResponse

from app.core.config import get_settings
from typing import List, Optional
import os
import json
from app.domain.entities import Slide

from app.v1.endpoints.validate import router as validation_router

router = APIRouter()

router.include_router(validation_router)

@router.get("/healthz", summary="Проверка на то, насколько жив сервис")
def heallthz() -> dict:
    return {"status": "ok"}

@router.get("/version", summary="Версия и окружение")
def version() -> dict:
    s = get_settings()
    return {
        "name": s.APP_NAME,
        "version": s.APP_VERSION,
        "env": s.ENV,
    }
