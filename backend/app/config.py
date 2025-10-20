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
    # Path Configuration
    ROOT_PATH: Path = Path(__file__).parent.parent.parent
    FRONTEND_PATH: Path = ROOT_PATH / "frontend"
    BACKEND_PATH: Path = ROOT_PATH / "backend"
    PROJECT_PATH: Path = BACKEND_PATH / "app"

    # Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "FindMyGap")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    DESCRIPTION: str = os.getenv("DESCRIPTION", "A FastAPI + Next.js AI agent application")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LVL: str = os.getenv("LOG_LVL", "DEBUG")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    ENV_STATE: str = os.getenv("ENV_STATE", "LOCAL").upper()

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "True") == "True"
    WORKERS: int = int(os.getenv("WORKERS", "1"))

    # CORS Origins
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "[http://localhost:3000,http://127.0.0.1:3000]")

    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Clerk Authentication
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: str = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "")
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")

    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "anthropic/claude-4.5-sonnet")

    # Vector DB Configuration
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")

    # Search
    BRAVE_SEARCH_API_KEY: str = os.getenv("BRAVE_SEARCH_API_KEY", "")

    # Apify Configuration (Web Scraping)
    APIFY_API_TOKEN: str = os.getenv("APIFY_API_TOKEN", "")
    APIFY_REDDIT_ACTOR_ID: str = os.getenv("APIFY_REDDIT_ACTOR_ID", "trudax/reddit-scraper")
    APIFY_TWITTER_ACTOR_ID: str = os.getenv("APIFY_TWITTER_ACTOR_ID", "apidojo/tweet-scraper")

    # Review Scraping Costs
    REDDIT_REVIEW_COST: float = float(os.getenv("REDDIT_REVIEW_COST", "0.01"))
    TWITTER_REVIEW_COST: float = float(os.getenv("TWITTER_REVIEW_COST", "0.01"))
    CSV_REVIEW_COST: float = float(os.getenv("CSV_REVIEW_COST", "0.00"))

    # Stripe Configuration (Payments)
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_CURRENCY: str = os.getenv("STRIPE_CURRENCY", "usd")

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/findmygap")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "postgres")
    DATABASE_USERNAME: str = os.getenv("DATABASE_USERNAME", "postgres")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "findmygap")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "100"))
    REDIS_SOCKET_TIMEOUT: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))

    # Sentry
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


SETTINGS = get_settings()
