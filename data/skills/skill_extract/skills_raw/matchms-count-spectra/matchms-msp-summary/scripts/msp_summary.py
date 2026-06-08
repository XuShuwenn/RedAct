#!/usr/bin/env python3
"""Summarize an MSP file using matchms: count spectra, find the spectrum with
most peaks, and sum total peaks. Includes robust fallbacks for empty or
unparsable files.

Usage:
  python msp_summary.py INPUT.msp [--output OUTPUT.txt] [--name-key compound_name]

Output format (default):
  Total spectra: N
  Spectrum with most peaks: NAME (K peaks)
  Total peaks across all spectra: M

Exit codes:
  0 on success (including fallback summary when input is empty/unparsable)
  1 on write failure or invalid CLI usage
"""

import argparse
import sys
from typing import Dict, Any

try:
    from matchms.importing import load_from_msp
except Exception as e:
    print("ERROR: matchms is required: pip install matchms", file=sys.stderr)
    sys.exit(1)


def safe_len_peaks(spectrum) -> int:
    """Return number of peaks for a spectrum, or 0 if unavailable."""
    try:
        p = getattr(spectrum, "peaks", None)
        if p is None:
            return 0
        mz = getattr(p, "mz", None)
        if mz is None:
            return 0
        return len(mz)
    except Exception:
        return 0


def get_spectrum_name(spectrum, preferred_key: str = "compound_name") -> str:
    """Resolve spectrum name with reasonable fallbacks.
    Tries: preferred_key -> 'compound_name' -> 'name' -> 'Unknown'.
    """
    keys = [preferred_key, "compound_name", "name"]
    for k in keys:
        val = None
        # Try Spectrum.get if available
        try:
            val = spectrum.get(k)
        except Exception:
            val = None
        # Try metadata dict if present
        if not val:
            try:
                meta = getattr(spectrum, "metadata", None)
                if isinstance(meta, dict):
                    val = meta.get(k)
            except Exception:
                pass
        if val:
            return str(val)
    return "Unknown"


def summarize_msp(path: str, name_key: str = "compound_name") -> Dict[str, Any]:
    """Summarize an MSP file. Returns a dict with counts and status.

    Keys: ok, total_spectra, top_name, top_peaks, total_peaks, (optional) error
    """
    total_spectra = 0
    total_peaks = 0
    max_peaks = -1
    top_name = "N/A"

    try:
        for spectrum in load_from_msp(path):
            total_spectra += 1
            peaks = safe_len_peaks(spectrum)
            total_peaks += peaks
            if peaks > max_peaks:
                max_peaks = peaks
                top_name = get_spectrum_name(spectrum, preferred_key=name_key)
    except Exception as e:
        return {
            "ok": False,
            "total_spectra": 0,
            "top_name": "N/A",
            "top_peaks": 0,
            "total_peaks": 0,
            "error": str(e),
        }

    if total_spectra == 0:
        return {
            "ok": True,
            "total_spectra": 0,
            "top_name": "N/A",
            "top_peaks": 0,
            "total_peaks": 0,
        }

    return {
        "ok": True,
        "total_spectra": total_spectra,
        "top_name": top_name,
        "top_peaks": max(max_peaks, 0),
        "total_peaks": total_peaks,
    }


def format_summary(summary: Dict[str, Any]) -> str:
    """Format summary as three lines with a trailing newline."""
    return (
        f"Total spectra: {summary['total_spectra']}\n"
        f"Spectrum with most peaks: {summary['top_name']} ({summary['top_peaks']} peaks)\n"
        f"Total peaks across all spectra: {summary['total_peaks']}\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize MSP with matchms")
    ap.add_argument("input", help="Path to input MSP file")
    ap.add_argument("--output", help="Optional path to write the summary")
    ap.add_argument("--name-key", default="compound_name", help="Metadata key to use for spectrum name (default: compound_name)")
    args = ap.parse_args()

    summary = summarize_msp(args.input, name_key=args.name_key)
    text = format_summary(summary)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(text)

    # Note: even if parsing failed, we wrote fallback lines; exit 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
