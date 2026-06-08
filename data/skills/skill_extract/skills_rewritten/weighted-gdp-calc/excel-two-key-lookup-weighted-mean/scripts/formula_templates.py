#!/usr/bin/env python3
"""Generate generic spreadsheet formula templates for two-key lookups,
net-exports percentage, summary stats, and SUMPRODUCT-weighted mean.

This does not modify any workbook; it prints formulas you can paste into Excel/LibreOffice.

Examples:
  python scripts/formula_templates.py --type two_key \
    --data-sheet Data --data-range A1:Z100 \
    --rowkey-col A:A --header-row 1:1 \
    --rowkey-ref $A$12 --year-ref $H$10

  python scripts/formula_templates.py --type net_exports \
    --exports-ref H12 --imports-ref H19 --gdp-ref H26

  python scripts/formula_templates.py --type weighted_mean \
    --values-range H35:H40 --weights-range H26:H31

  python scripts/formula_templates.py --type stats \
    --values-range H35:H40
"""

import argparse
import sys


def two_key_formula(data_sheet: str, data_range: str, rowkey_col: str, header_row: str,
                    rowkey_ref: str, year_ref: str) -> str:
    """INDEX + MATCH + MATCH template with exact matches and anchored ranges.

    Returns a formula string like:
    =INDEX(Data!$A$1:$Z$100, MATCH($A$12, Data!$A:$A, 0), MATCH($H$10, Data!$1:$1, 0))
    """
    ds = data_sheet.strip()
    # Quote sheet name if contains space or special char
    if not ds.startswith("'") and not ds.endswith("'") and any(c.isspace() for c in ds):
        ds = f"'{ds}'"
    return (
        f"=INDEX({ds}!${data_range}, "
        f"MATCH({rowkey_ref}, {ds}!${rowkey_col}, 0), "
        f"MATCH({year_ref}, {ds}!${header_row}, 0))"
    )


def net_exports_pct_formula(exports_ref: str, imports_ref: str, gdp_ref: str,
                            wrap_iferror: bool = True) -> str:
    base = f"(({exports_ref} - {imports_ref}) / {gdp_ref})"
    if wrap_iferror:
        return f"=IFERROR({base}, \"\")"
    return f"={base}"


def weighted_mean_formula(values_range: str, weights_range: str, wrap_iferror: bool = True) -> str:
    base = f"SUMPRODUCT({values_range}, {weights_range}) / SUM({weights_range})"
    if wrap_iferror:
        return f"=IFERROR({base}, \"\")"
    return f"={base}"


def stats_formulas(values_range: str) -> dict:
    """Return a dict of common summary formulas over a range.
    Percentile variants include both INC and base PERCENTILE for compatibility.
    """
    return {
        "min": f"=MIN({values_range})",
        "max": f"=MAX({values_range})",
        "median": f"=MEDIAN({values_range})",
        "mean": f"=AVERAGE({values_range})",
        "p25_inc": f"=PERCENTILE.INC({values_range}, 0.25)",
        "p75_inc": f"=PERCENTILE.INC({values_range}, 0.75)",
        "p25_base": f"=PERCENTILE({values_range}, 0.25)",
        "p75_base": f"=PERCENTILE({values_range}, 0.75)",
    }


def main():
    p = argparse.ArgumentParser(description="Spreadsheet formula template generator")
    p.add_argument("--type", required=True, choices=["two_key", "net_exports", "weighted_mean", "stats"],
                   help="Type of template to generate")

    # Shared/optional args
    p.add_argument("--data-sheet")
    p.add_argument("--data-range")
    p.add_argument("--rowkey-col")
    p.add_argument("--header-row")
    p.add_argument("--rowkey-ref")
    p.add_argument("--year-ref")

    p.add_argument("--exports-ref")
    p.add_argument("--imports-ref")
    p.add_argument("--gdp-ref")
    p.add_argument("--values-range")
    p.add_argument("--weights-range")
    p.add_argument("--no-iferror", action="store_true", help="Do not wrap with IFERROR")

    args = p.parse_args()

    if args.type == "two_key":
        required = [args.data_sheet, args.data_range, args.rowkey_col, args.header_row, args.rowkey_ref, args.year_ref]
        if any(x is None for x in required):
            print("ERROR: --data-sheet --data-range --rowkey-col --header-row --rowkey-ref --year-ref are required for two_key", file=sys.stderr)
            sys.exit(1)
        print(two_key_formula(args.data_sheet, args.data_range, args.rowkey_col, args.header_row,
                              args.rowkey_ref, args.year_ref))
        return

    if args.type == "net_exports":
        required = [args.exports_ref, args.imports_ref, args.gdp_ref]
        if any(x is None for x in required):
            print("ERROR: --exports-ref --imports-ref --gdp-ref are required for net_exports", file=sys.stderr)
            sys.exit(1)
        print(net_exports_pct_formula(args.exports_ref, args.imports_ref, args.gdp_ref, wrap_iferror=not args.no_iferror))
        return

    if args.type == "weighted_mean":
        required = [args.values_range, args.weights_range]
        if any(x is None for x in required):
            print("ERROR: --values-range --weights-range are required for weighted_mean", file=sys.stderr)
            sys.exit(1)
        print(weighted_mean_formula(args.values_range, args.weights_range, wrap_iferror=not args.no_iferror))
        return

    if args.type == "stats":
        if not args.values_range:
            print("ERROR: --values-range is required for stats", file=sys.stderr)
            sys.exit(1)
        fm = stats_formulas(args.values_range)
        for k, v in fm.items():
            print(f"{k}: {v}")
        return


if __name__ == "__main__":
    main()
