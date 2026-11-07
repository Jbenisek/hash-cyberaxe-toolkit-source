"""2-core of the guess-and-determine hypergraph (plain model, no tables).
Peeling: repeatedly remove a variable that occurs in exactly one remaining equation, together with that equation
(it can be solved LAST from that equation).  What remains is the unique 2-core: every remaining variable occurs in
>= 2 remaining equations.  Variables left with no equation ("stranded") must be guessed.
A 0-check order needs: guesses = freedom, and the guesses must break the whole core.
Usage: python core.py
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

sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
from gd_order import build  # noqa: E402  (read only)


def core(eqs, const):
    E = [set(v for v in vs if v not in const) for _, vs in eqs]
    alive = [True] * len(E)
    vars_ = set().union(*E)
    occ = {v: set() for v in vars_}
    for i, e in enumerate(E):
        for v in e:
            occ[v].add(i)
    removed_v = set()
    changed = True
    while changed:
        changed = False
        for v in list(vars_ - removed_v):
            live = [i for i in occ[v] if alive[i]]
            if len(live) == 1:
                alive[live[0]] = False
                removed_v.add(v)
                changed = True
    cv = {v for v in vars_ - removed_v if any(alive[i] for i in occ[v])}
    stranded = vars_ - removed_v - cv
    ce = [i for i in range(len(E)) if alive[i]]
    return cv, ce, stranded, [eqs[i][0] for i in ce]


def report(label, eqs, const):
    vars_ = {v for _, vs in eqs for v in vs} - const
    F = len(vars_) - len(eqs)
    cv, ce, st, names = core(eqs, const)
    print(f"{label:28s} vars {len(vars_)} eqs {len(eqs)} freedom {F} | core vars {len(cv)} core eqs {len(ce)} "
          f"core deficiency {len(cv) - len(ce)} | stranded {len(st)}")
    return cv, ce, names


if __name__ == "__main__":
    for variant in ("fixed", "outhalf"):
        eqs, const, _ = build(variant, "len64")
        report(variant, eqs, const)
    eqs, const, _ = build("outhalf", "len64")
    outs = ["out0", "out2", "out5", "out7"]
    for k in range(0, 4):
        for S in itertools.combinations(outs, k):
            e2 = [e for e in eqs if not (e[0].startswith("out") and e[0] not in S)]
            cv, ce, names = report("outhalf held=" + (",".join(S) or "-"), e2, const)
    eqs, const, _ = build("outhalf", "len64")
    e1 = [e for e in eqs if not (e[0].startswith("out") and e[0] != "out0")]
    cv, ce, st, names = core(e1, const)
    print("core equations for held=out0:", sorted(names))
