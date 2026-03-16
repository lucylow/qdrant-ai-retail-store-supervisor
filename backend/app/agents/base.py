from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from time import monotonic
from typing import Any, Callable, Dict, Mapping, Protocol

import json
import logging
import uuid


logger = logging.getLogger(__name__)


class Agent(Protocol):
    name: str

    def run(self, query: str, context: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        ...


def _log_agent_event(
    agent_name: str,
    status: str,
    duration_s: float,
    payload: Mapping[str, Any] | None = None,
) -> None:
    record = {
        "agent": agent_name,
        "status": status,
        "duration_s": round(duration_s, 3),
        "payload": payload or {},
        "event_id": str(uuid.uuid4()),
    }
    logger.info(json.dumps(record))


def timed_agent(fn: Callable[[str, Mapping[str, Any] | None], Mapping[str, Any]]) -> Callable[
    [str, Mapping[str, Any] | None], Mapping[str, Any]
]:
    def wrapper(query: str, context: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        start = monotonic()
        name = getattr(fn, "__name__", "agent")
        try:
            result = fn(query, context)
            _log_agent_event(name, "success", monotonic() - start)
            return result
        except Exception as exc:  # noqa: BLE001
            _log_agent_event(name, "error", monotonic() - start, {"error": str(exc)})
            raise

    return wrapper


@dataclass
class AgentResult:
    name: str
    ok: bool
    data: Mapping[str, Any]
    error: str | None = None


class ParallelAgentExecutor:
    """
    Small helper for running agents in parallel with a fixed thread pool.
    """

    def __init__(self, max_workers: int = 4) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, agent: Agent, query: str, context: Mapping[str, Any] | None = None) -> Future[AgentResult]:
        def _task() -> AgentResult:
            start = monotonic()
            try:
                res = agent.run(query, context)
                _log_agent_event(agent.name, "success", monotonic() - start)
                return AgentResult(name=agent.name, ok=True, data=res)
            except Exception as exc:  # noqa: BLE001
                _log_agent_event(
                    agent.name,
                    "error",
                    monotonic() - start,
                    {"error": str(exc)},
                )
                return AgentResult(
                    name=agent.name,
                    ok=False,
                    data={},
                    error=str(exc),
                )

        return self._executor.submit(_task)


__all__ = ["Agent", "AgentResult", "ParallelAgentExecutor", "timed_agent"]

from typing import TypedDict, Dict, Any, Protocol
import abc


class AgentResult(TypedDict, total=False):
    agent: str
    status: str
    result: Dict[str, Any]
    error: str
    duration_s: float
    provenance: Any


class Context(Dict[str, Any]):
    pass


class Agent(Protocol):
    name: str

    def run(self, context: Context) -> AgentResult:
        ...

