#!/usr/bin/env python3
"""
Portable Excel formula helpers and simple normalization utilities.
These do not compute results; they return strings for formulas or canonical names.
Use when generating spreadsheets programmatically for cross-engine recalculation.
"""
from typing import Optional
import re


def normalize_country(name: str) -> str:
    """Normalize entity name from a verbose header.
    - Take substring before ':' if present
    - Collapse whitespace
    - Expand common abbreviations (Intl -> International)
    - Lower-level cleanup without locale assumptions
    """
    if not name:
        return ""
    base = name.split(":")[0]
    base = re.sub(r"\s+", " ", base).strip()
    # Expand common variants
    base = re.sub(r"\bIntl\b", "International", base, flags=re.IGNORECASE)
    base = re.sub(r"\bRep\b", "Republic", base, flags=re.IGNORECASE)
    return base


def last_value_formula(sheet: str, col: str) -> str:
    """Return a robust formula to fetch the last non-empty value in a column.
    Example: LOOKUP(2,1/('Sheet'!D:D<>""),'Sheet'!D:D)
    """
    s = f"'{sheet}'" if " " in sheet else sheet
    return f"=LOOKUP(2,1/({s}!{col}:{col}<>\"\"),{s}!{col}:{col})"


def rolling_stdev_formula(col: str, row: int, window: int) -> Optional[str]:
    """Return a rolling STDEV range formula for a given row.
    Uses legacy STDEV for cross-engine compatibility.
    Returns None if row is too small for the window.
    """
    if row < (window + 1):
        return None
    start = row - (window - 1)
    return f"=STDEV({col}{start}:{col}{row})"


def log_return_formula(price_col: str, row: int) -> Optional[str]:
    """Monthly log return in percent points: LN(P_t/P_{t-1})*100.
    Returns None for the very first data row (no prior).
    """
    if row <= 2:
        return None
    return f"=LN({price_col}{row}/{price_col}{row-1})*100"


def exposure_formula(val_cell: str, vol_cell: str, z_cell: str, vol_as_pct: bool = True) -> str:
    """Exposure formula: Value * Volatility * Z.
    - If vol_as_pct is True, divide volatility by 100.
    Absolute refs for vol_cell and z_cell should be provided by the caller.
    """
    if vol_as_pct:
        return f"={val_cell}*({vol_cell}/100)*{z_cell}"
    return f"={val_cell}*{vol_cell}*{z_cell}"


def index_match_by_header(sheet: str, target_row: int, header_label_cell: str) -> str:
    """INDEX a specific row using MATCH on header row (row 1), matching the header label in header_label_cell.
    Wrap with IFERROR outside if desired.
    Example: =INDEX('S'!$18:$18, MATCH("*"&C20&"*", 'S'!$1:$1, 0))
    """
    s = f"'{sheet}'" if " " in sheet else sheet
    return f"=INDEX({s}!${target_row}:${target_row}, MATCH(""*""&{header_label_cell}&""*"", {s}!$1:$1, 0))"


def iferror_division(numerator: str, denominator: str) -> str:
    """Guarded division formula to avoid #DIV/0!"""
    return f"=IFERROR({numerator}/{denominator}, \"\")"


def guard_blank_product(product_formula: str, required_cell: str) -> str:
    """Return product_formula only if required_cell is non-blank; else blank.
    Example: =IF(C12="", "", C12*$C$3*$C$4/100)
    """
    return f"=IF({required_cell}=\"\", \"\", {product_formula})"


if __name__ == "__main__":
    # Demo printout of common formulas
    print("-- Demo --")
    print("Normalize:", normalize_country("Czechia Intl Reserves: Gold Volume (Mil. Troy Oz)"))
    print("Last value:", last_value_formula("Gold price", "D"))
    print("Rolling 3M stdev row 15:", rolling_stdev_formula("C", 15, 3))
    print("Log return row 10:", log_return_formula("B", 10))
    print("Exposure:", exposure_formula("C12", "$C$4", "$C$3", vol_as_pct=True))
    print("INDEX+MATCH by header:", index_match_by_header("Total Reserves", 18, "C20"))
    print("Guarded division:", iferror_division("C22", "C23"))
    print("Guarded product:", guard_blank_product("C12*$C$3*($C$4/100)", "C12"))
