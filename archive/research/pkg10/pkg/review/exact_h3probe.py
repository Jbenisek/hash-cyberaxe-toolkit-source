#!/usr/bin/env python3
"""exact lens, pkg7 (draft): a small independent look at the share of batches that run stage 2 (H3), laid out as
runs of 6.4: the four words of step 1 fixed per run, C0.d1 below 1,424,469, w5 and X2 consecutive from a start.

Uses the stage A typed in exact_check.py from the text of 6.5 (its flag was compared with rule A on the real h1 of
the real messages on every lane of the other parts). A measurement on a small sample, not a proof of anything.

    python -B exact_h3probe.py RUNS OUTER X2S
"""
import os
import statistics
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exact_check import (ALL, CONST, M, SIX, X15, build, compile_steps, lanes, lemma_a_word, list_word, pror,  # noqa: E402
                         read_displays, rep, rol, shake_words)

LISTS = [list_word(j) for j in range(18725)]
C_ALL, C_CARRY, C_R = rep(ALL), rep((1 << 32) - ALL), rep(rol(X15, 8))
BIT32 = sum(1 << (36 * i + 32) for i in range(7))


def stage_a(o, m, row, V):
    X0 = row["XA"] + rep(-m["w2"])
    X10 = (X0 ^ C_R) + rep(o["S10"] + X15)
    a1 = row["X6"] + rep(m["X2"] + o["w7"])
    d1 = pror(a1 ^ rep(o["X14"]), 16)
    b1 = pror(row["X6"] ^ (X10 + d1), 12)
    z = (a1 + b1 + rep(m["w0"])) ^ d1
    return (((lemma_a_word(z) ^ V) & C_ALL) + C_CARRY) & BIT32


def main(runs, outers, x2s):
    disp, _ = read_displays()
    fn = compile_steps(disp)
    run_means = []
    allctx = []
    for r in range(runs):
        w = shake_words("exact h3 run %d" % r, 8)
        ctx = []
        for oi in range(outers):
            # C0.d1 spread over its range, w5 consecutive from a start, in pairs of neighbours
            c0d1 = (w[4] + (oi // 2) * 177787) % 1424469
            w5 = (w[5] + oi) & M
            o = dict(CONST)
            o.update(zip(SIX, [w[0], c0d1, w[1], w[2], w[3], w5]))
            fn["O"](o)
            tab = [build(o, U) for _, U, _ in LISTS]
            for xi in range(x2s):
                m = dict(o)
                m["X2"] = (w[6] + xi) & M if oi % 2 == 0 else (xi * 0x01000193 + w[7]) & M
                fn["M"](m)
                entered = members = 0
                for j in range(18725):
                    f = stage_a(o, m, tab[j], LISTS[j][2])
                    if f:
                        entered += 1
                        cnt = bin(f).count("1")
                        members += cnt if j < 18724 else min(cnt, 4)
                ctx.append((entered / 18725, members))
        shares = [c[0] for c in ctx]
        allctx += ctx
        run_means.append(statistics.mean(shares))
        print("run %d: %d contexts (%d outer steps x %d X2); share of batches entering stage 2: mean %.5f, "
              "min %.5f, max %.5f, s.d. of a context %.5f; members satisfying rule A per context: mean %.1f (512)" % (
                  r, len(ctx), outers, x2s, run_means[-1], min(shares), max(shares), statistics.pstdev(shares),
                  statistics.mean(c[1] for c in ctx)), flush=True)
    shares = [c[0] for c in allctx]
    print("all %d contexts: mean %.5f (budget 0.03125, text 0.0262); contexts above the budget: %d; run means from "
          "%.5f to %.5f, s.d. between runs %.5f; expected s.d. of a run mean from the contexts alone %.5f" % (
              len(shares), statistics.mean(shares), sum(s > 1 / 32 for s in shares), min(run_means), max(run_means),
              statistics.pstdev(run_means), statistics.pstdev(shares) / (len(shares) / len(run_means)) ** 0.5))


if __name__ == "__main__":
    main(*(int(a) for a in sys.argv[1:4]))
