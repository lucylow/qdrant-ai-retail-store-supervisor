from __future__ import annotations

import logging

from app.metrics import compute_conversion_rate, compute_episode_reuse_rate


logger = logging.getLogger(__name__)


def main() -> None:
    # AUTONOMOUS-AGENT-HACKATHON: quick metrics snapshot for judges.
    reuse = compute_episode_reuse_rate()
    conv = compute_conversion_rate()
    logger.info(
        "Benchmark metrics",
        extra={
            "event": "benchmark.metrics",
            "episode_reuse_rate": reuse,
            "conversion_rate": conv,
        },
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

