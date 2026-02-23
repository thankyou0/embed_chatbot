from pydantic_settings import BaseSettings
from typing import List, Union, Optional
from pydantic import field_validator
from pathlib import Path
from app.core.logging import get_logger
import json
import os
import threading

logger = get_logger(__name__)


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
    # 4️⃣ If no .env found
    # Returns None, meaning:
    # 👉 Your app will rely only on system environment variables (typical for production servers).
    return None


# Get the appropriate .env file path
ENV_FILE_PATH = get_env_file_path()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:post@localhost:5432/embed_chatbot"
    )

    # API
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # Billing
    BILLING_MOCK_MODE: bool = True

    # JWT
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
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
    GROQ_API_KEYS: Optional[str] = None  # Comma-separated list for round-robin rotation
    DEEPSEEK_API_KEY: Optional[str] = None

    # OpenRouter API (alternative LLM provider — supports many models)
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_API_KEYS: Optional[str] = None  # Comma-separated list for round-robin rotation
    # Model for Call1 (classification/analysis) — fast, cheap
    OPENROUTER_CALL1_MODEL: str = "google/gemini-2.5-flash"
    # Model for Call2 (main response) — best quality, humanized
    OPENROUTER_CALL2_MODEL: str = "google/gemini-2.5-flash-lite"
    # Model for translation
    OPENROUTER_TRANSLATION_MODEL: str = "google/gemini-2.5-flash"

    # GROQ Models (Fallback)
    GROQ_CALL1_MODEL: str = "llama-3.1-8b-instant"
    GROQ_CALL2_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TRANSLATION_MODEL: str = "llama-3.3-70b-versatile"

    # Google Gemini API (free tier for vision)
    GEMINI_API_KEY: Optional[str] = None

    # Vision model provider: "groq" or "gemini"
    VISION_MODEL_PROVIDER: str = "gemini"

    # HuggingFace API for Embeddings
    # Primary: HF_API_KEY (preferred name)
    # Also supports HUGGINGFACE_API_KEY for backward compatibility
    HF_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = ""

    # Email configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False

    # Email settings
    EMAIL_FROM: Optional[str] = None
    EMAIL_FROM_NAME: str = "Chatbot Platform"
    FRONTEND_URL: str = "http://localhost:3000"
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # Redis (distributed rate limiting + query caching)
    REDIS_URL: Optional[str] = None  # e.g. redis://redis:6379/0

    # Sentry (error tracking)
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # S3 Compatible Storage (Supabase, DigitalOcean, etc.)
    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = (
        None  # e.g., https://[id].supabase.co/storage/v1/s3
    )
    S3_REGION: str = "us-east-1"  # Supabase uses us-east-1 for S3 compatibility
    S3_BUCKET_NAME: str = "chatbot-uploads"
    S3_PUBLIC_URL: Optional[str] = (
        None  # e.g., https://[id].supabase.co/storage/v1/object/public/[bucket]
    )

    @property
    def huggingface_api_key(self) -> Optional[str]:
        """Get HuggingFace API key, checking HF_API_KEY first, then HUGGINGFACE_API_KEY."""
        return self.HF_API_KEY or self.HUGGINGFACE_API_KEY

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Try to parse as JSON first
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, try comma-separated
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    class Config:
        env_file = ENV_FILE_PATH
        case_sensitive = True
        # Allow environment variables to override .env file
        env_file_encoding = "utf-8"


settings = Settings()


# ── GROQ API Key Rotation (circuit-breaker: permanently skip exhausted keys) ──
class _GroqKeyRotator:
    """Thread-safe Groq API key rotator with circuit-breaker for exhausted keys.

    Once a key is marked as exhausted (rate-limited / credits gone) it is
    permanently skipped for the lifetime of the process.  Restart the server
    to reset the circuit-breaker (or refill the key and restart).
    """

    def __init__(self):
        self._lock = threading.Lock()
        keys: list[str] = []
        if settings.GROQ_API_KEYS:
            keys = [k.strip() for k in settings.GROQ_API_KEYS.split(",") if k.strip()]
        if not keys and settings.GROQ_API_KEY:
            keys = [settings.GROQ_API_KEY]
        self._all_keys = keys
        self._dead_keys: set[str] = set()
        self._index = 0
        self._count = len(keys)

    def _alive(self) -> list[str]:
        """Return all keys that are NOT exhausted (call with lock held)."""
        return [k for k in self._all_keys if k not in self._dead_keys]

    def next_key(self) -> Optional[str]:
        """Return the next alive Groq API key, skipping any exhausted ones."""
        with self._lock:
            alive = self._alive()
            if not alive:
                return settings.GROQ_API_KEY  # last-resort fallback
            key = alive[self._index % len(alive)]
            self._index = (self._index + 1) % len(alive)
            return key

    def active_keys(self) -> list[str]:
        """Return a snapshot of all currently alive keys."""
        with self._lock:
            return list(self._alive())

    def mark_exhausted(self, key: str) -> None:
        """Permanently blacklist *key* for this process lifetime."""
        if not key:
            return
        with self._lock:
            if key not in self._dead_keys:
                self._dead_keys.add(key)
                key_hint = f"...{key[-8:]}" if len(key) > 8 else key
                remaining = len(self._alive())
                logger.warning(
                    f"\u26a0\ufe0f  Groq API key [{key_hint}] exhausted/rate-limited "
                    f"\u2014 permanently skipping this session. "
                    f"{remaining} key(s) remaining."
                )
                if remaining == 0:
                    logger.error(
                        "\U0001f534 ALL Groq API keys exhausted! "
                        "Please add/refresh keys and restart the server."
                    )

    @property
    def key_count(self) -> int:
        return self._count


_groq_rotator = _GroqKeyRotator()


def get_groq_api_key() -> Optional[str]:
    """Get the next GROQ API key (round-robin if multiple configured)."""
    return _groq_rotator.next_key()


# ── OpenRouter API Key Rotation (circuit-breaker: permanently skip exhausted keys) ──
class _OpenRouterKeyRotator:
    """Thread-safe OpenRouter API key rotator with circuit-breaker for exhausted keys.

    Once a key is marked as exhausted (HTTP 402, 429, or credits-gone error) it is
    permanently skipped for the lifetime of the process.  The operator will be
    notified via an ERROR log entry showing which key (last 8 chars) was dropped.
    Restart the server to reset the circuit-breaker after refilling credits.
    """

    def __init__(self):
        self._lock = threading.Lock()
        keys: list[str] = []
        if settings.OPENROUTER_API_KEYS:
            keys = [
                k.strip() for k in settings.OPENROUTER_API_KEYS.split(",") if k.strip()
            ]
        if not keys and settings.OPENROUTER_API_KEY:
            keys = [settings.OPENROUTER_API_KEY]
        self._all_keys = keys
        self._dead_keys: set[str] = set()
        self._index = 0
        self._count = len(keys)

    def _alive(self) -> list[str]:
        """Return all keys that are NOT exhausted (call with lock held)."""
        return [k for k in self._all_keys if k not in self._dead_keys]

    def next_key(self) -> Optional[str]:
        """Return the next alive OpenRouter API key, skipping exhausted ones."""
        with self._lock:
            alive = self._alive()
            if not alive:
                return settings.OPENROUTER_API_KEY  # last-resort fallback
            key = alive[self._index % len(alive)]
            self._index = (self._index + 1) % len(alive)
            return key

    def active_keys(self) -> list[str]:
        """Return a snapshot of all currently alive keys."""
        with self._lock:
            return list(self._alive())

    def mark_exhausted(self, key: str) -> None:
        """Permanently blacklist *key* for this process lifetime and log a prominent warning."""
        if not key:
            return
        with self._lock:
            if key not in self._dead_keys:
                self._dead_keys.add(key)
                key_hint = f"...{key[-8:]}" if len(key) > 8 else key
                remaining = len(self._alive())
                logger.warning(
                    f"\u26a0\ufe0f  OpenRouter API key [{key_hint}] exhausted/rate-limited "
                    f"\u2014 permanently skipping this session. "
                    f"{remaining} key(s) remaining."
                )
                if remaining == 0:
                    logger.error(
                        "\U0001f534 ALL OpenRouter API keys exhausted! "
                        "Please add/refresh keys and restart the server."
                    )

    @property
    def key_count(self) -> int:
        return self._count


_openrouter_rotator = _OpenRouterKeyRotator()


def get_openrouter_api_key() -> Optional[str]:
    """Get the next alive OpenRouter API key."""
    return _openrouter_rotator.next_key()


def get_openrouter_active_keys() -> list[str]:
    """Return all currently alive (non-exhausted) OpenRouter API keys."""
    return _openrouter_rotator.active_keys()


def mark_openrouter_key_exhausted(key: str) -> None:
    """Permanently blacklist an OpenRouter key for this process session."""
    _openrouter_rotator.mark_exhausted(key)


def get_openrouter_key_count() -> int:
    """Return the total number of configured OpenRouter API keys (including exhausted)."""
    return _openrouter_rotator.key_count


def get_groq_key_count() -> int:
    """Return the total number of configured Groq API keys (including exhausted)."""
    return _groq_rotator.key_count


def get_groq_active_keys() -> list[str]:
    """Return all currently alive (non-exhausted) Groq API keys."""
    return _groq_rotator.active_keys()


def mark_groq_key_exhausted(key: str) -> None:
    """Permanently blacklist a Groq key for this process session."""
    _groq_rotator.mark_exhausted(key)
