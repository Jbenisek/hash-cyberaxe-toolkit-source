"""Table-backed chaining value (two-block messages), guess-and-determine model.

Block 2 of a 2-block message starts from v0..v7 = CV = first 8 output words of block 1 (flags CHUNK_START);
v8..v15 are constants (IV0..3, counter 0, block length, flags CHUNK_END|ROOT).  Memory is free and 2^(32t)
preprocessing is cheap for t <= 2 (2^64) or t = 2.75 (2^88): hash 2^(32t) random first blocks and index the CVs
by any t chosen CV words.  Then 'any t CV words known -> all 8 CV words known' (one lookup, ~1 hit expected).
So the CV is a block of 8 unknown words with dimension t: rules {p,q} -> r for every pair p,q (t = 2).
freedom = (unknowns - equations) - (8 - t).
Usage: python gdcv.py <gdv variant> [runs] [seed] [t=2] [--export]
"""
import itertools
import random
import sys

sys.dont_write_bytecode = True
from gdv import build, make_index  # noqa: E402


def make_rules(t, cvn):
    rules = []
    for trig in itertools.combinations(cvn, t):
        for r in cvn:
            if r not in trig:
                rules.append((trig, r))
    return rules


def run(eqs, occ, rules, occR, vars_, rng):
    known, steps, guesses = set(), [], []
    unk = [len(vs) for _, vs in eqs]
    rmiss = [len(tr) for tr, _ in rules]

    def learn(v, why, queue):
        known.add(v)
        steps.append(why + (v,))
        for k2 in occ[v]:
            unk[k2] -= 1
            if unk[k2] == 1:
                queue.append(("e", k2))
        for r in occR.get(v, ()):
            rmiss[r] -= 1
            if rmiss[r] == 0:
                queue.append(("r", r))

    def prop(queue):
        while queue:
            kind, k = queue.pop()
            if kind == "e":
                if unk[k] != 1:
                    continue
                v = next(x for x in eqs[k][1] if x not in known)
                learn(v, ("solve", eqs[k][0]), queue)
            else:
                v = rules[k][1]
                if v not in known:
                    learn(v, ("table", "CV"), queue)

    q = [("e", k) for k in range(len(eqs)) if unk[k] == 1]
    prop(q)
    while len(known) < len(vars_):
        cand = {}
        for k, (_, vs) in enumerate(eqs):
            if unk[k] == 2:
                for v in vs:
                    if v not in known:
                        cand[v] = cand.get(v, 0) + 1
        if not cand:
            cand = {v: 1 for v in vars_ if v not in known}
        best = max(cand.values())
        pool = [v for v, c in cand.items() if c >= best - rng.choice((0, 0, 1))]
        g = rng.choice(pool)
        guesses.append(g)
        q = []
        learn(g, ("guess", ""), q)
        prop(q)
    return guesses, steps


def main():
    variant = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    t = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    eqs, const, vars_, H = build(variant, "len64", tuple(range(8)))
    cvn = [f"init{i}" for i in range(8)]
    rules = make_rules(t, cvn)
    occ = make_index(eqs, vars_)
    occR = {}
    for r, (tr, _) in enumerate(rules):
        for v in tr:
            occR.setdefault(v, []).append(r)
    free = len(vars_) - len(eqs) - (8 - t)
    if "--export" in sys.argv:
        ix = {v: i for i, v in enumerate(vars_)}
        fn = f"rules_{variant}cv{t}_len64.txt"
        with open(fn, "w", newline="\n") as fh:
            fh.write(f"{len(vars_)} {len(eqs)} {len(rules)}\n")
            fh.write(" ".join(vars_) + "\n")
            for _, vs in eqs:
                fh.write(" ".join(str(ix[v]) for v in vs) + "\n")
            for tr, r in rules:
                fh.write(" ".join(str(ix[v]) for v in (r,) + tuple(tr)) + "\n")
        print(f"{fn}: {len(vars_)} vars {len(eqs)} eqs {len(rules)} rules, freedom {free}")
        return
    rng = random.Random(seed)
    hist, best = {}, None
    for _ in range(runs):
        g, steps = run(eqs, occ, rules, occR, vars_, rng)
        hist[len(g)] = hist.get(len(g), 0) + 1
        if best is None or len(g) < len(best[0]):
            best = (g, steps)
    g, steps = best
    c = len(g) - free
    print(f"{variant}+CVtable(t={t}): {len(vars_)} unknowns, {len(eqs)} eqs, CV block dim {t}, freedom {free} words; "
          f"greedy {runs}: hist {dict(sorted(hist.items()))}")
    print(f"  best {len(g)} guesses -> {c} checks; guesses: {g}")
    with open(f"gdcv_best_{variant}_t{t}.txt", "w") as fh:
        for s in steps:
            fh.write(" ".join(map(str, s)) + "\n")


if __name__ == "__main__":
    main()
