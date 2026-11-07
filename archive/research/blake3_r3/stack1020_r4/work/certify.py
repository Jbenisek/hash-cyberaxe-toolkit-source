# certify.py: independent recomputation of the r4 stack ledger and the exact Lemma 2 certificate (not shipped; Appendix A quotes its output)
from fractions import Fraction
from math import log, exp, log2, expm1, log1p
import json, sys

PH, PH7, LANES = 23479, 845, 256                 # gates of the step, packed recovery circuit (printed by --ledger)
GEN_CALLS1, KEY_OPS = 344207, 17750836600        # generator calls (one pass), offline key choice charge
S1, SC, W, KAPPA, N_BITS = 32, 12, 90, 20, 256
TB, META, ENTRY = 18, 3, 7
HIT, EVENT, SLOT, CUTOPS, SLICE, GEN_FACTOR, LOOP = 2800, 3800, 64, 4200, 1300, 200, 1
KR, KCHK, REC1, REC2, CHK, PROBE, RECF = Fraction(62, 5), 8192, 38, 39, 80, 100, 600
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 1
MEM, SPARE, REGFILE, COUNTERS, ADVICE = 1048576, 64, 775 * 32, 5248, 32
DELAY, SLACK, LIMIT = 3000, Fraction(1, 1024), 2
GATE, INSTR, OTHER, IMM = 5, 9, 1 + 4 + 1060 + 160 + 110, 64 * (37 - 9)   # loop, stage-1 branches + limit, handlers, setup, recovery
P_MIN, GRAIN, FINE, COARSE = 0.390000001, 10 ** 24, 20000, 2000
per, rest = (SC - 1) + 1, (S1 - SC) + 1 + LIMIT
body = PH + per + LOOP
code = (PH + S1 - 1 + PH7) * GATE + OTHER * INSTR + IMM
tmax = (MEM - SPARE - code - REGFILE - COUNTERS - ADVICE) // ENTRY
l = (tmax + 1).bit_length() - 1
KEYB = 8 * ENTRY - TB - META + l
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def tail_log2(mean, k):
    return (-mean + k * (1 + log(mean / k))) / log(2)


def plower(Tp, q):
    L = Fraction(1 << D, Tp)
    c = -(-KAPPA * L.numerator // L.denominator)
    th, Lf, cf, kr = Tp / 2.0 ** D, float(L), float(c), float(KR) * float(L)
    Q, B, Np = q * Lf, q * Lf / LANES, 2.0 ** N_BITS
    k = int(q) + 1
    while tail_log2(q, k) > -40:
        k += 1
    n2, shift = k + LANES + 1, 1 / (1 - k * Q / Np)
    pi = lambda m: exp(-m * (m - 1) / (2 * Np))
    split = max(1.0, Q - 120 * LANES * Lf)
    edges = [split * i / COARSE for i in range(COARSE + 1)] + [split + (Q - split) * i / FINE for i in range(1, FINE + 1)]
    delay, pa = 0.0, 1.0
    for b in edges[1:]:
        pb = pi(b)
        delay += (pa - pb) * exp(-th * max(0.0, B - b / LANES))
        pa = pb
    p, ql, hq = exp(-cf * th), Q * Lf / Np, Q * (Q - 1) / (2 * Np)
    p2 = exp(-(cf - 1) * th) * (1 + (cf - 1) * th / (1 - th))
    hh = (Q * (Q - 1) / 2 + 2.0 ** TB * Q) / Np
    t = [pi(Q) * shift, delay * shift, ql, (cf + SB + DELAY) * Q * p * (q + LANES) / ((1 - p) * Np), hq * p2,
         2 * hq * exp(-(kr - 1) * th) * (1 + (kr - 1) * th / (1 - th)), hq * Lf * (Q + 2.0 ** TB) / Np, 2.0 ** -40,
         -expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p)) + ql * (1 + (2 + KAPPA) * exp(-KAPPA / 2) + 2 * hq) + hq * p * (3 + 2 * KAPPA),
         tmax * (tmax - 1) / 2 * 2.0 ** -(min(KEYB - (Tp - 1).bit_length(), N_BITS - D) + log2(Tp)), 2.0 ** tail_log2(q, tmax - 59),
         Q * 2.0 ** TB / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -300 + (exp(5) - 1) * hh)) + 2.0 ** -90]
    return 1 - sum(t)


def plan_tp(Tp):
    L = Fraction(1 << D, Tp)
    lo, hi = 1.0, tmax + 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if plower(Tp, mid) >= P_MIN else (mid, hi)
    b = -(-int(hi * L / LANES) // GRAIN) * GRAIN
    while plower(Tp, float(b * LANES / L)) < P_MIN:
        b += GRAIN
    return L, b, -(-KAPPA * L.numerator // L.denominator)


def certify(Tp, B):
    from decimal import Decimal as Dm, getcontext, localcontext, ROUND_CEILING, ROUND_FLOOR
    getcontext().prec = 60
    up = lambda x: x * (1 + Dm("1e-40")) + Dm("1e-58")
    dn = lambda x: x * (1 - Dm("1e-40")) - Dm("1e-58")

    def fd(x, u):
        with localcontext() as cx:
            cx.rounding = ROUND_CEILING if u else ROUND_FLOOR
            return Dm(x.numerator) / Dm(x.denominator)
    ex = lambda x: up(fd(x, True).exp())
    L = Fraction(1 << D, Tp)
    th, Q = 1 / L, LANES * B
    Np = Fraction(Nn - Tp * (1 << (N_BITS - D)))
    q = Q / L
    c = -(-KAPPA * L.numerator // L.denominator)
    M = c + SB + DELAY
    qu, qd, lne = fd(q, True), fd(q, False), -Dm(2).ln() * 40
    k = int(q) + 1
    while up(-qd + k * (1 + (qu / k).ln())) > lne * (1 - Dm("1e-40")):
        k += 1
    n2 = k + LANES + 1
    shift = fd(1 / (1 - k * Q / Np), True)
    lam = lambda m: Fraction(m * (m - 1), 2) / Np
    pi_up = lambda m: up((-fd(lam(m), False)).exp())
    pi_lo = lambda m: dn((-fd(lam(m) + Fraction((m - 1) * m * (2 * m - 1), 6) / Np ** 2, True)).exp())
    split = max(1, Q - 120 * LANES * (1 << D) // Tp)
    E = [split * i // COARSE for i in range(COARSE + 1)] + [split + (Q - split) * i // FINE for i in range(1, FINE + 1)]
    delay, pa = Dm(0), pi_up(E[0])
    for a, b in zip(E, E[1:]):
        pb = pi_lo(b)
        R = max(0, B - (-(-b // LANES)))
        delay += (pa - pb) * ex(-th * R)
        pa = pi_up(b)
    delay = up(delay) * shift
    p = ex(-c * th)
    p2 = ex(-(c - 1) * th) * fd(1 + (c - 1) * th / (1 - th), True)
    cr = KR * L
    p2r = ex(-(cr - 1) * th) * fd(1 + (cr - 1) * th / (1 - th), True)
    Hs = Fraction(Q * (Q - 1), 2) + (1 << TB) * Q
    H, PP = Hs / Np, Fraction(Q * (Q - 1), 2) / Np
    EK = p * (fd(q, True) + LANES) / (1 - p)
    terms = dict(P_coll=pi_up(Q) * shift, P_delay=delay, P_own=fd(Q * L / Np, True), P_long=up(fd(Fraction(M * Q) / Np, True) * EK),
                 P_age=fd(PP, True) * p2, P_rec=2 * fd(PP, True) * p2r, P_dist=fd(PP * L * (Q + (1 << TB)) / Np, True), N1=Dm(2) ** -40,
                 Bin=up(1 - (1 - p) ** n2 - n2 * p * (1 - p) ** (n2 - 1)), E_S=fd(Q * L / Np, True),
                 E_X=fd(Q / Np, True) * fd(L, True) * ex(-(c - 2) * th / 2) * fd(2 + (c - 1) * th, True) + fd(PP, True) * p2,
                 E_J2a=fd(Q * L * H / Np + (Q + (1 << TB)) * L * PP / Np, True), E_J2b=fd(PP * (1 - th), True) * p2, E_Y=ex(-(c - 1) * th) * fd(H, True),
                 P_key=fd(Fraction(tmax * (tmax - 1), 2 * Tp) / (1 << min(KEYB - (Tp - 1).bit_length(), N_BITS - D)), True),
                 P_table=up((-qd + (tmax - 59) * (1 + (qu / (tmax - 59)).ln())).exp()),
                 P_tiny=fd(Fraction(Q << TB, Nn) + Fraction(k * k) * L / Np + 255 * Q / Np, True) + up((-300 + (Dm(5).exp() - 1) * fd(H, True)).exp()) + Dm(2) ** -90)
    pk = 1 - Fraction((1 << SC) - 1, 1 << SC) ** LANES
    mu = B * pk
    assert Fraction(Q, 1 << 32) * Fraction(108, 1000) > 1000 and 240 * M <= Q                  # stage-1 hit budget (Step 7)
    assert mu / (3 << 22) > 1000 and Fraction(2 * M, 1 << SC) + 3001 * pk <= mu / 2048 and Fraction(M, 1 << SC) * Fraction(386, 1000) > 1000   # passing-batch budget
    return 1 - sum(terms.values()), terms, dict(k=k, n2=n2, q=float(q), PP=float(PP), H=float(H), M=M, mu=float(mu), pk=float(pk))


lo, hi = 1.0, tmax + 1.0
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
a, b = 1500, 4095
ok = lambda t: plower(t, lo) >= P_MIN
while b - a > 1:
    mm = (a + b) // 2
    a, b = (mm, b) if ok(mm) else (a, mm)
Tp = a
L, B, c = plan_tp(Tp)
cr = -(-(KR * L.numerator) // L.denominator)
e2max = 2 * B * LANES // (1 << S1) + 64
pk = 1 - Fraction((1 << SC) - 1, 1 << SC) ** LANES
pmax = -(-((1 + SLACK) * B * pk).numerator // ((1 + SLACK) * B * pk).denominator) + 64
Dd = -(-cr // KCHK)
gen = GEN_FACTOR * (2 * GEN_CALLS1 + PH)
rows = [("main loop: (B + 3000) * %d" % body, body * (B + DELAY)),
        ("stage-1 rest: pmax * %d" % rest, pmax * rest),
        ("slice checks: ceil((B + 3000) / 2^48) * 1300", -(-(B + DELAY) // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 64 (tmax + 1))", tmax * (EVENT + SLOT * (tmax + 1))),
        ("cut trails: 1 * 4200", CMAX * CUTOPS),
        ("recovery: c_r (%d + 38) + 8192 * 80 + 17 D (%d + 39) + 16 * 100 + 600" % (PH7, PH7), cr * (PH7 + REC1) + KCHK * CHK + 17 * Dd * (PH7 + REC2) + 16 * PROBE + RECF),
        ("setup and generator", SETUP_FIXED + gen),
        ("choice of the prefix key", KEY_OPS)]
N = sum(v for _, v in rows)
print("code bytes =", code, " tmax =", tmax, " key bits =", KEYB, " Tp =", Tp, " B =", B, " c =", c, " c_r =", cr, " D =", Dd)
print("e2max =", e2max, " pmax =", pmax)
print("memory bytes (search phase) =", ENTRY * (tmax + 1) + code + REGFILE + COUNTERS + ADVICE)
print("P_lower (float) = %.10f" % plower(Tp, float(B * LANES / L)))
pc, terms, aux = certify(Tp, B)
for kk, vv in terms.items():
    print("  %-8s %s" % (kk, format(vv, ".12e")))
print("aux", aux)
print("P_lower certified =", str(pc)[:16])
assert pc >= Fraction(39, 100)
for kk, vv in rows:
    print(kk.ljust(80), vv)
print("N =", N)
P, C = 100000, 846
a = (N ** P // C ** P).bit_length() - 1
while (1 << (a + 1)) * C ** P <= N ** P:
    a += 1
while (1 << a) * C ** P > N ** P:
    a -= 1
print("certificate: 2^%d * %d^%d <= N^%d < 2^%d * %d^%d" % (a, C, P, P, a + 1, C, P))
print("log2(N/C) = %.10f" % (log2(N) - log2(C)))
print("time_log2 = %.5f" % ((a + 1) / P))
print("preprocessing log2 units (setup + generator + key choice) = %.4f" % log2((SETUP_FIXED + gen + KEY_OPS) / C))
