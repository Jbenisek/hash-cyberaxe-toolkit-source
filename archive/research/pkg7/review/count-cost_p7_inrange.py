#!/usr/bin/env python3
"""Reviewer (count and cost), research/pkg7 DRAFT: the share of the batches that would run stage 2, sampled in the
RANGES of proof.md 6.4 (four random seed words per run; C0.d1 small, w5 and X2 small and consecutive), all 18,725
batches of each context. Own code on top of count-cost_p7_tracer.py; h1 anchored against the own compression.
usage: python -B count-cost_p7_inrange.py RUNS SEED"""
import importlib.util, math, pathlib, random, sys
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p7tracer", HERE / "count-cost_p7_tracer.py")
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
M32 = 0xFFFFFFFF
hs = T.load_program()
runs, seed = int(sys.argv[1]), int(sys.argv[2])
rng = random.Random(seed)
members = [T.member_text(k) for k in range(131072)]
per, anchor, bad, pas_t, tot_t = [], 0, 0, 0, 0
for run in range(runs):
    c0c, d3d, s15, s9 = (rng.getrandbits(32) for _ in range(4))
    for c0d, w5, x2 in ((0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0), (1424468, 0, 2), (0, 2, 3), (7, 1, 1), (0, 0, 0xFFFFFFFF)):
        v = hs.context([c0c, c0d, d3d, s15, s9, w5, x2])      # order of CONTEXT_WORDS
        x4w2, rx15, pb = v["X4"] + v["w2"], hs.rol(hs.X15, 8), 0
        for j in range(18725):
            hit = 0
            for i in range(7 if j < 18724 else 4):
                y4 = members[7 * j + i]
                r = hs.member(v, y4)
                x10 = (v["S10"] + (rx15 ^ ((r["C0.a1"] - x4w2) & M32)) + hs.X15) & M32
                h1 = hs.ror(hs.g(v["X2"], r["X6"], x10, v["X14"], v["w7"], v["w0"])[3] ^ ((T.Y3 + y4) & M32), 16)
                ok = T.rule_a_text(h1)
                if (7 * j + i) % 8191 == 5:
                    w, _ = hs.trial(v, y4)
                    _, ycol, mp = T.compress2(hs.messages(w)[0])
                    anchor += 1
                    bad += h1 != T.rotr(ycol[14] ^ ((ycol[3] + ycol[4] + mp[14]) & M32), 16)
                hit |= ok; pas_t += ok
            pb += hit
        tot_t += 131072
        per.append(pb / 18725)
mean = sum(per) / len(per)
sd = (sum((x - mean) ** 2 for x in per) / (len(per) - 1)) ** 0.5
print("in-range sample: %d runs x 8 contexts, %d trials; share of the trials 2^%.4f; share of the batches %.5f (budget 0.03125); "
      "single contexts %.4f to %.4f, standard deviation %.4f, standard error %.4f; per run %s; h1 anchored on %d, wrong %d"
      % (runs, tot_t, math.log2(pas_t / tot_t), mean, min(per), max(per), sd, sd / len(per) ** 0.5,
         " ".join("%.4f" % (sum(per[8 * r:8 * r + 8]) / 8) for r in range(runs)), anchor, bad))
