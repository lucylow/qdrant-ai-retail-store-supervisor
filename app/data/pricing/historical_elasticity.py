"""Historical demand elasticity curves for pricing models."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


def load_historical_elasticity(
    path: Optional[Path] = None,
) -> Dict[str, List[float]]:
    """Load historical elasticity by category/SKU (demo: synthetic)."""
    if path and path.exists():
        try:
            data = np.load(path, allow_pickle=True)
            return dict(data.get("elasticity", {}))
        except Exception as e:
            logger.warning("Could not load historical elasticity from %s: %s", path, e)
    return {
        "tshirt": [-1.8, -1.6, -1.9],
        "jeans": [-1.4, -1.5, -1.3],
        "dress": [-2.0, -1.7, -1.8],
        "default": [-1.5],
    }
