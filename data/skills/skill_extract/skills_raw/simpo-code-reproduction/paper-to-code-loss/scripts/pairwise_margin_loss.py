#!/usr/bin/env python3
"""Reusable utilities for pairwise margin losses (sigmoid and hinge).

This module helps implement and validate pairwise preference losses that use
average log-probabilities, a scaling factor beta, and a target margin gamma.

Functions are framework-agnostic and depend only on PyTorch.

Example:
    import torch
    from pairwise_margin_loss import (
        logits_from_avg_logps, sigmoid_loss_with_smoothing, hinge_loss
    )

    avg_chosen = torch.tensor([ -1.2, -0.8 ])
    avg_rejected = torch.tensor([ -1.5, -1.1 ])
    beta = 2.0
    gamma_beta_ratio = 0.25
    gamma = beta * gamma_beta_ratio

    logits, r_w, r_l = logits_from_avg_logps(avg_chosen, avg_rejected, beta, gamma)
    losses = sigmoid_loss_with_smoothing(logits, label_smoothing=0.0)
    print(losses)
"""

from __future__ import annotations
import torch
import torch.nn.functional as F
from typing import Tuple


def logits_from_avg_logps(
    avg_chosen_logps: torch.Tensor,
    avg_rejected_logps: torch.Tensor,
    beta: float,
    gamma: float,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Compute logits and rewards from average log-probabilities.

    Args:
        avg_chosen_logps: Per-example average log p(y_w|x), shape (batch,)
        avg_rejected_logps: Per-example average log p(y_l|x), shape (batch,)
        beta: Scaling factor for rewards
        gamma: Target margin to subtract from (r_w - r_l)

    Returns:
        logits: r_w - r_l - gamma
        chosen_rewards: beta * avg_chosen_logps
        rejected_rewards: beta * avg_rejected_logps
    """
    if avg_chosen_logps.shape != avg_rejected_logps.shape:
        raise ValueError("avg_chosen_logps and avg_rejected_logps must have the same shape")

    chosen_rewards = beta * avg_chosen_logps
    rejected_rewards = beta * avg_rejected_logps
    logits = chosen_rewards - rejected_rewards - gamma
    return logits, chosen_rewards, rejected_rewards


def sigmoid_loss_with_smoothing(
    logits: torch.Tensor,
    label_smoothing: float = 0.0,
) -> torch.Tensor:
    """Compute -log(sigmoid(logits)) with optional label smoothing.

    L = -(1-eps) * log(sigma(logits)) - eps * log(sigma(-logits))

    Args:
        logits: Pairwise logits, shape (batch,)
        label_smoothing: epsilon in [0, 0.5]. Only applies to sigmoid loss.

    Returns:
        Per-example losses, shape (batch,)
    """
    if label_smoothing == 0.0:
        return -F.logsigmoid(logits)
    if not (0.0 <= label_smoothing <= 0.5):
        raise ValueError("label_smoothing should be in [0, 0.5]")
    return (
        -F.logsigmoid(logits) * (1.0 - label_smoothing)
        - F.logsigmoid(-logits) * label_smoothing
    )


def hinge_loss(logits: torch.Tensor, margin: float = 1.0) -> torch.Tensor:
    """Compute hinge loss: max(0, margin - logits).

    Args:
        logits: Pairwise logits, shape (batch,)
        margin: Hinge margin threshold

    Returns:
        Per-example losses, shape (batch,)
    """
    return torch.relu(margin - logits)
