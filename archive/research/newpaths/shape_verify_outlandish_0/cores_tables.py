"""Lower bound on checks WITH per-call tables (any subset of one G call's equations, plus the held out-equation
of that call, may be solved jointly when it has a perfect matching onto words used nowhere else).
min checks (tables) >= min number of deleted equations that empties this permissive core (see cores.py).
Searches deletions of size <= maxd.  Usage: python cores_tables.py <maxd> [held list, e.g. out0,out2,out5]
"""
import itertools
import sys

from build import system
from cores import incid, table_core


def main():
    maxd = int(sys.argv[1])
    outs = ["out0", "out2", "out5", "out7"]
    cases = [tuple(sys.argv[2].split(","))] if len(sys.argv) > 2 else list(itertools.combinations(outs, 3))
    for S in cases:
        eqs, const, _ = system(held=S)
        E, occ = incid(eqs, const)
        allq = set(range(len(eqs)))
        core0 = table_core(eqs, E, occ, allq)
        found = None
        calls = 0

        def rec(alive, core, depth, lo):
            nonlocal calls
            if depth == 0:
                return None
            for i in sorted(core):
                if i <= lo:
                    continue
                a2 = alive - {i}
                calls += 1
                c2 = table_core(eqs, E, occ, a2)
                if not c2:
                    return (i,)
                r = rec(a2, c2, depth - 1, i)
                if r:
                    return (i,) + r
            return None

        for d in range(1, maxd + 1):
            found = rec(allq, core0, d, -1)
            if found:
                break
        res = f"min deletions = {len(found)} {[eqs[i][0] for i in found]}" if found else \
            f"no deletion of <= {maxd} equations empties the table core => checks >= {maxd + 1}"
        print(f"held={','.join(S):18s} table core {len(core0)} eqs | {res} | core evaluations {calls}", flush=True)


if __name__ == "__main__":
    main()
