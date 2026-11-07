"""Independent numpy implementation of the truncated model in trunc_search.c, plus summaries and
route reconstruction.  One process, seconds per call.

  python -B analyze.py check  <results.bin> <Tdump.bin> [n]   cross-check C results on n patterns
  python -B analyze.py summary <init> <results.bin> [...]       minima per column (files merged by min)
  python -B analyze.py route   <init> <M> <model> [x0]          print one optimal route

init: -1 message-only, or the state word carrying the initial difference (14 = block length).
M: message-activity pattern (int, bit j = word m_j active).  model: A, B or C (see trunc_search.c).
"""
import random
import sys

import numpy as np

INF = 10_000
COLW = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAW = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
STEPS = ["K", "D", "C", "E"]
WEIGHTS = {"A": (0, 0, 0, 1), "B": (0, 0, 1, 1), "C": (1, 1, 1, 1)}   # K, D, C, E; fold always 1
COLS = ["A", "B", "C", "A@X0", "B@X0", "C@X0", "A_halfA", "A_halfB", "B_halfA", "B_halfB"]


def build_T():
    T = np.full((16, 4, 16), INF, dtype=np.int64)
    for inp in range(16):
        a, b, c, d = (inp >> 0) & 1, (inp >> 1) & 1, (inp >> 2) & 1, (inp >> 3) & 1
        for m in range(4):
            x, y = m & 1, (m >> 1) & 1
            # enumerate cancellation choices operation by operation
            def rec2(k, v, cost):
                if k == 8:
                    out = v[4] | (v[7] << 1) | (v[6] << 2) | (v[5] << 3)
                    T[inp, m, out] = min(T[inp, m, out], cost)
                    return
                if k == 0:
                    n = a + b + x
                elif k == 1:
                    n = d + v[0]
                elif k == 2:
                    n = c + v[1]
                elif k == 3:
                    n = b + v[2]
                elif k == 4:
                    n = v[0] + v[3] + y
                elif k == 5:
                    n = v[1] + v[4]
                elif k == 6:
                    n = v[2] + v[5]
                else:
                    n = v[3] + v[6]
                if n <= 1:
                    rec2(k + 1, v + [n], cost)
                else:
                    rec2(k + 1, v + [1], cost)
                    rec2(k + 1, v + [0], cost + 1)
            rec2(0, [], 0)
    return T


T1 = build_T()
T0 = np.where(T1 < INF, 0, INF)


def calls_of(step, M):
    """(words, msg activity) of the 4 calls of a step."""
    out = []
    for g in range(4):
        if step == "K":
            W, wx, wy = COLW[g], 2 * g, 2 * g + 1
        elif step == "D":
            W, wx, wy = DIAW[g], 8 + 2 * g, 9 + 2 * g
        elif step == "C":
            W, wx, wy = COLW[g], PERM[2 * g], PERM[2 * g + 1]
        else:
            W, wx, wy = DIAW[g], PERM[8 + 2 * g], PERM[9 + 2 * g]
        msg = ((M >> wx) & 1) | (((M >> wy) & 1) << 1)
        out.append((W, msg, wx, wy))
    return out


def apply_call(arr, W, Tw):
    wa, wb, wc, wd = W
    view = arr.reshape((2,) * 16)
    axes = [15 - wd, 15 - wc, 15 - wb, 15 - wa]
    v2 = np.moveaxis(view, axes, [0, 1, 2, 3])
    shp = v2.shape
    flat = v2.reshape(16, -1)
    new = np.min(flat[:, None, :] + Tw[:, :, None], axis=0)
    new = np.minimum(new, INF)
    back = np.moveaxis(new.reshape(shp), [0, 1, 2, 3], axes)
    return np.ascontiguousarray(back).reshape(-1)


LO = np.arange(65536) & 0xFF
HI = np.arange(65536) >> 8
FOLD_OK = LO == HI
POP = np.array([bin(i).count("1") for i in range(65536)])


def run_dp(init, M, model, x0=False, keep=False, half=None):
    wK, wD, wC, wE = WEIGHTS[model]
    arr = np.full(65536, INF, dtype=np.int64)
    arr[0 if init < 0 else (1 << init)] = 0
    hist = [("start", None, None, arr.copy())]
    for step, w in zip(STEPS, (wK, wD, wC, wE)):
        for (W, msg, wx, wy) in calls_of(step, M):
            Tw = (T1 if w else T0)[:, msg, :]
            arr = apply_call(arr, W, Tw)
            if keep:
                hist.append((step, W, Tw, arr.copy()))
        if step == "D" and x0:
            mask = np.full(65536, INF, dtype=np.int64)
            mask[0] = arr[0]
            arr = mask
            if keep:
                hist[-1] = (hist[-1][0], hist[-1][1], hist[-1][2], arr.copy())
    if half is None:
        fold = np.where(FOLD_OK, arr + POP[LO], INF)
    else:
        words = [0, 2, 5, 7] if half == "A" else [1, 3, 4, 6]
        mlo = sum(1 << i for i in words)
        ok = (LO & mlo) == (HI & mlo)
        fold = np.where(ok, arr + np.array([bin(i & mlo).count("1") for i in range(256)])[LO], INF)
    best = int(fold.min())
    return best, fold, hist


def bits(s):
    return [i for i in range(16) if (s >> i) & 1]


def route(init, M, model, x0=False):
    best, fold, hist = run_dp(init, M, model, x0=x0, keep=True)
    if best >= INF:
        print("no route")
        return
    s = int(np.argmin(fold))
    print(f"init={init} M={M} words m{bits(M)} model={model} x0={x0}: min conditions {best}")
    lo = s & 0xFF
    print(f"  final state Z active words {bits(s)}; fold cancellations {bin(lo).count('1')} on digest words {bits(lo)}")
    trail = []
    for k in range(len(hist) - 1, 0, -1):
        step, W, Tw, after = hist[k]
        before = hist[k - 1][3]
        o = sum(((s >> W[j]) & 1) << j for j in range(4))
        base = s & ~sum(1 << w for w in W)
        target = after[s]
        found = None
        for i in range(16):
            sin = base | sum(((i >> j) & 1) << W[j] for j in range(4))
            if before[sin] + Tw[i, o] == target and Tw[i, o] < INF:
                found = (sin, i, int(Tw[i, o]))
                break
        assert found, "backtrack failed"
        trail.append((step, W, found[1], o, found[2], s))
        s = found[0]
    trail.reverse()
    names = {"K": "K", "D": "D", "C": "C", "E": "E"}
    idx = {"K": 0, "D": 0, "C": 0, "E": 0}
    for step, W, i, o, c, s_after in trail:
        g = idx[step]
        idx[step] += 1
        lab = "abcd"
        ins = "".join(lab[j] for j in range(4) if (i >> j) & 1) or "-"
        outs = "".join(lab[j] for j in range(4) if (o >> j) & 1) or "-"
        print(f"  {names[step]}{g} words {W}: in {ins:4s} -> out {outs:4s} conditions(counted) {c}")
        if g == 3:
            print(f"    state after {step}: active words {bits(s_after)}")


def load(path):
    return np.fromfile(path, dtype=np.uint8).reshape(65536, 10).astype(np.int64)


def main():
    cmd = sys.argv[1]
    if cmd == "check":
        res = load(sys.argv[2])
        Tc = np.fromfile(sys.argv[3], dtype=np.uint8).reshape(16, 4, 16).astype(np.int64)
        Tc = np.where(Tc >= 200, INF, Tc)
        print("G table identical to C:", bool((Tc == T1).all()))
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 12
        done = [M for M in range(65536) if res[M, 0] < 200 or res[M, 2] < 200]
        rng = random.Random(7)
        sample = rng.sample(done, min(n, len(done)))
        mism = 0
        for M in sample:
            got = []
            for model in "ABC":
                b, _, _ = run_dp(-1, M, model)
                got.append(min(b, 200))
            for model in "AB":
                b, _, _ = run_dp(-1, M, model, half="A")
                got.append(min(b, 200))
            exp = [res[M, 0], res[M, 1], res[M, 2], res[M, 6], res[M, 8]]
            if got != list(exp):
                mism += 1
                print("MISMATCH", M, got, list(exp))
        print(f"cross-check {len(sample)} patterns: {len(sample) - mism} agree")
    elif cmd == "summary":
        res = None
        for p in sys.argv[3:]:
            r = load(p)
            res = r if res is None else np.minimum(res, r)
        init = int(sys.argv[2])
        rng_ok = np.arange(65536) != 0 if init < 0 else np.ones(65536, bool)
        for k, name in enumerate(COLS):
            col = np.where(rng_ok, res[:, k], 200)
            mn = int(col.min())
            arg = np.flatnonzero(col == mn)
            ex = ", ".join(f"{int(M)}:m{bits(int(M))}" for M in arg[:4])
            hist = np.bincount(np.minimum(col, 40), minlength=41)
            small = {v: int(hist[v]) for v in range(0, 41) if hist[v] and v <= mn + 3}
            print(f"{name:8s} min {mn:3d}  #patterns at min {len(arg):6d}  near-min counts {small}  e.g. {ex}")
        done = int((res[:, 0] < 200).sum())
        print(f"patterns with a finite model-A value: {done}")
    elif cmd == "route":
        init, M, model = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        x0 = len(sys.argv) > 5 and sys.argv[5] == "x0"
        route(init, M, model, x0=x0)


if __name__ == "__main__":
    main()
