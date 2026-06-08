#!/usr/bin/env python3
"""
Generic JAX problem runner for small tasks defined in a JSON file.

Supports example task IDs:
- basic_reduce: row-wise mean (2D) or reduce along last axis
- map_square: elementwise square
- grad_logistic: gradient of stable logistic loss (labels in {0,1} or {-1,1})
- scan_rnn: RNN forward pass via lax.scan (tanh activation)
- jit_mlp: 2-layer MLP with ReLU hidden, JIT compiled

Usage:
  python3 scripts/jax_problem_runner.py --problem problem.json

This script is designed to be extended for additional tasks.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

import numpy as np
import jax
import jax.numpy as jnp

# ---------- Utilities ----------

def resolve_path(base: Path, p: str) -> Path:
    path = Path(p)
    return path if path.is_absolute() else base / path


def ensure_parent(path: Path) -> None:
    parent = path.parent
    if parent and not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


def npz_pick(d: Any, candidates: Iterable[str], *, required: bool = True) -> Any:
    """Return the first present key from candidates in an npz-like dict.
    If not found and required, raise a KeyError.
    """
    for k in candidates:
        if k in d:
            return d[k]
    if required:
        raise KeyError(f"None of keys {list(candidates)} found in npz file.")
    return None


def to_jax(x: Any) -> jnp.ndarray:
    return jnp.asarray(x)


def to_numpy(x: Any) -> np.ndarray:
    return np.asarray(x)


def save_npy(path: Path, arr: Any) -> None:
    ensure_parent(path)
    np.save(path, to_numpy(arr))


def check_finite(name: str, arr: jnp.ndarray) -> None:
    if not jnp.all(jnp.isfinite(arr)):
        raise ValueError(f"Non-finite values detected in {name}.")

# ---------- Task Handlers ----------

def handle_basic_reduce(input_path: Path) -> np.ndarray:
    x = np.load(input_path)
    xj = to_jax(x)
    if xj.ndim >= 2:
        out = jnp.mean(xj, axis=1)
    else:
        out = jnp.mean(xj, axis=0)
    check_finite("basic_reduce", out)
    return to_numpy(out)


def handle_map_square(input_path: Path) -> np.ndarray:
    x = np.load(input_path)
    xj = to_jax(x)
    out = jnp.square(xj)
    check_finite("map_square", out)
    return to_numpy(out)


def _labels_to_pm1(y: jnp.ndarray) -> jnp.ndarray:
    uniq = jnp.unique(y)
    # If labels are {0,1}, map to {-1,1}
    if uniq.size <= 2 and jnp.all((uniq == 0) | (uniq == 1)):
        return 2.0 * y - 1.0
    # If labels already in {-1,1}, return as float
    if uniq.size <= 2 and jnp.all((uniq == -1) | (uniq == 1)):
        return y.astype(jnp.result_type(y, 1.0))
    raise ValueError("Unsupported label domain for logistic loss. Expected {0,1} or {-1,1}.")


def handle_grad_logistic(input_path: Path) -> np.ndarray:
    data = np.load(input_path)
    x = to_jax(npz_pick(data, ["x", "X"]))
    y = to_jax(npz_pick(data, ["y"]))
    w = to_jax(npz_pick(data, ["w"]))

    y_pm = _labels_to_pm1(y)

    def loss_fn(w_vec: jnp.ndarray) -> jnp.ndarray:
        logits = x @ w_vec  # shape (N,)
        return jnp.mean(jnp.logaddexp(0.0, -y_pm * logits))

    g = jax.grad(loss_fn)(w)
    check_finite("grad_logistic", g)
    return to_numpy(g)


def handle_scan_rnn(input_path: Path) -> np.ndarray:
    data = np.load(input_path)
    # Flexible key resolution
    seq = to_jax(npz_pick(data, ["seq", "x"]))              # (T, D)
    init = to_jax(npz_pick(data, ["init", "h0"]))           # (H,)
    Wx = to_jax(npz_pick(data, ["Wx", "Wxh"]))              # (D, H)
    Wh = to_jax(npz_pick(data, ["Wh", "Whh"]))              # (H, H)
    b = to_jax(npz_pick(data, ["b", "bh"]))                 # (H,)

    # Shape sanity checks (best-effort)
    if seq.ndim != 2:
        raise ValueError("seq must be 2D (T, D)")
    T, D = seq.shape
    H = init.shape[0]
    if Wx.shape != (D, H):
        raise ValueError(f"Wx must be (D,H) = ({D},{H}), got {Wx.shape}")
    if Wh.shape != (H, H):
        raise ValueError(f"Wh must be (H,H) = ({H},{H}), got {Wh.shape}")
    if b.shape != (H,):
        raise ValueError(f"b must be (H,), got {b.shape}")

    def step(h_prev: jnp.ndarray, x_t: jnp.ndarray) -> Tuple[jnp.ndarray, jnp.ndarray]:
        h_next = jnp.tanh(x_t @ Wx + h_prev @ Wh + b)
        return h_next, h_next

    _, h_seq = jax.lax.scan(step, init, seq)
    check_finite("scan_rnn", h_seq)
    return to_numpy(h_seq)


def handle_jit_mlp(input_path: Path, activation: str = "relu") -> np.ndarray:
    data = np.load(input_path)
    X = to_jax(npz_pick(data, ["X", "x"]))                   # (N, Din)
    W1 = to_jax(npz_pick(data, ["W1"]))                      # (Din, H)
    b1 = to_jax(npz_pick(data, ["b1"]))                      # (H,)
    W2 = to_jax(npz_pick(data, ["W2"]))                      # (H, Dout)
    b2 = to_jax(npz_pick(data, ["b2"]))                      # (Dout,)

    # Choose activation
    def act(z: jnp.ndarray) -> jnp.ndarray:
        if activation == "relu":
            return jax.nn.relu(z)
        elif activation == "tanh":
            return jnp.tanh(z)
        elif activation == "sigmoid":
            return jax.nn.sigmoid(z)
        else:
            return z  # linear

    def forward(x_in: jnp.ndarray) -> jnp.ndarray:
        h = act(x_in @ W1 + b1)
        return h @ W2 + b2

    forward_jit = jax.jit(forward)
    Y = forward_jit(X)
    check_finite("jit_mlp", Y)
    return to_numpy(Y)

# ---------- Dispatcher ----------

HANDLERS = {
    "basic_reduce": lambda p: handle_basic_reduce(p),
    "map_square": lambda p: handle_map_square(p),
    "grad_logistic": lambda p: handle_grad_logistic(p),
    "scan_rnn": lambda p: handle_scan_rnn(p),
    "jit_mlp": lambda p: handle_jit_mlp(p, activation="relu"),
}

# ---------- CLI ----------

def main() -> None:
    parser = argparse.ArgumentParser(description="Run JAX tasks from a problem.json file.")
    parser.add_argument("--problem", default="problem.json", help="Path to problem.json")
    args = parser.parse_args()

    base = Path.cwd()
    problem_path = resolve_path(base, args.problem)
    tasks = json.loads(problem_path.read_text())

    for task in tasks:
        task_id = task.get("id")
        input_rel = task.get("input")
        output_rel = task.get("output")
        if not (task_id and input_rel and output_rel):
            raise ValueError(f"Task is missing required fields: {task}")
        handler = HANDLERS.get(task_id)
        if handler is None:
            raise ValueError(f"Unknown task id: {task_id}")

        input_path = resolve_path(base, input_rel)
        output_path = resolve_path(base, output_rel)

        result = handler(input_path)
        save_npy(output_path, result)

if __name__ == "__main__":
    main()
