#!/usr/bin/env python3
"""Reusable tools for building Excel pivot-style reports from merged tabular data.

Features:
- Numeric coercion from messy strings (commas, currency symbols, parentheses for negatives)
- Join key normalization (trim, case, optional zero-padding)
- Robust quartile labeling (Q1–Q4) with fallback for tied quantiles
- Writing an Excel workbook with SourceData and aggregated summary sheets
- Optional helpers to build true Excel pivot tables via xlsxwriter (if desired)

This module avoids hard-coding column names. Provide the columns when calling writer functions.
"""

from __future__ import annotations
import re
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

try:
    import xlsxwriter  # noqa: F401
    _HAS_XLSXWRITER = True
except Exception:
    _HAS_XLSXWRITER = False


_NON_NUMERIC_RE = re.compile(r"[^0-9.\-]|")


def coerce_numeric(s: pd.Series) -> pd.Series:
    """Convert a Series with mixed numeric/string values to float.

    - Removes commas and common currency symbols
    - Treats parentheses as negatives, e.g., (123.45) -> -123.45
    - Returns float dtype (NaN for unparseable values)
    """
    if s is None:
        return s
    x = s.astype(str).str.strip()
    # Handle parentheses negatives
    neg_mask = x.str.match(r"^\(.*\)$")
    x = x.str.replace(r"[,$\s]", "", regex=True)
    x = x.str.replace(r"^\((.*)\)$", r"-\\1", regex=True)
    # Remove any remaining non-numeric except dot and minus
    x = x.str.replace(r"[^0-9.\-]", "", regex=True)
    out = pd.to_numeric(x, errors="coerce")
    # Preserve original NaN where appropriate
    return out.astype(float)


def normalize_key(s: pd.Series, *, zero_pad: Optional[int] = None, upper: bool = True) -> pd.Series:
    """Normalize join keys: trim, case, and optional zero-padding.

    Args:
        s: Series of keys (will be cast to string)
        zero_pad: If provided, left-pad numeric-like keys to this width.
        upper: Convert to uppercase if True (otherwise lowercase).
    """
    x = s.astype(str).str.strip()
    x = x.str.upper() if upper else x.str.lower()
    if zero_pad is not None:
        # Keep only digits for padding; re-attach non-digits if needed
        # Simple approach: pad if the whole string is digits
        x = x.apply(lambda v: v.zfill(zero_pad) if v.isdigit() else v)
    return x


def assign_quartiles(values: pd.Series, labels: Tuple[str, str, str, str] = ("Q1", "Q2", "Q3", "Q4")) -> pd.Series:
    """Assign quartile labels Q1–Q4 across all non-null values.

    Uses pandas.qcut with a deterministic fallback when quantile edges are not unique
    (e.g., many tied values). The fallback uses rank-based binning to ensure 4 labels.
    """
    v = pd.to_numeric(values, errors="coerce")
    mask = v.notna()
    res = pd.Series(index=v.index, dtype=object)
    if mask.sum() == 0:
        return res
    try:
        res.loc[mask] = pd.qcut(v[mask], 4, labels=labels, duplicates="drop")
        # If fewer than 4 bins, qcut will drop duplicates; detect and fallback
        if pd.Series(res[mask]).nunique() < 4:
            raise ValueError("Non-unique quantile edges; using fallback")
    except Exception:
        # Fallback: rank-based binning into 4 groups
        r = v[mask].rank(method="first")
        n = float(len(r))
        # Compute 4 bins by rank position
        bins = [0, n * 0.25, n * 0.5, n * 0.75, n]
        # To avoid edge collisions, add a tiny epsilon
        eps = 1e-9
        bins = [b + eps for b in bins]
        res.loc[mask] = pd.cut(r, bins=bins, labels=labels, include_lowest=True)
    return res.astype(object)


def ensure_columns(df: pd.DataFrame, required: Iterable[str]):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _a1_range(nrows: int, ncols: int, sheet: str = "SourceData") -> str:
    """Return Excel A1 range like 'SourceData!$A$1:$Z$100' for given shape.
    Assumes headers at row 1.
    """
    def col_letter(idx: int) -> str:
        s = ""
        idx0 = idx
        while True:
            idx0, rem = divmod(idx0, 26)
            s = chr(ord('A') + rem) + s
            if idx0 == 0:
                break
            idx0 -= 1
        return s
    last_col = col_letter(ncols - 1)
    last_row = nrows
    return f"{sheet}!$A$1:${last_col}${last_row}"


def write_aggregated_report(
    *,
    df: pd.DataFrame,
    output_path: str,
    state_col: str,
    region_col: str,
    population_col: str,
    earners_col: str,
    quarter_col: str,
    engine: str = "xlsxwriter",
) -> None:
    """Write an Excel report with SourceData and four aggregated summary sheets.

    Aggregations:
    - Population by State: sum(population_col) by state_col
    - Earners by State: sum(earners_col) by state_col
    - Regions by State: count of region rows by state_col
    - State Income Quartile: sum(earners_col) by state_col × quarter_col (Q1–Q4)
    """
    required = [state_col, region_col, population_col, earners_col, quarter_col]
    ensure_columns(df, required)

    with pd.ExcelWriter(output_path, engine=engine) as writer:
        # SourceData first
        df.to_excel(writer, sheet_name="SourceData", index=False)

        # 1) Population by State
        pop = (
            df.groupby(state_col, dropna=False)[population_col]
            .sum(min_count=1)
            .reset_index()
            .sort_values(state_col)
        )
        pop.to_excel(writer, sheet_name="Population by State", index=False)

        # 2) Earners by State
        earn = (
            df.groupby(state_col, dropna=False)[earners_col]
            .sum(min_count=1)
            .reset_index()
            .sort_values(state_col)
        )
        earn.to_excel(writer, sheet_name="Earners by State", index=False)

        # 3) Regions by State (row count)
        reg = (
            df.groupby(state_col, dropna=False)[region_col]
            .size()
            .reset_index(name="Region_Count")
            .sort_values(state_col)
        )
        reg.to_excel(writer, sheet_name="Regions by State", index=False)

        # 4) State Income Quartile (sum of earners by state × quarter)
        cross = (
            pd.pivot_table(
                df,
                index=state_col,
                columns=quarter_col,
                values=earners_col,
                aggfunc="sum",
                fill_value=0,
            )
            .reset_index()
            .sort_values(state_col)
        )
        cross.to_excel(writer, sheet_name="State Income Quartile", index=False)

        # Optional formatting niceties
        try:
            workbook = writer.book
            for sheet in [
                "SourceData",
                "Population by State",
                "Earners by State",
                "Regions by State",
                "State Income Quartile",
            ]:
                ws = writer.sheets[sheet]
                ws.freeze_panes(1, 0)
        except Exception:
            pass


def write_excel_with_pivots(
    *,
    df: pd.DataFrame,
    output_path: str,
    state_col: str,
    region_col: str,
    population_col: str,
    earners_col: str,
    quarter_col: str,
) -> None:
    """Write an Excel report using true pivot tables (xlsxwriter required).

    Falls back to aggregated report if xlsxwriter is unavailable.
    """
    if not _HAS_XLSXWRITER:
        # Fallback to aggregated tables
        write_aggregated_report(
            df=df,
            output_path=output_path,
            state_col=state_col,
            region_col=region_col,
            population_col=population_col,
            earners_col=earners_col,
            quarter_col=quarter_col,
            engine="xlsxwriter",
        )
        return

    required = [state_col, region_col, population_col, earners_col, quarter_col]
    ensure_columns(df, required)

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="SourceData", index=False)
        workbook = writer.book
        ws_source = writer.sheets["SourceData"]
        ws_source.freeze_panes(1, 0)

        nrows, ncols = df.shape
        data_range = _a1_range(nrows + 1, ncols, sheet="SourceData")  # +1 for header

        # Helper to add a pivot table
        def add_pivot(sheet_name: str, dest_cell: str, rows: Sequence[str], values: Sequence[Tuple[str, str]], cols: Optional[Sequence[str]] = None):
            ws = workbook.add_worksheet(sheet_name)
            # Map pandas columns to Excel fields as-is
            fields_rows = [{"data_field": r} for r in rows]
            fields_vals = [{"data_field": v, "subtotal": agg.upper()} for v, agg in values]
            fields_cols = [{"data_field": c} for c in (cols or [])]
            options = {
                "data": data_range,
                "row_fields": fields_rows,
                "column_fields": fields_cols,
                "data_fields": fields_vals,
                "name": f"Pivot_{sheet_name.replace(' ', '_')}",
                "insert_row": int(re.sub(r"[A-Z]", "", dest_cell)) - 1,
                "insert_col": ord(re.sub(r"[^A-Z]", "", dest_cell)) - ord('A'),
            }
            ws.add_pivot_table(options)

        # 1) Population by State
        add_pivot(
            sheet_name="Population by State",
            dest_cell="A3",
            rows=[state_col],
            values=[(population_col, "sum")],
        )
        # 2) Earners by State
        add_pivot(
            sheet_name="Earners by State",
            dest_cell="A3",
            rows=[state_col],
            values=[(earners_col, "sum")],
        )
        # 3) Regions by State (count rows via region_col)
        add_pivot(
            sheet_name="Regions by State",
            dest_cell="A3",
            rows=[state_col],
            values=[(region_col, "count")],
        )
        # 4) State Income Quartile (state × quarter: sum of earners)
        add_pivot(
            sheet_name="State Income Quartile",
            dest_cell="A3",
            rows=[state_col],
            cols=[quarter_col],
            values=[(earners_col, "sum")],
        )

        # Ensure writer knows about created sheets
        for name in [
            "Population by State",
            "Earners by State",
            "Regions by State",
            "State Income Quartile",
        ]:
            writer.sheets[name] = workbook.get_worksheet_by_name(name)


# End of module
