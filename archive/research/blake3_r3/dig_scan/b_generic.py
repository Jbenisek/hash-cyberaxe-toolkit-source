from common import *
import json, random
from math import exp, lgamma, log, sqrt
B = base()
def sc(**kw): return led(**kw)["score"]
def dt(**kw): return sc(**kw) - B["score"]
res = {}

def pois_sf(mu, k):
    """P(Poisson(mu) >= k) by log-sum (k > mu)."""
    if k <= mu: return 1.0
    s = 0.0
    for j in range(int(k), int(k) + 4000):
        s += exp(-mu + j * log(mu) - lgamma(j + 1))
    return s

# ---------------- DPFRAC
dp = {}
mu0 = B["Q"] / (1 << 114)
dp["expected_finished_trails_at_halt_d114"] = mu0
dp["table_full_prob_at_tmax18432"] = pois_sf(mu0, 18433)
dp["d_sweep(integer d: time,mem,score,delta)"] = {}
for d in range(110, 119):
    r = led(d=d)
    dp["d_sweep(integer d: time,mem,score,delta)"][d] = (r["time"], r["mem"], r["score"], r["score"] - B["score"], r["tmax"])
# memory headroom: largest tmax at 32 bytes per key with 374400 code + 2048
tmax_max = (2**20 - 374400 - 2048) // 32
dp["tmax_max_32B_entries"] = tmax_max
frac = {}
for target in (1e-6, 1e-9, 1e-12):
    # smallest d' such that Poisson tail beyond tmax_max is below target
    lo, hi = 112.0, 114.0
    for _ in range(40):
        mid = (lo + hi) / 2
        mu = mu0 * 2 ** (114 - mid)
        if pois_sf(mu, tmax_max + 1) > target: lo = mid
        else: hi = mid
    r = led(d=hi, tmax=tmax_max)
    frac[target] = dict(d=hi, mu=mu0 * 2 ** (114 - hi), delta_score=r["score"] - B["score"], mem=r["mem"])
dp["fractional_d_to_fill_2^20(32B entries)"] = frac
# 25-byte entries (8 key + 2 t + 15 length) : more keys
tmax25 = (2**20 - 374400 - 2048) // 25
frac25 = {}
for target in (1e-9,):
    lo, hi = 111.0, 114.0
    for _ in range(40):
        mid = (lo + hi) / 2
        mu = mu0 * 2 ** (114 - mid)
        if pois_sf(mu, tmax25 + 1) > target: lo = mid
        else: hi = mid
    r = led(d=hi, tmax=tmax25)
    frac25[target] = dict(d=hi, tmax=tmax25, delta_score=r["score"] - B["score"])
dp["fractional_d_25B_entries"] = frac25
# marginal values
dp["marginal_recovery_share"] = float(B["parts"]["recovery"] / B["total"])
dp["memory_term_slope_bits_per_bit_of_d"] = "table 589824 of 966272 bytes: lowering d by 1 doubles table"
# s1 sweep
dp["s1_prefilter_bits(delta)"] = {s: dt(s1=s) for s in (16, 20, 24, 28, 31, 32)}
res["dpfrac"] = dp

# Floyd / Brent versus DP at n = 2^22 (sampled)
import numpy as np
def rho_costs(n_bits, runs, seed):
    N = 1 << n_bits
    rng = np.random.default_rng(seed)
    out_f, out_b, out_rl = [], [], []
    for _ in range(runs):
        f = rng.integers(0, N, size=N, dtype=np.int64)
        x0 = int(rng.integers(0, N))
        fl = f.tolist()
        # trail until repeat to get mu, lam (exact rho length)
        seen = {}; x = x0; i = 0
        while x not in seen:
            seen[x] = i; x = fl[x]; i += 1
        mu = seen[x]; lam = i - mu
        rl = mu + lam
        # Floyd evaluations: tortoise+hare 3 evals per step until meet at index m=ceil(max(mu,1)/lam)*lam
        m = max(1, -(-mu // lam)) * lam
        floyd = 3 * m
        # Brent: power-of-two teleport, evals until detection = first time lam found
        power = 1; lam_b = 1; t = x0; h = fl[x0]; ev = 1
        while t != h:
            if power == lam_b:
                t = h; power *= 2; lam_b = 0
            h = fl[h]; ev += 1; lam_b += 1
        out_f.append(floyd); out_b.append(ev); out_rl.append(rl)
    return np.array(out_f), np.array(out_b), np.array(out_rl)
fa, ba, ra = rho_costs(18, 300, 7)
Nn = 1 << 18
res["alt_cycle_finding_n18_300runs"] = dict(
    q39_floyd_over_sqrt2N=float(np.quantile(fa, 0.39) / sqrt(2 * Nn)),
    q39_brent_detect_over_sqrt2N=float(np.quantile(ba, 0.39) / sqrt(2 * Nn)),
    q39_rho_length_over_sqrt2N=float(np.quantile(ra, 0.39) / sqrt(2 * Nn)),
    dp_filed_q_over_sqrt2N=sqrt(0.497), note="Brent detect count excludes the extra evals to locate mu and the colliding pair")

# ---------------- CHAINLEN
cl = {}
CL = {}
for kappa in (6, 8, 9, 10, 11, 12, 13, 14, 16, 20):
    cut = Fraction(15, 100000) * Fraction(kappa * exp(-kappa) / (12 * exp(-12)))
    cut = Fraction(float(cut)).limit_denominator(10**9)
    r = led(kappa=kappa, cutloss=cut)
    CL[kappa] = dict(cutloss=float(cut), delta=r["score"] - B["score"])
cl["kappa_sweep_cutloss_scaled_as_kappa*exp(-kappa)"] = CL
cl["mean_cut_loss_kappa12"] = 12 * exp(-12)
cl["cutloss_allowance/mean"] = 15e-5 / (12 * exp(-12))
# inflight: Gamma(7,1) tail in units of L
def gamma7_sf(x):
    return exp(-x) * sum(x ** k / exp(lgamma(k + 1)) for k in range(7))
cl["P(inflight_total>28L)_if_7_exponential_ages"] = gamma7_sf(28)
cl["P(inflight_total>20L)"] = gamma7_sf(20)
cl["P(inflight_total>15L)"] = gamma7_sf(15)
cl["inflight_sweep_delta(28,20,15,10,7)"] = {i: dt(inflight=i) for i in (28, 20, 15, 10, 7)}
cl["trail_start_pool"] = "tmax 18432 = 2^14 + 2^11 trail ids; t<2^16 key space"
res["chainlen"] = cl

# ---------------- SUCC
sc_ = {}
lam_min = -log(1 - 0.39)
sc_["lambda_for_P=0.39 exactly"] = lam_min
sc_["P at lambda 0.497"] = 1 - exp(-0.497)
sc_["margin_in_P"] = 1 - exp(-0.497) - 0.39
def lam_for(Pmin): return -log(1 - Pmin)
cands = {}
for name, P in (("P=0.39+1.2e-4 (spent loss only)", 0.39 + 1.2e-4), ("P=0.39+3e-4", 0.39 + 3e-4), ("P=0.39+1e-3", 0.39 + 1e-3), ("shipped 0.39165", 1 - exp(-0.497))):
    lam = Fraction(lam_for(P)).limit_denominator(10**7)
    cands[name] = dict(lam=float(lam), delta=dt(lam=lam))
sc_["lambda_options"] = cands
sc_["combined_lambda0.4944_inflight8_extra29"] = dt(lam=Fraction(4944, 10000), inflight=8, extra=29)
sc_["sensitivity_time_vs_P"] = {P: dt(lam=Fraction(lam_for(P)).limit_denominator(10**7)) for P in (0.30, 0.39, 0.45, 0.5, 0.63)}
res["succ"] = sc_

# ---------------- ATT
att = {}
for a in (1, 2, 3, 4, 8):
    lam_a = Fraction(497, 1000) / a
    r = led(lam=lam_a, inflight=28)
    p = r["parts"]
    per_attempt = p["main"] + p["slices"] + p["stage2"] + p["events"] + p["init"]
    tot = a * per_attempt + p["recovery"]
    att[a] = dict(time_log2=log2(tot / C), delta=log2(tot / C) - B["time"])
res["att"] = {"a_attempts_total_points_x_sqrt(a)": att,
              "ideal_birthday_penalty_bits_0.5*log2(a)": {a: 0.5 * log2(a) for a in (1, 2, 4, 8)}}

json.dump(res, open("b_generic.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
