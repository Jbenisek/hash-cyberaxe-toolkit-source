"""rho(A, B(A)) of hand-picked cuts (unions of G calls) in a system file; also the best union of whole G calls
in the window [R/3, 2R/3) by exhaustive enumeration (an UPPER bound on the window minimum).  shape_any agent.
Usage: python cuts.py <sys>
"""
import itertools
import sys


def load(fn):
    lines = open(fn).read().split("\n")
    N, E, F = map(int, lines[0].split())
    names = lines[1:1 + N]
    en, eqs = [], []
    for ln in lines[1 + N:1 + N + E]:
        p = ln.split()
        en.append(p[0]); eqs.append([int(t) for t in p[2:2 + int(p[1])]])
    return N, E, F, names, en, eqs


def rho(A, eqs, E):
    Aset = set(A)
    WA = {v for e in A for v in eqs[e]}
    Wout = {v for e in range(E) if e not in Aset for v in eqs[e]}
    B = WA & Wout
    avail = WA - B
    mv = {}

    def aug(e, seen):
        for v in eqs[e]:
            if v in avail and v not in seen:
                seen.add(v)
                if v not in mv or aug(mv[v], seen):
                    mv[v] = e
                    return True
        return False
    m = sum(1 for e in A if aug(e, set()))
    return len(B) - (len(A) - m), len(B)


def main():
    N, E, F, names, en, eqs = load(sys.argv[1])
    calls = {}
    for e, n in enumerate(en):
        calls.setdefault(n.split(":")[0], []).append(e)
    cl = sorted(calls)
    print(f"{sys.argv[1]}: N={N} E={E} F={F}; calls: " + " ".join(f"{c}:{len(calls[c])}" for c in cl))
    lo, hi = E / 3, 2 * E / 3
    best = []
    for r in range(1, len(cl)):
        for S in itertools.combinations(cl, r):
            A = [e for c in S for e in calls[c]]
            if lo <= len(A) < hi:
                rr, b = rho(A, eqs, E)
                best.append((rr, b, S))
    best.sort()
    print(f"unions of whole G calls in window [{lo:.1f},{hi:.1f}): {len(best)} sets; smallest rho:")
    for rr, b, S in best[:8]:
        print(f"  rho={rr} |B|={b}  {' '.join(S)}")


if __name__ == "__main__":
    main()
