#!/usr/bin/env python3
"""Transit period detection helper: filtering, detrending, BLS search, alias checks.

Requirements (preferred):
- numpy
- astropy (for BoxLeastSquares); if unavailable, the script will instruct installation
- scipy (optional, for savgol_filter); falls back to moving median if not available

Usage examples:
  python scripts/transit_period_tools.py --input lc.txt --period-min 0.5 --period-max 12 --output period.txt
  python scripts/transit_period_tools.py --input lc.txt --time-col 0 --flux-col 1 --qual-col 2 --err-col 3 --quality-good 0 \
      --detrend-window-days 1.0 --period-min 0.3 --period-max 20 --output period.txt

The script writes a single number (days) rounded to 5 decimals to the output path.
"""

import os
import sys
import math
import argparse
from typing import Tuple, Optional

import numpy as np

# Optional SciPy imports
try:
    from scipy.signal import savgol_filter
except Exception:
    savgol_filter = None

# Set resource guards early
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")


def load_txt(
    path: str,
    time_col: int = 0,
    flux_col: int = 1,
    qual_col: Optional[int] = 2,
    err_col: Optional[int] = 3,
) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
    arr = np.loadtxt(path)
    time = arr[:, time_col].astype(float)
    flux = arr[:, flux_col].astype(float)
    qual = arr[:, qual_col].astype(float) if qual_col is not None else None
    err = arr[:, err_col].astype(float) if err_col is not None else None
    return time, flux, qual, err


def finite_mask(*arrays):
    mask = np.ones_like(arrays[0], dtype=bool)
    for a in arrays:
        if a is not None:
            mask &= np.isfinite(a)
    return mask


def sigma_clip_mask(x: np.ndarray, sigma: float = 5.0) -> np.ndarray:
    med = np.nanmedian(x)
    mad = np.nanmedian(np.abs(x - med))
    if mad <= 0:
        # Fallback to std if MAD is zero
        std = np.nanstd(x)
        if std == 0:
            return np.ones_like(x, dtype=bool)
        lo = med - sigma * std
        hi = med + sigma * std
    else:
        # 1.4826 * MAD ≈ std for normal distribution
        std = 1.4826 * mad
        lo = med - sigma * std
        hi = med + sigma * std
    return (x >= lo) & (x <= hi)


def segment_indices(time: np.ndarray, gap_factor: float = 5.0) -> np.ndarray:
    if len(time) < 2:
        return np.array([0, len(time)], dtype=int)
    dt = np.diff(time)
    med_dt = np.nanmedian(dt) if np.isfinite(dt).any() else 0.0
    if med_dt <= 0:
        return np.array([0, len(time)], dtype=int)
    gap = gap_factor * med_dt
    cuts = np.where(dt > gap)[0]
    # segment boundaries
    bounds = [0] + [c + 1 for c in cuts] + [len(time)]
    return np.array(bounds, dtype=int)


def moving_median(y: np.ndarray, win: int) -> np.ndarray:
    # Simple O(n*w) median filter (fallback if SciPy unavailable)
    n = len(y)
    if win <= 1:
        return y.copy()
    k = win // 2
    out = np.empty_like(y)
    for i in range(n):
        lo = max(0, i - k)
        hi = min(n, i + k + 1)
        out[i] = np.nanmedian(y[lo:hi])
    return out


def detrend_segment(time: np.ndarray, flux: np.ndarray, window_days: float, polyorder: int = 2) -> np.ndarray:
    if len(time) < 5:
        return np.ones_like(flux)
    dt = np.nanmedian(np.diff(time))
    if not np.isfinite(dt) or dt <= 0:
        dt = (time[-1] - time[0]) / max(1, len(time) - 1)
    window_pts = max(5, int(round(window_days / max(dt, 1e-10))))
    if window_pts % 2 == 0:
        window_pts += 1
    # Clamp polyorder
    poly = min(polyorder, max(1, window_pts - 2))
    if savgol_filter is not None and window_pts >= (poly + 2):
        try:
            trend = savgol_filter(flux, window_length=window_pts, polyorder=poly, mode="interp")
            trend[~np.isfinite(trend)] = np.nanmedian(flux)
            trend[trend <= 0] = np.nanmedian(flux)
            return trend
        except Exception:
            pass
    # Fallback moving median
    trend = moving_median(flux, window_pts)
    trend[~np.isfinite(trend)] = np.nanmedian(flux)
    trend[trend <= 0] = np.nanmedian(flux)
    return trend


def flatten(time: np.ndarray, flux: np.ndarray, window_days: float) -> np.ndarray:
    bounds = segment_indices(time)
    trend = np.empty_like(flux)
    for i in range(len(bounds) - 1):
        lo, hi = bounds[i], bounds[i + 1]
        trend[lo:hi] = detrend_segment(time[lo:hi], flux[lo:hi], window_days)
    flat = flux / trend
    return flat


def run_bls(
    time: np.ndarray,
    flux: np.ndarray,
    err: Optional[np.ndarray],
    period_min: float,
    period_max: float,
    q_min: float = 0.005,
    q_max: float = 0.1,
    oversample: float = 5.0,
):
    try:
        from astropy.timeseries import BoxLeastSquares
    except Exception as e:
        raise RuntimeError(
            "astropy is required for BLS. Install 'astropy' or use another method."
        ) from e
    # Normalize flux to have median ~1 for stability
    f = flux / np.nanmedian(flux)
    w = None
    if err is not None and np.isfinite(err).all() and np.nanmin(err) > 0:
        w = 1.0 / (err ** 2)
    bls = BoxLeastSquares(time, f)
    durations = np.linspace(q_min, q_max, num=10)
    res = bls.autopower(durations, minimum_period=period_min, maximum_period=period_max, oversample=oversample, objective='snr') if w is None else bls.autopower(durations, minimum_period=period_min, maximum_period=period_max, oversample=oversample, objective='snr', normalization='standard', weights=w)
    # Identify best
    best_idx = int(np.nanargmax(res.power))
    return {
        'periods': res.period,
        'power': res.power,
        'duration': res.duration[best_idx],
        'best_period': float(res.period[best_idx]),
        't0': float(res.transit_time[best_idx]),
        'depth': float(res.depth[best_idx]) if hasattr(res, 'depth') else float('nan'),
        'snr': float(res.power[best_idx]),
    }


def bls_power_at_period(time, flux, period, duration_frac, t0=None):
    try:
        from astropy.timeseries import BoxLeastSquares
    except Exception:
        return np.nan
    f = flux / np.nanmedian(flux)
    bls = BoxLeastSquares(time, f)
    duration = period * max(1e-5, duration_frac)
    try:
        res = bls.power(period=np.array([period]), duration=np.array([duration]), transit_time=t0, objective='snr')
        return float(res.power[0])
    except Exception:
        return np.nan


def odd_even_depth_test(time, flux, period, duration, t0=None, bins=50) -> float:
    # Returns absolute difference between odd/even median in-transit depths (in ppm-like fraction), robust indicator
    phase = ((time - (t0 if t0 is not None else time[0])) / period) % 1.0
    q = max(1e-5, duration / period)
    in_tr = (phase < q/2) | (phase > 1 - q/2)
    # Assign each transit number
    transit_number = np.floor((time - (t0 if t0 is not None else time[0])) / period).astype(int)
    odd = in_tr & (transit_number % 2 != 0)
    even = in_tr & (transit_number % 2 == 0)
    if odd.sum() < 5 or even.sum() < 5:
        return np.nan
    f_med = np.nanmedian(flux)
    odd_depth = f_med - np.nanmedian(flux[odd])
    even_depth = f_med - np.nanmedian(flux[even])
    return float(abs(odd_depth - even_depth))


def refine_period(time, flux, err, base_period, width_frac=0.02, oversample=15.0, q_min=0.005, q_max=0.1):
    pmin = max(0.1, base_period * (1 - width_frac))
    pmax = base_period * (1 + width_frac)
    return run_bls(time, flux, err, pmin, pmax, q_min=q_min, q_max=q_max, oversample=oversample)


def choose_anti_alias(time, flux, candidate_period, duration_frac, t0=None) -> float:
    # Compare power at P, 2P, P/2; pick the strongest consistent candidate
    Ps = [candidate_period, 2 * candidate_period, candidate_period / 2]
    powers = [bls_power_at_period(time, flux, p, duration_frac, t0=t0) for p in Ps]
    # Ignore NaNs by replacing with -inf
    powers = [(-np.inf if not np.isfinite(x) else x) for x in powers]
    best_idx = int(np.argmax(powers))
    return Ps[best_idx]


def main():
    ap = argparse.ArgumentParser(description="Transit period detection with BLS, detrending, and alias checks")
    ap.add_argument("--input", required=True, help="Path to whitespace-delimited light curve file")
    ap.add_argument("--time-col", type=int, default=0, help="Zero-based column index for time")
    ap.add_argument("--flux-col", type=int, default=1, help="Zero-based column index for normalized flux")
    ap.add_argument("--qual-col", type=int, default=2, help="Zero-based column index for quality flags (-1 to disable)")
    ap.add_argument("--err-col", type=int, default=3, help="Zero-based column index for flux uncertainty (-1 to disable)")
    ap.add_argument("--quality-good", type=float, default=0.0, help="Value of good quality flag to keep")
    ap.add_argument("--sigma", type=float, default=5.0, help="Sigma threshold for clipping outliers")
    ap.add_argument("--detrend-window-days", type=float, default=1.0, help="Window length (days) for detrending")
    ap.add_argument("--period-min", type=float, required=True, help="Minimum period (days)")
    ap.add_argument("--period-max", type=float, required=True, help="Maximum period (days)")
    ap.add_argument("--output", required=True, help="Output file path for the period (days)")
    ap.add_argument("--oversample", type=float, default=5.0, help="BLS oversampling for broad scan")
    ap.add_argument("--refine-width-frac", type=float, default=0.02, help="Relative half-width for refinement scan")
    ap.add_argument("--refine-oversample", type=float, default=15.0, help="BLS oversampling for refinement")
    args = ap.parse_args()

    qual_col = None if args.qual_col < 0 else args.qual_col
    err_col = None if args.err_col < 0 else args.err_col

    time, flux, qual, err = load_txt(args.input, time_col=args.time_col, flux_col=args.flux_col, qual_col=qual_col, err_col=err_col)

    mask = finite_mask(time, flux, err if err_col is not None else None)
    if qual is not None:
        mask &= (qual == args.quality_good)
    time = time[mask]
    flux = flux[mask]
    err = err[mask] if (err_col is not None and err is not None) else None

    if len(time) < 100:
        print("ERROR: Not enough data points after filtering.", file=sys.stderr)
        sys.exit(1)

    # Initial outlier clip
    mask2 = sigma_clip_mask(flux, sigma=args.sigma)
    time, flux = time[mask2], flux[mask2]
    if err is not None:
        err = err[mask2]

    # Detrend per segments
    flat = flatten(time, flux, window_days=args.detrend_window_days)
    flat_flux = flux / flat

    # Post-detrend clipping
    mask3 = sigma_clip_mask(flat_flux, sigma=args.sigma)
    time, flat_flux = time[mask3], flat_flux[mask3]
    if err is not None:
        err = err[mask3]

    # Broad BLS search
    broad = run_bls(time, flat_flux, err, args.period_min, args.period_max, q_min=0.005, q_max=0.1, oversample=args.oversample)
    cand_P = broad['best_period']
    cand_q = max(1e-5, broad['duration'] / broad['best_period'])

    # Alias check P vs 2P vs P/2
    cand_P = choose_anti_alias(time, flat_flux, cand_P, cand_q, t0=broad.get('t0', None))

    # Ensure not at boundaries; if near, expand and rescan
    span = args.period_max - args.period_min
    near_edge = (cand_P <= args.period_min + 0.01 * span) or (cand_P >= args.period_max - 0.01 * span)
    if near_edge:
        pmin = max(0.1, cand_P * 0.8)
        pmax = cand_P * 1.2
        broad2 = run_bls(time, flat_flux, err, pmin, pmax, q_min=0.005, q_max=0.1, oversample=max(args.oversample, 8.0))
        cand_P = broad2['best_period']
        cand_q = max(1e-5, broad2['duration'] / broad2['best_period'])
        cand_P = choose_anti_alias(time, flat_flux, cand_P, cand_q, t0=broad2.get('t0', None))

    # Refinement
    ref = refine_period(time, flat_flux, err, cand_P, width_frac=args.refine_width_frac, oversample=args.refine_oversample, q_min=0.005, q_max=0.1)
    best_P = ref['best_period']
    best_q = max(1e-5, ref['duration'] / ref['best_period'])
    best_P = choose_anti_alias(time, flat_flux, best_P, best_q, t0=ref.get('t0', None))

    # Validation checks (non-fatal but informative)
    baseline = time.max() - time.min()
    n_transits = int(math.floor(baseline / best_P)) if best_P > 0 else 0
    odd_even_delta = odd_even_depth_test(time, flat_flux, best_P, best_P * best_q, t0=ref.get('t0', None))

    if n_transits < 2:
        print("WARNING: Fewer than 2 transits across baseline; period may be unreliable.", file=sys.stderr)

    if np.isfinite(odd_even_delta) and odd_even_delta > 5e-4:
        # threshold depends on data normalization; here ~500 ppm difference triggers warning
        print("WARNING: Odd-even depth difference suggests possible harmonic/EB.", file=sys.stderr)

    # Write result
    try:
        with open(args.output, 'w') as f:
            f.write(f"{best_P:.5f}\n")
    except Exception as e:
        print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Wrote period (days): {best_P:.5f}")
    print(f"Baseline (days): {baseline:.3f}; Estimated transits: {n_transits}")


if __name__ == "__main__":
    main()
