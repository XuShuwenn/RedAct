#!/usr/bin/env python3
"""
Invoice Fraud Auditing Toolkit

- Extract invoice data from a PDF (1 invoice per page)
- Normalize and fuzzy-match vendor names
- Cross-validate IBAN and purchase orders
- Emit JSON of only the flagged invoices with prioritized reasons

CLI example:
  python3 scripts/invoice_fraud_toolkit.py \
    --pdf /root/invoices.pdf \
    --vendors /root/vendors.xlsx \
    --pos /root/purchase_orders.csv \
    --out /root/fraud_report.json \
    --fuzzy-threshold 0.8 --fuzzy-method token

Dependencies: pdfplumber, pandas
"""
import argparse
import json
import math
import os
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple

# Optional imports with helpful errors
try:
    import pdfplumber
except Exception as e:  # pragma: no cover
    pdfplumber = None

try:
    import pandas as pd
except Exception as e:  # pragma: no cover
    pd = None

# ---------------------------
# Normalization & Fuzzy Match
# ---------------------------
_SUFFIX_MAP = {
    "limited": "ltd",
    "incorporated": "inc",
    "corporation": "corp",
    "company": "co",
}

_NONWORD_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_WS_RE = re.compile(r"\s+")


def normalize_vendor_name(name: str) -> str:
    if not name:
        return ""
    s = name.strip().lower()
    s = _NONWORD_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    for src, dst in _SUFFIX_MAP.items():
        s = s.replace(src, dst)
    return s


def _token_set_string(s: str) -> str:
    tokens = [t for t in _WS_RE.split(normalize_vendor_name(s)) if t]
    uniq = sorted(set(tokens))
    return " ".join(uniq)


def similarity(a: str, b: str, method: str = "sequence") -> float:
    """Return similarity in [0,1]. Uses difflib ratio on normalized strings.
    method: 'sequence' (normalized full string) or 'token' (token-set style).
    """
    from difflib import SequenceMatcher

    if method == "token":
        a_norm = _token_set_string(a)
        b_norm = _token_set_string(b)
    else:
        a_norm = normalize_vendor_name(a)
        b_norm = normalize_vendor_name(b)

    if not a_norm and not b_norm:
        return 1.0
    return SequenceMatcher(None, a_norm, b_norm).ratio()


def fuzzy_match_vendor(invoice_vendor: str, vendor_names: List[str], threshold: float = 0.8, method: str = "sequence") -> Optional[str]:
    if not invoice_vendor:
        return None

    # Case-insensitive exact
    low = invoice_vendor.lower().strip()
    for v in vendor_names:
        if v.lower().strip() == low:
            return v

    # Normalized exact
    inv_norm = normalize_vendor_name(invoice_vendor)
    for v in vendor_names:
        if normalize_vendor_name(v) == inv_norm:
            return v

    # Best fuzzy
    best_name, best_score = None, 0.0
    for v in vendor_names:
        score = similarity(invoice_vendor, v, method=method)
        if score > best_score:
            best_score, best_name = score, v
    if best_score >= float(threshold):
        return best_name
    return None

# ---------------------------
# Data Loading & Column Mapping
# ---------------------------

_DEF_VENDOR_ID_KEYS = ("id", "vendor_id", "vendor id")
_DEF_VENDOR_NAME_KEYS = ("name", "vendor_name", "vendor name")
_DEF_VENDOR_IBAN_KEYS = ("iban", "authorized_iban", "authorized iban")

_DEF_PO_NUMBER_KEYS = ("po_number", "po", "po number", "po no")
_DEF_PO_VENDOR_ID_KEYS = ("vendor_id", "vendor id", "id")
_DEF_PO_AMOUNT_KEYS = ("amount", "total", "po_amount")


def _canon(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower()).replace("-", " ").replace("_", " ")


def _find_col(df, candidates: Tuple[str, ...]) -> Optional[str]:
    cols = list(df.columns)
    by_canon = { _canon(c): c for c in cols }
    for cand in candidates:
        if cand in by_canon:
            return by_canon[cand]
    # fallback: token containment
    for c in cols:
        ccan = _canon(c)
        for cand in candidates:
            toks = cand.split()
            if all(t in ccan for t in toks):
                return c
    return None


def load_table(path: str):
    if pd is None:  # pragma: no cover
        raise RuntimeError("pandas is required to load tables")
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm", ".xltx", ".xltm"):
        return pd.read_excel(path)
    elif ext in (".csv", ".tsv"):
        sep = "," if ext == ".csv" else "\t"
        return pd.read_csv(path, sep=sep)
    else:
        # try csv by default
        return pd.read_csv(path)


def build_vendor_index(vendors_df) -> Dict[str, Dict[str, str]]:
    id_col = _find_col(vendors_df, _DEF_VENDOR_ID_KEYS)
    name_col = _find_col(vendors_df, _DEF_VENDOR_NAME_KEYS)
    iban_col = _find_col(vendors_df, _DEF_VENDOR_IBAN_KEYS)
    if not (id_col and name_col and iban_col):
        raise ValueError("Unable to detect vendor columns (id/name/iban)")

    index = {
        "name_to_id": {},
        "name_to_iban": {},
        "id_to": {},
        "names": [],
    }
    for _, row in vendors_df.iterrows():
        vid = str(row[id_col]).strip()
        vname = str(row[name_col]).strip()
        vib = str(row[iban_col]).strip()
        if not vname:
            continue
        index["name_to_id"][vname] = vid
        index["name_to_iban"][vname] = vib
        index["id_to"][vid] = {"name": vname, "iban": vib}
        index["names"].append(vname)
    return index


def _to_decimal(v) -> Optional[Decimal]:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    s = str(v).strip().replace(",", "")
    if not s:
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def build_po_index(po_df) -> Dict[str, Dict[str, str]]:
    po_col = _find_col(po_df, _DEF_PO_NUMBER_KEYS)
    vid_col = _find_col(po_df, _DEF_PO_VENDOR_ID_KEYS)
    amt_col = _find_col(po_df, _DEF_PO_AMOUNT_KEYS)
    if not (po_col and vid_col and amt_col):
        raise ValueError("Unable to detect PO columns (po_number/vendor_id/amount)")

    lookup = {}
    for _, row in po_df.iterrows():
        po = str(row[po_col]).strip()
        vid = str(row[vid_col]).strip()
        amt = _to_decimal(row[amt_col])
        if not po:
            continue
        lookup[po] = {"vendor_id": vid, "amount": amt}
    return lookup

# ---------------------------
# PDF Parsing
# ---------------------------
_VENDOR_RE = re.compile(r"^\s*From:\s*(.+)$", re.MULTILINE)
_AMOUNT_RE = re.compile(r"Total\s*\$?([0-9][0-9,]*\.?\d*)")
_IBAN_RE = re.compile(r"Payment\s+IBAN:\s*(\S+)")
_PO_RE = re.compile(r"PO\s*Number:\s*(\S+)")


def parse_invoices_from_pdf(pdf_path: str, invalid_po_tokens: Optional[List[str]] = None) -> List[dict]:
    if pdfplumber is None:  # pragma: no cover
        raise RuntimeError("pdfplumber is required to parse PDFs")

    invalid_set = set([t.strip() for t in (invalid_po_tokens or ["PO-INVALID"]) if t])

    invoices: List[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            vendor = None
            amount = None
            iban = None
            po = None

            m = _vendor_re_search(text)
            if m:
                vendor = m.group(1).strip()

            m = _AMOUNT_RE.search(text)
            if m:
                amount = _to_decimal(m.group(1))

            m = _IBAN_RE.search(text)
            if m:
                iban = m.group(1).strip()

            m = _PO_RE.search(text)
            if m:
                raw_po = m.group(1).strip()
                po = raw_po if raw_po and raw_po not in invalid_set else None

            invoices.append({
                "invoice_page_number": i,
                "vendor_name": vendor,
                "invoice_amount": amount,
                "iban": iban,
                "po_number": po,
            })
    return invoices


def _vendor_re_search(text: str):
    # Try several variants to be robust
    m = _VENDOR_RE.search(text)
    if m:
        return m
    alt = re.search(r"Vendor\s*:\s*(.+)", text)
    return alt

# ---------------------------
# Fraud Rules
# ---------------------------
_ALLOWED_REASONS = (
    "Unknown Vendor",
    "IBAN Mismatch",
    "Invalid PO",
    "Amount Mismatch",
    "Vendor Mismatch",
)


def apply_fraud_rules(
    invoices: List[dict],
    vendor_index: Dict[str, Dict[str, str]],
    po_index: Dict[str, Dict[str, str]],
    fuzzy_threshold: float = 0.8,
    fuzzy_method: str = "sequence",
) -> List[dict]:
    names = vendor_index.get("names", [])
    name_to_id = vendor_index.get("name_to_id", {})
    name_to_iban = vendor_index.get("name_to_iban", {})

    results = []
    for inv in invoices:
        page = inv.get("invoice_page_number")
        vendor_name = inv.get("vendor_name")
        amount = inv.get("invoice_amount")
        iban = inv.get("iban")
        po = inv.get("po_number")

        reason = None
        matched_vendor = None

        # 1) Unknown Vendor
        matched_vendor = fuzzy_match_vendor(vendor_name or "", names, threshold=fuzzy_threshold, method=fuzzy_method)
        if matched_vendor is None:
            reason = "Unknown Vendor"
        else:
            # 2) IBAN Mismatch (only if both registry IBAN and invoice IBAN present and unequal)
            expected_iban = name_to_iban.get(matched_vendor)
            if expected_iban and iban and iban != expected_iban:
                reason = "IBAN Mismatch"
            # 3) Invalid PO
            elif po is None or po not in po_index:
                reason = "Invalid PO"
            else:
                po_data = po_index[po]
                # 4) Amount Mismatch (> 0.01)
                po_amt = po_data.get("amount")
                if isinstance(amount, Decimal) and isinstance(po_amt, Decimal):
                    if (amount - po_amt).copy_abs() > Decimal("0.01"):
                        reason = "Amount Mismatch"
                else:
                    # Fallback with float (avoid if possible)
                    try:
                        a = float(amount) if amount is not None else None
                        b = float(po_amt) if po_amt is not None else None
                        if a is None or b is None or abs(a - b) > 0.01:
                            reason = "Amount Mismatch"
                    except Exception:
                        reason = "Amount Mismatch"
                # 5) Vendor Mismatch (by ID)
                if reason is None:
                    po_vid = po_data.get("vendor_id")
                    matched_vid = name_to_id.get(matched_vendor)
                    if matched_vid != po_vid:
                        reason = "Vendor Mismatch"

        if reason:
            out_po = po
            if reason == "Invalid PO":
                out_po = None
            results.append({
                "invoice_page_number": page,
                "vendor_name": vendor_name,
                "invoice_amount": float(amount) if isinstance(amount, Decimal) else amount,
                "iban": iban,
                "po_number": out_po,
                "reason": reason,
            })
    return results

# ---------------------------
# CLI
# ---------------------------

def main():
    ap = argparse.ArgumentParser(description="Invoice Fraud Auditing Toolkit")
    ap.add_argument("--pdf", required=True, help="Path to invoices PDF")
    ap.add_argument("--vendors", required=True, help="Path to vendors registry (Excel/CSV)")
    ap.add_argument("--pos", required=True, help="Path to purchase orders registry (CSV/Excel)")
    ap.add_argument("--out", required=True, help="Output JSON path for flagged invoices")
    ap.add_argument("--fuzzy-threshold", type=float, default=0.8, help="Fuzzy match threshold [0-1]")
    ap.add_argument("--fuzzy-method", choices=["sequence", "token"], default="token", help="Fuzzy match method")
    ap.add_argument("--invalid-po-token", action="append", default=["PO-INVALID"], help="PO tokens considered invalid (repeatable)")
    args = ap.parse_args()

    if pdfplumber is None:
        raise RuntimeError("Missing dependency: pdfplumber")
    if pd is None:
        raise RuntimeError("Missing dependency: pandas")

    # Load registries
    vendors_df = load_table(args.vendors)
    po_df = load_table(args.pos)

    vendor_index = build_vendor_index(vendors_df)
    po_index = build_po_index(po_df)

    # Extract and parse invoices
    invoices = parse_invoices_from_pdf(args.pdf, invalid_po_tokens=args.invalid_po_token)

    # Apply rules
    flagged = apply_fraud_rules(
        invoices,
        vendor_index,
        po_index,
        fuzzy_threshold=args.fuzzy_threshold,
        fuzzy_method=args.fuzzy_method,
    )

    # Validate reasons and types
    for entry in flagged:
        assert entry["reason"] in _ALLOWED_REASONS, f"Invalid reason: {entry['reason']}"
        assert isinstance(entry["invoice_page_number"], int), "Page number must be 1-based int"

    # Save
    with open(args.out, "w") as f:
        json.dump(flagged, f, indent=2)

    print(f"Flagged invoices: {len(flagged)} -> {args.out}")


if __name__ == "__main__":
    main()
