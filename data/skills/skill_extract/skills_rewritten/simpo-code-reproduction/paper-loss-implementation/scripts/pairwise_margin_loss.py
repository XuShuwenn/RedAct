#!/usr/bin/env python3
"""Utility for pairwise margin-based loss computations.

Implements a generic pairwise preference loss:
  - logits = beta * (chosen_logps - rejected_logps - gamma_ratio)
  - sigmoid loss with optional label smoothing
  - hinge loss

This script is dependency-light (uses numpy) and can be used to sanity-check
formulas before implementing them in a trainer with a deep learning framework.

Usage examples:
  python scripts/pairwise_margin_loss.py --chosen 0.2,0.0 --rejected -0.1,0.1 --beta 2.0 --gamma-ratio 0.5 --loss-type sigmoid --label-smoothing 0.1
  python scripts/pairwise_margin_loss.py --chosen 0.2,0.0 --rejected -0.1,0.1 --beta 2.0 --gamma-ratio 0.5 --loss-type hinge
"""

import argparse
import numpy as np
from typing import Tuple


def compute_logits(chosen_logps: np.ndarray, rejected_logps: np.ndarray, beta: float, gamma_ratio: float) -> np.ndarray:
    """Compute pairwise logits with margin and reward scaling.

    logits = beta * (chosen_logps - rejected_logps - gamma_ratio)
    """
    if chosen_logps.shape != rejected_logps.shape:
        raise ValueError("chosen_logps and rejected_logps must have the same shape")
    return beta * (chosen_logps - rejected_logps - gamma_ratio)


def softplus(x: np.ndarray) -> np.ndarray:
    # Stable softplus: log(1 + exp(x)); np.log1p(np.exp(x)) is OK for typical ranges.
    # For improved stability, split by sign.
    out = np.empty_like(x)
    pos = x >= 0
    neg = ~pos
    out[pos] = x[pos] + np.log1p(np.exp(-x[pos]))
    out[neg] = np.log1p(np.exp(x[neg]))
    return out


def sigmoid_loss(logits: np.ndarray, label_smoothing: float = 0.0) -> np.ndarray:
    """Sigmoid-style pairwise loss with optional label smoothing.

    Base: L = -log(sigmoid(logits)) = softplus(-logits)
    With smoothing s: L = (1-s)*softplus(-logits) + s*softplus(logits)
    """
    if not (0.0 <= label_smoothing <= 1.0):
        raise ValueError("label_smoothing must be in [0, 1]")
    base = softplus(-logits)
    if label_smoothing == 0.0:
        return base
    alt = softplus(logits)
    return (1.0 - label_smoothing) * base + label_smoothing * alt


def hinge_loss(logits: np.ndarray) -> np.ndarray:
    """Hinge-style pairwise loss: max(1 - logits, 0)."""
    return np.maximum(1.0 - logits, 0.0)


def compute_pairwise_loss(
    chosen_logps: np.ndarray,
    rejected_logps: np.ndarray,
    beta: float,
    gamma_ratio: float,
    loss_type: str = "sigmoid",
    label_smoothing: float = 0.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute losses and rewards for pairwise preference training.

    Returns (losses, chosen_rewards, rejected_rewards).
    """
    logits = compute_logits(chosen_logps, rejected_logps, beta, gamma_ratio)
    chosen_rewards = beta * chosen_logps
    rejected_rewards = beta * rejected_logps
    lt = loss_type.lower()
    if lt == "sigmoid":
        losses = sigmoid_loss(logits, label_smoothing)
    elif lt == "hinge":
        losses = hinge_loss(logits)
    else:
        raise ValueError("Unknown loss_type. Use 'sigmoid' or 'hinge'.")
    return losses, chosen_rewards, rejected_rewards


def parse_array(arg: str) -> np.ndarray:
    arg = arg.strip()
    if not arg:
        raise ValueError("Empty array argument")
    return np.array([float(x) for x in arg.split(',')], dtype=np.float64)


def main():
    p = argparse.ArgumentParser(description="Pairwise margin-based loss utility")
    p.add_argument("--chosen", required=True, help="Comma-separated chosen log probabilities")
    p.add_argument("--rejected", required=True, help="Comma-separated rejected log probabilities")
    p.add_argument("--beta", type=float, required=True, help="Reward scaling factor")
    p.add_argument("--gamma-ratio", type=float, required=True, help="Margin ratio before scaling")
    p.add_argument("--loss-type", choices=["sigmoid", "hinge"], default="sigmoid")
    p.add_argument("--label-smoothing", type=float, default=0.0)
    args = p.parse_args()

    chosen = parse_array(args.chosen)
    rejected = parse_array(args.rejected)

    losses, cr, rr = compute_pairwise_loss(
        chosen, rejected, args.beta, args.gamma_ratio, args.loss_type, args.label_smoothing
    )

    # Print concise results for inspection
    np.set_printoptions(precision=6, suppress=True)
    print("losses:", losses)
    print("chosen_rewards:", cr)
    print("rejected_rewards:", rr)


if __name__ == "__main__":
    main()
