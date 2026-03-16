from __future__ import annotations

from dataclasses import dataclass
from subprocess import CalledProcessError, run
from tempfile import NamedTemporaryFile
from textwrap import dedent
from typing import Any, Mapping

import json
import logging
import sys
import uuid

from app.agents.base import Agent


logger = logging.getLogger(__name__)


TOOL_TEMPLATE = """\
import json

def tool_main(payload: dict) -> dict:
    {body}

if __name__ == "__main__":
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw else {{}}
        out = tool_main(payload)
        print(json.dumps({{"ok": True, "result": out}}))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({{"ok": False, "error": str(exc)}}))
"""


def _write_and_run(code: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    with NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        proc = run(
            [sys.executable, path],
            input=json.dumps(dict(payload)),
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return json.loads(proc.stdout or "{}")
    except CalledProcessError as exc:
        logger.exception("Tool subprocess failed", exc_info=exc)
        return {"ok": False, "error": str(exc), "stdout": exc.stdout, "stderr": exc.stderr}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Tool execution failed", exc_info=exc)
        return {"ok": False, "error": str(exc)}


class ToolBuilderAgent(Agent):
    """
    Minimal LLM→Python tool generator + sandboxed exec.
    For the hackathon we assume the tool body is provided or synthesized upstream.
    """

    name = "tool_builder"

    def run(self, query: str, context: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        """
        Expects context to contain a "tool_body" (python code for tool_main payload logic)
        and optional "payload" dict to feed into the tool.
        """
        ctx = context or {}
        body = ctx.get("tool_body")
        if not isinstance(body, str):
            return {"ok": False, "error": "tool_body missing"}
        payload = ctx.get("payload") or {}
        code = TOOL_TEMPLATE.format(body=dedent(body))
        result = _write_and_run(code, payload)
        return {"tool_id": str(uuid.uuid4()), "query": query, "result": result}


__all__ = ["ToolBuilderAgent"]

