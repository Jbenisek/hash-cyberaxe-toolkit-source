"""Does adding intermediate-sum words ever lower the minimum cover?  Random small systems with 4-word equations
(like o = p + q + r); each 4-word equation is split through a new word s (s = p + q, o = s + r, random pairing).
Brute-force kmin (plain and look, literal one-at-a-time definition) for the original and the split system.
Guesses in the split system may include the new words.  Prints the comparison; writes split_small.log."""
import itertools
import os
import random

from test_small import plain, look

HERE = os.path.dirname(os.path.abspath(__file__))


def rand_sys(rng):
    nv = rng.randint(6, 11)
    f = rng.randint(1, 4)
    ne = max(2, nv - f)
    eqs = []
    for _ in range(ne):
        k = rng.choice((3, 3, 4, 4))
        eqs.append(tuple(rng.sample(range(nv), k)))
    used = set().union(*map(set, eqs))
    for v in range(nv):
        if v not in used:
            eqs.append((v, rng.choice([u for u in range(nv) if u != v]), rng.choice([u for u in range(nv) if u != v])))
    return nv, eqs


def split(nv, eqs, rng):
    out = []
    n = nv
    for e in eqs:
        if len(e) == 4:
            e = list(e)
            rng.shuffle(e)
            s = n
            n += 1
            out.append(frozenset({s, e[0], e[1]}))
            out.append(frozenset({s, e[2], e[3]}))
        else:
            out.append(frozenset(e))
    return n, out


def kmin(eqs, nv, rng, on, cap):
    for k in range(cap + 1):
        for G in itertools.combinations(range(nv), k):
            if len(look(eqs, nv, set(G), rng, on)) == nv:
                return k
    return None


def main():
    rng = random.Random(4242)
    rows, worse, better, same = [], 0, 0, 0
    for t in range(150):
        nv, eqs = rand_sys(rng)
        fe = [frozenset(e) for e in eqs if len(set(e)) == len(e)]
        if len(fe) != len(eqs):
            continue
        n2, se = split(nv, eqs, rng)
        for on in (False, True):
            k1 = kmin(fe, nv, rng, on, 6)
            k2 = kmin(se, n2, rng, on, 6)
            if k1 is None or k2 is None:
                continue
            tag = "look" if on else "plain"
            if k2 < k1:
                better += 1
                rows.append(f"sys {t} {tag}: original kmin {k1}, split kmin {k2}  <-- split LOWER")
            elif k2 > k1:
                worse += 1
                rows.append(f"sys {t} {tag}: original kmin {k1}, split kmin {k2}  (split higher)")
            else:
                same += 1
    rows.append(f"comparisons: equal {same}, split lower {better}, split higher {worse}")
    print("\n".join(rows[-12:]))
    open(os.path.join(HERE, "split_small.log"), "w").write("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
