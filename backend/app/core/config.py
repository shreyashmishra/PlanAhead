from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(
        default="mysql+pymysql://root:password@localhost:3306/degree_tracker",
        alias="DATABASE_URL",
    )
    graphql_path: str = "/graphql"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    next_public_app_url: str = Field(
        default="http://localhost:3000",
        alias="NEXT_PUBLIC_APP_URL",
    )
    next_public_graphql_api_url: str = Field(
        default="http://localhost:8000/graphql",
        alias="NEXT_PUBLIC_GRAPHQL_API_URL",
    )

    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", REPO_ROOT / ".env.local", Path(".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
