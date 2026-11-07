"""Promotion search, part 2: (a) every subset of message words of size 1..10 promoted, (b) simulated annealing
over promoted sets drawn from message words, E0/E2 inputs, out-equation words and all call outputs.
Score = equations left after generous per-call table peeling (peel.table_peel); constraint F' >= 3.
Usage: python anneal.py <held e.g. 0,2,5> <mode: msg|anneal> <seed> [anneal_steps]
"""
import itertools
import math
import random
import sys

sys.dont_write_bytecode = True
from peel import build, table_peel  # noqa: E402
from promote_search import reduce  # noqa: E402


def sc(eqs, const, P, rng):
    e2, c2, F = reduce(eqs, const, P)
    if F < 3:
        return None, F
    return len(table_peel(e2, c2, rng)), F


def main():
    held = tuple(int(x) for x in sys.argv[1].split(","))
    mode = sys.argv[2]
    rng = random.Random(int(sys.argv[3]))
    eqs, const, allv = build(held)
    msg = [f"m{i}" for i in range(16)]
    best = (10 ** 9, None, None)
    hist = {}
    if mode == "msg":
        n = 0
        for k in range(1, 11):
            for P in itertools.combinations(msg, k):
                s, F = sc(eqs, const, list(P), rng)
                if s is None:
                    continue
                n += 1
                hist[s // 10 * 10] = hist.get(s // 10 * 10, 0) + 1
                if s < best[0]:
                    best = (s, P, F)
        print(f"held={held} msg subsets tested {n}; core-size histogram (by tens) {dict(sorted(hist.items()))}")
    else:
        steps = int(sys.argv[4]) if len(sys.argv) > 4 else 3000
        pool = sorted(set(msg) | {v for v in allv if v.endswith(("a2", "b2", "c2", "d2"))})
        P = []
        cur, F = sc(eqs, const, P, rng)
        for t in range(steps):
            T = 3.0 * (1 - t / steps) + 0.05
            Q = list(P)
            r = rng.random()
            if Q and r < 0.33:
                Q.remove(rng.choice(Q))
            elif Q and r < 0.66:
                Q[rng.randrange(len(Q))] = rng.choice([v for v in pool if v not in Q])
            else:
                Q.append(rng.choice([v for v in pool if v not in Q]))
            s, F2 = sc(eqs, const, Q, rng)
            if s is None:
                continue
            if s <= cur or rng.random() < math.exp((cur - s) / T):
                P, cur = Q, s
                if s < best[0]:
                    best = (s, list(Q), F2)
            if best[0] == 0:
                break
        print(f"held={held} anneal steps {steps} seed {sys.argv[3]}")
    print(f"BEST core eqs left {best[0]}  F' {best[2]}  P={best[1]}")


if __name__ == "__main__":
    main()
