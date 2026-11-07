"""Same lower-bound query as lbsat3.py, encoded with totalizers (unary counters) instead of sequential counters.
cost: sum q_v <= T + sum c_e is encoded as  Q >= T + j + 1  ->  C >= j + 1  between two unary counters.
Usage: python lbsat4.py cut  <sys> <k> <T> <S> <out.cnf> [letters]
       python lbsat4.py drop <sys> <D> <S> <out.cnf> [letters]
"""
import sys


def load(fn):
    lines = open(fn).read().split("\n")
    N, E, F = map(int, lines[0].split())
    eqs, names = [], []
    for ln in lines[1 + N:1 + N + E]:
        p = ln.split()
        names.append(p[0])
        eqs.append([int(t) for t in p[2:2 + int(p[1])]])
    return N, E, eqs, names


class CNF:
    def __init__(self):
        self.nv = 0
        self.cl = []

    def new(self):
        self.nv += 1
        return self.nv

    def tot(self, lits, up=True, down=True):
        """unary counter: returns o[1..n] (o[i] <-> at least i of lits), as list with o[0] unused."""
        if len(lits) == 1:
            return [None, lits[0]]
        h = len(lits) // 2
        a = self.tot(lits[:h], up, down)
        b = self.tot(lits[h:], up, down)
        p, q = len(a) - 1, len(b) - 1
        o = [None] + [self.new() for _ in range(p + q)]
        for i in range(p + 1):
            for j in range(q + 1):
                if up and i + j >= 1:
                    c = [o[i + j]]
                    if i:
                        c.append(-a[i])
                    if j:
                        c.append(-b[j])
                    self.cl.append(c)
                if down and i + j + 1 <= p + q:
                    c = [-o[i + j + 1]]
                    if i + 1 <= p:
                        c.append(a[i + 1])
                    if j + 1 <= q:
                        c.append(b[j + 1])
                    self.cl.append(c)
        return o

    def atmost(self, lits, K):
        if K >= len(lits):
            return
        if K < 0:
            self.cl.append([])
            return
        o = self.tot(lits, up=True, down=False)
        self.cl.append([-o[K + 1]])

    def atleast(self, lits, K):
        if K <= 0:
            return
        if K > len(lits):
            self.cl.append([])
            return
        o = self.tot(lits, up=False, down=True)
        self.cl.append([o[K]])

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
            f.cl.append([r[e], p[v]])
        f.cl.append([-r[e]] + [-p[v] for v in vs])
    f.atmost(p + ce + cv, S + E)
    return p, r


def main():
    mode = sys.argv[1]
    if mode == "drop":
        fn, D, S, out = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
        letters = sys.argv[6] if len(sys.argv) > 6 else None
        N, E, eqs, names = load(fn)
        wt = [1 if letters is None or nm[0] in letters else 0 for nm in names]
        f = CNF()
        p, r = promo_part(f, N, E, eqs, S)
        rw = [r[e] for e in range(E) if wt[e]]
        f.atmost(rw, len(rw) - D)
        f.write(out)
        return
    fn, k, T, S, out = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    letters = sys.argv[7] if len(sys.argv) > 7 else None
    N, E, eqs, names = load(fn)
    wt = [1 if letters is None or nm[0] in letters else 0 for nm in names]
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
    if S > 0:
        p, r = promo_part(f, N, E, eqs, S)
    else:
        p, r = None, None
    for e, vs in enumerate(eqs):
        f.cl.append([-c[e], x[e]])
        if r:
            f.cl.append([-c[e], r[e]])
        for v in vs:
            f.cl.append([-c[e], y[v]] + ([p[v]] if p else []))
        if r:
            f.cl.append([-z[e], x[e]]); f.cl.append([-z[e], r[e]]); f.cl.append([z[e], -x[e], -r[e]])
        else:
            f.cl.append([-z[e], x[e]]); f.cl.append([z[e], -x[e]])
    for v in range(N):
        for e in occ[v]:
            for g in occ[v]:
                if e != g:
                    f.cl.append([-x[e], x[g], y[v]] + ([p[v]] if p else []))
        f.cl.append([q[v], -y[v]] + ([p[v]] if p else []))
    # cost: Q <= T + C
    oq = f.tot(q, up=True, down=False)
    oc = f.tot(c, up=False, down=True)
    nq, nc = len(q), len(c)
    for j in range(0, nq - T):
        i = T + j + 1
        if i > nq:
            break
        if j + 1 <= nc:
            f.cl.append([-oq[i], oc[j + 1]])
        else:
            f.cl.append([-oq[i]])
    zw = [z[e] for e in range(E) if wt[e]]
    f.atleast(zw, k)
    f.atmost(zw, 2 * k - 1)
    f.write(out)


if __name__ == "__main__":
    main()
