#!/usr/bin/env python3
"""Geospatial helper utilities for finding the point farthest from a region's boundary.

Functions are generic and dataset-agnostic. They assume GeoPandas/Shapely types.

Key capabilities:
- Build a local Azimuthal Equidistant (AEQD) CRS centered on a polygon
- Dissolve/unify boundary segments
- Filter points inside a polygon
- Compute point-to-boundary distances in a projected CRS
- Robust ISO 8601 UTC time formatting from mixed time inputs
"""

from __future__ import annotations

import datetime as _dt
from typing import Iterable, Optional, Tuple

import geopandas as gpd
import pandas as pd
from shapely.geometry import base as shapely_base
from shapely.ops import unary_union
import numpy as np


def ensure_geographic_crs(gdf: gpd.GeoDataFrame, fallback_epsg: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Ensure GeoDataFrame has a geographic CRS. If CRS is None, set to EPSG:4326.
    Does not reproject; only sets when missing.
    """
    if gdf.crs is None:
        gdf = gdf.set_crs(fallback_epsg)
    return gdf


def build_local_aeqd_crs(poly_geom: shapely_base.BaseGeometry) -> str:
    """Return a proj string for a local Azimuthal Equidistant (AEQD) projection
    centered on the centroid of the given polygon geometry (assumed lon/lat).
    """
    if poly_geom is None or poly_geom.is_empty:
        raise ValueError("Polygon geometry is empty or None.")
    centroid = poly_geom.centroid
    lat = float(centroid.y)
    lon = float(centroid.x)
    # AEQD centered at region centroid; units meters
    proj = f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0 +units=m +no_defs"
    return proj


def dissolve_boundaries(boundary_gdf: gpd.GeoDataFrame) -> shapely_base.BaseGeometry:
    """Dissolve/unify boundary segments to a single (Multi)LineString geometry."""
    if boundary_gdf.empty:
        raise ValueError("Boundary GeoDataFrame is empty.")
    geom = unary_union(boundary_gdf.geometry)
    if geom.is_empty:
        raise ValueError("Unified boundary geometry is empty after dissolve.")
    return geom


def filter_points_in_polygon(points: gpd.GeoDataFrame,
                             polygon: shapely_base.BaseGeometry,
                             predicate: str = "covered_by") -> gpd.GeoDataFrame:
    """Return subset of points inside the polygon. Predicate options include
    'within' or 'covered_by'. 'covered_by' includes points on the boundary.
    Assumes points and polygon share the same CRS.
    """
    if predicate not in ("within", "covered_by"):
        raise ValueError("predicate must be 'within' or 'covered_by'")
    # Spatial index-free approach for portability
    mask = points.geometry.apply(lambda g: getattr(g, predicate)(polygon))
    return points.loc[mask].copy()


def max_point_to_boundary_distance(points_ll: gpd.GeoDataFrame,
                                   boundary_ll: shapely_base.BaseGeometry,
                                   local_proj: Optional[str] = None,
                                   distance_col: str = "distance_km") -> Tuple[pd.Series, int]:
    """Compute distances from each point to the boundary and return:
    - distances Series in kilometers (indexed like points_ll)
    - index (row label) of the point with maximum distance

    Inputs must be in lon/lat CRS. The function projects to a local AEQD CRS if
    local_proj is None, using the centroid of the points' convex hull; otherwise
    uses the provided proj string.
    """
    if points_ll.empty:
        raise ValueError("No input points to measure.")
    if boundary_ll is None or boundary_ll.is_empty:
        raise ValueError("Boundary geometry is empty or None.")

    # Ensure CRS on points
    points_ll = ensure_geographic_crs(points_ll)

    # Derive a reasonable local AEQD if not provided (use points hull centroid)
    if local_proj is None:
        hull = points_ll.unary_union.convex_hull
        c = hull.centroid
        local_proj = f"+proj=aeqd +lat_0={float(c.y)} +lon_0={float(c.x)} +x_0=0 +y_0=0 +units=m +no_defs"

    # Project points and boundary
    points_proj = points_ll.to_crs(local_proj)
    boundary_proj = gpd.GeoSeries([boundary_ll], crs=points_ll.crs).to_crs(local_proj).iloc[0]

    # Compute distances in meters then km
    dists_m = points_proj.geometry.apply(lambda g: g.distance(boundary_proj))
    dists_km = dists_m / 1000.0
    dists_km.name = distance_col

    # idxmax returns label index aligned with points_ll
    idx_max = dists_km.idxmax()
    return dists_km, idx_max


def isoformat_time(value) -> str:
    """Convert various time representations to ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ).

    Supported inputs:
    - Unix epoch seconds or milliseconds (int/float)
    - Pandas/NumPy datetime-like
    - ISO 8601-like strings

    If parsing fails, returns str(value).
    """
    # Numeric epochs
    if isinstance(value, (int, float, np.integer, np.floating)):
        ts = float(value)
        # Heuristic: treat as ms if very large in magnitude
        if abs(ts) > 1e12:
            ts /= 1000.0
        try:
            dt = _dt.datetime.utcfromtimestamp(ts).replace(tzinfo=_dt.timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            return str(value)

    # Pandas/NumPy datetime-like
    try:
        dt = pd.to_datetime(value, utc=True, errors="raise")
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        pass

    # String fallback attempt
    try:
        dt = pd.to_datetime(str(value), utc=True, errors="coerce")
        if pd.isna(dt):
            return str(value)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return str(value)


# Example end-to-end utility (optional):

def furthest_point_within_region(points: gpd.GeoDataFrame,
                                 region_poly: shapely_base.BaseGeometry,
                                 boundary_gdf_or_geom,
                                 include_boundary_points: bool = True,
                                 distance_col: str = "distance_km") -> Tuple[pd.Series, int, str]:
    """High-level helper to:
    - Filter points to inside region
    - Dissolve boundary if GeoDataFrame given
    - Compute distances in a local AEQD CRS

    Returns: (distances Series in km for kept points, index of furthest point, proj string used)
    """
    # Ensure geographic CRS on points
    points = ensure_geographic_crs(points)

    # Filter to inside polygon
    pred = "covered_by" if include_boundary_points else "within"
    kept = filter_points_in_polygon(points, region_poly, predicate=pred)
    if kept.empty:
        raise ValueError("No points lie within the provided region polygon.")

    # Boundary geometry
    if isinstance(boundary_gdf_or_geom, gpd.GeoDataFrame):
        boundary_geom = dissolve_boundaries(boundary_gdf_or_geom)
        boundary_geom = boundary_geom  # shapely geometry
    else:
        boundary_geom = boundary_gdf_or_geom

    # Local projection centered on region
    local_proj = build_local_aeqd_crs(region_poly)

    distances, idx = max_point_to_boundary_distance(kept, boundary_geom, local_proj, distance_col)
    return distances, idx, local_proj
