"""DDS (FSE 2012) double-kernel family on SHA3-256 r6, exact (COMPUTED). Replaces the slow dds.py loop.

Middle placement (the cheapest one for 6 rounds with a 2-round connector):
  connector delivers b2 = S (S and pi.rho(S) in the CP kernel),
  chi3: a3 = pi.rho(S)            weight w1 (paid)
  chi3 output b3 chosen in S(a3) and still in the kernel ("mid" choices)
  chi4: a4 = pi.rho(b3)           weight w2 (paid)
  chi4 output b4 chosen in S(a4); theta5 is NOT in the kernel (checked) and spreads
  chi5: a5 = L(b4)                weight F (paid)
  chi6: digest round.
For every class and every mid choice: exact min over b4 of F when 2^w2 <= 2^22 (numpy, exhaustive);
otherwise a rigorous lower bound F >= 0.8*min|theta(b4)| from an exact cyclic DP over slices.
Writes dds2.txt and dds2_best.json."""
import itertools
import json
import math
import time
import numpy as np
import kk

t0 = time.time()
out = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.append(s)


PI, PIINV = kk.RHOPI, kk.RHOPI_INV


def A_nb(i):
    x, y, z = kk.xyz(i)
    return [kk.idx(x, yy, z) for yy in range(5) if yy != y]


def B_nb(i):
    X, Y, Z = kk.xyz(PI[i])
    return [PIINV[kk.idx(X, YY, Z)] for YY in range(5) if YY != Y]


def in_kernel(s):
    return not kk.odd_columns(s)


def shift(s, d):
    return frozenset(kk.idx(*kk.xyz(i)[:2], (kk.xyz(i)[2] + d) % 64) for i in s)


def canon(s):
    return min(tuple(sorted(shift(s, d))) for d in range(64))


found6 = set()
for x in range(5):
    for z in range(64):
        for y1 in range(5):
            p1 = kk.idx(x, y1, z)
            for p2 in A_nb(p1):
                for p3 in B_nb(p2):
                    if p3 in (p1, p2):
                        continue
                    for p4 in A_nb(p3):
                        if p4 in (p1, p2):
                            continue
                        for p5 in B_nb(p4):
                            if p5 in (p1, p2, p3):
                                continue
                            for p6 in A_nb(p5):
                                if p6 in (p1, p2, p3, p4) or p1 not in B_nb(p6):
                                    continue
                                s = frozenset((p1, p2, p3, p4, p5, p6))
                                if len(s) == 6 and in_kernel(s) and in_kernel({PI[i] for i in s}):
                                    found6.add(canon(s))
classes = sorted(found6)
P(f"6-bit double-kernel classes: {len(classes)}  [{time.time() - t0:.1f}s]")

# ---------- numpy exact weight of L(b) over a product of row choices ----------
WTAB = np.array(kk.W, dtype=np.int32)


def vec(s):
    v = np.zeros(25, dtype=np.uint64)
    for i in s:
        v[i // 64] |= np.uint64(1) << np.uint64(i % 64)
    return v


def weights_of(arr):
    """arr (N,25) uint64 chi-input differences -> restriction weights (N,)"""
    bits = np.unpackbits(arr.view(np.uint8).reshape(arr.shape[0], 200), axis=1, bitorder="little")
    b = bits.reshape(-1, 5, 5, 64)                               # [n][y][x][z] uint8
    val = b[:, :, 0] | (b[:, :, 1] << 1) | (b[:, :, 2] << 2) | (b[:, :, 3] << 3) | (b[:, :, 4] << 4)
    return WTAB[val].sum(axis=(1, 2))


def exact_min_F(a_set, cap_log2=18):
    """min over b in S(a_set) of weight(L(b)); returns (minF, argmin b as set) or None if too big."""
    rw = kk.rows(a_set)
    keys = list(rw)
    opts = [kk.out_space(rw[k]) for k in keys]
    total = sum(math.log2(len(o)) for o in opts)
    if total > cap_log2:
        return None
    Lv = [[vec(kk.L_set(kk.unrows({k: o}))) for o in opts[j]] for j, k in enumerate(keys)]
    # split rows: inner block vectorized (<= 2^14), outer looped
    inner, acc = [], 0.0
    for j in range(len(keys)):
        if acc + math.log2(len(opts[j])) <= 14:
            inner.append(j)
            acc += math.log2(len(opts[j]))
    outer = [j for j in range(len(keys)) if j not in inner]
    base = np.zeros((1, 25), dtype=np.uint64)
    for j in inner:
        base = (base[:, None, :] ^ np.stack(Lv[j])[None, :, :]).reshape(-1, 25)
    inner_idx = list(itertools.product(*[range(len(opts[j])) for j in inner]))
    best = (10 ** 9, None)
    for oc in itertools.product(*[range(len(opts[j])) for j in outer]):
        off = np.zeros(25, dtype=np.uint64)
        for j, o in zip(outer, oc):
            off ^= Lv[j][o]
        w = weights_of(base ^ off[None, :])
        k = int(np.argmin(w))
        if int(w[k]) < best[0]:
            choice = dict(zip(outer, oc))
            choice.update(dict(zip(inner, inner_idx[k])))
            bset = kk.unrows({keys[j]: opts[j][choice[j]] for j in range(len(keys))})
            best = (int(w[k]), bset)
    return best


def dp_min_theta(a_set):
    """exact min over b in S(a_set) of |theta(b)| (bits), cyclic DP over the 64 slices."""
    rw = kk.rows(a_set)
    by_slice = {}
    for (y, z), v in rw.items():
        by_slice.setdefault(z, []).append((y, kk.out_space(v)))
    slice_choices = []
    for z in range(64):
        lst = []
        if z not in by_slice:
            lst.append(([0] * 5, 0))
        else:
            ys = [y for y, _ in by_slice[z]]
            for combo in itertools.product(*[o for _, o in by_slice[z]]):
                col = [0] * 5                       # col[x] = 5-bit vector over y
                for y, v in zip(ys, combo):
                    for x in range(5):
                        if (v >> x) & 1:
                            col[x] |= 1 << y
                par = sum(((bin(col[x]).count("1") & 1) << x) for x in range(5))
                lst.append((col, par))
        slice_choices.append(lst)
    best = 10 ** 9
    for s0 in range(32):
        cur = {s0: 0}
        for z in range(64):
            nxt = {}
            for pprev, cost in cur.items():
                for col, par in slice_choices[z]:
                    c = cost
                    for x in range(5):
                        e = ((par >> ((x - 1) % 5)) & 1) ^ ((pprev >> ((x + 1) % 5)) & 1)
                        n = bin(col[x]).count("1")
                        c += (5 - n) if e else n
                    if c < nxt.get(par, 10 ** 9):
                        nxt[par] = c
            cur = nxt
        if s0 in cur:
            best = min(best, cur[s0])
    return best


def choices(a_set):
    rw = kk.rows(a_set)
    keys = list(rw)
    opts = [kk.out_space(rw[k]) for k in keys]
    return [kk.unrows(dict(zip(keys, c))) for c in itertools.product(*opts)]


# sanity: numpy weight == kk.weight on random sets
rng = np.random.default_rng(5)
for _ in range(50):
    s = {int(i) for i in rng.integers(0, 1600, size=int(rng.integers(1, 60)))}
    assert int(weights_of(vec(s)[None, :])[0]) == kk.weight(s)
P("numpy weight check ok")

def main():
    import sys
    records = []
    LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else len(classes)
    for n, c in enumerate(classes[:LIMIT]):
        S = set(c)
        a3 = {PI[i] for i in S}
        w1 = kk.weight(a3)
        mids = [b for b in choices(a3) if in_kernel(b)]
        cls_best = None
        exact_n = bound_n = 0
        for b3 in mids:
            a4 = {PI[i] for i in b3}
            w2 = kk.weight(a4)
            res = exact_min_F(a4)
            if res is not None:
                F, b4 = res
                exact_n += 1
                kind = "exact"
            else:
                F = math.ceil(0.8 * dp_min_theta(a4))
                b4 = None
                bound_n += 1
                kind = "lower bound"
            rec = (w1 + w2 + F, w1, w2, F, kind, len(b3), sorted(S), sorted(b3), sorted(b4) if b4 else None)
            if cls_best is None or rec[0] < cls_best[0]:
                cls_best = rec
        records.append(cls_best)
        P(f"class {n}: w(chi3)={w1}  mids={len(mids)} (exact {exact_n}, bound {bound_n})  best w1+w2+F = {cls_best[0]} "
          f"(w2={cls_best[2]}, F={cls_best[3]} {cls_best[4]}, |b3|={cls_best[5]})  [{time.time() - t0:.1f}s]")

    records.sort(key=lambda r: r[0])
    P(f"\nmin over all classes and choices of w(chi3)+w(chi4)+w(chi5) = {records[0][0]} ({records[0][4]})")
    with open("dds2_best.json", "w") as f:
        json.dump(records, f)
    with open("dds2.txt", "w") as f:
        f.write("\n".join(out) + "\n")
    P(f"done [{time.time() - t0:.1f}s]")


if __name__ == "__main__":
    main()

