"""Trace plain + look closure of a guess set on my own rebuilt 'fixed' system; for each look-accepted word z, list the
words its plain closure adds, the newly covered equations, and which known words (parameters) the univariate
equation in z depends on, split into family constants vs per-instance words.
Usage: python trace.py "w1 w2 ..." ["set2" ...]"""
import sys

sys.dont_write_bytecode = True
from sys_build import symbolic  # noqa: E402


def main():
    eqs, const, names, Y = symbolic()
    ncq = [(nm, frozenset(v for v in (o,) + ins if v not in const), frozenset(v for v in (o,) + ins if v in const))
           for nm, _, o, ins in eqs]
    vars_ = sorted({v for _, s, _ in ncq for v in s})

    def plain(K):
        K = set(K)
        ch = True
        while ch:
            ch = False
            for _, s, _ in ncq:
                u = s - K
                if len(u) == 1:
                    K |= u
                    ch = True
        return K

    def cov(K):
        return {nm for nm, s, _ in ncq if s <= K}

    for gs in sys.argv[1:]:
        G = gs.split()
        K = plain(G)
        print(f"guesses ({len(G)}): {G}\n  plain closure {len(K)}/{len(vars_)}")
        guessed_core = set(G)
        while True:
            c0 = cov(K)
            for z in vars_:
                if z in K:
                    continue
                A = plain(K | {z})
                new = A - K
                nc = cov(A) - c0
                if len(nc) >= len(new):
                    # parameters: known words (in K) appearing in the newly covered equations
                    params = set()
                    for nm, s, cs in ncq:
                        if nm in nc:
                            params |= (s & K)
                    print(f"  look z={z}: +{len(new)} words, {len(nc)} new eqs (checks on z: {len(nc) - len(new) + 1});"
                          f" per-instance parameters ({len(params)}): {sorted(params)}")
                    K = A
                    break
            else:
                break
        print(f"  final closure {len(K)}/{len(vars_)}")


if __name__ == "__main__":
    main()
