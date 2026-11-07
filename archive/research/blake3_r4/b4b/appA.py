from fractions import Fraction
from math import isqrt, log, exp, log2

PH, FILT, LOOP, LANES = 24422, 34, 3, 256      # operations of the bit-sliced step (generator), stage-1 test, loop control, lanes
GEN_CALLS = 99448                               # generator primitive calls, both passes (the C port; 2 x 49,724 in python3 bsrho.py --ledger)
PH7, EXTRA, PASSES = 836, 64, 2                            # packed recovery circuit (with the 8 XORs of q), extra operations per recovery batch
N_BITS, S1, W, KAPPA = 256, 32, 90, 11          # width, stage-1 bits, window bits (D = 122), age cap in units of L
LAM, CUT = Fraction(497, 1000), Fraction(15, 100000)
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, SPARE = 36, 2043, 800 * 32, 16384, 10, 0, 8
TAIL_AGES = 1e-6


def inflight_m(lanes=LANES, eps=TAIL_AGES):    # smallest M with P(sum of `lanes` exponential ages > M L) <= eps (Chernoff, exact in the exponent)
    m = lanes
    while True:
        x = m / lanes
        if exp(-lanes * (x - 1 - log(x))) <= eps:
            return m
        m += 1


M = inflight_m()
body = PH + FILT + LOOP                                        # one batch = one loop body = 24,459 operations
code_bytes = (body + OTHER_CODE) * INSTR
tmax = ((1 << 20) - SPARE - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY  # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def plan_tp(Tp):
    L = Fraction(1 << D, Tp)                                   # trail length scale 1/theta, theta = Tp / 2^D
    ureq = isqrt(2 * Nn * LAM.numerator // LAM.denominator) + 2
    num, den = ureq + M * L + 1, CUT.denominator
    q = -(-(num * den) // (den - CUT.numerator))
    b = -(-q // LANES)
    c = -(-KAPPA * L.numerator // L.denominator)
    return L, b, c


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


Tp = max(t for t in range(1, 4097)
         if float(plan_tp(t)[1] * LANES / plan_tp(t)[0]) < tmax + 1
         and tail_log2(float(plan_tp(t)[1] * LANES / plan_tp(t)[0]), tmax + 1) <= -40)
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + PH)
rows = [("main loop: B * 24459", body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("cut trails: 2 * 4200", CMAX * CUTOPS),
        ("recovery: 2 * (c + 2^48) * (836 + 64) + 600", PASSES * capr * (PH7 + EXTRA) + 600),
        ("setup and generator", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("M =", M, " Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE)
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
