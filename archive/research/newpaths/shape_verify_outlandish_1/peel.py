"""Skeptic check of the sphere door (k = 3 held half-digest words with 0 checks).
Independent rebuild of the word-level GD system from the spec (does NOT import gd_order), then
  (1) plain 2-core by peeling: a 0-check order exists  <=>  the 2-core is empty (proof in NOTES.txt);
  (2) generous table peeling: besides single equations, ANY subset B of the remaining equations of ONE G call
      with dof(B) = |vars(B)| - |B| <= 2 (vars = non-constant words) may be removed when at most dof(B) of its
      words still occur outside B (they are the table trigger, the rest is solved by the table and is private).
      Randomised removal order, many restarts (the block rule is not obviously confluent).
  (3) optional promotions: extra family constants (sub-family), freedom must stay >= 3 words (2^96 >= 2^80).
Usage: python peel.py [restarts] [promote_trials]
"""
import itertools
import random
import sys

PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def build(held):
    """held: subset of {0,2,5,7}.  Returns eqs [(name, call, frozenset vars)], consts, all vars."""
    st = [f"iv{i}" for i in range(16)]
    const = set(st)
    eqs = []
    m = [f"m{i}" for i in range(16)]

    def G(nm, idx, x, y):
        a, b, c, d = (st[i] for i in idx)
        a1, d1, c1, b1, a2, d2, c2, b2 = (f"{nm}.{t}" for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2"))
        for role, vs in (("a1", (a1, a, b, x)), ("d1", (d1, d, a1)), ("c1", (c1, c, d1)), ("b1", (b1, b, c1)),
                         ("a2", (a2, a1, b1, y)), ("d2", (d2, d1, a2)), ("c2", (c2, c1, d2)), ("b2", (b2, b1, c2))):
            eqs.append((f"{nm}:{role}", nm, vs))
        st[idx[0]], st[idx[1]], st[idx[2]], st[idx[3]] = a2, b2, c2, d2

    s = m[:]
    for j in range(4):
        G(f"K{j}", COLS[j], s[2 * j], s[2 * j + 1])
    for j in range(4):
        G(f"D{j}", DIAG[j], s[8 + 2 * j], s[9 + 2 * j])
    s = [s[p] for p in PERM]
    assert s[:8] == ["m2", "m6", "m3", "m10", "m7", "m0", "m4", "m13"]
    assert s[8:] == ["m1", "m11", "m12", "m5", "m9", "m14", "m15", "m8"]
    for j in range(4):
        G(f"C{j}", COLS[j], s[2 * j], s[2 * j + 1])
    for j in (0, 2):                      # E1, E3 do not touch out0,2,5,7
        G(f"E{j}", DIAG[j], s[8 + 2 * j], s[9 + 2 * j])
    for i in held:
        eqs.append((f"out{i}", f"out{i}", (st[i], st[i + 8])))
    allv = sorted({v for _, _, vs in eqs for v in vs} - const)
    return eqs, const, allv


def plain_core(eqs, const):
    E = [set(v for v in vs if v not in const) for _, _, vs in eqs]
    alive = [True] * len(E)
    occ = {}
    for i, e in enumerate(E):
        for v in e:
            occ.setdefault(v, set()).add(i)
    changed = True
    while changed:
        changed = False
        for v, ii in occ.items():
            live = [i for i in ii if alive[i]]
            if len(live) == 1:
                alive[live[0]] = False
                changed = True
    return [i for i in range(len(E)) if alive[i]]


def candidate_blocks(eqs, E):
    """All multi-equation subsets of one G call with dof <= 2 (fixed by the constants, not by the order)."""
    calls = {}
    for i, (_, c, _) in enumerate(eqs):
        calls.setdefault(c, []).append(i)
    out = []
    for c, ii in calls.items():
        for r in range(2, len(ii) + 1):
            for B in itertools.combinations(ii, r):
                V = set().union(*(E[i] for i in B))
                dof = len(V) - len(B)
                if 0 <= dof <= 2:
                    inner = {}
                    for i in B:
                        for v in E[i]:
                            inner[v] = inner.get(v, 0) + 1
                    out.append((B, V, dof, inner))
    return out


def table_peel(eqs, const, rng):
    """Generous peeling with per-call table blocks.  Returns the indices of the equations left."""
    E = [frozenset(v for v in vs if v not in const) for _, _, vs in eqs]
    blocks = candidate_blocks(eqs, E)
    alive = set(range(len(E)))
    cnt = {}
    for i in alive:
        for v in E[i]:
            cnt[v] = cnt.get(v, 0) + 1
    while True:
        moves = [(i,) for i in alive if any(cnt[v] == 1 for v in E[i])]
        for B, V, dof, inner in blocks:
            if all(i in alive for i in B) and sum(1 for v in V if cnt[v] > inner[v]) <= dof:
                moves.append(B)
        if not moves:
            break
        B = rng.choice(moves)
        for i in B:
            alive.discard(i)
            for v in E[i]:
                cnt[v] -= 1
    return sorted(alive)


def main():
    restarts = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    rng = random.Random(2026)
    print("held          vars eqs freedom | plain-core eqs | table-peel: min eqs left over restarts")
    for k in range(0, 5):
        for S in itertools.combinations((0, 2, 5, 7), k):
            eqs, const, allv = build(S)
            F = len(allv) - len(eqs)
            pc = plain_core(eqs, const)
            left = min(len(table_peel(eqs, const, rng)) for _ in range(restarts))
            print(f"{','.join('out%d' % i for i in S) or '-':22s} {len(allv)} {len(eqs)} {F:3d} | {len(pc):3d} | {left}")


if __name__ == "__main__":
    main()
