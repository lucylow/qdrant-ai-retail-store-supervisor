"""
Retail-specific context utilities.

This package contains lightweight helpers that sit on top of the existing
agentic RAG stack in `app.context_manager` and friends. They are intentionally
simple so they can be composed freely inside agents and demo scripts.
"""

from .retail_context_builder import RetailContextBuilder

__all__ = ["RetailContextBuilder"]

