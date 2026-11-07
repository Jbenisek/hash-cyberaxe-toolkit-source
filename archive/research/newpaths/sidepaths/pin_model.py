"""Word-level guess-and-determine model of the PINNED 55/63 family (message A), with E1 and E3 included.

Same primitive-equation model as ../gd_order.py: each G call = 8 equations, each solvable for any one unknown.
Constants: initial state, w4 = W4, w13 = W13, w14 = w15 = 0, the pins X3 = D3.a2, X7 = D2.b2, X11 = D1.c2,
X15 = D0.d2 (so C3 is entirely constant).  E1 and E3 of message A are included in full (they add as many
words as equations).  Family freedom must come out as 8 words.

usage: python pin_model.py check            -> sanity: the published basis closes everything
       python pin_model.py export T1,T2,.. out.model  -> gdx model with the listed words also constant
"""
import sys

PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def build(extra_diag=("E1", "E3")):
    eqs = []
    state = [f"init{i}" for i in range(16)]
    const = set(state)
    msg = [f"m{i}" for i in range(16)]
    const.update(["m4", "m13", "m14", "m15"])
    alias = {}

    def G(name, idx, x, y):
        a, b, c, d = (state[i] for i in idx)
        a1, d1, c1, b1, a2, d2, c2, b2 = (f"{name}.{t}" for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2"))
        eqs.extend([
            (f"{name}:a1", (a1, a, b, x)), (f"{name}:d1", (d1, d, a1)), (f"{name}:c1", (c1, c, d1)),
            (f"{name}:b1", (b1, b, c1)), (f"{name}:a2", (a2, a1, b1, y)), (f"{name}:d2", (d2, d1, a2)),
            (f"{name}:c2", (c2, c1, d2)), (f"{name}:b2", (b2, b1, c2)),
        ])
        for i, v in zip(idx, (a2, b2, c2, d2)):
            state[i] = v

    order = list(range(16))
    s = [msg[order[i]] for i in range(16)]
    for j, idx in enumerate(COLS):
        G(f"K{j}", idx, s[2 * j], s[2 * j + 1])
    for i in range(16):
        alias[f"S{i}"] = state[i]
    for j, idx in enumerate(DIAG):
        G(f"D{j}", idx, s[8 + 2 * j], s[9 + 2 * j])
    for i in range(16):
        alias[f"X{i}"] = state[i]
    const.update([alias["X3"], alias["X7"], alias["X11"], alias["X15"]])
    order = [order[p] for p in PERM]
    s = [msg[order[i]] for i in range(16)]
    for j, idx in enumerate(COLS):
        G(f"C{j}", idx, s[2 * j], s[2 * j + 1])
    for i in range(16):
        alias[f"Y{i}"] = state[i]
    for j, idx in enumerate(DIAG):
        if f"E{j}" in extra_diag:
            G(f"E{j}", idx, s[8 + 2 * j], s[9 + 2 * j])
    for i in range(16):
        alias.setdefault(f"w{i}", f"m{i}")
    # close the constants (C3 is fully constant)
    const = closure(eqs, set(const))
    vars_ = sorted({v for _, vs in eqs for v in vs} - const)
    eqs2 = [(n, vs) for n, vs in eqs if any(v not in const for v in vs)]
    return eqs2, const, vars_, alias


def closure(eqs, known, macros=()):
    known = set(known)
    changed = True
    while changed:
        changed = False
        for _, vs in eqs:
            unk = [v for v in vs if v not in known]
            if len(unk) == 1:
                known.add(unk[0])
                changed = True
    return known


def resolve(alias, names):
    return [alias.get(n, n) for n in names]


def t2_macros(eqs, const):
    """2^64-entry tables for round-0 column calls whose four state inputs are constants (K0, K1, K3; K2 has
    w4 constant and is 1-dimensional, plain propagation covers it).  In such a call every word is a function
    of (x, y); words in {x, a1, d1, c1, b1} depend on x only.  Any pair of words not both in that x-only group
    is a generically finite-to-one key: a table of 2^64 entries returns the whole call.  Preprocessing 2^64."""
    calls = {}
    for name, vs in eqs:
        if ":" in name:
            calls.setdefault(name.split(":")[0], {})[name.split(":")[1]] = vs
    macros = []
    for call in ("K0", "K1", "K3"):
        e = calls.get(call)
        if e is None:
            continue
        a, b, x = e["a1"][1], e["a1"][2], e["a1"][3]
        c, d, y = e["c1"][1], e["d1"][1], e["a2"][3]
        if not all(u in const for u in (a, b, c, d)):
            continue
        xonly = [x, e["a1"][0], e["d1"][0], e["c1"][0], e["b1"][0]]
        words = xonly + [y, e["a2"][0], e["d2"][0], e["c2"][0], e["b2"][0]]
        words = [w for w in words if w not in const]
        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                p, q = words[i], words[j]
                if p in xonly and q in xonly:
                    continue
                for w in words:
                    if w not in (p, q):
                        macros.append(((p, q), w))
    return macros


def closure_m(eqs, known, macros):
    known = set(known)
    changed = True
    while changed:
        changed = False
        for _, vs in eqs:
            unk = [v for v in vs if v not in known]
            if len(unk) == 1:
                known.add(unk[0])
                changed = True
        for trig, tgt in macros:
            if tgt not in known and all(t in known for t in trig):
                known.add(tgt)
                changed = True
    return known


def export(eqs, const, vars_, fn, extra_const=(), tables=0):
    macros = t2_macros(eqs, const) if tables else []
    const = closure_m(eqs, set(const) | set(extra_const), macros)
    vars2 = [v for v in vars_ if v not in const]
    ix = {v: i for i, v in enumerate(vars2)}
    rules = []
    for _, vs in eqs:
        nv = [ix[v] for v in vs if v not in const]
        if nv:
            rules.append((0, nv))
    for trig, tgt in macros:
        if tgt in const:
            continue
        tr = [ix[t] for t in trig if t not in const]
        if not tr:
            continue
        rules.append((1, tr + [ix[tgt]]))
    seen = {}
    reps = []
    for v in vars2:
        key = frozenset(closure_m(eqs, set(const) | {v}, macros))
        if key not in seen:
            seen[key] = v
            reps.append(ix[v])
    with open(fn, "w") as fh:
        fh.write(f"{len(vars2)} {len(rules)}\n")
        for t, nv in rules:
            fh.write(f"{t} {len(nv)} {' '.join(map(str, nv))}\n")
        fh.write(f"reps {len(reps)} {' '.join(map(str, reps))}\n")
    rules = [r for r in rules if r[0] == 0]
    with open(fn + ".vars", "w") as fh:
        fh.write("\n".join(vars2) + "\n")
    neq = len(rules)
    return len(vars2), neq, len(reps)


if __name__ == "__main__":
    eqs, const, vars_, alias = build()
    print(f"vars {len(vars_)} eqs {len(eqs)} freedom {len(vars_) - len(eqs)}")
    if sys.argv[1] == "check":
        basis = resolve(alias, ["C0.c1", "C0.d1", "D3.d1", "S15", "S9", "w5", "X2", "Y4"])
        print("basis", basis)
        cl = closure(eqs, set(const) | set(basis))
        miss = [v for v in vars_ if v not in cl]
        print("published basis closes everything:", not miss, "missing:", miss[:10])
        for drop in range(8):
            b2 = basis[:drop] + basis[drop + 1:]
            cl = closure(eqs, set(const) | set(b2))
            print("  without", basis[drop], "known", len(cl & set(vars_)), "of", len(vars_))
    elif sys.argv[1] == "export":
        tg = resolve(alias, [t for t in sys.argv[2].split(",") if t])
        tabs = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        n, r, nr = export(eqs, const, vars_, sys.argv[3], tg, tabs)
        print(f"{sys.argv[3]}: targets {tg} -> vars {n} eqs {r} freedom {n - r} reps {nr}")
