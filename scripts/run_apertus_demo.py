#!/usr/bin/env python3
"""
Demo: Apertus-70B-2509 agentic flow with tool calling.

Shows the full pipeline:
  1. User query (multilingual)
  2. Language detection
  3. Apertus generates with tools
  4. Tool dispatch
  5. Apertus reasons over results
  6. Localised response

Usage:
    APERTUS_BACKEND=remote APERTUS_ENDPOINT=http://localhost:8000/v1 python -m scripts.run_apertus_demo
"""

from __future__ import annotations

import json
import sys

from app.llm.apertus_client import ApertusClient, ChatMessage, get_llm_client
from app.llm.tools import RETAIL_TOOLS, dispatch_tool_calls
from app.llm.multilingual import detect_language, build_multilingual_system_prompt


DEMO_QUERIES = [
    "Fondue-Set für 6 Personen, Genf, Freitag Lieferung",
    "Cherche un kit raclette pour 4 personnes, livraison à Lausanne",
    "Looking for organic milk delivery tomorrow in Zurich",
    "Cerco cioccolato svizzero per regalo, consegna a Lugano",
]


def run_demo(query: str) -> None:
    print(f"\n{'='*60}")
    print(f"  Query: {query}")
    print(f"{'='*60}")

    # 1. Detect language
    lang = detect_language(query)
    print(f"  Language: {lang}")

    # 2. Build system prompt
    system_prompt = build_multilingual_system_prompt("supervisor", lang)

    # 3. Call Apertus with tools
    client = get_llm_client()
    messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=query),
    ]

    print("  Calling Apertus with tools...")
    response = client.chat(messages, tools=RETAIL_TOOLS)
    print(f"  Finish reason: {response.finish_reason}")

    # 4. If tool calls, dispatch and continue
    if response.tool_calls:
        print(f"  Tool calls: {len(response.tool_calls)}")
        for tc in response.tool_calls:
            func = tc.get("function", tc)
            print(f"    → {func.get('name')}: {func.get('arguments', '')[:80]}")

        tool_results = dispatch_tool_calls(response.tool_calls)

        # Add assistant + tool results to conversation
        messages.append(ChatMessage(role="assistant", content=response.content, tool_calls=response.tool_calls))
        for tr in tool_results:
            messages.append(ChatMessage(
                role="tool",
                content=json.dumps(tr["result"]),
                tool_call_id=tr.get("tool_call_id", ""),
                name=tr.get("name", ""),
            ))

        # 5. Final reasoning
        print("  Apertus reasoning over tool results...")
        final = client.chat(messages)
        print(f"\n  Response ({lang}):\n  {final.content[:500]}")
    else:
        print(f"\n  Response ({lang}):\n  {response.content[:500]}")

    if response.usage:
        print(f"\n  Tokens: {response.usage}")


def main() -> None:
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

    if query:
        run_demo(query)
    else:
        for q in DEMO_QUERIES:
            run_demo(q)


if __name__ == "__main__":
    main()
