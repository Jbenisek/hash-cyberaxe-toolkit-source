#!/usr/bin/env python3
"""scan_y4.py [LEVELS]   (counter_next/stack; research only)

Y4 subset chosen for beta*: in the counter arrangement Y4 is an outer word, fixed per outer step, so the run may use
any part of the eta class, down to ONE member (2^224 outer steps remain).  The beta* rate of a cube of e1 = Y3 + Y4
is  r = sum_j L_j N_j / 2^(64 + free bits)  (Sol answer Y section 2; normalisation as a15).  Exact N_j per cube come
from the team's binary pair_calc_sub (run_cube.sh, beta* alone, rule S8 = filed rule A printed beside).
Greedy: start from the class (mask 03cf8303, value 030c0303); at each level try every remaining free bit at 0 and at
1, keep the best (by the all-solutions rate), until LEVELS bits are fixed.  Every cube is printed.
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import subprocess, sys, os
from math import log2
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
SH = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/counter_next/stack/run_cube.sh')
CLASS_M, CLASS_V = 0x03CF8303, 0x030C0303
SUB_RATE = 67698688


def run(mask, val):
    name = f'{mask:08x}_{val:08x}'
    out = os.path.join(HERE, f'cube_{name}.out')
    if not os.path.exists(out) or os.path.getsize(out) == 0:
        subprocess.run(['wsl', '-d', 'Ubuntu', '--', 'bash', SH, name, f'{mask:08x}', f'{val:08x}'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    free = 32 - bin(mask).count('1')
    tot = keep = Fraction(0)
    rows = 0
    for line in open(out):
        f = line.split()
        if not f or f[0] != 'OUTR':
            continue
        L = int(f[f.index('E1') + 1]); N = int(f[f.index('N3') + 1]); P = int(f[f.index('P') + 1])
        if L and N:
            rows += 1
        tot += Fraction(L * N, 2 ** (64 + free)); keep += Fraction(L * P, 2 ** (64 + free))
    os.remove(out) if False else None
    return tot, keep, rows


def main():
    levels = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    mask, val = CLASS_M, CLASS_V
    if len(sys.argv) > 3:                       # optional start cube (hex mask, hex value)
        mask, val = int(sys.argv[2], 16), int(sys.argv[3], 16)
    t, k, n = run(mask, val)
    print(f'class {mask:08x}/{val:08x}: beta* rate {float(t):,.0f} (x{float(t)/SUB_RATE:.4f} of sub-class, 2^{log2(t/SUB_RATE):+.3f}); '
          f'rule-A pass {float(k):,.0f}; rows {n}', flush=True)
    for lev in range(levels):
        best = None
        for b in range(32):
            if mask >> b & 1:
                continue
            for v in (0, 1):
                m2, v2 = mask | 1 << b, val | v << b
                t, k, n = run(m2, v2)
                print(f'  L{lev+1} bit {b:2d}={v}: rate {float(t):14,.0f}  2^{log2(t/SUB_RATE) if t else -99:+.3f}  '
                      f'ruleA {float(k):14,.0f}  rows {n}', flush=True)
                if best is None or t > best[0]:
                    best = (t, k, m2, v2, b, v)
        t, k, mask, val, b, v = best
        print(f'L{lev+1}: fix bit {b}={v} -> cube {mask:08x}/{val:08x} ({32-bin(mask).count("1")} free bits): '
              f'rate {float(t):,.0f} = 2^{log2(t/SUB_RATE):+.3f} x sub-class; rule-A pass 2^{log2(k/SUB_RATE) if k else -99:+.3f}', flush=True)


if __name__ == '__main__':
    main()
