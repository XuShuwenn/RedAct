#!/usr/bin/env python3
"""
BGP Oscillation and Route Leak Analysis Helper

- Detects preference-cycle oscillations from normalized preference data
- Detects valley-free routing violations from route events/relationships
- Evaluates proposed solutions with keyword-based categorization

Usage:
  python scripts/bgp_analysis.py --input-dir /path/to/data --output-file /path/to/output/oscillation_report.json

Inputs (optional/flexible shapes):
  preferences.json        Routing preferences (varied schema supported)
  local_pref.json         Optional weights/relationship hints
  relationships.json      Pairwise relationships or mapping of AS relations
  route.json              Route advertisement info (optional)
  route_events.json       Per-event advertisement with source/destination types if available
  possible_solutions.json List of solution strings or objects with "name"
"""

import argparse
import json
import os
from typing import Any, Dict, List, Set, Tuple, Union


def _try_int(x: Any) -> Any:
    try:
        if isinstance(x, bool):
            return x
        if isinstance(x, (int,)):
            return x
        if isinstance(x, str) and x.strip() != "":
            return int(x)
    except Exception:
        pass
    return x


def normalize_asn(x: Any) -> Union[int, str]:
    v = _try_int(x)
    if isinstance(v, str):
        return v.strip()
    return v


def load_json(path: str) -> Any:
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_preferences(pref_data: Any) -> Dict[Union[int, str], Set[Union[int, str]]]:
    """Return directed graph: node -> set(preferred_neighbors). Accepts flexible shapes.
    Supported patterns:
      - {"65002": [65003, ...], ...}
      - {"65002": {"prefers": [65003]}, ...}
      - [{"from": 65002, "to": 65003, ...}, ...]
      - [[65002, 65003], ...]
    """
    graph: Dict[Union[int, str], Set[Union[int, str]]] = {}

    def add_edge(a: Any, b: Any):
        u = normalize_asn(a)
        v = normalize_asn(b)
        if u is None or v is None:
            return
        if u not in graph:
            graph[u] = set()
        graph[u].add(v)

    if pref_data is None:
        return graph

    if isinstance(pref_data, dict):
        for k, v in pref_data.items():
            src = normalize_asn(k)
            if isinstance(v, list):
                for dst in v:
                    add_edge(src, dst)
            elif isinstance(v, dict):
                # Try known keys
                if "prefers" in v and isinstance(v["prefers"], list):
                    for dst in v["prefers"]:
                        add_edge(src, dst)
                elif "to" in v:
                    add_edge(src, v["to"])
                elif "next_hops" in v and isinstance(v["next_hops"], list):
                    for dst in v["next_hops"]:
                        add_edge(src, dst)
                else:
                    # Fallback: any single key that looks like a neighbor
                    for val in v.values():
                        if isinstance(val, (int, str)):
                            add_edge(src, val)
                        elif isinstance(val, list):
                            for dst in val:
                                add_edge(src, dst)
            else:
                # Scalar treated as single neighbor
                add_edge(src, v)
    elif isinstance(pref_data, list):
        for item in pref_data:
            if isinstance(item, dict):
                if "from" in item and "to" in item:
                    add_edge(item["from"], item["to"])
                elif "src" in item and "dst" in item:
                    add_edge(item["src"], item["dst"])
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                add_edge(item[0], item[1])

    return graph


def find_cycle(graph: Dict[Union[int, str], Set[Union[int, str]]]) -> List[Union[int, str]]:
    """Detect one directed cycle using DFS. Returns cycle path (nodes in order) or []."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[Union[int, str], int] = {u: WHITE for u in graph}
    parent: Dict[Union[int, str], Union[int, str]] = {}

    def dfs(u: Union[int, str]) -> List[Union[int, str]]:
        color[u] = GRAY
        for v in graph.get(u, []):
            if v not in color:
                color[v] = WHITE
            if color[v] == WHITE:
                parent[v] = u
                cyc = dfs(v)
                if cyc:
                    return cyc
            elif color[v] == GRAY:
                # Found a back-edge u->v; reconstruct cycle from v to u
                cycle = [v]
                x = u
                while x != v and x in parent:
                    cycle.append(x)
                    x = parent[x]
                cycle.reverse()
                return cycle
        color[u] = BLACK
        return []

    for start in list(graph.keys()):
        if color[start] == WHITE:
            parent[start] = None  # type: ignore
            cyc = dfs(start)
            if cyc:
                return cyc
    return []


def normalize_rel_type(s: Any) -> str:
    if not isinstance(s, str):
        return ""
    t = s.strip().lower()
    # map synonyms
    if t in {"provider", "upstream"}:
        return "provider"
    if t in {"customer", "downstream"}:
        return "customer"
    if t in {"peer", "lateral"}:
        return "peer"
    return t


def detect_valley_free_leaks(route_events: Any, relationships: Any) -> List[Dict[str, Any]]:
    leaks: List[Dict[str, Any]] = []

    # Helper to infer relationship type between two ASNs from relationships mapping
    def rel_type(a: Any, b: Any) -> str:
        if not relationships:
            return ""
        try:
            # relationships may be a dict like {"a-b": "peer"} or nested dict
            if isinstance(relationships, dict):
                key1 = f"{a}-{b}"
                key2 = f"{b}-{a}"
                if key1 in relationships:
                    return normalize_rel_type(relationships[key1])
                if key2 in relationships:
                    return normalize_rel_type(relationships[key2])
                # nested dict: relationships[a][b] = type
                aa = str(a)
                bb = str(b)
                if aa in relationships and isinstance(relationships[aa], dict):
                    if bb in relationships[aa]:
                        return normalize_rel_type(relationships[aa][bb])
        except Exception:
            pass
        return ""

    # If route_events are present and have explicit types, use them directly
    if isinstance(route_events, list):
        for ev in route_events:
            if not isinstance(ev, dict):
                continue
            leaker = normalize_asn(ev.get("leaker_as")) if ev.get("leaker_as") is not None else normalize_asn(ev.get("advertiser_as"))
            src_as = normalize_asn(ev.get("source_as"))
            dst_as = normalize_asn(ev.get("destination_as"))
            st = normalize_rel_type(ev.get("source_type"))
            dt = normalize_rel_type(ev.get("destination_type"))
            # Infer types if missing using relationships
            if not st and src_as is not None and leaker is not None:
                st = rel_type(src_as, leaker)
            if not dt and leaker is not None and dst_as is not None:
                dt = rel_type(leaker, dst_as)
            if not (leaker is not None and src_as is not None and dst_as is not None):
                continue
            # Valley-free violations: provider->peer/provider export, peer->provider export
            is_violation = False
            if st == "provider" and dt in {"peer", "provider"}:
                is_violation = True
            elif st == "peer" and dt == "provider":
                is_violation = True
            if is_violation:
                leaks.append({
                    "leaker_as": leaker,
                    "source_as": src_as,
                    "destination_as": dst_as,
                    "source_type": st or "",
                    "destination_type": dt or "",
                })
    # If no explicit events, best-effort inference would require route paths; omit to avoid false positives
    return leaks


def load_solutions(data: Any) -> List[str]:
    sols: List[str] = []
    if data is None:
        return sols
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                sols.append(item)
            elif isinstance(item, dict):
                name = item.get("name") or item.get("title") or item.get("solution")
                if isinstance(name, str):
                    sols.append(name)
    elif isinstance(data, dict):
        for v in data.values():
            if isinstance(v, str):
                sols.append(v)
            elif isinstance(v, dict):
                name = v.get("name") or v.get("title") or v.get("solution")
                if isinstance(name, str):
                    sols.append(name)
            elif isinstance(v, list):
                for x in v:
                    if isinstance(x, str):
                        sols.append(x)
    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for s in sols:
        if s not in seen:
            uniq.append(s)
            seen.add(s)
    return uniq


def eval_solutions(solution_names: List[str], cycle_nodes: Set[Union[int, str]], leaks: List[Dict[str, Any]]) -> Dict[str, Dict[str, bool]]:
    results: Dict[str, Dict[str, bool]] = {}

    both_kw = ["routing intent", "policy intent", "udr", "user defined route", "static override"]
    leak_kw = [
        "no-export", "no export", "export policy", "block provider", "block upstream",
        "ingress filter", "as-path", "as path", "rpki", "origin validation",
        "prevent provider routes", "block re-advertisement", "block readvertisement", "filter routes"
    ]
    osc_kw = [
        "update routing preference", "route preference", "local-pref", "local pref",
        "weight", "stop preferring", "preference hierarchy"
    ]
    ineffective_kw = [
        "timer", "keepalive", "holdtime", "dampening", "max-prefix", "ecmp",
        "wait", "restart", "disable peering", "disconnect", "remove peering"
    ]

    # Check if any leak involves nodes in the cycle
    leak_in_cycle = False
    for ev in leaks:
        leaker = ev.get("leaker_as")
        dst = ev.get("destination_as")
        if leaker in cycle_nodes and dst in cycle_nodes:
            leak_in_cycle = True
            break

    for name in solution_names:
        s = name.lower()
        osc = False
        leak = False

        if any(k in s for k in both_kw):
            osc = True
            leak = True
        elif any(k in s for k in leak_kw):
            leak = True
            # If leak directly couples the cycle nodes and the solution blocks re-advertisement, it may break the cycle
            if leak_in_cycle and any(k in s for k in ["export policy", "no-export", "no export", "filter", "block re-advertisement", "block readvertisement"]):
                osc = True
        elif any(k in s for k in osc_kw):
            osc = True
        elif any(k in s for k in ineffective_kw):
            osc = False
            leak = False
        else:
            # Unknown/insufficiently specific: default to no
            osc = False
            leak = False

        results[name] = {
            "oscillation_resolved": bool(osc),
            "route_leak_resolved": bool(leak),
        }

    return results


def main():
    ap = argparse.ArgumentParser(description="BGP oscillation and route leak analyzer")
    ap.add_argument("--input-dir", required=True, help="Directory containing input JSON files")
    ap.add_argument("--output-file", required=True, help="Path to write the analysis report JSON")
    args = ap.parse_args()

    def p(name: str) -> str:
        return os.path.join(args.input_dir, name)

    preferences = load_json(p("preferences.json"))
    local_pref = load_json(p("local_pref.json"))  # optional, not strictly required
    relationships = load_json(p("relationships.json"))
    route = load_json(p("route.json"))
    route_events = load_json(p("route_events.json"))
    possible_solutions = load_json(p("possible_solutions.json"))

    graph = normalize_preferences(preferences)
    cycle = find_cycle(graph)
    affected = list(dict.fromkeys(cycle)) if cycle else []

    leaks = detect_valley_free_leaks(route_events, relationships)

    solution_names = load_solutions(possible_solutions)
    solution_results = eval_solutions(solution_names, set(affected), leaks)

    report = {
        "oscillation_detected": bool(len(cycle) > 0),
        "oscillation_cycle": cycle,
        "affected_ases": affected,
        "route_leak_detected": bool(len(leaks) > 0),
        "route_leaks": leaks,
        "solution_results": solution_results,
    }

    out_dir = os.path.dirname(os.path.abspath(args.output_file))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Wrote report: {args.output_file}")


if __name__ == "__main__":
    main()
