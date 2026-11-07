"""Word-level solving orders for torus-symmetric families (shape_torus, 2026-10-08).

sigma = column shift by 2.  If the state Y after the round-1 columns is sigma-symmetric and the E messages are
paired (E0/E2: m1=m9, m11=m14; E1/E3: m12=m15, m5=m8), then the final state is symmetric and
out0=out2, out1=out3, out4=out6, out5=out7: the digest has 128 bits.  X (after round 0) need NOT be symmetric.
Variants (equalities added to the round-0 + round-1-column system of ../gd_order.py):
  Ysym     : Y_i = Y_sigma(i) (8) + 4 E-message pairs          -> 16 - 12 = 4 words of freedom, 128-bit digest
  Xsym     : X_i = X_sigma(i) (8) + 8 round-1 message pairs    -> 0 words (and empty for the real IV: parity)
  YsymA    : only the E0/E2 half: Y0=Y2,Y5=Y7,Y10=Y8,Y15=Y13, m1=m9, m11=m14 -> out0=out2,out5=out7 (10 words)
  YsymA_fixB: YsymA and E1,E3 inputs held constant (idea 1 on half B): digest 64 bits
Usage: python torus_gd.py <variant> <runs> <seed>
"""
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from ring_gd import gd_run  # noqa: E402
from dm import dm_blocks  # noqa: E402

PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def sig(i):
    return 4 * (i // 4) + (i % 4 + 2) % 4


def build(variant):
    eqs, const = [], set()
    state = [f"init{i}" for i in range(16)]
    const.update(state)
    msg = [f"m{i}" for i in range(16)]

    def G(name, idx, x, y):
        a, b, c, d = (state[i] for i in idx)
        a1, d1, c1, b1, a2, d2, c2, b2 = (f"{name}.{t}" for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2"))
        eqs.extend([(f"{name}:a1", (a1, a, b, x)), (f"{name}:d1", (d1, d, a1)), (f"{name}:c1", (c1, c, d1)),
                    (f"{name}:b1", (b1, b, c1)), (f"{name}:a2", (a2, a1, b1, y)), (f"{name}:d2", (d2, d1, a2)),
                    (f"{name}:c2", (c2, c1, d2)), (f"{name}:b2", (b2, b1, c2))])
        for i, v in zip(idx, (a2, b2, c2, d2)):
            state[i] = v

    for j, idx in enumerate(COLS):
        G(f"K{j}", idx, msg[2 * j], msg[2 * j + 1])
    for j, idx in enumerate(DIAG):
        G(f"D{j}", idx, msg[8 + 2 * j], msg[9 + 2 * j])
    X = list(state)
    s = [msg[PERM[i]] for i in range(16)]
    for j, idx in enumerate(COLS):
        G(f"C{j}", idx, s[2 * j], s[2 * j + 1])
    Y = list(state)
    pairs = []
    if variant == "Ysym":
        pairs += [(Y[i], Y[sig(i)]) for i in range(16) if sig(i) > i]
        pairs += [("m1", "m9"), ("m11", "m14"), ("m12", "m15"), ("m5", "m8")]
    elif variant == "Xsym":
        pairs += [(X[i], X[sig(i)]) for i in range(16) if sig(i) > i]
        pairs += [("m2", "m7"), ("m6", "m0"), ("m3", "m4"), ("m10", "m13"), ("m1", "m9"), ("m11", "m14"),
                  ("m12", "m15"), ("m5", "m8")]
    elif variant in ("YsymA", "YsymA_fixB"):
        pairs += [(Y[0], Y[2]), (Y[5], Y[7]), (Y[10], Y[8]), (Y[15], Y[13]), ("m1", "m9"), ("m11", "m14")]
        if variant == "YsymA_fixB":
            for i in (1, 6, 11, 12, 3, 4, 9, 14):
                const.add(Y[i])
            const.update(["m12", "m5", "m15", "m8"])
    else:
        raise ValueError(variant)
    for k, (u, v) in enumerate(pairs):
        eqs.append((f"out_eq{k}", (u, v)))
    vars_ = sorted({v for _, vs in eqs for v in vs} - const)
    return eqs, const, vars_


def main():
    variant, runs, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    eqs, const, vars_ = build(variant)
    F = len(vars_) - len(eqs)
    rng = random.Random(seed)
    hist = {}
    best = None
    for _ in range(runs):
        g, solved, checks, anc = gd_run(eqs, const, vars_, rng)
        hist[len(g)] = hist.get(len(g), 0) + 1
        if best is None or len(g) < len(best[0]):
            best = (g, checks)
    g, checks = best
    lines = [f"{variant}: {len(vars_)} unknown words, {len(eqs)} equations, freedom {F} words",
             f"  guess-count histogram {dict(sorted(hist.items()))}",
             f"  best {len(g)} guesses -> {len(g) - F} checks; guesses {g}",
             f"  check equations {[n for n, _ in checks]}"]
    # DM core for index = the first F guesses that leave a structurally regular square system
    import itertools
    cores = []
    for idx in (itertools.islice(itertools.combinations(g, F), 400) if F > 0 else []):
        bl = dm_blocks(eqs, const, vars_, idx)
        if bl is None:
            continue
        cores.append(max(len(b[0]) for b in bl))
    if cores:
        lines.append(f"  DM largest block over index choices from the best order: min {min(cores)}, max {max(cores)}")
    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(HERE, f"torus_gd_{variant}.txt"), "w") as fh:
        fh.write(txt + "\n")


if __name__ == "__main__":
    main()
