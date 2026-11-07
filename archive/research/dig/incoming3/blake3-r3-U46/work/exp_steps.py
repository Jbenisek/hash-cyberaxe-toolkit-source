"""exp_steps.py - deterministic part of the blake3-r3 step/word scan. Writes steps_out.json and words_out.json."""
import json, sys, os
from fractions import Fraction
from math import factorial, comb
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from b3scan import *

OUT = os.path.dirname(__file__)
STEPS = [(2, 6, 3), (2, 6, 4), (2, 7, 1), (2, 7, 2), (2, 7, 3), (2, 7, 4)]
KINDS = ("add", "xor", "rot", "and")


def ih_tail(n, x):
    """P(sum of n iid U[0,1) >= x), exact Fraction; x Fraction."""
    if n == 0:
        return Fraction(1) if x <= 0 else Fraction(0)
    if x <= 0:
        return Fraction(1)
    if x >= n:
        return Fraction(0)
    F = Fraction(0)
    for k in range(int(x) + 1):
        F += (-1) ** k * comb(n, k) * (x - k) ** n
    F /= factorial(n)
    return 1 - F


def per_step(tr, tag):
    c = tr.by_tag.get(tag, {})
    return {k: int(c.get(k, 0)) for k in KINDS} | {"total": int(sum(c.values()))}


def variant_row(label, **kw):
    tr = build(**kw)
    lanes = kw.get("lanes", 7)
    row = {"label": label, "ops": tr.ops, "lanes": lanes,
           "ops_per_lane": tr.ops / lanes, "internal_masks": len(tr.masks_internal),
           "steps": {"R%dD%d.q%d" % (t[0], t[1] - 4, t[2]): per_step(tr, t)["total"] for t in STEPS}}
    return row


def main():
    res = {}
    base = build()
    res["base_ops"] = base.ops
    res["base_time_log2"] = time_log2(base.ops)
    res["per_step_round2"] = {"R2D%d.q%d" % (j - 4, q): per_step(base, (2, j, q)) for j in range(4, 8) for q in range(1, 5)}
    res["per_step_all_sum_check"] = sum(sum(c.values()) for t, c in base.by_tag.items() if t != "digest") + sum(base.by_tag["digest"].values())
    res["digest_ops"] = per_step(base, "digest")
    # which message word / position each round-2 call uses
    pos = word_positions(3)
    res["round2_words"] = {}
    for w, lst in pos.items():
        for (r, j, xy) in lst:
            if r == 2 and j >= 4:
                res["round2_words"].setdefault("D%d.%s" % (j - 4, xy), w)
    res["word_positions"] = {str(w): lst for w, lst in pos.items()}
    # add-chain data at the mask steps
    chains = {}
    for tag, v in base.adds:
        pass
    # ---- necessity: skip each step
    inputs = rand_inputs(256, 11)
    res["skip"] = {}
    for t in STEPS:
        tr = build(skip={t}, inputs=inputs)
        ok = check_vs_scalar(tr, inputs, 256, skip={t}, nchk=100)
        av = avalanche(skip={t}, n=1500, seed=5)
        res["skip"]["R%dD%d.q%d" % (t[0], t[1] - 4, t[2])] = {
            "ops": tr.ops, "delta_ops": tr.ops - base.ops, "time_log2": time_log2(tr.ops),
            "delta_time_log2": time_log2(tr.ops) - res["base_time_log2"],
            "tracer_vs_scalar_mismatch_of_100": ok, "mean_digest_bits_changed_of_256": av[0],
            "mean_equal_digest_words_of_8": av[1], "frac_inputs_with_any_equal_word": av[2],
            "internal_masks_left": len(tr.masks_internal)}
    # dead code check: backward reachability on emitted ops is by construction (every op feeds); verify via skip of the step's
    # output with all digest words changed -> done by avalanche. Also: skip all 24 round-2 steps one by one (table)
    res["skip_all_round2"] = {}
    for j in range(4, 8):
        for q in range(1, 5):
            t = (2, j, q)
            tr = build(skip={t})
            av = avalanche(skip={t}, n=300, seed=9)
            res["skip_all_round2"]["R2D%d.q%d" % (j - 4, q)] = {"delta_ops": tr.ops - base.ops, "bits_changed": av[0], "eq_words": av[1]}
    # ---- variants: mask policy none (all internal masks dropped)
    nm = build(policy="none", inputs=inputs)
    res["nomask"] = {"ops": nm.ops, "delta_ops": nm.ops - base.ops, "time_log2": time_log2(nm.ops),
                     "delta_time_log2": time_log2(nm.ops) - res["base_time_log2"],
                     "tracer_vs_scalar_mismatch_of_200": check_vs_scalar(nm, inputs, 256, nchk=200),
                     "per_step": {"R%dD%d.q%d" % (t[0], t[1] - 4, t[2]): per_step(nm, t)["total"] for t in STEPS}}
    # chain data for the add that follows the (dropped) mask sites: find adds with large bound in the nomask variant
    big = [(tag, v.nv, v.cs, v.bound / 2.0 ** 32) for tag, v in nm.adds if v.bound >= 8 * (1 << 32)]
    res["nomask"]["big_adds"] = [{"tag": list(t), "nv": nv, "cs": cs, "bound_units": b} for t, nv, cs, b in big]
    # exact IH tail under independent uniform leaves, per big add, threshold 16 units (lane limit 2^36)
    tails = []
    for t, nv, cs, b in big:
        x = Fraction(16) - Fraction(cs)
        p = ih_tail(nv, x)
        tails.append({"tag": list(t), "nv": nv, "cs": cs, "p_overflow_IH": float(p)})
    res["nomask"]["ih_tails"] = tails
    # same for the shipped variant at the 3 mask sites (value that WOULD be formed): done via the nomask list
    # ---- layout variants
    rows = []
    rows.append(variant_row("shipped pitch36 x7", ))
    for p in (35, 34):
        rows.append(variant_row("pitch%d x7 (guard %d)" % (p, p - 32), pitch=p, lanes=7))
    rows.append(variant_row("pitch36 x7 no internal masks (policy none)", policy="none"))
    rows.append(variant_row("pitch42 x6", pitch=42, lanes=6))
    rows.append(variant_row("pitch51 x5", pitch=51, lanes=5))
    rows.append(variant_row("pitch64 x4", pitch=64, lanes=4))
    rows.append(variant_row("SWAR pitch32 x8 (6-op masked add)", pitch=32, lanes=8, swar=True))
    res["variants"] = rows
    # time_log2 per variant using ops per lane: ledger scales with PH/7 per lane; PH_equiv = ops*7/lanes
    for r in rows:
        ph = Fraction(r["ops"] * 7, r["lanes"])
        r["PH_equiv_7lane"] = float(ph)
        r["time_log2_equiv"] = time_log2(ph)
    json.dump(res, open(os.path.join(OUT, "steps_out.json"), "w"), indent=1, default=str)
    print("ok", base.ops, res["base_time_log2"])


if __name__ == "__main__":
    main()
