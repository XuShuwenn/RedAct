#!/usr/bin/env python3
"""
Generic gravitational-wave matched filtering pipeline:
- Load and condition strain data
- Estimate PSD
- Convert data and templates to frequency domain with matching delta_f
- Grid search over masses for specified approximants
- Report best SNR and total mass per approximant to CSV

This script is parameterized via CLI; it is not tied to a specific dataset.
"""
import argparse
import csv
import math
import os
import sys

import numpy as np
from pycbc.frame import read_frame
from pycbc.filter import highpass, resample_to_delta_t, matched_filter
from pycbc.psd import interpolate, inverse_spectrum_truncation
from pycbc.waveform import get_td_waveform


def log(msg: str):
    print(msg, flush=True)


def condition_data(frame_file: str,
                   channel: str,
                   sample_rate: float,
                   highpass_hz: float,
                   crop_sec: float,
                   psd_seg_len: float,
                   psd_low_freq: float):
    """Load, condition strain, and build PSD and data frequency series."""
    log("[1/4] Loading strain data...")
    strain = read_frame(frame_file, channel)

    log(f"  Raw: duration={strain.duration:.1f}s, fs={strain.sample_rate:.0f} Hz")

    log(f"[2/4] Conditioning: high-pass {highpass_hz:g} Hz, resample {sample_rate:g} Hz, crop {crop_sec:g}s")
    strain = highpass(strain, highpass_hz)
    strain = resample_to_delta_t(strain, 1.0 / sample_rate)
    strain = strain.crop(crop_sec, crop_sec)
    log(f"  Cond: duration={strain.duration:.1f}s, fs={strain.sample_rate:.0f} Hz")

    log("[3/4] Estimating PSD...")
    psd = strain.psd(psd_seg_len)
    psd = interpolate(psd, strain.delta_f)
    psd = inverse_spectrum_truncation(
        psd,
        int(4 * strain.sample_rate),
        low_frequency_cutoff=psd_low_freq,
    )
    log(f"  PSD: len={len(psd)}, delta_f={psd.delta_f:.6f}")

    # Prepare frequency-series data to avoid repeated FFTs later
    data_fd = strain.to_frequencyseries(delta_f=psd.delta_f)
    data_fd.resize(len(psd))

    return strain, psd, data_fd


def best_for_approximant(approximant: str,
                          strain,
                          psd,
                          data_fd,
                          mass_min: int,
                          mass_max: int,
                          f_lower: float,
                          crop_sec: float,
                          progress_every: int = 200):
    """Search grid of masses and return dict(approximant, snr, total_mass)."""
    tested = 0
    failures = 0
    best = {
        "snr": -math.inf,
        "m1": None,
        "m2": None,
    }

    log(f"[4/4] Approximant: {approximant} | mass grid: {mass_min}..{mass_max} (m1>=m2)")

    total_pairs = (mass_max - mass_min + 1) * (mass_max - mass_min + 2) // 2

    for m1 in range(mass_min, mass_max + 1):
        for m2 in range(mass_min, m1 + 1):  # enforce m1 >= m2
            tested += 1
            try:
                hp, _ = get_td_waveform(
                    approximant=approximant,
                    mass1=m1,
                    mass2=m2,
                    delta_t=strain.delta_t,
                    f_lower=f_lower,
                    distance=1,
                )
            except Exception:
                failures += 1
                continue

            # Align and convert template to frequency domain with PSD's frequency resolution
            hp = hp.cyclic_time_shift(hp.start_time)
            htilde = hp.to_frequencyseries(delta_f=psd.delta_f)
            htilde.resize(len(psd))

            try:
                snr = matched_filter(
                    htilde,
                    data_fd,
                    psd=psd,
                    low_frequency_cutoff=f_lower,
                )
            except Exception:
                failures += 1
                continue

            # Crop edge artifacts (unit: seconds)
            try:
                snr = snr.crop(crop_sec, crop_sec)
            except Exception:
                # If cropping fails due to short length, skip template
                continue

            peak = np.max(np.abs(snr.numpy()))
            if not (np.isfinite(peak)):
                continue

            if peak > best["snr"]:
                best["snr"] = float(peak)
                best["m1"] = m1
                best["m2"] = m2

            if tested % progress_every == 0 or tested == total_pairs:
                msg = (f"  {approximant}: {tested}/{total_pairs} checked | "
                       f"best SNR={best['snr']:.2f} @ m1={best['m1']}, m2={best['m2']} | "
                       f"fail={failures}")
                log(msg)

    if best["m1"] is None:
        raise RuntimeError(f"No valid templates found for {approximant}")

    return {
        "approximant": approximant,
        "snr": best["snr"],
        "total_mass": int(best["m1"] + best["m2"]),
    }


def main():
    ap = argparse.ArgumentParser(description="GW matched filtering over mass grid")
    ap.add_argument("--frame", required=True, help="Path to frame (GWF) file")
    ap.add_argument("--channel", required=True, help="Channel name (e.g., H1:STRAIN)")
    ap.add_argument("--approximant", action="append", default=[],
                    help="Waveform approximant (repeat flag to add more)")
    ap.add_argument("--mass-min", type=int, default=10, help="Minimum component mass (solar masses)")
    ap.add_argument("--mass-max", type=int, default=40, help="Maximum component mass (solar masses)")
    ap.add_argument("--sample-rate", type=float, default=2048.0, help="Target sampling rate (Hz)")
    ap.add_argument("--highpass", type=float, default=15.0, help="High-pass frequency (Hz)")
    ap.add_argument("--f-lower", type=float, default=20.0, help="Low frequency cutoff for templates and filtering (Hz)")
    ap.add_argument("--psd-seg-len", type=float, default=4.0, help="PSD segment length (s)")
    ap.add_argument("--crop-sec", type=float, default=4.0, help="Seconds to crop from SNR edges")
    ap.add_argument("--progress-every", type=int, default=200, help="Progress print frequency (templates)")
    ap.add_argument("--output", required=True, help="Output CSV path")

    args = ap.parse_args()

    approximants = args.approximant or ["SEOBNRv4_opt", "IMRPhenomD", "TaylorT4"]

    strain, psd, data_fd = condition_data(
        frame_file=args.frame,
        channel=args.channel,
        sample_rate=args.sample_rate,
        highpass_hz=args.highpass,
        crop_sec=args.crop_sec,
        psd_seg_len=args.psd_seg_len,
        psd_low_freq=args.highpass,
    )

    results = []
    for approx in approximants:
        res = best_for_approximant(
            approximant=approx,
            strain=strain,
            psd=psd,
            data_fd=data_fd,
            mass_min=args.mass_min,
            mass_max=args.mass_max,
            f_lower=args.f_lower,
            crop_sec=args.crop_sec,
            progress_every=args.progress_every,
        )
        results.append(res)

    # Write CSV
    out = args.output
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["approximant", "snr", "total_mass"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    log(f"Done. Wrote results to {out}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
