"""DDS (FSE 2012) double-kernel family on SHA3-256 r6: exact enumeration (COMPUTED).

S = 6-bit set with S in the CP kernel and pi.rho(S) in the CP kernel (a 6-cycle of column pairs).
Places the double kernel at theta_{k+1}, theta_{k+2} and computes, exactly,
  F(S)  = min over the chi output choices of the round after the double kernel of the next chi weight
          (the first out-of-kernel theta spread), over every kernel-keeping middle choice;
  the weight of the two kernel rounds;
  whether any choice keeps a third theta in the kernel (triple kernel), forward or backward.
Writes dds.txt and dds_best.json.  Single process, z-translation classes only."""
import itertools
import json
import time
import kk

t0 = time.time()
out = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.append(s)


PI = kk.RHOPI
PIINV = kk.RHOPI_INV


def colkey(i):
    x, y, z = kk.xyz(i)
    return (x, z)


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


# ---- enumerate 4-cycles and 6-cycles ----
found4, found6 = set(), set()
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
                        if p1 in B_nb(p4):
                            s = frozenset((p1, p2, p3, p4))
                            if len(s) == 4 and in_kernel(s) and in_kernel({PI[i] for i in s}):
                                found4.add(canon(s))
                        for p5 in B_nb(p4):
                            if p5 in (p1, p2, p3):
                                continue
                            for p6 in A_nb(p5):
                                if p6 in (p1, p2, p3, p4):
                                    continue
                                if p1 in B_nb(p6):
                                    s = frozenset((p1, p2, p3, p4, p5, p6))
                                    if len(s) == 6 and in_kernel(s) and in_kernel({PI[i] for i in s}):
                                        found6.add(canon(s))
P(f"4-bit double-kernel classes (z-translation): {len(found4)}")
P(f"6-bit double-kernel classes (z-translation): {len(found6)}  [{time.time() - t0:.1f}s]")

# message-legal members (all 6 bits in the 1080 free bits) for the early placement
legal = 0
for c in found6:
    for d in range(64):
        if set(shift(c, d)) <= kk.FREE:
            legal += 1
P(f"6-bit patterns (all z-shifts) lying inside the 1080 free message bits: {legal}")


def choices(a_set):
    """all chi output differences for chi input difference a_set (list of sets)."""
    rw = kk.rows(a_set)
    keys = list(rw)
    opts = [kk.out_space(rw[k]) for k in keys]
    res = []
    for combo in itertools.product(*opts):
        res.append(kk.unrows(dict(zip(keys, combo))))
    return res


best = []
tri_fwd = 0
tri_bwd = 0
for n, c in enumerate(sorted(found6)):
    S = set(c)
    a1 = {PI[i] for i in S}                 # chi input after the first kernel theta (identity)
    w1 = kk.weight(a1)
    # middle choices: chi output after the first kernel round that stays in the kernel
    mids = [b for b in choices(a1) if in_kernel(b)]
    bestF = None
    for b1 in mids:
        a2 = {PI[i] for i in b1}            # second kernel theta is identity
        w2 = kk.weight(a2)
        for b2 in choices(a2):
            if in_kernel(b2):
                tri_fwd += 1
            a3 = kk.L_set(b2)
            w3 = kk.weight(a3)
            if bestF is None or (w3, w1 + w2) < (bestF[0], bestF[1]):
                bestF = (w3, w1 + w2, sorted(S), sorted(b1), sorted(b2), len(a3), len(kk.rows(a3)))
    # backward: is pi^-1 of any chi-compatible input of S's rows in the kernel? (would give a 3rd kernel round)
    rwS = kk.rows(S)
    keys = list(rwS)
    opts = []
    for k in keys:
        lst = []
        for a in range(1, 32):
            if kk.DDT[a][rwS[k]]:
                m = 0
                for i in kk.unrows({k: a}):
                    x, y, z = kk.xyz(PIINV[i])
                    m ^= 1 << (x + 5 * z)
                lst.append(m)
        opts.append(lst)
    h = len(opts) // 2

    def xors(lists):
        acc = {0}
        for l in lists:
            acc = {u ^ v for u in acc for v in l}
        return acc

    if xors(opts[:h]) & xors(opts[h:]):
        tri_bwd += 1
    best.append(bestF)
    if n % 10 == 0:
        P(f"  class {n}: kernel rounds w={bestF[1]}, F={bestF[0]} (a has {bestF[5]} bits/{bestF[6]} rows), "
          f"kernel-keeping middle choices={len(mids)}  [{time.time() - t0:.1f}s]")

best.sort()
P(f"\nforward third kernel (some chi choice keeps theta in kernel a 3rd time): {tri_fwd} cases")
P(f"backward third kernel (some chi-compatible input pre-image in kernel): {tri_bwd} classes")
Fs = sorted(b[0] for b in best)
P(f"F(S) over {len(best)} classes: min {Fs[0]}, median {Fs[len(Fs) // 2]}, max {Fs[-1]}")
P(f"two kernel rounds weight for the min-F class: {best[0][1]}")
P("lowest 10 (F, kernel-round weight, a-bits, a-rows):", [(b[0], b[1], b[5], b[6]) for b in best[:10]])
with open("dds_best.json", "w") as f:
    json.dump(best[:20], f)
with open("dds.txt", "w") as f:
    f.write("\n".join(out) + "\n")
P(f"done [{time.time() - t0:.1f}s]")
