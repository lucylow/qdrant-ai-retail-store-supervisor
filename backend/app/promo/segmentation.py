from __future__ import annotations

from dataclasses import dataclass
from typing import List, Mapping, Sequence


@dataclass(slots=True)
class Customer:
    customer_id: str
    monetary: float
    frequency: int
    recency_days: int
    features: Mapping[str, float]


@dataclass(slots=True)
class Segment:
    name: str
    customers: List[Customer]


class Segmenter:
    """
    Very small RFM segmenter.
    """

    def cluster(self, customers: List[Customer]) -> List[Segment]:
        vip = [c for c in customers if c.monetary > 200 and c.frequency > 3]
        regular = [c for c in customers if c not in vip]
        segments: List[Segment] = []
        if vip:
            segments.append(Segment(name="VIP", customers=vip))
        if regular:
            segments.append(Segment(name="Regular", customers=regular))
        return segments


__all__: Sequence[str] = ["Customer", "Segment", "Segmenter"]

