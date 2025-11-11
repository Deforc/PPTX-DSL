from __future__ import annotations

from fastapi import APIRouter

from backend.app.core.config import get_settings

router = APIRouter()


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
