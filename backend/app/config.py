import os
import logging
from functools import lru_cache

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL")


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
