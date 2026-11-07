"""Solving-order search with precomputed tables and promoted constants (main session, Pivot, 2026-10-08).

Memory is free and preprocessing up to ~2^85 is negligible in this cost model, so a G call whose external words
include k family constants has 6 - k degrees of freedom; when 6 - k <= 2, ANY 6 - k known words of it determine
the rest through a table of at most 2^64 entries built once per family (enumerate the free words, store by the
known ones).  Special cycles with constant parameters (C0/C2: input c -> d1; C1/C3: input b -> c1) are kept.

"Promoting" p words makes them constants of a sub-family: the sub-family keeps 4 - p words of freedom (fixed
variant), and the extra constants may turn more calls into table lookups.  checks = min guesses - (4 - p).
A sub-family of 2^64 members (p = 2) is enough for the birthday.
Usage: python gd_promote.py <fixed|outhalf> <p> <runs> [pool: msg|msgX]
"""
import itertools
import random
import sys

from gd_order import build


def calls_of(eqs):
    calls = {}
    for name, vs in eqs:
        if ":" in name:
            call, role = name.split(":")
            calls.setdefault(call, {})[role] = vs
    return calls


def macros_for(eqs, const):
    out = []
    for call, e in calls_of(eqs).items():
        a, b, x = e["a1"][1], e["a1"][2], e["a1"][3]
        d, c, y = e["d1"][1], e["c1"][1], e["a2"][3]
        a1, d1, c1, b1 = e["a1"][0], e["d1"][0], e["c1"][0], e["b1"][0]
        a2, d2, c2, b2 = e["a2"][0], e["d2"][0], e["c2"][0], e["b2"][0]
        ext = [a, b, c, d, x, y, a2, b2, c2, d2]
        allw = [w for w in ext + [a1, d1, c1, b1] if w not in const]
        unk = [w for w in ext if w not in const]
        dof = 6 - (len(ext) - len(unk))
        if dof <= 0:
            out.extend(((), t) for t in allw)
        elif dof <= 2:
            for trig in itertools.combinations(unk, dof):
                out.extend((trig, t) for t in allw if t not in trig)
        if a2 in const and c2 in const and c not in const:
            out.append(((c,), d1))
        if b2 in const and d2 in const and b not in const:
            out.append(((b,), c1))
    return out


def solve(eqs, macros, known, rng):
    """Greedy guess-and-determine; returns the guesses."""
    eq_vars = [vs for _, vs in eqs]
    allv = {v for vs in eq_vars for v in vs} | {t for _, t in macros}
    guesses = []

    def prop():
        changed = True
        while changed:
            changed = False
            for vs in eq_vars:
                unk = [v for v in vs if v not in known]
                if len(unk) == 1:
                    known.add(unk[0])
                    changed = True
            for trig, t in macros:
                if t not in known and all(w in known for w in trig):
                    known.add(t)
                    changed = True

    prop()
    while not allv <= known:
        cand = {}
        for vs in eq_vars:
            unk = [v for v in vs if v not in known]
            if len(unk) == 2:
                for v in unk:
                    cand[v] = cand.get(v, 0) + 1
        for trig, t in macros:
            if t in known:
                continue
            unk = [w for w in trig if w not in known]
            if len(unk) == 1:
                cand[unk[0]] = cand.get(unk[0], 0) + 1
        if not cand:
            cand = {v: 1 for v in allv - known}
        best = max(cand.values())
        pool = [v for v, n in cand.items() if n >= best - rng.choice((0, 0, 1))]
        g = rng.choice(pool)
        known.add(g)
        guesses.append(g)
        prop()
    return guesses


def main():
    variant, p, runs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    pool_kind = sys.argv[4] if len(sys.argv) > 4 else "msg"
    eqs, const, vars_ = build(variant, "len64")
    pool = [v for v in vars_ if v.startswith("m")]
    if pool_kind == "msgX":
        pool += [v for v in vars_ if v.startswith("D") and v.split(".")[1] in ("a2", "b2", "c2", "d2")]
        pool += [v for v in vars_ if v.startswith("K") and v.split(".")[1] in ("a2", "b2", "c2", "d2")]
    rng = random.Random(7)
    results = []
    for prom in itertools.combinations(sorted(pool), p):
        c2 = set(const) | set(prom)
        mac = macros_for(eqs, c2)
        freedom = len([v for v in vars_ if v not in c2]) - len(eqs)
        best = None
        for _ in range(runs):
            g = solve(eqs, mac, set(c2), rng)
            if best is None or len(g) < len(best):
                best = g
        results.append((len(best) - freedom, len(best), prom, best))
    results.sort(key=lambda r: (r[0], r[1]))
    fn = f"promote_{variant}_p{p}_{pool_kind}.txt"
    with open(fn, "w") as fh:
        for chk, g, prom, best in results:
            fh.write(f"checks={chk} guesses={g} promoted={list(prom)} guessed={best}\n")
    hist = {}
    for r in results:
        hist[r[0]] = hist.get(r[0], 0) + 1
    print(f"{variant} p={p} pool={pool_kind}: {len(results)} sets; checks histogram {dict(sorted(hist.items()))}")
    for r in results[:3]:
        print(f"  checks={r[0]} promoted={list(r[2])} guessed={r[3]}")


if __name__ == "__main__":
    main()
