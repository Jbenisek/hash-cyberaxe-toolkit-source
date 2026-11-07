"""Can PROMOTED family constants (a sub-family) plus per-call tables open the k = 3 sphere door?
Promote a set P of words to constants (chosen once, consistently, from one solution).  Equations whose words are
all constant drop out (paid once, at set-up).  Sub-family freedom F' = (vars - |P|) - (equations left); need
F' >= 3 words (2^96 >= 2^80 members).  0 per-member checks  <=>  generous table peeling (peel.py) empties the
system.  Search: greedy (add the word that shrinks the core most) + random sets biased to useful words.
Usage: python promote_search.py <held e.g. 0,2,5> <random_trials> <seed>
"""
import random
import sys

sys.dont_write_bytecode = True
from peel import build, table_peel  # noqa: E402  (own folder)


def reduce(eqs, const, P):
    c2 = set(const) | set(P)
    out = [(n, c, vs) for n, c, vs in eqs if any(v not in c2 for v in vs)]
    allv = {v for _, _, vs in out for v in vs} - c2
    return out, c2, len(allv) - len(out)


def score(eqs, const, P, rng, restarts=2):
    e2, c2, F = reduce(eqs, const, P)
    return min(len(table_peel(e2, c2, rng)) for _ in range(restarts)), F


def main():
    held = tuple(int(x) for x in sys.argv[1].split(","))
    trials = int(sys.argv[2])
    rng = random.Random(int(sys.argv[3]))
    eqs, const, allv = build(held)
    outvars = [v for n, _, vs in eqs if n.startswith("out") for v in vs]
    einputs = []
    for n, c, vs in eqs:
        if c in ("E0", "E2") and n.endswith(":a1"):
            einputs += [vs[1], vs[2], vs[3]]
        if c in ("E0", "E2") and n.endswith((":d1", ":c1", ":a2")):
            einputs.append(vs[1] if not n.endswith(":a2") else vs[3])
    msg = [f"m{i}" for i in range(16)]
    pool = sorted(set(outvars + einputs + msg + [v for v in allv if v.endswith(("a2", "b2", "c2", "d2"))]))
    best = (10 ** 9, None, None)
    log = []
    # greedy
    P = []
    cur, F = score(eqs, const, P, rng)
    log.append(f"greedy start core {cur} F' {F}")
    while True:
        cands = []
        for v in allv:
            if v in P:
                continue
            s, F2 = score(eqs, const, P + [v], rng, 1)
            if F2 >= 3:
                cands.append((s, F2, v))
        if not cands:
            break
        cands.sort()
        s, F2, v = cands[0]
        P.append(v)
        log.append(f"greedy +{v}: core {s} F' {F2}")
        if s < best[0]:
            best = (s, list(P), F2)
        if s == 0:
            break
    # random
    for _ in range(trials):
        k = rng.randint(1, 10)
        P = rng.sample(pool, k)
        s, F2 = score(eqs, const, P, rng, 1)
        if F2 >= 3 and s < best[0]:
            best = (s, P, F2)
            log.append(f"random best core {s} F' {F2} P={P}")
    log.append(f"BEST held={held}: core eqs left {best[0]}  F' {best[2]}  P={best[1]}")
    print("\n".join(log))


if __name__ == "__main__":
    main()
