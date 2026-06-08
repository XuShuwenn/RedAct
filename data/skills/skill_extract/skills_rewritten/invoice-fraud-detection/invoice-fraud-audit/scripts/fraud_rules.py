#!/usr/bin/env python3
"""
Reusable normalization, fuzzy vendor matching, and fraud-rule evaluation for invoice audits.

This module does NOT parse PDFs or spreadsheets. It expects:
- invoices: dicts with keys: vendor_name (str), invoice_amount (Decimal|float|str), iban (str|None), po_number (str|None)
- vendors: list of dicts with keys: vendor_id (str), vendor_name (str), iban (str)
- purchase orders: list of dicts with keys: po_number (str), amount (Decimal|float|str), vendor_id (str)

Exports:
- normalize_vendor_name
- normalize_iban
- similarity
- best_vendor_match
- build_vendor_index
- build_po_index
- evaluate_invoice_reason

All logic uses standard library only.
"""

from __future__ import annotations
import re
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

# ---------- Normalization Utilities ----------

_SUFFIX_MAP = {
    # common business suffix normalization (map to canonical form)
    'ltd': 'limited',
    'co': 'company',
    'co.': 'company',
    'corp': 'corporation',
    'inc': 'incorporated',
    'llc': 'llc',  # keep as-is but lowercased
    'gmbh': 'gmbh',
    'sa': 'sa',
    'bv': 'bv',
}

_PUNCT_RE = re.compile(r"[\.,;&\-_/\\\(\)\[\]\{\}\:!\?\']+")
_WS_RE = re.compile(r"\s+")


def normalize_vendor_name(name: str) -> str:
    if not name:
        return ''
    s = name.strip().lower()
    s = _PUNCT_RE.sub(' ', s)
    # normalize common suffixes as whole words
    words: List[str] = []
    for w in _WS_RE.split(s):
        if not w:
            continue
        words.append(_SUFFIX_MAP.get(w, w))
    s = ' '.join(words)
    s = _WS_RE.sub(' ', s).strip()
    return s


def normalize_iban(iban: Optional[str]) -> str:
    if not iban:
        return ''
    return re.sub(r"\s+", "", iban).upper()


# ---------- Amount Utilities ----------

def to_decimal(n: Any) -> Optional[Decimal]:
    if n is None:
        return None
    if isinstance(n, Decimal):
        return n
    if isinstance(n, (int, float)):
        # Convert via string to avoid float artifacts
        n = format(n, 'f')
    s = str(n).strip()
    # remove common currency symbols and thousand separators
    s = s.replace(',', '')
    s = re.sub(r"[\$€£¥]", "", s)
    try:
        d = Decimal(s)
        return d
    except InvalidOperation:
        return None


def quantize_cents(d: Decimal) -> Decimal:
    return d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


# ---------- Vendor Matching ----------

def similarity(a: str, b: str) -> float:
    a_n = normalize_vendor_name(a)
    b_n = normalize_vendor_name(b)
    if not a_n or not b_n:
        return 0.0
    return SequenceMatcher(None, a_n, b_n).ratio()


def build_vendor_index(vendors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    indexed = []
    for v in vendors:
        name = v.get('vendor_name', '')
        indexed.append({
            'vendor_id': str(v.get('vendor_id', '')).strip(),
            'vendor_name': name,
            'vendor_name_norm': normalize_vendor_name(name),
            'iban_norm': normalize_iban(v.get('iban')),
        })
    return indexed


def best_vendor_match(invoice_vendor_name: str, vendor_index: List[Dict[str, Any]], threshold: float = 0.85) -> Optional[Dict[str, Any]]:
    if not invoice_vendor_name:
        return None
    best = None
    best_score = -1.0
    cand_norm = normalize_vendor_name(invoice_vendor_name)
    for v in vendor_index:
        score = SequenceMatcher(None, cand_norm, v['vendor_name_norm']).ratio()
        if score > best_score:
            best = v
            best_score = score
    if best is not None and best_score >= threshold:
        # include score for downstream diagnostics if desired
        out = dict(best)
        out['match_score'] = best_score
        return out
    return None


# ---------- PO Index ----------

def _norm_po(po: Optional[str]) -> str:
    if not po:
        return ''
    return re.sub(r"\s+", "", str(po)).strip()


def build_po_index(purchase_orders: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for p in purchase_orders:
        key = _norm_po(p.get('po_number'))
        if not key:
            continue
        amt = to_decimal(p.get('amount'))
        out[key] = {
            'po_number': p.get('po_number'),
            'amount': quantize_cents(amt) if amt is not None else None,
            'vendor_id': str(p.get('vendor_id', '')).strip(),
        }
    return out


# ---------- Rule Evaluation ----------

REASONS = [
    'Unknown Vendor',
    'IBAN Mismatch',
    'Invalid PO',
    'Amount Mismatch',
    'Vendor Mismatch',
]


def evaluate_invoice_reason(
    invoice: Dict[str, Any],
    vendor_index: List[Dict[str, Any]],
    po_index: Dict[str, Dict[str, Any]],
    vendor_threshold: float = 0.85,
    amount_tolerance: Decimal = Decimal('0.01'),
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Returns (reason, po_record_used) where reason is one of REASONS or None if valid.
    - If invoice['po_number'] is missing/empty, it's considered invalid for the 'Invalid PO' check (po_number should be written as null in output).
    - IBAN mismatch is applied only when a vendor match exists; missing invoice IBAN counts as mismatch.
    - Amount mismatch and vendor mismatch are evaluated only if PO exists.
    """
    inv_vendor_name = (invoice.get('vendor_name') or '').strip()
    inv_iban = normalize_iban(invoice.get('iban'))
    inv_po_raw = invoice.get('po_number')
    inv_po_key = _norm_po(inv_po_raw)

    inv_amt_dec = to_decimal(invoice.get('invoice_amount'))
    if inv_amt_dec is not None:
        inv_amt_dec = quantize_cents(inv_amt_dec)

    # 1) Unknown Vendor
    vendor_match = best_vendor_match(inv_vendor_name, vendor_index, threshold=vendor_threshold)
    if vendor_match is None:
        return 'Unknown Vendor', None

    # 2) IBAN Mismatch
    approved_iban = vendor_match.get('iban_norm', '')
    if not inv_iban or inv_iban != approved_iban:
        return 'IBAN Mismatch', None

    # 3) Invalid PO
    po_rec = po_index.get(inv_po_key) if inv_po_key else None
    if po_rec is None:
        return 'Invalid PO', None

    # 4) Amount Mismatch
    po_amt = po_rec.get('amount')
    if inv_amt_dec is None or po_amt is None:
        # If either amount is missing/unparseable, treat as mismatch
        return 'Amount Mismatch', po_rec
    if (inv_amt_dec - po_amt).copy_abs() > amount_tolerance:
        return 'Amount Mismatch', po_rec

    # 5) Vendor Mismatch
    if po_rec.get('vendor_id') != vendor_match.get('vendor_id'):
        return 'Vendor Mismatch', po_rec

    # Valid
    return None, po_rec


if __name__ == '__main__':
    # Minimal CLI showcasing evaluation for a single invoice read from stdin as JSON.
    # This block is optional runtime help and avoids non-standard libraries.
    import json, sys
    data = sys.stdin.read()
    if not data.strip():
        print("Provide JSON on stdin with keys: invoice, vendors, purchase_orders", file=sys.stderr)
        sys.exit(1)
    try:
        payload = json.loads(data)
    except Exception as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    invoice = payload.get('invoice', {})
    vendors = payload.get('vendors', [])
    purchase_orders = payload.get('purchase_orders', [])

    v_index = build_vendor_index(vendors)
    p_index = build_po_index(purchase_orders)

    reason, po_used = evaluate_invoice_reason(invoice, v_index, p_index)
    out = {
        'reason': reason,
        'po_used': po_used,
    }
    print(json.dumps(out, ensure_ascii=False))
