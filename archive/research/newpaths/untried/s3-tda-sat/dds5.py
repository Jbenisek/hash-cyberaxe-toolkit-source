"""DDS middle placement: achievable collision probability through chi5 + digest round (COMPUTED, linear algebra).

Given chi5 input difference a5, the chi5 output difference b5 is uniform on the affine space S(a5) (dim w(a5)).
The digest collides when every plane-0 chi6 row has an allowed input difference.  Relaxation used here
(sufficient, so it gives an ACHIEVABLE probability, i.e. an upper bound on the cost):
  bits x=0..3 of all 64 plane-0 chi6 rows are zero  -> probability 2^-r over b5 (r = rank, if consistent),
  then each plane-0 row with only its x=4 bit set costs 2 conditions (PD = 8/32);
  cost C_ub = r + 2*E|x4| (Jensen), E|x4| = (#constant-1 bits) + (#non-constant bits)/2.
Total over the b4 choices of a mid:  P = 2^-(w3+w4) * sum_b4 2^-C_ub(L(b4)).
Usage: python dds5.py <first_class> <last_class_exclusive> [max_w4=13]"""
import sys
import math
import time
import kk
import dds2 as D

t0 = time.time()
lo, hi = int(sys.argv[1]), int(sys.argv[2])
MAXW4 = int(sys.argv[3]) if len(sys.argv) > 3 else 13
PI = kk.RHOPI


def plane0_vec(s):
    """bits of a chi6-input difference in plane y=0 -> (low256 int for x=0..3, x4 64-bit int)."""
    lo256, x4 = 0, 0
    for i in s:
        x, y, z = kk.xyz(i)
        if y != 0:
            continue
        if x < 4:
            lo256 ^= 1 << (x * 64 + z)
        else:
            x4 ^= 1 << z
    return lo256, x4


def row_affine(v):
    sp = kk.out_space(v)
    base = sp[0]
    basis = []
    for b in sp:
        u = b ^ base
        for q in basis:
            u = min(u, u ^ q)
        if u:
            basis.append(u)
    return base, basis


def digest_cost_ub(a5):
    """returns (C_ub or inf, r, c1, nc, dim) for chi5 input difference a5."""
    rw = kk.rows(a5)
    base_set = set()
    dirs = []
    for (y, z), v in rw.items():
        b0, basis = row_affine(v)
        base_set ^= kk.unrows({(y, z): b0})
        for u in basis:
            dirs.append(kk.unrows({(y, z): u}))
    dim = len(dirs)
    B0 = plane0_vec(kk.L_set(base_set))
    vecs = [plane0_vec(kk.L_set(d)) for d in dirs]
    # Gaussian elimination on the 256-bit part, carrying the x4 part
    pivots = {}  # pivot bit -> (lo, x4)
    kernel_x4 = []
    for lo_, x4 in vecs:
        while lo_:
            p = lo_.bit_length() - 1
            if p in pivots:
                plo, px4 = pivots[p]
                lo_ ^= plo
                x4 ^= px4
            else:
                pivots[p] = (lo_, x4)
                break
        if not lo_:
            kernel_x4.append(x4)
    r = len(pivots)
    blo, bx4 = B0
    while blo:
        p = blo.bit_length() - 1
        if p not in pivots:
            return math.inf, r, None, None, dim
        plo, px4 = pivots[p]
        blo ^= plo
        bx4 ^= px4
    varying = 0
    for k in kernel_x4:
        varying |= k
    # a coordinate is non-constant iff some kernel direction has it set (span support = OR of generators)
    nc = bin(varying).count("1")
    c1 = bin(bx4 & ~varying).count("1")
    return r + 2 * c1 + nc, r, c1, nc, dim


if __name__ == "__main__":
    for n in range(lo, hi):
        S = set(D.classes[n])
        a3 = {PI[i] for i in S}
        w3 = kk.weight(a3)
        mids = [b for b in D.choices(a3) if D.in_kernel(b)]
        cls_best = None
        for b3 in mids:
            a4 = {PI[i] for i in b3}
            w4 = kk.weight(a4)
            if w4 > MAXW4:
                continue
            tot = 0.0
            best_single = None
            for b4 in D.choices(a4):
                a5 = kk.L_set(b4)
                C, r, c1, nc, dim = digest_cost_ub(a5)
                if C < math.inf:
                    tot += 2.0 ** (-C)
                    if best_single is None or C < best_single[0]:
                        best_single = (C, r, c1, nc, dim, kk.weight(a5))
            if tot > 0:
                T = w3 + w4 - math.log2(tot)
                rec = (T, w3, w4, best_single)
                if cls_best is None or T < cls_best[0]:
                    cls_best = rec
        if cls_best:
            C, r, c1, nc, dim, w5 = cls_best[3]
            print(f"class {n}: achievable T = {cls_best[0]:.2f} (w3={cls_best[1]}, w4={cls_best[2]}); best single b4: "
                  f"C_ub={C} (rank r={r}, x4 const-1={c1}, x4 varying={nc}; chi5 weight w5={w5}=dim {dim})  "
                  f"[{time.time() - t0:.1f}s]", flush=True)
        else:
            print(f"class {n}: relaxation inconsistent for every b4 of every mid with w4<={MAXW4}  "
                  f"[{time.time() - t0:.1f}s]", flush=True)
