import torch
import torch.nn as nn


class PolicyNetwork(nn.Module):
    """
    Simple MLP policy over a 128-dim state embedding.

    Output logits correspond to a discrete action space of size 10, which
    you can map to:
    - retrieval strategies
    - context selection schemas
    - tool choices
    - reasoning modes
    """

    def __init__(self, state_dim: int = 128, action_dim: int = 10) -> None:
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

