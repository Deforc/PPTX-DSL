import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import get_settings
from backend.app.core.logging import setup_logging
from backend.app.v1.routers import router

def create_app() -> FastAPI:
    s = get_settings()
    setup_logging()

    app = FastAPI(
        title=s.APP_NAME,
        version=s.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Гарантируем наличие директории загрузок
    upload_dir: Path = s.upload_path
    os.makedirs(upload_dir, exist_ok=True)

    # Роуты v1
    app.include_router(router, prefix=s.API_V1_PREFIX)
    return app

app = create_app()
