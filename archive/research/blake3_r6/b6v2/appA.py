from fractions import Fraction
from math import log, exp, log2, expm1, log1p

PH, FILT, LOOP, LANES = 38790, 34, 3, 256      # operations of the bit-sliced step (generator), stage-1 test, loop control, lanes
GEN_CALLS = 156984                              # generator primitive calls, both passes (the C port; 2 x 78,492 in python3 bsrho.py --ledger)
PH7, EXTRA, PASSES = 1307, 64, 2                            # packed recovery circuit (with the 8 XORs of q), extra operations per recovery batch
N_BITS, S1, W, KAPPA = 256, 32, 90, 13          # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 1
MEM_LIMIT = 1635324                                       # bytes (2^20 is not binding at 6 rounds, proof 3.8)
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, SPARE = 36, 2514, 800 * 32, 16384, 10, 0, 64
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
EPS, HZ, GRAIN = 1e-3, 257 / 2, 10 ** 24        # Lemma 2 tail budgets, weight of a squared trail length, B is a multiple of GRAIN
body = PH + FILT + LOOP                                        # one batch = one loop body (PH + FILT + LOOP operations)
code_bytes = (body + OTHER_CODE) * INSTR
tmax = (MEM_LIMIT - SPARE - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY  # table entries that fit in MEM_LIMIT bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


def zq(q, uc, uh, n):         # (z*, lam): P(sum of n i.i.d. block terms z(min(beta, c + S)) / L^2 > z*) <= EPS (Chernoff), beta geometric of mean L
    k = 20000                 # UPPER bound on the MGF: beta <= L E + 1, E ~ Exp(1); exp(lam z(u) - u) is convex, so the trapezoid rule (chords) bounds
    h = uc / k                # its integral from above; 1 + 2^-30 covers float rounding and the 1/L shifts; certify() below redoes it in decimals
    us = [i * h for i in range(k + 1)]
    zs = [HZ * u * u + 2 * q * max(0.0, u - uh) for u in us]

    def f(lam):
        a = [lam * z - u for z, u in zip(zs, us)]
        m = max(a)
        e = [exp(x - m) for x in a]
        return (n * (m + log(((sum(e) - (e[0] + e[-1]) / 2) * h + e[-1]) * (1 + 2.0 ** -30))) - log(EPS)) / lam
    lo, hi = -16.0, -4.0
    for _ in range(50):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        lo, hi = (lo, m2) if f(exp(m1)) < f(exp(m2)) else (m1, hi)
    return f(exp((lo + hi) / 2)), exp((lo + hi) / 2)


def plower(Tp, q):            # the lower bound of Lemma 2 (v2) on the success probability, q = Q / L
    L = Fraction(1 << D, Tp)
    c = -(-KAPPA * L.numerator // L.denominator)
    uc, uh = float((c + SB) / L), float((c // 2) / L)
    k = int(q) + 1
    while tail_log2(q, k) > log(EPS, 2) - 1e-6:                 # lottery count N1 ~ Binomial(Q, 1/L) <= k - 1 except with probability EPS
        k += 1
    z = zq(q, uc, uh, k - 1 + LANES)[0]                         # at most k - 1 + LANES lottery blocks
    l2n = float(L * L / Nn)
    kap = (2 * q * uc + HZ * uc * uc + 2 * q * (uc - uh)) * l2n
    w = 1.0
    for _ in range(100):
        w = exp(w * kap)
    w *= 1 + 2.0 ** -40                                          # ln w >= w kap
    s0 = q * q / 2
    th = l2n * (w * (s0 - z - CMAX * (q * uc + min(q * (uc - uh), z / (LANES + 1) + q * float(SB / L)))) - (w - 1) * s0)   # cut trail (Step 5 (c))
    p, hq, ql, n2 = exp(-KAPPA), s0 * l2n, q * l2n, k + LANES + 1
    cuts = -expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p))   # P(Bin(n2, p) >= 2): fresh cut trails (Step 5b (i))
    cuts += ql * (1 + (2 + KAPPA) * exp(-KAPPA / 2) + 2 * hq) + hq * p * (3 + 2 * KAPPA)   # colliding cut trails: S, X, J2a, J2b, Y (Step 5b (ii))
    keyfm = tmax * (tmax - 1) / 2 * 2.0 ** -(min(64 - (Tp - 1).bit_length(), N_BITS - D) + log2(Tp))
    return 1 - exp(-th) - 2 * EPS - cuts - uc * q * l2n - keyfm - 2.0 ** tail_log2(q, tmax - 59) - n2 * p * float(SB / L) - 2.0 ** -90


def plan_tp(Tp):              # the least B (a multiple of GRAIN) with plower >= 0.39
    L = Fraction(1 << D, Tp)
    lo, hi = 1.0, tmax + 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if plower(Tp, mid) >= P_MIN else (mid, hi)
    b = -(-int(hi * L / LANES) // GRAIN) * GRAIN
    while plower(Tp, float(b * LANES / L)) < P_MIN:
        b += GRAIN
    return L, b, -(-KAPPA * L.numerator // L.denominator)

def certify(Tp, B, K=20000):  # Lemma 2 v2 in exact rationals and 60-digit decimals (every exp and ln correctly rounded), results moved outward by 1e-40
    from decimal import Decimal as Dm, getcontext, localcontext, ROUND_CEILING, ROUND_FLOOR
    getcontext().prec = 60
    up = lambda x: x * (1 + Dm("1e-40")) + Dm("1e-58")

    def fd(x, u):             # Fraction -> Decimal rounded up (u) or down
        with localcontext() as cx:
            cx.rounding = ROUND_CEILING if u else ROUND_FLOOR
            return Dm(x.numerator) / Dm(x.denominator)
    ex = lambda x: up(fd(x, True).exp())                         # upper bound on exp(x), x rational
    L = Fraction(1 << D, Tp)
    th_D, Q, Np = 1 / L, LANES * B, Fraction(Nn) * (1 - 1 / L)
    q = Q / L
    c = -(-KAPPA * L.numerator // L.denominator)
    h, M, HF = c // 2, c + SB, Fraction(LANES + 1, 2)
    qu, qd, lnE = fd(q, True), fd(q, False), Dm("0.001").ln()
    k = int(q) + 1                                               # P(N1 >= k) <= e^-q (e q / k)^k <= EPS
    while up(-qd + k * (1 + (qu / k).ln())) > lnE * (1 + Dm("1e-40")):
        k += 1
    n = k - 1 + LANES
    lam = Dm(repr(zq(float(q), float(M / L), float(h / L), n)[1]))
    ucu, ucd, uhd, dl = fd(M / L + th_D / 2, True), fd(M / L + th_D / 2, False), fd(h / L, False), fd(3 * th_D / 2, True)
    with localcontext() as cx:
        cx.prec, cx.rounding = 40, ROUND_CEILING
        hh = ucu / K
    with localcontext() as cx:
        cx.prec = 100
        ys = [i * hh for i in range(K + 1)]                      # exact nodes, K hh >= uc + 1 / (2 L)
    zeta = lambda y: Dm(HF.numerator) / Dm(HF.denominator) * y * y + 2 * qu * max(Dm(0), y - uhd)
    ph = [(lam * zeta(y) - y).exp() for y in ys]
    mgf = up(dl.exp() * (hh * (sum(ph) - (ph[0] + ph[-1]) / 2) + (lam * zeta(ucu) - ucd + dl).exp()))
    zstar = Fraction(up((n * up(mgf.ln()) - lnE) / lam))       # P(trail sums > zstar L^2) <= EPS
    kap = fd((2 * M * Q + HF * M * (M + 1) + 2 * Q * (M - h)) / Np, True)
    w = Dm(1)
    for _ in range(200):
        w = (w * kap).exp()
    w *= 1 + Dm("1e-30")
    assert w.ln() >= w * kap                                    # ln w >= w kap0 / N'
    w = Fraction(w)
    Hs = Fraction(Q * (Q - 1), 2) + (1 << 16) * Q
    theta = (w * (Fraction(LANES * LANES * B * (B - 1), 2) - 2 * k * Q - CMAX * (M * Q + min(Q * (M - h), zstar * L * L / (LANES + 1) + SB * Q)) - zstar * L * L) - (w - 1) * Hs) / Np
    p = ex(-c * th_D)                                            # (1 - 1/L)^c <= e^(-c / L)
    p2 = ex(-(c - 1) * th_D) * fd(1 + (c - 1) * th_D / (1 - th_D), True)
    n2, H, PP = k + LANES + 1, Hs / Np, Fraction(Q * (Q - 1), 2) / Np
    kt = tmax - 59
    terms = [ex(-theta), Dm("0.002"),                            # main; finished-trail count and trail sums (EPS each)
             up(1 - (1 - p) ** n2 - n2 * p * (1 - p) ** (n2 - 1)),   # fresh cut trails: P(Bin(n2, p) >= 2)
             fd(Q * L / Np, True),                               # S: a trail closes a cycle
             fd(Q / Np, True) * fd(L, True) * ex(-(c - 2) * th_D / 2) * fd(2 + (c - 1) * th_D, True) + fd(PP, True) * p2,   # X
             fd(Q * L * H / Np + (Q + (1 << 16)) * L * PP / Np, True),   # J2a
             fd(PP * (1 - th_D), True) * p2, ex(-(c - 1) * th_D) * fd(H, True),   # J2b, Y
             fd(M * (Q + (1 << 16)) / Np, True),                 # Step 3
             fd(Fraction(tmax * (tmax - 1), 2 * Tp) / (1 << min(64 - (Tp - 1).bit_length(), N_BITS - D)), True),   # key false match
             up((-qd + kt * (1 + (qu / kt).ln())).exp()),           # table capacity
             n2 * p * fd(SB * th_D, True),                       # long finish
             fd(Fraction(Q << 16, Nn) + Fraction(Q * k, Nn) + k * k * L / Nn, True) + up((-300 + (Dm(5).exp() - 1) * fd(H, True)).exp()) + Dm(2) ** -99]
    assert Fraction(Q, 1 << 32) * Fraction(108, 1000) > 1000 and 240 * M <= Q   # stage-1 budget (Step 6): below e^-1000, inside the last term
    return 1 - sum(terms)


lo, hi = 1.0, tmax + 1.0                                       # the largest mean number of trails the table holds (tail within 2^-40)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
Tp = next(t for t in range(400, 0, -1) if plower(t, lo) >= P_MIN)  # the largest Tp that reaches 0.39 at that mean
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + PH)
rows = [("main loop: B * %d" % body, body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("cut trails: 1 * 4200", CMAX * CUTOPS),
        ("recovery: 2 * (c + 2^48) * (1307 + 64) + 600", PASSES * capr * (PH7 + EXTRA) + 600),
        ("setup and generator", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE)
print("P_lower = %.5f" % plower(Tp, float(B * LANES / L)))
pc = certify(Tp, B)
print("P_lower certified (exact rationals, 60-digit decimals) = %s" % str(pc)[:14])
assert pc >= Fraction(39, 100)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 1262
a = (N ** P // C ** P).bit_length() - 1                        # 2^a * C^P <= N^P < 2^(a+1) * C^P
while (1 << (a + 1)) * C ** P <= N ** P:
    a += 1
while (1 << a) * C ** P > N ** P:
    a -= 1
print("certificate: 2^%d * %d^%d <= N^%d < 2^%d * %d^%d" % (a, C, P, P, a + 1, C, P))
print("log2(N/C) = %.10f" % (log2(N) - log2(C)))
print("time_log2 = %.5f" % ((a + 1) / P))
