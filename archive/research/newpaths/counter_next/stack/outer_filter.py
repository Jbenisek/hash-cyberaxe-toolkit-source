#!/usr/bin/env python3
"""outer_filter.py [OUTCOMES]   (counter_next/stack; research only)

EXACT share of outer steps that can contain a collision, for the counter arrangement (pin H8, 55/63, sub-class).
Per outer step the E3 inputs y = Y4, Q = Y9, W = w8 are fixed (only h1 moves); E = Y3 + y + w8, E' = E + DY3.
For an E1 outcome (beta, tau, eps) with n = 0, an E3 match needs (e3cond.py, checked on 200,000 real pairs):
  (1) exists h1:  (Q + h1) ^ (Q + (h1 ^ eta)) = G(tau),  G = ROL(tau ^ ROR(tau,1), 12)
  (2) exists f1:  (E + f1) ^ (E' + (f1 ^ ROR(G,12))) = eps
Both are properties of outer words only.  An outer step where, for every listed outcome, (1) or (2) has no solution
holds no trial with R = 0 of a listed outcome: skipping it loses no collision (exact, no model).
Counted exactly over all 2^32 Q and all 2^32 E by subset-construction DPs (state: the reachable carry pairs of the
existential word, per outcome).  Q and E are independent uniform words under M_outer (Sol answer Y section 7: Q = Y9 and
W = w8 are two of the seven independent outer words; E = Y3 + y + W), so
  P(pass) = sum over (solvable pattern a of Q, solvable pattern b of E) P(a) P(b) [a and b share an outcome].
OUTCOMES: 'bstar' (the 7 rows of beta*, default) or 'all' (every row of a15_outcomes.tsv with a nonzero product).
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

import sys
from fractions import Fraction
from math import log2
M = 0xFFFFFFFF
def ror(x, r): return ((x >> r) | (x << (32 - r))) & M
def rol(x, r): return ror(x, (32 - r) % 32)
Y3, Y3B, ETA = 0x8127C181, 0x7EDF3E7E, 0x830303CF
DY3 = (Y3B - Y3) & M
TAB = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/pkg/count/a15_outcomes.tsv')
# betas by unconditional sub-class mass (Sol answer Y section 4: C / 2^k): 67.7M, 51.4M, 50.8M, 13.2M, 1.47M, ...
TOP = [0x18B0E098, 0x18B1A098, 0x18D0E098, 0x18D1A098, 0x18B3E098, 0x18D3E098]


def outcomes(which):
    rows = []
    if which.endswith('.out'):                  # a cube_*.out of run_cube.sh: rows with L and N nonzero
        for line in open(which):
            f = line.split()
            if not f or f[0] != 'OUTR':
                continue
            L = int(f[f.index('E1') + 1]); N = int(f[f.index('N3') + 1])
            if L and N:
                rows.append((int(f[2], 16), int(f[3], 16), int(f[4], 16), Fraction(L * N)))
        return rows
    for line in open(TAB):
        f = line.split('\t')
        if f[0] == 'beta':
            continue
        beta, tau, eps, R = int(f[0], 16), int(f[1], 16), int(f[2], 16), Fraction(f[13])
        if R == 0:
            continue
        if which == 'bstar' and beta != 0x18B0E098:
            continue
        if which.startswith('top') and beta not in TOP[:int(which[3:])]:
            continue
        rows.append((beta, tau, eps, R))
    return rows


def G(tau): return rol(tau ^ ror(tau, 1), 12)


def step_pairs(states, a, b, d, o):
    """one bit of: exists v with (x0 + v) ^ (x1 + (v ^ dz)) = out; a, b = bits of x0, x1; d = bit of dz; o = out bit."""
    nxt = set()
    for (c, cb) in states:
        for v in (0, 1):
            vb = v ^ d
            if (a ^ v ^ c) ^ (b ^ vb ^ cb) != o:
                continue
            nxt.add(((a & v) | (a & c) | (v & c), (b & vb) | (b & cb) | (vb & cb)))
    return frozenset(nxt)


def dp_Q(targets):
    """targets: list of G values.  returns {pattern (tuple of bool): number of Q in Z_2^32}."""
    init = tuple(frozenset({(0, 0)}) for _ in targets)
    layer = {init: 1}
    for i in range(32):
        nl = {}
        e = ETA >> i & 1
        for st, n in layer.items():
            for q in (0, 1):
                ns = tuple(step_pairs(s, q, q, e, g >> i & 1) if s else s for s, g in zip(st, targets))
                nl[ns] = nl.get(ns, 0) + n
        layer = nl
    out = {}
    for st, n in layer.items():
        pat = tuple(bool(s) for s in st)
        out[pat] = out.get(pat, 0) + n
    return out, max(1, len(layer))


def dp_E(pairs):
    """pairs: list of (df1, eps).  E' = E + DY3.  returns {pattern: number of E}."""
    init = (0, tuple(frozenset({(0, 0)}) for _ in pairs))
    layer = {init: 1}
    width = 0
    for i in range(32):
        nl = {}
        dy = DY3 >> i & 1
        for (k, st), n in layer.items():
            for e in (0, 1):
                eb = e ^ dy ^ k
                kn = (e & dy) | (e & k) | (dy & k)
                ns = tuple(step_pairs(s, e, eb, df >> i & 1, ep >> i & 1) if s else s for s, (df, ep) in zip(st, pairs))
                key = (kn, ns)
                nl[key] = nl.get(key, 0) + n
        layer = nl
        width = max(width, len(layer))
    out = {}
    for (k, st), n in layer.items():
        pat = tuple(bool(s) for s in st)
        out[pat] = out.get(pat, 0) + n
    return out, width


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else 'bstar'
    rows = outcomes(which)
    taus = sorted({t for _, t, _, _ in rows})
    pairs = sorted({(t, e) for _, t, e, _ in rows})
    print(f'outcomes {which}: {len(rows)} rows, {len(taus)} distinct tau, {len(pairs)} distinct (tau, eps); '
          f'mass sum R = {float(sum(r for *_, r in rows)):,.2f}')
    # (1) over Q, per distinct tau
    pq, wq = dp_Q([G(t) for t in taus])
    # (2) over E, per distinct (tau, eps)
    pe, we = dp_E([(ror(G(t), 12), e) for t, e in pairs])
    tidx = {t: i for i, t in enumerate(taus)}
    pidx = {p: i for i, p in enumerate(pairs)}
    two32 = 2 ** 32
    s1 = sum(n for p, n in pq.items() if any(p))
    s2 = sum(n for p, n in pe.items() if any(p))
    print(f'(1) Q with some tau solvable: {s1} of 2^32 = 2^{log2(s1 / two32):.3f}   ({len(pq)} patterns, DP width {wq})')
    print(f'(2) E with some (tau,eps) solvable: {s2} of 2^32 = 2^{log2(s2 / two32):.3f}   ({len(pe)} patterns, DP width {we})')
    for t in taus:
        c1 = sum(n for p, n in pq.items() if p[tidx[t]])
        print(f'   tau {t:08x}: P(1 solvable) = 2^{log2(c1 / two32) if c1 else -99:.3f}', end='')
        for (tt, e) in pairs:
            if tt == t:
                c2 = sum(n for p, n in pe.items() if p[pidx[(tt, e)]])
                print(f' | eps {e:08x}: P(2 solvable) = 2^{log2(c2 / two32) if c2 else -99:.3f}', end='')
        print()
    # joint pass: an outcome (tau, eps) whose (1) and (2) are both solvable
    tot = 0
    for a, na in pq.items():
        if not any(a):
            continue
        for b, nb in pe.items():
            if not any(b):
                continue
            if any(a[tidx[t]] and b[pidx[(t, e)]] for (t, e) in pairs):
                tot += na * nb
    P = Fraction(tot, two32 * two32)
    print(f'P(pass) = {tot} / 2^64 = {float(P):.6e} = 2^{log2(float(P)):.4f}  (exact)')
    print(f'mass per passing outer step is 1/P(pass) = 2^{-log2(float(P)):.3f} times the average (skipped steps carry none)')


if __name__ == '__main__':
    main()
