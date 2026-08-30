import logging
from contextvars import ContextVar, Token
from typing import Any

from pythonjsonlogger.json import JsonFormatter

correlation_id_context: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_context.get()
        return True


def configure_logging(
    level: str,
    *,
    service: str,
    environment: str,
    version: str,
) -> None:
    """Configure structured logs for local and hosted environments."""
    handler = logging.StreamHandler()
    handler.setFormatter(
        JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(correlation_id)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"},
            static_fields={
                "service": service,
                "environment": environment,
                "version": version,
            },
        )
    )
    handler.addFilter(ContextFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


def bind_correlation_id(value: str) -> Token[str | None]:
    return correlation_id_context.set(value)


def reset_correlation_id(token: Token[str | None]) -> None:
    correlation_id_context.reset(token)


def get_logger(name: str, **context: Any) -> logging.LoggerAdapter[logging.Logger]:
    return logging.LoggerAdapter(logging.getLogger(name), context)
