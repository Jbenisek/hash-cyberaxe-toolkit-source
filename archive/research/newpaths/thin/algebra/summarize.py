#!/usr/bin/env python
"""summarize.py: aggregate algebra.py output over seeds (fixed-word draws). Usage: python -B summarize.py out_*.txt"""
import sys, re
from collections import defaultdict

deg = defaultdict(list); wal = defaultdict(list); base = {}; cube = defaultdict(list); hull = defaultdict(list); zeros = defaultdict(list)
for fn in sys.argv[1:]:
    for L in open(fn, encoding='utf-8'):
        t = L.split()
        if not t: continue
        if t[0] == 'DEG':
            W, seed, st, n = int(t[2]), int(t[4]), t[6], int(t[8])
            d = {t[i]: [int(x) for x in t[i + 1].split(',')] for i in range(9, len(t), 2)}
            deg[(W, st, n)].append(d)
        elif t[0] == 'WAL':
            W, st, n = int(t[2]), t[6], int(t[8])
            rec = {}
            i = 9
            while i < len(t):
                if t[i] in ('r1', 'r3', 'r4', 'r6'):
                    rec[t[i]] = ([float(x) for x in t[i + 2].split(',')], [float(x) for x in t[i + 4].split(',')]); i += 5
                elif t[i] == 'indgain':
                    rec['gain'] = t[i + 1]; i += 2
                else: i += 1
            wal[(W, st, n)].append(rec)
        elif t[0] == 'WALBASE':
            base[(int(t[2]), int(t[4]))] = float(t[6])
        elif t[0] == 'CUBE':
            W, st, n, k = int(t[2]), t[6], int(t[8]), int(t[10])
            rec = {}
            for i in range(13, len(t)):
                if t[i] in ('r1', 'r3', 'r4', 'r6', 'ind'):
                    rec[t[i]] = (int(t[i + 2]), float(t[i + 4]), float(t[i + 6]), float(t[i + 8]), float(t[i + 10]))
            cube[(W, st, n, k)].append(rec)
        elif t[0] == 'HULL':
            W, st, n = int(t[2]), t[6], int(t[8])
            ind, sz, cd = t[10], int(t[12]), int(t[14])
            eqs = t[16:]
            hull[(W, st, n, ind)].append((sz, cd, eqs))

print("== DEGREE per output bit position (min-max over seeds), n = number of free bits ==")
for (W, st, n), lst in sorted(deg.items()):
    s = f"W{W} {st:14s} n{n:3d} seeds {len(lst)}:"
    lo = 99
    for w in ('r1', 'r3', 'r4', 'r6'):
        mins = [min(d[w][i] for d in lst) for i in range(W)]; maxs = [max(d[w][i] for d in lst) for i in range(W)]
        lo = min(lo, min(m for m in mins if m >= 1) if any(m >= 1 for m in mins) else 99)
        s += f" {w} " + ",".join(f"{a}" if a == b else f"{a}-{b}" for a, b in zip(mins, maxs))
    ind = [min(d['ind'][i] for d in lst) for i in range(len(lst[0]['ind']))]
    s += f" | ind(min) {','.join(map(str, ind))} | lowest nonconst bit deg {lo}"
    print(s)

print("\n== LINEAR: max |corr| over nonzero masks per word (max over bits; min-max over seeds) vs random baseline; max imbalance ==")
for (W, st, n), lst in sorted(wal.items()):
    s = f"W{W} {st:14s} n{n:3d} base {base.get((W, n), float('nan')):.3f}:"
    for w in ('r1', 'r3', 'r4', 'r6'):
        mx = [max(r[w][1]) for r in lst]; im = [max(r[w][0]) for r in lst]
        best = [max(range(W), key=lambda i: r[w][1][i]) for r in lst]
        s += f" {w} lin {min(mx):.2f}-{max(mx):.2f} (bit {','.join(map(str, best))}) imb {min(im):.2f}-{max(im):.2f}"
    s += " | indgain " + " ".join(r['gain'] for r in lst)
    print(s)

print("\n== CUBE SUMS (only (cube, bit) pairs whose bit depends on every cube variable): mean fractions over seeds ==")
for (W, st, n, k), lst in sorted(cube.items()):
    s = f"W{W} {st:14s} n{n:3d} k{k}:"
    for w in ('r1', 'r3', 'r4', 'r6', 'ind'):
        P = sum(r[w][0] for r in lst)
        if P == 0: s += f" {w} -"; continue
        z = sum(r[w][0] * r[w][1] for r in lst) / P; o = sum(r[w][0] * r[w][2] for r in lst) / P
        a = sum(r[w][0] * r[w][3] for r in lst) / P
        s += f" {w} P{P} 0:{z:.3f} 1:{o:.3f} aff:{a:.3f}"
    print(s)

print("\n== AFFINE HULL of the support of each indicator: codim (support size) per seed; equations of seed 1 ==")
for (W, st, n, ind), lst in sorted(hull.items()):
    s = f"W{W} {st:14s} n{n:3d} {ind:11s}: " + " ".join(f"{cd}({sz})" for sz, cd, _ in lst)
    if lst[0][1] and lst[0][2] != ['-']: s += "  eqs " + " ".join(lst[0][2][:8])
    print(s)
