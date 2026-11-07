"""kverify_0: my own CNF encoding (independent of ksplit/bigsat.py, rootcore.py) of the two SAT facts behind R10.
  one D S        : a proper closed region A with delta(A) <= D and |A| >= S
  two D U        : proper closed A, B with delta(A), delta(B), delta(A u B) <= D and |A u B| >= U
  peel N         : random peeling orders, reports max number of words peelable (so |J| >= 100 - max)
Closed = contains every word that some equation determines from words in A (constants always known).
delta(X) = |X| - #equations whose unknown words all lie in X.  Cardinality by sequential counters.
Usage: python kv_region_sat.py one 4 47  -> writes r1_D4_S47.cnf
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys
import random
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
from gd_order import build

eqs, const, vars_ = build("fixed", "len64")
WORDS = sorted(vars_)
EQ = [tuple(v for v in vs if v not in const) for _, vs in eqs]


class CNF:
    def __init__(self):
        self.n = 0
        self.cl = []

    def new(self):
        self.n += 1
        return self.n

    def add(self, c):
        self.cl.append(list(c))

    def atmost(self, lits, k):
        n = len(lits)
        if k >= n:
            return
        if k == 0:
            for x in lits:
                self.add([-x])
            return
        S = [[self.new() for _ in range(k)] for _ in range(n)]
        self.add([-lits[0], S[0][0]])
        for j in range(1, k):
            self.add([-S[0][j]])
        for i in range(1, n):
            self.add([-lits[i], S[i][0]])
            self.add([-S[i - 1][0], S[i][0]])
            for j in range(1, k):
                self.add([-lits[i], -S[i - 1][j - 1], S[i][j]])
                self.add([-S[i - 1][j], S[i][j]])
            self.add([-lits[i], -S[i - 1][k - 1]])

    def write(self, fn):
        with open(fn, "w") as fh:
            fh.write(f"p cnf {self.n} {len(self.cl)}\n")
            for c in self.cl:
                fh.write(" ".join(map(str, c)) + " 0\n")


def region(c):
    x = {w: c.new() for w in WORDS}
    for U in EQ:
        for w in U:
            c.add([-x[u] for u in U if u != w] + [x[w]])      # closed
    c.add([-x[w] for w in WORDS])                              # proper
    return x


def delta_le(c, x, D):
    e = []
    for U in EQ:
        v = c.new()
        for u in U:
            c.add([-v, x[u]])
        e.append(v)
    # |X| - sum e <= D  <=>  sum x + sum(not e) <= D + |E|
    c.atmost([x[w] for w in WORDS] + [-v for v in e], D + len(EQ))


def main():
    mode = sys.argv[1]
    if mode == "peel":
        rng = random.Random(1)
        best = 0
        occ = {w: [i for i, U in enumerate(EQ) if w in U] for w in WORDS}
        for _ in range(int(sys.argv[2])):
            rem_e = set(range(len(EQ)))
            rem_w = set(WORDS)
            peeled = []
            while True:
                p = [w for w in rem_w if len([i for i in occ[w] if i in rem_e]) == 1]
                if not p:
                    break
                w = rng.choice(sorted(p))
                i = [i for i in occ[w] if i in rem_e][0]
                rem_e.discard(i)
                rem_w.discard(w)
                peeled.append(w)
            best = max(best, len(peeled))
        print("COMPUTED max peelable over random orders:", best, "-> |J| >=", len(WORDS) - best)
        return
    c = CNF()
    if mode == "one":
        D, S = int(sys.argv[2]), int(sys.argv[3])
        x = region(c)
        delta_le(c, x, D)
        c.atmost([-x[w] for w in WORDS], len(WORDS) - S)
        fn = f"r1_D{D}_S{S}.cnf"
    else:
        D, U = int(sys.argv[2]), int(sys.argv[3])
        a = region(c)
        b = region(c)
        delta_le(c, a, D)
        delta_le(c, b, D)
        u = {w: c.new() for w in WORDS}
        for w in WORDS:
            c.add([-u[w], a[w], b[w]])
            c.add([u[w], -a[w]])
            c.add([u[w], -b[w]])
        delta_le(c, u, D)
        c.atmost([-u[w] for w in WORDS], len(WORDS) - U)
        fn = f"r2_D{D}_U{U}.cnf"
    c.write(fn)
    print(fn, c.n, len(c.cl))


if __name__ == "__main__":
    main()
