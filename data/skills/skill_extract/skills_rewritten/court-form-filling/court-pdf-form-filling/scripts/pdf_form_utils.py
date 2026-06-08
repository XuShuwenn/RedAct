#!/usr/bin/env python3
"""
Utility for inspecting and filling AcroForm PDFs.

Features:
- list: Extract form fields, types, pages, and checkbox/radio appearance states to JSON
- fill: Fill form fields from a JSON mapping (text & checkbox/radio)
- verify: Compare filled field values with expected mapping and optionally validate date formats

Requirements:
- PyPDF2 (or pypdf). Install with: pip install PyPDF2

JSON mapping format (values file):
{
  "FieldName1": "text value",
  "A_Checkbox": true,                  # boolean allowed for checkboxes/radios
  "RadioGroup": "OnStateLabel"         # or explicit on-state string
}

Notes on checkboxes/radios:
- The On state label is the appearance key (e.g., "Yes", "On", "1").
- This script will map True -> chosen On state, False -> Off.
- If multiple On states exist for a radio group, provide the exact On label in the values file.
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

try:
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import NameObject
except Exception as e:
    print("ERROR: PyPDF2 is required for this tool. Install with 'pip install PyPDF2'", file=sys.stderr)
    raise


def _iter_widgets(reader: PdfReader):
    """Yield tuples of (page_index, field_dict, widget_ref, widget_annot)."""
    for page_index, page in enumerate(reader.pages):
        annots = page.get("/Annots")
        if not annots:
            continue
        for annot_ref in annots:
            annot = annot_ref.get_object()
            if annot.get("/Subtype") != "/Widget":
                continue
            field = annot
            yield page_index, field, annot_ref, annot


def _field_name(field) -> Optional[str]:
    name = field.get("/T")
    if name is None:
        return None
    if hasattr(name, "__str__"):
        return str(name)
    return name


def _field_type(field) -> Optional[str]:
    ft = field.get("/FT")
    if ft is None:
        return None
    return str(ft)


def _field_value(field) -> Any:
    v = field.get("/V")
    if v is None:
        return None
    return str(v)


def _appearance_states(field) -> Dict[str, List[str]]:
    """Return available appearance states for normal appearance: {"On": [labels...], "Off": [labels...]}"""
    ap = field.get("/AP")
    states = {"On": [], "Off": []}
    if not ap:
        return states
    n = ap.get("/N")
    if not n:
        return states
    try:
        keys = list(n.keys())
    except Exception:
        return states
    for k in keys:
        label = str(k)
        if label.lower() == "/off":
            states["Off"].append("Off")
        else:
            # strip leading slash
            states["On"].append(label[1:] if label.startswith("/") else label)
    return states


def list_fields(pdf_path: str, out_path: Optional[str] = None) -> Dict[str, Any]:
    reader = PdfReader(pdf_path)
    result: Dict[str, Any] = {"fields": []}
    for page_index, field, widget_ref, annot in _iter_widgets(reader):
        name = _field_name(field)
        if not name:
            continue
        ftype = _field_type(field)
        value = _field_value(field)
        states = _appearance_states(field) if ftype in ("/Btn",) else {"On": [], "Off": []}
        result["fields"].append({
            "name": name,
            "type": ftype,
            "page": page_index + 1,
            "value": value,
            "appearance_states": states
        })
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    return result


def _choose_on_label(states: Dict[str, List[str]]) -> Optional[str]:
    # Prefer a label named "Yes" or "On" if present, else first available.
    ons = states.get("On") or []
    for pref in ("Yes", "On", "1", "True"):
        if pref in ons:
            return pref
    return ons[0] if ons else None


def fill_fields(pdf_in: str, values: Dict[str, Any], pdf_out: str) -> None:
    reader = PdfReader(pdf_in)
    writer = PdfWriter()

    # Ensure NeedAppearances so viewers render appearances properly
    if "/AcroForm" in reader.trailer["/Root"]:
        acro_form = reader.trailer["/Root"]["/AcroForm"].get_object()
        acro_form.update({NameObject("/NeedAppearances"): True})
        writer._root_object.update({NameObject("/AcroForm"): acro_form})

    for page in reader.pages:
        writer.add_page(page)

    # Build index of widgets by field name
    widgets_by_name: Dict[str, List[Tuple[int, Any]]] = {}
    for page_index, field, widget_ref, annot in _iter_widgets(reader):
        name = _field_name(field)
        if not name:
            continue
        widgets_by_name.setdefault(name, []).append((page_index, field))

    # Apply values
    for name, desired in values.items():
        if name not in widgets_by_name:
            continue
        for page_index, field in widgets_by_name[name]:
            ftype = _field_type(field)
            if ftype == "/Btn":
                # checkbox or radio
                states = _appearance_states(field)
                off_label = "Off"
                on_label = None
                # Determine on_label
                if isinstance(desired, bool):
                    on_label = _choose_on_label(states)
                    selected_label = on_label if desired else off_label
                else:
                    # Explicit label requested by user
                    desired_label = str(desired)
                    if desired_label in states.get("On", []):
                        selected_label = desired_label
                    elif desired_label.lower() == "off":
                        selected_label = off_label
                    else:
                        # Fallback: choose default on-label if desired truthy
                        on_label = _choose_on_label(states)
                        selected_label = on_label if on_label else off_label
                # Set value and appearance
                for page in writer.pages:
                    # Update first match found on that page (multiple widgets may share name)
                    pass
                field.update({NameObject("/V"): NameObject(f"/{selected_label}") if selected_label != "Off" else NameObject("/Off")})
                field.update({NameObject("/AS"): NameObject(f"/{selected_label}") if selected_label != "Off" else NameObject("/Off")})
            else:
                # Treat as text
                text_val = "" if desired is None else str(desired)
                field.update({NameObject("/V"): text_val})

    with open(pdf_out, "wb") as f:
        writer.write(f)


def verify(pdf_path: str, expect: Dict[str, Any], date_regex: Optional[str] = None) -> Tuple[bool, List[str]]:
    reader = PdfReader(pdf_path)
    issues: List[str] = []
    # Build current values
    current: Dict[str, Any] = {}
    for _, field, _, _ in _iter_widgets(reader):
        name = _field_name(field)
        if not name:
            continue
        ftype = _field_type(field)
        if ftype == "/Btn":
            v = _field_value(field)
            if v is None or v.lower() == "/off":
                current[name] = "Off"
            else:
                current[name] = v[1:] if v.startswith("/") else v
        else:
            v = _field_value(field)
            current[name] = v or ""

    # Compare expected subset only
    for key, exp in expect.items():
        if key not in current:
            issues.append(f"Missing field in PDF: {key}")
            continue
        if isinstance(exp, bool):
            # Compare to Off/On label presence
            cur = current[key]
            if exp and cur in ("Off", None, ""):
                issues.append(f"Field {key} expected checked but is Off")
            if not exp and cur not in ("Off", None, ""):
                issues.append(f"Field {key} expected Off but is {cur}")
        else:
            if str(current[key]).strip() != str(exp).strip():
                issues.append(f"Field {key} mismatch: got '{current[key]}', expected '{exp}'")

        if date_regex and isinstance(exp, str) and re.fullmatch(date_regex, exp):
            # ensure filled value also matches date format
            cur = str(current[key])
            if not re.fullmatch(date_regex, cur):
                issues.append(f"Date format mismatch for {key}: '{cur}' does not match {date_regex}")

    return (len(issues) == 0), issues


def main():
    parser = argparse.ArgumentParser(description="PDF form inspector/filler")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List fields and states to JSON")
    p_list.add_argument("--pdf", required=True, help="Path to blank or filled PDF")
    p_list.add_argument("--out", help="Output JSON file (defaults to stdout)")

    p_fill = sub.add_parser("fill", help="Fill a PDF from a JSON mapping")
    p_fill.add_argument("--pdf-in", required=True, help="Path to input PDF")
    p_fill.add_argument("--values", required=True, help="Path to JSON field-value mapping")
    p_fill.add_argument("--pdf-out", required=True, help="Path to output filled PDF")

    p_verify = sub.add_parser("verify", help="Verify filled PDF against expected mapping")
    p_verify.add_argument("--pdf", required=True, help="Path to filled PDF")
    p_verify.add_argument("--expect", required=True, help="Path to JSON expected values (subset)")
    p_verify.add_argument("--require-date-format", help="Regex (fullmatch) to validate date strings")

    args = parser.parse_args()

    if args.cmd == "list":
        data = list_fields(args.pdf, out_path=args.out)
        if not args.out:
            json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
            print()
    elif args.cmd == "fill":
        with open(args.values, "r", encoding="utf-8") as f:
            values = json.load(f)
        fill_fields(args.pdf_in, values, args.pdf_out)
        print(f"Filled PDF written to: {args.pdf_out}")
    elif args.cmd == "verify":
        with open(args.expect, "r", encoding="utf-8") as f:
            exp = json.load(f)
        ok, issues = verify(args.pdf, exp, date_regex=args.require_date_format)
        if ok:
            print("Verification passed.")
        else:
            print("Verification issues:")
            for i in issues:
                print(f"- {i}")
            sys.exit(1)


if __name__ == "__main__":
    main()
