"""kverify_0: outhalf variant, small independent sample.  For valid 16-guess sets (4 checks): every bipartition,
and random 4-block partitions: max separable conditions n_sep = sum delta(K_i) - delta(union K_i).
Usage: python kv_outhalf.py nsets n4 seed
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
import random
import itertools
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
from gd_order import build

eqs, const, vars_ = build("outhalf", "len64")
W = set(vars_)
EQ = [tuple(v for v in vs if v not in const) for _, vs in eqs]
occ = {v: [] for v in W}
for i, vs in enumerate(EQ):
    for v in vs:
        occ[v].append(i)
F = len(W) - len(EQ)
cache = {}


def closure(T):
    key = frozenset(T)
    if key in cache:
        return cache[key]
    K = set(T)
    stack = list(T)
    while stack:
        w = stack.pop()
        for i in occ[w]:
            unk = [u for u in EQ[i] if u not in K]
            if len(unk) == 1:
                K.add(unk[0])
                stack.append(unk[0])
    cache[key] = frozenset(K)
    return cache[key]


def delta(X):
    return len(X) - sum(1 for vs in EQ if all(v in X for v in vs))


def main():
    nsets, n4, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(seed)
    g0 = "K0.a1 K2.a1 K2.b2 K3.a1 K3.b2 K0.b2 D2.c1 D2.c2 D2.a1 K1.d1 D3.c1 D0.d1 D1.a1 D0.c2 D1.a2 C1.b1".split()
    print(f"outhalf: {len(W)} words, {len(EQ)} eqs, F={F}; greedy set full closure:", len(closure(g0)) == len(W))
    words = sorted(W)
    cur, done, seen = list(g0), 0, set()
    while done < nsets:
        g = list(cur)
        g[rng.randrange(16)] = rng.choice(words)
        if len(set(g)) != 16 or len(closure(g)) != len(W):
            continue
        cur = g
        if frozenset(g) in seen:
            continue
        seen.add(frozenset(g))
        cache.clear()
        mx2 = 0
        first, rest = g[0], g[1:]
        for r in range(0, 15):
            for S in itertools.combinations(rest, r):
                A = [first] + list(S)
                B = [w for w in g if w not in A]
                KA, KB = closure(A), closure(B)
                mx2 = max(mx2, delta(KA) + delta(KB) - delta(KA | KB))
        mx4 = 0
        for _ in range(n4):
            lab = [rng.randrange(4) for _ in g]
            blocks = [[w for w, l in zip(g, lab) if l == j] for j in range(4)]
            if any(not b for b in blocks):
                continue
            Ks = [closure(b) for b in blocks]
            U = frozenset().union(*Ks)
            mx4 = max(mx4, sum(delta(K) for K in Ks) - delta(U))
        done += 1
        print(f"COMPUTED set {done}: max n_sep over all 32767 bipartitions = {mx2}; over {n4} random 4-block = {mx4}",
              flush=True)


if __name__ == "__main__":
    main()
