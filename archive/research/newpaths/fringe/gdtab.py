"""Free-memory tables of whole G calls (2^64 entries, 2^64 preprocessing each).

A G call whose four state INPUTS are family constants (K calls) or whose four state OUTPUTS are family constants
(E0, E2 in the 'eout' variant) is a 2-dimensional relation in its six free ports (x, y and the four other state
words): tabulate it over its two free dimensions (2^64 entries) and any 2 known ports give the other 4 (one
lookup, ~1 solution expected).  Calls with one more constant port (e.g. K0 with m1 fixed) are 1-dimensional:
any 1 known port gives the rest (2^32 table).  Rules {p,q} -> r (or {p} -> r) are added to the plain model.
Usage: python gdtab.py <gdv variant> [runs] [seed] [--export] [--cv]
  --cv : also the table-backed chaining value of gdcv.py (2-block message)
"""
import itertools
import random
import sys

sys.dont_write_bytecode = True
from gdv import build, make_index  # noqa: E402
from gdcv import run as run_rules, make_rules  # noqa: E402


def call_ports(raw):
    calls = {}
    for name, vs in raw:
        if ":" in name:
            c, part = name.split(":")
            calls.setdefault(c, {})[part] = vs
    out = {}
    for c, e in calls.items():
        a, b, x = e["a1"][1], e["a1"][2], e["a1"][3]
        d, cc, y = e["d1"][1], e["c1"][1], e["a2"][3]
        outs = (e["a2"][0], e["b2"][0], e["c2"][0], e["d2"][0])
        out[c] = ((a, b, cc, d), (x, y), outs)
    return out


def table_rules(raw, const):
    """Only calls whose state inputs or state outputs are all constants.  Words the call's own equations already
    give from the constants (plain propagation) are removed first: they are not free coordinates (bug found in the
    first version: E0 with constant outputs gives b and c for free, and the pair (b, c) then fired the table)."""
    rules, info = [], []
    ceqs = {}
    for name, vs in raw:
        if ":" in name:
            ceqs.setdefault(name.split(":")[0], []).append(vs)
    for c, (ins, xy, outs) in sorted(call_ports(raw).items()):
        if not (all(v in const for v in ins) or all(v in const for v in outs)):
            continue
        known = set(v for vs in ceqs[c] for v in vs if v in const)
        ch = True
        while ch:
            ch = False
            for vs in ceqs[c]:
                u = [v for v in vs if v not in known]
                if len(u) == 1:
                    known.add(u[0])
                    ch = True
        U = {v for vs in ceqs[c] for v in vs if v not in known}
        R = [vs for vs in ceqs[c] if any(v in U for v in vs)]
        dim = len(U) - len(R)
        ports = [v for v in ins + xy + outs if v in U]
        if dim < 1 or dim > 2:
            continue
        def cl(start):
            k = set(known) | set(start)
            ch2 = True
            while ch2:
                ch2 = False
                for vs in ceqs[c]:
                    u = [v for v in vs if v not in k]
                    if len(u) == 1:
                        k.add(u[0])
                        ch2 = True
            return k
        info.append(f"{c}:{dim}")
        for trig in itertools.combinations(ports, dim):
            # a pair is a valid table key only if neither word already gives the other (e.g. E0 with constant
            # outputs: d and y both fix a1, so (d, y) is not a coordinate pair)
            if dim == 2 and (trig[1] in cl([trig[0]]) or trig[0] in cl([trig[1]])):
                continue
            for r in ports:
                if r not in trig:
                    rules.append((trig, r))
    return rules, info


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    variant = args[0]
    runs = int(args[1]) if len(args) > 1 else 3000
    seed = int(args[2]) if len(args) > 2 else 1
    cv = "--cv" in sys.argv
    eqs, const, vars_, H, raw = build(variant, "len64", tuple(range(8)) if cv else (), want_raw=True)
    rules, info = table_rules(raw, const)
    if cv:
        rules += make_rules(2, [f"init{i}" for i in range(8)])
    occ = make_index(eqs, vars_)
    occR = {}
    for r, (tr, _) in enumerate(rules):
        for v in tr:
            occR.setdefault(v, []).append(r)
    free = len(vars_) - len(eqs) - (6 if cv else 0)
    tag = f"{variant}tab{'cv' if cv else ''}"
    if "--export" in sys.argv:
        ix = {v: i for i, v in enumerate(vars_)}
        fn = f"rules_{tag}_len64.txt"
        with open(fn, "w", newline="\n") as fh:
            fh.write(f"{len(vars_)} {len(eqs)} {len(rules)}\n")
            fh.write(" ".join(vars_) + "\n")
            for _, vs in eqs:
                fh.write(" ".join(str(ix[v]) for v in vs) + "\n")
            for tr, r in rules:
                fh.write(" ".join(str(ix[v]) for v in (r,) + tuple(tr)) + "\n")
        print(f"{fn}: {len(vars_)} vars {len(eqs)} eqs {len(rules)} rules; tabled calls {info}; freedom {free}")
        return
    rng = random.Random(seed)
    hist, best = {}, None
    for _ in range(runs):
        g, steps = run_rules(eqs, occ, rules, occR, vars_, rng)
        hist[len(g)] = hist.get(len(g), 0) + 1
        if best is None or len(g) < len(best[0]):
            best = (g, steps)
    g, steps = best
    print(f"{tag}: {len(vars_)} unknowns, {len(eqs)} eqs, {len(rules)} table rules, tabled calls {info}, "
          f"freedom {free}; greedy {runs}: {dict(sorted(hist.items()))}")
    print(f"  best {len(g)} guesses -> {len(g) - free} checks; guesses {g}")


if __name__ == "__main__":
    main()
