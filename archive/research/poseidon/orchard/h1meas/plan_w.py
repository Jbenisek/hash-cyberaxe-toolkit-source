"""Lemma 2 parameters (corrected conditional DP bounds) for a random function on N points, D distinguished points.
theta_lo = (D - SMAX) / N <= P(next fresh value is a DP | any history of at most SMAX values)
theta_hi = D / (N - SMAX) >= the same probability.
d = ceil(KD / theta_lo), gmax = ceil(H / theta_lo); S = n + d <= SMAX;
eps = e^-KD + n d / N + (S theta_hi + 1) e^-H + e^-TAB;  success >= 1 - exp(-n(n+1)/2N) - n/N - eps;
table overflow: Chernoff on Binomial(S, theta_hi) at mcap + 1 must be <= e^-TAB.
Usage: python3 plan_w.py w  (width ladder: N = 2^w, h = w/2, T = 2^10, mcap from Chernoff)  |  python3 plan_w.py real
"""
import sys, json
from decimal import Decimal, getcontext
from math import log, log2, sqrt, exp, ceil

getcontext().prec = 80
KD, H, TAB = 8, 18, 100


def e(x):
    return (-Decimal(x)).exp()


def bound(n, d, N, D, SMAX):
    th_hi = Decimal(D) / (Decimal(N) - SMAX)
    eps = e(KD) + Decimal(n) * d / N + ((n + d) * th_hi + 1) * e(H) + e(TAB)
    return 1 - e(Decimal(n) * (n + 1) / (2 * Decimal(N))) - Decimal(n) / N - eps, eps


def plan(N, D, SMAX, grain, mcap=None):
    d = -(-KD * N // (D - SMAX))
    gmax = -(-H * N // (D - SMAX))
    nf = 0.9 * sqrt(N)                    # float guess, then the exact search for the least multiple of grain
    for _ in range(60):
        epsf = exp(-KD) + nf * d / N + ((nf + d) * D / N + 1) * exp(-H) + exp(-TAB)
        nf = sqrt(2 * N * (-log(0.61 - nf / N - epsf)))
    k = max(1, int(nf // grain) - 2)
    while bound(k * grain, d, N, D, SMAX)[0] < Decimal("0.39"):
        k += 1
    while k > 1 and bound((k - 1) * grain, d, N, D, SMAX)[0] >= Decimal("0.39"):
        k -= 1
    n = k * grain
    succ, eps = bound(n, d, N, D, SMAX)
    S = n + d
    assert S <= SMAX
    th_hi = D / (N - SMAX)
    mu = S * th_hi
    if mcap is None:                      # least cap whose Chernoff tail is below e^-TAB
        mcap = int(mu)
        while -mu + (mcap + 1) * (1 + log(mu / (mcap + 1))) > -TAB:
            mcap += 1
    lch = -mu + (mcap + 1) * (1 + log(mu / (mcap + 1)))
    assert lch <= -TAB
    return {"N_log2": log2(N), "D": D, "theta": D / N, "theta_log2": log2(D / N), "SMAX_log2": log2(SMAX), "n": n, "d": d,
            "gmax": gmax, "S": S, "mcap": mcap, "mean_stored": mu, "ln_P_table": lch, "eps": float(eps),
            "success_lower_bound": float(succ), "success_lower_bound_decimal": str(succ)[:22]}


if __name__ == "__main__":
    if sys.argv[1] == "real":
        P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
        T = 27554
        print(json.dumps(plan(P, ((1 << 126) + 1) * T, 1 << 128, 1 << 100, mcap=int(sys.argv[2]) if len(sys.argv) > 2 else None), indent=1))
    else:
        w = int(sys.argv[1]); h = w // 2
        N = 1 << w; T = 1 << 10; D = T << (w - h)
        out = plan(N, D, 1 << (h + 3), 1)
        out.update({"w": w, "h": h, "T": T})
        print(json.dumps(out))
