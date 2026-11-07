"""Balanced-region lower bound for join trees (ksplit).

Question: is there a set V of words with lo <= |V| <= hi and delta(V) = |V| - Ein(V) <= D ?
(Ein(V) = equations whose unknown words all lie in V.)  Writes DIMACS; e_e -> v_w for w in e (sound: an
equation may only be counted when all its words are in V).
Usage: python regsat.py <sysfile> <lo> <hi> <D> <out.cnf>
       python regsat.py --decode <sysfile> <out.cnf> <solver output>
"""
import sys


def load(fn):
    with open(fn) as f:
        tok = f.read().split()
    N, E, NM, F = map(int, tok[:4])
    p = 4
    names = tok[p:p + N]
    p += N
    eqs = []
    for _ in range(E):
        nm, k = tok[p], int(tok[p + 1])
        ws = list(map(int, tok[p + 2:p + 2 + k]))
        p += 2 + k
        eqs.append((nm, ws))
    return N, E, F, names, eqs


class CNF:
    def __init__(self):
        self.n = 0
        self.cl = []

    def new(self):
        self.n += 1
        return self.n

    def atmost(self, lits, k):
        """sequential counter: at most k of lits true"""
        n = len(lits)
        if k >= n:
            return
        if k == 0:
            for x in lits:
                self.cl.append([-x])
            return
        S = [[self.new() for _ in range(k)] for _ in range(n)]
        self.cl.append([-lits[0], S[0][0]])
        for j in range(1, k):
            self.cl.append([-S[0][j]])
        for i in range(1, n):
            self.cl.append([-lits[i], S[i][0]])
            self.cl.append([-S[i - 1][0], S[i][0]])
            for j in range(1, k):
                self.cl.append([-lits[i], -S[i - 1][j - 1], S[i][j]])
                self.cl.append([-S[i - 1][j], S[i][j]])
            self.cl.append([-lits[i], -S[i - 1][k - 1]])

    def atleast(self, lits, k):
        self.atmost([-x for x in lits], len(lits) - k)


def encode(fn, lo, hi, D):
    N, E, F, names, eqs = load(fn)
    c = CNF()
    v = [c.new() for _ in range(N)]
    e = [c.new() for _ in range(E)]
    for j, (_, ws) in enumerate(eqs):
        for w in ws:
            c.cl.append([-e[j], v[w]])
    # delta(V) <= D  <=>  sum v + sum(not e) <= D + E
    c.atmost(v + [-x for x in e], D + E)
    c.atleast(v, lo)
    c.atmost(v, hi)
    return c, v, e, names, eqs


def main():
    if sys.argv[1] == "--decode":
        fn, cnf, out = sys.argv[2], sys.argv[3], sys.argv[4]
        N, E, F, names, eqs = load(fn)
        true = set()
        for line in open(out):
            if line.startswith("v "):
                true.update(int(x) for x in line[2:].split() if int(x) > 0)
        V = [names[i] for i in range(N) if (i + 1) in true]
        Vi = {i for i in range(N) if (i + 1) in true}
        ein = sum(1 for _, ws in eqs if all(w in Vi for w in ws))
        print(f"|V|={len(V)} Ein={ein} delta={len(V) - ein}")
        print("V:", " ".join(V))
        return
    fn, lo, hi, D, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    c, *_ = encode(fn, lo, hi, D)
    with open(out, "w") as f:
        f.write(f"p cnf {c.n} {len(c.cl)}\n")
        for cl in c.cl:
            f.write(" ".join(map(str, cl)) + " 0\n")
    print(out, c.n, len(c.cl))


if __name__ == "__main__":
    main()
