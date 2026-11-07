"""Beyond one-word-at-a-time: a 2-word joint solve is tabulable within the preprocessing budget (2^64 entries)
only if all its parameters are family constants, i.e. it is visible from the constants alone.  Test every pair
{z1, z2} of unknown words from K = {} (constants only): does guessing both and propagating plainly cover at least as
many equations as it adds words (2 checks on 2 words)?  Also count single words (look from {}) for reference."""
import itertools
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(fn):
    with open(fn) as fh:
        nv, ne, nr = map(int, fh.readline().split())
        names = fh.readline().split()
        eqs = [frozenset(map(int, fh.readline().split())) for _ in range(ne)]
    return nv, names, eqs


def plain(eqs, K):
    K = set(K)
    ch = True
    while ch:
        ch = False
        for e in eqs:
            u = e - K
            if len(u) == 1:
                K |= u
                ch = True
    return K


def main():
    nv, names, eqs = load(os.path.join(HERE, "sys_fixed.txt"))
    singles = 0
    for z in range(nv):
        A = plain(eqs, {z})
        if sum(1 for e in eqs if e <= A) >= len(A):
            singles += 1
    hits = []
    best = -99
    for z1, z2 in itertools.combinations(range(nv), 2):
        A = plain(eqs, {z1, z2})
        surplus = sum(1 for e in eqs if e <= A) - len(A)      # >= 0 means 2 checks on the 2 words
        best = max(best, surplus)
        if surplus >= 0:
            hits.append((names[z1], names[z2], len(A)))
    lines = [f"single words pinned from constants alone: {singles}",
             f"pairs pinned from constants alone (2 checks on 2 words): {len(hits)}; best surplus {best} "
             f"(-2 = no check, -1 = one check)", *[f"  {h}" for h in hits[:20]]]
    print("\n".join(lines))
    open(os.path.join(HERE, "pairs0.log"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
