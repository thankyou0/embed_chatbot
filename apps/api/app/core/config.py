from pydantic_settings import BaseSettings
from typing import List, Union, Optional
from pydantic import field_validator
from pathlib import Path
import json
import os


def get_env_file_path() -> Optional[str]:
    """
    Determine the correct .env file path based on environment.

    Priority:
    1. /app/.env (Docker container)
    2. Project root .env (local development)
    3. None (rely on environment variables only - production)
    """
    # Docker container path
    docker_env = Path("/app/.env")
    if docker_env.exists() and docker_env.is_file():
        return str(docker_env)

    # Local development: project root (embed_chatbot/.env)
    # Path: config.py -> core -> app -> api -> apps -> embed_chatbot
    try:
        project_root_env = Path(__file__).resolve().parents[4] / ".env"
        if project_root_env.exists() and project_root_env.is_file():
            return str(project_root_env)
    except IndexError:
        pass

    # Fallback: relative path (for running from apps/api directory)
    try:
        local_env = Path(__file__).resolve().parents[2] / ".env"
        if local_env.exists() and local_env.is_file():
            return str(local_env)
    except IndexError:
        pass

    # No .env file found - rely on environment variables
    return None


# Get the appropriate .env file path
ENV_FILE_PATH = get_env_file_path()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:post@localhost:5432/embed_chatbot"

    # API
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 150
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3005",  # Test site
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3005",  # Test site
    ]

    # LLM
    GROQ_API_KEY: Optional[str] = None
    
    # HuggingFace API for Embeddings
    # Primary: HF_API_KEY (preferred name)
    # Also supports HUGGINGFACE_API_KEY for backward compatibility
    HF_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    @property
    def huggingface_api_key(self) -> Optional[str]:
        """Get HuggingFace API key, checking HF_API_KEY first, then HUGGINGFACE_API_KEY."""
        return self.HF_API_KEY or self.HUGGINGFACE_API_KEY

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Try to parse as JSON first
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, try comma-separated
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    class Config:
        env_file = ENV_FILE_PATH
        case_sensitive = True
        # Allow environment variables to override .env file
        env_file_encoding = 'utf-8'


settings = Settings()
