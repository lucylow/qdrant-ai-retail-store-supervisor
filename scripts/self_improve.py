from __future__ import annotations

import logging

from app.rag.self_improving import SelfImprovingRAG


logger = logging.getLogger(__name__)


def main() -> None:
    # AUTONOMOUS-AGENT-HACKATHON: daily self-improvement entrypoint.
    rag = SelfImprovingRAG()
    rag.daily_improvement_cycle()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

