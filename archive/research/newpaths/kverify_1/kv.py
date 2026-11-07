"""kverify_1: independent check of the 4-list two-level merge (lists 2^(n/2), n check bits).
Different code from kmath/kmerge.py: plain Python dicts, exact solution count by histogram convolution.
Group = 4 coordinates of w bits: add, xor, add, xor  (n = 4w).  Usage: python kv.py
"""
import sys
import numpy as np

TYPES = ["add", "xor", "add", "xor"]


def run(w, seed, clamp_coords, max_clamps=None):
    rng = np.random.default_rng(seed)
    n, a = 4 * w, 2 * w                      # lists of 2^(n/2)
    M = (1 << w) - 1
    L = [rng.integers(0, 1 << w, size=(1 << a, 4)).tolist() for _ in range(4)]
    op = lambda u, v: tuple(((u[j] + v[j]) & M) if TYPES[j] == "add" else (u[j] ^ v[j]) for j in range(4))
    neg = lambda u: tuple(((-u[j]) & M) if TYPES[j] == "add" else u[j] for j in range(4))
    # exact number of solutions f1+f2+f3+f4 = 0 (histogram of pair sums)
    def hist(A, B):
        h = {}
        for x in A:
            for y in B:
                s = op(x, y)
                h[s] = h.get(s, 0) + 1
        return h
    h12, h34 = hist(L[0], L[1]), hist(L[2], L[3])
    exact = sum(c * h34.get(neg(g), 0) for g, c in h12.items())
    C = clamp_coords
    R = [j for j in range(4) if j not in C]
    key = lambda u, idx: tuple(u[j] for j in idx)
    steps = {"build": 4 << a, "ins": 0, "look": 0, "out": 0}
    D2, D4 = {}, {}
    for j, v in enumerate(L[1]):
        D2.setdefault(key(v, C), []).append(j)
    for j, v in enumerate(L[3]):
        D4.setdefault(key(v, C), []).append(j)
    steps["ins"] += 2 << a
    members, bad, seen = 0, 0, set()
    clamps = 0
    import itertools
    for cvals in itertools.product(range(1 << w), repeat=len(C)):
        if max_clamps is not None and clamps >= max_clamps:
            break
        clamps += 1
        c = [0] * 4
        for j, cv in zip(C, cvals):
            c[j] = cv
        cn = neg(c)
        def level1(LA, LB, DB, tgt):
            out = []
            for i, x in enumerate(LA):
                need = tuple(((tgt[j] - x[j]) & M) if TYPES[j] == "add" else (tgt[j] ^ x[j]) for j in C)
                steps["look"] += 1
                for jj in DB.get(need, ()):
                    out.append((i, jj, op(x, LB[jj])))
            steps["out"] += len(out)
            return out
        L12 = level1(L[0], L[1], D2, c)
        L34 = level1(L[2], L[3], D4, cn)
        T = {}
        for (k, l, s) in L34:
            T.setdefault(key(s, R), []).append((k, l, s))
        steps["ins"] += len(L34)
        for (i, j, s) in L12:
            steps["look"] += 1
            for (k, l, s2) in T.get(key(neg(s), R), ()):
                steps["out"] += 1
                members += 1
                tot = op(s, s2)
                if any(tot):
                    bad += 1
                seen.add((i, j, k, l))
    tot = sum(steps.values())
    return dict(n=n, a=a, t=w * len(C), clamps=clamps, exact=exact, members=members, distinct=len(seen),
                bad=bad, steps=steps, steps_per_member=tot / max(members, 1))


if __name__ == "__main__":
    out = open("kv_results.txt", "w")
    def say(s):
        print(s, flush=True)
        out.write(s + "\n")
    for w, seed in ((3, 1), (4, 2), (5, 3)):
        r = run(w, seed, [0, 1])                     # t = n/2, ALL clamp values
        say(f"ALL   n={r['n']:2d} a={r['a']:2d} t={r['t']:2d} clamps={r['clamps']:5d} exact={r['exact']:8d} "
            f"found={r['members']:8d} distinct={r['distinct']:8d} bad={r['bad']} steps/member={r['steps_per_member']:.2f} {r['steps']}")
        r = run(w, seed, [0, 1], max_clamps=1)       # t = n/2, ONE clamp value  (2^(n/2) members: the 2^64-of-2^128 regime)
        say(f"ONE   n={r['n']:2d} a={r['a']:2d} t={r['t']:2d} clamps={r['clamps']:5d} members={r['members']:8d} "
            f"(2^(n/2)={1 << (r['n'] // 2)}) bad={r['bad']} steps/member={r['steps_per_member']:.2f} {r['steps']}")
        r = run(w, seed, [0, 1, 2], max_clamps=64)   # t = 3n/4: claim 'independent of t' tested
        say(f"T3/4  n={r['n']:2d} a={r['a']:2d} t={r['t']:2d} clamps={r['clamps']:5d} members={r['members']:8d} "
            f"bad={r['bad']} steps/member={r['steps_per_member']:.2f} (formula 2^(n-min(a1+a2,a3+a4)) = 1) {r['steps']}")
    out.close()
