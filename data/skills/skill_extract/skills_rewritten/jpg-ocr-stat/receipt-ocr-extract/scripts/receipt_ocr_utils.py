#!/usr/bin/env python3
"""Receipt OCR utilities: text extraction, date parsing, and final total detection.

This module provides reusable functions for:
- OCR-ing an image path into text (with light preprocessing)
- Parsing an ISO date (YYYY-MM-DD) from free text
- Extracting the final total amount as a two-decimal string from text lines

No dataset-specific constants are included.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional, List, Tuple

try:
    from PIL import Image, ImageOps, ImageFilter
except Exception:
    Image = None  # PIL not required for the parsing helpers

try:
    import pytesseract
except Exception:
    pytesseract = None


# Prioritized total label groups (highest first). Customize as needed per project.
PRIORITY_LABEL_GROUPS: List[List[str]] = [
    ["GRAND TOTAL"],
    ["TOTAL RM", "TOTAL: RM"],
    ["TOTAL AMOUNT"],
    ["TOTAL DUE", "AMOUNT DUE", "BALANCE DUE", "NETT TOTAL", "NET TOTAL", "TOTAL", "AMOUNT"],
]

# Exclusion labels commonly not the final total
EXCLUDE_LABELS: List[str] = [
    "SUBTOTAL", "SUB TOTAL", "TAX", "GST", "SST", "DISCOUNT", "CHANGE", "CASH TENDERED",
]

# Currency marker patterns to slightly boost confidence when present
CURRENCY_MARKERS: List[str] = ["RM", "$", "USD", "MYR", "SGD", "EUR", "GBP"]

# Numeric patterns for amounts (allow thousands separators and optional decimal)
# We'll parse the last plausible number on a line.
AMOUNT_TOKEN = re.compile(r"(?<![A-Za-z0-9])(\d{1,3}(?:[\s,]\d{3})+|\d+)(?:\.(\d{1,2}))?(?![A-Za-z0-9])")

# Month names for textual dates
MONTHS = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9, 'SEPT': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}

# Date regex patterns (capture groups will be interpreted in code)
RE_YMD = re.compile(r"\b(\d{4})[\-/](\d{1,2})[\-/](\d{1,2})\b")  # YYYY-MM-DD or YYYY/MM/DD
RE_DMY = re.compile(r"\b(\d{1,2})[\-/](\d{1,2})[\-/](\d{2,4})\b")  # DD/MM/YYYY or DD-MM-YY
RE_TEXTUAL = re.compile(r"\b(\d{1,2})\s*([A-Za-z]{3,4})\s*(\d{4})\b")  # D Mon YYYY
RE_COMPACT8 = re.compile(r"\b(\d{8})\b")  # YYYYMMDD or DDMMYYYY


def ocr_image(image_path: str, psm: int = 6) -> str:
    """OCR an image file path into text using Tesseract with light preprocessing.

    Parameters:
        image_path: Path to the image file
        psm: Tesseract page segmentation mode (default 6)

    Returns:
        Extracted text (str). If PIL/pytesseract unavailable, returns empty string.
    """
    if Image is None or pytesseract is None:
        return ""

    img = Image.open(image_path)
    # Light preprocessing: grayscale + auto-contrast + slight sharpening
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    config = f"--psm {psm} -l eng"
    try:
        text = pytesseract.image_to_string(img, config=config)
    except Exception:
        text = ""
    return text


def normalize_text(text: str) -> str:
    """Normalize OCR text for parsing: unify case, trim trailing spaces, normalize spaces.

    - Converts to uppercase for label matching.
    - Normalizes multiple spaces to a single space on a per-line basis.
    """
    lines = []
    for raw in text.splitlines():
        # Strip non-breaking spaces and normalize spacing
        ln = raw.replace('\u00A0', ' ').strip()
        ln = re.sub(r"\s+", " ", ln)
        lines.append(ln)
    return "\n".join(lines).upper()


def _safe_date(y: int, m: int, d: int) -> Optional[datetime]:
    try:
        return datetime(y, m, d)
    except Exception:
        return None


def find_date_iso(text: str) -> Optional[str]:
    """Find a plausible date in the text and return ISO format (YYYY-MM-DD), else None.

    Search order:
    1) YYYY-MM-DD or YYYY/MM/DD
    2) DD/MM/YYYY or DD-MM-YY(YY) with disambiguation
    3) D Mon YYYY (e.g., 3 JAN 2019)
    4) Compact 8 digits: YYYYMMDD preferred; else DDMMYYYY if valid
    """
    t = normalize_text(text)

    # 1) YYYY-MM-DD (or /)
    for y, m, d in RE_YMD.findall(t):
        dt = _safe_date(int(y), int(m), int(d))
        if dt:
            return dt.strftime('%Y-%m-%d')

    # 2) DD/MM/YYYY or DD-MM-YY(YY)
    for d, m, y in RE_DMY.findall(t):
        yi = int(y)
        if len(y) == 2:
            yi += 2000 if yi < 70 else 1900
        # Try DMY, then MDY if DMY invalid
        dt = _safe_date(yi, int(m), int(d))
        if not dt:
            dt = _safe_date(yi, int(d), int(m))
        if dt:
            return dt.strftime('%Y-%m-%d')

    # 3) D Mon YYYY
    for d, mon, y in RE_TEXTUAL.findall(t):
        mon_num = MONTHS.get(mon[:3].upper())
        if mon_num:
            dt = _safe_date(int(y), mon_num, int(d))
            if dt:
                return dt.strftime('%Y-%m-%d')

    # 4) Compact 8: try YYYYMMDD then DDMMYYYY
    for s in RE_COMPACT8.findall(t):
        y, m, d = int(s[:4]), int(s[4:6]), int(s[6:])
        dt = _safe_date(y, m, d)
        if dt:
            return dt.strftime('%Y-%m-%d')
        d2, m2, y2 = int(s[:2]), int(s[2:4]), int(s[4:])
        dt = _safe_date(y2, m2, d2)
        if dt:
            return dt.strftime('%Y-%m-%d')

    return None


def _label_priority(line_upper: str) -> Tuple[int, Optional[str]]:
    """Return (priority_index, matched_label) for the first matched label group; lower index = higher priority.
    If no label matched, returns (len(PRIORITY_LABEL_GROUPS)+1, None).
    """
    for idx, group in enumerate(PRIORITY_LABEL_GROUPS):
        for label in group:
            if label in line_upper:
                return idx, label
    return len(PRIORITY_LABEL_GROUPS) + 1, None


def _has_exclusion(line_upper: str) -> bool:
    return any(ex in line_upper for ex in EXCLUDE_LABELS)


def _currency_boost(line_upper: str) -> int:
    return 1 if any(cur in line_upper for cur in CURRENCY_MARKERS) else 0


def _format_two_decimals(num_str: str) -> Optional[str]:
    """Normalize a numeric string to two decimal places.
    - Remove spaces and commas
    - If decimal present with 1 digit, pad to 2; if none, add .00
    - Reject if not numeric after cleanup
    """
    s = re.sub(r"[ ,]", "", num_str)
    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", s):
        return None
    if "." in s:
        whole, frac = s.split(".")
        if len(frac) == 1:
            frac = frac + "0"
        elif len(frac) == 2:
            pass
        else:
            frac = frac[:2]
        return f"{int(whole)}.{frac}"
    else:
        return f"{int(s)}.00"


def _inject_decimal_if_plausible(num_str: str) -> Optional[str]:
    """When OCR drops the decimal (e.g., '2000' for 20.00), infer cents by inserting
    a decimal before the last two digits. Only applies to 3+ digit integers.
    """
    s = re.sub(r"[ ,]", "", num_str)
    if not s.isdigit() or len(s) < 3:
        return None
    whole, cents = s[:-2], s[-2:]
    try:
        return f"{int(whole)}.{cents}"
    except Exception:
        return None


def _last_amount_token(line: str) -> Optional[str]:
    """Return the last numeric token from a line as text, if any."""
    matches = list(AMOUNT_TOKEN.finditer(line))
    if not matches:
        return None
    m = matches[-1]
    num = m.group(0)
    return num


def find_final_total(lines: List[str]) -> Optional[str]:
    """Find the final total amount from OCR text lines.

    Strategy:
    - Iterate lines; skip those with exclusion labels.
    - Score candidates by label priority, currency marker boost, and position.
    - For labeled lines, parse amount on the same line or next non-empty line.
    - Normalize to two decimals; if integer-like without decimal, consider inserting a decimal before last two digits for high-confidence labels.
    - Return the best candidate as a two-decimal string.
    """
    candidates: List[Tuple[int, int, str]] = []  # (score, position, amount)
    total_groups = len(PRIORITY_LABEL_GROUPS)

    # Work with uppercase copies for labels but keep original for numeric tokens
    upper_lines = [ln.upper() for ln in lines]

    for i, (ln_u, ln) in enumerate(zip(upper_lines, lines)):
        if _has_exclusion(ln_u):
            continue
        pr_idx, matched_label = _label_priority(ln_u)
        if matched_label is None:
            continue
        # Find amount on the same line
        amt_raw = _last_amount_token(ln)
        # If not found, look at the next non-empty line
        if not amt_raw:
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and not _has_exclusion(upper_lines[j]):
                amt_raw = _last_amount_token(lines[j])
        if not amt_raw:
            continue

        # Normalize amount
        amt_norm = _format_two_decimals(amt_raw)
        if not amt_norm:
            # Consider inserting decimal when strong label (top 2 groups)
            if pr_idx <= 1:
                inferred = _inject_decimal_if_plausible(amt_raw)
                if inferred:
                    amt_norm = _format_two_decimals(inferred)
        if not amt_norm:
            continue

        # Score: higher for higher-priority labels and later positions
        # Convert priority to a score; lower index => higher score
        base = (total_groups - pr_idx) * 10
        pos_bonus = min(i, 50)  # prefer later lines modestly
        cur_bonus = _currency_boost(ln_u)
        score = base + pos_bonus + cur_bonus
        candidates.append((score, i, amt_norm))

    if not candidates:
        return None

    candidates.sort(key=lambda x: (x[0], x[1]))
    best = candidates[-1]
    return best[2]


def text_to_lines(text: str) -> List[str]:
    """Split normalized text into non-empty lines, preserving original characters for number parsing."""
    lines = []
    for raw in text.splitlines():
        if raw is None:
            continue
        ln = raw.strip()
        if ln:
            lines.append(ln)
    return lines


if __name__ == "__main__":
    # Simple manual test harness when run standalone (no I/O paths embedded)
    sample = (
        "Date: 23-01-2019\n"
        "SUBTOTAL: 18.87\n"
        "GST: 1.13\n"
        "GRAND TOTAL : 20.00\n"
    )
    iso = find_date_iso(sample)
    amt = find_final_total(text_to_lines(sample))
    print({"date": iso, "total": amt})
