#!/usr/bin/env python3
"""e3solve.py [SEED] [PLANTS] [STEPS]   (counter_next/stack; research only)

Prototype of an E3-first solve for one outer step of the counter arrangement: given (y, Q = Y9, W = w8), find EVERY
h1 in Z_2^32 for which E3 matches an outcome (G, eps, tau):  (1) dg1 = G, (2) de2 = eps, (3) dg2 = tau.
Method: enumerate the solutions f1 of (2) by a carry DFS pruned with a backward feasibility table (output-sensitive),
map f1 -> g1 = ROL(f1,12) ^ y -> h1 = g1 - Q, test (1), then run E3 on both messages and test (3).
Checks: (a) PLANTS random real E3 pairs, each pair's own differences as the target: its h1 must be among the solutions
(completeness); every returned h1 must satisfy all three conditions on a forward re-run (soundness).
(b) STEPS outer steps that pass the exact outer filter (outer_filter.py) for the beta* outcomes: number of f1
solutions enumerated, DFS nodes, survivors of (1), solutions of (1)-(3); an op count of the solve.
"""
import random, sys
from math import log2
M = 0xFFFFFFFF
def ror(x, r): return ((x >> r) | (x << (32 - r))) & M
def rol(x, r): return ror(x, (32 - r) % 32)
Y3, Y3B, ETA = 0x8127C181, 0x7EDF3E7E, 0x830303CF
DY3 = (Y3B - Y3) & M
SUB_M, SUB_V = 0x07EF8303, 0x030C0303
EPS = 0x6E21BE55
TAUS = [0x175020A0, 0x185020A0, 0x275020A0, 0x285020A0, 0x385020A0, 0x675020A0, 0x685020A0]
def G(tau): return rol(tau ^ ror(tau, 1), 12)


def e3(a, y, q, h1, w8):
    e1 = (a + y) & M
    g1 = (q + h1) & M
    f1 = ror(y ^ g1, 12)
    e2 = (e1 + f1 + w8) & M
    h2 = ror(h1 ^ e2, 8)
    g2 = (g1 + h2) & M
    f2 = ror(f1 ^ g2, 7)
    return g1, f1, e2, h2, g2, f2


def trans(a, b, d, o, c, cb, v):
    vb = v ^ d
    if (a ^ v ^ c) ^ (b ^ vb ^ cb) != o:
        return None
    return ((a & v) | (a & c) | (v & c), (b & vb) | (b & cb) | (vb & cb))


def solutions_add_xor(x0, x1, dz, out, stats):
    """all v with (x0 + v) ^ (x1 + (v ^ dz)) == out; backward-pruned DFS.  stats[0] += nodes."""
    bits = [(x0 >> i & 1, x1 >> i & 1, dz >> i & 1, out >> i & 1) for i in range(32)]
    alive = [None] * 33
    alive[32] = {(0, 0), (0, 1), (1, 0), (1, 1)}
    for i in range(31, -1, -1):
        a, b, d, o = bits[i]
        s = set()
        for c in (0, 1):
            for cb in (0, 1):
                for v in (0, 1):
                    n = trans(a, b, d, o, c, cb, v)
                    if n is not None and n in alive[i + 1]:
                        s.add((c, cb)); break
        alive[i] = s
    res = []
    if (0, 0) not in alive[0]:
        return res
    stack = [(0, 0, 0, 0)]
    while stack:
        i, c, cb, v = stack.pop()
        stats[0] += 1
        if i == 32:
            res.append(v); continue
        a, b, d, o = bits[i]
        for bit in (0, 1):
            n = trans(a, b, d, o, c, cb, bit)
            if n is not None and n in alive[i + 1]:
                stack.append((i + 1, n[0], n[1], v | bit << i))
    return res


def solve_step(y, q, w8, targets, stats):
    """targets: list of (G, eps, tau).  returns sorted list of (h1, index)."""
    E = (Y3 + y + w8) & M
    Eb = (E + DY3) & M
    out = []
    for k, (g, eps, tau) in enumerate(targets):
        fs = solutions_add_xor(E, Eb, ror(g, 12), eps, stats)
        stats[1] += len(fs)
        for f1 in fs:
            g1 = rol(f1, 12) ^ y
            h1 = (g1 - q) & M
            if ((q + (h1 ^ ETA)) & M) ^ g1 != g:
                continue
            stats[2] += 1
            A = e3(Y3, y, q, h1, w8); B = e3(Y3B, y, q, h1 ^ ETA, w8)
            if A[4] ^ B[4] == tau:
                out.append((h1, k))
    return sorted(out)


def member(rng):
    return ((SUB_V | (rng.getrandbits(32) & ~SUB_M)) - Y3) & M


def solvable1(q, g):
    st = {(0, 0)}
    for i in range(32):
        a = q >> i & 1; d = ETA >> i & 1; o = g >> i & 1
        st = {n for (c, cb) in st for v in (0, 1) for n in [trans(a, a, d, o, c, cb, v)] if n is not None}
        if not st: return False
    return True


def solvable2(E, df1, eps):
    Eb = (E + DY3) & M
    st = {(0, 0)}
    for i in range(32):
        a, b, d, o = E >> i & 1, Eb >> i & 1, df1 >> i & 1, eps >> i & 1
        st = {n for (c, cb) in st for v in (0, 1) for n in [trans(a, b, d, o, c, cb, v)] if n is not None}
        if not st: return False
    return True


def main():
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
    plants = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    steps = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    # (a) completeness and soundness on planted real pairs
    miss = unsound = tot_sol = 0
    st = [0, 0, 0]
    for _ in range(plants):
        y, q, w8, h1 = member(rng), rng.getrandbits(32), rng.getrandbits(32), rng.getrandbits(32)
        A = e3(Y3, y, q, h1, w8); B = e3(Y3B, y, q, h1 ^ ETA, w8)
        tgt = (A[0] ^ B[0], A[2] ^ B[2], A[4] ^ B[4])
        sol = solve_step(y, q, w8, [tgt], st)
        tot_sol += len(sol)
        if (h1, 0) not in sol:
            miss += 1
        for hh, _ in sol:
            a = e3(Y3, y, q, hh, w8); b = e3(Y3B, y, q, hh ^ ETA, w8)
            if (a[0] ^ b[0], a[2] ^ b[2], a[4] ^ b[4]) != tgt:
                unsound += 1
    print(f'(a) planted {plants}: planted h1 missed {miss}, unsound solutions {unsound}, solutions per plant '
          f'{tot_sol / plants:.2f}, f1 enumerated per plant {st[1] / plants:.1f}, DFS nodes per plant {st[0] / plants:.1f}')
    # (b) beta* targets on outer steps that pass the exact filter
    targets = [(G(t), EPS, t) for t in TAUS]
    tried = passed = 0
    st = [0, 0, 0]; nsol = 0; viable = 0
    fcounts = []
    while passed < steps:
        tried += 1
        y, q, w8 = member(rng), rng.getrandbits(32), rng.getrandbits(32)
        E = (Y3 + y + w8) & M
        ok = [solvable1(q, g) and solvable2(E, ror(g, 12), e) for g, e, t in targets]
        if not any(ok):
            continue
        passed += 1
        sub = [tg for tg, k in zip(targets, ok) if k]
        viable += len(sub)
        before = st[1]
        nsol += len(solve_step(y, q, w8, sub, st))
        fcounts.append(st[1] - before)
    print(f'(b) outer steps tried {tried}, passing {passed} (share 2^{log2(passed / tried):.2f}; exact 2^-9.81)')
    print(f'    per passing step: viable outcomes {viable / passed:.2f}, f1 solutions of (2) {st[1] / passed:.1f} '
          f'(median {sorted(fcounts)[len(fcounts)//2]}, max {max(fcounts)}), DFS nodes {st[0] / passed:.1f}, '
          f'survivors of (1) {st[2] / passed:.3f}, E3 solutions {nsol} in total')
    # op count of the solve per passing step (scalar word ops, rotation 5): DFS node ~6, per f1 ~12 for (1), per
    # survivor ~40 for both E3 runs; backward table 32 x 8 x ~4 per viable outcome (or 4 byte-table loads)
    ops = st[0] / passed * 6 + st[1] / passed * 12 + st[2] / passed * 40 + viable / passed * 32 * 8 * 4
    print(f'    ops per passing step (DERIVED weights above): about {ops:,.0f} = 2^{log2(ops):.2f}; per walked outer step '
          f'x 2^-9.81 = {ops * 2 ** -9.8132:,.1f}')


if __name__ == '__main__':
    main()
