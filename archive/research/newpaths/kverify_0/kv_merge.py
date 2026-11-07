"""kverify_0: independent 4-list two-level merge (own code, not kmath's), with an exact completeness check.
Group = Z/2^w (add) x (Z/2)^w (xor), n = 2w.  Lists of 2^a1..2^a4 random elements.
Level 1 clamps the low t bits of the xor coordinate to tau (pairs 12) and tau (pairs 34; xor is self-inverse);
root matches the add coordinate fully and the remaining w-t xor bits.
Steps counted: list build, table inserts (L2, L4 once), stream lookups (L1, L3 per tau), level-1 outputs,
root inserts (L34), root lookups (L12), root outputs.
Usage: python kv_merge.py
"""
import sys
import time
import numpy as np

rng = np.random.default_rng(424242)


def mk(w, a):
    return (rng.integers(0, 1 << w, 1 << a, dtype=np.int64), rng.integers(0, 1 << w, 1 << a, dtype=np.int64))


def pairs_by_xor_low(X, Y, w, t, tau):
    """all (i,j) with low t bits of X.x ^ Y.x == tau; returns idx arrays; lookups = len(X)"""
    m = (1 << t) - 1
    ky = Y[1] & m
    order = np.argsort(ky, kind="stable")
    ks = ky[order]
    need = (X[1] & m) ^ tau
    lo = np.searchsorted(ks, need, "left")
    hi = np.searchsorted(ks, need, "right")
    cnt = hi - lo
    ix = np.repeat(np.arange(len(cnt)), cnt)
    start = np.repeat(lo - (np.cumsum(cnt) - cnt), cnt)
    iy = order[start + np.arange(int(cnt.sum()))]
    return ix, iy


def merge(L, w, t, taus, verify=True):
    mask = (1 << w) - 1
    steps = sum(len(l[0]) for l in L) + len(L[1][0]) + len(L[3][0])     # build + tables of L2, L4
    sols = 0
    bad = 0
    for tau in taus:
        i1, i2 = pairs_by_xor_low(L[0], L[1], w, t, tau)
        i3, i4 = pairs_by_xor_low(L[2], L[3], w, t, tau)
        steps += len(L[0][0]) + len(L[2][0]) + len(i1) + len(i3)
        sa12 = (L[0][0][i1] + L[1][0][i2]) & mask
        sx12 = L[0][1][i1] ^ L[1][1][i2]
        sa34 = (L[2][0][i3] + L[3][0][i4]) & mask
        sx34 = L[2][1][i3] ^ L[3][1][i4]
        # root: need sa12 + sa34 == 0 and sx12 ^ sx34 == 0 (high w-t bits; low t bits already equal tau)
        key34 = (((-sa34) & mask) << w) | (sx34 >> t << t)
        key12 = (sa12 << w) | (sx12 >> t << t)
        order = np.argsort(key34, kind="stable")
        ks = key34[order]
        lo = np.searchsorted(ks, key12, "left")
        hi = np.searchsorted(ks, key12, "right")
        cnt = hi - lo
        out = int(cnt.sum())
        steps += len(key34) + len(key12) + out
        if verify and out:
            ix = np.repeat(np.arange(len(cnt)), cnt)
            start = np.repeat(lo - (np.cumsum(cnt) - cnt), cnt)
            jy = order[start + np.arange(out)]
            a = (L[0][0][i1[ix]] + L[1][0][i2[ix]] + L[2][0][i3[jy]] + L[3][0][i4[jy]]) & mask
            x = L[0][1][i1[ix]] ^ L[1][1][i2[ix]] ^ L[2][1][i3[jy]] ^ L[3][1][i4[jy]]
            bad += int(((a != 0) | (x != 0)).sum())
        sols += out
    return sols, steps, bad


def exact_count(L, w):
    """number of 4-tuples with sum 0, by pair histograms over the whole group (2^(2w) cells)."""
    mask = (1 << w) - 1

    def hist(A, B):
        a = (A[0][:, None] + B[0][None, :]) & mask
        x = A[1][:, None] ^ B[1][None, :]
        return np.bincount(((a << w) | x).ravel(), minlength=1 << (2 * w))
    h12 = hist(L[0], L[1])
    h34 = hist(L[2], L[3])
    g = np.arange(1 << (2 * w))
    neg = (((-(g >> w)) & mask) << w) | (g & mask)
    return int((h12 * h34[neg]).sum())


def main():
    out = open("merge_results.txt", "a")

    def say(s):
        print(s, flush=True)
        out.write(s + "\n")
    say(f"=== kv_merge run {time.ctime()}")
    # 1. completeness: all taus, balanced lists 2^(n/2), exact count by histograms
    for w in (6, 8, 10):
        n = 2 * w
        L = [mk(w, w) for _ in range(4)]
        t0 = time.time()
        sols, steps, bad = merge(L, w, w, range(1 << w))
        ex = exact_count(L, w)
        say(f"COMPLETE n={n} lists 2^{w} t={w} all taus: found {sols} exact {ex} (2^n={1 << n}) bad={bad} "
            f"steps={steps} steps/sol={steps / max(sols, 1):.2f}  {time.time() - t0:.1f}s")
    # 2. M = 2^(n/2) members (one tau with t = n/2): steps per member including list build
    for w in (10, 12, 14, 16):
        n = 2 * w
        L = [mk(w, w) for _ in range(4)]
        sols, steps, bad = merge(L, w, w, [0])
        say(f"ONE-TAU n={n} lists 2^{w} t={w}: sols={sols} (exp {1 << w}) bad={bad} steps={steps} "
            f"steps/sol={steps / max(sols, 1):.2f}")
    # 3. unbalanced lists vs formula: per member 2^(n-min(a1+a2,a3+a4)) + stream 2^(n+t-a2-a3-a4) (+O(1))
    w = 10
    n = 2 * w
    for a, t in (((10, 10, 6, 6), 10), ((10, 10, 6, 6), 4), ((12, 8, 10, 10), 10), ((8, 8, 8, 8), 4),
                 ((11, 11, 11, 11), 10), ((10, 10, 10, 10), 2)):
        L = [mk(w, ai) for ai in a]
        T = min(1 << t, 64)
        sols, steps, bad = merge(L, w, t, range(T))
        build = sum(1 << ai for ai in a) + (1 << a[1]) + (1 << a[3])
        per = (steps - build) / max(sols, 1)
        f_main = 2.0 ** (n - min(a[0] + a[1], a[2] + a[3]))
        f_stream = 2.0 ** (n + t - a[1] - a[2] - a[3]) + 2.0 ** (n + t - a[0] - a[1] - a[3])
        exp_sols = T * 2.0 ** (sum(a) - n - t)
        say(f"UNBAL n={n} a={a} t={t} taus={T}: sols={sols} (exp {exp_sols:.0f}) bad={bad} "
            f"steps/sol excl build={per:.1f}  formula 2^(n-min)={f_main:.1f}  stream term={f_stream:.1f}  "
            f"predicted 2*(2^(n-a3-a4)+2^(n-a1-a2))+stream+1={2 * (2.0 ** (n - a[2] - a[3]) + 2.0 ** (n - a[0] - a[1])) + f_stream + 1:.1f}")
    out.close()


if __name__ == "__main__":
    main()
