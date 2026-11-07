#!/usr/bin/env python3
# Exact re-pricing of the per-frame table route with the batch-inversion bounds
# (Astra share report, Sol cloud batch-S answer). Integers and Fractions only.
# Run: python -B batchprice.py
from fractions import Fraction as Fr
import math

P38 = 2**38

def lg(n):  # float log2 of a big positive int or Fraction, for display only
    if isinstance(n, Fr):
        return lg(n.numerator) - lg(n.denominator)
    s = n.bit_length() - 64
    return math.log2(n >> s) + s if s > 0 else math.log2(n)

def up4(O):
    """time_log2 rounded up at the 4th decimal, T <= O/430 + 2^38, integer test:
    smallest k with (O + 430*2^38)^10000 <= 430^10000 * 2^k."""
    N = O + 430 * P38
    k = math.ceil(10000 * (lg(N) - math.log2(430))) - 2
    lhs = N ** 10000
    rhs430 = 430 ** 10000
    while not (lhs <= rhs430 << k):
        k += 1
    assert lhs <= rhs430 << k and not (lhs <= rhs430 << (k - 1))
    return k, lg(Fr(N, 430))

def show(name, O):
    k, l = up4(O)
    print(f"{name}: O = {O:,}\n   log2 T = {l:.10f}  -> {k // 10000}.{k % 10000:04d} "
          f"(integer test passes at 2^{k}/10000, fails at {k-1})")
    return k

# ---------------- GPT Sol AP section 3 (lines 46-81) ----------------
a = 99033509302
Gs = 2**32
J = -((-2**95) // ((2**21 - 1) * a))          # ceil(1/(2*Gsize*mu0)), mu0=(2^21-1)a/2^128
assert J == 190738216507
Bf = J * Gs
assert Bf == 819214401994932355072
Lf = -((-17 * Bf * 312881258079) // 2**52)     # ceil((17/16)*Bf*312881258079/2^48)
assert Lf == 967534087615711559
S64 = 417832691590563484145792
Q0 = 2**46 + 2**20 + 3 * 2**26 + 40
assert Q0 == 70368946552872
O_AP = S64 + Q0 + 4096 * J + 303 * Bf + 144164 * (Lf + 1) + 8
assert O_AP == 805538240453692110434000
print("AP terms: S64 %.2f%%, 303Bf %.2f%% (of which 80Bf %.2f%%, 117Bf %.2f%%, 106Bf %.2f%%), passes %.2f%%" % tuple(
    100 * x / O_AP for x in (S64, 303 * Bf, 80 * Bf, 117 * Bf, 106 * Bf, 144164 * (Lf + 1))))
show("AP conditional (as filed by Sol)", O_AP)

# ---------------- cloud batch-S universal bound (section 6-7) ----------------
N0 = 2**32
I29E = 10793677616                              # 29I+E <= 10,793,677,616 (every q)
def C_cloud(m):  # 20N0 + 29I + E + 4m + 5R + 27 with R <= N0
    return 20 * N0 + I29E + 4 * m + 5 * N0 + 27
assert C_cloud(2**20) == 118172054347
# ---------------- Astra mean (Result / section 4) ----------------
def C_astra_mean(m):
    return Fr(355046943117547601, 4194304) + 7 * m
assert abs(float(C_astra_mean(0)) - 84649787692.43898) < 1e-3

m = 2**21
print(f"cloud universal C(2^21) = {C_cloud(m):,}  = {Fr(C_cloud(m), N0).__float__():.6f} per g, log2 {lg(C_cloud(m)):.6f}")
print(f"Astra mean     C(2^21) = {float(C_astra_mean(m)):,.5f} = {float(C_astra_mean(m) / N0):.6f} per g, log2 {lg(C_astra_mean(m)):.6f}")
print(f"pkg16f table row per frame 512*2^32 = {512 * N0:,} (log2 41)")

# AP ceiling: pretend the WHOLE 117/G scan is replaced by one batch sweep per frame,
# keep 80/G (target generation + buckets) and 106/G (test2), 4096/O and all passes.
O_AP_cloud = S64 + Q0 + 4096 * J + 186 * Bf + J * C_cloud(m) + 144164 * (Lf + 1) + 8
show("AP conditional, ceiling with cloud universal sweep for all of 117/G", O_AP_cloud)
O_AP_astra = S64 + Q0 + 4096 * J + 186 * Bf + math.ceil(J * C_astra_mean(m)) + 144164 * (Lf + 1) + 8
show("AP conditional, ceiling with Astra MEAN sweep for all of 117/G", O_AP_astra)

# ---------------- pkg16f Section 11 ----------------
S = 498959033940035296819072
FRAMES = -((-6643392 * 2**101) // (3125 * 1033 * (2**21 - 1)))
assert FRAMES == 2487937099176099696050654
REC = 53 * 2**26
per_frame = 4096 + 512 * 2**32 + 64 * REC + 8192 * 2**21
assert per_frame == 2443836395520
O_16f = S + 2**46 + FRAMES * per_frame
assert O_16f == 6080111232731503201962608254739666816
k16 = show("pkg16f filed (table built, proved rho<=3,071)", O_16f)
assert k16 == 1134454

# (a) pkg16f's own unclaimed variant (proof.md 1633-1636): compute K_O(g*) alone,
#     charged the full 512 per-g allowance of 9.5 once per frame instead of 512*2^32.
pf_k = 4096 + 512 + 64 * REC + 8192 * 2**21
O_16f_k = S + 2**46 + FRAMES * pf_k
print(f"pkg16f K*-only per frame = {pf_k:,}")
show("pkg16f with K*-only (no table)", O_16f_k)
# (b) for reference only: table row replaced by the cloud universal sweep at m=2^21
pf_c = 4096 + C_cloud(m) + 64 * REC + 8192 * 2**21
show("pkg16f with cloud sweep in place of the table (not needed)", S + 2**46 + FRAMES * pf_c)
# (c) LEAD ONLY, unverified design: step 3 visits the 2^21 c of Q* and solves
#     H = K* in closed form (b = ROR12((u-K*) XOR c), a = b+u+w5, z = ROR8(a XOR d)),
#     then looks (c,z) up in an index of the E1 record table built once (charged 2^46 more).
#     512 machine units per c is an assumed allowance, not a derived one.
pf_lead = 4096 + 512 + 512 * 2**21 + 8192 * 2**21
show("LEAD: pkg16f, K*-only + per-c closed-form step 3 (assumed 512/c)", S + 2**46 + 2**46 + FRAMES * pf_lead)
