"""Replication on STREAM 2 (fresh seeds) of (a) the pre-registered hypotheses in prereg.json and (b) every test that was
Bonferroni-significant on STREAM 1. Each stream is compared with its own control stream. Writes replicate_out.txt."""
import sys
sys.dont_write_bytecode = True
import json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oclib as L

out = open(os.path.join(HERE, "replicate_out.txt"), "w")


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


ld = lambda f: L.split_flat(np.fromfile(os.path.join(HERE, f), "<u8"))
T1 = L.evaluate2(ld("stream_real_2p28.bin"), ld("stream_ctrl_2p28.bin"))
T2 = L.evaluate2(ld("stream2_real_2p28.bin"), ld("stream2_ctrl_2p28.bin"))
pre = json.load(open(os.path.join(HERE, "prereg.json")))
fam = [k for k in T1 if k[0] in L.TESTED_QS]
thr = 0.01 / len(fam)
say("STREAM 1 vs its control, STREAM 2 vs its control (2^28 pairs each).")
say("Pre-registered one-sided (advantage > 0): pass = one-sided p < 0.01 on STREAM 2")
for k in pre["one_sided_positive_advantage"]:
    a, b = T1[k], T2[k]
    p1s = b["p"] / 2 if b["stat"] > 0 else 1 - b["p"] / 2
    sk = "S" + k[1:]
    say("  %-20s STREAM1 adv %+.4f+-%.4f | STREAM2 adv %+.4f+-%.4f one-sided p %.3g -> %s | surrogate S: %+.4f / %+.4f" % (
        k, a["eff"], a["se"], b["eff"], b["se"], p1s, "REPLICATED" if p1s < 0.01 else "not replicated", T1[sk]["eff"], T2[sk]["eff"]))
say("KEY ERROR in prereg.json: keys use the word INDEX (w0..w3 = words 1,3,4,6). The section-3 effect I meant to pre-register"
    " was residual WORD 3 = index w1; I wrote w3 (= word 6). The intended tests, run after the fact on STREAM 2:")
for k in ("D.w1.m65535.zero", "D.w1.m65537.zero"):
    a, b = T1[k], T2[k]
    p1s = b["p"] / 2 if b["stat"] > 0 else 1 - b["p"] / 2
    sk = "S" + k[1:]
    say("  %-20s STREAM1 adv %+.4f+-%.4f | STREAM2 adv %+.4f+-%.4f one-sided p %.3g | surrogate S: %+.4f / %+.4f" % (
        k, a["eff"], a["se"], b["eff"], b["se"], p1s, T1[sk]["eff"], T2[sk]["eff"]))
say("Pre-registered chi-square replications: pass = p < 0.01 on STREAM 2 (index w1 = residual word 3)")
for k in pre["chi_replication"]:
    a, b = T1[k], T2[k]
    sk = "S" + k[1:]
    say("  %-20s STREAM1 p %.2e KL %.3g | STREAM2 p %.2e KL %.3g -> %s | surrogate S KL: %.3g / %.3g" % (
        k, a["p"], a["eff"], b["p"], b["eff"], "REPLICATED" if b["p"] < 0.01 else "not replicated", T1[sk]["eff"], T2[sk]["eff"]))
sig1 = [k for k in fam if T1[k]["p"] < thr]
rep = [k for k in sig1 if T2[k]["p"] < 0.01 and (T1[k]["kind"] == "chi" or np.sign(T1[k]["stat"]) == np.sign(T2[k]["stat"]))]
say("Bonferroni-significant on STREAM 1: %d (D %d, R %d, E %d); replicated on STREAM 2 at p < 0.01: %d (D %d, R %d, E %d)" % (
    len(sig1), sum(k[0] == "D" for k in sig1), sum(k[0] == "R" for k in sig1), sum(k[0] == "E" for k in sig1),
    len(rep), sum(k[0] == "D" for k in rep), sum(k[0] == "R" for k in rep), sum(k[0] == "E" for k in rep)))
for k in sig1:
    if k[0] == "D":
        sk = "S" + k[1:]
        say("  %-22s STREAM1 p %.2e eff %.3g | STREAM2 p %.2e eff %.3g | surrogate S eff %.3g / %.3g" % (
            k, T1[k]["p"], T1[k]["eff"], T2[k]["p"], T2[k]["eff"], T1[sk]["eff"], T2[sk]["eff"]))
nr = [k for k in sig1 if k not in rep]
say("  not replicated: %s" % (", ".join(nr) if nr else "none"))
# pooled zero-cell advantages for D (both streams), the 'lean toward 0' summary
say("Pooled D cell-0 advantage (STREAM 1 + STREAM 2, 2^29 pairs vs 2^29 control), log2 ratio +- s.e.:")
C = {k: v1 + v2 for (k, v1), v2 in zip(ld("stream_real_2p28.bin").items(), ld("stream2_real_2p28.bin").values())}
R = {k: v1 + v2 for (k, v1), v2 in zip(ld("stream_ctrl_2p28.bin").items(), ld("stream2_ctrl_2p28.bin").values())}
TP = L.evaluate2(C, R, qs=("D", "S"))
for q in ("D", "S"):
    for w in range(4):
        say("  %s word %d: %s" % (q, (1, 3, 4, 6)[w], "  ".join("m%d %+.4f+-%.4f" % (m, TP["%s.w%d.m%d.zero" % (q, w, m)]["eff"], TP["%s.w%d.m%d.zero" % (q, w, m)]["se"])
                                                         for m in (3, 5, 15, 17, 255, 257, 65535, 65537))))
    say("  %s joint 4-word: %s" % (q, "  ".join("m%d %+.4f+-%.4f" % (m, TP["%s.joint.m%d.zero" % (q, m)]["eff"], TP["%s.joint.m%d.zero" % (q, m)]["se"]) for m in L.JMODS)))
