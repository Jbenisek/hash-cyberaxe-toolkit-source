#!/usr/bin/env python3
"""e3solve2.py [SEED] [STEPS]   (counter_next/stack; research only)

Joint DFS for the E3-first solve: walk the bits of h1 from 0 to 31, carrying the (1)-automaton state (carries of
Q + h1 and Q + (h1 ^ eta)); g1 = Q + h1 is known bit by bit, and f1 bit k = (y ^ g1) bit k+12, so from bit 12 on
the (2)-automaton (carries of E + f1 and E' + f1') advances too; both are pruned by exact backward feasibility tables.
At the leaf the (2)-automaton finishes on f1 bits 20..31 = (y ^ g1) bits 0..11.  Output: all h1 with (1) and (2).
Checked against e3solve.py's solver (enumerate (2), filter by (1)) on the same passing outer steps: the two solution
sets must be equal.  Reports DFS nodes per passing step.
"""
import random, sys
from math import log2
sys.dont_write_bytecode = True
import e3solve as S        # same folder (own code)
M, ETA, DY3, Y3, EPS = S.M, S.ETA, S.DY3, S.Y3, S.EPS
ror, rol, trans = S.ror, S.rol, S.trans


def backward(x0, x1, dz, out):
    alive = [None] * 33
    alive[32] = {(0, 0), (0, 1), (1, 0), (1, 1)}
    for i in range(31, -1, -1):
        a, b, d, o = x0 >> i & 1, x1 >> i & 1, dz >> i & 1, out >> i & 1
        alive[i] = {(c, cb) for c in (0, 1) for cb in (0, 1)
                    if any((n := trans(a, b, d, o, c, cb, v)) is not None and n in alive[i + 1] for v in (0, 1))}
    return alive


def joint(y, q, E, g, eps, stats):
    Eb = (E + DY3) & M
    df1 = ror(g, 12)
    al1 = backward(q, q, ETA, g)
    al2 = backward(E, Eb, df1, eps)
    if (0, 0) not in al1[0] or (0, 0) not in al2[0]:
        return []
    res = []
    # node: (i, s1, s2, h1 prefix, g1 prefix)
    stack = [(0, (0, 0), (0, 0), 0, 0)]
    while stack:
        i, s1, s2, h, gg = stack.pop()
        stats[0] += 1
        if i == 32:
            st = s2
            ok = True
            for k in range(20, 32):
                f = (y ^ gg) >> (k - 20) & 1
                st = trans(E >> k & 1, Eb >> k & 1, df1 >> k & 1, eps >> k & 1, st[0], st[1], f)
                if st is None or st not in al2[k + 1]:
                    ok = False; break
            if ok:
                res.append(h)
            continue
        a, d, o = q >> i & 1, ETA >> i & 1, g >> i & 1
        for v in (0, 1):
            n1 = trans(a, a, d, o, s1[0], s1[1], v)
            if n1 is None or n1 not in al1[i + 1]:
                continue
            gbit = a ^ v ^ s1[0]
            n2 = s2
            if i >= 12:
                k = i - 12
                f = (y >> i & 1) ^ gbit
                n2 = trans(E >> k & 1, Eb >> k & 1, df1 >> k & 1, eps >> k & 1, s2[0], s2[1], f)
                if n2 is None or n2 not in al2[k + 1]:
                    continue
            stack.append((i + 1, n1, n2, h | v << i, gg | gbit << i))
    return res


def main():
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 11)
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    targets = [(S.G(t), EPS, t) for t in S.TAUS]
    passed = tried = mism = 0
    nodes = [0]; nsol = 0; st_simple = [0, 0, 0]; viable = 0
    while passed < steps:
        tried += 1
        y, q, w8 = S.member(rng), rng.getrandbits(32), rng.getrandbits(32)
        E = (Y3 + y + w8) & M
        ok = [S.solvable1(q, g) and S.solvable2(E, ror(g, 12), e) for g, e, t in targets]
        if not any(ok):
            continue
        passed += 1
        for (g, e, t), k in zip(targets, ok):
            if not k:
                continue
            viable += 1
            a = sorted(joint(y, q, E, g, e, nodes))
            # simple solver's (1)&(2) set
            fs = S.solutions_add_xor(E, (E + DY3) & M, ror(g, 12), e, st_simple)
            b = sorted(h1 for h1 in (((rol(f1, 12) ^ y) - q) & M for f1 in fs)
                       if ((q + (h1 ^ ETA)) & M) ^ ((q + h1) & M) == g)
            mism += a != b
            nsol += len(a)
    print(f'passing outer steps {passed} of {tried}; viable outcomes per step {viable / passed:.2f}')
    print(f'joint DFS: nodes per passing step {nodes[0] / passed:,.1f} (2^{log2(nodes[0] / passed):.2f}); '
          f'(1)&(2) solutions per passing step {nsol / passed:.2f}; set mismatches against the simple solver {mism}')
    print(f'simple solver on the same steps: DFS nodes {st_simple[0] / passed:,.1f}, f1 solutions {st_simple[1] / passed:,.1f}')
    # op weights (DERIVED, scalar word ops): node ~10, backward tables 2 x 32 x 8 x 3 per viable outcome,
    # (3) check of a (1)&(2) solution: both E3 runs ~40
    ops = nodes[0] / passed * 10 + viable / passed * 2 * 32 * 8 * 3 + nsol / passed * 40
    print(f'ops per passing step about {ops:,.0f} = 2^{log2(ops):.2f}; per walked step x 2^-9.8132 = {ops * 2 ** -9.8132:,.1f}')


if __name__ == '__main__':
    main()
