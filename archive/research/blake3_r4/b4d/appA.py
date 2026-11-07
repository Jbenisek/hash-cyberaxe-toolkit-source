from fractions import Fraction
from math import log, exp, log2, factorial

PH, FILT, LOOP, LANES = 24422, 34, 3, 256      # operations of the bit-sliced step (generator), stage-1 test, loop control, lanes
GEN_CALLS = 99448                               # generator primitive calls, both passes (the C port; 2 x 49,724 in python3 bsrho.py --ledger)
PH7, EXTRA, PASSES = 836, 64, 2                            # packed recovery circuit (with the 8 XORs of q), extra operations per recovery batch
N_BITS, S1, W, KAPPA = 256, 32, 90, 13          # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 1
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, SPARE = 36, 2043, 800 * 32, 16384, 10, 0, 64
EPS, HZ, GRAIN = 1e-3, 257 / 2, 10 ** 24        # Lemma 2 tail budgets, weight of a squared trail length, B is a multiple of GRAIN
body = PH + FILT + LOOP                                        # one batch = one loop body = 24,459 operations
code_bytes = (body + OTHER_CODE) * INSTR
tmax = ((1 << 20) - SPARE - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY  # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


def zq(q, uc, uh, n):         # Chernoff quantile at EPS (units L^2) of the sum of n independent z(u) = HZ m^2 + 2 q (m - uh)+, m = min(u, uc), u ~ Exp(1)
    k = 1500
    h = uc / k
    us = [(i + .5) * h for i in range(k)]
    zs = [HZ * u * u + 2 * q * max(0.0, u - uh) for u in us]
    zc = HZ * uc * uc + 2 * q * (uc - uh)

    def f(lam):
        a = [lam * z - u for z, u in zip(zs, us)]
        m = max(max(a), lam * zc - uc)
        return (n * (m + log(sum(exp(x - m) for x in a) * h + exp(lam * zc - uc - m))) - log(EPS)) / lam
    lo, hi = -16.0, -4.0
    for _ in range(50):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        lo, hi = (lo, m2) if f(exp(m1)) < f(exp(m2)) else (m1, hi)
    return f(exp((lo + hi) / 2))


def plower(Tp, q):            # the lower bound of Lemma 2 on the success probability, q = Q / L
    L = Fraction(1 << D, Tp)
    c = -(-KAPPA * L.numerator // L.denominator)
    uc, uh = float((c + SB) / L), float((c // 2) / L)
    k = int(q) + 1
    while tail_log2(q, k) > log(EPS, 2):
        k += 1
    z = zq(q, uc, uh, k - 1 + CMAX + LANES)
    l2n = float(L * L / Nn)
    kap = (2 * q * uc + HZ * uc * uc + 2 * q * (uc - uh)) * l2n
    w = 1.0
    for _ in range(100):
        w = exp(w * kap)
    s0 = q * q / 2
    th = l2n * (w * (s0 - z - CMAX * uc * q) - (w - 1) * s0)
    mu = q * exp(-KAPPA)
    cuts = 1 - sum(exp(-mu) * mu ** j / factorial(j) for j in range(CMAX + 1))
    keyfm = tmax * (tmax - 1) / 2 * 2.0 ** -(min(64 - (Tp - 1).bit_length(), N_BITS - D) + log2(Tp))
    return 1 - exp(-th) - 2 * EPS - cuts - uc * q * l2n - keyfm - 2.0 ** tail_log2(q, tmax - 59) - (k + CMAX + LANES) * exp(-KAPPA) * float(SB / L) - 2.0 ** -100


def plan_tp(Tp):              # the least B (a multiple of GRAIN) with plower >= 0.39
    L = Fraction(1 << D, Tp)
    lo, hi = 1.0, tmax + 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if plower(Tp, mid) >= 0.39 else (mid, hi)
    b = -(-int(hi * L / LANES) // GRAIN) * GRAIN
    while plower(Tp, float(b * LANES / L)) < 0.39:
        b += GRAIN
    return L, b, -(-KAPPA * L.numerator // L.denominator)


lo, hi = 1.0, tmax + 1.0                                       # the largest mean number of trails the table holds (tail within 2^-40)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
Tp = next(t for t in range(120, 0, -1) if plower(t, lo) >= 0.39)  # the largest Tp that reaches 0.39 at that mean
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + PH)
rows = [("main loop: B * 24459", body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("cut trails: 1 * 4200", CMAX * CUTOPS),
        ("recovery: 2 * (c + 2^48) * (836 + 64) + 600", PASSES * capr * (PH7 + EXTRA) + 600),
        ("setup and generator", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE)
print("P_lower = %.5f" % plower(Tp, float(B * LANES / L)))
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 846
a = (N ** P // C ** P).bit_length() - 1                        # 2^a * C^P <= N^P < 2^(a+1) * C^P
while (1 << (a + 1)) * C ** P <= N ** P:
    a += 1
while (1 << a) * C ** P > N ** P:
    a -= 1
print("certificate: 2^%d * %d^%d <= N^%d < 2^%d * %d^%d" % (a, C, P, P, a + 1, C, P))
print("log2(N/C) = %.10f" % (log2(N) - log2(C)))
print("time_log2 = %.5f" % ((a + 1) / P))
