#!/usr/bin/env python3
"""
Lightweight STA/LTA-based P and S phase picker using only NumPy.

Usage:
  python scripts/seismic_sta_lta_picker.py --data-dir /root/data --out /root/results.csv

Parameters (seconds unless noted):
  --sta-sec 0.3, --lta-sec 3.0, --hp-sec 0.5, --envelope-sec 0.2,
  --min-sep-sec 0.15, --p-thr 3.0, --s-thr 2.5, --s-after-p-sec 0.2,
  --hz-min-ratio 1.2, --hz-eval-sec 0.25, --max-picks-per-phase 1

Outputs CSV with header: file_name,phase,pick_idx
"""

import os
import glob
import csv
import sys
import argparse
import numpy as np

EPS = 1e-8


def as_float(v) -> float:
    return float(np.array(v).astype(np.float64).item())


def parse_channels(ch):
    """Return list of channel names (uppercased). Handles bytes/ndarray/str."""
    if isinstance(ch, bytes):
        s = ch.decode('utf-8', 'ignore')
        parts = [p.strip().upper() for p in s.split(',') if p.strip()]
        return parts
    if isinstance(ch, str):
        parts = [p.strip().upper() for p in ch.split(',') if p.strip()]
        return parts
    # ndarray or other
    if hasattr(ch, 'tolist'):
        lst = ch.tolist()
        if isinstance(lst, (list, tuple)):
            out = []
            for x in lst:
                if isinstance(x, (bytes, bytearray)):
                    out.append(x.decode('utf-8', 'ignore').strip().upper())
                else:
                    out.append(str(x).strip().upper())
            return out
        else:
            s = str(lst)
            return [p.strip().upper() for p in s.split(',') if p.strip()]
    s = str(ch)
    return [p.strip().upper() for p in s.split(',') if p.strip()]


def guess_component_indices(channels, ncol):
    """Guess (Z, E, N) indices from channel names; fall back deterministically."""
    ch_upper = [c.upper() for c in channels] if channels else []

    def find_any(targets):
        for t in targets:
            for i, c in enumerate(ch_upper):
                if c.endswith(t) or c == t or c[-1:] == t:
                    return i
        return None

    z = find_any(['Z'])
    e = find_any(['E', '1', 'X'])
    n = find_any(['N', '2', 'Y'])

    used = set()
    out = [None, None, None]  # Z, E, N
    if z is not None:
        out[0] = z
        used.add(z)
    if e is not None and e not in used:
        out[1] = e
        used.add(e)
    if n is not None and n not in used:
        out[2] = n
        used.add(n)

    remaining = [i for i in range(ncol) if i not in used]
    for j in range(3):
        if out[j] is None and remaining:
            out[j] = remaining.pop(0)
    return tuple(out)


def robust_scale(x):
    x = x.astype(np.float64, copy=False)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    med = np.median(x)
    mad = np.median(np.abs(x - med)) + EPS
    return (x - med) / mad


def moving_average(x, n):
    n = max(1, int(n))
    kernel = np.ones(n, dtype=np.float64) / n
    return np.convolve(x, kernel, mode='same')


def highpass_ma(x, n):
    # High-pass via moving-average subtraction (simple drift removal)
    return x - moving_average(x, n)


def energy_envelope(x, win):
    e = x * x
    return moving_average(e, win)


def sta_lta_ratio(x, sta, lta):
    sta = max(1, int(sta))
    lta = max(sta + 1, int(lta))
    e = x * x
    sta_avg = moving_average(e, sta) + EPS
    lta_avg = moving_average(e, lta) + EPS
    return sta_avg / lta_avg


def find_peak_groups(signal, thr, min_distance):
    above = signal > thr
    idxs = np.where(above)[0]
    if idxs.size == 0:
        return []
    groups = []
    start = None
    prev = None
    for i in idxs:
        if prev is None or i == prev + 1:
            if start is None:
                start = i
        else:
            groups.append((start, prev))
            start = i
        prev = i
    if start is not None:
        groups.append((start, prev))

    peaks = []
    for a, b in groups:
        seg = signal[a:b + 1]
        k = int(np.argmax(seg))
        peak = a + k
        peaks.append(peak)

    # enforce minimal separation
    peaks_sorted = sorted(peaks)
    filtered = []
    last = -10**9
    for p in peaks_sorted:
        if p - last >= min_distance:
            filtered.append(p)
            last = p
    return filtered


def pick_p_s(data, dt, channels, params):
    # data: (N, C)
    n, c = data.shape
    chs = parse_channels(channels)
    z_idx, e_idx, n_idx = guess_component_indices(chs, c)

    z = robust_scale(data[:, z_idx])
    e = robust_scale(data[:, e_idx])
    ncomp = robust_scale(data[:, n_idx])

    hp_win = max(1, int(round(params['hp_sec'] / dt)))
    if hp_win > 1:
        z = highpass_ma(z, hp_win)
        e = highpass_ma(e, hp_win)
        ncomp = highpass_ma(ncomp, hp_win)

    H = np.sqrt(e * e + ncomp * ncomp)

    env_win = max(1, int(round(params['envelope_sec'] / dt)))
    z_env = energy_envelope(z, env_win)
    h_env = energy_envelope(H, env_win)

    sta = max(1, int(round(params['sta_sec'] / dt)))
    lta = max(sta + 1, int(round(params['lta_sec'] / dt)))

    rP = sta_lta_ratio(z, sta, lta)
    rS = sta_lta_ratio(H, sta, lta)

    min_sep = int(round(params['min_sep_sec'] / dt))
    p_thr = float(params['p_thr'])
    s_thr = float(params['s_thr'])

    start_idx = int(round(params['search_start_sec'] / dt))
    p_candidates = [p for p in find_peak_groups(rP, p_thr, min_sep) if p >= start_idx]
    picksP = p_candidates[: params['max_picks_per_phase']] if p_candidates else []

    s_candidates = [s for s in find_peak_groups(rS, s_thr, min_sep) if s >= start_idx]
    if picksP:
        s_gate = picksP[0] + int(round(params['s_after_p_sec'] / dt))
        s_candidates = [s for s in s_candidates if s >= s_gate]

    hz = h_env / (z_env + EPS)
    picksS = []
    for s in s_candidates:
        w = int(round(params['hz_eval_sec'] / dt))
        a = max(0, s - w)
        b = min(n, s + w + 1)
        if np.median(hz[a:b]) >= float(params['hz_min_ratio']):
            picksS.append(s)
        if len(picksS) >= params['max_picks_per_phase']:
            break

    return picksP, picksS, {'channels_used': {'Z': z_idx, 'E': e_idx, 'N': n_idx}}


def process_dir(data_dir, out_csv, params):
    files = sorted(glob.glob(os.path.join(data_dir, '*.npz')))
    if not files:
        print(f'No .npz files in {data_dir}', file=sys.stderr)
        return 1

    rows = []
    for f in files:
        try:
            with np.load(f, allow_pickle=True) as d:
                X = d['data']
                dt = as_float(d['dt'])
                channels = d['channels']
                if not (X.ndim == 2 and X.shape[1] >= 3):
                    continue
                if not (dt > 0):
                    continue
                picksP, picksS, _ = pick_p_s(X, dt, channels, params)
                base = os.path.basename(f)
                for p in picksP:
                    if 0 <= int(p) < X.shape[0]:
                        rows.append((base, 'P', int(p)))
                for s in picksS:
                    if 0 <= int(s) < X.shape[0]:
                        rows.append((base, 'S', int(s)))
        except Exception as e:
            print(f'Error processing {f}: {e}', file=sys.stderr)

    os.makedirs(os.path.dirname(out_csv) or '.', exist_ok=True)
    with open(out_csv, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['file_name', 'phase', 'pick_idx'])
        for r in rows:
            w.writerow(r)
    print(f'Wrote {len(rows)} picks to {out_csv} from {len(files)} files.')
    return 0


def main():
    ap = argparse.ArgumentParser(description='Lightweight STA/LTA seismic phase picker (NumPy-only)')
    ap.add_argument('--data-dir', required=True, help='Directory containing .npz traces')
    ap.add_argument('--out', default='/root/results.csv', help='Output CSV path')
    ap.add_argument('--sta-sec', type=float, default=0.3)
    ap.add_argument('--lta-sec', type=float, default=3.0)
    ap.add_argument('--hp-sec', type=float, default=0.5)
    ap.add_argument('--envelope-sec', type=float, default=0.2)
    ap.add_argument('--min-sep-sec', type=float, default=0.15)
    ap.add_argument('--p-thr', type=float, default=3.0)
    ap.add_argument('--s-thr', type=float, default=2.5)
    ap.add_argument('--s-after-p-sec', type=float, default=0.2)
    ap.add_argument('--hz-min-ratio', type=float, default=1.2)
    ap.add_argument('--hz-eval-sec', type=float, default=0.25)
    ap.add_argument('--search-start-sec', type=float, default=0.1)
    ap.add_argument('--max-picks-per-phase', type=int, default=1)
    args = ap.parse_args()

    params = vars(args).copy()
    data_dir = params.pop('data_dir')
    out_csv = params.pop('out')

    code = process_dir(data_dir, out_csv, params)
    sys.exit(code)


if __name__ == '__main__':
    main()
