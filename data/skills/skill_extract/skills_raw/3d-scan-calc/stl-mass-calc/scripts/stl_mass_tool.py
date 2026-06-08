#!/usr/bin/env python3
"""
STL mass calculator for binary STL files where the 2-byte attribute per triangle stores a Material ID.

Features:
- Parse binary STL (little-endian) and extract triangles and per-triangle Material IDs (uint16)
- Build connected components using vertex-sharing adjacency with spatial hashing tolerance
- Compute component volumes via signed tetrahedra; choose the largest component by volume
- Determine majority Material ID for the largest component
- Parse a Markdown density table (material_id -> density)
- Compute mass = volume * density, with optional unit assumption for STL coordinates

Usage:
  python3 stl_mass_tool.py --stl model.stl --density-table materials.md --out mass_report.json [--assume-units {as-is,mm,cm,m}] [--precision 2]

Notes:
- If you computed the volume directly from STL coordinates, set --assume-units to the coordinate unit (mm, cm, m) so the script converts to cm^3 for g/cm^3 densities.
- Default behavior (as-is) assumes the computed volume is already in cm^3, suitable when you trust an external analyzer's unit.
"""

import argparse
import json
import math
import os
import re
import struct
import sys
from collections import deque, Counter, defaultdict
from typing import Dict, List, Tuple

Vec3 = Tuple[float, float, float]
Triangle = Tuple[int, int, int]


def read_binary_stl(path: str):
    """Read binary STL and return (vertices, triangles, tri_material_ids, bbox)

    vertices: list[Vec3] after spatial hashing collapse (filled later)
    triangles: list of triples of vertex indices (filled later)
    tri_material_ids: list[uint16] per triangle
    bbox: ((minx,miny,minz),(maxx,maxy,maxz)) estimated during raw read

    This function reads raw floats and material attributes; vertex merging occurs in build_indexed_mesh.
    """
    with open(path, 'rb') as f:
        header = f.read(80)
        if len(header) < 80:
            raise ValueError("Invalid STL: header too short")
        tri_count_bytes = f.read(4)
        if len(tri_count_bytes) != 4:
            raise ValueError("Invalid STL: could not read triangle count")
        (n_tris,) = struct.unpack('<I', tri_count_bytes)
        raw_tris = []  # list of (a,b,c) as Vec3
        mat_ids = []   # list of uint16
        minx = miny = minz = float('inf')
        maxx = maxy = maxz = float('-inf')
        for i in range(n_tris):
            data = f.read(50)
            if len(data) != 50:
                raise ValueError(f"Invalid STL: triangle {i} record incomplete")
            floats = struct.unpack('<12f', data[:48])
            ax, ay, az, bx, by, bz, cx, cy, cz = floats[3:12]
            a = (ax, ay, az)
            b = (bx, by, bz)
            c = (cx, cy, cz)
            raw_tris.append((a, b, c))
            (attr,) = struct.unpack('<H', data[48:50])
            mat_ids.append(int(attr))
            for v in (a, b, c):
                x, y, z = v
                if x < minx: minx = x
                if y < miny: miny = y
                if z < minz: minz = z
                if x > maxx: maxx = x
                if y > maxy: maxy = y
                if z > maxz: maxz = z
        bbox = ((minx, miny, minz), (maxx, maxy, maxz))
        return raw_tris, mat_ids, bbox


def build_indexed_mesh(raw_tris: List[Tuple[Vec3, Vec3, Vec3]], bbox) -> Tuple[List[Vec3], List[Triangle]]:
    """Collapse near-identical vertices with spatial hashing and return (vertices, triangles)."""
    (minx, miny, minz), (maxx, maxy, maxz) = bbox
    diag = math.sqrt((maxx-minx)**2 + (maxy-miny)**2 + (maxz-minz)**2)
    # Tolerance scales with model size; fallback to small absolute in degenerate case
    tol = max(diag * 1e-6, 1e-8)

    def key(v: Vec3):
        return (round(v[0] / tol), round(v[1] / tol), round(v[2] / tol))

    vert_index: Dict[Tuple[int,int,int], int] = {}
    vertices: List[Vec3] = []
    triangles: List[Triangle] = []

    for a, b, c in raw_tris:
        keys = []
        for v in (a, b, c):
            k = key(v)
            idx = vert_index.get(k)
            if idx is None:
                idx = len(vertices)
                vert_index[k] = idx
                vertices.append(v)
            keys.append(idx)
        triangles.append((keys[0], keys[1], keys[2]))

    return vertices, triangles


def components_from_triangles(triangles: List[Triangle], n_vertices: int) -> List[List[int]]:
    """Return list of components, each a list of triangle indices.

    Adjacency: triangles share at least one vertex.
    """
    tris_by_vertex: List[List[int]] = [[] for _ in range(n_vertices)]
    for ti, (a, b, c) in enumerate(triangles):
        tris_by_vertex[a].append(ti)
        tris_by_vertex[b].append(ti)
        tris_by_vertex[c].append(ti)

    visited = [False] * len(triangles)
    comps: List[List[int]] = []

    for i in range(len(triangles)):
        if visited[i]:
            continue
        comp = []
        dq = deque([i])
        visited[i] = True
        while dq:
            t = dq.popleft()
            comp.append(t)
            a, b, c = triangles[t]
            for v in (a, b, c):
                for nb in tris_by_vertex[v]:
                    if not visited[nb]:
                        visited[nb] = True
                        dq.append(nb)
        comps.append(comp)
    return comps


def tri_volume(a: Vec3, b: Vec3, c: Vec3) -> float:
    """Signed volume contribution of triangle (a,b,c) as tetrahedron with origin.
    V = dot(a, cross(b, c)) / 6
    """
    bx, by, bz = b
    cx, cy, cz = c
    cross_x = by * cz - bz * cy
    cross_y = bz * cx - bx * cz
    cross_z = bx * cy - by * cx
    return (a[0] * cross_x + a[1] * cross_y + a[2] * cross_z) / 6.0


def component_volume(vertices: List[Vec3], triangles: List[Triangle], tri_indices: List[int]) -> float:
    vol = 0.0
    for ti in tri_indices:
        a_idx, b_idx, c_idx = triangles[ti]
        a = vertices[a_idx]
        b = vertices[b_idx]
        c = vertices[c_idx]
        vol += tri_volume(a, b, c)
    return abs(vol)


def majority_material_id(tri_indices: List[int], tri_material_ids: List[int]) -> Tuple[int, Dict[int, int]]:
    """Return (majority_id, histogram) for given triangle indices."""
    hist = Counter(tri_material_ids[i] for i in tri_indices)
    majority_id, _ = hist.most_common(1)[0]
    return majority_id, dict(hist)


def parse_density_table(md_path: str) -> Dict[int, float]:
    """Parse a Markdown table mapping material_id to density.

    Looks for rows like: | id | name | density | ... |
    Extracts integer id and floating density from pipe-delimited lines.
    Ignores header and separator rows.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    density_map: Dict[int, float] = {}
    # Match table rows with at least three columns, capturing first (id) and third (density)
    # Be tolerant to extra formatting and whitespace
    row_re = re.compile(r"^\s*\|([^\n]+)\|\s*$", re.MULTILINE)
    for m in row_re.finditer(content):
        row = m.group(1)
        cols = [c.strip() for c in row.split('|')]
        if len(cols) < 3:
            continue
        # Skip separator/header rows
        if all(set(c) <= {'-', ':'} for c in cols):
            continue
        # Try to parse id (first numeric in col0) and density (first float in col2)
        id_match = re.search(r"(?<![\d])([0-9]+)(?![\d])", cols[0])
        dens_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", cols[2])
        if not id_match or not dens_match:
            continue
        try:
            mid = int(id_match.group(1))
            density = float(dens_match.group(1))
            density_map[mid] = density
        except Exception:
            continue
    if not density_map:
        raise ValueError("No densities parsed from Markdown table")
    return density_map


def convert_volume_to_cm3(volume: float, assume_units: str) -> float:
    """Convert volume to cm^3 based on assumed coordinate units.

    assume_units:
      - 'as-is': treat volume as already in cm^3 (e.g., external analyzer result)
      - 'mm': volume is in mm^3 -> divide by 1000
      - 'cm': volume in cm^3 -> unchanged
      - 'm': volume in m^3 -> multiply by 1e6
    """
    if assume_units == 'as-is':
        return volume
    if assume_units == 'mm':
        return volume / 1000.0
    if assume_units == 'cm':
        return volume
    if assume_units == 'm':
        return volume * 1_000_000.0
    raise ValueError(f"Unknown assume_units: {assume_units}")


def analyze_and_compute_mass(stl_path: str, md_path: str, assume_units: str, precision: int):
    raw_tris, tri_mat_ids, bbox = read_binary_stl(stl_path)
    vertices, triangles = build_indexed_mesh(raw_tris, bbox)
    comps = components_from_triangles(triangles, len(vertices))
    if not comps:
        raise ValueError("No components detected in STL")

    # Compute volume for each component and pick largest
    comp_vols = []
    for comp in comps:
        vol = component_volume(vertices, triangles, comp)
        comp_vols.append(vol)
    max_idx = max(range(len(comp_vols)), key=lambda i: comp_vols[i])
    main_comp = comps[max_idx]
    main_volume_raw = comp_vols[max_idx]

    # Determine material
    mat_id, hist = majority_material_id(main_comp, tri_mat_ids)

    # Convert volume if needed
    volume_cm3 = convert_volume_to_cm3(main_volume_raw, assume_units)

    # Parse density table
    densities = parse_density_table(md_path)
    if mat_id not in densities:
        # If multiple materials are present, try the most common in entire mesh as a fallback
        global_id = Counter(tri_mat_ids).most_common(1)[0][0]
        if global_id in densities:
            mat_id = global_id
        else:
            raise KeyError(f"Material ID {mat_id} not found in density table and no suitable fallback available")
    density = densities[mat_id]

    mass = volume_cm3 * density
    # Round only at the end
    mass_out = round(mass, precision)

    diagnostics = {
        "components": len(comps),
        "bbox": bbox,
        "main_component_triangles": len(main_comp),
        "main_volume_raw": main_volume_raw,
        "assume_units": assume_units,
        "volume_cm3": volume_cm3,
        "material_histogram_main": hist,
        "material_id": mat_id,
        "density": density,
        "mass_unrounded": mass,
        "mass_out": mass_out,
    }
    return {"main_part_mass": mass_out, "material_id": mat_id}, diagnostics


def main():
    ap = argparse.ArgumentParser(description="Compute mass of largest STL component using Material ID from triangle attributes and Markdown density table.")
    ap.add_argument("--stl", required=True, help="Path to binary STL file")
    ap.add_argument("--density-table", required=True, help="Path to Markdown density table")
    ap.add_argument("--out", required=True, help="Output JSON path")
    ap.add_argument("--assume-units", default="as-is", choices=["as-is", "mm", "cm", "m"],
                    help="Assumed coordinate units for converting volume to cm^3 (see help)")
    ap.add_argument("--precision", type=int, default=2, help="Decimal places for final mass")
    ap.add_argument("--print-diagnostics", action="store_true", help="Print diagnostic info to stderr")
    args = ap.parse_args()

    result, diag = analyze_and_compute_mass(args.stl, args.density_table, args.assume_units, args.precision)

    # Write JSON
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    if args.print_diagnostics:
        import pprint
        pprint.pprint(diag, stream=sys.stderr)

    # Also print a brief confirmation to stdout
    print(json.dumps(result))


if __name__ == "__main__":
    main()
