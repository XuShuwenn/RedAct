#!/usr/bin/env python3
"""
Compute PCAP traffic metrics and simple intrusion heuristics, output as JSON.

Requirements:
  - dpkt (preferred) or scapy; will attempt dpkt, then scapy. If neither is installed, exit.

Usage:
  python3 scripts/pcap_metrics.py --pcap packets.pcap \
      [--port-scan-port-threshold 100] [--port-scan-dst-threshold 10] \
      [--dos-multiplier 20.0] [--dos-absolute 1000] [--beacon-cv 0.2]

Outputs to stdout a JSON mapping metric_name -> value.
"""
import argparse
import json
import math
import sys
from collections import defaultdict

# Attempt to import dpkt first
HAVE_DPKT = False
HAVE_SCAPY = False
try:
    import dpkt  # type: ignore
    import socket
    HAVE_DPKT = True
except Exception:
    pass

if not HAVE_DPKT:
    try:
        from scapy.utils import RawPcapReader  # type: ignore
        from scapy.layers.l2 import Ether  # type: ignore
        from scapy.layers.inet import IP, TCP, UDP, ICMP  # type: ignore
        from scapy.layers.inet6 import IPv6, ICMPv6Unknown  # type: ignore
        HAVE_SCAPY = True
    except Exception:
        pass


def shannon_entropy_from_counts(counts: dict) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    ent = 0.0
    for c in counts.values():
        if c <= 0:
            continue
        p = c / total
        ent -= p * math.log(p, 2)
    return ent


def population_variance(values):
    n = len(values)
    if n == 0:
        return 0.0
    mean = sum(values) / n
    return sum((x - mean) ** 2 for x in values) / n


def inet_to_str(ip_bytes):
    # Convert bytes to string representation for IPv4/IPv6
    try:
        if len(ip_bytes) == 4:
            return socket.inet_ntop(socket.AF_INET, ip_bytes)
        elif len(ip_bytes) == 16:
            return socket.inet_ntop(socket.AF_INET6, ip_bytes)
    except Exception:
        pass
    return None


def parse_with_dpkt(pcap_path):
    metrics = {
        'timestamps': [],
        'lengths': [],
        'protocol_tcp': 0,
        'protocol_udp': 0,
        'protocol_icmp': 0,
        'protocol_arp': 0,
        'protocol_ip_total': 0,
    }
    # Counters and sets
    bucket_counts = defaultdict(int)
    src_ip_counts = defaultdict(int)
    dst_ip_counts = defaultdict(int)
    src_port_counts = defaultdict(int)
    dst_port_counts = defaultdict(int)
    unique_src_ports = set()
    unique_dst_ports = set()
    nodes = set()
    edges = set()  # (src, dst)
    bytes_sent = defaultdict(int)
    bytes_recv = defaultdict(int)
    # For port-scan heuristics
    per_src_dst_ports = defaultdict(lambda: defaultdict(set))  # src -> dst -> set(ports)
    per_src_ports = defaultdict(set)  # src -> set(dst_ports)
    flows = set()  # (src, dst, sport, dport, proto)
    tcp_flows = set()
    udp_flows = set()

    with open(pcap_path, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        for ts, buf in pcap:
            if not isinstance(ts, (int, float)):
                # Some readers may return non-float ts; coerce if possible
                try:
                    ts = float(ts)
                except Exception:
                    continue
            caplen = len(buf)
            metrics['timestamps'].append(ts)
            metrics['lengths'].append(caplen)
            bucket_counts[int(ts // 60)] += 1

            try:
                eth = dpkt.ethernet.Ethernet(buf)
            except Exception:
                continue

            # ARP
            if isinstance(eth.data, dpkt.arp.ARP):
                metrics['protocol_arp'] += 1
                # ARP is not IP; skip IP-level stats
                continue

            # IP/IPv6 detection
            ip = None
            src_ip = None
            dst_ip = None
            is_ipv4 = isinstance(eth.data, dpkt.ip.IP)
            is_ipv6 = isinstance(eth.data, dpkt.ip6.IP6)
            if is_ipv4 or is_ipv6:
                ip = eth.data
                metrics['protocol_ip_total'] += 1
                src_ip = inet_to_str(ip.src)
                dst_ip = inet_to_str(ip.dst)
                if src_ip:
                    nodes.add(src_ip)
                if dst_ip:
                    nodes.add(dst_ip)
                if src_ip and dst_ip:
                    edges.add((src_ip, dst_ip))
                    # bytes for PCR counts use captured length
                    bytes_sent[src_ip] += caplen
                    bytes_recv[dst_ip] += caplen
                    src_ip_counts[src_ip] += 1
                    dst_ip_counts[dst_ip] += 1

                # Transport
                sport = None
                dport = None
                proto_name = None
                try:
                    if isinstance(ip.data, dpkt.tcp.TCP):
                        metrics['protocol_tcp'] += 1
                        proto_name = 'TCP'
                        sport = int(ip.data.sport)
                        dport = int(ip.data.dport)
                    elif isinstance(ip.data, dpkt.udp.UDP):
                        metrics['protocol_udp'] += 1
                        proto_name = 'UDP'
                        sport = int(ip.data.sport)
                        dport = int(ip.data.dport)
                    elif isinstance(ip.data, dpkt.icmp.ICMP) or isinstance(ip.data, dpkt.icmp6.ICMP6):
                        metrics['protocol_icmp'] += 1
                except Exception:
                    pass

                # Ports for TCP/UDP only
                if proto_name in ('TCP', 'UDP') and src_ip and dst_ip and sport is not None and dport is not None:
                    src_port_counts[sport] += 1
                    dst_port_counts[dport] += 1
                    unique_src_ports.add(sport)
                    unique_dst_ports.add(dport)
                    per_src_ports[src_ip].add(dport)
                    per_src_dst_ports[src_ip][dst_ip].add(dport)
                    flow = (src_ip, dst_ip, sport, dport, proto_name)
                    flows.add(flow)
                    if proto_name == 'TCP':
                        tcp_flows.add(flow)
                    else:
                        udp_flows.add(flow)

    # Post processing
    timestamps = sorted(metrics['timestamps'])
    packet_count = len(timestamps)

    # Duration
    if packet_count >= 2:
        duration_seconds = float(timestamps[-1] - timestamps[0])
    else:
        duration_seconds = 0.0

    # Per-minute buckets over non-empty buckets
    bucket_values = list(bucket_counts.values())
    if bucket_values:
        ppm_avg = sum(bucket_values) / len(bucket_values)
        ppm_max = max(bucket_values)
        ppm_min = min(bucket_values)
    else:
        ppm_avg = 0.0
        ppm_max = 0
        ppm_min = 0

    # Size stats
    total_bytes = sum(metrics['lengths']) if metrics['lengths'] else 0
    if metrics['lengths']:
        avg_packet_size = total_bytes / len(metrics['lengths'])
        min_packet_size = min(metrics['lengths'])
        max_packet_size = max(metrics['lengths'])
    else:
        avg_packet_size = 0.0
        min_packet_size = 0
        max_packet_size = 0

    # Entropy
    src_ip_entropy = shannon_entropy_from_counts(src_ip_counts)
    dst_ip_entropy = shannon_entropy_from_counts(dst_ip_counts)
    src_port_entropy = shannon_entropy_from_counts(src_port_counts)
    dst_port_entropy = shannon_entropy_from_counts(dst_port_counts)

    # Graph metrics
    num_nodes = len(nodes)
    num_edges = len(edges)
    if num_nodes >= 2:
        network_density = num_edges / (num_nodes * (num_nodes - 1))
    else:
        network_density = 0.0

    # Degrees
    out_neighbors = defaultdict(set)
    in_neighbors = defaultdict(set)
    for s, d in edges:
        out_neighbors[s].add(d)
        in_neighbors[d].add(s)
    max_outdegree = max((len(v) for v in out_neighbors.values()), default=0)
    max_indegree = max((len(v) for v in in_neighbors.values()), default=0)

    # IATs
    iats = []
    for i in range(1, len(timestamps)):
        dt = timestamps[i] - timestamps[i - 1]
        if dt < 0:
            # Ignore negative deltas from out-of-order timestamps
            continue
        iats.append(dt)
    if iats:
        iat_mean = sum(iats) / len(iats)
        iat_variance = population_variance(iats)
        iat_std = math.sqrt(iat_variance)
        iat_cv = (iat_std / iat_mean) if iat_mean > 0 else 0.0
    else:
        iat_mean = 0.0
        iat_variance = 0.0
        iat_cv = 0.0

    # PCR
    pcr_values = {}
    for ip_str in set(list(bytes_sent.keys()) + list(bytes_recv.keys())):
        sent = bytes_sent.get(ip_str, 0)
        recv = bytes_recv.get(ip_str, 0)
        denom = sent + recv
        if denom > 0:
            pcr_values[ip_str] = (sent - recv) / denom
    num_producers = sum(1 for v in pcr_values.values() if v > 0.2)
    num_consumers = sum(1 for v in pcr_values.values() if v < -0.2)

    # Flows
    unique_flows = len(flows)
    tcp_flows_count = len(tcp_flows)
    udp_flows_count = len(udp_flows)
    # Directional bidirectional count: count flows that have reverse present
    bi_count = 0
    flow_set = flows  # alias
    for (s, d, sp, dp, pr) in flow_set:
        if (d, s, dp, sp, pr) in flow_set:
            bi_count += 1

    # Heuristics (parameterized later by caller)
    result = {
        'protocol_tcp': metrics['protocol_tcp'],
        'protocol_udp': metrics['protocol_udp'],
        'protocol_icmp': metrics['protocol_icmp'],
        'protocol_arp': metrics['protocol_arp'],
        'protocol_ip_total': metrics['protocol_ip_total'],
        'duration_seconds': float(duration_seconds),
        'packets_per_minute_avg': float(ppm_avg),
        'packets_per_minute_max': int(ppm_max),
        'packets_per_minute_min': int(ppm_min),
        'total_bytes': int(total_bytes),
        'avg_packet_size': float(avg_packet_size),
        'min_packet_size': int(min_packet_size),
        'max_packet_size': int(max_packet_size),
        'src_ip_entropy': float(src_ip_entropy),
        'dst_ip_entropy': float(dst_ip_entropy),
        'src_port_entropy': float(src_port_entropy),
        'dst_port_entropy': float(dst_port_entropy),
        'unique_src_ports': int(len(unique_src_ports)),
        'unique_dst_ports': int(len(unique_dst_ports)),
        'num_nodes': int(num_nodes),
        'num_edges': int(num_edges),
        'network_density': float(network_density),
        'max_outdegree': int(max_outdegree),
        'max_indegree': int(max_indegree),
        'iat_mean': float(iat_mean),
        'iat_variance': float(iat_variance),
        'iat_cv': float(iat_cv),
        'num_producers': int(num_producers),
        'num_consumers': int(num_consumers),
        'unique_flows': int(unique_flows),
        'tcp_flows': int(tcp_flows_count),
        'udp_flows': int(udp_flows_count),
        'bidirectional_flows': int(bi_count),
        # Defer flags calculation until thresholds applied
        '_aux': {
            'bucket_avg': float(ppm_avg),
            'bucket_max': int(ppm_max),
            'per_src_ports': {k: len(v) for k, v in per_src_ports.items()},
            'per_src_dst_ports': {s: {d: len(ps) for d, ps in dd.items()} for s, dd in per_src_dst_ports.items()},
        }
    }
    return result


def parse_with_scapy(pcap_path):
    # Minimal scapy fallback. Note: scapy may be slower and memory demanding for huge PCAPs.
    # This mirrors the dpkt logic where possible.
    from collections import defaultdict
    metrics = {
        'timestamps': [],
        'lengths': [],
        'protocol_tcp': 0,
        'protocol_udp': 0,
        'protocol_icmp': 0,
        'protocol_arp': 0,
        'protocol_ip_total': 0,
    }
    bucket_counts = defaultdict(int)
    src_ip_counts = defaultdict(int)
    dst_ip_counts = defaultdict(int)
    src_port_counts = defaultdict(int)
    dst_port_counts = defaultdict(int)
    unique_src_ports = set()
    unique_dst_ports = set()
    nodes = set()
    edges = set()
    bytes_sent = defaultdict(int)
    bytes_recv = defaultdict(int)
    per_src_dst_ports = defaultdict(lambda: defaultdict(set))
    per_src_ports = defaultdict(set)
    flows = set()
    tcp_flows = set()
    udp_flows = set()

    for (pkt_data, pkt_meta) in RawPcapReader(pcap_path):
        try:
            ts = float(pkt_meta.sec) + float(pkt_meta.usec) / 1_000_000.0
        except Exception:
            try:
                ts = float(pkt_meta.time)
            except Exception:
                continue
        caplen = len(pkt_data)
        metrics['timestamps'].append(ts)
        metrics['lengths'].append(caplen)
        bucket_counts[int(ts // 60)] += 1

        try:
            eth = Ether(pkt_data)
        except Exception:
            continue

        # ARP
        if eth.type == 0x0806:  # ARP
            metrics['protocol_arp'] += 1
            continue

        ip = None
        src_ip = None
        dst_ip = None
        if eth.haslayer(IP):
            ip = eth[IP]
            metrics['protocol_ip_total'] += 1
            src_ip = ip.src
            dst_ip = ip.dst
        elif eth.haslayer(IPv6):
            ip = eth[IPv6]
            metrics['protocol_ip_total'] += 1
            src_ip = ip.src
            dst_ip = ip.dst

        if ip is None:
            continue

        if src_ip:
            nodes.add(src_ip)
        if dst_ip:
            nodes.add(dst_ip)
        if src_ip and dst_ip:
            edges.add((src_ip, dst_ip))
            bytes_sent[src_ip] += caplen
            bytes_recv[dst_ip] += caplen
            src_ip_counts[src_ip] += 1
            dst_ip_counts[dst_ip] += 1

        sport = None
        dport = None
        proto_name = None
        if ip.haslayer(TCP):
            t = ip[TCP]
            proto_name = 'TCP'
            metrics['protocol_tcp'] += 1
            sport = int(t.sport)
            dport = int(t.dport)
        elif ip.haslayer(UDP):
            u = ip[UDP]
            proto_name = 'UDP'
            metrics['protocol_udp'] += 1
            sport = int(u.sport)
            dport = int(u.dport)
        elif ip.haslayer(ICMP) or ip.haslayer(ICMPv6Unknown):
            metrics['protocol_icmp'] += 1

        if proto_name in ('TCP', 'UDP') and src_ip and dst_ip and sport is not None and dport is not None:
            src_port_counts[sport] += 1
            dst_port_counts[dport] += 1
            unique_src_ports.add(sport)
            unique_dst_ports.add(dport)
            per_src_ports[src_ip].add(dport)
            per_src_dst_ports[src_ip][dst_ip].add(dport)
            flow = (src_ip, dst_ip, sport, dport, proto_name)
            flows.add(flow)
            if proto_name == 'TCP':
                tcp_flows.add(flow)
            else:
                udp_flows.add(flow)

    # Post-processing mirrors dpkt path
    timestamps = sorted(metrics['timestamps'])
    packet_count = len(timestamps)
    duration_seconds = (timestamps[-1] - timestamps[0]) if packet_count >= 2 else 0.0
    bucket_values = list(bucket_counts.values())
    ppm_avg = (sum(bucket_values) / len(bucket_values)) if bucket_values else 0.0
    ppm_max = max(bucket_values) if bucket_values else 0
    ppm_min = min(bucket_values) if bucket_values else 0

    total_bytes = sum(metrics['lengths']) if metrics['lengths'] else 0
    avg_packet_size = (total_bytes / len(metrics['lengths'])) if metrics['lengths'] else 0.0
    min_packet_size = min(metrics['lengths']) if metrics['lengths'] else 0
    max_packet_size = max(metrics['lengths']) if metrics['lengths'] else 0

    src_ip_entropy = shannon_entropy_from_counts(src_ip_counts)
    dst_ip_entropy = shannon_entropy_from_counts(dst_ip_counts)
    src_port_entropy = shannon_entropy_from_counts(src_port_counts)
    dst_port_entropy = shannon_entropy_from_counts(dst_port_counts)

    num_nodes = len(nodes)
    num_edges = len(edges)
    network_density = (num_edges / (num_nodes * (num_nodes - 1))) if num_nodes >= 2 else 0.0

    out_neighbors = defaultdict(set)
    in_neighbors = defaultdict(set)
    for s, d in edges:
        out_neighbors[s].add(d)
        in_neighbors[d].add(s)
    max_outdegree = max((len(v) for v in out_neighbors.values()), default=0)
    max_indegree = max((len(v) for v in in_neighbors.values()), default=0)

    iats = []
    for i in range(1, len(timestamps)):
        dt = timestamps[i] - timestamps[i - 1]
        if dt >= 0:
            iats.append(dt)
    if iats:
        iat_mean = sum(iats) / len(iats)
        iat_variance = population_variance(iats)
        iat_std = math.sqrt(iat_variance)
        iat_cv = (iat_std / iat_mean) if iat_mean > 0 else 0.0
    else:
        iat_mean = 0.0
        iat_variance = 0.0
        iat_cv = 0.0

    pcr_values = {}
    for ip_str in set(list(bytes_sent.keys()) + list(bytes_recv.keys())):
        sent = bytes_sent.get(ip_str, 0)
        recv = bytes_recv.get(ip_str, 0)
        denom = sent + recv
        if denom > 0:
            pcr_values[ip_str] = (sent - recv) / denom
    num_producers = sum(1 for v in pcr_values.values() if v > 0.2)
    num_consumers = sum(1 for v in pcr_values.values() if v < -0.2)

    unique_flows = len(flows)
    tcp_flows_count = len(tcp_flows)
    udp_flows_count = len(udp_flows)

    bi_count = 0
    for (s, d, sp, dp, pr) in flows:
        if (d, s, dp, sp, pr) in flows:
            bi_count += 1

    result = {
        'protocol_tcp': metrics['protocol_tcp'],
        'protocol_udp': metrics['protocol_udp'],
        'protocol_icmp': metrics['protocol_icmp'],
        'protocol_arp': metrics['protocol_arp'],
        'protocol_ip_total': metrics['protocol_ip_total'],
        'duration_seconds': float(duration_seconds),
        'packets_per_minute_avg': float(ppm_avg),
        'packets_per_minute_max': int(ppm_max),
        'packets_per_minute_min': int(ppm_min),
        'total_bytes': int(total_bytes),
        'avg_packet_size': float(avg_packet_size),
        'min_packet_size': int(min_packet_size),
        'max_packet_size': int(max_packet_size),
        'src_ip_entropy': float(src_ip_entropy),
        'dst_ip_entropy': float(dst_ip_entropy),
        'src_port_entropy': float(src_port_entropy),
        'dst_port_entropy': float(dst_port_entropy),
        'unique_src_ports': int(len(unique_src_ports)),
        'unique_dst_ports': int(len(unique_dst_ports)),
        'num_nodes': int(num_nodes),
        'num_edges': int(num_edges),
        'network_density': float(network_density),
        'max_outdegree': int(max_outdegree),
        'max_indegree': int(max_indegree),
        'iat_mean': float(iat_mean),
        'iat_variance': float(iat_variance),
        'iat_cv': float(iat_cv),
        'num_producers': int(num_producers),
        'num_consumers': int(num_consumers),
        'unique_flows': int(unique_flows),
        'tcp_flows': int(tcp_flows_count),
        'udp_flows': int(udp_flows_count),
        'bidirectional_flows': int(bi_count),
        '_aux': {
            'bucket_avg': float(ppm_avg),
            'bucket_max': int(ppm_max),
            'per_src_ports': {k: len(v) for k, v in per_src_ports.items()},
            'per_src_dst_ports': {s: {d: len(ps) for d, ps in dd.items()} for s, dd in per_src_dst_ports.items()},
        }
    }
    return result


def apply_heuristics(result, port_scan_port_threshold, port_scan_dst_threshold, dos_multiplier, dos_absolute, beacon_cv):
    aux = result.get('_aux', {})
    bucket_avg = float(aux.get('bucket_avg', 0.0))
    bucket_max = int(aux.get('bucket_max', 0))

    # Port scan heuristic
    has_port_scan = False
    per_src_ports = aux.get('per_src_ports', {})  # src -> count of unique dst ports
    per_src_dst_ports = aux.get('per_src_dst_ports', {})  # src -> dst -> count unique ports

    # Condition A: any src with very high unique destination ports overall
    for src, n_ports in per_src_ports.items():
        if n_ports >= port_scan_port_threshold:
            has_port_scan = True
            break
    # Condition B: any src contacting any single dst on many distinct ports
    if not has_port_scan:
        for src, dmap in per_src_dst_ports.items():
            for dst, n_ports in dmap.items():
                if n_ports >= port_scan_port_threshold:
                    has_port_scan = True
                    break
            if has_port_scan:
                break

    # DoS heuristic: extreme spikes
    has_dos_pattern = False
    if bucket_avg > 0 and bucket_max >= max(dos_absolute, dos_multiplier * bucket_avg):
        has_dos_pattern = True

    # Beaconing heuristic: highly regular timings (low CV)
    has_beaconing = False
    if result.get('iat_cv', 0.0) <= beacon_cv and result.get('iat_mean', 0.0) > 0:
        has_beaconing = True

    is_traffic_benign = (not has_port_scan) and (not has_dos_pattern) and (not has_beaconing)

    result['has_port_scan'] = bool(has_port_scan)
    result['has_dos_pattern'] = bool(has_dos_pattern)
    result['has_beaconing'] = bool(has_beaconing)
    result['is_traffic_benign'] = bool(is_traffic_benign)
    # Drop aux before output
    result.pop('_aux', None)
    return result


def main():
    parser = argparse.ArgumentParser(description='Compute PCAP traffic metrics and intrusion heuristics')
    parser.add_argument('--pcap', required=True, help='Path to PCAP file')
    parser.add_argument('--port-scan-port-threshold', type=int, default=100,
                        help='Unique destination port threshold to flag scanning (overall or per-destination)')
    parser.add_argument('--port-scan-dst-threshold', type=int, default=10,
                        help='Reserved for future use (e.g., require multiple destinations)')
    parser.add_argument('--dos-multiplier', type=float, default=20.0,
                        help='Max per-minute must exceed avg by at least this factor to flag DoS')
    parser.add_argument('--dos-absolute', type=int, default=1000,
                        help='Absolute packets-per-minute threshold to consider for DoS')
    parser.add_argument('--beacon-cv', type=float, default=0.2,
                        help='IAT coefficient of variation threshold for beaconing')
    args = parser.parse_args()

    if HAVE_DPKT:
        result = parse_with_dpkt(args.pcap)
    elif HAVE_SCAPY:
        result = parse_with_scapy(args.pcap)
    else:
        print('ERROR: Neither dpkt nor scapy is available. Please install one of them.', file=sys.stderr)
        sys.exit(1)

    result = apply_heuristics(
        result,
        port_scan_port_threshold=args.port_scan_port_threshold,
        port_scan_dst_threshold=args.port_scan_dst_threshold,
        dos_multiplier=args.dos_multiplier,
        dos_absolute=args.dos_absolute,
        beacon_cv=args.beacon_cv,
    )

    # Output only the required fields, coercing to JSON-serializable primitives
    print(json.dumps(result, separators=(',', ':'), sort_keys=False))


if __name__ == '__main__':
    main()
