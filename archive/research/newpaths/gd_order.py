"""Guess-and-determine search for a solving order of 2-round BLAKE3 (single block, fixed IV).

Each G call is split into its eight primitive equations; each primitive equation links 3 or 4 words and can be
solved for any one of them once the others are known (additions and xor-rotations are invertible in each
argument).  Given the constants (IV, counter, length, flags, the fixed message words and the fixed internal words
of the chosen variant), find the fewest words to guess so that propagation determines everything.

checks = guesses - freedom.  A sampler with checks == 0 produces one family member per guess at O(1) cost.
Variants:
  fixed   : inputs of E0 and E2 fixed (Y0,Y5,Y10,Y15,Y2,Y7,Y8,Y13 and m1,m11,m9,m14)
  outhalf : only out0,out2,out5,out7 fixed (E0 and E2 included; out_i = v_i ^ v_{i+8})
Usage: python gd_order.py [fixed|outhalf] [len64|len55] [runs]
"""
import random
import sys

PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def build(variant, length):
    eqs = []          # list of (name, tuple of variables)
    const = set()
    state = [f"init{i}" for i in range(16)]
    const.update(state)
    msg = [f"m{i}" for i in range(16)]
    if length == "len55":
        const.update(["m14", "m15"])      # m13 top byte is zero: treated as free here (3 bytes)
    order = list(range(16))

    def G(name, idx, x, y):
        a, b, c, d = (state[i] for i in idx)
        a1, d1, c1, b1 = (f"{name}.{t}" for t in ("a1", "d1", "c1", "b1"))
        a2, d2, c2, b2 = (f"{name}.{t}" for t in ("a2", "d2", "c2", "b2"))
        eqs.extend([
            (f"{name}:a1", (a1, a, b, x)), (f"{name}:d1", (d1, d, a1)), (f"{name}:c1", (c1, c, d1)),
            (f"{name}:b1", (b1, b, c1)), (f"{name}:a2", (a2, a1, b1, y)), (f"{name}:d2", (d2, d1, a2)),
            (f"{name}:c2", (c2, c1, d2)), (f"{name}:b2", (b2, b1, c2)),
        ])
        for i, v in zip(idx, (a2, b2, c2, d2)):
            state[i] = v

    for r, pref in ((0, ("K", "D")), (1, ("C", "E"))):
        s = [msg[order[i]] for i in range(16)]
        for j, idx in enumerate(COLS):
            G(f"{pref[0]}{j}", idx, s[2 * j], s[2 * j + 1])
        if r == 1:
            ystate = list(state)
        if r == 0 or variant.startswith("outhalf"):
            skip = (0, 2) if variant == "outhalf13" else (1, 3)
            for j, idx in enumerate(DIAG):
                if r == 1 and j in skip:
                    continue
                G(f"{pref[1]}{j}", idx, s[8 + 2 * j], s[9 + 2 * j])
        order = [order[p] for p in PERM]

    # variants: fixed / outhalf hold the E0,E2 half (out0,2,5,7); fixed13 / outhalf13 the E1,E3 half (out1,3,4,6)
    if variant == "fixed":
        const.update(["m1", "m11", "m9", "m14"])
        for i in (0, 5, 10, 15, 2, 7, 8, 13):
            const.add(ystate[i])
    elif variant == "fixed13":
        const.update(["m12", "m5", "m15", "m8"])
        for i in (1, 6, 11, 12, 3, 4, 9, 14):
            const.add(ystate[i])
    else:
        for i in ((1, 3, 4, 6) if variant == "outhalf13" else (0, 2, 5, 7)):
            eqs.append((f"out{i}", (state[i], state[i + 8])))   # out_i fixed: two words, xor relation
    vars_ = sorted({v for _, vs in eqs for v in vs} - const)
    return eqs, const, vars_


def propagate(eqs, known, steps):
    changed = True
    while changed:
        changed = False
        for name, vs in eqs:
            unk = [v for v in vs if v not in known]
            if len(unk) == 1:
                known.add(unk[0])
                steps.append(("solve", name, unk[0]))
                changed = True


def run(eqs, const, vars_, rng):
    known = set(const)
    steps = []
    guesses = []
    propagate(eqs, known, steps)
    while len(known) < len(const) + len(vars_):
        # candidates: unknown words in equations with exactly two unknowns (a guess unlocks a solve)
        cand = {}
        for name, vs in eqs:
            unk = [v for v in vs if v not in known]
            if len(unk) == 2:
                for v in unk:
                    cand[v] = cand.get(v, 0) + 1
        if not cand:
            cand = {v: 1 for v in vars_ if v not in known}
        best = max(cand.values())
        pool = [v for v, c in cand.items() if c >= best - rng.choice((0, 0, 1))]
        g = rng.choice(pool)
        known.add(g)
        guesses.append(g)
        steps.append(("guess", "", g))
        propagate(eqs, known, steps)
    return guesses, steps


def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "fixed"
    length = sys.argv[2] if len(sys.argv) > 2 else "len64"
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
    eqs, const, vars_ = build(variant, length)
    freedom = len(vars_) - len(eqs)
    print(f"variant={variant} length={length}: {len(vars_)} unknown words, {len(eqs)} equations, "
          f"freedom {freedom} words")
    rng = random.Random(1)
    best = None
    hist = {}
    for _ in range(runs):
        g, steps = run(eqs, const, vars_, rng)
        hist[len(g)] = hist.get(len(g), 0) + 1
        if best is None or len(g) < len(best[0]):
            best = (g, steps)
    print("guess-count histogram:", dict(sorted(hist.items())))
    g, steps = best
    print(f"best: {len(g)} guesses -> {len(g) - freedom} checks of 32 bits")
    print("guessed words:", g)
    checks = [s for s in steps if s[0] == "solve"]
    used = {s[1] for s in checks}
    print("check equations (never used to solve):", [n for n, _ in eqs if n not in used])
    with open(f"gd_best_{variant}_{length}.txt", "w") as fh:
        for s in steps:
            fh.write(f"{s[0]:5s} {s[1]:10s} {s[2]}\n")


if __name__ == "__main__":
    main()
