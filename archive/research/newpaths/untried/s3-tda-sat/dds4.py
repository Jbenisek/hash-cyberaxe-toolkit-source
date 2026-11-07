"""DDS double-kernel family on SHA3-256 r6, middle placement: EXACT min of w(chi5) per mid by factor tables (COMPUTED).

w(L(b4)) = sum over chi5 rows R of W(value_R), value_R = XOR of the contributions of the chi4-output rows that touch R
(L is linear, so theta cancellations are included).  Each R is a factor over the few variables touching it;
the sum is accumulated on the full grid of variable choices with numpy broadcasting, chunked on leading variables.
Usage: python dds4.py <first_class> <last_class_exclusive> [max_vars_exact=14]
Appends per-class lines to dds4.txt and per-mid lines to dds4_mids.txt."""
import sys
import math
import time
import itertools
import numpy as np
import kk
import dds2 as D

t0 = time.time()
lo, hi = int(sys.argv[1]), int(sys.argv[2])
MAXV = int(sys.argv[3]) if len(sys.argv) > 3 else 14
PI = kk.RHOPI


def factor_min(a_set, cost_of_value, relevant=lambda R: True):
    """exact min over b in S(a_set) of sum_R cost(value_R of L(b)) ; returns (min, b)."""
    rw = kk.rows(a_set)
    keys = list(rw)
    opts = [kk.out_space(rw[k]) for k in keys]
    nv = len(keys)
    contrib = []   # contrib[j][o] = {R: value}
    for j, k in enumerate(keys):
        lst = []
        for o in opts[j]:
            d = {}
            for i in kk.L_set(kk.unrows({k: o})):
                x, y, z = kk.xyz(i)
                if relevant((y, z)):
                    d[(y, z)] = d.get((y, z), 0) ^ (1 << x)
            lst.append(d)
        contrib.append(lst)
    touch = {}
    for j in range(nv):
        for d in contrib[j]:
            for R in d:
                touch.setdefault(R, set()).add(j)
    # build merged factor tables keyed by variable tuple
    tables = {}
    for R, vs in touch.items():
        vs = tuple(sorted(vs))
        shape = tuple(len(opts[j]) for j in vs)
        tab = np.zeros(shape, dtype=np.float64)
        for combo in itertools.product(*[range(len(opts[j])) for j in vs]):
            v = 0
            for j, o in zip(vs, combo):
                v ^= contrib[j][o].get(R, 0)
            tab[combo] = cost_of_value(R, v)
        if vs in tables:
            tables[vs] = tables[vs] + tab
        else:
            tables[vs] = tab
    sizes = [len(o) for o in opts]
    # chunk on leading variables so that each chunk grid has <= 2^24 cells
    lead = 0
    while lead < nv and math.prod(sizes[lead:]) > 2 ** 24:
        lead += 1
    best = (math.inf, None)
    rest = list(range(lead, nv))
    for lc in itertools.product(*[range(sizes[j]) for j in range(lead)]):
        grid = np.zeros([sizes[j] for j in rest], dtype=np.float32)
        for vs, tab in tables.items():
            # fix leading variables, then broadcast over the rest
            sub = tab.astype(np.float32)
            keep = []
            for pos, j in enumerate(vs):
                if j < lead:
                    sub = np.take(sub, lc[j], axis=len(keep))
                else:
                    keep.append(j)
            shape = [1] * len(rest)
            for j in keep:
                shape[rest.index(j)] = sizes[j]
            grid = grid + sub.reshape(shape)
        k = int(np.argmin(grid))
        val = float(grid.flat[k])
        if val < best[0]:
            ridx = np.unravel_index(k, grid.shape)
            choice = list(lc) + [int(t) for t in ridx]
            best = (val, kk.unrows({keys[j]: opts[j][choice[j]] for j in range(nv)}))
    return best


def chi_cost(R, v):
    return kk.W[v]


if __name__ == "__main__":
    # self-check against the brute-force numpy minimum on the identity mid of class 0
    S0 = set(D.classes[0])
    a4 = {PI[i] for i in {PI[i] for i in S0}}
    bf = D.exact_min_F(a4, cap_log2=14)[0]
    fm, b = factor_min(a4, chi_cost)
    assert abs(fm - bf) < 1e-9 and kk.weight(kk.L_set(b)) == bf, (fm, bf)
    print(f"factor method check: {fm} == brute force {bf}", flush=True)
    lines, mlines = [], []
    for n in range(lo, hi):
        S = set(D.classes[n])
        a3 = {PI[i] for i in S}
        w1 = kk.weight(a3)
        mids = [b for b in D.choices(a3) if D.in_kernel(b)]
        best_exact, best_bound = None, None
        for b3 in mids:
            a4 = {PI[i] for i in b3}
            w2 = kk.weight(a4)
            nvars = len(kk.rows(a4))
            if nvars <= MAXV:
                F, b4 = factor_min(a4, chi_cost)
                F = int(round(F))
                assert kk.weight(kk.L_set(b4)) == F
                T = w1 + w2 + F
                mlines.append(f"class {n} |b3|={len(b3)} vars={nvars} w2={w2} F={F} exact T3={T}")
                if best_exact is None or T < best_exact[0]:
                    best_exact = (T, w2, F, sorted(b3), sorted(b4))
            else:
                Flb = math.ceil(0.8 * D.dp_min_theta(a4))
                T = w1 + w2 + Flb
                mlines.append(f"class {n} |b3|={len(b3)} vars={nvars} w2={w2} F>={Flb} bound T3>={T}")
                if best_bound is None or T < best_bound[0]:
                    best_bound = (T, w2, Flb)
        line = (f"class {n}: w(chi3)={w1} mids={len(mids)}  min exact T3 = {best_exact[0]} (w2={best_exact[1]}, "
                f"F={best_exact[2]}); non-exact mids T3 >= {best_bound[0] if best_bound else '-'}  [{time.time() - t0:.1f}s]")
        print(line, flush=True)
        lines.append(line)
        with open(f"dds4_best_class{n}.txt", "w") as f:
            f.write(repr(best_exact) + "\n")
    with open("dds4.txt", "a") as f:
        f.write("\n".join(lines) + "\n")
    with open("dds4_mids.txt", "a") as f:
        f.write("\n".join(mlines) + "\n")
