"""
Pluggable LLM layer: Apertus-70B-2509 (default) / OpenAI / HF Inference.
"""

from app.llm.apertus_client import ApertusClient, get_llm_client

__all__ = ["ApertusClient", "get_llm_client"]
