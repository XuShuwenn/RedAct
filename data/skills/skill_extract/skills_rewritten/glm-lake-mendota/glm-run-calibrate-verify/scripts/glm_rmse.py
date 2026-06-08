#!/usr/bin/env python3
"""
Compute RMSE between GLM NetCDF temperature output and field observations.

Usage:
  python3 scripts/glm_rmse.py \
    --nc path/to/output.nc \
    --obs path/to/observations.csv \
    [--obs-time-col datetime] [--obs-depth-col depth] [--obs-temp-col temp] \
    [--nc-temp-var temp] [--nc-time-var time] [--nc-depth-var depth] \
    [--start YYYY-MM-DD] [--end YYYY-MM-DD] \
    [--time-tol-hours 12]

Notes:
- Aligns observations to model by nearest time within tolerance and nearest depth level.
- Ignores pairs with missing values; reports matched count and RMSE.
- Tries common depth variable names if --nc-depth-var is not provided.
"""

import argparse
import sys
import os
import math
from datetime import datetime

import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date


def _find_first_var(ds, candidates):
    for name in candidates:
        if name in ds.variables:
            return name
    return None


def _to_datetime_index(nc_time_var):
    units = getattr(nc_time_var, 'units', None)
    calendar = getattr(nc_time_var, 'calendar', 'standard')
    times = num2date(nc_time_var[:], units=units, calendar=calendar)
    # Convert to pandas DatetimeIndex (coerce cftime to numpy datetime64 if possible)
    # Fallback: use pandas to_datetime on string representations
    try:
        t_series = pd.to_datetime(times)
    except Exception:
        t_series = pd.to_datetime([str(t) for t in times])
    return pd.DatetimeIndex(t_series)


def nearest_index(sorted_index: pd.DatetimeIndex, target: pd.Timestamp):
    pos = sorted_index.searchsorted(target)
    if pos == 0:
        return 0
    if pos == len(sorted_index):
        return len(sorted_index) - 1
    before = sorted_index[pos - 1]
    after = sorted_index[pos]
    if abs((after - target).value) < abs((target - before).value):
        return pos
    return pos - 1


def compute_rmse(nc_path, obs_path, obs_time_col, obs_depth_col, obs_temp_col,
                 nc_temp_var, nc_time_var, nc_depth_var, start, end,
                 time_tol_hours):
    if not os.path.exists(nc_path):
        raise FileNotFoundError(f"Missing NetCDF: {nc_path}")
    if not os.path.exists(obs_path):
        raise FileNotFoundError(f"Missing observations: {obs_path}")

    # Load observations
    df = pd.read_csv(obs_path)
    if obs_time_col not in df.columns:
        raise ValueError(f"Observation time column '{obs_time_col}' not found")
    if obs_depth_col not in df.columns:
        raise ValueError(f"Observation depth column '{obs_depth_col}' not found")
    if obs_temp_col not in df.columns:
        # try common fallbacks
        for cand in ["wtr", "temperature", "temp_c", "Temp", "TEMP"]:
            if cand in df.columns:
                obs_temp_col = cand
                break
        else:
            raise ValueError(f"Observation temp column '{obs_temp_col}' not found")

    df[obs_time_col] = pd.to_datetime(df[obs_time_col])
    if start:
        df = df[df[obs_time_col] >= pd.to_datetime(start)]
    if end:
        df = df[df[obs_time_col] <= pd.to_datetime(end)]

    df = df.dropna(subset=[obs_time_col, obs_depth_col, obs_temp_col])

    # Load model output
    with Dataset(nc_path, 'r') as ds:
        time_name = nc_time_var or _find_first_var(ds, ["time", "Times", "t"])
        if time_name is None:
            raise ValueError("Could not find time variable in NetCDF")
        tindex = _to_datetime_index(ds.variables[time_name])

        # Determine depth variable and temperature variable
        depth_name = nc_depth_var or _find_first_var(ds, ["depth", "z", "depths", "lev", "layer"])
        if depth_name is None:
            # some GLM outputs encode depth as a coordinate dimension without a var; try dimension name
            depth_name = next((d for d in ds.dimensions.keys() if d.lower() in ("depth", "z", "layer", "lev")), None)
        if depth_name is None:
            raise ValueError("Could not find depth variable or dimension in NetCDF")

        temp_name = nc_temp_var or _find_first_var(ds, ["temp", "temperature", "water_temperature"]) 
        if temp_name is None:
            raise ValueError("Could not find temperature variable in NetCDF")

        # Extract depth levels
        if depth_name in ds.variables:
            depths = np.array(ds.variables[depth_name][:], dtype=float).ravel()
        else:
            # if it's only a dimension without variable, infer depth indices as 0..n-1 (not ideal, but avoids crash)
            depths = np.arange(len(ds.dimensions[depth_name]), dtype=float)

        temp_var = ds.variables[temp_name]
        temp_data = np.array(temp_var[:])  # expect shape (time, depth) or (time, depth, ...)

    # Standardize temp_data shape to (time, depth)
    if temp_data.ndim > 2:
        temp_data = temp_data[:, :, ...]
        temp_data = temp_data.reshape(temp_data.shape[0], temp_data.shape[1], -1)
        temp_data = temp_data[:, :, 0]
    if temp_data.ndim != 2:
        raise ValueError(f"Unexpected temperature array shape: {temp_data.shape}")

    # Optional time window derived from model
    model_start, model_end = tindex.min(), tindex.max()
    df = df[(df[obs_time_col] >= model_start) & (df[obs_time_col] <= model_end)]

    # Build matched pairs using nearest in time and depth
    time_tol = pd.Timedelta(hours=time_tol_hours)
    obs_times = df[obs_time_col].to_numpy()
    obs_depths = df[obs_depth_col].astype(float).to_numpy()
    obs_temps = df[obs_temp_col].astype(float).to_numpy()

    matched_model = []
    matched_obs = []

    # Precompute for speed
    tindex_values = tindex.values  # numpy datetime64[ns]

    # Depth nearest mapping
    depths_arr = np.asarray(depths)

    for t_obs, z_obs, y_obs in zip(obs_times, obs_depths, obs_temps):
        if pd.isna(t_obs) or pd.isna(z_obs) or pd.isna(y_obs):
            continue
        t_obs = pd.Timestamp(t_obs)
        ti = nearest_index(tindex, t_obs)
        dt = abs(tindex[ti] - t_obs)
        if dt > time_tol:
            continue
        # nearest depth
        zi = int(np.nanargmin(np.abs(depths_arr - z_obs)))
        y_model = temp_data[ti, zi]
        if np.isnan(y_model) or np.isnan(y_obs):
            continue
        matched_model.append(float(y_model))
        matched_obs.append(float(y_obs))

    matched_model = np.array(matched_model)
    matched_obs = np.array(matched_obs)

    if matched_model.size == 0:
        raise ValueError("No matched pairs within tolerance; check time/depth alignment and inputs.")

    mse = np.mean((matched_model - matched_obs) ** 2)
    rmse = float(np.sqrt(mse))

    result = {
        "nc_path": nc_path,
        "obs_path": obs_path,
        "model_period_start": str(model_start),
        "model_period_end": str(model_end),
        "matches": int(matched_model.size),
        "rmse_c": rmse,
    }
    return result


def main():
    p = argparse.ArgumentParser(description="Compute RMSE between GLM NetCDF output and observations")
    p.add_argument("--nc", required=True, help="Path to model NetCDF output")
    p.add_argument("--obs", required=True, help="Path to observations CSV")
    p.add_argument("--obs-time-col", default="datetime")
    p.add_argument("--obs-depth-col", default="depth")
    p.add_argument("--obs-temp-col", default="temp")
    p.add_argument("--nc-temp-var", default=None)
    p.add_argument("--nc-time-var", default=None)
    p.add_argument("--nc-depth-var", default=None)
    p.add_argument("--start", default=None)
    p.add_argument("--end", default=None)
    p.add_argument("--time-tol-hours", type=float, default=12.0)
    args = p.parse_args()

    try:
        out = compute_rmse(
            args.nc, args.obs,
            args.obs_time_col, args.obs_depth_col, args.obs_temp_col,
            args.nc_temp_var, args.nc_time_var, args.nc_depth_var,
            args.start, args.end, args.time_tol_hours
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Simple, parseable output
    for k, v in out.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
