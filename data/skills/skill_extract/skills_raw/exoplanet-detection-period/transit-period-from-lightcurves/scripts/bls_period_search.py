#!/usr/bin/env python3
"""
Robust transit period search with detrending + Astropy BoxLeastSquares.

Features:
- Quality and finite-value filtering, sigma clipping
- Detrending via Savitzky–Golay or (if available) wotan.flatten
- BLS coarse search and fine refinement
- Harmonic checks (P/2 and 2P)
- Resilient stats handling across Astropy versions
- Writes final period rounded to 5 decimals as a single line

Usage:
  python scripts/bls_period_search.py --input lightcurve.txt --output period.txt \
      --min-period 0.5 --max-period 15 --windows 0.3,0.5,0.75 --method savgol

Notes:
- Assumes input columns: time, flux, quality, flux_err (0-based indices configurable).
- Time must be in days. Flux should be normalized (around ~1.0) but not required.
"""

import argparse
import sys
import numpy as np

try:
    import astropy.units as u
    from astropy.timeseries import BoxLeastSquares
except Exception as e:
    print(f"ERROR: astropy is required: {e}", file=sys.stderr)
    sys.exit(1)

from math import isfinite


def parse_args():
    p = argparse.ArgumentParser(description="Transit period search via BLS with detrending")
    p.add_argument("--input", required=True, help="Path to light curve file")
    p.add_argument("--output", required=True, help="Path to write final period (single line)")
    p.add_argument("--time-col", type=int, default=0, help="Time column index (default=0)")
    p.add_argument("--flux-col", type=int, default=1, help="Flux column index (default=1)")
    p.add_argument("--quality-col", type=int, default=2, help="Quality column index (default=2); set -1 to ignore")
    p.add_argument("--err-col", type=int, default=3, help="Flux error column index (default=3); set -1 to ignore")
    p.add_argument("--good-quality", type=float, default=0.0, help="Value indicating good quality (default=0)")
    p.add_argument("--sigma", type=float, default=5.0, help="Sigma for clipping outliers (default=5)")
    p.add_argument("--windows", default="0.3,0.5,0.75", help="Comma-separated detrending window lengths in days")
    p.add_argument("--method", choices=["savgol", "wotan", "median"], default="savgol",
                   help="Detrending method (default=savgol)")
    p.add_argument("--polyorder", type=int, default=2, help="Savgol polyorder if method=savgol (default=2)")
    p.add_argument("--min-period", type=float, default=0.5, help="Minimum period [days] (default=0.5)")
    p.add_argument("--max-period", type=float, default=None, help="Maximum period [days]; default=baseline/2")
    p.add_argument("--dur-min", type=float, default=0.02, help="Min transit duration [days] (default=0.02)")
    p.add_argument("--dur-max", type=float, default=0.12, help="Max transit duration [days] (default=0.12)")
    p.add_argument("--dur-n", type=int, default=8, help="# of duration grid points (default=8)")
    p.add_argument("--harmonics", action="store_true", help="Evaluate P/2 and 2P for comparison")
    return p.parse_args()


def load_lightcurve(path, tcol, fcol, qcol, ecol):
    # Load robustly, ignoring comment lines
    data = []
    with open(path, "r") as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            try:
                row = [float(x) for x in parts]
                data.append(row)
            except Exception:
                continue
    if not data:
        raise RuntimeError("No data rows parsed from input file.")
    arr = np.array(data, dtype=float)

    # Column extraction with basic validation
    time = arr[:, tcol].astype(float)
    flux = arr[:, fcol].astype(float)
    quality = arr[:, qcol].astype(float) if qcol >= 0 else None
    flux_err = arr[:, ecol].astype(float) if ecol >= 0 else None

    # Sort by time
    idx = np.argsort(time)
    time, flux = time[idx], flux[idx]
    if quality is not None:
        quality = quality[idx]
    if flux_err is not None:
        flux_err = flux_err[idx]

    return time, flux, quality, flux_err


def finite_mask(*arrays):
    mask = np.ones_like(arrays[0], dtype=bool)
    for a in arrays:
        if a is None:
            continue
        mask &= np.isfinite(a)
    return mask


def sigma_clip_mask(x, sigma=5.0):
    med = np.nanmedian(x)
    std = np.nanstd(x)
    if not isfinite(std) or std == 0:
        return np.ones_like(x, dtype=bool)
    return np.abs(x - med) < sigma * std


def detrend(time, flux, method, window_days, polyorder):
    # Estimate cadence
    if len(time) < 5:
        return flux.copy()
    dt = np.median(np.diff(time))
    # Guard against zero/negative dt
    if dt <= 0 or not np.isfinite(dt):
        dt = (time[-1] - time[0]) / max(1, (len(time) - 1))
        if dt <= 0 or not np.isfinite(dt):
            return flux.copy()

    if method == "wotan":
        try:
            from wotan import flatten
            flat, trend = flatten(time, flux, method='biweight', window_length=window_days,
                                  return_trend=True, break_tolerance=0.5)
            # Avoid division by zero
            trend = np.where(trend == 0, np.nanmedian(trend), trend)
            return flux / trend
        except Exception:
            method = "savgol"  # fallback

    if method == "savgol":
        try:
            from scipy.signal import savgol_filter
            window_pts = max(int(round(window_days / dt)), 5)
            if window_pts % 2 == 0:
                window_pts += 1
            if window_pts >= len(flux):
                window_pts = len(flux) - (1 - len(flux) % 2)
                if window_pts < 5:
                    return flux.copy()
            trend = savgol_filter(flux, window_length=window_pts, polyorder=min(polyorder, window_pts - 1), mode='interp')
            trend = np.where(trend == 0, np.nanmedian(trend), trend)
            return flux / trend
        except Exception:
            return flux.copy()

    if method == "median":
        try:
            # median filter in points approximating window_days
            from scipy.ndimage import median_filter
            window_pts = max(int(round(window_days / dt)), 5)
            trend = median_filter(flux, size=window_pts, mode='nearest')
            trend = np.where(trend == 0, np.nanmedian(trend), trend)
            return flux / trend
        except Exception:
            return flux.copy()

    return flux.copy()


def bls_search(time, flux, flux_err, min_period, max_period, dur_min, dur_max, dur_n):
    # Prepare inputs with units
    t = time * u.day
    dy = None
    if flux_err is not None:
        dy = flux_err
    model = BoxLeastSquares(t, flux, dy=dy)
    durations = np.linspace(dur_min, dur_max, dur_n) * u.day

    per_min = min_period * u.day
    per_max = max_period * u.day
    res = model.autopower(durations, minimum_period=per_min, maximum_period=per_max)

    idx = int(np.argmax(res.power))
    return {
        "period": res.period[idx].to_value(u.day),
        "power": float(res.power[idx]),
        "duration": res.duration[idx].to_value(u.day),
        "t0": res.transit_time[idx].to_value(u.day),
        "result": res,
        "model": model,
    }


def bls_refine(model, center_period, dur_min, dur_max, dur_n, half_width=0.01, min_period=0.5, max_period=None):
    # half_width defines the ±fractional search window around the center period
    p0 = center_period
    if max_period is None:
        max_period = p0 * (1 + half_width)
    pmin = max(min_period, p0 * (1 - half_width))
    pmax = max_period if max_period is not None else p0 * (1 + half_width)

    periods = np.linspace(pmin, pmax, 30000) * u.day
    durations = np.linspace(dur_min, dur_max, dur_n) * u.day
    res = model.power(periods, durations)
    idx = int(np.argmax(res.power))
    return {
        "period": res.period[idx].to_value(u.day),
        "power": float(res.power[idx]),
        "duration": res.duration[idx].to_value(u.day),
        "t0": res.transit_time[idx].to_value(u.day),
        "result": res,
    }


def compute_depth_snr(model, period, duration, t0, time, flux, flux_err):
    # Try compute_stats; versions differ in keys and shapes
    try:
        stat = model.compute_stats(period * u.day, duration * u.day, t0 * u.day)
    except Exception:
        stat = {}
    depth_val = np.nan
    depth_err = np.nan
    if isinstance(stat, dict):
        d = stat.get("depth", None)
        if d is not None:
            try:
                # Often depth is [value, error]
                depth_val = float(d[0])
                depth_err = float(d[1]) if len(np.atleast_1d(d)) > 1 else np.nan
            except Exception:
                try:
                    depth_val = float(d)
                except Exception:
                    pass
        if not np.isfinite(depth_err):
            # Some versions expose depth_err separately
            if "depth_err" in stat and np.isfinite(stat["depth_err"]):
                depth_err = float(stat["depth_err"])
    # Fallback using out-of-transit scatter
    if not np.isfinite(depth_val) or depth_val == 0 or not np.isfinite(depth_err) or depth_err == 0:
        # Phase fold and estimate depth vs out-of-transit scatter
        phase = ((time - t0) % period) / period
        phase[phase > 0.5] -= 1.0
        half_width = duration / period / 2.0
        in_tr = np.abs(phase) < half_width
        out_tr = np.abs(phase) > 3 * half_width
        if np.any(in_tr) and np.any(out_tr):
            med_in = np.median(flux[in_tr])
            med_out = np.median(flux[out_tr])
            depth_val = med_out - med_in
            oot_scatter = np.std(flux[out_tr])
            neff = max(1, np.sum(in_tr))
            depth_err = oot_scatter / np.sqrt(neff)
    snr = np.nan
    if np.isfinite(depth_val) and np.isfinite(depth_err) and depth_err > 0:
        snr = depth_val / depth_err
    return float(depth_val) if np.isfinite(depth_val) else np.nan, float(depth_err) if np.isfinite(depth_err) else np.nan, float(snr) if np.isfinite(snr) else np.nan


def main():
    args = parse_args()

    # Load and basic filtering
    time, flux, quality, flux_err = load_lightcurve(
        args.input, args.time_col, args.flux_col, args.quality_col, args.err_col
    )

    mask = finite_mask(time, flux)
    if quality is not None:
        mask &= (quality == args.good_quality)
    if flux_err is not None:
        mask &= finite_mask(flux_err)

    time, flux = time[mask], flux[mask]
    flux_err = flux_err[mask] if flux_err is not None else None

    # Sigma-clip outliers on raw flux
    keep = sigma_clip_mask(flux, sigma=args.sigma)
    time, flux = time[keep], flux[keep]
    if flux_err is not None:
        flux_err = flux_err[keep]

    if len(time) < 50:
        print("ERROR: Not enough data points after filtering.", file=sys.stderr)
        sys.exit(1)

    baseline = time.max() - time.min()
    if baseline <= 0:
        print("ERROR: Non-positive baseline.", file=sys.stderr)
        sys.exit(1)

    min_period = float(args.min_period)
    max_period = float(args.max_period) if args.max_period is not None else float(baseline / 2)
    if max_period <= min_period:
        max_period = min_period + 0.1

    windows = []
    try:
        windows = [float(x) for x in args.windows.split(',') if x.strip()]
    except Exception:
        windows = [0.5]
    if not windows:
        windows = [0.5]

    candidates = []

    for wl in windows:
        # Detrend
        f_det = detrend(time, flux, args.method, wl, args.polyorder)
        # Re-clip after detrending
        m2 = sigma_clip_mask(f_det, sigma=args.sigma)
        t2 = time[m2]
        f2 = f_det[m2]
        e2 = flux_err[m2] if flux_err is not None else None
        if len(t2) < 50:
            continue
        try:
            cand = bls_search(t2, f2, e2, min_period, max_period, args.dur_min, args.dur_max, args.dur_n)
            cand.update({"window": wl, "time": t2, "flux": f2, "err": e2})
            candidates.append(cand)
            print(f"Window {wl:.3f} d -> coarse best P={cand['period']:.6f} d, power={cand['power']:.2f}")
        except Exception as e:
            print(f"Window {wl:.3f} d -> BLS error: {e}", file=sys.stderr)
            continue

    if not candidates:
        print("ERROR: No valid BLS results.", file=sys.stderr)
        sys.exit(1)

    # Pick highest power across windows
    best_cand = max(candidates, key=lambda c: c["power"])

    # Refine around best
    refined = bls_refine(best_cand["model"], best_cand["period"], args.dur_min, args.dur_max,
                         args.dur_n, half_width=0.01, min_period=min_period, max_period=max_period)

    period = refined["period"]
    duration = refined["duration"]
    t0 = refined["t0"]

    # Compute depth SNR for refined
    depth, depth_err, snr = compute_depth_snr(best_cand["model"], period, duration, t0,
                                              best_cand["time"], best_cand["flux"], best_cand["err"])

    print(f"Refined: P={period:.6f} d, dur={duration:.4f} d, depth={depth:.6g}, SNR≈{snr:.2f}")

    # Harmonic check
    if args.harmonics:
        choices = [(period, refined["power"])]
        for factor in [0.5, 2.0]:
            hp = period * factor
            if hp < min_period or hp > max_period:
                continue
            try:
                hres = bls_refine(best_cand["model"], hp, args.dur_min, args.dur_max, args.dur_n,
                                  half_width=0.005, min_period=min_period, max_period=max_period)
                choices.append((hres["period"], hres["power"]))
                print(f"Harmonic test {factor:+.1f}x: P={hres['period']:.6f} d, power={hres['power']:.2f}")
            except Exception:
                pass
        # Pick by highest power among tested periods
        best_p, _ = max(choices, key=lambda x: x[1])
        if abs(best_p - period) / period > 1e-6:
            period = best_p
            # Optionally recompute duration/t0 at the new period
            newref = bls_refine(best_cand["model"], period, args.dur_min, args.dur_max, args.dur_n,
                                half_width=0.01, min_period=min_period, max_period=max_period)
            duration = newref["duration"]
            t0 = newref["t0"]
            depth, depth_err, snr = compute_depth_snr(best_cand["model"], period, duration, t0,
                                                      best_cand["time"], best_cand["flux"], best_cand["err"])
            print(f"Selected harmonic-refined P={period:.6f} d")

    # Sanity checks
    n_transits = (best_cand["time"].max() - best_cand["time"].min()) / period
    frac = duration / period if period > 0 else np.nan
    print(f"Baseline/Period ≈ {n_transits:.1f} transits; duration/period ≈ {frac:.4f}")

    # Final rounding and write
    period_rounded = f"{period:.5f}"
    try:
        with open(args.output, "w") as fh:
            fh.write(period_rounded + "\n")
        print(f"Wrote period {period_rounded} to {args.output}")
    except Exception as e:
        print(f"ERROR writing output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
