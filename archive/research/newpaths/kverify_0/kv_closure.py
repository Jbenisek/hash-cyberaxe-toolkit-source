"""kverify_0: independent recomputation of side closures and check separability from gd_order.build().
Read-only import of gd_order (no bytecode written outside this folder).
Usage: python kv_closure.py [nsamples]
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
import random
import itertools
from gd_order import build, run

eqs, const, vars_ = build("fixed", "len64")
W = set(vars_)
EQ = [(n, tuple(v for v in vs if v not in const)) for n, vs in eqs]
GT = {n: ("add" if n.split(":")[-1] in ("a1", "c1", "a2", "c2") else "xor") for n, _ in EQ}
occ = {v: [] for v in W}
for i, (_, vs) in enumerate(EQ):
    for v in vs:
        occ[v].append(i)
F = len(W) - len(EQ)


def closure(T):
    K = set(T)
    stack = list(T)
    while stack:
        w = stack.pop()
        for i in occ[w]:
            unk = [u for u in EQ[i][1] if u not in K]
            if len(unk) == 1:
                K.add(unk[0])
                stack.append(unk[0])
    return frozenset(K)


def ein(X):
    return sum(1 for _, vs in EQ if all(v in X for v in vs))


def delta(X):
    return len(X) - ein(X)


def lin_sep(sides):
    """separable checks after joining side closures, with linear post-derivation (same group chain)."""
    U = set().union(*sides)
    lin = {}            # word -> group type
    used = set()
    changed = True
    while changed:
        changed = False
        for i, (n, vs) in enumerate(EQ):
            if i in used:
                continue
            t = GT[n]
            out = [v for v in vs if v not in U and v not in lin]
            ok = all((v in U) or (lin.get(v) == t) for v in vs if v not in out)
            if len(out) == 1 and ok:
                lin[out[0]] = t
                used.add(i)
                changed = True
    extra = 0
    for i, (n, vs) in enumerate(EQ):
        if i in used:
            continue
        if any(v in lin for v in vs) and all((v in U) or (lin.get(v) == GT[n]) for v in vs):
            extra += 1
    return extra


def set_partitions(items, k):
    items = list(items)
    if k == 1:
        yield [items]
        return
    if len(items) < k:
        return
    first, rest = items[0], items[1:]
    for p in set_partitions(rest, k - 1):
        yield [[first]] + p
    for p in set_partitions(rest, k):
        for j in range(len(p)):
            yield p[:j] + [[first] + p[j]] + p[j + 1:]


def analyse(G, do_lin=True):
    G = list(G)
    cl = {}
    for r in range(1, len(G) + 1):
        for S in itertools.combinations(G, r):
            cl[frozenset(S)] = closure(S)
    full = cl[frozenset(G)]
    res = {"full": len(full) == len(W)}
    # proper subsets carrying an internal condition
    res["sub_cond"] = sum(1 for S, K in cl.items() if len(S) < len(G) and delta(K) < len(S))
    best = {}
    for k in (2, 3, 4):
        mx, mxl = 0, 0
        for P in set_partitions(G, k):
            Ks = [cl[frozenset(b)] for b in P]
            U = frozenset().union(*Ks)
            nsep = sum(delta(K) for K in Ks) - delta(U)
            mx = max(mx, nsep)
            if do_lin:
                mxl = max(mxl, nsep + lin_sep(Ks))
        best[k] = (mx, mxl)
    res["best"] = best
    return res


def main():
    nsamp = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    print(f"fixed len64: {len(W)} unknown words, {len(EQ)} equations, freedom F={F}")
    print("COMPUTED R1 check: max closure 1 guess =", max(len(closure([v])) for v in W),
          " 2 guesses =", max(len(closure([a, b])) for a, b in itertools.combinations(sorted(W), 2)))
    # peeling core
    rem_w, rem_e = set(W), set(range(len(EQ)))
    peeled = []
    while True:
        cnt = {v: [i for i in occ[v] if i in rem_e] for v in rem_w}
        p = [v for v in sorted(rem_w) if len(cnt[v]) == 1]
        if not p:
            break
        v = p[0]
        rem_w.discard(v)
        rem_e.discard(cnt[v][0])
        peeled.append(v)
    print("COMPUTED peeling core:", len(rem_w), "words; peeled", peeled)
    greedy = ["K2.c1", "K3.d1", "K3.d2", "C3.a2", "m0", "D1.d1", "K2.d2", "C0.a1"]
    r = analyse(greedy)
    print("COMPUTED greedy set", greedy, r)
    # positive controls: the detector must see separable conditions where they exist
    A, B = closure(["m0"]), closure(["K0.d1"])
    print("CONTROL m0 | K0.d1: |A|,|B| =", len(A), len(B), " n_sep =", delta(A) + delta(B) - delta(A | B))
    extra = [w for w in sorted(W) if w not in greedy][0]
    A, B = closure(greedy), closure([extra])
    print("CONTROL greedy |", extra, ": n_sep =", delta(A) + delta(B) - delta(A | B))
    A, B = closure(["m0", "K3.d1"]), closure(["K0.c2", "K3.d2"])
    print("CONTROL m0,K3.d1 | K0.c2,K3.d2: n_sep =", delta(A) + delta(B) - delta(A | B), " lin extra =", lin_sep([A, B]))
    if len(sys.argv) > 3:
        return
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
    seen = set()
    stats = {"sets": 0, "sub_cond": 0, "nonfull": 0}
    hist = {k: {} for k in (2, 3, 4)}
    tries = 0
    cur = list(greedy)
    words = sorted(W)
    while len(seen) < nsamp and tries < 2000 * nsamp:
        tries += 1
        # random walk over valid 8-sets: swap one guess for another word, keep if closure is still everything
        g = list(cur)
        g[rng.randrange(8)] = rng.choice(words)
        if len(set(g)) != 8 or len(closure(g)) != len(W):
            continue
        cur = g
        key = frozenset(g)
        if key in seen:
            continue
        seen.add(key)
        r = analyse(g)
        stats["sets"] += 1
        stats["sub_cond"] += r["sub_cond"] > 0
        stats["nonfull"] += not r["full"]
        for k, v in r["best"].items():
            hist[k][v] = hist[k].get(v, 0) + 1
    print("COMPUTED random greedy 8-sets:", stats, "tries", tries)
    for k in (2, 3, 4):
        print(f"  k={k}: histogram of (max n_sep, max n_sep with LIN) over all partitions into {k} blocks:",
              dict(sorted(hist[k].items())))


if __name__ == "__main__":
    main()
