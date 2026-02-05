from __future__ import annotations

from typing import Optional


_EMBEDDING_KEYWORDS = (
    "huggingface",
    "hf-inference",
    "sentence-transformers",
    "all-minilm",
)

_VISION_KEYWORDS = (
    "groq",
    "gemini",
)

_INTERNAL_KEYWORDS = (
    "traceback",
    "stack trace",
    "sqlalchemy",
    "asyncpg",
    "postgres",
    "supabase",
    "s3",
    "uvicorn",
    "fastapi",
    "pydantic",
)


def sanitize_error_message(
    message: Optional[str],
    *,
    fallback: str = "Something went wrong. Please try again.",
) -> str:
    if not message:
        return fallback

    text = str(message)
    lowered = text.lower()

    # Preserve quota/limit warnings as-is (user-facing by design)
    if "quota" in lowered or "limit" in lowered:
        return text

    if any(keyword in lowered for keyword in _EMBEDDING_KEYWORDS):
        if "timeout" in lowered or "timed out" in lowered or "504" in lowered:
            return "Embedding service timed out. Please try again in a few minutes."
        if "rate limit" in lowered or "too many requests" in lowered:
            return "Embedding service is busy. Please try again shortly."
        if "unauthorized" in lowered or "api key" in lowered or "authentication" in lowered:
            return "Embedding service is not configured. Please contact support."
        return "Embedding service is temporarily unavailable. Please try again shortly."

    if any(keyword in lowered for keyword in _VISION_KEYWORDS):
        return "Image analysis service is temporarily unavailable. Please try again."

    if any(keyword in lowered for keyword in _INTERNAL_KEYWORDS):
        return fallback

    return text
