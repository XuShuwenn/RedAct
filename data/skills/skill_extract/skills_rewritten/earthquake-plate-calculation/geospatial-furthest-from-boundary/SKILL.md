---
name: geospatial-furthest-from-boundary
description: "Find the point within a region that is farthest from that region’s boundary using GeoPandas projections and robust distance computation."
---

# Geospatial: Farthest Point From Boundary (Projected Workflow)

Reusable workflow to identify, among many points inside a region (polygon), the one farthest from that region’s boundary. Typical applications include earthquakes inside a tectonic plate, facilities inside an administrative area, or observations inside any domain polygon. Distances are computed with GeoPandas/Shapely in a distance-preserving projected CRS.

## When to Use

Activate this skill when you need to:
- Filter points to those inside a target polygon/region
- Compute each point’s minimum distance to the region’s boundary lines
- Select the point with the maximum of these distances
- Produce consistent, verifiable results using GeoPandas projections

## Core Workflow

1) Inspect and Load Data
- Load points (e.g., earthquakes) and polygons (e.g., plates/regions) with GeoPandas read_file. Ensure both are in a geographic CRS (lat/long), typically EPSG:4326.
- If boundaries are provided separately as line features, load those as well. If not, you can derive a boundary from the polygon exterior; however, prefer an authoritative boundary dataset when provided.

2) Identify the Target Region
- Select the target polygon by an identifying attribute (e.g., code or name). Handle case differences and alternative field names.
- If the region consists of multiple parts, dissolve/group to a single MultiPolygon for containment and centroid calculations.

3) Filter Points to Inside the Region
- Ensure both points and polygon share the same CRS (reproject if needed).
- Use a spatial join or a predicate (covered_by/within) to include points inside (and optionally on) the polygon boundary.

4) Select/Assemble the Boundary Geometry
- If a boundary dataset exists with segments that store “sides” (e.g., left/right plate IDs), include segments where either side equals the target region identifier.
- Dissolve/unify the selected boundary segments into a single LineString/MultiLineString via unary_union.
- If no boundary dataset is provided, derive the boundary from the polygon exterior.

5) Choose a Distance-Preserving Projection
- Build a local Azimuthal Equidistant (AEQD) projection centered on the target polygon centroid. This preserves distances well within the region extent.
- Example proj string: +proj=aeqd +lat_0={centroid_lat} +lon_0={centroid_lon} +x_0=0 +y_0=0 +units=m +no_defs

6) Project and Compute Distances
- Reproject both the filtered points and the unified boundary to the local AEQD CRS.
- Compute each point’s Euclidean distance to the boundary geometry (meters), then convert to kilometers and round as required.
- Select the point with the maximum distance.

7) Prepare Outputs
- Include the requested attributes (e.g., id, place, magnitude, coordinates).
- Convert time fields to ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ). Detect epoch seconds vs milliseconds when necessary.
- Write a JSON file with the required schema and numeric rounding.

## Verification

Perform these checks before finalizing:
- CRS and Projection
  - Confirm points and polygon share the same CRS before containment filtering.
  - Confirm both points and boundary were reprojected to the same local AEQD CRS before distance calculations.
- Boundary Completeness
  - If boundaries encode sides, verify both directions (e.g., left/right) were included.
  - Ensure the unified boundary geometry is non-empty and valid.
- Containment
  - Verify the selected “furthest” point is covered_by the target polygon.
- Distance Sanity
  - For the top 1–3 candidates, cross-check distances using an alternative projection (e.g., a different AEQD centered nearby). Distances should be stable within a small tolerance.
  - Optionally validate 1–2 candidates with geodesic line sampling (e.g., pyproj.Geod) for approximate agreement.
- Time Formatting
  - Confirm output time is ISO 8601 UTC with trailing Z and not a raw epoch value.
- Output Schema
  - Ensure required keys exist, numeric fields are floats where expected, and distances are rounded as specified.

## Common Pitfalls

- Computing distances in degrees (unprojected). Always project to a metric CRS before using geometry.distance.
- Using an inappropriate CRS (e.g., Web Mercator) for long-range distances. Prefer a local AEQD centered on the region.
- Missing half the boundary because only one side of side-encoded segments was filtered. Include segments where either side equals the target identifier.
- Using polygon exterior as a boundary when a more detailed, authoritative boundary dataset is provided.
- Not dissolving/unifying boundary segments. Disjoint segments can still work, but unifying simplifies and can improve performance.
- Containment edge cases: using within excludes boundary-touching points. Prefer covered_by or within with a tiny buffer if edge cases matter.
- Time conversion mistakes: mixing seconds vs milliseconds. Detect and normalize before formatting to ISO 8601.
- Antimeridian effects: a local AEQD projection mitigates wraparound issues. Avoid relying on bounding boxes in lon/lat.

## Success Criteria

- The selected point is inside the target region.
- Distances computed in a metric CRS are stable under a reasonable alternative projection check.
- The boundary geometry represents the true region boundary (authoritative dataset if available).
- Output JSON includes all required fields with correct formats and rounding.

## Optional Script Usage

A helper module is provided to streamline projection, distance calculation, and time formatting.

Example usage:

- Build local AEQD CRS centered on the region
- Dissolve boundary geometries and compute distances
- Select the furthest point and format time

Pseudocode:
- Load points, polygon, boundaries
- Filter points to inside polygon
- boundary_union = unary_union(boundaries_for_region)
- crs = build_local_aeqd_crs(polygon.geometry)
- distances_km, idx = max_point_to_boundary_distance(points, boundary_union, crs)
- iso_time = isoformat_time(points.loc[idx, 'time'])
- Write output JSON
