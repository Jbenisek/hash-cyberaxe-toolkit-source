from fractions import Fraction
from math import isqrt, log, log2

PH, LANES, U = 593, 7, 16                     # operations per batch (tracer), lanes, batches per loop body
N_BITS, S1, W = 256, 32, 90                   # width, filter bits, window bits; D = S1 + W = 122
KAPPA, INFLIGHT = 12, 28
LAM, CUT = Fraction(497, 1000), Fraction(15, 100000)
EVENT, STAGE2, REPLAY, EXTRA = 700, 300, 300, 64
ENTRY, INSTR, CODE_OTHER, FIXED = 25, 36, 640 + 170 + 40, 2048 + 2048
C = 638                                       # operations of the 3-round reference compression

body = U * PH + (U + (U - 1) + 1 + 2) + 3 + 1                 # batches + grouped filter + loop control + one move = 9,558
code_bytes = (body + CODE_OTHER) * INSTR
tmax = ((1 << 20) - code_bytes - FIXED) // ENTRY               # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def plan(Tp):
    L = Fraction(1 << D, Tp)                                   # trail length scale 1/theta, theta = Tp / 2^D
    ureq = isqrt(2 * Nn * LAM.numerator // LAM.denominator) + 2
    num, den = ureq + INFLIGHT * L + 1, CUT.denominator
    q = -(-(num * den) // (den - CUT.numerator))
    b = -(-q // LANES)
    b = -(-b // U) * U
    c = -(-KAPPA * L.numerator // L.denominator)
    return L, b, c


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


Tp = max(t for t in range(1, 2049)
         if float(plan(t)[1] * LANES / plan(t)[0]) < tmax + 1
         and tail_log2(float(plan(t)[1] * LANES / plan(t)[0]), tmax + 1) <= -40)
L, B, c = plan(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
rows = [("main loop: B * 9558 / 16", Fraction(body, U) * B),
        ("slice checks: ceil(B / 2^48) * 100", -(-B // SB) * 100),
        ("stage-2 events: e2max * (300 + 16 * 593 + 300)", e2max * (STAGE2 + U * PH + REPLAY)),
        ("finished trails: tmax * (700 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("recovery: (c + 2^48) * (593 + 64) + 600", (c + SB) * (PH + EXTRA) + 600),
        ("setup", 2000)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + FIXED)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P = 100000
a = (N ** P // C ** P).bit_length() - 1                        # 2^a * C^P <= N^P < 2^(a+1) * C^P
while (1 << (a + 1)) * C ** P <= N ** P:
    a += 1
while (1 << a) * C ** P > N ** P:
    a -= 1
print("certificate: 2^%d * %d^%d <= N^%d < 2^%d * %d^%d" % (a, C, P, P, a + 1, C, P))
print("log2(N/C) = %.10f" % (log2(N) - log2(C)))
print("time_log2 = %.5f" % ((a + 1) / P))
