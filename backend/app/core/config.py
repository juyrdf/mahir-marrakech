from typing import List
from pathlib import Path
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Marrakech Companion"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Auth / JWT
    SECRET_KEY: str = "marrakech-companion-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Secrets (Loaded from environment)
    DATABASE_URL: str | None = None
    OPENAI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    DEEPSEEK_API_KEY: str | None = None
    N8N_AI_AGENT_URL: str | None = None
    PINECONE_API_KEY: str | None = None
    PINECONE_ENVIRONMENT: str | None = "us-east1-gcp"
    PINECONE_INDEX_NAME: str | None = "mahir-pois"

    class Config:
        case_sensitive = True
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")
        extra = "ignore"

settings = Settings()
