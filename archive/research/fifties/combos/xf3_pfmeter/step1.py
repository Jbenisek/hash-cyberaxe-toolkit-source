# XF3 step 1: stage-2 share of PF71's charged total (proof.md Section 11) and the gain bound.
from math import log2, sqrt, ceil, exp
O_TOT = 1119513945581117291751304          # proof.md 2559
rows = {"SEL S_old": 8882224365081579520, "SEL S_new": 498950152841501402605440,
        "E1 record table": 70368744177664, "frame lines": 937516481769472,
        "frame tables": 503325328582607806398464, "record scans": 52102035966559011209216,
        "roots (ROOT_CAP*8192)": 65127544958198764011520, "cap test": 8}
assert sum(rows.values()) == O_TOT
price = lambda O: log2(O / 430 + 2**38)
print("PF71 price", price(O_TOT))
for k, v in rows.items(): print(f"  {k:24s} {v/O_TOT:.4%}")
s = 0  # no stage-2 (counter batch) row in Section 11; STAGE_2_BUDGET is not charged
f = 0.133
print("stage-2 share s =", s, " gain bound =", -log2(1 - s*(1 - f)), "bit")
# Side check (NOT the claim under test): CK3-style Bernstein budget on the analogous static cap, ROOT_CAP.
FRAMES, MEAN_H8 = 228885859807, 1.2 * 1736704
ROOT_CAP = 20 * FRAMES * 1736704
m = ceil(MEAN_H8 * FRAMES)
for Lname, L in (("2^53 (trials of a frame)", 2**53), ("RECORDS*2^32", 3556769792 * 2**32)):
    B = m + ceil(sqrt(40 * L * m)) + 14 * L
    fr = B / ROOT_CAP
    O2 = O_TOT - rows["roots (ROOT_CAP*8192)"] * (1 - fr)
    print(f"root cap, L={Lname}: B/ROOT_CAP={fr:.4f}, row-only gain={price(O_TOT)-price(O2):.4f} bit")
