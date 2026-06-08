#!/usr/bin/env python3
"""Run medchem CommonAlertsFilters for a single SMILES and write a standardized report.

Usage:
  python medchem_common_alerts.py --input /root/input.txt --output /root/output.txt
  python medchem_common_alerts.py --smiles "CCO" --output /root/output.txt

Behavior:
- Supports both medchem API shapes: callable filter (returns DataFrame) and .check_mol.
- Counts alert reasons robustly from strings/lists/dicts/None.
- Writes exactly three lines to the output file:
    Common alerts: N
    Status: status
    Pass: yes/no
"""

import argparse
import sys
from typing import Any, Tuple


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def count_alerts(val: Any) -> int:
    """Normalize diverse 'reasons' representations into an integer count."""
    if val is None:
        return 0
    # Try to accept pandas NA-like values as empty
    try:
        import math
        if isinstance(val, float) and math.isnan(val):
            return 0
    except Exception:
        pass

    if isinstance(val, str):
        s = val.strip()
        if not s or s.lower() == 'none' or s.lower() == 'nan':
            return 0
        # unify common separators
        for sep in [',', '|']:
            s = s.replace(sep, ';')
        parts = [p.strip() for p in s.split(';') if p.strip()]
        return len(parts)

    if isinstance(val, dict):
        # count non-empty keys or entries
        return len([k for k in val.keys() if str(k).strip()])

    if isinstance(val, (list, tuple, set)):
        return len([x for x in val if str(x).strip()])

    # Fallback: try casting to int
    try:
        n = int(val)  # may raise
        return max(0, n)
    except Exception:
        return 1  # conservative default


def parse_mol(smiles: str):
    """Try to build a molecule object from SMILES using datamol or RDKit."""
    mol = None
    try:
        import datamol as dm  # type: ignore
        mol = dm.to_mol(smiles)
        if mol is not None:
            return mol
    except Exception:
        pass
    try:
        from rdkit import Chem  # type: ignore
        mol = Chem.MolFromSmiles(smiles)
        return mol
    except Exception:
        return None


def run_filter(smiles: str, n_jobs: int = 1) -> Tuple[str, int]:
    import medchem as mc  # type: ignore

    f = mc.structural.CommonAlertsFilters()

    # Preferred path: callable filter returning a DataFrame-like object
    try:
        if callable(f):
            res = f([smiles], n_jobs=n_jobs)
            # Extract first row in a pandas-like fashion
            try:
                row = res.iloc[0]
                get = row.get  # pandas Series has get
            except Exception:
                # Accept dict/list fallbacks if any
                row = res[0] if isinstance(res, (list, tuple)) and res else {}
                get = (row.get if isinstance(row, dict) else (lambda *a, **k: None))

            status = str(get('status', '') or '').strip()
            reasons = get('reasons', None)
            if reasons is None:
                # Try alternate field names observed in different versions
                for key in ('alert_types', 'exclude_reasons', 'reasons_str'):
                    if isinstance(row, dict) and key in row:
                        reasons = row.get(key)
                        break
                    try:
                        # pandas Series supports 'in'
                        if key in row:
                            reasons = row[key]
                            break
                    except Exception:
                        pass

            num_alerts = count_alerts(reasons)
            if not status:
                status = 'ok' if num_alerts == 0 else 'alert'
            return status, num_alerts
    except Exception:
        # Fall back to check_mol path
        pass

    # Fallback path: check_mol API
    if hasattr(f, 'check_mol'):
        mol = parse_mol(smiles)
        if mol is None:
            raise RuntimeError('Could not parse SMILES into a molecule for check_mol().')
        res = f.check_mol(mol)
        has_alerts = None
        details = {}
        if isinstance(res, tuple) and len(res) >= 2:
            has_alerts, details = res[0], (res[1] or {})
        elif isinstance(res, dict):
            details = res
        # Extract reasons from details
        reasons = None
        if isinstance(details, dict):
            reasons = details.get('alert_types') or details.get('reasons')
        num_alerts = count_alerts(reasons)
        if has_alerts is None:
            has_alerts = num_alerts > 0
        status = 'ok' if not has_alerts else ('annotations' if num_alerts == 0 else 'alert')
        return status, num_alerts

    raise RuntimeError('Unsupported medchem.CommonAlertsFilters API on this installation.')


def main():
    parser = argparse.ArgumentParser(description='Run medchem CommonAlertsFilters on a single SMILES and write a standard report.')
    parser.add_argument('--input', default='/root/input.txt', help='Path to input file containing a SMILES string (default: /root/input.txt)')
    parser.add_argument('--output', default='/root/output.txt', help='Path to write the report (default: /root/output.txt)')
    parser.add_argument('--smiles', default=None, help='SMILES string (overrides --input if provided)')
    parser.add_argument('--n-jobs', type=int, default=1, help='n_jobs for callable filter API (default: 1)')
    args = parser.parse_args()

    try:
        if args.smiles is not None:
            smiles = args.smiles.strip()
        else:
            with open(args.input, 'r') as f:
                smiles = f.read().strip()
        if not smiles:
            raise ValueError('Empty SMILES input.')

        status, num_alerts = run_filter(smiles, n_jobs=args.n_jobs)
        passes = 'yes' if (status == 'ok' or (status == 'annotations' and num_alerts == 0)) else 'no'

        with open(args.output, 'w') as f:
            f.write(f'Common alerts: {num_alerts}\n')
            f.write(f'Status: {status}\n')
            f.write(f'Pass: {passes}\n')
    except ModuleNotFoundError as e:
        eprint(f'ERROR: Required module not found: {e}')
        sys.exit(1)
    except Exception as e:
        eprint(f'ERROR: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
