"""Exact check-count facts for the sphere door (k of out0,2,5,7 held) in the word-level GD model.

LEMMA (DERIVED; brute-force checked in lemma.py): in the GD model (each equation solvable for any one unknown),
  min checks = min number of equations whose deletion leaves a hypergraph with an EMPTY 2-core
  (2-core = what remains after repeatedly removing a word that lies in exactly one remaining equation, together
  with that equation; guesses are NOT removed - they play no role).
  Proof sketch: in a 0-check order every equation solves a word that occurs in no earlier equation; the last
  core equation cannot do that, because each of its words lies in another (earlier) core equation.  Conversely
  an empty core gives the order (reverse peeling) and the guesses are the words never solved.
  So: non-empty core => at least 1 check, for EVERY guess set.

TABLE MODEL (permissive): any subset B of the live equations of ONE G call (every call treated as table-able,
  the held out-equations of that call allowed in B) may be removed when B has a perfect matching onto words that
  occur in no other live equation.  A real table step (or one of ../gd_promote.py's cycle macros) with 0 checks
  has such a matching (Hall: otherwise a subset of its equations over-determines its words = a check), so a
  non-empty permissive core => at least 1 check with any per-call tables.

Usage: python cores.py [maxdel]     (writes nothing; print to stdout)
"""
import itertools
import sys

from build import system


def incid(eqs, const):
    E = [frozenset(v for v in vs if v not in const) for _, vs in eqs]
    occ = {}
    for i, e in enumerate(E):
        for v in e:
            occ.setdefault(v, []).append(i)
    return E, occ


def plain_core(E, occ, alive):
    """alive: set of eq indices.  Returns the 2-core (set of eq indices)."""
    alive = set(alive)
    deg = {v: sum(1 for i in occ[v] if i in alive) for v in occ}
    stack = [v for v, d in deg.items() if d == 1]
    while stack:
        v = stack.pop()
        if deg[v] != 1:
            continue
        i = next(i for i in occ[v] if i in alive)
        alive.discard(i)
        for u in E[i]:
            deg[u] -= 1
            if deg[u] == 1:
                stack.append(u)
    return alive


def has_matching(block, E, private):
    """Perfect matching of equations in block onto distinct private words they contain (simple augmenting)."""
    match = {}

    def aug(i, seen):
        for v in E[i] & private:
            if v in seen:
                continue
            seen.add(v)
            if v not in match or aug(match[v], seen):
                match[v] = i
                return True
        return False

    return all(aug(i, set()) for i in block)


def table_core(eqs, E, occ, alive):
    names = [n for n, _ in eqs]
    callof = {}
    for i, n in enumerate(names):
        callof[i] = n.split(":")[0] if ":" in n else None
    # out equations may join the block of the call that produced one of their words
    producer = {}
    for i, n in enumerate(names):
        if ":" in n:
            producer[eqs[i][1][0]] = callof[i]
    groups = {}
    for i in range(len(eqs)):
        if callof[i] is not None:
            groups.setdefault(callof[i], set()).add(i)
    for i in range(len(eqs)):
        if callof[i] is None:
            for v in eqs[i][1]:
                if v in producer:
                    groups[producer[v]].add(i)
    alive = set(alive)
    changed = True
    while changed:
        changed = False
        alive = plain_core(E, occ, alive)
        for g, members in groups.items():
            live = sorted(members & alive)
            for r in range(1, len(live) + 1):
                for B in itertools.combinations(live, r):
                    Bs = set(B)
                    words = set().union(*(E[i] for i in B))
                    private = {v for v in words if all(j in Bs or j not in alive for j in occ[v])}
                    if len(private) >= r and has_matching(B, E, private):
                        alive -= Bs
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break
    return alive


def min_deletions(E, occ, alive0, maxd):
    """Smallest d <= maxd such that deleting d equations empties the plain core; None if none."""
    core0 = plain_core(E, occ, alive0)
    if not core0:
        return 0, ()

    def rec(alive, core, depth, lo):
        if depth == 0:
            return None
        for i in sorted(core):
            if i <= lo:
                continue
            a2 = alive - {i}
            c2 = plain_core(E, occ, a2)
            if not c2:
                return (i,)
            r = rec(a2, c2, depth - 1, i)
            if r:
                return (i,) + r
        return None

    for d in range(1, maxd + 1):
        r = rec(set(alive0), core0, d, -1)
        if r:
            return d, r
    return None, ()


def main():
    maxd = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    outs = ["out0", "out2", "out5", "out7"]
    rows = []
    cases = [("outhalf", S) for k in range(0, 5) for S in itertools.combinations(outs, k)] + [("fixed", ())]
    for variant, S in cases:
        eqs, const, _ = system(held=S, variant=variant)
        E, occ = incid(eqs, const)
        nv, ne = len(occ), len(eqs)
        F = nv - ne
        allq = set(range(ne))
        pc = plain_core(E, occ, allq)
        tc = table_core(eqs, E, occ, allq)
        pv = set().union(*(E[i] for i in pc)) if pc else set()
        tv = set().union(*(E[i] for i in tc)) if tc else set()
        # upper bound: outhalf -> delete the k out-equations (the held=- system has an empty core); fixed -> 4
        ub = len(S) if variant == "outhalf" else 4
        lim = min(maxd, ub - 1)
        d, D = min_deletions(E, occ, allq, lim) if lim >= 0 else (0, ())
        if d is None:
            res = f"= {ub} (no deletion of <= {lim} works; {ub} works)"
        else:
            res = f"= {d} {[eqs[i][0] for i in D]}"
        lab = variant + ":" + (",".join(S) or "-")
        print(f"{lab:26s} words {nv:3d} eqs {ne:3d} F {F:2d} | plain core {len(pc):3d} eqs/{len(pv):3d} words "
              f"def {len(pv) - len(pc):2d} | table core {len(tc):3d} eqs/{len(tv):3d} words def {len(tv) - len(tc):2d}"
              f" | exact min checks (plain) {res}", flush=True)


if __name__ == "__main__":
    main()
