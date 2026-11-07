"""Exact lower bound on the free width of ANY binary join tree, by SAT (shape_any agent).

Fact (DERIVED): in a rooted binary tree with E equation leaves, for every 2 <= k <= E/2 some internal node t has
k <= |A_t| < 2k (walk the heavy path); its list pi_{B(A_t)} Sol(A_t) must be built, so
    width >= LB(k) = min_{k <= |A| < 2k} rho(A, B(A)),  rho(A, Z) = min_{Z <= Y} |Y| - e_A(Y).
With P promoted words (any choice, dependent or not) the bound uses cost |Y \\ P| (a valid lower bound).
Query: is there A, Y (and P) with cost <= T?  UNSAT -> LB(k) > T.
Usage: python lbsat.py <sys> <k> <T> <P> <out.cnf>
"""
import sys


def main():
    fn, k, T, P, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    lines = open(fn).read().split("\n")
    N, E, F = map(int, lines[0].split())
    eqs = []
    for ln in lines[1 + N:1 + N + E]:
        p = ln.split()
        eqs.append([int(t) for t in p[2:2 + int(p[1])]])
    occ = [[] for _ in range(N)]
    for e, vs in enumerate(eqs):
        for v in vs:
            occ[v].append(e)
    nv = [0]
    cl = []

    def new():
        nv[0] += 1
        return nv[0]

    x = [new() for _ in range(E)]
    y = [new() for _ in range(N)]
    c = [new() for _ in range(E)]
    p = [new() for _ in range(N)] if P > 0 else None
    q = [new() for _ in range(N)] if P > 0 else y
    for e, vs in enumerate(eqs):
        cl.append([-c[e], x[e]])
        for v in vs:
            cl.append([-c[e], y[v]] + ([p[v]] if p else []))
    for v in range(N):
        for e in occ[v]:
            for f in occ[v]:
                if e != f:
                    cl.append([-x[e], x[f], y[v]] + ([p[v]] if p else []))
        if p:
            cl.append([q[v], -y[v], p[v]])

    def atmost(lits, K):
        n = len(lits)
        if K >= n:
            return
        if K <= 0:
            for l in lits:
                cl.append([-l])
            return
        s = [[new() for _ in range(K)] for _ in range(n)]
        cl.append([-lits[0], s[0][0]])
        for j in range(1, K):
            cl.append([-s[0][j]])
        for i in range(1, n):
            cl.append([-lits[i], s[i][0]])
            cl.append([-s[i - 1][0], s[i][0]])
            for j in range(1, K):
                cl.append([-lits[i], -s[i - 1][j - 1], s[i][j]])
                cl.append([-s[i - 1][j], s[i][j]])
            cl.append([-lits[i], -s[i - 1][K - 1]])

    atmost(q + [-ci for ci in c], T + E)          # sum q - sum c <= T
    atmost([-xi for xi in x], E - k)              # |A| >= k
    atmost(x, min(2 * k - 1, E - 1))              # |A| < 2k and A != all
    if p:
        atmost(p, P)
    with open(out, "w") as fh:
        fh.write(f"p cnf {nv[0]} {len(cl)}\n")
        for cc in cl:
            fh.write(" ".join(map(str, cc)) + " 0\n")
    print(out, nv[0], len(cl))


if __name__ == "__main__":
    main()
