"""exp_words.py - message words m0..m11 of the blake3-r3 circuit: uses, op deltas under changes, diffusion. -> words_out.json"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from b3scan import *
OUT = os.path.dirname(__file__)
base = build(); T0 = time_log2(base.ops)
pos = word_positions(3)
res = {"base_ops": base.ops, "base_time_log2": T0, "words": {}}
rng = np.random.default_rng(21)
inputs = rand_inputs(256, 5)
def tl(o): return time_log2(o)
for i in range(12):
    w = {"id": i, "positions": pos[i]}
    # per-use op attribution: add ops in tags whose x/y operand is this word
    uses = []
    for (r, j, xy) in pos[i]:
        q = 1 if xy == "x" else 3
        c = base.by_tag.get((r, j, q), {})
        uses.append({"round": r, "call": j, "xy": xy, "step_ops": int(sum(c.values())), "step_adds": int(c.get("add", 0)), "step_masks": int(c.get("and", 0))})
    w["uses"] = uses
    modes = {}
    for label, mode in (("zero", "z"), ("var", "v"), ("const_9e3779b9", 0x9E3779B9), ("const_1", 1), ("const_ffffffff", 0xFFFFFFFF)):
        tr = build(words={i: mode})
        modes[label] = {"ops": tr.ops, "delta_ops": tr.ops - base.ops, "delta_time_log2": tl(tr.ops) - T0, "internal_masks": len(tr.masks_internal)}
    # correctness of the variants vs scalar for the nonzero-constant and var cases
    chk = {}
    for label, mode in (("const_9e3779b9", 0x9E3779B9), ("var", "v"), ("zero", "z")):
        tr = build(words={i: mode}, inputs=inputs)
        wm = {k: ("z" if k < 8 else "v") for k in range(16)}; wm[i] = mode
        bad = 0
        for s in range(60):
            m = [0 if wm[k] == "z" else (int(inputs[k][s]) if wm[k] == "v" else wm[k]) for k in range(16)]
            got = [int(tr.out[k].real[s]) & M32 if tr.out[k].c is None else tr.out[k].c for k in range(8)]
            if got != digest_words(m, 3): bad += 1
        chk[label] = bad
    w["modes"] = modes; w["scalar_check_mismatch_of_60"] = chk
    # diffusion: flip each bit of word i, mean digest bits changed
    perbit = []
    for b in range(32):
        tot = 0; minw = 8
        for _ in range(48):
            m = [0] * 8 + [int(rng.integers(0, 1 << 32)) for _ in range(8)]
            a = digest_words(m, 3); m2 = list(m); m2[i] ^= 1 << b; c2 = digest_words(m2, 3)
            tot += sum(bin(x ^ y).count("1") for x, y in zip(a, c2))
        perbit.append(tot / 48)
    w["flip_mean_bits_of_256"] = {"mean": sum(perbit) / 32, "min_bit": min(perbit), "max_bit": max(perbit)}
    # digest words never touched? (words changed on any flip)
    touched = [0] * 8
    for b in range(32):
        for _ in range(8):
            m = [0] * 8 + [int(rng.integers(0, 1 << 32)) for _ in range(8)]
            a = digest_words(m, 3); m2 = list(m); m2[i] ^= 1 << b; c2 = digest_words(m2, 3)
            for k in range(8):
                if a[k] != c2[k]: touched[k] += 1
    w["digest_word_changed_fraction"] = [t / 256 for t in touched]
    res["words"][str(i)] = w
# freeze combinations among chain words (ops only)
comb = {}
for subset in ([8], [9], [10], [11], [8, 9], [10, 11], [8, 9, 10, 11], list(range(8, 16))):
    tr = build(words={k: "z" for k in subset})
    comb["freeze_zero_" + "_".join(map(str, subset))] = {"ops": tr.ops, "delta_ops": tr.ops - base.ops, "delta_time_log2": tl(tr.ops) - T0}
res["freeze_chain_words"] = comb
# all-zero-word set as variables (target without the zero prefix)
tr = build(words={k: "v" for k in range(8)})
res["prefix_all_variable"] = {"ops": tr.ops, "delta_ops": tr.ops - base.ops, "delta_time_log2": tl(tr.ops) - T0}
json.dump(res, open(os.path.join(OUT, "words_out.json"), "w"), indent=1, default=str)
print("ok")
