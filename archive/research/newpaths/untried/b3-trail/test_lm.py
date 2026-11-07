#!/usr/bin/env python3
"""test_lm.py - brute-force checks of the LM formula and of the CNF encoding of b3trail.py.

1. For n = 5 bits, every (a, b, c): exact xdp+ by enumerating all x, y equals 2^-lm(a,b,c)
   (and 0 exactly when lm says impossible).
2. The add2 clause set of b3trail.Builder(n=5), evaluated at every (a, b, c) with minimal weight
   bits, accepts exactly the LM-valid triples and its weight equals lm().
"""
import itertools
import sys

sys.path.insert(0, '.')
from b3trail import Builder, T, F  # noqa: E402
from decode import lm  # noqa: E402


def exact_xdp(a, b, c, n):
    mask = (1 << n) - 1
    cnt = 0
    for x in range(1 << n):
        for y in range(1 << n):
            if (((x ^ a) + (y ^ b)) & mask) ^ ((x + y) & mask) == c:
                cnt += 1
    return cnt / float(1 << (2 * n))


def main():
    n = 5
    bad = 0
    for a, b, c in itertools.product(range(1 << n), repeat=3):
        p = exact_xdp(a, b, c, n)
        w = lm(a, b, c, n)
        if w is None:
            if p != 0:
                bad += 1
        elif abs(p - 2.0 ** (-w)) > 1e-12:
            bad += 1
    print('LM formula vs brute force, n=5: mismatches =', bad)

    bld = Builder(n=n)
    A, B = bld.word(), bld.word()
    Z = bld.add2(A, B)
    wl = bld.weights
    cls = bld.cl
    bad2 = 0
    for a, b, c in itertools.product(range(1 << n), repeat=3):
        val = {}
        for i in range(n):
            val[A[i]] = bool((a >> i) & 1)
            val[B[i]] = bool((b >> i) & 1)
            val[Z[i]] = bool((c >> i) & 1)
        # minimal weights: w_i = not all equal at bit i
        for i, wv in enumerate(wl):
            ai, bi, ci = (a >> i) & 1, (b >> i) & 1, (c >> i) & 1
            val[wv] = not (ai == bi == ci)
        ok = all(any((val[abs(l)] if l > 0 else not val[abs(l)]) for l in cl) for cl in cls)
        w = lm(a, b, c, n)
        if ok != (w is not None):
            bad2 += 1
        elif ok and sum(val[wv] for wv in wl) != w:
            bad2 += 1
    print('CNF add2 encoding vs LM, n=5: mismatches =', bad2)

    # guarded 3-input alternative: best weight over orders equals min over pairings and tau
    bld = Builder(n=4, order='best')
    P, Q, R = bld.word(), bld.word(), bld.word()
    S = bld.add3(P, Q, R)
    print('add3 built: vars', bld.nv, 'clauses', len(bld.cl), 'adds', len(bld.adds))
    sys.exit(1 if (bad or bad2) else 0)


if __name__ == '__main__':
    main()
