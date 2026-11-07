"""Guess-and-determine order search over more family variants (word level, same model as ../gd_order.py:
every G call split into 8 primitive equations, each solvable for any one unknown word).

New variants (half A = E0,E2 -> out0,2,5,7; half B = E1,E3 -> out1,3,4,6):
  fixed[A|B]     E-inputs of the half held constant (12 words)                       = ../gd_order 'fixed' for A
  plus[A|B]      sum absorption: E0 output depends on (Y0+m1, Y5, Y10, Y15, m11) only, since a and x enter
                 G only through a1 = a+b+x.  Hold the 5+5 effective inputs constant (10 words)
  eout[A|B]      hold the 8 output words of the half's two E calls constant (8 words)
  outhalf[A|B]   hold only the half's 4 output words constant (4 words)             = ../gd_order 'outhalf' for A
  symAB          internal symmetry: effective inputs of E0 equal those of E2 and E1's equal E3's (10 relations).
                 Then out0=out2, out5=out7, out1=out3, out4=out6: output has 128 bits
  symA_outB      E0 eff. inputs = E2 eff. inputs (5 relations, out_A has 64 bits) and out1,3,4,6 constant (4)
  symB_outA      mirror
checks = guesses - freedom.  Output entropy H (bits); birthday needs 2^(H/2) family members.
Usage: python gdv.py <variant> [runs] [seed] [len64|len55]
"""
import random
import sys

sys.dont_write_bytecode = True
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
# E call j reads Y at DIAG[j] and message words EMSG[j] (x, y)
EMSG = [(1, 11), (12, 5), (9, 14), (15, 8)]
HALF = {"A": (0, 2), "B": (1, 3)}
OUTW = {"A": (0, 2, 5, 7), "B": (1, 3, 4, 6)}
H_BITS = {"fixed": 128, "plus": 128, "eout": 128, "outhalf": 128, "symAB": 128, "symA_outB": 64, "symB_outA": 64}


def build(variant, length="len64", free_init=(), want_raw=False):
    """free_init: indices of initial-state words treated as unknowns (diagnostic only; in the real function they
    are IV / counter / length / flags constants)."""
    eqs, const = [], set()
    state = [f"init{i}" for i in range(16)]
    const.update(s for i, s in enumerate(state) if i not in free_init)
    msg = [f"m{i}" for i in range(16)]
    if length == "len55":
        const.update(["m14", "m15"])

    def G(name, idx, x, y):
        a, b, c, d = (state[i] for i in idx)
        a1, d1, c1, b1, a2, d2, c2, b2 = (f"{name}.{t}" for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2"))
        eqs.extend([(f"{name}:a1", (a1, a, b, x)), (f"{name}:d1", (d1, d, a1)), (f"{name}:c1", (c1, c, d1)),
                    (f"{name}:b1", (b1, b, c1)), (f"{name}:a2", (a2, a1, b1, y)), (f"{name}:d2", (d2, d1, a2)),
                    (f"{name}:c2", (c2, c1, d2)), (f"{name}:b2", (b2, b1, c2))])
        for i, v in zip(idx, (a2, b2, c2, d2)):
            state[i] = v

    s = msg
    for j, idx in enumerate(COLS):
        G(f"K{j}", idx, s[2 * j], s[2 * j + 1])
    for j, idx in enumerate(DIAG):
        G(f"D{j}", idx, s[8 + 2 * j], s[9 + 2 * j])
    s = [msg[PERM[i]] for i in range(16)]
    for j, idx in enumerate(COLS):
        G(f"C{j}", idx, s[2 * j], s[2 * j + 1])
    Y = list(state)

    def einputs(j):
        return [Y[i] for i in DIAG[j]] + [msg[k] for k in EMSG[j]]

    def add_E(j):
        G(f"E{j}", DIAG[j], msg[EMSG[j][0]], msg[EMSG[j][1]])

    def out_rel(h):
        for i in OUTW[h]:
            eqs.append((f"out{i}", (state[i], state[i + 8])))

    def plus_half(h):
        for j in HALF[h]:
            a, b, c, d, x, y = einputs(j)
            sname = f"s{j}"
            const.update([sname, b, c, d, y])
            eqs.append((f"sum{j}", (sname, a, x)))

    def sym_half(h):
        j, k = HALF[h]
        u, v = einputs(j), einputs(k)
        aux = f"sym{j}{k}"
        eqs.append((f"symsum{j}{k}a", (aux, u[0], u[4])))
        eqs.append((f"symsum{j}{k}b", (aux, v[0], v[4])))
        for p, q, nm in zip(u[1:4] + [u[5]], v[1:4] + [v[5]], "bcdy"):
            eqs.append((f"symeq{j}{k}{nm}", (p, q)))

    base = variant.rstrip("AB") if variant[-1] in "AB" and not variant.startswith("sym") else variant
    h = variant[-1] if base != variant else None
    if base == "fixed":
        for j in HALF[h]:
            const.update(einputs(j))
    elif base == "plus":
        plus_half(h)
    elif base == "eout":
        for j in HALF[h]:
            add_E(j)
        for j in HALF[h]:
            const.update(state[i] for i in DIAG[j])
    elif base == "outhalf":
        for j in HALF[h]:
            add_E(j)
        out_rel(h)
    elif variant == "symAB":
        sym_half("A")
        sym_half("B")
    elif variant in ("symA_outB", "symB_outA"):
        hs, ho = variant[3], variant[-1]
        sym_half(hs)
        for j in HALF[ho]:
            add_E(j)
        out_rel(ho)
    else:
        raise SystemExit("unknown variant " + variant)
    raw = list(eqs)
    eqs = [(n, tuple(v for v in vs if v not in const)) for n, vs in eqs]
    eqs = [(n, vs) for n, vs in eqs if vs]
    vars_ = sorted({v for _, vs in eqs for v in vs})
    if want_raw:
        return eqs, const, vars_, H_BITS[base if base in H_BITS else variant], raw
    return eqs, const, vars_, H_BITS[base if base in H_BITS else variant]


def make_index(eqs, vars_):
    occ = {v: [] for v in vars_}
    for k, (_, vs) in enumerate(eqs):
        for v in vs:
            occ[v].append(k)
    return occ


def propagate(eqs, occ, known, unk, queue, steps):
    while queue:
        k = queue.pop()
        if unk[k] != 1:
            continue
        for v in eqs[k][1]:
            if v not in known:
                known.add(v)
                steps.append(("solve", eqs[k][0], v))
                for k2 in occ[v]:
                    unk[k2] -= 1
                    if unk[k2] == 1:
                        queue.append(k2)
                break


def run(eqs, occ, vars_, rng):
    known, steps, guesses = set(), [], []
    unk = [len(vs) for _, vs in eqs]
    queue = [k for k in range(len(eqs)) if unk[k] == 1]
    propagate(eqs, occ, known, unk, queue, steps)
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
        known.add(g)
        guesses.append(g)
        steps.append(("guess", "", g))
        q = []
        for k2 in occ[g]:
            unk[k2] -= 1
            if unk[k2] == 1:
                q.append(k2)
        propagate(eqs, occ, known, unk, q, steps)
    return guesses, steps


def main():
    variant = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    length = sys.argv[4] if len(sys.argv) > 4 else "len64"
    free_init = tuple(int(x) for x in sys.argv[5].split(",")) if len(sys.argv) > 5 else ()
    eqs, const, vars_, H = build(variant, length, free_init)
    if free_init:
        variant = f"{variant}_free{'-'.join(map(str, free_init))}"
    occ = make_index(eqs, vars_)
    free = len(vars_) - len(eqs)
    rng = random.Random(seed)
    hist, best = {}, None
    for _ in range(runs):
        g, steps = run(eqs, occ, vars_, rng)
        hist[len(g)] = hist.get(len(g), 0) + 1
        if best is None or len(g) < len(best[0]):
            best = (g, steps)
    g, steps = best
    c = len(g) - free
    print(f"{variant} {length}: {len(vars_)} unknown words, {len(eqs)} eqs, freedom {free} words, "
          f"output entropy {H} bits; greedy runs {runs}: hist {dict(sorted(hist.items()))}")
    print(f"  best {len(g)} guesses -> {c} checks; naive cost per member 2^{32 * c}, "
          f"members needed 2^{H // 2}, naive total 2^{H // 2 + 32 * c}; two-list join (if separable) "
          f"~2^{(H // 2 + 32 * c) / 2 + 1:.0f}")
    print("  guesses:", g)
    with open(f"gdv_best_{variant}_{length}.txt", "w") as fh:
        for s in steps:
            fh.write(f"{s[0]:5s} {s[1]:12s} {s[2]}\n")


if __name__ == "__main__":
    main()
