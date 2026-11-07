"""affine.py: can small-t cube members be ENUMERATED instead of filtered? (a push on the method's size limit)

Per outer step the map F: c1 -> t (the counter solved from E1.d1 = c1 - Y11) is a bijection built from three
rotations (16, 7, 8: net ROR 1), XORs with constants and four additions of constants. Over the T1 cube (11 fixed
bits, 21 free bits) it is close to affine over GF(2). The affine-guided enumerator:
  1. evaluate F at the cube's base point and at base XOR e_i for the 21 free bits: delta_i = F(base^e_i)^F(base)
     (22 evaluations, about 300 word ops);
  2. solve over GF(2): bits >= k of F(base) ^ sum x_i delta_i must be 0 (32 - k equations, 21 unknowns);
     inconsistent -> skip the outer step;
  3. enumerate the solution space (particular + null space), compute F exactly on each candidate, keep t < 2^k.
Ground truth: all t in [1, 2^k) inverted through F^-1 (exact list of cube members with small t).
Reported: fraction of outer steps flagged good vs actually good, recall (true hits found / all true hits),
candidates per hit (exact evaluations per kept trial).
usage: python -B affine.py NOUTER K SEED [NBASE]
(NBASE linearization points per outer step: the cube base point, then random cube members)
"""
import math
import random
import sys

import numpy as np

sys.dont_write_bytecode = True
import arr
from sizecap import t_of_c1, c1_of_t

M = 0xFFFFFFFF


def gf2_solve(rows, rhs, n):
    """rows: list of int bitmasks over n unknowns; rhs: list of bits. Returns (particular, nullbasis) or None."""
    piv = []
    R = [(r, b) for r, b in zip(rows, rhs)]
    used = []
    pivcols = []
    for col in range(n):
        sel = None
        for i, (r, b) in enumerate(R):
            if i in used:
                continue
            if r >> col & 1:
                sel = i
                break
        if sel is None:
            continue
        used.append(sel)
        pivcols.append((col, sel))
        r0, b0 = R[sel]
        for i, (r, b) in enumerate(R):
            if i != sel and r >> col & 1:
                R[i] = (r ^ r0, b ^ b0)
    for i, (r, b) in enumerate(R):
        if r == 0 and b:
            return None
    part = 0
    for col, i in pivcols:
        if R[i][1]:
            part |= 1 << col
    pc = {c for c, _ in pivcols}
    null = []
    for f in range(n):
        if f in pc:
            continue
        v = 1 << f
        for col, i in pivcols:
            if R[i][0] >> f & 1:
                v |= 1 << col
        null.append(v)
    return part, null


def main():
    global NBASE
    nouter, k, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    NBASE = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rng = random.Random(seed)
    free = arr.FREE_CUBE
    base = np.uint32(arr.CUBE_VAL)
    ts = np.arange(1, 1 << k, dtype=np.uint32)
    hi_mask = (M >> k) << k
    good_true = good_flag = both = 0
    hits_true = hits_found = 0
    cand_total = 0
    dims = []
    for _ in range(nouter):
        o = arr.random_outer(rng)
        cc = c1_of_t(o, ts)
        true_set = set(int(x) for x in cc[(cc & np.uint32(arr.CUBE_MASK)) == np.uint32(arr.CUBE_VAL)])
        found = set()
        flagged = False
        for r in range(NBASE):
            b = arr.CUBE_VAL if r == 0 else arr.draw_c1(rng)
            pts = np.array([b] + [b ^ (1 << i) for i in free], dtype=np.uint32)
            tv = t_of_c1(o, pts)
            t0 = int(tv[0])
            deltas = [int(tv[1 + j]) ^ t0 for j in range(len(free))]
            rows, rhs = [], []
            for bit in range(k, 32):
                rows.append(sum(((deltas[j] >> bit) & 1) << j for j in range(len(free))))
                rhs.append((t0 >> bit) & 1)
            sol = gf2_solve(rows, rhs, len(free))
            if sol is None:
                continue
            flagged = True
            part, null = sol
            dims.append(len(null))
            d = len(null)
            idx = np.arange(1 << d, dtype=np.uint64)
            xs = np.full(1 << d, part, dtype=np.uint64)
            for j, v in enumerate(null):
                xs ^= ((idx >> np.uint64(j)) & np.uint64(1)) * np.uint64(v)
            c1 = np.full(len(xs), b, dtype=np.uint32)
            for j, i in enumerate(free):
                c1 ^= (((xs >> np.uint64(j)) & np.uint64(1)).astype(np.uint32)) << np.uint32(i)
            t = t_of_c1(o, c1)
            keep = c1[(t < np.uint32(1 << k)) & (t > 0)]
            found |= set(int(x) for x in keep)
            cand_total += len(c1)
        good_true += bool(true_set); good_flag += flagged; both += bool(true_set) and flagged
        hits_true += len(true_set); hits_found += len(found & true_set)
        assert found <= true_set
    print(f'affine-guided enumeration, k = {k} (t < 2^{k}), {nouter} outer steps, {NBASE} linearization point(s) per outer step')
    print(f'  outer steps actually holding small-t cube members: {good_true} ({good_true / nouter:.4f}); '
          f'flagged by the affine solve: {good_flag} ({good_flag / nouter:.4f}); both: {both}')
    print(f'  true hits {hits_true} (mean {hits_true / nouter:.3f} per outer step, uniform prediction {(2 ** k - 1) / 2 ** 11:.3f}); '
          f'found by enumeration {hits_found} (recall {hits_found / max(1, hits_true):.3f})')
    if dims:
        print(f'  null-space dimension when flagged: mean {np.mean(dims):.2f}, min {min(dims)}, max {max(dims)}')
    print(f'  exact evaluations of F (candidates) per found hit: {cand_total / max(1, hits_found):.2f}; '
          f'per outer step: {cand_total / nouter:.2f}; plus 22 evaluations + a 21-unknown GF(2) solve per outer step')
    eff = hits_found / nouter
    if eff > 0:
        for outer_ops in (400, 700):
            per_hit = (outer_ops + NBASE * (22 * 14 + 200)) / eff + 14 * cand_total / max(1, hits_found) + 6.5
            print(f'  cost per kept trial with {outer_ops} ops per outer step (GUESS), 14 ops per F evaluation, '
                  f'200 ops for the solve (GUESS): {per_hit:.0f} ops -> time_log2 about '
                  f'{84.96 + math.log2(per_hit / 6.5) - math.log2(hits_found / max(1, hits_true)) * 0:.2f} '
                  f'(rate loss from recall {-math.log2(max(1e-9, hits_found / max(1, hits_true))):.2f} bit is '
                  f'not a rate loss: missed hits are simply not used)')


if __name__ == '__main__':
    main()
