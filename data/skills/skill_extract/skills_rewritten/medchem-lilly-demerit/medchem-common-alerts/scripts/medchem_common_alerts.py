#!/usr/bin/env python3
"""
Run MedChem Common Alerts on a SMILES string and write a normalized three-line report.

Usage:
  python medchem_common_alerts.py --smiles "CCO" --outfile /root/output.txt
  python medchem_common_alerts.py --infile /path/to/input.txt --outfile /root/output.txt

Behavior:
  - Attempts to import medchem Common Alerts filter via multiple known paths
  - Tries calling the filter with SMILES or RDKit Mol
  - Normalizes result to {status, n_alerts} and writes deterministic output
"""

import argparse
import sys
from typing import Any, Dict, Optional, Tuple


def read_smiles_from_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if s:
                return s
    return ""


def get_rdkit_mol(smiles: str):
    try:
        from rdkit import Chem  # type: ignore
    except Exception:
        return None
    try:
        return Chem.MolFromSmiles(smiles)
    except Exception:
        return None


def try_import_filter() -> Tuple[Optional[Any], Optional[str]]:
    """Try several import paths for the Common Alerts filter.

    Returns: (filter_object or None, error_reason or None)
    """
    # Attempt 1: medchem.filters.CommonAlertsFilter
    try:
        from medchem.filters import CommonAlertsFilter  # type: ignore
        try:
            return CommonAlertsFilter(), None
        except Exception:
            pass
    except Exception:
        pass

    # Attempt 2: medchem.filters.common_alerts.CommonAlertsFilter
    try:
        from medchem.filters.common_alerts import CommonAlertsFilter  # type: ignore
        try:
            return CommonAlertsFilter(), None
        except Exception:
            pass
    except Exception:
        pass

    # Attempt 3: medchem.filters.common_alerts.CommonAlerts
    try:
        from medchem.filters.common_alerts import CommonAlerts  # type: ignore
        try:
            return CommonAlerts(), None
        except Exception:
            pass
    except Exception:
        pass

    # Attempt 4: Namespace search fallback
    try:
        import medchem  # type: ignore
        # Heuristically search attributes
        for name in dir(medchem):
            if 'filter' in name.lower() or 'alert' in name.lower():
                obj = getattr(medchem, name)
                try:
                    inst = obj() if callable(obj) else obj
                    return inst, None
                except Exception:
                    continue
    except Exception as e:
        return None, 'import-error: medchem not available'

    return None, 'import-error: common alerts filter not found'


def call_filter(filter_obj: Any, smiles: str) -> Tuple[str, int]:
    """Call the filter using common method names and argument styles.

    Returns (status, n_alerts). On failure, returns ('error', 0).
    """
    # Possible method names in order of likelihood
    methods = ['evaluate', 'check', 'run', 'predict', '__call__', 'apply', 'filter']

    # Build possible inputs
    mol = get_rdkit_mol(smiles)
    arg_candidates = [
        ((), {'smiles': smiles}),
        ((smiles,), {}),
        ((mol,), {}) if mol is not None else None,
        ((), {'mol': mol}) if mol is not None else None,
    ]
    arg_candidates = [c for c in arg_candidates if c is not None]

    # Try method calls
    for mname in methods:
        func = getattr(filter_obj, mname, None)
        if func is None:
            continue
        for args, kwargs in arg_candidates:
            try:
                res = func(*args, **kwargs)
                status, n_alerts = normalize_result(res)
                if status is not None:
                    return status, n_alerts
            except Exception:
                continue

    # If the filter itself is callable
    if callable(filter_obj):
        for args, kwargs in arg_candidates:
            try:
                res = filter_obj(*args, **kwargs)
                status, n_alerts = normalize_result(res)
                if status is not None:
                    return status, n_alerts
            except Exception:
                continue

    return 'error', 0


def normalize_result(res: Any) -> Tuple[Optional[str], int]:
    """Extract (status, n_alerts) from various possible structures.

    If not recognized, returns (None, 0) to let caller try other strategies.
    """
    # Dict-like result
    if isinstance(res, dict):
        status = str(res.get('status', 'unknown'))
        if 'alerts_count' in res and isinstance(res['alerts_count'], int):
            n_alerts = int(res['alerts_count'])
        elif 'n_alerts' in res and isinstance(res['n_alerts'], int):
            n_alerts = int(res['n_alerts'])
        elif 'alerts' in res and isinstance(res['alerts'], (list, tuple)):
            n_alerts = len(res['alerts'])
        elif 'reasons' in res and isinstance(res['reasons'], (list, tuple)):
            n_alerts = len(res['reasons'])
        else:
            # Could be zero-issue annotations without explicit list
            n_alerts = int(res.get('count', 0)) if isinstance(res.get('count', 0), int) else 0
        return status, n_alerts

    # Tuple-like result: try known (status, items) pattern
    if isinstance(res, (tuple, list)) and len(res) >= 2:
        status = str(res[0])
        second = res[1]
        if isinstance(second, int):
            n_alerts = int(second)
        elif isinstance(second, (list, tuple)):
            n_alerts = len(second)
        else:
            n_alerts = 0
        return status, n_alerts

    # Object with attributes
    for attr_status in ['status']:
        if hasattr(res, attr_status):
            status = str(getattr(res, attr_status))
            if hasattr(res, 'n_alerts') and isinstance(getattr(res, 'n_alerts'), int):
                return status, int(getattr(res, 'n_alerts'))
            if hasattr(res, 'alerts') and isinstance(getattr(res, 'alerts'), (list, tuple)):
                return status, len(getattr(res, 'alerts'))
            if hasattr(res, 'reasons') and isinstance(getattr(res, 'reasons'), (list, tuple)):
                return status, len(getattr(res, 'reasons'))
            return status, 0

    return None, 0


def decide_pass(status: str, n_alerts: int) -> bool:
    if n_alerts == 0 and (status == 'ok' or status == 'annotations'):
        return True
    return False


def write_output(path: str, n_alerts: int, status: str, passed: bool) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"Common alerts: {n_alerts}\n")
        f.write(f"Status: {status}\n")
        f.write(f"Pass: {'yes' if passed else 'no'}\n")


def main():
    ap = argparse.ArgumentParser(description='Run MedChem Common Alerts on a SMILES string and write standardized output.')
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument('--smiles', help='SMILES string')
    grp.add_argument('--infile', help='Path to input file with a SMILES on the first non-empty line')
    ap.add_argument('--outfile', required=True, help='Path to write the three-line result')
    args = ap.parse_args()

    smiles = args.smiles if args.smiles is not None else read_smiles_from_file(args.infile)
    if not smiles:
        write_output(args.outfile, 0, 'error', False)
        return

    filter_obj, err = try_import_filter()
    if filter_obj is None:
        status = 'error'
        n_alerts = 0
    else:
        status, n_alerts = call_filter(filter_obj, smiles)

    passed = decide_pass(status, n_alerts)
    write_output(args.outfile, n_alerts, status, passed)


if __name__ == '__main__':
    main()
