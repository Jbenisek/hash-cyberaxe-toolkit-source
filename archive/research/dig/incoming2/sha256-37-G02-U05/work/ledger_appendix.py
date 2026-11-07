from fractions import Fraction as Fr
# Exact ledger of the counted program (proof.md Sections 9-11). Integers and Fractions only.
C = 2644                                   # reference cost of one target compression, in word operations
# stage prices (primitives of the straight-line text, proof.md Section 9; the plane-program counts are measured by lowm.py and asserted at every execution)
W6_OPS = {(3, False): 404, (3, True): 415, (1, False): 420, (1, True): 431}                              # W6 program of a batch of reps by (cube bits k, all 32 sums needed)
SUBF = {(3, 1): 94, (3, 4): 89, (3, 5): 95, (3, 8): 88, (3, 9): 94, (3, 12): 89, (3, 13): 95, (1, 1): 94}                              # F6 of W - cu by (k, cu)
F7_OPS, SCAN_FIX, SCAN_LANE, CLS_LANE = 166, 70, 8, 6
EXTR, PLACE, GROUP_BODY, PAD_OPS, PROBE = (1, 2, 2, 1), 7, 31, 7, (11, 12, 12, 12)
SURV_FIX, SURV_LANE, EX_OPS, RARE_LOOKUP, RECOMP, ROWCHECK, ROWCOMP = 8, 7, 34, 2, 35, 53, 106
CPREP, CF_CLASS, SWEEP_OVH, FIXED, RUN_CU, SPILL = 410, 6, 195, 615, 7, 64
SP_LOADS = {3: 30, 1: 34}             # per batch: stored planes of the reps (14 or 16) with their address adds, two pointers
# the 222 classes: (variants, cube bits k, classes): lists 0, 1 / 2, 3, 4 / 5, 6 / 7, 8, 9 (proof.md Section 5.3)
CLASS_TYPES = [(3456, 3, 85), (3456, 1, 26), (3600, 3, 85), (3584, 1, 26)]
CUBE = {3: 13, 1: 1}                        # the cube bits {0, 2, 3} or {0} as a mask
NCLS = 222; NVAR = sum(n * c for n, k, c in CLASS_TYPES); NFEAS = 32
P7 = Fr(68157440, 1 << 32); P6 = Fr(287309824, 1 << 32); R16F = Fr(2097152, 1 << 32); MU = Fr(NFEAS, 256); PNZ = Fr(1521152, 1 << 24)
# allowances (unchanged) and the success-floor constants
A_C, A_S, DEV, PRE, FIN = 1 << 60, 1 << 50, 1 << 40, 1 << 38, 1600
Q3 = Fr(1587616940162, 1 << 112)                 # q3 = 2^-71.47 rounded down to a 40-bit mantissa (2^40.53 / 2^112)
MU0 = Fr(24779247, 50000000)                   # smallest 8-decimal number above -ln(0.61 - PCAP_ASSUMED - 2^-60) / (1 - 2^-10.4)  (Appendix C)
SLACK = Fr(1, 4096); PCAP_ASSUMED = Fr(28103, 50000000)
def subsets(mask): return [s for s in range(16) if s & ~mask == 0]
def lane_costs(nls): return sum(SCAN_LANE + EXTR[L // 64] for nl in nls for L in range(nl))   # scan and extraction of every lane of the batches of reps
def memcost(j): return PLACE if j == 0 else 12 * (1 << j) - 2                                 # members of a rep with |I| = j
def class_det(n, k, Q0):
    # operations of a passing class with relevant cube bits Q0 that do not depend on which reps are good (2^|Q0| runs)
    nr = n >> k; nb = (nr + 255) // 256; nsw = (nb + 1) // 2; part = 1 if nr % 256 else 0; full = Q0 != 0
    tot = CPREP + CF_CLASS + nsw * SWEEP_OVH + nb * (SP_LOADS[k] + W6_OPS[(k, full)] + SCAN_FIX) + part
    if full:
        tot += 2 * nb * SPILL
        for cu in subsets(Q0):
            if cu: tot += nb * (RUN_CU + SUBF[(k, cu)] + SCAN_FIX) + part
    return tot
def class_run_cost(n, k, Q0):
    # scan, extraction and members of one run if all reps are good (times p6 for the expectation)
    nr = n >> k; nb = (nr + 255) // 256; nls = [min(256, nr - 256 * b) for b in range(nb)]
    return lane_costs(nls) + nr * memcost(k - bin(Q0).count('1'))
def class_expected(n, k):
    # Q0 is uniform among the submasks of the cube given that the class passes (x mod 16 is uniform)
    return sum(Fr(1, 1 << k) * (class_det(n, k, Q0) + (1 << bin(Q0).count('1')) * P6 * class_run_cost(n, k, Q0)) for Q0 in subsets(CUBE[k]))
def class_max(n, k):
    return max(class_det(n, k, Q0) + (1 << bin(Q0).count('1')) * class_run_cost(n, k, Q0) for Q0 in subsets(CUBE[k]))
perclass = pairs = Fr(0); vmax = Fr(0)
c3b_row = ROWCOMP + ROWCHECK + 1; c3b_pair = 201 + RECOMP + 1 + RARE_LOOKUP; c3b_l = 2 + 6 + 2 * c3b_row
for n, k, cnt in CLASS_TYPES:
    perclass += cnt * P7 * class_expected(n, k); pairs += cnt * P7 * P6 * n; vmax += cnt * class_max(n, k)
ct_var = CLS_LANE * NCLS * P7
groups = (pairs + 3) / 4; lanes = 4 * groups
grp = groups * (GROUP_BODY + sum(PROBE)) + PAD_OPS
surv = lanes * (PNZ * SURV_FIX + MU * (SURV_LANE + EX_OPS))
rare = lanes * R16F * (c3b_pair + c3b_l + 19 * Fr(1, 512) * c3b_row)
vbar = ct_var + perclass + grp + surv + rare            # expected data-dependent operations per first block
g = pairs                                               # expected good pairs per first block
vlanes = NVAR + 3                                       # one first block's maximal data-dependent work: all classes pass, all variants good, every l survives, every probe hits
vmax_fb = vmax + Fr(vlanes, 4) * (GROUP_BODY + sum(PROBE)) + PAD_OPS + vlanes * (SURV_FIX + NFEAS * (SURV_LANE + EX_OPS)) \
          + vlanes * Fr(11, 10) * (c3b_pair + NFEAS * (c3b_l + 19 * c3b_row)) + 24 + CLS_LANE * NCLS
NFB = int(-(-MU0 // (g * 32 * Q3)))                     # first blocks: E[successes] = NFB g 32 q3 >= MU0
PCAP = vmax_fb / (SLACK * SLACK * NFB * vbar)           # Chebyshev bound of the work-cap overflow
assert PCAP <= PCAP_ASSUMED
V_MAX = int(-(-(1 + SLACK) * NFB * vbar // 1))          # cap on the counted data-dependent operations
ROWS = [("A_C: characteristic search (units x C)", A_C * C), ("A_S: Step-1 solve (units x C)", A_S * C), ("DEV: development (units x C)", DEV * C),
        ("N_FB first-block compressions (units x C)", NFB * C), ("fixed operations: N_FB x FIXED", NFB * FIXED), ("V_MAX: data-dependent operations", V_MAX),
        ("overshoot past the cap: vmax_fb", -(-vmax_fb // 1)), ("PRE: preprocessing", PRE), ("FIN: final verification", FIN), ("6 further compressions (units x C)", 6 * C)]
ROWS = [(a, int(b)) for a, b in ROWS]
N = sum(b for _, b in ROWS)
P = 100000
a = (N ** P // C ** P).bit_length() - 1
while (1 << (a + 1)) * C ** P <= N ** P: a += 1
while (1 << a) * C ** P > N ** P: a -= 1
claim = Fr(-(-(a + 1) * 10 ** 5 // P), 10 ** 5)
w = max(len(k) for k, _ in ROWS)
for k, v in ROWS: print(k.ljust(w), format(v, ","))
print("N_FB = %d, g = %s, vbar = %s, Pcap = %s <= %s" % (NFB, float(g), float(vbar), float(PCAP), float(PCAP_ASSUMED)))
print("N = %d" % N)
print("certificate: 2^%d * %d^%d <= N^%d < 2^%d * %d^%d" % (a, C, P, P, a + 1, C, P))
print("time_log2 = %.5f" % float(claim))
