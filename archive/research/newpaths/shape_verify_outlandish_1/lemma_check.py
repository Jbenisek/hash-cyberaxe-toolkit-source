"""Brute-force check of the lemma used in NOTES.txt:
   in the plain GD model (each equation solves any ONE unknown when all its other words are known),
   a guess set of size F = vars - eqs that determines everything exists  <=>  the 2-core (peeling) is empty.
Random small hypergraphs (sizes 2..4 like the BLAKE3 primitives), exhaustive over all guess sets of size F.
"""
import itertools
import random


def propagate(E, known):
    known = set(known)
    ch = True
    while ch:
        ch = False
        for e in E:
            u = [v for v in e if v not in known]
            if len(u) == 1:
                known.add(u[0])
                ch = True
    return known


def core_empty(E):
    alive = set(range(len(E)))
    ch = True
    while ch:
        ch = False
        cnt = {}
        for i in alive:
            for v in E[i]:
                cnt[v] = cnt.get(v, 0) + 1
        for i in list(alive):
            if any(cnt[v] == 1 for v in E[i]):
                alive.discard(i)
                ch = True
                break
    return not alive


rng = random.Random(5)
agree = disagree = tested = nonempty = 0
for trial in range(4000):
    n = rng.randint(4, 11)
    m = rng.randint(1, n - 1)
    E = [tuple(rng.sample(range(n), rng.randint(2, min(4, n)))) for _ in range(m)]
    used = set(v for e in E for v in e)
    if len(used) < n:
        continue
    F = n - m
    exists = any(len(propagate(E, G)) == n for G in itertools.combinations(range(n), F))
    tested += 1
    nonempty += not core_empty(E)
    if exists == core_empty(E):
        agree += 1
    else:
        disagree += 1
        print("DISAGREE", n, E, exists)
print(f"tested {tested} random hypergraphs ({nonempty} with a non-empty 2-core): agree {agree}, disagree {disagree}")
