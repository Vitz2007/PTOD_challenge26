from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """App settings, read from environment variables or `.env`."""

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")

    odpt_consumer_key: str
    odpt_base_url: str = "https://api-challenge.odpt.org/api/v4"
    odpt_timeout_seconds: float = 20

    # How long ODPT responses are reused before fetching again
    live_cache_seconds: int = 30  # trains, line status
    static_cache_seconds: int = 24 * 60 * 60  # station lists, passenger surveys

    # Frontend origins allowed to call the API (JSON list in env, e.g. '["https://example.com"]')
    cors_origins: list[str] = ["http://localhost:5173"]
    frontend_dist: Path = PROJECT_ROOT / "frontend" / "dist"


@lru_cache
def get_settings() -> Settings:
    return Settings()
