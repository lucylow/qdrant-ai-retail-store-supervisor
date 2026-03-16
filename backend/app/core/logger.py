"""Structured JSON logging with rotation and Prometheus-ready context."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from app.core.config import get_settings


class StructuredFormatter(logging.Formatter):
    """Format log records as single-line JSON for log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "trace_id"):
            log_obj["trace_id"] = str(record.trace_id)
        if hasattr(record, "agent"):
            log_obj["agent"] = record.agent
        if hasattr(record, "step"):
            log_obj["step"] = record.step
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        # Merge any extra passed via extra={}
        for k, v in record.__dict__.items():
            if k not in (
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message", "taskName", "timestamp", "level", "logger",
            ) and v is not None:
                log_obj[k] = v
        return json.dumps(log_obj, default=str)


def _configure_root(log_level: str) -> None:
    """Configure root logger with structured JSON to stdout."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        root.addHandler(handler)


class StructuredLogger:
    """Logger wrapper that adds structured fields (agent, step, duration, trace_id)."""

    def __init__(self, name: str, trace_id: str | None = None) -> None:
        self._logger = logging.getLogger(name)
        self.trace_id = trace_id

    def _log(
        self,
        level: int,
        event: str,
        message: str,
        **extra: Any,
    ) -> None:
        merged = {"event": event, **extra}
        if self.trace_id is not None:
            merged["trace_id"] = self.trace_id
        self._logger.log(level, message, extra=merged)

    def info(self, event: str, message: str = "", **extra: Any) -> None:
        """Log info with structured extra fields."""
        self._log(logging.INFO, event, message or event, **extra)

    def warning(self, event: str, message: str = "", **extra: Any) -> None:
        """Log warning with structured extra fields."""
        self._log(logging.WARNING, event, message or event, **extra)

    def error(self, event: str, message: str = "", **extra: Any) -> None:
        """Log error with structured extra fields."""
        self._log(logging.ERROR, event, message or event, **extra)

    def debug(self, event: str, message: str = "", **extra: Any) -> None:
        """Log debug with structured extra fields."""
        self._log(logging.DEBUG, event, message or event, **extra)

    def agent_step(
        self,
        agent_name: str,
        step: str,
        input_data: dict[str, Any],
        duration_ms: float,
        event: str = "agent_step_completed",
    ) -> None:
        """Emit agent step metric (Prometheus-ready)."""
        self._log(
            logging.INFO,
            event,
            "",
            agent=agent_name,
            step=step,
            input_size=len(input_data),
            duration_ms=round(duration_ms, 2),
        )


def get_logger(name: str, trace_id: str | None = None) -> StructuredLogger:
    """Return a structured logger; call configure_logging() at app startup."""
    settings = get_settings()
    _configure_root(settings.log_level)
    return StructuredLogger(name, trace_id)
