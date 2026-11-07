"""b3-r1c scout: which E-input words can be prescribed for free (zero scan)?

A set H of E-input words is "free-holdable" if some 9-word basis B containing H has
closure(B) = every word with 0 checks (each word assigned once, no guessing).
Search: B = H + T with T drawn from the front-line basis B0 (all subsets), then with one
or two members of T replaced by any other word.  A miss is not a proof of impossibility
(except where gd2.py ran exhaustively).
"""
import itertools, sys, time
from gd import VARS, NV, CONST, E1IN, E3IN, mask
from gd2 import close, FULL

B0 = ["C0.d1", "D2.a1", "D2.b1", "S11", "S4", "X9", "w6", "Y4", "w0"]
EW = ["Y4", "Y9", "Y14", "w8", "Y1", "Y6", "Y12", "w12", "w5"]
K0 = mask(CONST)
k0c, u0c, c0c = close(K0, 0, [v for v in range(NV) if K0 >> v & 1])


def is_basis(names):
    vs = [VARS.index(n) for n in names]
    k, u, c = close(k0c, u0c, [])
    known = k
    for v in vs:
        if known >> v & 1:
            return False
        known, u, ch = close(known | (1 << v), u, [v])
        if ch:
            return False
    return known == FULL


def holdable(H, depth=2):
    need = 9 - len(H)
    pool = [b for b in B0 if b not in H]
    others = [v for v in VARS if not (K0 >> VARS.index(v) & 1) and v not in H]
    for T in itertools.combinations(pool, need):
        if is_basis(list(H) + list(T)):
            return list(H) + list(T)
    if depth >= 1:
        for T in itertools.combinations(pool, need - 1):
            for o in others:
                if o in T:
                    continue
                if is_basis(list(H) + list(T) + [o]):
                    return list(H) + list(T) + [o]
    if depth >= 2:
        for T in itertools.combinations(pool, need - 2):
            for o1, o2 in itertools.combinations(others, 2):
                if o1 in T or o2 in T:
                    continue
                if is_basis(list(H) + list(T) + [o1, o2]):
                    return list(H) + list(T) + [o1, o2]
    return None


if __name__ == "__main__":
    print("front-line basis B0 is a basis:", is_basis(B0))
    t0 = time.time()
    results = {}
    maxsize = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for r in range(1, maxsize + 1):
        for H in itertools.combinations(EW, r):
            # only sets containing Y4 and Y14 are front-line-compatible (member + trial); test all
            b = holdable(H, depth=1 if r < 3 else 1)
            results[H] = b
            print("%-28s %s" % (",".join(H), ("FREE  basis=" + ",".join(b)) if b else "not found (depth 1)"))
            sys.stdout.flush()
    print("time %.1fs" % (time.time() - t0))
