#!/usr/bin/env python3
"""
Lightweight P/S phase picker for 3-component NPZ waveform files.

Assumptions:
- Each NPZ file contains:
  - data: (num_samples, 3) float array
  - dt: sampling interval in seconds (float)
  - channels: optional comma-separated string naming channels

Algorithm overview:
- Robust preprocessing (detrend, clip, robust scale)
- Simple bandpass via moving-average high-pass + short smoothing
- STA/LTA on vertical (P) and horizontal magnitude (S)
- Candidate refinement with local AIC
- Validation via SNR and polarization checks

Usage:
  python lightweight_phase_picker.py --data-dir /path/to/data --output /path/to/results.csv \
      [--p-thr 3.5] [--s-thr 3.5] [--min-ps-gap 0.2] [--max-picks 3]

This script uses only Python stdlib and numpy.
"""

import os
import csv
import glob
import math
import argparse
from typing import List, Tuple, Optional

import numpy as np


def moving_average(x: np.ndarray, n: int) -> np.ndarray:
    if n <= 1:
        return x.copy()
    kernel = np.ones(n, dtype=float) / n
    y = np.convolve(x, kernel, mode='same')
    return y


def highpass_ma(x: np.ndarray, n_hp: int) -> np.ndarray:
    # High-pass by subtracting a moving average
    return x - moving_average(x, max(1, n_hp))


def smooth(x: np.ndarray, n: int) -> np.ndarray:
    return moving_average(x, max(1, n))


def robust_scale(x: np.ndarray) -> np.ndarray:
    x = x.astype(float)
    x = x - np.nanmean(x)
    # MAD scaling
    med = np.nanmedian(x)
    mad = np.nanmedian(np.abs(x - med))
    scale = mad * 1.4826 if mad > 0 else (np.nanstd(x) if np.nanstd(x) > 0 else 1.0)
    # Clip outliers before scaling
    if scale > 0:
        z = (x - med) / scale
    else:
        z = x
    z = np.clip(z, -5.0, 5.0)
    return z


def energy_sta_lta(x: np.ndarray, nsta: int, nlta: int, eps: float = 1e-12) -> np.ndarray:
    """STA/LTA on energy (x^2) using moving averages.
    Returns ratio array aligned with x.
    """
    nsta = max(1, int(nsta))
    nlta = max(nsta + 1, int(nlta))
    e = x * x
    sta = moving_average(e, nsta)
    lta = moving_average(e, nlta)
    return sta / (lta + eps)


def aic_pick(x: np.ndarray, center: int, half_win: int) -> int:
    """Local AIC minimization around a center index.
    Returns index of minimum AIC within [center - half_win, center + half_win].
    """
    n = len(x)
    lo = max(1, center - half_win)
    hi = min(n - 2, center + half_win)
    seg = x[lo:hi+1]
    m = len(seg)
    if m < 4:
        return center
    # Compute AIC for each split k
    aic_vals = np.full(m, np.inf)
    for k in range(1, m - 1):
        v1 = np.var(seg[:k])
        v2 = np.var(seg[k:])
        v1 = v1 if v1 > 1e-12 else 1e-12
        v2 = v2 if v2 > 1e-12 else 1e-12
        aic_vals[k] = k * math.log(v1) + (m - k - 1) * math.log(v2)
    kmin = int(np.argmin(aic_vals))
    return lo + kmin


def horizontal_magnitude(h1: np.ndarray, h2: np.ndarray) -> np.ndarray:
    return np.sqrt(np.maximum(0.0, h1*h1 + h2*h2))


def compute_snr(e: np.ndarray, idx: int, fs: float, pre_s: float = 0.1, post_s: float = 0.1) -> float:
    pre_n = max(1, int(pre_s * fs))
    post_n = max(1, int(post_s * fs))
    a = max(0, idx - pre_n)
    b = min(len(e), idx + post_n)
    pre = e[max(0, idx - pre_n): idx]
    post = e[idx: b]
    if pre.size == 0 or post.size == 0:
        return 0.0
    pre_e = np.mean(pre)
    post_e = np.mean(post)
    return (post_e + 1e-12) / (pre_e + 1e-12)


def estimate_vertical_index(channels: Optional[str], data: np.ndarray, fs: float) -> int:
    # Prefer label-based
    if channels:
        labels = [c.strip().upper() for c in channels.split(',')]
        for i, lab in enumerate(labels):
            if 'Z' in lab:
                return i
    # Fallback: pick channel with highest kurtosis in early window
    n = data.shape[0]
    w = max(10, int(0.1 * n))
    early = data[:w, :]
    # Simple kurtosis estimate (excess not needed for ranking)
    kurt = []
    for i in range(3):
        x = early[:, i]
        m2 = np.mean((x - np.mean(x))**2) + 1e-12
        m4 = np.mean((x - np.mean(x))**4)
        k = m4 / (m2*m2)
        kurt.append(k)
    return int(np.argmax(kurt))


def pick_phase_indices(data: np.ndarray,
                       dt: float,
                       channels: Optional[str] = None,
                       p_thr: float = 3.5,
                       s_thr: float = 3.5,
                       min_ps_gap_s: float = 0.2,
                       max_picks: int = 3) -> Tuple[List[int], List[int]]:
    """Return lists of P and S pick indices (0-based)."""
    fs = 1.0 / float(dt)
    n = data.shape[0]
    x = data.copy().astype(float)

    # Replace NaNs, detrend, robust scale per channel
    for i in range(3):
        xi = x[:, i]
        # NaN to 0
        if np.isnan(xi).any():
            xi = np.nan_to_num(xi)
        # Detrend (demean is cheap and sufficient for STA/LTA in most cases)
        xi = xi - np.mean(xi)
        xi = robust_scale(xi)
        x[:, i] = xi

    # Determine vertical and horizontals
    v_idx = estimate_vertical_index(channels, x, fs)
    h_idx = [i for i in range(3) if i != v_idx]
    v = x[:, v_idx]
    h1, h2 = x[:, h_idx[0]], x[:, h_idx[1]]
    hmag = horizontal_magnitude(h1, h2)

    # Simple bandpass proxy: high-pass by subtracting long MA, then smooth
    n_hp = max(1, int(0.75 * fs))
    n_sm_short = max(1, int(0.05 * fs))
    v_bp = smooth(highpass_ma(v, n_hp), n_sm_short)
    h_bp = smooth(highpass_ma(hmag, n_hp), n_sm_short)

    # Noise baseline from early segment
    w_noise = max(10, int(0.1 * n))
    v_noise = np.mean(v_bp[:w_noise]**2) + 1e-12
    h_noise = np.mean(h_bp[:w_noise]**2) + 1e-12

    # STA/LTA configurations
    sta_p = max(3, int(0.06 * fs))
    lta_p = max(sta_p + 1, int(0.8 * fs))
    sta_s = max(3, int(0.08 * fs))
    lta_s = max(sta_s + 1, int(1.0 * fs))

    r_p = energy_sta_lta(v_bp, sta_p, lta_p)
    r_s = energy_sta_lta(h_bp, sta_s, lta_s)

    # Detect candidates with refractory period
    def detect_candidates(r: np.ndarray, thr: float, refractory_s: float) -> List[int]:
        refractory = max(1, int(refractory_s * fs))
        idxs = []
        i = 1
        while i < len(r) - 1:
            if r[i-1] < thr <= r[i] and r[i] >= r[i+1]:
                # local crossing peak
                idx = i
                idxs.append(idx)
                i += refractory
            else:
                i += 1
        return idxs

    p_cands = detect_candidates(r_p, p_thr, refractory_s=0.35)

    # Refine P picks with local AIC and validate
    p_picks: List[int] = []
    for idx in p_cands:
        pk = aic_pick(v_bp, idx, half_win=max(5, int(0.05 * fs)))
        # SNR validation on vertical energy
        snr = compute_snr(v_bp*v_bp, pk, fs, pre_s=0.1, post_s=0.1)
        # Vertical dominance: compare vertical vs horizontal energy nearby
        win = max(5, int(0.05 * fs))
        a = max(0, pk - win)
        b = min(n, pk + win)
        ve = np.mean(v_bp[a:b]**2) + 1e-12
        he = np.mean(h_bp[a:b]**2) + 1e-12
        v_frac = ve / (ve + he)
        if snr >= 2.5 and v_frac >= 0.4:
            p_picks.append(pk)
            if len(p_picks) >= max_picks:
                break

    # S candidates: search after earliest valid P pick if present
    s_search_start = 0
    if p_picks:
        min_ps_gap = int(min_ps_gap_s * fs)
        s_search_start = min(n-1, p_picks[0] + min_ps_gap)
    r_s_masked = r_s.copy()
    r_s_masked[:s_search_start] = 0.0
    s_cands = [i for i in detect_candidates(r_s_masked, s_thr, refractory_s=0.4) if i >= s_search_start]

    s_picks: List[int] = []
    for idx in s_cands:
        pk = aic_pick(h_bp, idx, half_win=max(5, int(0.06 * fs)))
        # SNR validation on horizontal energy
        snr = compute_snr(h_bp*h_bp, pk, fs, pre_s=0.1, post_s=0.12)
        win = max(5, int(0.06 * fs))
        a = max(0, pk - win)
        b = min(n, pk + win)
        ve = np.mean(v_bp[a:b]**2) + 1e-12
        he = np.mean(h_bp[a:b]**2) + 1e-12
        h_frac = he / (he + ve)
        # Enforce P->S ordering if P exists
        ok_order = True
        if p_picks:
            ok_order = pk > p_picks[0] + int(min_ps_gap_s * fs)
        if snr >= 2.5 and h_frac >= 0.6 and ok_order:
            s_picks.append(pk)
            if len(s_picks) >= max_picks:
                break

    return p_picks, s_picks


def load_npz(path: str) -> Tuple[np.ndarray, float, Optional[str]]:
    d = np.load(path, allow_pickle=True)
    if 'data' not in d or 'dt' not in d:
        raise ValueError(f"File missing required fields: {path}")
    data = d['data']
    dt = float(d['dt'])
    channels = None
    if 'channels' in d:
        # channels may be stored as np array or string
        ch = d['channels']
        if isinstance(ch, (np.ndarray, list)):
            channels = ','.join([str(x) for x in ch])
        else:
            channels = str(ch)
    if data.ndim != 2 or data.shape[1] != 3:
        raise ValueError(f"Expected data shape (N, 3), got {data.shape} in {path}")
    return data, dt, channels


def process_directory(data_dir: str,
                      output_csv: str,
                      p_thr: float,
                      s_thr: float,
                      min_ps_gap: float,
                      max_picks: int) -> None:
    files = sorted(glob.glob(os.path.join(data_dir, '*.npz')))
    if not files:
        raise SystemExit(f"No NPZ files found in {data_dir}")

    rows: List[Tuple[str, str, int]] = []

    for f in files:
        try:
            data, dt, channels = load_npz(f)
            p_picks, s_picks = pick_phase_indices(
                data, dt, channels,
                p_thr=p_thr, s_thr=s_thr,
                min_ps_gap_s=min_ps_gap,
                max_picks=max_picks,
            )
            base = os.path.basename(f)
            for pk in p_picks:
                rows.append((base, 'P', int(pk)))
            for pk in s_picks:
                rows.append((base, 'S', int(pk)))
        except Exception as e:
            # Skip file on hard errors; continue batch
            # Could log to stderr; keeping silent for portability
            continue

    # Write CSV
    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    with open(output_csv, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['file_name', 'phase', 'pick_idx'])
        for row in rows:
            w.writerow(row)


def main():
    ap = argparse.ArgumentParser(description='Lightweight seismic P/S picker (no heavy deps)')
    ap.add_argument('--data-dir', required=True, help='Directory containing *.npz waveform files')
    ap.add_argument('--output', required=True, help='Output CSV path')
    ap.add_argument('--p-thr', type=float, default=3.5, help='STA/LTA threshold for P candidates')
    ap.add_argument('--s-thr', type=float, default=3.5, help='STA/LTA threshold for S candidates')
    ap.add_argument('--min-ps-gap', type=float, default=0.2, help='Minimum P->S gap in seconds')
    ap.add_argument('--max-picks', type=int, default=3, help='Maximum P or S picks per file')
    args = ap.parse_args()

    process_directory(
        data_dir=args.data_dir,
        output_csv=args.output,
        p_thr=args.p_thr,
        s_thr=args.s_thr,
        min_ps_gap=args.min_ps_gap,
        max_picks=args.max_picks,
    )


if __name__ == '__main__':
    main()
