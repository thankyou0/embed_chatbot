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

    # GROQ Models
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


# ── GROQ API Key Rotation (circuit-breaker + rate-limit rotation) ──
class _GroqKeyRotator:
    """Thread-safe Groq API key rotator with circuit-breaker and rate-limit rotation.

    - Permanently exhausted keys (402 / credits gone) are blacklisted forever.
    - Rate-limited keys (429) are rotated to end of queue and recover after cooldown.
    """

    _RATE_LIMIT_COOLDOWN = 60  # seconds before a rate-limited key is retried

    def __init__(self):
        import time as _time
        self._lock = threading.Lock()
        keys: list[str] = []
        if settings.GROQ_API_KEYS:
            keys = [k.strip() for k in settings.GROQ_API_KEYS.split(",") if k.strip()]
        if not keys and settings.GROQ_API_KEY:
            keys = [settings.GROQ_API_KEY]
        self._all_keys = keys
        self._dead_keys: set[str] = set()
        self._rate_limited: dict[str, float] = {}  # key -> timestamp
        self._index = 0
        self._count = len(keys)

    def _alive_sorted(self) -> list[str]:
        """Return alive keys: fresh first, then rate-limited (oldest first). Lock must be held."""
        import time
        now = time.time()
        alive = [k for k in self._all_keys if k not in self._dead_keys]
        fresh = []
        limited = []
        for k in alive:
            rl_time = self._rate_limited.get(k)
            if rl_time and (now - rl_time) < self._RATE_LIMIT_COOLDOWN:
                limited.append((k, rl_time))
            else:
                if k in self._rate_limited:
                    del self._rate_limited[k]
                fresh.append(k)
        limited.sort(key=lambda x: x[1])  # oldest rate-limit first
        return fresh + [k for k, _ in limited]

    def next_key(self) -> Optional[str]:
        """Return the next alive Groq API key (fresh keys first, rate-limited last)."""
        with self._lock:
            alive = self._alive_sorted()
            if not alive:
                return settings.GROQ_API_KEY  # last-resort fallback
            key = alive[self._index % len(alive)]
            self._index = (self._index + 1) % len(alive)
            return key

    def active_keys(self) -> list[str]:
        """Return a snapshot of all currently alive keys (fresh first, rate-limited last)."""
        with self._lock:
            return list(self._alive_sorted())

    def mark_exhausted(self, key: str) -> None:
        """Permanently blacklist *key* (credits gone / 402)."""
        if not key:
            return
        with self._lock:
            if key not in self._dead_keys:
                self._dead_keys.add(key)
                self._rate_limited.pop(key, None)
                key_hint = f"...{key[-8:]}" if len(key) > 8 else key
                remaining = len([k for k in self._all_keys if k not in self._dead_keys])
                logger.warning(
                    f"\u26a0\ufe0f  Groq API key [{key_hint}] permanently exhausted "
                    f"\u2014 blacklisted. {remaining} key(s) remaining."
                )
                if remaining == 0:
                    logger.error(
                        "\U0001f534 ALL Groq API keys exhausted! "
                        "Please add/refresh keys and restart the server."
                    )

    def mark_rate_limited(self, key: str) -> None:
        """Rotate rate-limited key to end of queue (429). Recovers after cooldown."""
        import time
        if not key:
            return
        with self._lock:
            self._rate_limited[key] = time.time()
            key_hint = f"...{key[-8:]}" if len(key) > 8 else key
            fresh = [k for k in self._all_keys if k not in self._dead_keys and k not in self._rate_limited]
            logger.warning(
                f"\u26a0\ufe0f  Groq key [{key_hint}] rate-limited \u2014 rotated to end. "
                f"{len(fresh)} fresh key(s), "
                f"{len(self._rate_limited)} cooling down."
            )

    def all_exhausted_or_limited(self) -> bool:
        """True if ALL alive keys are currently dead or rate-limited (no fresh ones)."""
        import time
        now = time.time()
        with self._lock:
            alive = [k for k in self._all_keys if k not in self._dead_keys]
            if not alive:
                return True
            for k in alive:
                rl_time = self._rate_limited.get(k)
                if not rl_time or (now - rl_time) >= self._RATE_LIMIT_COOLDOWN:
                    return False
            return True

    @property
    def key_count(self) -> int:
        return self._count


_groq_rotator = _GroqKeyRotator()


def get_groq_api_key() -> Optional[str]:
    """Get the next GROQ API key (round-robin if multiple configured)."""
    return _groq_rotator.next_key()


def get_groq_key_count() -> int:
    """Return the total number of configured Groq API keys (including exhausted)."""
    return _groq_rotator.key_count


def get_groq_active_keys() -> list[str]:
    """Return all currently alive (non-exhausted) Groq API keys."""
    return _groq_rotator.active_keys()


def mark_groq_key_exhausted(key: str) -> None:
    """Permanently blacklist a Groq key for this process session."""
    _groq_rotator.mark_exhausted(key)


def mark_groq_key_rate_limited(key: str) -> None:
    """Rotate a Groq key to end of queue (429 rate limit)."""
    _groq_rotator.mark_rate_limited(key)
