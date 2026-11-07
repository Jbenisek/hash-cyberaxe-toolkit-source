"""filt_real.py (counter_next/knobs; research only): the feasibility shares of filt2.py on REAL outer steps.

Real outer steps (arrange_check.outer: seven random words + a sub-class member y) give Y9 and c = (Y3 + y) + w8.
A_t(Y9) and B_t(c) are evaluated by vectorised exact automata (reachable carry-pair sets, 4-bit masks), and the
shares are compared with the uniform-word figures of filt2.py / g1exact.py.  Also: uniform Y9, c with the same code
(control, and a cross-check of the automata against filt2.py).
usage: python -B filt_real.py NREAL SEED
"""
import sys, random, math
import numpy as np
sys.dont_write_bytecode = True
import e3dfs as D
import arrange_check as A

DY3 = (D.Y3B - D.Y3) & D.M32
rows, _ = D.load_targets()
bstar = [r for r in rows if r[1] == 0x18b0e098]
T = [D.outcome_target(r[2], r[3]) for r in bstar]
PAIRS = [(0, 0), (0, 1), (1, 0), (1, 1)]


def automaton(xa, xb, tbits, hdiff):
    """Reachable-set automaton over 32 bits.  xa, xb: uint64 arrays (first operands of the two sums, A and B);
    the second operand is a free word z (A) and z ^ hdiff (B); the XOR of the two sums must equal tbits.
    Returns bool array: some z exists."""
    n = len(xa)
    reach = np.zeros((n, 4), dtype=bool)
    reach[:, 0] = True
    for i in range(32):
        a = ((xa >> np.uint64(i)) & np.uint64(1)).astype(np.int64)
        b = ((xb >> np.uint64(i)) & np.uint64(1)).astype(np.int64)
        hd, tb = (hdiff >> i) & 1, (tbits >> i) & 1
        nr = np.zeros_like(reach)
        for s, (ca, cb) in enumerate(PAIRS):
            w = reach[:, s]
            for zb in (0, 1):
                sa = a + zb + ca
                sb = b + (zb ^ hd) + cb
                ok = w & (((sa & 1) ^ (sb & 1)) == tb)
                for s2, (na, nb) in enumerate(PAIRS):
                    nr[:, s2] |= ok & ((sa >> 1) == na) & ((sb >> 1) == nb)
        reach = nr
    return reach.any(axis=1)


def shares(Y9, c):
    Y9 = np.asarray(Y9, dtype=np.uint64)
    c = np.asarray(c, dtype=np.uint64)
    cp = (c + np.uint64(DY3)) & np.uint64(D.M32)
    am = np.zeros(len(Y9), dtype=np.int64)
    bm = np.zeros(len(c), dtype=np.int64)
    for ti, t in enumerate(T):
        am |= automaton(Y9, Y9, t[0], D.ETA).astype(np.int64) << ti          # g1 = Y9 + h, g1' = Y9 + (h ^ eta)
        bm |= automaton(c, cp, t[1], D.ror(t[0], 12)).astype(np.int64) << ti  # e2 = c + f1, e2' = c' + (f1 ^ phi)
    return am, bm


def report(tag, am, bm):
    n = len(am)
    ka, kb, kk = np.mean(am != 0), np.mean(bm != 0), np.mean((am & bm) != 0)
    f = lambda x: f'{x:.5f} (2^{math.log2(x):.3f})' if x > 0 else '0'
    print(f'{tag}: n {n}; Y9 feasible {f(ka)}; c feasible {f(kb)}; both for the same t (kept) {f(kk)} '
          f'[{int(np.sum((am & bm) != 0))} kept]')


def main():
    nreal, seed = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(seed)
    Y9s, cs = [], []
    for _ in range(nreal):
        o = A.outer(*[rng.getrandbits(32) for _ in range(7)], A.sub_member(rng))
        Y9s.append(o['Y9'])
        cs.append(((A.Y3A + o['y']) + o['w8']) & D.M32)
    am, bm = shares(Y9s, cs)
    report('real outer steps', am, bm)
    nr = np.random.default_rng(seed)
    am2, bm2 = shares(nr.integers(0, 2**32, nreal, dtype=np.uint64), nr.integers(0, 2**32, nreal, dtype=np.uint64))
    report('uniform words (control)', am2, bm2)
    # independence of the two conditions on real outer steps: kept vs product of per-target marginals
    pred = 1 - np.prod([1 - np.mean((am >> t) & 1) * np.mean((bm >> t) & 1) for t in range(len(T))])
    print(f'real outer steps: kept predicted from per-target marginals (independent Y9, c) {pred:.6f}')


if __name__ == '__main__':
    main()
