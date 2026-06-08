---
name: projected-boundary-distance
description: "Compute distances from point events to the nearest relevant boundary within a parent polygon using GeoPandas projections, then select the extremal case (e.g., farthest)."
---

# Projected Boundary Distance Analysis

A reusable workflow to:
- load points (e.g., events) and polygons (e.g., plates) from GeoJSON,
- filter points by containment within a chosen polygon,
- assemble the relevant boundary network for that polygon,
- project to a metric CRS and compute point-to-boundary distances, and
- select the extremal point (e.g., farthest) and produce validated outputs.

This pattern applies to plates and plate boundaries, administrative regions and borders, protected areas and perimeters, and similar tasks.

## When to Use
Activate this skill when you need to:
- find the point inside a given polygon that is farthest (or nearest) to that polygon’s boundary network;
- compute accurate distances using GeoPandas projections (not degree units);
- output a structured record for the selected point with derived metrics (e.g., distance_km) and normalized timestamps.

## Core Workflow

1) Inspect and Load Data
- Read all inputs with GeoPandas. Confirm geometry and attribute columns.
- Typical layers:
  - Points: events with geometry or lon/lat plus attributes (id, time, magnitude, etc.).
  - Polygons: parent areas (e.g., a specific region/plate) with an identifier column (e.g., Code or Name).
  - Boundaries: line features linking two areas (e.g., PlateA/PlateB) used as the distance target.

2) Identify the Target Polygon
- Select the polygon feature(s) representing the region of interest by a stable identifier (e.g., code) with a robust fallback to a name search.
- Build a single polygon geometry via unary union.

3) Filter Points by Containment
- Ensure points are in EPSG:4326 (WGS84).
- Use within(target_polygon) to keep only points inside the region. If result is empty, verify attributes, polygon identifier, and antimeridian/geometry validity; optionally try a zero-distance fix (buffer(0)) on the polygon.

4) Build the Relevant Boundary Geometry
- Filter the boundary layer to segments associated with the target polygon (e.g., rows where attribute A or B equals the target code).
- Combine all boundary segments into a single geometry (MultiLineString) via a robust union function (see script helper or examples below).

5) Choose a Projection and Compute Distances
- Project both the filtered points and the boundary union to the same metric CRS before measuring distance.
  - Default: a global equidistant-like CRS such as EPSG:4087 (World Equidistant Cylindrical) for scalable simplicity.
  - Advanced (higher fidelity): per-point Azimuthal Equidistant (AEQD) centered at each point; compute distance to the same boundary (reprojected per point). This is slower but minimizes distortion.
- Compute distances in meters; convert to kilometers.

6) Select the Extremal Point and Prepare Output
- Select by idxmax (farthest) or idxmin (nearest) on the distance column.
- Normalize time (e.g., milliseconds since epoch) to ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ).
- Round distance_km to 2 decimals and include necessary attributes.

## Reference Implementation (concise pattern)

- Robust geometry union (handles different Shapely/GeoPandas versions):
```python
from shapely.ops import unary_union as ops_unary_union

def union_geoms(gdf):
    # Try GeoSeries.union_all (newer) then .unary_union, else shapely.ops
    gs = gdf.geometry
    if hasattr(gs, "union_all"):
        return gs.union_all()
    if hasattr(gs, "unary_union"):
        return gs.unary_union
    return ops_unary_union(gs)
```

- Main steps sketch:
```python
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime, timezone

# 1) Load
points = gpd.read_file(points_path)            # EPSG:4326 expected
polys  = gpd.read_file(polygons_path)          # EPSG:4326 expected
bounds = gpd.read_file(boundaries_path)        # EPSG:4326 expected

# 2) Target polygon selection (prefer code, fallback to name contains)
poly_sel = polys[polys[target_code_col] == target_code]
if len(poly_sel) == 0 and target_name_col and target_name_value:
    poly_sel = polys[polys[target_name_col].str.contains(target_name_value, case=False, na=False)]
poly_geom = union_geoms(poly_sel)

# 3) Filter points inside polygon
points = points.set_crs("EPSG:4326", allow_override=True)
inside = points[points.within(poly_geom)].copy()
if inside.empty:
    # Optional repair
    try:
        inside = points[points.within(poly_geom.buffer(0))].copy()
    except Exception:
        pass

# 4) Relevant boundaries
rel_bounds = bounds[(bounds[bound_col_a] == target_code) | (bounds[bound_col_b] == target_code)]
bound_union = union_geoms(rel_bounds)

# 5) Project and measure
METRIC_CRS = "EPSG:4087"
inside_proj = inside.to_crs(METRIC_CRS)
bounds_proj = gpd.GeoSeries([bound_union], crs="EPSG:4326").to_crs(METRIC_CRS).iloc[0]
inside_proj["distance_m"] = inside_proj.geometry.distance(bounds_proj)
inside_proj["distance_km"] = inside_proj["distance_m"] / 1000.0

# 6) Select extremal
choice = inside_proj.loc[inside_proj["distance_km"].idxmax()]
# Normalize time if milliseconds since epoch
if isinstance(choice.get("time"), (int, float)):
    iso_time = datetime.fromtimestamp(choice["time"] / 1000.0, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
else:
    iso_time = str(choice.get("time"))

result = {
    "id": choice.get("id"),
    "place": choice.get("place"),
    "time": iso_time,
    "magnitude": float(choice.get("mag", choice.get("magnitude", 0)) or 0),
    "latitude": float(choice.geometry.y),
    "longitude": float(choice.geometry.x),
    "distance_km": round(float(choice["distance_km"]), 2)
}
```

- Advanced per-point AEQD (optional):
```python
from shapely.ops import unary_union

def aeqd_distance_km(pt_wgs84, lines_gdf_wgs84):
    lat = pt_wgs84.y
    lon = pt_wgs84.x
    aeqd = f"+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs"
    pt_proj = gpd.GeoSeries([pt_wgs84], crs="EPSG:4326").to_crs(aeqd).iloc[0]
    lines_proj = lines_gdf_wgs84.to_crs(aeqd)
    line_union = union_geoms(lines_proj)
    return pt_proj.distance(line_union) / 1000.0
```
Use AEQD for higher precision at the cost of computation time.

## Verification
Perform these checks before finalizing:
- Data integrity
  - Non-empty target polygon selection; confirm the identifier and column names.
  - Non-empty filtered points within the polygon.
  - Non-empty boundary subset for the target polygon.
- CRS and distance sanity
  - Ensure points and boundaries are projected to the same metric CRS before measuring.
  - Distances are strictly positive; farthest_distance >= nearest_distance.
  - Spot-check 1–3 points with the AEQD method; results should be close to the simpler global projection (within a small percentage for large-scale cases).
- Geometry containment
  - Confirm the selected extremal point is within the target polygon via within().
- Timestamp normalization
  - If time is numeric and large (likely milliseconds), divide by 1000 before converting to ISO. If it’s already an ISO string, pass through.
- Output schema
  - Include all required fields; round distance to 2 decimals; ensure numeric types are serializable.

## Common Pitfalls and How to Avoid Them
- Using degree units for distance
  - Symptom: extremely small distances or values that make no sense.
  - Fix: Always project to a metric CRS and confirm gdf.crs is set correctly before calling distance().
- CRS mismatch between layers
  - Symptom: distances or containment checks fail or return empty/incorrect results.
  - Fix: Reproject both the point layer and the boundary union to the same metric CRS; keep the original data in EPSG:4326 for filtering and selection steps that depend on global coordinates.
- Wrong boundary subset
  - Symptom: distances measured to unrelated boundaries; results not plausible.
  - Fix: Filter boundary segments by the target polygon’s identifier across both boundary-side columns (e.g., A or B).
- Not unifying boundary segments
  - Symptom: vectorized distance misbehavior or unexpected arrays.
  - Fix: Compute a single union geometry of all relevant boundary segments and measure each point’s distance to that union.
- Empty containment due to geometry quirks (antimeridian, tiny gaps, or invalid rings)
  - Symptom: zero points within the polygon.
  - Fix: Validate target polygon; try polygon.buffer(0) or repair; verify that the points truly lie in the region and that identifiers were correct.
- Timestamp unit confusion
  - Symptom: incorrect ISO times far in the past/future.
  - Fix: Detect milliseconds (typical large values) and divide by 1000 before conversion.

## Success Criteria
- The selected point lies within the chosen polygon.
- Distances are computed in kilometers using a valid projected CRS.
- Boundary geometry used is the correct union of all relevant segments.
- Output contains requested fields with correct types and rounding.

## Optional Script Usage
This skill ships with a small helper module for robust geometry unions, projection, distance computation, and time normalization. See scripts/geo_helpers.py for details.

Example usage snippet:
```python
from scripts.geo_helpers import union_geoms_safe, to_metric, ms_to_iso8601

# After loading and filtering to inside points and relevant boundaries:
inside_proj = to_metric(inside, "EPSG:4087")
bounds_union = union_geoms_safe(rel_bounds)
bounds_proj = to_metric(gpd.GeoDataFrame(geometry=[bounds_union], crs="EPSG:4326"), "EPSG:4087").geometry.iloc[0]
inside_proj["distance_km"] = inside_proj.geometry.distance(bounds_proj) / 1000.0
chosen = inside_proj.loc[inside_proj["distance_km"].idxmax()]
iso = ms_to_iso8601(chosen.get("time"))
```
