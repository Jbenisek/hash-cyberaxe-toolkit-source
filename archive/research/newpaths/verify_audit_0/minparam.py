"""For the look-solve in the 7-guess look cover (z = C0.a1 after K2.c1 K3.d1 K3.d2 C3.a2 m0 D1.d1 K2.d2): the smallest
set P of known per-instance words such that guessing z with only constants + P known, then propagating plainly,
gives a check on z.  |P| = 0 -> 2^32 table, |P| = 1 -> 2^64 table (both within budget), |P| >= 2 -> per-instance
solve (~2^32 by enumeration) or a >= 2^96 table.  Searches |P| <= 3 exhaustively."""
import itertools
import os

from pairs0 import load, plain

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    nv, names, eqs = load(os.path.join(HERE, "sys_fixed.txt"))
    ix = {n: i for i, n in enumerate(names)}
    G = "K2.c1 K3.d1 K3.d2 C3.a2 m0 D1.d1 K2.d2".split()
    K = plain(eqs, {ix[g] for g in G})
    z = ix["C0.a1"]
    lines = [f"plain closure of the 7 guesses: {len(K)} words; z = C0.a1"]
    Kl = sorted(K)
    found = None
    for r in range(0, 4):
        for P in itertools.combinations(Kl, r):
            A = plain(eqs, set(P) | {z})
            base = plain(eqs, set(P))
            newc = sum(1 for e in eqs if e <= A) - sum(1 for e in eqs if e <= base)
            if newc >= len(A) - len(base):
                found = [names[p] for p in P]
                break
        lines.append(f"|P| = {r}: {'pinned with P = ' + str(found) if found else 'no P of this size pins z'}")
        if found:
            break
    print("\n".join(lines))
    open(os.path.join(HERE, "minparam.log"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
