#!/usr/bin/env python3
"""
Compute mass of the largest connected component from a binary STL where the
2-byte Attribute Byte Count stores a Material ID.

Features:
- Binary STL parsing (little-endian floats and attribute ushort)
- Vertex deduplication with tolerance for stable connectivity
- Connected component detection by triangle adjacency (shared vertices)
- Volume computation via signed tetrahedron method
- Material ID selection by mode within largest component
- Density table parsing from Markdown (supports g/cm^3 and kg/m^3)
- Unit conversion with sensible defaults
- JSON report writing with main_part_mass (grams) and material_id

Usage:
  python3 stl_mass_calc.py \
    --stl /path/to/input.stl \
    --density-table /path/to/material_density_table.md \
    --out /path/to/mass_report.json \
    [--stl-units mm|cm|m] [--density-units g/cm3|kg/m3] [--tol 1e-5]

Defaults:
  --stl-units=mm, --density-units auto (attempt parse; fallback g/cm3), --tol=1e-5

Note: This script avoids external dependencies and targets general robustness.
"""

import argparse
import json
import math
import os
import re
import struct
import sys
from collections import Counter, defaultdict, deque
from typing import Dict, List, Tuple, Optional

# ------------------------------
# Binary STL Parsing
# ------------------------------

Triangle = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]

class STLData:
    def __init__(self):
        self.triangles: List[Triangle] = []
        self.material_ids: List[int] = []  # per-triangle material id


def read_binary_stl(path: str) -> STLData:
    data = STLData()
    with open(path, 'rb') as f:
        header = f.read(80)
        if len(header) < 80:
            raise ValueError("File too short to be a valid binary STL")
        tri_count_bytes = f.read(4)
        if len(tri_count_bytes) < 4:
            raise ValueError("Missing triangle count in STL")
        (tri_count,) = struct.unpack('<I', tri_count_bytes)
        record_fmt = '<12fH'  # normal (3f), v1 (3f), v2 (3f), v3 (3f), attr (H)
        record_size = struct.calcsize(record_fmt)
        for i in range(tri_count):
            rec = f.read(record_size)
            if len(rec) < record_size:
                raise ValueError(f"Truncated triangle record at index {i}")
            *floats, attr = struct.unpack(record_fmt, rec)
            # Unpack vertices (skip the normal for geom; normals may be unreliable)
            v1 = (floats[3], floats[4], floats[5])
            v2 = (floats[6], floats[7], floats[8])
            v3 = (floats[9], floats[10], floats[11])
            data.triangles.append((v1, v2, v3))
            data.material_ids.append(int(attr))
    return data

# ------------------------------
# Geometry Utilities
# ------------------------------

def cross(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])

def dot(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def signed_tet_volume(o: Tuple[float, float, float], a: Tuple[float, float, float], b: Tuple[float, float, float], c: Tuple[float, float, float]) -> float:
    # Volume of tetrahedron (o,a,b,c) signed; we use o=(0,0,0)
    ab = b
    ac = c
    aa = a
    return dot(aa, cross(ab, ac)) / 6.0

# ------------------------------
# Vertex Deduplication and Connectivity
# ------------------------------

def quantize(v: Tuple[float, float, float], tol: float) -> Tuple[int, int, int]:
    # Map coordinates to integer grid for stable deduplication
    return (int(round(v[0] / tol)), int(round(v[1] / tol)), int(round(v[2] / tol)))

class MeshComponents:
    def __init__(self):
        self.components: List[List[int]] = []  # list of triangle indices per component
        self.component_volumes: List[float] = []
        self.component_material_modes: List[int] = []
        self.boundary_edge_counts: List[int] = []


def build_components(triangles: List[Triangle], tri_mat_ids: List[int], tol: float) -> MeshComponents:
    n = len(triangles)
    # Assign vertex IDs via quantization
    vid_map: Dict[Tuple[int, int, int], int] = {}
    vertex_id_counter = 0
    tri_vids: List[Tuple[int, int, int]] = []
    for (a,b,c) in triangles:
        q1 = quantize(a, tol)
        q2 = quantize(b, tol)
        q3 = quantize(c, tol)
        for q in (q1, q2, q3):
            if q not in vid_map:
                vid_map[q] = vertex_id_counter
                vertex_id_counter += 1
        tri_vids.append((vid_map[q1], vid_map[q2], vid_map[q3]))
    # Build vertex->triangles adjacency
    v2tris: Dict[int, List[int]] = defaultdict(list)
    for ti, (v1,v2,v3) in enumerate(tri_vids):
        v2tris[v1].append(ti)
        v2tris[v2].append(ti)
        v2tris[v3].append(ti)
    # BFS to group triangles
    visited = [False]*n
    components: List[List[int]] = []
    for i in range(n):
        if visited[i]:
            continue
        q = deque([i])
        visited[i] = True
        comp = []
        while q:
            t = q.popleft()
            comp.append(t)
            for v in tri_vids[t]:
                for nb in v2tris[v]:
                    if not visited[nb]:
                        visited[nb] = True
                        q.append(nb)
        components.append(comp)
    # Volume by component; material mode; boundary edges count
    comp_vols: List[float] = []
    comp_modes: List[int] = []
    comp_boundary_edges: List[int] = []
    # To estimate open-ness, count boundary edges (edges seen once)
    for comp in components:
        vol = 0.0
        edge_count: Dict[Tuple[int,int], int] = defaultdict(int)
        mat_counter = Counter()
        for ti in comp:
            (a,b,c) = triangles[ti]
            vol += signed_tet_volume((0.0,0.0,0.0), a, b, c)
            mat_counter[tri_mat_ids[ti]] += 1
            v1,v2,v3 = tri_vids[ti]
            edges = [(v1,v2),(v2,v3),(v3,v1)]
            for e in edges:
                e_sorted = (e[0], e[1]) if e[0] <= e[1] else (e[1], e[0])
                edge_count[e_sorted] += 1
        boundary_edges = sum(1 for cnt in edge_count.values() if cnt == 1)
        comp_boundary_edges.append(boundary_edges)
        comp_vols.append(abs(vol))
        comp_modes.append(mat_counter.most_common(1)[0][0] if mat_counter else 0)
    mc = MeshComponents()
    mc.components = components
    mc.component_volumes = comp_vols
    mc.component_material_modes = comp_modes
    mc.boundary_edge_counts = comp_boundary_edges
    return mc

# ------------------------------
# Density Table Parsing
# ------------------------------

def parse_density_table(path: str) -> Tuple[Dict[int, float], Optional[str]]:
    """
    Parse a Markdown-like table that contains Material ID and density.
    Returns mapping {material_id: density_value} and detected unit string if any.
    Supported unit tokens: g/cm^3, g/cm3, kg/m^3, kg/m3 (case-insensitive).
    The function is tolerant to extra columns.
    """
    id_to_density: Dict[int, float] = {}
    detected_unit: Optional[str] = None
    unit_pattern = re.compile(r"(g\s*/\s*cm\^?3|kg\s*/\s*m\^?3)", re.IGNORECASE)
    # Row pattern: try to capture ID and density with optional unit
    # e.g., | 42 | PLA | 1.24 g/cm^3 |
    row_pattern = re.compile(r"\|([^|]*)\|([^|]*)\|([^|]*)\|.*$")

    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or not ('|' in line):
                continue
            m = row_pattern.match(line)
            if not m:
                continue
            cells = [c.strip() for c in m.groups()]
            # Try to detect which cell has ID and which has density
            # Strategy: First numeric integer is ID; first float in remaining is density, capture unit nearby.
            mat_id: Optional[int] = None
            dens_val: Optional[float] = None
            dens_unit: Optional[str] = None
            # Find candidate integers and floats
            for idx, cell in enumerate(cells):
                # Try integer for ID
                try:
                    iv = int(cell)
                    if mat_id is None:
                        mat_id = iv
                        continue
                except ValueError:
                    pass
                # Try density float
                # Extract first float in the cell
                fl = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", cell)
                if fl and dens_val is None:
                    try:
                        dens_val = float(fl.group(0))
                    except ValueError:
                        dens_val = None
                # Unit detection
                up = unit_pattern.search(cell)
                if up:
                    dens_unit = up.group(1)
            if mat_id is not None and dens_val is not None:
                id_to_density[mat_id] = dens_val
                if dens_unit and not detected_unit:
                    u = dens_unit.lower().replace(' ', '')
                    u = u.replace('^3', '3')  # normalize cm^3 -> cm3, m^3 -> m3
                    detected_unit = 'g/cm3' if 'g/cm' in u else 'kg/m3'
    return id_to_density, detected_unit

# ------------------------------
# Unit Conversion
# ------------------------------

def volume_convert(volume: float, stl_units: str, target: str) -> float:
    """Convert volume from STL units (mm, cm, m) to target units (cm3 or m3)."""
    stl_units = stl_units.lower()
    if target == 'cm3':
        if stl_units == 'mm':
            return volume / 1000.0  # 1 cm^3 = 1000 mm^3
        elif stl_units == 'cm':
            return volume
        elif stl_units == 'm':
            return volume * 1e6  # 1 m^3 = 1e6 cm^3
        else:
            raise ValueError(f"Unknown stl_units '{stl_units}' for cm3 target")
    elif target == 'm3':
        if stl_units == 'mm':
            return volume / 1e9  # 1 m^3 = 1e9 mm^3
        elif stl_units == 'cm':
            return volume / 1e6  # 1 m^3 = 1e6 cm^3
        elif stl_units == 'm':
            return volume
        else:
            raise ValueError(f"Unknown stl_units '{stl_units}' for m3 target")
    else:
        raise ValueError(f"Unknown target '{target}'")

# ------------------------------
# Main Calculation
# ------------------------------

def compute_mass_grams(volume: float, stl_units: str, density_val: float, density_units: str) -> float:
    density_units = density_units.lower().replace('^3', '3').replace(' ', '')
    if density_units in ('g/cm3', 'g/cm^3'):
        v_cm3 = volume_convert(volume, stl_units, 'cm3')
        return v_cm3 * density_val
    elif density_units in ('kg/m3', 'kg/m^3'):
        v_m3 = volume_convert(volume, stl_units, 'm3')
        mass_kg = v_m3 * density_val
        return mass_kg * 1000.0
    else:
        raise ValueError(f"Unsupported density unit '{density_units}'")

# ------------------------------
# CLI
# ------------------------------

def main():
    ap = argparse.ArgumentParser(description='Compute mass of largest component from binary STL with Material ID in attribute bytes')
    ap.add_argument('--stl', required=True, help='Input binary STL path')
    ap.add_argument('--density-table', required=True, help='Material density reference (Markdown)')
    ap.add_argument('--out', required=True, help='Output JSON path')
    ap.add_argument('--stl-units', default='mm', choices=['mm','cm','m'], help='STL linear units (default: mm)')
    ap.add_argument('--density-units', default=None, choices=['g/cm3','kg/m3'], help='Override density units if not detectable')
    ap.add_argument('--tol', type=float, default=1e-5, help='Vertex quantization tolerance in STL units (default: 1e-5)')
    args = ap.parse_args()

    if not os.path.exists(args.stl):
        print(f"ERROR: STL not found: {args.stl}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.density_table):
        print(f"ERROR: Density table not found: {args.density_table}", file=sys.stderr)
        sys.exit(1)

    # Parse STL
    stl = read_binary_stl(args.stl)
    if not stl.triangles:
        print("ERROR: No triangles in STL", file=sys.stderr)
        sys.exit(1)

    # Components
    comps = build_components(stl.triangles, stl.material_ids, tol=args.tol)
    if not comps.components:
        print("ERROR: No connected components found", file=sys.stderr)
        sys.exit(1)

    # Select largest by volume
    max_idx = max(range(len(comps.components)), key=lambda i: comps.component_volumes[i])
    main_vol = comps.component_volumes[max_idx]
    main_mat = comps.component_material_modes[max_idx]
    boundary_edges = comps.boundary_edge_counts[max_idx]

    # Density table
    id2dens, detected_unit = parse_density_table(args.density_table)
    dens_units = args.density_units or detected_unit or 'g/cm3'

    if main_mat not in id2dens:
        print(f"ERROR: Material ID {main_mat} not found in density table", file=sys.stderr)
        sys.exit(1)
    dens_val = id2dens[main_mat]

    # Compute mass in grams
    try:
        mass_g = compute_mass_grams(main_vol, args.stl_units, dens_val, dens_units)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Simple sanity logs
    print(f"Components: {len(comps.components)} | Largest volume (stl^3): {main_vol:.6g}")
    print(f"Main material ID: {main_mat}")
    if boundary_edges > 0:
        print(f"WARNING: Largest component has {boundary_edges} boundary edges; mesh may be open -> volume may be underestimated.")

    # Write JSON
    out = {
        'main_part_mass': float(mass_g),
        'material_id': int(main_mat),
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print(f"Wrote: {args.out}")

if __name__ == '__main__':
    main()
