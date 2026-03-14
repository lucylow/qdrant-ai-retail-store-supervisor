from __future__ import annotations

from typing import Iterable, List, Tuple

from sentence_transformers import CrossEncoder, InputExample, losses
from torch.utils.data import DataLoader


def build_triplet_dataloader(
    triplets: Iterable[Tuple[str, str, str]],
    batch_size: int = 16,
) -> DataLoader:
    """
    Convert (query, positive, hard_negative) triplets into a simple pairwise
    training dataset for CrossEncoder.
    """
    examples: List[InputExample] = []
    for query, positive, hard_negative in triplets:
        # Positive pair (label 1.0)
        examples.append(InputExample(texts=[query, positive], label=1.0))
        # Hard negative pair (label 0.0)
        examples.append(InputExample(texts=[query, hard_negative], label=0.0))

    return DataLoader(examples, shuffle=True, batch_size=batch_size)


def fine_tune_cross_encoder(
    model_name: str,
    triplets: Iterable[Tuple[str, str, str]],
    epochs: int = 1,
    batch_size: int = 16,
    output_path: str | None = None,
) -> CrossEncoder:
    """
    Minimal fine‑tuning loop over mined hard‑negative triplets.
    """
    model = CrossEncoder(model_name)
    dataloader = build_triplet_dataloader(triplets, batch_size=batch_size)
    loss = losses.BinaryCrossEntropyLoss(model)

    model.fit(
        train_dataloader=dataloader,
        loss_fct=loss,
        epochs=epochs,
        warmup_steps=min(100, len(dataloader)),
        output_path=output_path,
        show_progress_bar=True,
    )
    return model


__all__ = ["build_triplet_dataloader", "fine_tune_cross_encoder"]

