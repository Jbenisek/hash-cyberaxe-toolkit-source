"""Independent check of a SAT witness from lbsat4.py/lbsat5.py (promotion encodings).
Decodes A (x) and P (p), propagates constants, and recomputes slack, the remaining system, |A n remaining|,
the boundary and rho(A, B(A)) by bipartite matching.  Usage: python checkwit.py <sys> <kissat.out>
"""
import sys


def matching(eqs_idx, eqs, avail):
    mv = {}

    def aug(e, seen):
        for v in eqs[e]:
            if v in avail and v not in seen:
                seen.add(v)
                if v not in mv or aug(mv[v], seen):
                    mv[v] = e
                    return True
        return False
    return sum(1 for e in eqs_idx if aug(e, set()))


def main():
    fn, out = sys.argv[1], sys.argv[2]
    lines = open(fn).read().split("\n")
    N, E, F = map(int, lines[0].split())
    names = lines[1:1 + N]
    enames, eqs = [], []
    for ln in lines[1 + N:1 + N + E]:
        p = ln.split()
        enames.append(p[0])
        eqs.append([int(t) for t in p[2:2 + int(p[1])]])
    true = set()
    for ln in open(out):
        if ln.startswith("v "):
            true.update(int(t) for t in ln[2:].split() if int(t) > 0)
    x = [e for e in range(E) if (e + 1) in true]
    poff = 3 * E + 2 * N
    P = {v for v in range(N) if (poff + v + 1) in true}
    # propagate
    C = set(P)
    alive = [True] * E
    ch = True
    while ch:
        ch = False
        for e in range(E):
            if alive[e]:
                unk = [v for v in eqs[e] if v not in C]
                if len(unk) == 0:
                    alive[e] = False; ch = True
                elif len(unk) == 1:
                    C.add(unk[0]); alive[e] = False; ch = True
    rem = [e for e in range(E) if alive[e]]
    req = {e: [v for v in eqs[e] if v not in C] for e in rem}
    Vrem = set(range(N)) - C
    Fp = len(Vrem) - len(rem)
    mm = matching(rem, req, Vrem)
    slack = F - (len(Vrem) - mm)
    A = [e for e in x if alive[e]]
    Aset = set(A)
    WA = {v for e in A for v in req[e]}
    Wout = {v for e in rem if e not in Aset for v in req[e]}
    B = WA & Wout
    unm = len(A) - matching(A, req, WA - B)
    rho = len(B) - unm
    calls = {}
    for e in A:
        c = enames[e].split(":")[0]
        calls[c] = calls.get(c, 0) + 1
    print(f"promoted |P|={len(P)} derived={len(C) - len(P)} slack={slack} remaining eqs={len(rem)} F'={Fp} "
          f"(remaining system {'consistent' if mm == len(rem) else 'OVER-DETERMINED'})")
    print(f"|A n remaining|={len(A)} window [R/3,2R/3)=[{len(rem) / 3:.1f},{2 * len(rem) / 3:.1f}) |B|={len(B)} rho={rho}")
    print("A calls:", " ".join(f"{c}:{n}" for c, n in sorted(calls.items())))
    print("P:", ",".join(names[v] for v in sorted(P)))
    print("B:", ",".join(names[v] for v in sorted(B)))


if __name__ == "__main__":
    main()
