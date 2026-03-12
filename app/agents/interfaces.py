"""
Utilities for agent implementers: decorators for safe execution, retry helpers, and timing.
"""

from typing import Callable, Any
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def timed(fn: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(fn)
    def _wrap(*args, **kwargs):
        t0 = time.time()
        try:
            res = fn(*args, **kwargs)
            duration = time.time() - t0
            if isinstance(res, dict):
                res.setdefault("duration_s", duration)
            return res
        except Exception as e:
            logger.exception("Exception in timed wrapper: %s", e)
            duration = time.time() - t0
            return {"status": "failed", "error": str(e), "duration_s": duration}

    return _wrap


def safe_execute(fn):
    """
    Decorator to catch exceptions and return standardized AgentResult dict.
    Expects the wrapped function to return a dict or raise.
    """

    @wraps(fn)
    def wrapped(self, context):
        try:
            res = fn(self, context)
            return {
                "agent": getattr(self, "name", self.__class__.__name__),
                "status": "ok",
                "result": res,
            }
        except Exception as e:
            logger.exception(
                "Agent %s failed: %s",
                getattr(self, "name", self.__class__.__name__),
                e,
            )
            return {
                "agent": getattr(self, "name", self.__class__.__name__),
                "status": "failed",
                "error": str(e),
            }

    return wrapped

