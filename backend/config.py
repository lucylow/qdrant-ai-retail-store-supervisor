import os
from typing import Optional

from openai import OpenAI

# OpenAI Configuration
# Note: In Manus, OPENAI_API_KEY is pre-configured.
client = OpenAI()

# Logging / runtime configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Qdrant Configuration
# Default to in-memory for the hackathon prototype, but allow overrides.
QDRANT_URL = os.getenv("QDRANT_URL") or None
QDRANT_PATH = os.getenv("QDRANT_PATH", ":memory:")
QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")

COLLECTION_GOALS = "goals"
COLLECTION_SOLUTIONS = "solutions"
COLLECTION_EPISODES = "episodes"
COLLECTION_PROMOTIONS = "promotions"

# Embedding / LLM models
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
