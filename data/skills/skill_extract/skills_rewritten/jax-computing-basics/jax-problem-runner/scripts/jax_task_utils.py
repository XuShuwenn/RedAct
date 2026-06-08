#!/usr/bin/env python3
"""
JAX task utilities for loading inputs, running common computations,
and saving outputs deterministically.

Usage examples (import in your solver script):

from scripts.jax_task_utils import (
    load_input, save_output, row_reduce_mean, elementwise_square,
    logistic_loss_grad, rnn_scan_tanh, two_layer_mlp,
)

# Load input
x = load_input("data/x.npy")  # returns jnp.ndarray
bundle = load_input("data/pack.npz")  # returns {key: jnp.ndarray}

# Compute
y = row_reduce_mean(x, axis=1)

# Save
save_output("outputs/reduced.npy", y)

Notes:
- Keep I/O outside of JIT and grad; only JIT pure numerical functions.
- Convert to jnp arrays before JAX transformations.
"""

from __future__ import annotations
import os
from typing import Any, Dict, Tuple, Union

import numpy as np
import jax
import jax.numpy as jnp
from jax import lax

ArrayOrDict = Union[jnp.ndarray, Dict[str, jnp.ndarray]]


def _ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


def load_input(path: str) -> ArrayOrDict:
    """Load .npy (as array) or .npz (as dict of arrays) and convert to jnp.

    - .npy => jnp.ndarray
    - .npz => dict[str, jnp.ndarray]
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input not found: {path}")
    if path.endswith(".npy"):
        arr = np.load(path, allow_pickle=False)
        return jnp.array(arr)
    if path.endswith(".npz"):
        pack = np.load(path, allow_pickle=False)
        return {k: jnp.array(pack[k]) for k in pack.files}
    # Fallback: try numpy load (may raise)
    obj = np.load(path, allow_pickle=False)
    if isinstance(obj, np.lib.npyio.NpzFile):
        return {k: jnp.array(obj[k]) for k in obj.files}
    return jnp.array(obj)


def save_output(path: str, arr: jnp.ndarray) -> None:
    """Save a JAX array to .npy deterministically, creating directories as needed."""
    _ensure_dir(path)
    host_arr = jax.device_get(arr)
    np.save(path, host_arr)


# ------------------------------
# Common computations
# ------------------------------

def row_reduce_mean(x: jnp.ndarray, axis: int = 1) -> jnp.ndarray:
    """Row/axis mean reduction with explicit axis."""
    return jnp.mean(x, axis=axis)


def elementwise_square(x: jnp.ndarray) -> jnp.ndarray:
    """Elementwise square with broadcasting support."""
    return jnp.square(x)


# ------------------------------
# Gradients (example: binary logistic loss)
# ------------------------------

def _logistic_loss(w: jnp.ndarray, X: jnp.ndarray, y: jnp.ndarray) -> jnp.ndarray:
    """Mean binary logistic loss with numerically stable softplus.

    Assumes y in {0,1}. Shapes: X[..., D], w[D], logits = X @ w.
    """
    logits = X @ w
    # softplus = log(1 + exp(z)) implemented as logaddexp(0, z)
    return jnp.mean(jnp.logaddexp(0.0, logits) - y * logits)


def logistic_loss_grad(w: jnp.ndarray, X: jnp.ndarray, y: jnp.ndarray) -> jnp.ndarray:
    """Gradient of mean binary logistic loss w.r.t. w."""
    grad_fn = jax.grad(_logistic_loss)
    return grad_fn(w, X, y)


# ------------------------------
# Sequential computation with lax.scan (simple tanh RNN)
# ------------------------------

def rnn_scan_tanh(
    params: Dict[str, jnp.ndarray],
    xs: jnp.ndarray,
    h0: jnp.ndarray | None = None,
) -> Tuple[jnp.ndarray, jnp.ndarray]:
    """Run a tanh RNN using lax.scan.

    params: {'Wx': [D, H], 'Wh': [H, H], 'b': [H]}
    xs: [T, D]
    h0: [H] (defaults to zeros)

    Returns: (h_final [H], hs [T, H])
    """
    Wx = params["Wx"]
    Wh = params["Wh"]
    b = params["b"]
    H = Wh.shape[0]
    if h0 is None:
        h0 = jnp.zeros((H,), dtype=xs.dtype)

    def step(h: jnp.ndarray, x: jnp.ndarray) -> Tuple[jnp.ndarray, jnp.ndarray]:
        h_new = jnp.tanh(x @ Wx + h @ Wh + b)
        return h_new, h_new

    h_final, hs = lax.scan(step, h0, xs)
    return h_final, hs


# ------------------------------
# JIT-compiled two-layer MLP
# ------------------------------

def _two_layer_mlp_impl(params: Dict[str, jnp.ndarray], x: jnp.ndarray) -> jnp.ndarray:
    """2-layer MLP: ReLU hidden, linear output.

    params: {'W1': [D, H], 'b1': [H], 'W2': [H, O], 'b2': [O]}
    x: [..., D]
    """
    z1 = x @ params["W1"] + params["b1"]
    h = jnp.maximum(z1, 0.0)
    y = h @ params["W2"] + params["b2"]
    return y


two_layer_mlp = jax.jit(_two_layer_mlp_impl)


# ------------------------------
# Utilities
# ------------------------------

def summarize(obj: ArrayOrDict) -> Dict[str, Any]:
    """Return a lightweight summary of shapes/dtypes for debugging/verification."""
    if isinstance(obj, dict):
        return {k: {"shape": tuple(v.shape), "dtype": str(v.dtype)} for k, v in obj.items()}
    return {"shape": tuple(obj.shape), "dtype": str(obj.dtype)}


def finite_difference_check(
    f, params: jnp.ndarray, eps: float = 1e-4, idx: int = 0
) -> float:
    """Simple 1D finite-difference gradient check at a single index.

    f: function(params) -> scalar
    params: parameter vector
    eps: small perturbation
    idx: index to check

    Returns absolute difference between analytic and numeric gradient at idx.
    """
    params = jnp.array(params)
    g = jax.grad(lambda p: f(p))(params)
    e = jnp.zeros_like(params).at[idx].set(1.0)
    fp = f(params + eps * e)
    fm = f(params - eps * e)
    g_num = (fp - fm) / (2 * eps)
    return float(jnp.abs(g[idx] - g_num))
