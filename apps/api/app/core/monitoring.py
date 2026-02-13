"""
Centralized monitoring helpers for Sentry integration.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional

import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_sentry_initialized = False


def is_sentry_enabled() -> bool:
    return bool(settings.SENTRY_DSN)


def _to_primitive(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _before_send(event, hint):
    """
    Drop expected 4xx exceptions so Sentry focuses on operational failures.
    """
    exc_info = hint.get("exc_info") if hint else None
    if exc_info and len(exc_info) >= 2:
        exc = exc_info[1]
        status_code = getattr(exc, "status_code", None)
        if isinstance(status_code, int) and status_code < 500:
            return None
    return event


def init_sentry() -> None:
    global _sentry_initialized

    if _sentry_initialized:
        return

    _sentry_initialized = True
    if not is_sentry_enabled():
        logger.info("Sentry disabled: set SENTRY_DSN to enable external error tracking")
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
        before_send=_before_send,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            AsyncioIntegration(),
        ],
    )
    logger.success("Sentry error tracking enabled")


def capture_exception_with_context(
    exc: Exception,
    *,
    tags: Optional[Mapping[str, Any]] = None,
    context: Optional[Mapping[str, Any]] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    if not is_sentry_enabled():
        return

    with sentry_sdk.push_scope() as scope:
        for key, value in (tags or {}).items():
            if value is None:
                continue
            scope.set_tag(str(key), str(value))

        if context:
            scope.set_context(
                "app_context",
                {str(key): _to_primitive(value) for key, value in context.items()},
            )

        for key, value in (extra or {}).items():
            if value is None:
                continue
            scope.set_extra(str(key), _to_primitive(value))

        sentry_sdk.capture_exception(exc)

