#!/usr/bin/env python3
"""rates.py  (untried/b3-heur; research only)

Parse one pair_calc_sub output (beta* = 18b0e098 alone, pin H8, eta 830303cf) into exact per-row masses
    m_j = L_j * N_j / 2^(64 + free bits of the e1 cube)            (normalisation of counter_next/stack/scan_y4.py)
and three rates of the cube (each the AVERAGE over the cube's members of the member rate):
    S      the six front-line outcomes (tau 285020a0 685020a0 185020a0 385020a0 275020a0 175020a0)
           -- identified by sum match: on the whole class they total 67,633,152 = the map's Section 2.6 figure
    r7     all seven tau x5020a0 rows (S plus 675020a0): 67,698,688 on the class = the stack's "sub-class" rate
    total  every row with L and N > 0 (the objective the stack's greedy scan used)
Run as a script: summarise the existing stack cube outputs (read-only) -> prior_cubes.tsv in this folder.
"""
import os, sys, glob
from fractions import Fraction

S_TAUS = {0x285020a0, 0x685020a0, 0x185020a0, 0x385020a0, 0x275020a0, 0x175020a0}
R7_TAUS = S_TAUS | {0x675020a0}


def parse(text, mask):
    free = 32 - bin(mask).count('1')
    rows = {}
    for line in text.splitlines():
        f = line.split()
        if not f or f[0] != 'OUTR':
            continue
        tau = int(f[3], 16)
        L = int(f[f.index('E1') + 1]); N = int(f[f.index('N3') + 1])
        rows[tau] = Fraction(L * N, 2 ** (64 + free))
    S = sum((v for t, v in rows.items() if t in S_TAUS), Fraction(0))
    r7 = sum((v for t, v in rows.items() if t in R7_TAUS), Fraction(0))
    tot = sum(rows.values(), Fraction(0))
    nrows = sum(1 for v in rows.values() if v)
    return S, r7, tot, nrows, rows


def main():
    stack = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'counter_next', 'stack')
    here = os.path.dirname(os.path.abspath(__file__))
    res = []
    for fn in sorted(glob.glob(os.path.join(stack, 'cube_*.out'))):
        base = os.path.basename(fn)[5:-4]
        parts = base.split('_')
        if len(parts) != 2:
            continue
        try:
            mask, val = int(parts[0], 16), int(parts[1], 16)
        except ValueError:
            continue
        txt = open(fn).read()
        if 'OUTR' not in txt:
            continue
        S, r7, tot, n, _ = parse(txt, mask)
        res.append((mask, val, S, r7, tot, n))
    with open(os.path.join(here, 'prior_cubes.tsv'), 'w') as fo:
        fo.write('mask\tvalue\tfree\tS_rate\tr7_rate\ttotal_rate\trows\n')
        for mask, val, S, r7, tot, n in res:
            fo.write(f'{mask:08x}\t{val:08x}\t{32-bin(mask).count("1")}\t{float(S):.0f}\t{float(r7):.0f}\t{float(tot):.0f}\t{n}\n')
    print(f'existing stack cubes parsed: {len(res)}')
    for key, name in ((2, 'S'), (3, 'r7'), (4, 'total')):
        vals = sorted({r[key] for r in res})
        best = max(res, key=lambda r: r[key])
        print(f'  {name:5s}: {len(vals)} distinct values, min {float(vals[0]):,.0f}, max {float(vals[-1]):,.0f} '
              f'(first at {best[0]:08x}/{best[1]:08x}, free {32-bin(best[0]).count("1")})')
    hist = {}
    for r in res:
        hist[float(r[2])] = hist.get(float(r[2]), 0) + 1
    print('  S-rate histogram:', ', '.join(f'{k:,.0f} x{v}' for k, v in sorted(hist.items())))


if __name__ == '__main__':
    main()
