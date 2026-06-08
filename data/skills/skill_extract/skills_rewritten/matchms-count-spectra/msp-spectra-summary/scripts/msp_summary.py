#!/usr/bin/env python3
"""Summarize an MSP file:
- Count total spectra
- Find the spectrum with the most peaks
- Compute total peaks across all spectra

Exact output format (three lines):
  Total spectra: N
  Spectrum with most peaks: NAME (K peaks)
  Total peaks across all spectra: M

Fallback (for empty or unparsable input):
  Total spectra: 0
  Spectrum with most peaks: N/A (0 peaks)
  Total peaks across all spectra: 0

Usage:
  python msp_summary.py --input input.msp --output output.txt
  python msp_summary.py --input input.msp --stdout
  python msp_summary.py --validate-output output.txt
"""

from __future__ import annotations
import argparse
import os
import re
import sys
from typing import Iterable, Tuple


def _try_import_matchms():
    try:
        from matchms.importing import load_from_msp  # type: ignore
        return load_from_msp
    except Exception:
        return None


def _count_peaks(spectrum) -> int:
    """Robustly count peaks from a matchms Spectrum object across versions.
    Prefers spectrum.peaks.mz if available. Falls back to len(spectrum.peaks).
    Returns 0 if peaks are unavailable or on any error.
    """
    try:
        p = getattr(spectrum, "peaks", None)
        if p is not None:
            # matchms typically exposes Peaks with .mz and .intensities
            mz = getattr(p, "mz", None)
            if mz is not None:
                try:
                    return len(mz)  # numpy array or list
                except Exception:
                    pass
            # Fallback: peaks might be list-like of (mz, intensity)
            try:
                return len(p)
            except Exception:
                return 0
        # Older or non-standard spectra may expose .mz or .intensities directly
        mz = getattr(spectrum, "mz", None)
        if mz is not None:
            try:
                return len(mz)
            except Exception:
                return 0
        intensities = getattr(spectrum, "intensities", None)
        if intensities is not None:
            try:
                return len(intensities)
            except Exception:
                return 0
        return 0
    except Exception:
        return 0


def _get_name(spectrum) -> str:
    """Get a display name for the spectrum from common metadata keys.
    Returns 'N/A' if no suitable name is available.
    """
    # matchms spectra usually support .get(key) for metadata
    keys = ("name", "compound_name", "spectrum_id")
    for k in keys:
        try:
            if hasattr(spectrum, "get"):
                v = spectrum.get(k)
            else:
                meta = getattr(spectrum, "metadata", None)
                v = meta.get(k) if isinstance(meta, dict) else None
        except Exception:
            v = None
        if v:
            return str(v)
    return "N/A"


def summarize_msp(input_path: str) -> Tuple[int, str, int, int]:
    """Parse MSP and compute summary.

    Returns a 4-tuple: (total_spectra, most_peaks_name, most_peaks_count, total_peaks)

    On any parsing problem or empty file, returns (0, 'N/A', 0, 0).
    """
    # Check file existence and non-empty size early
    if not input_path or not os.path.isfile(input_path):
        return (0, "N/A", 0, 0)
    try:
        if os.path.getsize(input_path) == 0:
            return (0, "N/A", 0, 0)
    except Exception:
        return (0, "N/A", 0, 0)

    load_from_msp = _try_import_matchms()
    if load_from_msp is None:
        return (0, "N/A", 0, 0)

    total_spectra = 0
    total_peaks = 0
    most_peaks = 0
    most_peaks_name = "N/A"

    try:
        spectra_iter = load_from_msp(input_path)
        for spectrum in spectra_iter:
            total_spectra += 1
            pk = _count_peaks(spectrum)
            total_peaks += int(pk)
            if pk > most_peaks:
                most_peaks = int(pk)
                most_peaks_name = _get_name(spectrum)
    except Exception:
        # Any parsing error triggers fallback
        return (0, "N/A", 0, 0)

    if total_spectra == 0:
        return (0, "N/A", 0, 0)

    return (total_spectra, most_peaks_name or "N/A", most_peaks, total_peaks)


def write_summary(output_path: str, total: int, top_name: str, top_peaks: int, total_peaks: int) -> None:
    lines = [
        f"Total spectra: {int(total)}",
        f"Spectrum with most peaks: {top_name if top_name else 'N/A'} ({int(top_peaks)} peaks)",
        f"Total peaks across all spectra: {int(total_peaks)}",
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def validate_output_format(text: str) -> bool:
    """Validate that text matches the exact three-line summary format."""
    lines = text.strip().splitlines()
    if len(lines) != 3:
        return False
    pat1 = re.compile(r"^Total spectra: \d+$")
    pat2 = re.compile(r"^Spectrum with most peaks: .+ \(\d+ peaks\)$")
    pat3 = re.compile(r"^Total peaks across all spectra: \d+$")
    return bool(pat1.match(lines[0]) and pat2.match(lines[1]) and pat3.match(lines[2]))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize MSP spectra with matchms")
    parser.add_argument("--input", help="Path to input MSP file")
    parser.add_argument("--output", help="Path to write summary output file")
    parser.add_argument("--stdout", action="store_true", help="Print summary to stdout instead of writing a file")
    parser.add_argument("--validate-output", metavar="PATH", help="Validate an existing output file's format and exit")

    args = parser.parse_args(list(argv) if argv is not None else None)

    # Standalone validation mode
    if args.validate_output:
        try:
            with open(args.validate_output, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"ERROR: Cannot read file for validation: {e}", file=sys.stderr)
            return 2
        ok = validate_output_format(content)
        print("VALID" if ok else "INVALID")
        return 0 if ok else 1

    if not args.input:
        print("ERROR: --input is required", file=sys.stderr)
        return 2

    total, name, k, total_pk = summarize_msp(args.input)

    if args.stdout and not args.output:
        print(f"Total spectra: {total}")
        print(f"Spectrum with most peaks: {name} ({k} peaks)")
        print(f"Total peaks across all spectra: {total_pk}")
        return 0

    if not args.output:
        print("ERROR: --output is required (or use --stdout)", file=sys.stderr)
        return 2

    try:
        write_summary(args.output, total, name, k, total_pk)
    except Exception as e:
        print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
