from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "AI Recommendation System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite+aiosqlite:///./recommendation_db.db"
    DATABASE_URL_SYNC: str = "sqlite:///./recommendation_db.db"

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL: int = 3600

    SECRET_KEY: str = "your-secret-key-change-in-production-very-long-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ML_MODEL_DIR: str = "./ml/saved_models"
    ML_DATA_DIR: str = "./ml/data"

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    ADMIN_EMAIL: str = "admin@recommendation.ai"
    ADMIN_PASSWORD: str = "admin123"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
