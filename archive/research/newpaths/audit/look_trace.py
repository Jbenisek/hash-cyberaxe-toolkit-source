"""Trace the 'look' relaxation of bf.c for given guess sets: which words were accepted by a one-word lookahead
(guess z, propagate plainly, >= 1 newly covered equation is a check on z) and which check equations decided them.
Usage: python look_trace.py <variant> "<w1 w2 ...>" ["<set2>" ...]"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "orig"))
from gd_order import build  # noqa: E402
from rules import nc_eqs, closure  # noqa: E402


def covered(ncq, K):
    return {n for n, vs in ncq if all(v in K for v in vs)}


def trace(variant, guesses):
    eqs, const, vars_ = build(variant, "len64")
    ncq = nc_eqs(eqs, const)
    K = closure(ncq, set(guesses))
    out = [f"guesses {guesses}: plain closure {len(K)}/{len(vars_)}"]
    while True:
        cov = covered(ncq, K)
        for z in vars_:
            if z in K:
                continue
            A = closure(ncq, K | {z})
            new = A - K
            newcov = covered(ncq, A) - cov
            if len(newcov) >= len(new):
                out.append(f"  look: z={z} adds {len(new)} words, {len(newcov)} new equations "
                           f"(checks on z: {len(newcov) - len(new) + 1}); new equations {sorted(newcov)}")
                K = A
                break
        else:
            break
    out.append(f"  final closure {len(K)}/{len(vars_)}")
    return out


if __name__ == "__main__":
    for s in sys.argv[2:]:
        print("\n".join(trace(sys.argv[1], s.split())))
