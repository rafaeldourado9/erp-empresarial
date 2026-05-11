from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: str = "development"
    app_secret_key: str = "dev-secret-change-in-prod"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://erp:erp_dev_secret@localhost:5432/erp_empresarial"
    database_url_sync: str = "postgresql+psycopg2://erp:erp_dev_secret@localhost:5432/erp_empresarial"

    redis_url: str = "redis://localhost:6379/0"

    jwt_private_key_path: str = "keys/private.pem"
    jwt_public_key_path: str = "keys/public.pem"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "ERP Empresarial"
    smtp_from_email: str = ""
    smtp_enabled: bool = False
    app_url: str = "http://localhost"

    def get_private_key(self) -> str:
        return Path(self.jwt_private_key_path).read_text()

    def get_public_key(self) -> str:
        return Path(self.jwt_public_key_path).read_text()


@lru_cache
def get_settings() -> Settings:
    return Settings()
