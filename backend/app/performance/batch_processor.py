"""
Dynamic batching and padding for GPU-efficient inference.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, TypeVar

T = TypeVar("T")
R = TypeVar("R")


@dataclass
class DynamicBatchConfig:
    max_batch_size: int = 128
    max_wait_s: float = 0.05
    padding_token_id: int = 0


class BatchProcessor:
    """Splits items into batches and runs processor; supports padding for GPU efficiency."""

    def __init__(
        self,
        processor: Callable[[List[T]], List[R]],
        config: DynamicBatchConfig | None = None,
    ) -> None:
        self.processor = processor
        self.config = config or DynamicBatchConfig()

    def process_batches(self, items: List[T]) -> List[R]:
        """Process all items in batches of max_batch_size."""
        results: List[R] = []
        for start in range(0, len(items), self.config.max_batch_size):
            batch = items[start : start + self.config.max_batch_size]
            results.extend(self.processor(batch))
        return results

    def pad_to_batch(self, items: List[T], pad_value: Any = None) -> List[T]:
        """Pad list to max_batch_size for GPU efficiency."""
        n = len(items)
        if n >= self.config.max_batch_size:
            return items[: self.config.max_batch_size]
        return items + [pad_value] * (self.config.max_batch_size - n)

    def _split_into_batches(self, items: List[T], size: int) -> List[List[T]]:
        batches: List[List[T]] = []
        for i in range(0, len(items), size):
            batches.append(items[i : i + size])
        return batches
