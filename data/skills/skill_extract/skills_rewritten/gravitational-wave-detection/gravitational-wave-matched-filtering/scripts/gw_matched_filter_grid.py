#!/usr/bin/env python3
"""
Generic gravitational-wave matched filtering grid search using PyCBC.

- Conditions strain (highpass, resample, crop)
- Estimates PSD and applies inverse spectrum truncation
- Generates time-domain templates for requested approximants across a (mass1, mass2) grid
- Aligns and length-matches templates to the conditioned strain without resampling
- Performs matched filtering, crops SNR edges, and extracts peak |SNR|
- Writes best result per approximant to a CSV with header: approximant,snr,total_mass

Usage example:
  python scripts/gw_matched_filter_grid.py \
    --data-file input.gwf \
    --channel H1:STRAIN \
    --approximant SEOBNRv4_opt --approximant IMRPhenomD --approximant TaylorT4 \
    --mass-min 10 --mass-max 40 --mass-step 1 \
    --f-low 20 --resample-rate 2048 \
    --hp-cutoff 15 --crop-sec 2 --psd-seg-len 4 --psd-trunc-sec 4 \
    --output results.csv

Note: Requires pycbc to be installed.
"""
import argparse
import csv
import math
from typing import Dict, Tuple, Optional

import numpy as np

try:
    from pycbc.frame import read_frame
    from pycbc.filter import highpass, resample_to_delta_t, matched_filter
    from pycbc.psd import interpolate, inverse_spectrum_truncation
    from pycbc.waveform import get_td_waveform
except Exception as e:
    raise SystemExit("PyCBC is required to run this script: pip install pycbc")


def parse_args():
    p = argparse.ArgumentParser(description="GW matched filtering grid search (PyCBC)")
    p.add_argument("--data-file", required=True, help="Path to frame (GWF) file")
    p.add_argument("--channel", required=True, help="Strain channel name in the frame")
    p.add_argument("--output", required=True, help="Output CSV path")

    p.add_argument("--approximant", action="append", required=True,
                   help="Waveform approximant (repeat for multiple)")

    p.add_argument("--mass-min", type=int, default=10)
    p.add_argument("--mass-max", type=int, default=40)
    p.add_argument("--mass-step", type=int, default=1)

    p.add_argument("--f-low", type=float, default=20.0, help="Low frequency cutoff (Hz)")
    p.add_argument("--hp-cutoff", type=float, default=15.0, help="Highpass cutoff (Hz)")
    p.add_argument("--resample-rate", type=float, default=2048.0, help="Target sample rate (Hz)")
    p.add_argument("--crop-sec", type=float, default=2.0, help="Seconds to crop off strain after conditioning (both ends)")

    p.add_argument("--psd-seg-len", type=float, default=4.0, help="PSD segment length (s)")
    p.add_argument("--psd-trunc-sec", type=float, default=4.0, help="Inverse spectrum truncation length (s)")

    p.add_argument("--crop-front-sec", type=float, default=None, help="Seconds to crop from start of SNR before peak finding")
    p.add_argument("--crop-back-sec", type=float, default=None, help="Seconds to crop from end of SNR before peak finding")

    p.add_argument("--progress-every", type=int, default=200, help="Print progress every N templates")
    p.add_argument("--no-enforce-ordered", action="store_true",
                   help="Do not enforce mass1 >= mass2 symmetry reduction")

    return p.parse_args()


def condition_strain(data_file: str, channel: str, hp_cutoff: float, resample_rate: float,
                     crop_sec: float, f_low: float, psd_seg_len: float, psd_trunc_sec: float):
    # Load raw strain
    strain = read_frame(data_file, channel)

    # Highpass filter
    strain = highpass(strain, hp_cutoff)

    # Resample to target delta_t
    delta_t = 1.0 / float(resample_rate)
    strain = resample_to_delta_t(strain, delta_t)

    # Crop edges to remove transients
    strain = strain.crop(crop_sec, crop_sec)

    # PSD estimation and stabilization
    psd = strain.psd(psd_seg_len)
    psd = interpolate(psd, strain.delta_f)
    psd = inverse_spectrum_truncation(
        psd,
        int(psd_trunc_sec * strain.sample_rate),
        low_frequency_cutoff=f_low,
    )

    return strain, psd


def generate_template(approximant: str, mass1: float, mass2: float, delta_t: float, f_low: float):
    # Generate time-domain template at the same delta_t as the conditioned strain
    hp, _ = get_td_waveform(
        approximant=approximant,
        mass1=mass1,
        mass2=mass2,
        delta_t=delta_t,
        f_lower=f_low,
        distance=1.0,
    )
    # Align template start to t=0 and return
    try:
        hp = hp.cyclic_time_shift(hp.start_time)
    except Exception:
        # Fallback: leave as-is if operation not available; matched_filter is shift-invariant in time
        pass
    return hp


def align_length(template, target_len: int):
    # Zero-pad or trim to match target length without changing delta_t
    if len(template) < target_len:
        # Pad at the end
        pad = target_len - len(template)
        template = template.append_zeros(pad)
    elif len(template) > target_len:
        template = template[:target_len]
    return template


def best_snr_for_family(approximant: str, strain, psd, f_low: float,
                        mass_min: int, mass_max: int, mass_step: int,
                        enforce_ordered: bool, crop_front_sec: float, crop_back_sec: float,
                        progress_every: int) -> Dict[str, Optional[float]]:
    best = {"snr": -math.inf, "mass1": None, "mass2": None}

    masses = list(range(mass_min, mass_max + 1, mass_step))
    total = len(masses) * len(masses)
    checked = 0

    for m1 in masses:
        for m2 in masses:
            if enforce_ordered and (m2 > m1):
                continue
            checked += 1
            if progress_every and (checked % progress_every == 0):
                print(f"{approximant}: {checked} templates checked", flush=True)
            try:
                tmpl = generate_template(approximant, float(m1), float(m2), strain.delta_t, f_low)
                tmpl = align_length(tmpl, len(strain))

                snr = matched_filter(tmpl, strain, psd=psd, low_frequency_cutoff=f_low)

                # Crop SNR edges before peak extraction
                snr = snr.crop(crop_front_sec, crop_back_sec)

                peak = float(np.max(np.abs(snr.numpy())))

                if peak > best["snr"]:
                    best["snr"] = peak
                    best["mass1"] = m1
                    best["mass2"] = m2
            except Exception:
                # Skip invalid/unavailable combos for this approximant
                continue

    return best


def main():
    args = parse_args()

    enforce_ordered = not args.no_enforce_ordered

    print("Conditioning strain...", flush=True)
    strain, psd = condition_strain(
        data_file=args.data_file,
        channel=args.channel,
        hp_cutoff=args.hp_cutoff,
        resample_rate=args.resample_rate,
        crop_sec=args.crop_sec,
        f_low=args.f_low,
        psd_seg_len=args.psd_seg_len,
        psd_trunc_sec=args.psd_trunc_sec,
    )

    # Default SNR crop if not provided explicitly
    crop_front_sec = args.crop_front_sec if args.crop_front_sec is not None else (2.0 * args.psd_trunc_sec)
    crop_back_sec = args.crop_back_sec if args.crop_back_sec is not None else (args.psd_trunc_sec)

    results = []
    for approx in args.approximant:
        print(f"Processing approximant: {approx}", flush=True)
        best = best_snr_for_family(
            approximant=approx,
            strain=strain,
            psd=psd,
            f_low=args.f_low,
            mass_min=args.mass_min,
            mass_max=args.mass_max,
            mass_step=args.mass_step,
            enforce_ordered=enforce_ordered,
            crop_front_sec=crop_front_sec,
            crop_back_sec=crop_back_sec,
            progress_every=args.progress_every,
        )
        if best["mass1"] is None:
            # No valid template found; record NaNs to keep output shape stable
            results.append({"approximant": approx, "snr": float("nan"), "total_mass": float("nan")})
        else:
            total_mass = int(best["mass1"]) + int(best["mass2"])
            results.append({
                "approximant": approx,
                "snr": round(float(best["snr"]), 3),
                "total_mass": total_mass,
            })

    with open(args.output, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["approximant", "snr", "total_mass"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Wrote results to {args.output}", flush=True)


if __name__ == "__main__":
    main()
