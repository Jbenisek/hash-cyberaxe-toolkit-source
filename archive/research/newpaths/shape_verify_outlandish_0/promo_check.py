"""Numerical sanity check of the promotion argument (NOTES section 4).

Promote = fix a word set P per sub-family; equations whose words all lie in P become setup constraints E_c.
Remaining system H' = (E - E_c) with P removed; its freedom F' = |words - P| - |E - E_c|.
Claim (DERIVED): H' has an empty 2-core only if E_c contains the whole 2-core of H, and then F' <= 0.
Test: random promotions built from random equation sets (grown along shared words), for every triple.
Usage: python promo_check.py <trials>
"""
import itertools
import random
import sys

from build import system
from cores import incid, plain_core


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    rng = random.Random(3)
    outs = ["out0", "out2", "out5", "out7"]
    for S in itertools.combinations(outs, 3):
        eqs, const, _ = system(held=S)
        E, occ = incid(eqs, const)
        core = plain_core(E, occ, set(range(len(eqs))))
        stats = {"empty_core": 0, "max_Fprime_when_empty": None, "violations": 0, "max_Fprime": -999}
        for t in range(trials + 1):
            if t == trials:
                seed = set(core)                       # promote exactly the core equations
            else:
                seed = set(rng.sample(sorted(core), rng.randint(1, len(core))))
                if rng.random() < 0.5:                 # sometimes grow a connected chunk instead
                    seed = {rng.choice(sorted(core))}
                    for _ in range(rng.randint(1, 110)):
                        w = rng.choice(sorted(set().union(*(E[i] for i in seed))))
                        seed.add(rng.choice(occ[w]))
            P = set().union(*(E[i] for i in seed))
            Ec = {i for i in range(len(eqs)) if E[i] <= P}
            rest = [frozenset(E[i] - P) for i in range(len(eqs)) if i not in Ec]
            occ2 = {}
            for j, e in enumerate(rest):
                for v in e:
                    occ2.setdefault(v, []).append(j)
            Fp = len(occ2) - len(rest)
            c2 = plain_core(rest, occ2, set(range(len(rest))))
            stats["max_Fprime"] = max(stats["max_Fprime"], Fp)
            if not c2:
                stats["empty_core"] += 1
                m = stats["max_Fprime_when_empty"]
                stats["max_Fprime_when_empty"] = Fp if m is None else max(m, Fp)
                if Fp > 0 or not core <= Ec:
                    stats["violations"] += 1
        print(f"held={','.join(S)} trials={trials + 1}: {stats}", flush=True)


if __name__ == "__main__":
    main()
