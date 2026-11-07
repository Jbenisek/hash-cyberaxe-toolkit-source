"""Brute-force check of the lemma used in cores.py, on random small hypergraphs.

A = exact minimum checks of the GD process (try every guess set of every size, propagate "equation with one
    unknown -> solve it", stop at the first size that determines every word; checks = size - (words - eqs)).
B = minimum number of equations whose deletion leaves an empty 2-core (peeling a word that lies in one equation).
Lemma: A == B.  Also: A == 0  <=>  the 2-core of the whole hypergraph is empty (guesses do not matter).
Usage: python lemma.py [trials] [seed]
"""
import itertools
import random
import sys


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


def exact_checks(n, E):
    F = n - len(E)
    for g in range(0, n + 1):
        for S in itertools.combinations(range(n), g):
            if len(propagate(E, S)) == n:
                return g - F
    return None


def core_empty(E):
    alive = list(range(len(E)))
    ch = True
    while ch:
        ch = False
        deg = {}
        for i in alive:
            for v in E[i]:
                deg[v] = deg.get(v, 0) + 1
        for i in alive:
            if any(deg[v] == 1 for v in E[i]):
                alive.remove(i)
                ch = True
                break
    return not alive


def min_del(E):
    for d in range(len(E) + 1):
        for D in itertools.combinations(range(len(E)), d):
            if core_empty([E[i] for i in range(len(E)) if i not in D]):
                return d


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 11)
    nmax = int(sys.argv[3]) if len(sys.argv) > 3 else 9
    agree = dis = nonempty = 0
    hist = {}
    for _ in range(trials):
        n = rng.randint(3, nmax)
        m = rng.randint(1, n)                       # m <= n, as in the GD systems (freedom >= 0)
        E = []
        for _ in range(m):
            k = rng.choice((2, 3, 3, 4))
            E.append(tuple(sorted(rng.sample(range(n), min(k, n)))))
        used = sorted(set(v for e in E for v in e))
        ren = {v: i for i, v in enumerate(used)}
        E = [tuple(ren[v] for v in e) for e in E]
        n = len(used)
        a = exact_checks(n, E)
        b = min_del(E)
        nonempty += not core_empty(E)
        hist[a] = hist.get(a, 0) + 1
        if a == b and ((a == 0) == core_empty(E)):
            agree += 1
        else:
            dis += 1
            print("DISAGREE", n, E, a, b)
    print(f"trials {trials}: agree {agree}, disagree {dis}; non-empty 2-core in {nonempty}; "
          f"exact-check histogram {dict(sorted(hist.items()))}")


if __name__ == "__main__":
    main()
