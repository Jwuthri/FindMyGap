import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from app import get_logger

logger = get_logger("config")

os.environ["TZ"] = os.getenv("TZ", "UTC")
load_dotenv()


class Settings(BaseSettings):
    ROOT_PATH: Path = Path(__file__).parent.parent.parent
    FRONTEND_PATH: Path = ROOT_PATH / "frontend"
    BACKEND_PATH: Path = ROOT_PATH / "backend"
    PROJECT_PATH: Path = BACKEND_PATH / "app"

    ENV_STATE: str = os.getenv("ENV_STATE", "LOCAL").upper()
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    LOG_LVL: str = os.getenv("LOG_LVL", "DEBUG")

    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/findmygap")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "findmygap")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "postgres")
    DATABASE_USERNAME: str = os.getenv("DATABASE_USERNAME", "postgres")

    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


logger.info(f"Settings: {get_settings()}")
