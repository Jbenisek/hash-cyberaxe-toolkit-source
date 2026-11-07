#!/usr/bin/env python3
"""count-cost reviewer: the exact probability, under the seven-word model, that a trial shows a listed partial E3
event AND satisfies the rule on h1. The GPU programs count this joint event on real trials; the package compares it
only with draws from the model. Here it is counted exactly, with a method written for this purpose.

    python -B count-cost_e3rule.py            (Windows Python with numpy; one thread; about a minute)

Partial E3 event of a pair (psi, eps): Y4 in the class, and for the words (Y4, h1, Y9, w8)
    f1 XOR f1' = psi   and   e2 XOR e2' = eps        (the first five assignments of E3 for A and B).
With e1 = Y3 + Y4, g1 = Y9 + h1, e2 = e1 + f1 + w8 the map (Y4, h1, Y9, w8) -> (e1, h1, g1, e2) is a bijection, and
    (g1 + dh) XOR g1 = ROL(psi, 12),   dh = (h1 XOR eta) - h1        (a function of the 13 bits of h1 on eta)
    (e2 + D) XOR e2 = eps,              D = DY3 + (f1 XOR psi) - f1,  f1 = ROR(Y4 XOR g1, 12).
For an addition x -> x + D with a prescribed XOR difference X the solutions x form a cube: the carry into bit i is
D_i XOR X_i, so D_0 = X_0, D_(i+1) XOR X_(i+1) = D_i wherever X_i = 0 (i < 31), and x_i = D_(i+1) XOR X_(i+1)
wherever X_i = 1 (i < 31); all other bits of x are free. So: for each of the 2^13 patterns of h1 on eta, g1 is
fixed on the bits of ROL(psi,12) below 31; for each such g1 pattern every member of the class is visited (arrays),
D is formed and the cube of e2 is counted. Nothing is sampled.

Checks: the cube rule against brute force for 8-bit words; every pair's count against the count in the groundwork's
table research/h8/gpu/out/e3p_expected_H8.txt (another program); the sum against the exact probability in
h8_deep_expected.txt. Then the same count with the rule on h1 (4, 5 and 6 conditions), and the comparison with the
GPU counts quoted from research/h8/gpu/out (files named in the output).
"""
import math
import random
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
GPU = HERE.parents[1] / "h8" / "gpu" / "out"
MORE = HERE.parents[1] / "h8" / "gpu_more" / "out"
U = np.uint32
M = 0xFFFFFFFF
ETA, Y3, DY3 = 0x830303CF, 0x8127C181, 0xFDB77CFD
QMASK, QVALUE = 0x03CF8303, 0x030C0303
RULES = {4: [(0x1, 0), (0x2, 1), (0x10000, 0), (0x20000, 0)]}
RULES[5] = RULES[4] + [(0xC, 1)]
RULES[6] = RULES[5] + [(0x180, 1)]


def ror(v, n, w=32):
    return ((v >> n) | (v << (w - n))) & ((1 << w) - 1)


def rol(v, n, w=32):
    return ror(v, w - n, w)


def cube(d, x, w=32):
    """(number of v with (v + d) XOR v == x on w-bit words, mask of the forced bits, their values)."""
    low = (1 << (w - 1)) - 1
    if (d ^ x) & 1 or (d ^ (d >> 1) ^ (x >> 1)) & ~x & low:
        return 0, 0, 0
    return 2 ** (bin(~x & low).count("1") + 1), x & low, ((d >> 1) ^ (x >> 1)) & x & low


def cube_selftest():
    rng, good, cases = random.Random(5), 0, 0
    for _ in range(600):
        d, x = rng.randrange(256), rng.randrange(256)
        if rng.random() < 0.7:
            v = rng.randrange(256)
            x = ((v + d) & 255) ^ v
        sols = [v for v in range(256) if ((v + d) & 255) ^ v == x]
        n, mask, val = cube(d, x, 8)
        good += int(n == len(sols) and all(v & mask == val for v in sols))
        cases += 1
    return good, cases


def passes(h, rule):
    return all(bin(h & m).count("1") & 1 == v for m, v in rule)


def main():
    start = time.time()
    good, cases = cube_selftest()
    free = [i for i in range(32) if not QMASK >> i & 1]
    k = np.arange(1 << len(free), dtype=np.uint32)
    e1 = np.full(k.shape, QVALUE, dtype=np.uint32)
    for j, i in enumerate(free):
        e1 |= ((k >> U(j)) & U(1)) << U(i)
    y4 = e1 - U(Y3)
    ebits = [i for i in range(32) if ETA >> i & 1]
    patterns = []
    for s in range(1 << len(ebits)):
        hb = sum((s >> j & 1) << i for j, i in enumerate(ebits))
        patterns.append((((hb ^ ETA) - hb) & M, tuple(passes(hb, RULES[n]) for n in (4, 5, 6))))
    pairs = []
    for line in (GPU / "e3p_expected_H8.txt").read_text(encoding="ascii").split("\n"):
        f = line.split()
        if len(f) >= 5 and f[0] == "E3P":
            pairs.append((int(f[1], 16), int(f[2], 16), int(f[4])))
    total = [0, 0, 0, 0]
    same = 0
    hist = {}
    with np.errstate(over="ignore"):
        for psi, eps, listed in pairs:
            p = rol(psi, 12)
            groups = {}
            for dh, ok in patterns:
                n, mask, val = cube(dh, p)
                if n:
                    g = groups.setdefault(val, [0, 0, 0, 0])
                    g[0] += 1
                    for j in range(3):
                        g[1 + j] += int(ok[j])
            free_g1 = 2 ** bin(~p & 0x7FFFFFFF).count("1")          # bits of g1 below 31 outside the mask
            n_e2 = 2 ** (bin(~eps & 0x7FFFFFFF).count("1") + 1)
            count = [0, 0, 0, 0]
            if p not in hist:                                       # the members of the class by their bits of Y4 on the mask
                hist[p] = np.unique(y4 & U(p), return_counts=True)
            keys, how_many = hist[p]
            for val, mult in groups.items():
                for top in ((0, 1) if p >> 31 else (None,)):
                    g1 = val | ((top or 0) << 31)
                    t = keys ^ U(g1 & p)                             # (Y4 XOR g1) on the mask
                    f = (t >> U(12)) | (t << U(20))                  # the bits of f1 on psi
                    d = U(DY3) + ((f ^ U(psi)) - f)
                    valid = (((d ^ U(eps)) & U(1)) == 0) & (((d ^ (d >> U(1)) ^ U(eps >> 1)) & U(~eps & 0x7FFFFFFF)) == 0)
                    members = int(how_many[valid].sum())
                    weight = members * n_e2 * free_g1 * (1 if top is not None else 2) * 2 ** (32 - len(ebits))
                    for j in range(4):
                        count[j] += mult[j] * weight
            same += int(count[0] == listed)
            for j in range(4):
                total[j] += count[j]
    space = 2 ** 115
    p_all = total[0] / space
    text = (GPU / "h8_deep_expected.txt").read_text(encoding="ascii")
    p_file = float(re.search(r"^SUM .* e3 ([0-9.e+-]+)", text, re.M).group(1))
    out = [f"cube rule against brute force, 8-bit words: {good} of {cases}; pairs (psi, eps) in e3p_expected_H8.txt {len(pairs)}, my count equal "
           f"to the listed count in {same}; P(listed partial E3 event) mine {p_all:.16e}, h8_deep_expected.txt {p_file:.16e}"]
    frac = [total[j] / total[0] for j in range(4)]
    out.append(f"exact under the model: P(rule | listed partial E3 event) = {frac[1]:.6f} (4 conditions), {frac[2]:.6f} (5), {frac[3]:.6f} (6); "
               f"a uniform h1 would give 0.0625, 0.03125, 0.015625")

    def stat(path):
        t = path.read_text(encoding="ascii", errors="replace")
        a = int(re.search(r"listed partial E3 event (\d+)", t).group(1))
        b = int(re.search(r"listed partial E3 events that pass it: (\d+)", t).group(1))
        return a, b

    runs = {"real, independent contexts": [(GPU / f"h8_real{e}.txt", 2 ** e) for e in (40, 42, 45)],
            "real, layout runs 1 to 8": [(GPU / f"h8_layout_run{i}.txt", 2 ** 40) for i in range(1, 9)],
            "real, layout runs 9 to 24": [(MORE / f"h8_layout_run{i}.txt", 2 ** 40) for i in range(9, 25)],
            "draws from the model": [(GPU / f"h8_model{e}.txt", 2 ** e) for e in (40, 42, 44)]}
    sums = {}
    for name, files in runs.items():
        try:
            got = [stat(path) for path, _ in files]
        except (OSError, AttributeError) as error:
            out.append(f"{name}: not read ({type(error).__name__})")
            continue
        trials = sum(n for _, n in files)
        a, b = sum(x for x, _ in got), sum(y for _, y in got)
        sums[name] = (trials, a, b)
        ea, eb = trials * p_all, trials * total[1] / space
        z_frac = (b / a - frac[1]) / math.sqrt(frac[1] * (1 - frac[1]) / a)
        out.append(f"{name}: trials 2^{math.log2(trials):.2f}; partial events {a} against {ea:.1f} exact ({(a - ea) / math.sqrt(ea):+.2f} sd); of them "
                   f"satisfying the four conditions {b} against {eb:.1f} exact ({(b - eb) / math.sqrt(eb):+.2f} sd); share {b / a:.4f} against "
                   f"{frac[1]:.4f} exact ({z_frac:+.2f} sd)")
    real = [v for name, v in sums.items() if name.startswith("real")]
    if real:
        trials, a, b = (sum(v[i] for v in real) for i in range(3))
        ea, eb = trials * p_all, trials * total[1] / space
        z_frac = (b / a - frac[1]) / math.sqrt(frac[1] * (1 - frac[1]) / a)
        out.append(f"all real trials read here: 2^{math.log2(trials):.2f}; partial events {a} against {ea:.1f} ({(a - ea) / math.sqrt(ea):+.2f} sd); "
                   f"satisfying the four conditions {b} against {eb:.1f} ({(b - eb) / math.sqrt(eb):+.2f} sd); share {b / a:.4f} against {frac[1]:.4f} "
                   f"({z_frac:+.2f} sd); not satisfying {a - b} against {ea - eb:.1f} ({(a - b - ea + eb) / math.sqrt(ea - eb):+.2f} sd)")
    out.append(f"{time.time() - start:.0f} s")
    (HERE / "count-cost_e3rule.out").write_text("\n".join(out) + "\n", encoding="ascii", newline="\n")
    for line in out:
        print(line[:330])
    return 0 if good == cases and same == len(pairs) else 1


if __name__ == "__main__":
    sys.exit(main())
