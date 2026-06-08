#!/usr/bin/env python3
"""
BGP analysis utilities: detect preference-cycle oscillations and valley-free route leaks.

This script is generic and does not assume a specific schema beyond common patterns.
It accepts:
  --preferences PATH         Preferences graph in JSON
  --route-events PATH        Route advertisement events in JSON
  --relationships PATH       (Optional) AS relationship map in JSON
  --out PATH                 (Optional) Write JSON report to file; otherwise print to stdout

Preferences input (flexible):
- Accepts one of the following common shapes:
  1) { "65002": ["65003", ...], ... }
  2) [ {"asn": 65002, "prefers": [65003, ...]}, ... ]
  3) [ {"from": 65002, "to": 65003}, ... ]
  4) [ [65002, 65003], ... ] (list of edges)

Route events (flexible):
- List of events; each event may contain:
  - leaker_as (int)
  - destination_as (int)
  - source_as (int) or learned_from_as (int)
  - source_type ("customer"|"peer"|"provider") [optional]
  - destination_type ("customer"|"peer"|"provider") [optional]

Relationships (optional but helps):
- A mapping per ASN indicating neighbors by type. Common shape:
  {
    "65002": {
      "customers": [65004, ...],
      "providers": [65001, ...],
      "peers": [65003, ...]
    },
    ...
  }

Output (analysis summary):
{
  "oscillation_detected": bool,
  "oscillation_cycles": [[asn,...], ...],
  "affected_ases": [asn,...],
  "route_leak_detected": bool,
  "route_leaks": [
    {"leaker_as": int, "source_as": int|None, "destination_as": int,
     "source_type": str, "destination_type": str}
  ]
}

Note: This script intentionally does not attempt to classify free-text solutions.
Use the SKILL.md evaluation rules to assess candidate fixes.
"""

import argparse
import json
import os
from collections import defaultdict, deque
from typing import Any, Dict, List, Set, Tuple, Optional

RelType = str  # "customer"|"peer"|"provider"


def load_json(path: str) -> Any:
    with open(path, 'r') as f:
        return json.load(f)


def parse_preferences(data: Any) -> Dict[int, Set[int]]:
    """Parse preferences into adjacency list: graph[u] = set(v) meaning u prefers v."""
    graph: Dict[int, Set[int]] = defaultdict(set)

    if isinstance(data, dict):
        # { "65002": ["65003", ...], ... } or nested dict with key 'prefers'
        for k, v in data.items():
            try:
                u = int(k)
            except Exception:
                continue
            if isinstance(v, dict) and 'prefers' in v:
                pref_list = v.get('prefers', [])
            else:
                pref_list = v
            if isinstance(pref_list, list):
                for n in pref_list:
                    try:
                        graph[u].add(int(n))
                    except Exception:
                        pass
            elif isinstance(pref_list, (str, int)):
                try:
                    graph[u].add(int(pref_list))
                except Exception:
                    pass
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, list) and len(item) >= 2:
                try:
                    u, v = int(item[0]), int(item[1])
                    graph[u].add(v)
                except Exception:
                    pass
            elif isinstance(item, dict):
                if 'asn' in item and 'prefers' in item:
                    try:
                        u = int(item['asn'])
                        for n in item.get('prefers', []) or []:
                            graph[u].add(int(n))
                    except Exception:
                        pass
                elif 'from' in item and 'to' in item:
                    try:
                        u, v = int(item['from']), int(item['to'])
                        graph[u].add(v)
                    except Exception:
                        pass
    return graph


def find_cycles(graph: Dict[int, Set[int]], limit: int = 50) -> List[List[int]]:
    """Find up to `limit` simple cycles using DFS with stack tracking.
    Returns list of cycles (each a list of ASNs in order). De-duplicates via canonical rotation.
    """
    cycles: List[List[int]] = []
    seen_canon: Set[Tuple[int, ...]] = set()

    color: Dict[int, int] = {u: 0 for u in graph}  # 0=unvisited,1=visiting,2=done

    stack: List[int] = []
    onstack: Set[int] = set()

    def canonicalize(cyc: List[int]) -> Tuple[int, ...]:
        # rotate so smallest ASN first; also ensure direction consistent
        if not cyc:
            return tuple()
        # remove possible duplicate last==first
        if len(cyc) > 1 and cyc[0] == cyc[-1]:
            cyc = cyc[:-1]
        m = min(cyc)
        idxs = [i for i, x in enumerate(cyc) if x == m]
        best = None
        for i in idxs:
            rotated = cyc[i:] + cyc[:i]
            t = tuple(rotated)
            if best is None or t < best:
                best = t
        # also compare reversed direction
        rcyc = list(reversed(cyc))
        idxs2 = [i for i, x in enumerate(rcyc) if x == m]
        for i in idxs2:
            rotated = rcyc[i:] + rcyc[:i]
            t = tuple(rotated)
            if best is None or t < best:
                best = t
        return best or tuple(cyc)

    def dfs(u: int):
        nonlocal cycles
        color[u] = 1
        stack.append(u)
        onstack.add(u)
        for v in graph.get(u, ()):  # neighbors
            if color.get(v, 0) == 0:
                dfs(v)
                if len(cycles) >= limit:
                    break
            elif v in onstack:
                # found a back-edge; reconstruct cycle
                try:
                    i = stack.index(v)
                except ValueError:
                    i = -1
                if i != -1:
                    cyc = stack[i:] + [v]
                    can = canonicalize(cyc)
                    if can not in seen_canon:
                        seen_canon.add(can)
                        cycles.append(list(can))
                        if len(cycles) >= limit:
                            break
        onstack.discard(u)
        stack.pop()
        color[u] = 2

    # ensure isolated nodes are also in graph keys
    nodes = set(graph.keys()) | {v for vs in graph.values() for v in vs}
    for n in nodes:
        if n not in graph:
            graph[n] = set()

    for u in list(graph.keys()):
        if color.get(u, 0) == 0:
            dfs(u)
        if len(cycles) >= limit:
            break
    return cycles


def parse_relationships(rel: Any) -> Dict[int, Dict[RelType, Set[int]]]:
    out: Dict[int, Dict[RelType, Set[int]]] = {}
    if not isinstance(rel, dict):
        return out
    for k, v in rel.items():
        try:
            asn = int(k)
        except Exception:
            continue
        out[asn] = {
            'customers': set(v.get('customers', []) or []),
            'providers': set(v.get('providers', []) or []),
            'peers': set(v.get('peers', []) or []),
        }
        # normalize to int
        for typ in ('customers', 'providers', 'peers'):
            out[asn][typ] = {int(x) for x in out[asn][typ]}
    return out


def get_rel_type(relmap: Dict[int, Dict[RelType, Set[int]]], leaker: int, neighbor: int) -> Optional[RelType]:
    m = relmap.get(leaker)
    if not m:
        return None
    for typ in ('customers', 'providers', 'peers'):
        if neighbor in m.get(typ, set()):
            return typ[:-1] if typ.endswith('s') else typ
    return None


def normalize_event(e: Dict[str, Any]) -> Dict[str, Any]:
    # Attempt to coerce fields to consistent names/types
    leaker = e.get('leaker_as')
    dest = e.get('destination_as') or e.get('neighbor_as')
    src = e.get('source_as') or e.get('learned_from_as')
    try:
        leaker = int(leaker) if leaker is not None else None
    except Exception:
        leaker = None
    try:
        dest = int(dest) if dest is not None else None
    except Exception:
        dest = None
    try:
        src = int(src) if src is not None else None
    except Exception:
        src = None

    return {
        'leaker_as': leaker,
        'destination_as': dest,
        'source_as': src,
        'source_type': e.get('source_type'),
        'destination_type': e.get('destination_type'),
    }


def is_valley_free_export(learned_from: RelType, to_neighbor: RelType) -> bool:
    # Valley-free rule: to non-customers (peer/provider), export only customer/self-origin.
    if to_neighbor in ('peer', 'provider') and learned_from in ('peer', 'provider'):
        return False
    return True


def detect_leaks(route_events: List[Dict[str, Any]], relmap: Dict[int, Dict[RelType, Set[int]]]) -> List[Dict[str, Any]]:
    leaks: List[Dict[str, Any]] = []
    for raw in route_events:
        e = normalize_event(raw)
        leaker = e['leaker_as']
        dest = e['destination_as']
        if leaker is None or dest is None:
            continue
        src_type = e.get('source_type')
        dst_type = e.get('destination_type')
        # derive types if missing
        if not src_type and e.get('source_as') is not None:
            src_type = get_rel_type(relmap, leaker, int(e['source_as']))
        if not dst_type:
            dst_type = get_rel_type(relmap, leaker, dest)
        # cannot evaluate without both types
        if not src_type or not dst_type:
            continue
        if not is_valley_free_export(src_type, dst_type):
            leaks.append({
                'leaker_as': leaker,
                'source_as': e.get('source_as'),
                'destination_as': dest,
                'source_type': src_type,
                'destination_type': dst_type,
            })
    return leaks


def main():
    ap = argparse.ArgumentParser(description='Detect BGP preference cycles and valley-free route leaks.')
    ap.add_argument('--preferences', required=True, help='Path to preferences.json')
    ap.add_argument('--route-events', required=True, help='Path to route_events.json')
    ap.add_argument('--relationships', help='Path to relationships.json (optional)')
    ap.add_argument('--out', help='Write report JSON to this path (optional)')
    args = ap.parse_args()

    pref_data = load_json(args.preferences)
    graph = parse_preferences(pref_data)

    relmap: Dict[int, Dict[RelType, Set[int]]] = {}
    if args.relationships and os.path.exists(args.relationships):
        rel_data = load_json(args.relationships)
        relmap = parse_relationships(rel_data)

    events = load_json(args.route_events)
    if not isinstance(events, list):
        raise SystemExit('route-events must be a list of events')

    cycles = find_cycles(graph)
    affected: Set[int] = set(x for cyc in cycles for x in cyc)

    leaks = detect_leaks(events, relmap)

    report = {
        'oscillation_detected': bool(cycles),
        'oscillation_cycles': cycles,
        'affected_ases': sorted(affected),
        'route_leak_detected': bool(leaks),
        'route_leaks': leaks,
    }

    if args.out:
        os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
        with open(args.out, 'w') as f:
            json.dump(report, f, indent=2)
    else:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
