#!/usr/bin/env python3
"""GeoPandas helper utilities for boundary-distance analysis.

Functions:
- union_geoms_safe(gdf): robustly union GeoDataFrame geometries across GeoPandas/Shapely versions
- to_metric(gdf, metric_crs): project a GeoDataFrame to a metric CRS (returns a copy)
- ms_to_iso8601(ts): convert epoch milliseconds (or seconds) to ISO 8601 UTC; pass through strings

These helpers are generic and reusable for workflows that need to compute
point-to-boundary distances in a projected CRS.
"""

from __future__ import annotations
import math
from datetime import datetime, timezone
from typing import Any

import geopandas as gpd
from shapely.ops import unary_union as ops_unary_union


def union_geoms_safe(gdf: gpd.GeoDataFrame):
    """Return a single union geometry from a GeoDataFrame's geometry column.

    Tries GeoSeries.union_all (newer), then GeoSeries.unary_union, then shapely.ops.unary_union.
    """
    gs = gdf.geometry
    # Newer GeoPandas/Shapely
    if hasattr(gs, "union_all"):
        try:
            return gs.union_all()
        except Exception:
            pass
    # Common fallback
    if hasattr(gs, "unary_union"):
        try:
            return gs.unary_union
        except Exception:
            pass
    # Last resort
    return ops_unary_union(gs)


def to_metric(gdf: gpd.GeoDataFrame, metric_crs: str = "EPSG:4087") -> gpd.GeoDataFrame:
    """Project GeoDataFrame to a metric CRS (returns a new GeoDataFrame).

    Ensures input has CRS. If missing, assumes WGS84 (EPSG:4326).
    """
    out = gdf.copy()
    if out.crs is None:
        out.set_crs("EPSG:4326", inplace=True, allow_override=True)
    return out.to_crs(metric_crs)


def ms_to_iso8601(ts: Any) -> str:
    """Convert a timestamp (ms or s since epoch) to ISO 8601 UTC. Strings are returned as-is.

    - If ts is a large integer/float (e.g., > 10^11), assume milliseconds.
    - If numeric but smaller, assume seconds.
    - If ts is falsy or cannot be parsed, return an empty string.
    """
    if ts is None:
        return ""
    if isinstance(ts, str):
        # Assume already normalized; caller may validate separately
        return ts
    try:
        t = float(ts)
    except Exception:
        return ""
    # Heuristic: distinguish ms vs s by magnitude
    # ~10^9 is seconds range for modern timestamps; ~10^12 for ms.
    if t > 1e11:
        t = t / 1000.0
    dt = datetime.fromtimestamp(t, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
