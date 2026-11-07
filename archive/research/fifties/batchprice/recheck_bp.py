#!/usr/bin/env python3
# Independent recheck of BATCHPRICE.md (2026-10-09). Exact integers/Fractions only.
# Inputs are re-derived from the cited source lines, not copied from batchprice.py.
# Run: python -B recheck_bp.py
from fractions import Fraction as F
import math, random

def L2(x):                       # display-only log2 of a positive int or Fraction
    if isinstance(x, F):
        return L2(x.numerator) - L2(x.denominator)
    b = x.bit_length()
    return math.log2(x) if b <= 60 else (b - 60) + math.log2(x >> (b - 60))

def cdiv(a, b):                  # exact ceiling of a/b, a,b > 0
    return -((-a) // b)

Y430 = 430 ** 10000
def kup(O):
    """least k with (O+430*2^38)^10000 <= 430^10000 * 2^k; checks k passes and k-1 fails."""
    X = (O + 430 * 2**38) ** 10000
    k = X.bit_length() - Y430.bit_length() - 2
    while (Y430 << k) < X:
        k += 1
    assert (Y430 << k) >= X and (Y430 << (k - 1)) < X
    return k

def row(name, O):
    k = kup(O)
    print(f"{name}\n   O = {O:,}\n   log2(O/430+2^38) = {L2(F(O + 430 * 2**38, 430)):.10f}  ->  {k//10000}.{k%10000:04d}  (k={k} passes, {k-1} fails)")
    return k

# ---------- AP section 3 (sol_answer_AP_combine.md lines 48-64) ----------
a = 99033509302
mu0_num = (2**21 - 1) * a
assert mu0_num == 207688223066198602                      # line 50
J = cdiv(2**128, 2 * 2**32 * mu0_num)                       # ceil[1/(2*Gsize*mu0)]
assert J == 190738216507                                    # line 52
Bf = J * 2**32
assert Bf == 819214401994932355072                          # line 53
Lf = cdiv(17 * Bf * 312881258079, 16 * 2**48)               # ceil[(17/16)*Bf*312881258079/2^48]
assert Lf == 967534087615711559                             # line 55
S64 = 417832691590563484145792
Q0 = 2**46 + 2**20 + 3 * 2**26 + 40
assert Q0 == 70368946552872                                 # line 57
assert 80 + 117 == 197 and 197 + 106 == 303                 # lines 32-38, 59
assert 144128 + 20 + 16 == 144164                           # lines 28-32
O_AP = S64 + Q0 + 4096 * J + 303 * Bf + 144164 * (Lf + 1) + 8
assert O_AP == 805538240453692110434000                     # line 62
k_AP = row("AP conditional (Sol)", O_AP)
for nm, t in (("S64", S64), ("303Bf", 303 * Bf), ("80Bf", 80 * Bf), ("117Bf", 117 * Bf), ("106Bf", 106 * Bf), ("passes", 144164 * (Lf + 1))):
    print(f"   share {nm}: {100 * F(t, O_AP).__float__():.4f}%")

# ---------- cloud universal bound (cloud_batchS_answer.md 186-190, 209, 260-269) ----------
pre = (1, 4, 12, 40, 130, 426, 1406, 4638, 15286)
suf = (1, 4, 14, 46, 154, 506, 1666, 5490, 18098)
Ib = pre[8] * suf[8]
Jb = sum(pre[:8]) + pre[8] * sum(suf[:8])
assert Ib == 276646028 and Jb == 120475623                 # line 269
Eb = 20 * Jb + 3 * Jb + 202 * 16 + 243                      # E=20J+B+202h+243, B<=3J, h=16
assert Eb == 2770942804 and 29 * Ib + Eb == 10793677616     # line 269
N0 = 2**32
def Ccl(m): return 20 * N0 + (29 * Ib + Eb) + 4 * m + 5 * N0 + 27   # R <= N0
assert Ccl(2**20) == 118172054347 and Ccl(0) == 118167860043
print(f"cloud C(2^21) = {Ccl(2**21):,} = {F(Ccl(2**21), N0).__float__():.6f}/g, log2 {L2(Ccl(2**21)):.6f}")
# ---------- Astra mean (ASTRA_SHARE_REPORT.md 143-146) ----------
def Cas(m): return F(355046943117547601, 4194304) + 7 * m
assert math.floor(Cas(0) * 10**5) == 8464978769243898       # 84,649,787,692.43898...
print(f"Astra mean C(2^21) = {float(Cas(2**21)):,.5f} = {float(Cas(2**21) / N0):.6f}/g")

# ---------- AP ceilings: 117/G replaced by one sweep per frame (J frames) ----------
NREC = 53 * 2**26
def ap_lim(per_frame_sweep, keep_per_G=0):
    return O_AP - 117 * Bf + keep_per_G * Bf + per_frame_sweep
lims = {}
for nm, O in (("AP ceiling, cloud m=2^21", ap_lim(J * Ccl(2**21))),
              ("AP ceiling, Astra mean m=2^21", ap_lim(math.ceil(J * Cas(2**21)))),
              ("AP ceiling, Astra mean m=2^21 (J*ceil per frame)", ap_lim(J * math.ceil(Cas(2**21)))),
              ("SENS: AP ceiling, cloud m=Nrec=53*2^26", ap_lim(J * Ccl(NREC))),
              ("SENS: AP ceiling, Astra mean m=Nrec", ap_lim(math.ceil(J * Cas(NREC)))),
              ("SENS: AP, cloud m=2^21, AM test(2) 23/G kept (AM line 104)", ap_lim(J * Ccl(2**21), 23)),
              ("SENS: AP, 117/G removed at zero cost", ap_lim(0))):
    lims[nm] = (row(nm, O), O)
lgAP = L2(F(O_AP + 430 * 2**38, 430))
for nm, (k, O) in lims.items():
    print(f"   move vs AP: {lgAP - L2(F(O + 430 * 2**38, 430)):.4f} bit  [{nm}]")

# ---------- pkg16f section 11 (proof.md 2532-2545), 9.1 (1597-1602), 9.5 (1953-1969) ----------
S = 498959033940035296819072
FRAMES = cdiv(6643392 * 2**101, 3125 * 1033 * (2**21 - 1))
assert FRAMES == 2487937099176099696050654
REC = 53 * 2**26
assert REC == 3556769792
assert FRAMES * 4096 == 10190590358225304355023478784
assert FRAMES * 512 * 2**32 == 5471031539438825850559026836178731008
assert FRAMES * 64 * REC == 566337249199722207186774262338813952
assert FRAMES * 8192 * 2**21 == 42742433901865826957492397157646336
pf = 4096 + 512 * 2**32 + 64 * REC + 8192 * 2**21
assert pf == 2443836395520 and FRAMES * pf == 6080111232731004242928597850698670080
O16 = S + 2**46 + FRAMES * pf
assert O16 == 6080111232731503201962608254739666816
assert O16 - S == 6080111232731004242928668219442847744    # "search part", line 2572
k16 = row("pkg16f filed", O16)
print(f"   shares: table {100*F(FRAMES*512*2**32, O16).__float__():.4f}%  records {100*F(FRAMES*64*REC, O16).__float__():.4f}%  roots {100*F(FRAMES*8192*2**21, O16).__float__():.4f}%")
# 9.5: 29 g-lines + 1 addition at <=12 each; 128 more per g for record/link/head/loop
assert 30 * 12 == 360 and 360 + 128 <= 512
pfK = 4096 + 512 + 64 * REC + 8192 * 2**21
assert pfK == 244813140480
OK = S + 2**46 + FRAMES * pfK
kK = row("pkg16f K*-only (512 once per frame)", OK)
kK360 = row("SENS: pkg16f K*-only at 360 (30 lines x 12)", S + 2**46 + FRAMES * (4096 + 360 + 64 * REC + 8192 * 2**21))
print(f"   frame factor log2 {L2(F(pf, pfK)):.6f};  records {100*F(64*REC, pfK).__float__():.4f}%  roots {100*F(8192*2**21, pfK).__float__():.4f}%")
row("pkg16f, cloud sweep m=2^21 in place of table (reference)", S + 2**46 + FRAMES * (4096 + Ccl(2**21) + 64 * REC + 8192 * 2**21))
row("LEAD: K*-only + 2^21 c at 512 + index 2^46 (unverified)", S + 2**46 + 2**46 + FRAMES * (4096 + 512 + 512 * 2**21 + 8192 * 2**21))

# ---------- lead algebra: closed-form step 3 solution satisfies step 3 (proof.md 1616-1620) ----------
M = 2**32 - 1
rol = lambda x, r: ((x << r) | (x >> (32 - r))) & M
ror = lambda x, r: rol(x, 32 - r)
rng = random.Random(20261009)
for _ in range(20000):
    Y11, Y12, w5, Ks, c = (rng.getrandbits(32) for _ in range(5))
    d = (c - Y11) & M; u = rol(d, 16) ^ Y12
    b = ror(((u - Ks) & M) ^ c, 12); aa = (b + u + w5) & M; z = ror(aa ^ d, 8)
    d2 = (c - Y11) & M; a2 = d2 ^ rol(z, 8); u2 = rol(d2, 16) ^ Y12; b2 = (a2 - u2 - w5) & M
    assert b2 == b and ((u2 - (rol(b2, 12) ^ c)) & M) == Ks
print("lead closed form: 20000 random frames/c, step-3 H equals K* every time (identity)")
