"""Exact D19-style low-degree (FES) ledger for SHA3-256 reduced to r rounds, r=3..7.

Generalizes research/sol_answer_D19_sha3r6_lowdegree.md (175-plane vertical cone, transpose,
140-bit-key birthday) from the r=6 / degree-8 case to any r. The ONLY things that change with r:
  - chi_r-input degree D = 2^(r-3)              (rounds 0-1 affine on W40, each chi doubles)
  - uncached FES chain sum  sum_L = sum_p C(n,p)*min(D,p)
  - degree-dependent setup constants P_D, J_D, V_D
  - per-point evaluation schedule length (r-1 full rounds + 1 linear step)
  - full-collision verification cost (two r-round permutations)
The 175-plane cone, the 4656 chi/transpose, the field dim n=40, and the 256-bit / 140-bit-key
birthday (G, Q, R129, R140, B) are the SAME for every r (digest is always 256 bits, key 140 bits).

Validation: r=6 must reproduce D19's N_v=19621183271953275558043014167496083929897 and 123.18243.
All integer, exact. Labels in the printout: COMPUTED here = the arithmetic; the formulas are DERIVED
from D19 (which labels its own pieces PROVED/DERIVED).
"""
from math import comb, log2
from fractions import Fraction

n = 40  # certified W40 dimension (D19 Section 1, COMPUTED there)

# --- birthday block: identical for every r (256-bit digest, 140-bit key, success>=0.39) ---
G    = 1202983983186596773302061
Q    = G * (1 << 48)
R129 = 84236407641058913330192574580177777103
R140 = 41131058418485810217402188405172195
B    = 1 << 129
ONCE = (1 << 70) + 16
assert Q == 338609888650739515842329177253285462016

def deg(r):            # chi_r-input degree
    return 1 << (r - 3)

def sum_L(D):          # sum_{i=1}^{2^n-1} min(D, popcount(i))  (exact, grouped by popcount)
    return sum(comb(n, p) * min(D, p) for p in range(1, n + 1))

def Fv(D):             # D19 Section 5 vertical FES per 256-coset group (175 planes, 39 retained)
    return 175 * (3 * sum_L(D) + ((1 << n) - 1)) - 78 * ((1 << n) - 1)

CHITR = 4656 * (1 << n)      # chi/transpose per group, D19 Section 5 (r-independent)

def P_D(D): return sum(comb(n, j) for j in range(0, D + 1))
def J_D(D): return sum(j * comb(n, j) for j in range(1, D + 1))
def V_D(D):                  # D19 Section 2 closed form (no 76M-subset enumeration)
    tot = 0
    for j in range(1, D + 1):
        for r2 in range(0, min(j, n - j) + 1):
            inner = sum(comb(r2, k) for k in range(0, min(r2, D - j) + 1))
            tot += comb(j, r2) * comb(n - j, r2) * inner
    return tot

def eval_cost(r):            # D19 Section 6 per-point: 28 lane-init + (r-1) full rounds + 1 linear step + 8 pack + 4 ld/st
    return 206 + (r - 1) * 242          # r=6 -> 1416

def Sv(r, D):                # D19 Section 6 setup upper bound
    A = 256 * G
    pd, jd, vd = P_D(D), J_D(D), V_D(D)
    return A * (eval_cost(r) * pd + 2 * jd + 544) \
         + G * (1282 * 175 * pd + 4 * 175 * jd + 2 * 175 * vd + 175)

def V_ver(r):                # full-collision verification: two r-round perms (271 ops/round) + 844
    return 2 * (271 * r) + 844          # r=6 -> 4096

def ledger(r):
    D = deg(r)
    Nv = (G * Fv(D) + G * CHITR + Sv(r, D)
          + 13 * Q + 13 * R129 + V_ver(r) * R140 + 3 * B + ONCE)
    return D, Nv

def log2_floor_frac(N, denom=1):
    """log2(N/denom) to 5 dp via exact integer power comparison (same method as D19)."""
    # find integer part
    val = Fraction(N, denom)
    # binary search on 5-dp resolution using integer powers: compare val^100000 vs 2^k
    K = 100000
    num = val.numerator ** K
    den = val.denominator ** K
    # largest integer m with 2^m <= num/den  ->  2^m * den <= num
    lo, hi = 0, 500 * K
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if (den << mid) <= num:
            lo = mid
        else:
            hi = mid - 1
    return lo / K  # = floor(K*log2)/K  (rounded down); D19 rounds up, we report both-ish

# validation against D19 r=6
D6, N6 = ledger(6)
EXPECT = 19621183271953275558043014167496083929897
print(f"VALIDATE r=6: D={D6}  N={N6}")
print(f"             D19 N_v ={EXPECT}  match={N6==EXPECT}")
s6 = log2_floor_frac(N6, 1626)
print(f"             time_log2 (/1626) = {s6:.5f}   (D19 states 123.18243, rounded up)")
print()

print("r | D=2^(r-3) | N (word ops, exact) | log2(N) word-ops | C_r=271r | log2(N/C_r) units | track?")
rows = []
for r in (3, 4, 5, 6, 7):
    D, Nv = ledger(r)
    Cr = 271 * r
    lw = log2_floor_frac(Nv, 1)
    lu = log2_floor_frac(Nv, Cr)
    track = {5: "r5 (1355)", 6: "r6 (1626)"}.get(r, "none")
    rows.append((r, D, Nv, lw, Cr, lu, track))
    print(f"{r} | {D:>2} | {Nv} | {lw:.5f} | {Cr} | {lu:.5f} | {track}")

print()
print("component breakdown log2 (word ops) per r:")
print("r | G*Fv | G*chiTr | Sv | 13Q | 13R129 | Vver*R140 | 3B | dominant")
for r in (3, 4, 5, 6, 7):
    D = deg(r)
    parts = {
        "G*Fv":      G * Fv(D),
        "G*chiTr":   G * CHITR,
        "Sv":        Sv(r, D),
        "13Q":       13 * Q,
        "13R129":    13 * R129,
        "Vver*R140": V_ver(r) * R140,
        "3B":        3 * B,
    }
    dom = max(parts, key=parts.get)
    cells = " | ".join(f"{log2_floor_frac(v,1):.2f}" for v in parts.values())
    print(f"{r} | {cells} | {dom}")
