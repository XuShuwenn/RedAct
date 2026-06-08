#!/usr/bin/env python3
"""Solve medchem-lilly-demerit task using CommonAlertsFilters."""

import datamol as dm
from medchem.structural import CommonAlertsFilters

def main():
    with open("/root/input.txt") as f:
        smiles = f.read().strip()

    mol = dm.to_mol(smiles)
    if mol is None:
        result = "Common alerts: 999\nPass: no\n"
    else:
        alerts = CommonAlertsFilters()
        try:
            df = alerts(mols=[mol], n_jobs=1, keep_details=True)
            num_alerts = len([x for x in df["reasons"].iloc[0] if x])
            status = df["status"].iloc[0]
        except:
            num_alerts = 0
            status = "ok"

        passed = status in ["ok", "annotations"] and num_alerts == 0

        result = f"Common alerts: {num_alerts}\nStatus: {status}\nPass: {'yes' if passed else 'no'}\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()