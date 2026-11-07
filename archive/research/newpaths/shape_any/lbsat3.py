"""Lower bound on the free width of ANY binary join tree (DP over any shape), with promoted constants chosen
freely up to a slack budget S (shape_any agent).  Refines lbsat2.py: the size window counts only equations that
still contain an unknown word after promotion (r_e), as in the propagated sub-family system.

  slack(P) = |P| - E + maxmatch(eq, words \\ P) <= S   <=> vertex cover C with |P| + |C| <= S + E   (Konig)
  window   : k <= #{e in A : r_e} < 2k,   r_e = OR_{v in e} not p_v
  cost     : |Y \\ P| - #{e in A : vars(e) <= Y u P} <= T,  Y >= B(A) \\ P
UNSAT => for every promotion set with slack <= S and every tree on the remaining equations having a node in the
window (true when the remaining system has >= 2k equations; checked by mode 'drop'), width > T.

Usage: python lbsat3.py cut  <sys> <k> <T> <S> <out.cnf>
       python lbsat3.py drop <sys> <D> <S> <out.cnf>      (SAT iff slack <= S can remove >= D equations)
"""
import sys


def load(fn):
    lines = open(fn).read().split("\n")
    N, E, F = map(int, lines[0].split())
    eqs = []
    for ln in lines[1 + N:1 + N + E]:
        p = ln.split()
        eqs.append([int(t) for t in p[2:2 + int(p[1])]])
    return N, E, eqs


class CNF:
    def __init__(self):
        self.nv = 0
        self.cl = []

    def new(self):
        self.nv += 1
        return self.nv

    def atmost(self, lits, K):
        n = len(lits)
        if K >= n:
            return
        if K <= 0:
            for l in lits:
                self.cl.append([-l])
            return
        s = [[self.new() for _ in range(K)] for _ in range(n)]
        cl = self.cl
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

    def write(self, out):
        with open(out, "w") as fh:
            fh.write(f"p cnf {self.nv} {len(self.cl)}\n")
            for cc in self.cl:
                fh.write(" ".join(map(str, cc)) + " 0\n")
        print(out, self.nv, len(self.cl))


def promo_part(f, N, E, eqs, S):
    p = [f.new() for _ in range(N)]
    ce = [f.new() for _ in range(E)]
    cv = [f.new() for _ in range(N)]
    r = [f.new() for _ in range(E)]
    for e, vs in enumerate(eqs):
        for v in vs:
            f.cl.append([p[v], ce[e], cv[v]])
            f.cl.append([r[e], p[v]])                 # some var unpromoted -> r_e
        f.cl.append([-r[e]] + [-p[v] for v in vs])   # r_e -> some var unpromoted
    f.atmost(p + ce + cv, S + E)
    return p, r


def main():
    mode = sys.argv[1]
    if mode == "drop":
        fn, D, S, out = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
        letters = sys.argv[6] if len(sys.argv) > 6 else None
        N, E, eqs = load(fn)
        names = open(fn).read().split("\n")[1 + N:1 + N + E]
        wt = [1 if letters is None or ln.split()[0][0] in letters else 0 for ln in names]
        f = CNF()
        p, r = promo_part(f, N, E, eqs, S)
        rw = [r[e] for e in range(E) if wt[e]]
        f.atmost(rw, len(rw) - D)                     # at least D (weighted) equations removed
        f.write(out)
        return
    fn, k, T, S, out = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    letters = sys.argv[7] if len(sys.argv) > 7 else None     # window counts only equations of these G calls
    N, E, eqs = load(fn)
    names = open(fn).read().split("\n")[1 + N:1 + N + E]
    wt = [1 if letters is None or ln.split()[0][0] in letters else 0 for ln in names]
    occ = [[] for _ in range(N)]
    for e, vs in enumerate(eqs):
        for v in vs:
            occ[v].append(e)
    f = CNF()
    x = [f.new() for _ in range(E)]
    y = [f.new() for _ in range(N)]
    c = [f.new() for _ in range(E)]
    q = [f.new() for _ in range(N)]
    z = [f.new() for _ in range(E)]
    p, r = promo_part(f, N, E, eqs, S)
    for e, vs in enumerate(eqs):
        f.cl.append([-c[e], x[e]])
        f.cl.append([-c[e], r[e]])                  # equations made fully constant are not conditions
        for v in vs:
            f.cl.append([-c[e], y[v], p[v]])
        f.cl.append([-z[e], x[e]]); f.cl.append([-z[e], r[e]]); f.cl.append([z[e], -x[e], -r[e]])
    for v in range(N):
        for e in occ[v]:
            for g in occ[v]:
                if e != g:
                    f.cl.append([-x[e], x[g], y[v], p[v]])
        f.cl.append([q[v], -y[v], p[v]])
    f.atmost(q + [-ci for ci in c], T + E)
    zw = [z[e] for e in range(E) if wt[e]]
    f.atmost([-zi for zi in zw], len(zw) - k)
    f.atmost(zw, 2 * k - 1)
    f.write(out)


if __name__ == "__main__":
    main()
