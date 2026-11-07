# nb_verify_nature_0 - recompute the numbers behind NATURE.md row 11 (kinetic proofreading):
# "already the leaders' stage A / stage 2 with rule A; cost factor only; at most 0.77 bit left; projected 90.8".
# Sources: research\pkg10\pkg\blake3-r2\proof.md section 8 (ledger), 6.5 (part table), 2302-2317 (c1 split);
#          END_OF_LINE.md 3.1; rivals\since_2100Z\93.5891_Subflatus3_ef81f589.md (leader ledger).
from fractions import Fraction as Fr
from math import log2
import numpy as np

L = lambda x: log2(float(x))
C = 430
N_d2 = 759300 * 2**81                     # trial-equivalents of the filed run (discount 2, F = 92,675,904)

def tlog(charge, N=N_d2):
    # proof.md 8: T <= charge*N*(1+2^-7)/430 + 2^81 ; claim = that, rounded up to 2 decimals
    T = Fr(charge) * N * (1 + Fr(1, 2**7)) / C + 2**81
    return L(T)

print("== A. reproduce the filed claim 92.53 ==")
print("  charge 1.65 -> time_log2 %.4f (filed 92.53)" % tlog(Fr(165, 100)))

print("\n== B. the ledger, per representative (rows of proof.md section 8) ==")
R, words = 16384, 2341
rows = {
 "group": Fr(1250, 16384),
 "rep stage A + store z": Fr(48 * words, R),
 "rep gate test + load z": Fr(10 * words, R),
 "rep stage 2 (E = 1/32 of rep words)": Fr(135 * words, 256 * 2048),
 "open gate routing+dispatch (G)": Fr(12, 10) * Fr(624630, 10**7) * 31,
 "open gate entry+exit (G)": Fr(12, 10) * Fr(624630, 10**7) * 33,
 "neighbour stage A (W)": Fr(12, 10) * Fr(5625, 10**4) * 47,
 "neighbour stage 2 (S)": Fr(12, 10) * Fr(1364, 10**4) * 135,
}
for k, v in rows.items(): print("  %-38s %10.6f" % (k, float(v)))
tot = sum(rows.values()); TE = Fr(4102, 100)
print("  total %.6f (filed 67.585260), per TE %.6f (filed 1.647618 -> 1.65)" % (float(tot), float(tot / TE)))
st2 = rows["rep stage 2 (E = 1/32 of rep words)"] + rows["neighbour stage 2 (S)"]
first = tot - st2
print("  stage-2 rows %.4f = %.1f%% of the charge; rows paid before any later stage %.4f" % (float(st2), 100*float(st2/tot), float(first)))

print("\n== C. what staging (more/cheaper later stages) can still buy in this layout ==")
q = Fr(105, 16384)
p_word = 1 - (1 - q)**7
print("  c1 cheap test: lane %s = %.8f, word (7 lanes) %.8f (proof: 0.0440075)" % (q, float(q), float(p_word)))
def with_price(price):  # replace the 135 stage-2 word price
    return first + st2 * Fr(price) / 135
cases = [
 ("filed, stage 2 whole (135)", Fr(135)),
 ("c1 split, expected: 81+12+p*57", 81 + 12 + p_word * 57),
 ("c1 split, 57-row at a 1.2x budget", 81 + 12 + Fr(12, 10) * p_word * 57),
 ("CEILING: every stage after stage A free (0)", Fr(0)),
]
base = tot / TE
for name, price in cases:
    tpr = with_price(price); ch = tpr / TE
    ch_up = Fr(int(ch * 100) + (0 if ch * 100 == int(ch * 100) else 1), 100)  # rounded up as the filing does
    print("  %-44s word %7.3f  per-rep %8.4f  charge %.5f (->%s)  gain %.3f bit  time_log2 %.3f"
          % (name, float(price), float(tpr), float(ch), float(ch_up), L(base / ch), tlog(ch_up)))

print("\n== D. the '0.77 bit' and the '1 op per trial' floor ==")
for c in (Fr(171, 100), Fr(165, 100), tot / TE):
    print("  log2(%.6f / 1.00) = %.4f bit" % (float(c), L(c)))
print("  rep stage A alone per TE: %.4f  (one packed op covers 7 lanes, so 1 op/TE is a convention, not a law)"
      % float(rows["rep stage A + store z"] / TE))
print("  first-stage floor of this layout (stage-2 rows removed): %.4f per TE" % float(first / TE))

print("\n== E. the projected exponent 90.8 ==")
# END_OF_LINE 2: time_log2 = 123.339 - log2(F) + log2(ops/34) + 0.012
eol = lambda F, ops: 123.339 - L(F) + L(Fr(ops) / 34) + 0.012
for F, lab in ((Fr(18535545345, 100), "kept for claim, discount 1"), (Fr(185351809), "with c1 test, discount 1"),
               (Fr(92675904), "filed assumed factor (discount 2)")):
    print("  F=%-16s %-34s ops 1.00 -> %.3f ; ops 1.65 -> %.3f ; ops 1.0942 -> %.3f"
          % (float(F), lab, eol(F, 1), eol(F, Fr(165, 100)), eol(F, first / TE)))
print("  discount 2 -> 1 is worth %.3f bit and is not a staging effect" % L(2))

print("\n== F. leader (93.5891, three stages 19/66/119): staging ceiling ==")
tot_l, B, Cc = 3.484995, 0.70846, 0.05829
print("  fixed (stage A + steps) %.5f ops/trial; stages B+C %.5f; ceiling if B and C were free: %.3f bit"
      % (tot_l - B - Cc, B + Cc, log2(tot_l / (tot_l - B - Cc))))

print("\n== G. why stage A cannot be split further in packed form (Monte Carlo, numpy) ==")
rng = np.random.default_rng(2026)
for lane_pass in (0.5, 0.25, 1/16, float(Fr(11430, 10000) / 256)):
    w = (rng.random((2_000_000, 7)) < lane_pass).any(axis=1).mean()
    print("  pre-test passing a lane w.p. %.5f: word continues w.p. %.4f (exact %.4f) -> abort saves %.1f%% of later work"
          % (lane_pass, w, 1 - (1 - lane_pass)**7, 100 * (1 - w)))
