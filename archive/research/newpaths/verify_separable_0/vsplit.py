"""verify_separable_0: independent recount of join keys for full-closure 8-sets (fixed variant, plain model).
For every assignment of the 8 guesses to core C / side A / side B (3^8, A and B non-empty):
  X1 = cl(C+A), X2 = cl(C+B), delta(X) = |X| - #equations inside X,
  kX = delta(X1) + delta(X2) - |C| - delta(X1 u X2), iA = |C+A| - delta(X1), p = delta(X1 u X2) - F.
Reports the max kX per set and a histogram.  Usage: python vsplit.py <sysfile> <setfile> <maxsets> [seed]
"""
import itertools
import random
import sys


def load(fn):
    L = open(fn).read().split("\n")
    N, E = map(int, L[0].split()[:2])
    names = L[1:1 + N]
    eqs = []
    for line in L[1 + N:1 + N + E]:
        p = line.split()
        eqs.append([int(x) for x in p[2:]])
    return N, names, eqs


def main():
    sysf, setf, maxsets = sys.argv[1], sys.argv[2], int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    N, names, eqs = load(sysf)
    F = N - len(eqs)
    emask = [sum(1 << i for i in e) for e in eqs]
    occ = [[] for _ in range(N)]
    for k, e in enumerate(eqs):
        for i in e:
            occ[i].append(k)
    ALL = (1 << N) - 1

    def cl(seed_mask):
        K = seed_mask
        stack = [i for i in range(N) if seed_mask >> i & 1]
        while stack:
            v = stack.pop()
            for k in occ[v]:
                u = emask[k] & ~K
                if u and not (u & (u - 1)):
                    K |= u
                    stack.append(u.bit_length() - 1)
        return K

    def delta(X):
        return bin(X).count("1") - sum(1 for m in emask if m & ~X == 0)

    sets = []
    for line in open(setf):
        if line.startswith("FULL"):
            sets.append([int(x) for x in line.split(":")[1].split()])
        elif line.strip():
            sets.append([int(x) for x in line.split()])
    rng = random.Random(seed)
    if len(sets) > maxsets:
        sets = rng.sample(sets, maxsets)
    hist = {}
    nfull = 0
    best_overall = None
    for S in sets:
        Sm = sum(1 << i for i in S)
        assert cl(Sm) == ALL, ("not full", S)
        nfull += 1
        best = (-99,)
        for assign in itertools.product((0, 1, 2), repeat=len(S)):
            C = sum(1 << S[i] for i in range(len(S)) if assign[i] == 0)
            A = sum(1 << S[i] for i in range(len(S)) if assign[i] == 1)
            B = sum(1 << S[i] for i in range(len(S)) if assign[i] == 2)
            if not A or not B:
                continue
            X1, X2 = cl(C | A), cl(C | B)
            nC = bin(C).count("1")
            d1, d2, d12 = delta(X1), delta(X2), delta(X1 | X2)
            kX = d1 + d2 - nC - d12
            if kX > best[0]:
                best = (kX, nC, bin(A).count("1"), bin(B).count("1"), d12 - F, [names[i] for i in S], assign)
        hist[best[0]] = hist.get(best[0], 0) + 1
        if best_overall is None or best[0] > best_overall[0]:
            best_overall = best
    print(f"COMPUTED {setf}: {nfull} sets checked (all have full closure); histogram of max kX over all C/A/B splits:",
          dict(sorted(hist.items())))
    print("best split seen:", best_overall)


if __name__ == "__main__":
    main()
