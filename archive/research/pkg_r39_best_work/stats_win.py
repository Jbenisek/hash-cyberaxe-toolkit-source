#!/usr/bin/env python3
"""stats_win.py SEED OUT.json : per-claw side-condition statistics of one full ledger window of the shipped program
(owner 10-27: re-measure 0b2616e3's offline uniformity block on OUR windows, not cut it). Runs Attack(win=P.WIN, seed=SEED,
check=True) exactly as `r39joint.py --windows 1 --seed S` does (seed = S*1000), then for every distinct claw recomputes
W8 in F8, W9 in F9, W17, W18 with the program's own functions (the same code path as r39-window-small)."""
import sys, os, json
sys.path.insert(0, os.getcwd())
import r39joint as J

seed = int(sys.argv[1]); out = sys.argv[2]
A = J.Attack(win=J.P.WIN, seed=seed, check=True); A.run_window()
lo16 = [0] * 65536; hi16 = [0] * 65536; w18h = [0] * 256
n = f8 = f9 = both = 0; low = {8: 0, 12: 0, 16: 0, 20: 0, 24: 0}; seq9 = []
for _, a0, u in sorted(A.distinct):
    a1 = J.recover_a1(A.cv, a0, u); W = J.build(A.cv, a0, a1); ex = J.expand(W); w17, w18 = ex[17], ex[18]
    in8 = int(((J.s0((W[8] + J.D8) & J.M) - J.s0(W[8])) & J.M) == J.T8)
    in9 = int(((J.s0((W[9] + J.D9) & J.M) - J.s0(W[9])) & J.M) == J.T9)
    n += 1; f8 += in8; f9 += in9; both += in8 & in9; seq9.append(in9)
    for k in low: low[k] += (w17 & ((1 << k) - 1)) == (J.W17PUB & ((1 << k) - 1))
    lo16[w17 & 0xffff] += 1; hi16[w17 >> 16] += 1; w18h[w18 & 0xff] += 1
adj9 = sum(seq9[i] & seq9[i + 1] for i in range(len(seq9) - 1))
json.dump({"seed": seed, "claws": n, "groups": J.count_groups(A.distinct), "f8": f8, "f9": f9, "both": both,
           "low": low, "adj9": adj9, "lo16": lo16, "hi16": hi16, "w18": w18h}, open(out, "w"))
print("seed", seed, "claws", n, "f9", f9, "f8", f8, "both", both, "low", low, "adj9", adj9)
