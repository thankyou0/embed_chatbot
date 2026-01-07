from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator
import json
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:post@localhost:5432/embed_chatbot"
    
    # API
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    
    # JWT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 150
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
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
        env_file = ".env"
        case_sensitive = True


settings = Settings()

