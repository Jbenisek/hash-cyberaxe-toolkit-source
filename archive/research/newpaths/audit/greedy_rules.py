"""Upper bounds by greedy search under each rule set (plain / orig / pair): at each step guess the word whose
closure gain is largest (random tie-break), then drop redundant guesses.  Usage: python greedy_rules.py <variant> <runs>"""
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "orig"))
from rulesets import get, closure_r  # noqa: E402


def run(vars_, ncq, rules, rng):
    K, G = set(), []
    while len(K) < len(vars_):
        best, cands = -1, []
        for z in vars_:
            if z in K:
                continue
            g = len(closure_r(ncq, rules, K | {z}))
            if g > best:
                best, cands = g, [z]
            elif g == best:
                cands.append(z)
        z = rng.choice(cands)
        G.append(z)
        K = closure_r(ncq, rules, K | {z})
    for z in list(G):                       # drop redundant guesses
        H = [x for x in G if x != z]
        if len(closure_r(ncq, rules, set(H))) == len(vars_):
            G = H
    return G


def main():
    variant, runs = sys.argv[1], int(sys.argv[2])
    lines = []
    for rset in ("plain", "orig", "pair"):
        eqs, const, vars_, ncq, rules = get(variant, "len64", rset)
        rng = random.Random(17)
        hist, best = {}, None
        for _ in range(runs):
            G = run(vars_, ncq, rules, rng)
            hist[len(G)] = hist.get(len(G), 0) + 1
            if best is None or len(G) < len(best):
                best = G
        freedom = len(vars_) - len(ncq)
        lines.append(f"{variant} {rset}: {runs} greedy runs, guess-count histogram {dict(sorted(hist.items()))};"
                     f" best {len(best)} guesses = {len(best) - freedom} checks: {best}")
        print(lines[-1], flush=True)
    open(os.path.join(HERE, f"greedy_{variant}.log"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
