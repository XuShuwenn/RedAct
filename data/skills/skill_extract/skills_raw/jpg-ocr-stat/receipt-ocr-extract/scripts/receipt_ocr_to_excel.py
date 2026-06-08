#!/usr/bin/env python3
"""
Receipt OCR extraction: parse ISO date and final total from images and write a
single-sheet Excel report with deterministic formatting.

Usage:
  python3 receipt_ocr_to_excel.py --image-dir /path/to/images --out-xlsx /path/to/output.xlsx

Requirements:
  - Tesseract OCR installed
  - pytesseract, Pillow (PIL), openpyxl

Behavior:
  - Processes files with extensions .jpg/.jpeg/.png in lexicographic order
  - Writes Excel with a single sheet named "results"
  - Columns: filename, date, total_amount
  - date is ISO (YYYY-MM-DD) or None
  - total_amount is a string with exactly two decimals or None
"""

import argparse
import os
import re
from datetime import datetime
from typing import Optional

from PIL import Image, ImageOps
import pytesseract
from openpyxl import Workbook


# ----------------------------- OCR & Preprocessing -----------------------------

def preprocess_image(path: str, upsample_small: bool = True) -> Image.Image:
    img = Image.open(path)
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    if upsample_small:
        w, h = img.size
        if max(w, h) < 2000:
            img = img.resize((int(w * 2), int(h * 2)), Image.LANCZOS)
    return img


def ocr_text(path: str) -> str:
    img = preprocess_image(path)
    # PSM 6 works well for uniform blocks
    return pytesseract.image_to_string(img, config='--psm 6')


def ocr_text_date_focused(path: str) -> str:
    """Fallback OCR emphasizing digits and separators for dates."""
    img = preprocess_image(path)
    return pytesseract.image_to_string(
        img,
        config='--psm 6 -c tessedit_char_whitelist=0123456789/:-.'
    )


# ------------------------------- Date Extraction -------------------------------

def parse_date_from_text(text: str) -> Optional[str]:
    lines = text.split('\n')

    # Date patterns: DD/MM/YYYY, YYYY-MM-DD, DD.MM.YYYY, DD/MM/YY
    date_patterns = [
        (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'dmy4'),
        (r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', 'ymd4'),
        (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', 'dmy4'),
        (r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})(?!\d)', 'dmy2'),
    ]

    # Prefer lines that contain the word 'date'
    prioritized = [ln for ln in lines if 'date' in ln.lower()]
    prioritized += [ln for ln in lines if ln not in prioritized]

    for line in prioritized:
        for pat, fmt in date_patterns:
            m = re.search(pat, line)
            if not m:
                continue
            try:
                if fmt == 'ymd4':
                    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                elif fmt == 'dmy4':
                    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                else:  # dmy2
                    d, mo, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    y = 2000 + yy if yy < 100 else yy
                if 1 <= mo <= 12 and 1 <= d <= 31 and 1990 <= y <= 2100:
                    return datetime(y, mo, d).strftime('%Y-%m-%d')
            except Exception:
                continue

    # Fallback: extract YYYYMMDD from long numeric strings on lines that appear to be invoice-like
    for line in lines:
        if 'invoice' in line.lower():
            m = re.search(r'(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])', line)
            if m:
                try:
                    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    return datetime(y, mo, d).strftime('%Y-%m-%d')
                except Exception:
                    pass

    return None


# ------------------------------ Amount Extraction ------------------------------

EXCLUSION_KEYWORDS = [
    'SUBTOTAL', 'SUB TOTAL', 'SUB-TOTAL',
    'DISCOUNT', 'CHANGE', 'CASH TENDERED', 'TENDERED', 'CASH RECEIVED',
    'TOTAL GROSS', 'TOTAL QTY', 'TOT QTY', 'ITEM COUNT', 'EXCLUDING', 'EXCL', 'SAVINGS',
    'AMT EXCL', 'AMT. EXCL', 'TOTAL SAVINGS',
    'VISA', 'MASTER', 'MASTERCARD', 'DEBIT', 'CREDIT', 'PAYMENT'
]

# Allowlist to keep final total lines even if they contain tax words
ALLOWLIST_IF_EXCLUDED = [
    'TOTAL AFTER ADJ', 'TOTAL AFTER ROUNDING', 'TOTAL AMT ROUNDED', 'TOTAL ROUNDED',
    'TOTAL INCL', 'TOTAL INCLUSIVE', 'TOTAL SALES'
]

PRIORITY_KEYWORDS = [
    ['GRAND TOTAL'],
    ['TOTAL AFTER ADJ', 'TOTAL AFTER ROUNDING'],
    ['TOTAL INCL', 'TOTAL INCLUSIVE'],
    ['TOTAL AMT ROUNDED', 'TOTAL ROUNDED', 'NET TOTAL', 'NETT TOTAL'],
    ['TOTAL AMOUNT'],
    ['TOTAL (RM)', 'TOTAL(RM)'],
    ['TOTAL RM', 'TOTAL: RM'],
    ['TOTAL:', 'TOTAL '],
    ['TOTAL']
]

AMOUNT_STD_PATTERN = re.compile(r'[\d,]+\.[\d]{2}')


def normalize_line_for_amount(line: str) -> str:
    s = line
    # Remove currency markers
    s = re.sub(r'\b(RM|USD|MYR|\$)\b', '', s, flags=re.IGNORECASE)
    # Fix spaces around decimal point, e.g. "85. 54" -> "85.54"
    s = re.sub(r'(\d)\s*\.\s*(\d{2})(?!\d)', r'\1.\2', s)
    # Fix space instead of decimal at EOL, e.g. "538 00" -> "538.00"
    s = re.sub(r'(\d)\s+(\d{2})$', r'\1.\2', s)
    # Convert comma as decimal when no dot present, e.g. "99,80" -> "99.80"
    if '.' not in s:
        s = re.sub(r'(\d),(\d{2})(?!\d)', r'\1.\2', s)
    # Remove thousands separators if both comma and dot are present
    if ',' in s and '.' in s:
        s = s.replace(',', '')
    return s


def parse_amount_str(amount_str: str) -> Optional[str]:
    try:
        # Strip any thousand-separating commas
        clean = amount_str.replace(',', '')
        val = float(clean)
        if val > 0:
            return f"{val:.2f}"
    except Exception:
        pass
    return None


def find_amount_in_line(line: str) -> Optional[str]:
    s = normalize_line_for_amount(line)
    m = AMOUNT_STD_PATTERN.findall(s)
    if m:
        return parse_amount_str(m[-1])
    # Fallback: whole number at end, infer cents (e.g., 1000 -> 10.00)
    tail = re.search(r'(\d{3,4})\s*$', s.strip())
    if tail:
        digits = tail.group(1)
        try:
            cents = int(digits) % 100
            units = int(digits) // 100
            return f"{units}.{cents:02d}"
        except Exception:
            pass
    return None


def should_exclude(line_upper: str) -> bool:
    for kw in EXCLUSION_KEYWORDS:
        if kw in line_upper:
            return True
    return False


def allowed_despite_exclusion(line_upper: str) -> bool:
    for kw in ALLOWLIST_IF_EXCLUDED:
        if kw in line_upper:
            return True
    return False


def extract_total_amount(text: str) -> Optional[str]:
    lines = text.split('\n')

    for keyword_group in PRIORITY_KEYWORDS:
        for i, raw_line in enumerate(lines):
            line_upper = raw_line.upper()
            if not any(k in line_upper for k in keyword_group):
                continue

            # Skip excluded contexts unless allowlisted
            if should_exclude(line_upper) and not allowed_despite_exclusion(line_upper):
                continue

            amt = find_amount_in_line(raw_line)
            if amt:
                return amt
            # Fallback: next line
            if i + 1 < len(lines):
                nxt = lines[i + 1]
                if not (should_exclude(nxt.upper()) and not allowed_despite_exclusion(nxt.upper())):
                    amt = find_amount_in_line(nxt)
                    if amt:
                        return amt
    return None


# --------------------------------- IO & Report --------------------------------

def process_image(path: str) -> tuple[str | None, str | None]:
    text = ocr_text(path)
    date = parse_date_from_text(text)
    if date is None:
        # Try date-focused OCR if necessary
        text2 = ocr_text_date_focused(path)
        date = parse_date_from_text(text2)
    total = extract_total_amount(text)
    return date, total


def write_excel(rows: list[dict], out_path: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = 'results'
    # Header
    ws.append(['filename', 'date', 'total_amount'])
    for r in rows:
        # Ensure total_amount is a string when present
        ta = r['total_amount']
        if ta is not None:
            ta = str(ta)
        ws.append([r['filename'], r['date'], ta])
    wb.save(out_path)


def main():
    ap = argparse.ArgumentParser(description='Receipt OCR extractor to Excel')
    ap.add_argument('--image-dir', required=True, help='Directory of receipt images')
    ap.add_argument('--out-xlsx', required=True, help='Output Excel file path')
    args = ap.parse_args()

    # Collect files
    files = [f for f in os.listdir(args.image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    files.sort()

    rows = []
    for fname in files:
        fpath = os.path.join(args.image_dir, fname)
        date, total = process_image(fpath)
        rows.append({'filename': fname, 'date': date, 'total_amount': total})

    write_excel(rows, args.out_xlsx)


if __name__ == '__main__':
    main()
