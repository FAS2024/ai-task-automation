from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_file() -> str | None:
    value = os.getenv("ENV_FILE", ".env")
    if value.strip().lower() in {"", "none", "null"}:
        return None
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_file(), env_file_encoding="utf-8")

    app_name: str = "AI Task Automation Platform"
    environment: str = "local"
    log_level: str = "INFO"
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")
    api_v1_prefix: str = "/api/v1"

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4o-mini"

    celery_broker_url: Optional[str] = Field(default=None, alias="CELERY_BROKER_URL")
    celery_result_backend: Optional[str] = Field(default=None, alias="CELERY_RESULT_BACKEND")
    celery_eager: bool = Field(default=True, alias="CELERY_EAGER")

    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    event_channel: str = "task_updates"

    database_url: str = Field(
        default="postgresql+psycopg2://app:app@localhost:5432/automation",
        alias="DATABASE_URL",
    )

    initial_admin_email: Optional[str] = Field(default=None, alias="INITIAL_ADMIN_EMAIL")
    initial_admin_password: Optional[str] = Field(default=None, alias="INITIAL_ADMIN_PASSWORD")

    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expires_minutes: int = Field(default=60, alias="JWT_EXPIRES_MINUTES")

    otlp_endpoint: Optional[str] = Field(default=None, alias="OTLP_ENDPOINT")


@lru_cache
def get_settings() -> Settings:
    return Settings()
