"""For one minimal guess set: best bipartition (largest cl(A) | cl(B)), the jointly derived words and which
G calls they belong to.  Usage: python explain.py <fixed|outhalf> <plain|tables> w1 .. wg"""
import itertools, sys
from kmodel import Sys
S = Sys(sys.argv[1], sys.argv[2])
G = [S.idx[w] for w in sys.argv[3:]]
pc = lambda x: bin(x).count("1")
best = None
for r in range(1, len(G) // 2 + 1):
    for A in itertools.combinations(G, r):
        B = [w for w in G if w not in A]
        KA = S.closure(sum(1 << w for w in A)); KB = S.closure(sum(1 << w for w in B))
        U = KA | KB
        key = (pc(U), -abs(len(A) - len(B)))
        if best is None or key > best[0]:
            best = (key, A, B, KA, KB, U)
_, A, B, KA, KB, U = best
d = lambda X: pc(X) - S.ein(X)
print("set:", " ".join(sys.argv[3:]))
print("best split A:", [S.names[w] for w in A], "B:", [S.names[w] for w in B])
print(f"|cl(A)|={pc(KA)} delta={d(KA)}  |cl(B)|={pc(KB)} delta={d(KB)}  |union|={pc(U)} delta={d(U)}  -> post={d(U) - S.F}")
out = S.nm(S.ALL & ~U)
calls = {}
for w in out:
    calls.setdefault(w.split(".")[0] if "." in w else "msg", []).append(w)
print("jointly derived words by call:", {k: len(v) for k, v in sorted(calls.items())})
ceq = [n for n, m, _ in S.eqs if n[0] == "C" and not (m & ~U)]
print("C-call equations inside the union:", len(ceq), "of 32:", ceq)
