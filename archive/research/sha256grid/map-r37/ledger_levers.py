# Lever sizing on the d3ec5c41 ledger, from the integers printed in its public note (COMPUTED arithmetic on them).
from fractions import Fraction as F
from math import log2
C = 2644
T = F(10005628052435696944197, C)                 # printed total, units
NFB = 358768880796199274                           # printed first blocks
VMAX = 5884436111293702870939                      # printed cap on data-dependent ops
AC, AS, DEV = 2**60, 2**50, 2**40
print("log2 T            = %.6f" % log2(T))
fixed = NFB * (1 + F(51, C))                       # 1 compression + 51 fixed ops per first block
vpart = F(VMAX, C)
rest = T - AC - AS - DEV - fixed - vpart
print("A_C share         = %.4f   log2 T without A_C = %.5f" % (AC / T, log2(T - AC)))
print("first-block share = %.4f   (compressions alone %.4f)" % (fixed / T, NFB / T))
print("V_MAX share       = %.4f   V_MAX/NFB = %.2f ops" % (vpart / T, VMAX / NFB))
print("residual (tables, caps, final) = 2^%.3f units" % log2(rest))
def score(ac=AC, fb_units=1 + F(51, C), vscale=1, nscale=1):
    n = NFB * nscale
    return log2(ac + AS + DEV + n * fb_units + vpart * nscale * vscale + rest)
print("\n--- one-lever rows (DERIVED: ledger shape held fixed, only the named term moved) ---")
print("A_C 2^60 -> 2^56                          : %.5f (note prints 61.22949)" % score(ac=2**56))
print("A_C 2^60 -> 2^46 (r32 35-step scale)      : %.5f" % score(ac=2**46))
for fbops in (230, 300, 400):
    print("first block 1 unit -> %3d ops (bit-sliced): %.5f" % (fbops, score(fb_units=F(fbops + 51, C))))
for s in (0.9, 0.75, 0.5):
    print("data-dependent work x%.2f                : %.5f" % (s, score(vscale=s)))
print("row-16 stage ~14000 of %.0f ops -> half    : %.5f" % (VMAX / NFB, score(vscale=1 - F(7000) / (F(VMAX) / NFB))))
for q in (0.5, 0.25):
    print("success per first block x%.0f (N_FB x%.2f) : %.5f" % (1/q, q, score(nscale=q)))
print("bit-sliced FB (300 ops) + A_C 2^56        : %.5f" % score(ac=2**56, fb_units=F(351, C)))

print("\n--- r38 side check (DERIVED from printed exponents of c99df2dc / 0ae69bcb) ---")
on, pre = 2**72.01600, 2**67.21233
tot = lambda ac, as_, dev=2**64: log2(on + pre + ac + as_ + dev)
print("0ae69bcb shape A_C=A_S=2^70           : %.5f (board 72.64)" % tot(2**70, 2**70))
print("same with A_S -> 2^50 (paper Step-1 2^38.3 published): %.5f" % tot(2**70, 2**50))
print("no allowances                          : %.5f (c99df2dc prints 72.06675)" % log2(on + pre))
print("\n--- stacked r37 rows (DERIVED) ---")
print("bit-sliced FB 300 ops + data x0.90 (7-lane u, cb table) : %.5f" % score(fb_units=F(351, C), vscale=0.9))
print("bit-sliced FB 300 ops + data x0.90 + success x2        : %.5f" % score(fb_units=F(351, C), vscale=0.9, nscale=0.5))
