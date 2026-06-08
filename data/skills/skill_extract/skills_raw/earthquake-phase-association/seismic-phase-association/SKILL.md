---
name: seismic-phase-association
description: "Run deep-learning phase picking (SeisBench) and robustly associate picks into earthquakes with GaMMA, with ID alignment, timestamp, projection, and config sanity checks."
---

Seismic Phase Association

This skill turns continuous multi-station waveform data into an event list by:
- picking P and S arrivals with SeisBench (e.g., PhaseNet)
- associating picks into earthquakes with GaMMA using a simple velocity model
- writing an events CSV with ISO timestamps

When to Use
- You have MSEED (or ObsPy-readable) waveforms and a CSV of station metadata (network, station, channel, longitude, latitude, elevation, response).
- You need an event catalog (origin times) from continuous data via phase picking + association.
- You can assume a uniform velocity model (e.g., vp and vs derived via a fixed ratio).

Core Workflow

1) Load data
- Waveforms: use ObsPy to read MSEED into a Stream.
- Stations: read CSV with columns network, station, channel, longitude, latitude, elevation_m, response.

2) Prepare station table for association
- Collapse per-station (not per-channel). Group by network,station and keep one row per station.
- Build station id that will match picks. For SeisBench PhaseNet classify results, picks trace_id usually encodes network and station (location may be empty). A robust convention is to normalize both stations and picks to id = "NET.STA." (two parts plus a trailing dot), which matches many SeisBench outputs.
- Project lon/lat to a local Cartesian in kilometers. Prefer pyproj (local stereographic centered at the array mean). If pyproj is unavailable, use an equirectangular approximation with km per degree based on mean latitude.
- Set z(km) = -elevation_m / 1000.0 (depth positive downward).

Example projection fallback:
```
import numpy as np
lon0 = stations['longitude'].mean()
lat0 = stations['latitude'].mean()
km_per_deg_lat = 110.574
km_per_deg_lon = 111.320 * np.cos(np.deg2rad(lat0))
stations['x(km)'] = (stations['longitude'] - lon0) * km_per_deg_lon
stations['y(km)'] = (stations['latitude'] - lat0) * km_per_deg_lat
stations['z(km)'] = -stations['elevation_m'] / 1000.0
stations = stations[['id','x(km)','y(km)','z(km)']]
```

3) Phase picking with SeisBench
- Use a pretrained model such as PhaseNet.
- Input: the full ObsPy Stream (multi-station, multi-channel). Optionally apply per-trace z-score normalization to mitigate extreme raw counts.
- Call model.classify(stream, P_threshold=..., S_threshold=...). The return is a ClassifyOutput; access picks via output.picks.
- For each pick, extract:
  - id: normalize to "NET.STA." from pick.trace_id (split on dots, keep network and station, then add trailing dot).
  - timestamp: use pick.peak_time.datetime, convert to pandas Timestamp with UTC.
  - type: pick.phase.lower() ('p' or 's').
  - prob: float(pick.peak_value).
- Do not rely on amplitude; set use_amplitude=False in GaMMA to keep the interface simple.

Example pick extraction:
```
co = model.classify(stream, P_threshold=0.3, S_threshold=0.3)
rows = []
for p in co.picks:
    parts = p.trace_id.split('.')
    net, sta = parts[0], parts[1]
    rows.append({
        'id': f"{net}.{sta}.",
        'timestamp': pd.to_datetime(p.peak_time.datetime, utc=True),
        'type': p.phase.lower(),
        'prob': float(p.peak_value),
    })
picks = pd.DataFrame(rows)
```

4) Align IDs between picks and stations
- Ensure picks['id'] and stations['id'] share the same format. Compute and log intersections and missing IDs before association; if there is a mismatch, normalize one side.
- Typical normalization for stations: stations['id'] = stations['network'] + '.' + stations['station'] + '.'

5) Configure GaMMA
- Required keys:
  - dims: ["x(km)", "y(km)", "z(km)"]
  - vel: {"p": vp, "s": vs} (vs can be vp/1.75 as a rule of thumb)
  - min_picks_per_eq: e.g., 4–6 (tune for precision/recall)
  - x(km), y(km), z(km): coordinate bounds as tuples (min, max)
  - bfgs_bounds: ((x_min,x_max),(y_min,y_max),(z_min,z_max),(None,None))
- Recommended:
  - use_dbscan: True; dbscan_eps from gamma.utils.estimate_eps(stations, vp) with fallback to a reasonable constant if estimation fails; dbscan_min_samples ~ 3
  - oversample_factor: integer (e.g., 5). Make sure it is int to avoid slicing errors.
  - use_amplitude: False (then no amp column needed)
  - ncpu: 1 (avoid multiprocessing hangs in constrained environments)

Example config skeleton:
```
x_min, x_max = stations['x(km)'].min()-10, stations['x(km)'].max()+10
y_min, y_max = stations['y(km)'].min()-10, stations['y(km)'].max()+10
z_min, z_max = 0.0, 30.0
try:
    from gamma.utils import estimate_eps
    eps = estimate_eps(stations, vp)
except Exception:
    eps = 20.0
config = {
  'dims': ['x(km)','y(km)','z(km)'],
  'vel': {'p': vp, 's': vs},
  'min_picks_per_eq': 5,
  'use_dbscan': True,
  'dbscan_eps': eps,
  'dbscan_min_samples': 3,
  'x(km)': (x_min, x_max),
  'y(km)': (y_min, y_max),
  'z(km)': (z_min, z_max),
  'bfgs_bounds': ((x_min, x_max),(y_min, y_max),(z_min, z_max),(None,None)),
  'use_amplitude': False,
  'oversample_factor': 5,  # int
  'ncpu': 1,
}
```

6) Run association and write output
- Call gamma.utils.association(picks, stations, config, method='BGMM').
- Build a DataFrame of events and write to CSV with a column "time" in ISO format without timezone.
- Ensure timestamps are naive ISO strings (no tz). Example:
```
out = []
for ev in events:
    t = pd.to_datetime(ev.get('time'))
    if getattr(t, 'tzinfo', None) is not None:
        t = t.tz_convert(None)
    out.append({'time': t.isoformat(timespec='milliseconds')})
pd.DataFrame(out).drop_duplicates().sort_values('time').to_csv(output_path, index=False)
```

Verification
- Before association:
  - Picks non-empty and contain both phases when expected.
  - picks['timestamp'] dtype is datetime64 with UTC (not object/str).
  - Station-projected columns present: ['id','x(km)','y(km)','z(km)'].
  - ID alignment: len(set(picks['id']) ∩ set(stations['id'])) > 0.
- Config completeness:
  - dims, vel, min_picks_per_eq present.
  - x(km), y(km), z(km) bounds present.
  - oversample_factor is int.
- Output:
  - /results.csv-like file exists.
  - Column 'time' present, ISO format, no timezone suffix.
  - Event times fall within the waveform time span (with small propagation margin).

Common Pitfalls and Fixes
- Mistaking classify output for a list
  - Symptom: TypeError when iterating or missing attributes.
  - Fix: Use output.picks from SeisBench's ClassifyOutput.
- Wrong pick attributes
  - Use pick.peak_time and pick.peak_value; not generic names like time/score.
- ID mismatch between picks and stations
  - Picks often use network.station.(location) without channel. Normalize both to 'NET.STA.'; log intersections and correct before association.
- Timestamp dtype issues
  - Do not store timestamps as strings before association. Use pandas Timestamp with UTC: pd.to_datetime(..., utc=True).
- Missing GaMMA bounds keys
  - Include 'x(km)', 'y(km)', 'z(km)' in config; also set bfgs_bounds.
- oversample_factor as float
  - Some GaMMA paths cast slice sizes from this value; ensure it is an int to avoid TypeErrors.
- Multiprocessing hangs
  - Set 'ncpu': 1 to disable multiprocessing in restricted environments.
- Amplitude handling complexity
  - Start with use_amplitude=False to reduce required columns; add amplitude later if needed.

Optional Script Usage
- This repo includes a deterministic input validator to de-risk GaMMA runs by checking timestamp dtype and ID alignment, and by producing a projected stations table.
- Example:
```
python scripts/assoc_sanity_check.py \
  --picks picks.csv \
  --stations stations.csv \
  --out-picks picks_norm.csv \
  --out-stations stations_gamma.csv
```
- Use the normalized outputs to feed GaMMA:
  - picks_norm.csv: ensured datetime dtype and normalized 'id' format
  - stations_gamma.csv: ['id','x(km)','y(km)','z(km)']

Success Criteria
- Produces a CSV of events with a 'time' column in ISO format (no timezone).
- Event times match ground truth within several seconds when evaluated, driven by sensible thresholds and min_picks settings.
