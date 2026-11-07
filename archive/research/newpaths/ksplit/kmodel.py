"""k-split model on top of gd_order.build / gd_sat.table_macros (read-only imports).

Words are bit positions in Python ints.  cl(T) = one-unknown propagation closure (optionally table macros).
Exports the system for the C search (ksearch.c) as: line "N E M F", N names, E lines "name k i..", M lines "t i.. tgt".
Usage: python kmodel.py export <fixed|outhalf> <plain|tables> <out>
       python kmodel.py stats  <fixed|outhalf> <plain|tables>
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

import itertools
import sys

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
from gd_order import build          # noqa: E402
from gd_sat import table_macros     # noqa: E402


class Sys:
    def __init__(self, variant, mode):
        eqs, const, vars_ = build(variant, "len64")
        self.variant, self.mode = variant, mode
        self.names = list(vars_)
        self.idx = {v: i for i, v in enumerate(vars_)}
        self.N = len(vars_)
        self.ALL = (1 << self.N) - 1
        self.eqs = []                 # (name, mask, [idx])
        for name, vs in eqs:
            ws = [self.idx[v] for v in vs if v not in const]
            m = 0
            for w in ws:
                m |= 1 << w
            self.eqs.append((name, m, ws))
        self.E = len(self.eqs)
        self.F = self.N - self.E
        self.macros = []              # (trigmask, tgt)
        if mode == "tables":
            for trig, tgt in table_macros(eqs, const):
                t = 0
                for u in trig:
                    if u not in const:
                        t |= 1 << self.idx[u]
                self.macros.append((t, self.idx[tgt]))

    def closure(self, K, steps=None):
        ch = True
        while ch:
            ch = False
            for name, m, _ in self.eqs:
                u = m & ~K
                if u and not (u & (u - 1)):
                    K |= u
                    ch = True
                    if steps is not None:
                        steps.append((name, u.bit_length() - 1))
            for t, tg in self.macros:
                if not (t & ~K) and not (K >> tg) & 1:
                    K |= 1 << tg
                    ch = True
                    if steps is not None:
                        steps.append(("TABLE", tg))
        return K

    def ein(self, X):
        return sum(1 for _, m, _ in self.eqs if not (m & ~X))

    def mask(self, names):
        m = 0
        for n in names:
            m |= 1 << self.idx[n]
        return m

    def nm(self, m):
        return [self.names[i] for i in range(self.N) if (m >> i) & 1]

    def export(self, out):
        with open(out, "w") as fh:
            fh.write(f"{self.N} {self.E} {len(self.macros)} {self.F}\n")
            for v in self.names:
                fh.write(v + "\n")
            for name, _, ws in self.eqs:
                fh.write(f"{name} {len(ws)} " + " ".join(map(str, ws)) + "\n")
            for t, tg in self.macros:
                bits = [i for i in range(self.N) if (t >> i) & 1]
                fh.write(f"{len(bits)} " + " ".join(map(str, bits)) + f" {tg}\n")


def stats(S):
    pc = lambda x: bin(x).count("1")
    single = [(pc(S.closure(1 << i)), S.names[i]) for i in range(S.N)]
    single.sort(reverse=True)
    print(f"{S.variant}/{S.mode}: N={S.N} E={S.E} F={S.F} macros={len(S.macros)}")
    print("largest singleton closures:", single[:8])
    best = []
    hist = {}
    for i, j in itertools.combinations(range(S.N), 2):
        c = pc(S.closure((1 << i) | (1 << j)))
        hist[c] = hist.get(c, 0) + 1
        best.append((c, S.names[i], S.names[j]))
    best.sort(reverse=True)
    print("pair closure size histogram:", dict(sorted(hist.items())))
    print("largest pair closures:", best[:6])


if __name__ == "__main__":
    if sys.argv[1] == "export":
        Sys(sys.argv[2], sys.argv[3]).export(sys.argv[4])
    else:
        stats(Sys(sys.argv[2], sys.argv[3]))
