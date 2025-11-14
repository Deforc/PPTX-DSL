from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Presentation Lint API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "development"

    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "https://pptx-dsl.vercel.app"]

    UPLOAD_DIR: str = "storage/uploads"
    MAX_PDF_MB: int = 25
    MAX_RULES_MB: int = 2
    REQUEST_BODY_LIMIT_MB: int = 30
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors(cls, v):
        if isinstance(v, str):
            parts = [p.strip() for p in v.split(",") if p.strip()]
            return parts or ["http://localhost:5173"]
        return v

    @property
    def request_body_limit_bytes(self) -> int:
        return int(self.REQUEST_BODY_LIMIT_MB) * 1024 * 1024

    @property
    def upload_path(self) -> Path:
        return Path(self.UPLOAD_DIR).resolve()

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
