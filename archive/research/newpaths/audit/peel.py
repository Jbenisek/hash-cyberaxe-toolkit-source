"""Exact reduction for the plain model: a word that occurs in exactly one equation can be removed with that
equation (min guesses unchanged: such a word is derived last, and a guess on it can be moved to another word of
its equation).  Repeats to a fixpoint.  Prints the reduced sizes; writes rules_<variant>_len64_peeled.txt for bf."""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "orig"))
from gd_order import build
from rules import nc_eqs
for variant in ("fixed", "outhalf"):
    eqs, const, vars_ = build(variant, "len64")
    E = [set(vs) for _, vs in nc_eqs(eqs, const)]
    removed = []
    ch = True
    while ch:
        ch = False
        occ = {}
        for i, e in enumerate(E):
            for v in e:
                occ.setdefault(v, []).append(i)
        for v, l in occ.items():
            if len(l) == 1:
                removed.append((v, l[0]))
                E[l[0]] = None
                E = [e for e in E if e is not None]
                ch = True
                break
    V = sorted({v for e in E for v in e})
    print(f"{variant}: {len(vars_)} words/{len(eqs)} eqs -> peeled {len(V)} words/{len(E)} eqs (freedom {len(V)-len(E)}); removed: {[v for v, _ in removed]}")
    ix = {v: i for i, v in enumerate(V)}
    with open(os.path.join(HERE, f"rules_{variant}_len64_peeled.txt"), "w") as fh:
        fh.write(f"{len(V)} {len(E)} 0\n" + " ".join(V) + "\n")
        for e in E:
            fh.write(" ".join(str(ix[v]) for v in sorted(e)) + "\n")
