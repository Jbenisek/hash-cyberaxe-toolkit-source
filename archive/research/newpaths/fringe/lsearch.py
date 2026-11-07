"""Local search for smaller guess sets: from greedy covering sets of size k, try every 'remove 2, add 1' move and
keep any covering set of size k-1 (then repeat).  Heuristic companion of the exhaustive bf runs.
Works on the rule files written by export_rules.py / gdcv.py / gdtab.py (same format as ../audit/bf.c).
Usage: python lsearch.py <rules file> <greedy starts> [seed]
"""
import random
import sys

sys.dont_write_bytecode = True


def load(fn):
    with open(fn) as fh:
        nv, ne, nr = map(int, fh.readline().split())
        names = fh.readline().split()
        eqs = [list(map(int, fh.readline().split())) for _ in range(ne)]
        rules = []
        for _ in range(nr):
            x = list(map(int, fh.readline().split()))
            rules.append((x[1:], x[0]))
    return nv, names, eqs, rules


def closure(nv, eqs, rules, occ, occr, start):
    known = [False] * nv
    unk = [len(e) for e in eqs]
    rmiss = [len(t) for t, _ in rules]
    stack = []

    def add(v):
        if not known[v]:
            known[v] = True
            stack.append(v)

    for v in start:
        add(v)
    n = 0
    while stack:
        v = stack.pop()
        n += 1
        for k in occ[v]:
            unk[k] -= 1
            if unk[k] == 1:
                for u in eqs[k]:
                    if not known[u]:
                        add(u)
        for r in occr[v]:
            rmiss[r] -= 1
            if rmiss[r] == 0:
                add(rules[r][1])
    return sum(known)


def main():
    fn, starts = sys.argv[1], int(sys.argv[2])
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    nv, names, eqs, rules = load(fn)
    occ = [[] for _ in range(nv)]
    for k, e in enumerate(eqs):
        for v in e:
            occ[v].append(k)
    occr = [[] for _ in range(nv)]
    for r, (t, _) in enumerate(rules):
        for v in t:
            occr[v].append(r)
    free = nv - len(eqs) - (6 if "cv" in fn else 0)   # the CV block (8 words, dimension 2) counts as 6 equations
    best = None
    seen = set()
    for _ in range(starts):
        # random greedy: guess a random unknown among those in equations with 2 unknowns, until full
        S = []
        while closure(nv, eqs, rules, occ, occr, S) < nv:
            S.append(rng.randrange(nv))
        S = sorted(set(S))
        # prune redundant guesses
        for v in list(S):
            T = [u for u in S if u != v]
            if closure(nv, eqs, rules, occ, occr, T) == nv:
                S = T
        improved = True
        while improved:
            improved = False
            key = tuple(S)
            if key in seen:
                break
            seen.add(key)
            for i in range(len(S)):
                for j in range(i + 1, len(S)):
                    base = [u for t, u in enumerate(S) if t not in (i, j)]
                    for a in range(nv):
                        if a in base:
                            continue
                        if closure(nv, eqs, rules, occ, occr, base + [a]) == nv:
                            S = sorted(base + [a])
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
        if best is None or len(S) < len(best):
            best = S
            print(f"{fn}: covering set of {len(S)} guesses ({len(S) - free} checks; freedom {free}): "
                  f"{[names[v] for v in S]}", flush=True)
    print(f"{fn}: done, {starts} starts, best {len(best)} guesses = {len(best) - free} checks")


if __name__ == "__main__":
    main()
