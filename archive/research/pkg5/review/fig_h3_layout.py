#!/usr/bin/env python3
# lens EVERY FIGURE: rule A at the very start of a run of proof.md 6.4, in the exact layout (CPU, one process per seed).
# One uniform word gives X2, X5, X6, X9; X1 = X10 = 0; contexts (X12, X13, X14) = (0, 0, c) for c = 0..NC-1 (the first
# contexts in the natural fixed order), alpha = 0..NA-1, all 65,536 members in order, seven per batch as in 6.5.
# Counts: trials that satisfy rule A, batches in which one does. h1 is computed forwards from the trial's words;
# for a sample of trials it is compared with the h1 of the full 2-round compression of message A (program's compress2).
# usage: fig_h3_layout.py SEEDTEXT NC NA

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import hashlib, importlib.util, math, struct, sys
P5 = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg5')
spec = importlib.util.spec_from_file_location("hs", P5 + "/blake3-r2/experiments/halfsearch.py")
hs = importlib.util.module_from_spec(spec); spec.loader.exec_module(hs)
seed, NC, NA = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
x2, x5, x6, x9 = struct.unpack("<4I", hashlib.shake_256(("fig h3 " + seed).encode()).digest(16))
M = hs.MASK
members = [hs.class_member(k) for k in range(hs.CLASS_SIZE)]
e1s = [(hs.Y3 + y) & M for y in members]
RULE = hs.RULE_A
def rule(h):
    return all(bin(h & m).count("1") & 1 == v for m, v in RULE)
tot = sat = batches = entered = checked = wrong = 0
per_loop = []
for c in range(NC):
    X, S, w = hs.context((0, x2, x5, x6, x9, 0, 0, 0, c))
    for alpha in range(NA):
        pre = hs.per_alpha(X, S, w, alpha)
        flags = []
        for k, y4 in enumerate(members):
            words, x1, x5n, y12 = hs.trial(X, S, w, alpha, y4, pre)
            v = (X[2] + X[6] + words[7]) & M
            d1 = hs.ror(X[14] ^ v, 16)
            c1 = (alpha + d1) & M
            b1 = hs.ror(X[6] ^ c1, 12)
            a2 = (v + b1 + words[0]) & M
            z = a2 ^ d1
            h1 = hs.ror(hs.ror(z, 8) ^ e1s[k], 16)
            f = rule(h1)
            flags.append(f)
            if k % 4099 == 0:                       # sample: against the full compression of message A
                wa, da, ya = hs.compress2(hs.messages(words)[0])
                ref = hs.ror(ya[14] ^ ((ya[3] + ya[4] + wa[15]) & M), 16)
                checked += 1; wrong += (ref != h1) or ya[4] != y4
        n = sum(flags)
        ent = sum(1 for j in range(hs.BATCHES) if any(flags[7 * j:7 * j + 7]))
        tot += len(flags); sat += n; batches += hs.BATCHES; entered += ent
        per_loop.append((n, ent))
p = 1 / 64
z = (sat - tot * p) / math.sqrt(tot * p * (1 - p))
ns = [n for n, _ in per_loop]; es = [e for _, e in per_loop]
print("seed %s: loops %d trials %d ; satisfy rule A %d = 2^%.4f (z %+.2f against 2^-6) ; batches %d entered %d = %.5f (budget 0.125, 7*2^-6 = 0.109375) ; "
      "per loop: trials min %d max %d (mean 1024 expected), entered min %d max %d of %d ; largest share of a loop %.5f ; h1 against compress2: %d checked, %d wrong" % (
          seed, len(per_loop), tot, sat, math.log2(sat / tot), z, batches, entered, entered / batches, min(ns), max(ns), min(es), max(es), hs.BATCHES,
          max(es) / hs.BATCHES, checked, wrong))
