#!/usr/bin/env python3
"""GLM skill helper utilities: NetCDF reading, observation loading, RMSE, namelist editing, and runner.

Functions:
- parse_time_vector(nc, time_var='time', default_origin=None, default_unit='hours')
- read_glm_output(nc_path, lake_depth)
- read_observations(csv_path, time_col='datetime', depth_col='depth', temp_col='temp')
- rmse_by_match(sim_df, obs_df)
- modify_nml(nml_path, params)
- run_glm(cwd='.')

All functions are generic and do not depend on task-specific constants.
"""

import re
import os
import subprocess
from typing import Tuple, Dict, Optional

import numpy as np
import pandas as pd
from netCDF4 import Dataset


def parse_time_vector(nc: Dataset,
                      time_var: str = 'time',
                      default_origin: Optional[pd.Timestamp] = None,
                      default_unit: str = 'hours') -> pd.Series:
    """Parse NetCDF time variable into pandas Timestamps.

    Attempts to use the units attribute (e.g., "hours since YYYY-MM-DD HH:MM:SS").
    Falls back to default_origin and default_unit when units are missing or unparsable.
    Supported units: seconds, minutes, hours, days.
    """
    var = nc.variables[time_var]
    vals = np.array(var[:], dtype=float)
    units = getattr(var, 'units', '') or ''
    units_l = units.lower()

    origin = None
    scale = None

    # Try parsing units like "hours since 2009-01-01 12:00:00"
    if 'since' in units_l:
        # Extract unit and origin
        # Accept flexible separators; capture everything after 'since'
        m = re.search(r"(seconds|minutes|hours|days)\s+since\s+([0-9\-:Tt\s]+)", units_l)
        if m:
            unit = m.group(1)
            origin_str = m.group(2).strip().replace('t', ' ').replace('T', ' ')
            try:
                origin = pd.to_datetime(origin_str)
                scale = unit
            except Exception:
                origin = None

    if origin is None:
        # Fallbacks
        origin = default_origin or pd.Timestamp('2009-01-01 12:00:00')
        scale = default_unit.lower()

    # Map unit to pandas Timedelta
    if scale.startswith('sec'):
        td = pd.to_timedelta(vals, unit='s')
    elif scale.startswith('min'):
        td = pd.to_timedelta(vals, unit='m')
    elif scale.startswith('hour'):
        td = pd.to_timedelta(vals, unit='h')
    elif scale.startswith('day'):
        td = pd.to_timedelta(vals, unit='D')
    else:
        # Final fallback: treat as hours
        td = pd.to_timedelta(vals, unit='h')

    return pd.Series(origin + td)


def _safe_slice_layer(arr, t_idx: int):
    """Return 1D layer array at time index t_idx from z/temp arrays of varying shape."""
    a = arr
    if a.ndim == 1:
        return a
    if a.ndim == 2:
        return a[t_idx, :]
    if a.ndim == 3:
        # choose first lateral dims if present
        return a[t_idx, :, 0]
    if a.ndim == 4:
        return a[t_idx, :, 0, 0]
    # Unknown shape
    raise ValueError(f"Unsupported array shape: {a.shape}")


def read_glm_output(nc_path: str, lake_depth: float) -> pd.DataFrame:
    """Read GLM NetCDF output and produce a dataframe with columns (datetime, depth, temp_sim).

    - Converts heights to depths using lake_depth (depth = lake_depth - height).
    - Rounds depths to integers.
    - Aggregates to mean temperature per (datetime, integer depth).
    """
    if not os.path.exists(nc_path):
        raise FileNotFoundError(f"NetCDF file not found: {nc_path}")

    nc = Dataset(nc_path, 'r')
    try:
        times = parse_time_vector(nc, time_var='time')
        z = nc.variables['z'][:]
        temp = nc.variables['temp'][:]
    finally:
        nc.close()

    records = []
    n_t = len(times)
    for t_idx in range(n_t):
        date = pd.Timestamp(times.iloc[t_idx])
        heights = _safe_slice_layer(z, t_idx)
        temps = _safe_slice_layer(temp, t_idx)

        # Handle masked arrays
        h_mask = np.ma.getmaskarray(heights)
        t_mask = np.ma.getmaskarray(temps)
        valid = ~(h_mask | t_mask)
        if np.ndim(valid) == 0:
            valid = np.array([bool(valid)])

        h_vals = np.asarray(heights)[valid].astype(float)
        t_vals = np.asarray(temps)[valid].astype(float)

        if h_vals.size == 0:
            continue

        depths = lake_depth - h_vals
        # Keep only within [0, lake_depth]
        keep = (depths >= 0) & (depths <= lake_depth)
        depths = depths[keep]
        t_vals = t_vals[keep]

        if depths.size == 0:
            continue

        depth_int = np.rint(depths).astype(int)
        for d, tv in zip(depth_int, t_vals):
            records.append({'datetime': date, 'depth': int(d), 'temp_sim': float(tv)})

    df = pd.DataFrame.from_records(records)
    if df.empty:
        return df
    return df.groupby(['datetime', 'depth'], as_index=False).agg({'temp_sim': 'mean'})


def read_observations(csv_path: str,
                      time_col: str = 'datetime',
                      depth_col: str = 'depth',
                      temp_col: str = 'temp') -> pd.DataFrame:
    """Load observations and normalize columns: (datetime, depth, temp_obs)."""
    df = pd.read_csv(csv_path)
    df = df.rename(columns={time_col: 'datetime', depth_col: 'depth', temp_col: 'temp_obs'})
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['depth'] = df['depth'].round().astype(int)
    return df[['datetime', 'depth', 'temp_obs']]


def rmse_by_match(sim_df: pd.DataFrame, obs_df: pd.DataFrame) -> Tuple[float, int]:
    """Compute RMSE after inner join on (datetime, depth). Returns (rmse, matched_count).
    If no matches, returns (large_penalty, 0).
    """
    if sim_df is None or obs_df is None or sim_df.empty or obs_df.empty:
        return 999.0, 0
    merged = pd.merge(obs_df, sim_df, on=['datetime', 'depth'], how='inner')
    n = len(merged)
    if n == 0:
        return 999.0, 0
    rmse = float(np.sqrt(np.mean((merged['temp_sim'] - merged['temp_obs'])**2)))
    return rmse, n


def modify_nml(nml_path: str, params: Dict[str, float]) -> None:
    """Modify numeric parameters in a GLM namelist file in-place.

    Regex is anchored to line start and replaces a single numeric value after 'param ='.
    It preserves other formatting and trailing content on the line.
    """
    if not os.path.exists(nml_path):
        raise FileNotFoundError(nml_path)

    with open(nml_path, 'r') as f:
        content = f.read()

    for param, value in params.items():
        # Format floats with reasonable precision; pass through ints unchanged
        if isinstance(value, float):
            val_str = f"{value:.6f}".rstrip('0').rstrip('.') if '.' in f"{value:.6f}" else f"{value:.6f}"
        else:
            val_str = str(value)
        # Regex: start of line (optional spaces), param, '=', numeric token to replace
        pattern = rf"(?im)^(\s*{re.escape(param)}\s*=\s*)([-+0-9\.eE]+)"
        content, nsub = re.subn(pattern, rf"\1{val_str}", content)
        if nsub == 0:
            # Try a more permissive pattern (e.g., values separated by commas)
            pattern2 = rf"(?im)^(\s*{re.escape(param)}\s*=\s*)([^\n,]+)"
            content, _ = re.subn(pattern2, rf"\1{val_str}", content)

    with open(nml_path, 'w') as f:
        f.write(content)


def run_glm(cwd: str = '.') -> Tuple[int, str]:
    """Run GLM in the given working directory. Returns (returncode, combined_output)."""
    try:
        proc = subprocess.run(['glm'], cwd=cwd, capture_output=True, text=True)
        out = (proc.stdout or '') + (proc.stderr or '')
        return proc.returncode, out
    except FileNotFoundError as e:
        return 127, f"GLM executable not found: {e}"


if __name__ == '__main__':
    # Minimal CLI demo (optional): compute RMSE if paths are provided via env vars.
    import os
    nc_path = os.environ.get('GLM_NC')
    obs_path = os.environ.get('OBS_CSV')
    lake_depth = float(os.environ.get('LAKE_DEPTH', '25'))
    if nc_path and obs_path and os.path.exists(nc_path) and os.path.exists(obs_path):
        sim = read_glm_output(nc_path, lake_depth)
        obs = read_observations(obs_path)
        rmse, n = rmse_by_match(sim, obs)
        print(f"RMSE: {rmse:.4f} C (matches: {n})")
    else:
        print("Set GLM_NC, OBS_CSV, and optionally LAKE_DEPTH to compute RMSE.")
