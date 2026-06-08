#!/usr/bin/env python3
"""
Generic helper to extract numeric values of ioctl and flag macros from Linux headers.

This script generates a temporary C source that includes specified headers and prints
values of requested macros, compiles it, and runs it to collect results for the host
and optionally 32-bit architecture (if toolchain supports -m32).

Usage examples:
  python3 scripts/ioctl_const_extractor.py \
    --includes linux/ppdev.h linux/parport.h \
    --macros PPCLAIM PPRELEASE PPRDATA PPWDATA

  # Also attempt 32-bit extraction if toolchain has -m32 support
  python3 scripts/ioctl_const_extractor.py \
    --includes linux/ppdev.h linux/parport.h \
    --macros PPGETTIME PPSETTIME \
    --m32

Notes:
- Requires a working C compiler and access to the requested headers.
- If a macro is undefined in the included context, the output will mark it as UNDEF.
- On systems without 32-bit toolchain/libs, the -m32 build will be skipped with a notice.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from textwrap import dedent


def which(cmd):
    return shutil.which(cmd)


def build_and_run(src_path: str, out_path: str, extra_cflags=None) -> str:
    cc = which('cc') or which('gcc') or which('clang')
    if not cc:
        raise RuntimeError('No C compiler (cc/gcc/clang) found in PATH')
    cflags = ['-O2', '-Wall'] + (extra_cflags or [])
    cmd = [cc, src_path, '-o', out_path] + cflags
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Compile failed: {e.stderr.decode(errors="ignore")[:400]}')
    try:
        res = subprocess.run([out_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Execution failed: {e.stderr.decode(errors="ignore")[:400]}')
    return res.stdout.decode()


def gen_source(includes, macros):
    inc_lines = '\n'.join(f'#include <{h}>' for h in includes)
    body_lines = []
    for m in macros:
        # Generate a guarded print per macro; prints name and value or UNDEF
        body_lines.append(dedent(f'''
        #ifdef {m}
            printf("{m}=%lu\n", (unsigned long)({m}));
        #else
            printf("{m}=UNDEF\n");
        #endif
        '''))
    src = dedent(f'''
    #include <stdio.h>
    {inc_lines}
    int main(void) {{
        {''.join(body_lines)}
        return 0;
    }}
    ''')
    return src


def main():
    ap = argparse.ArgumentParser(description='Extract numeric macro values from Linux headers')
    ap.add_argument('--includes', nargs='+', required=True, help='Header include list, e.g., linux/ppdev.h linux/parport.h')
    ap.add_argument('--macros', nargs='+', required=True, help='Macro names to print')
    ap.add_argument('--m32', action='store_true', help='Also attempt 32-bit compile/run with -m32')
    args = ap.parse_args()

    # Prepare temp workspace
    with tempfile.TemporaryDirectory() as td:
        src_path = os.path.join(td, 'extract.c')
        bin_host = os.path.join(td, 'extract_host')
        bin_32 = os.path.join(td, 'extract_32')

        # Write source
        src = gen_source(args.includes, args.macros)
        with open(src_path, 'w') as f:
            f.write(src)

        # Build and run host arch
        print('# host-arch results')
        try:
            out = build_and_run(src_path, bin_host)
            sys.stdout.write(out)
        except Exception as e:
            print(f'ERROR(host): {e}', file=sys.stderr)

        # Optionally build and run 32-bit
        if args.m32:
            print('# 32-bit results')
            cc = which('cc') or which('gcc') or which('clang')
            if not cc:
                print('ERROR(m32): no compiler found', file=sys.stderr)
            else:
                # Test if -m32 is supported quickly
                probe_src = os.path.join(td, 'probe.c')
                with open(probe_src, 'w') as f:
                    f.write('int main(){return 0;}')
                probe_bin = os.path.join(td, 'probe_32')
                try:
                    subprocess.run([cc, probe_src, '-o', probe_bin, '-m32'], check=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    try:
                        out32 = build_and_run(src_path, bin_32, extra_cflags=['-m32'])
                        sys.stdout.write(out32)
                    except Exception as e:
                        print(f'ERROR(m32-run): {e}', file=sys.stderr)
                except subprocess.CalledProcessError:
                    print('SKIP(m32): toolchain/libs for -m32 not available', file=sys.stderr)


if __name__ == '__main__':
    main()
