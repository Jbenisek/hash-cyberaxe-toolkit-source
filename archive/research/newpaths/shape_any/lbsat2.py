"""Lower bound on the free width of ANY binary join tree when promoted constants may be chosen freely, limited by
the slack they consume (shape_any agent).

slack(P) = F - F'(P) = |P| - E + maxmatch(equations, words \\ P)   (generic dimension lost by fixing P)
slack(P) <= S  <=>  there is a vertex cover (Konig) C_E + C_V of the bipartite graph eq--(word not in P) with
                   |P| + |C_E| + |C_V| <= S + E.
Cut part as in lbsat.py: A (k <= |A| < 2k), Y >= B(A) minus P, cost |Y \\ P| - #{e in A : vars(e) <= Y u P} <= T.
(Equations lying inside P are counted as conditions: this can only lower the cost, so UNSAT stays a valid bound.)
Usage: python lbsat2.py <sys> <k> <T> <S> <out.cnf>
"""
import sys


def main():
    fn, k, T, S, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
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
    p = [new() for _ in range(N)]
    q = [new() for _ in range(N)]
    ce = [new() for _ in range(E)]
    cv = [new() for _ in range(N)]
    for e, vs in enumerate(eqs):
        cl.append([-c[e], x[e]])
        for v in vs:
            cl.append([-c[e], y[v], p[v]])
            cl.append([p[v], ce[e], cv[v]])          # cover of edge (e, v) unless v promoted
    for v in range(N):
        for e in occ[v]:
            for f in occ[v]:
                if e != f:
                    cl.append([-x[e], x[f], y[v], p[v]])
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

    atmost(q + [-ci for ci in c], T + E)
    atmost([-xi for xi in x], E - k)
    atmost(x, min(2 * k - 1, E - 1))
    atmost(p + ce + cv, S + E)
    with open(out, "w") as fh:
        fh.write(f"p cnf {nv[0]} {len(cl)}\n")
        for cc in cl:
            fh.write(" ".join(map(str, cc)) + " 0\n")
    print(out, nv[0], len(cl))


if __name__ == "__main__":
    main()
