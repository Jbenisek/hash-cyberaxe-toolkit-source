#!/usr/bin/env python3
"""Exact pricing: replace the batch row of pkgCA Section 11 with the cluster
schedule and recompute time_log2.  Integer arithmetic throughout."""
import json, math
from fractions import Fraction

# ---- pkgCA Section 11 constants (recovered from the ledger) ----
RUN_CONTEXTS = 1553906557396539
RUN_BATCHES  = 116386047242443374561
E_BUDGET     = 47103299361697989262
PASS_BUDGET  = 858218304486124637
CREDIT       = 3795525293015086772861
ONE_TIME     = (1 << 39) + (1 << 27) + (1 << 20) + 4 * (1 << 26) + (1 << 50) + 40 + 16
P            = 1 << 70            # preprocessing bound
FINAL        = 1 << 38            # final-step units (added after /430)
DIV          = 430

RUN_STEPS = (1 << 19) * RUN_CONTEXTS

context_row = 600 * (RUN_CONTEXTS + 1)
batch_row_old = 67 * RUN_BATCHES - 30 * RUN_CONTEXTS
q_row = 67 * (E_BUDGET + 1)
pass_row = 450 * (PASS_BUDGET + 1)
credit_row = CREDIT

S_old = context_row + batch_row_old + q_row + pass_row + credit_row + ONE_TIME
assert S_old == 15136396605699096622327, S_old
assert ONE_TIME == 1126450066358328, ONE_TIME
assert batch_row_old == 7797818548046984199417, batch_row_old


def tlog2(S):
    num = S + P
    T = Fraction(num, DIV) + FINAL          # exact rational
    return math.log2(float(T)), T


log_old, T_old = tlog2(S_old)
assert abs(log_old - 65.04060003903857) < 1e-9, log_old

# ---- cluster schedule (exact) ----
# representatives: 2^14 per context, 7 per batch -> ceil(2^14/7)=2341 batches
REP_BATCHES_PER_CTX = -(-(1 << 14) // 7)          # 2341
REP_BATCH_UNITS = 95                               # 67 omega-first + 7*4 alive-bit(AND,addr,load,branch)
# partners: 31 per cluster in 5 packed batches = 4*67 + 43 = 311 units per alive cluster
PARTNER_UNITS_PER_ALIVE = 4 * 67 + 43              # 311
ALIVE_SHARE = Fraction(13, 32)                     # PROVED (automaton (2), omega mod 2^9)
MARGIN = Fraction(17, 16)                          # H4' budget margin (as E_BUDGET, PASS_BUDGET)

# budget on alive clusters (H4' type): ceil( (17/16)*(13/32)*2^14 * RUN_CONTEXTS )
alive_per_ctx_mean = ALIVE_SHARE * (1 << 14)       # 6656
ALIVE_BUDGET = (MARGIN * ALIVE_SHARE * (1 << 14)) * RUN_CONTEXTS   # 7072*RUN_CONTEXTS
assert ALIVE_BUDGET.denominator == 1, ALIVE_BUDGET
ALIVE_BUDGET = int(ALIVE_BUDGET)
assert ALIVE_BUDGET == 7072 * RUN_CONTEXTS

rep_row = REP_BATCH_UNITS * REP_BATCHES_PER_CTX * RUN_CONTEXTS
partner_row = PARTNER_UNITS_PER_ALIVE * (ALIVE_BUDGET + 1)
batch_row_new = rep_row + partner_row

S_new = S_old - batch_row_old + batch_row_new
log_new, T_new = tlog2(S_new)

# expected (mean) units per member, part (2) -- no margin, alive share 13/32
mean_batch_per_ctx = (REP_BATCH_UNITS * REP_BATCHES_PER_CTX
                      + PARTNER_UNITS_PER_ALIVE * int(alive_per_ctx_mean))
mean_units_per_member = Fraction(mean_batch_per_ctx, 1 << 19)
old_units_per_member = Fraction(batch_row_old, RUN_STEPS)
budg_units_per_member = Fraction(batch_row_new - partner_row % 1, RUN_STEPS)  # ~
budg_units_per_member = Fraction(2421787, 1 << 19)

# sensitivity: LEVERS light alive-bit (+2/lane -> rep batch 81)
rep_row_L = 81 * REP_BATCHES_PER_CTX * RUN_CONTEXTS
S_new_L = S_old - batch_row_old + rep_row_L + partner_row
log_new_L, _ = tlog2(S_new_L)

out = {
  "constants_ok": True,
  "log2T_old": log_old,
  "batch_row_old": batch_row_old,
  "batch_row_new": batch_row_new,
  "rep_row": rep_row, "partner_row": partner_row,
  "REP_BATCHES_PER_CTX": REP_BATCHES_PER_CTX,
  "ALIVE_BUDGET": ALIVE_BUDGET, "ALIVE_BUDGET_per_ctx": 7072,
  "alive_mean_per_ctx": int(alive_per_ctx_mean),
  "S_old": S_old, "S_new": S_new,
  "T_old_float": float(T_old), "T_new_float": float(T_new),
  "log2T_new": log_new,
  "delta_log2T": log_new - log_old,
  "log2T_new_LEVERS_plus2": log_new_L,
  "delta_log2T_LEVERS_plus2": log_new_L - log_old,
  "old_units_per_member": [old_units_per_member.numerator, old_units_per_member.denominator, float(old_units_per_member)],
  "mean_units_per_member": [mean_units_per_member.numerator, mean_units_per_member.denominator, float(mean_units_per_member)],
  "budgeted_units_per_member": [budg_units_per_member.numerator, budg_units_per_member.denominator, float(budg_units_per_member)],
  "batch_row_fraction_of_S_old": float(Fraction(batch_row_old, S_old)),
}
print(json.dumps(out, indent=1))

# --- aggregate the two GPU measurement runs ---
import os
HERE = os.path.dirname(os.path.abspath(__file__))
agg = {"pairs": 0, "exceptions": 0, "dead_clusters": 0, "clusters": 0,
       "dead_partner_pass2": 0, "dead_partner_pass2_nonexc": 0}
for fn in ("big_seed7.json", "big_seed99.json"):
    p = os.path.join(HERE, fn)
    if os.path.exists(p):
        d = json.load(open(p))
        agg["pairs"] += d["partner_pairs"]; agg["exceptions"] += d["exceptions"]
        agg["dead_clusters"] += d["dead_clusters"]; agg["clusters"] += d["clusters"]
        agg["dead_partner_pass2"] += d["dead_partner_pass2"]
        agg["dead_partner_pass2_nonexc"] += d["dead_partner_pass2_nonexc"]
if agg["pairs"]:
    N = agg["pairs"]; k = agg["exceptions"]
    rate = k / N
    se = math.sqrt(rate * (1 - rate) / N)
    ub_binom = rate + 1.645 * se
    ub_clust = rate + 1.645 * se * math.sqrt(31)   # conservative within-cluster deff<=31
    dead_partner_pairs = 31 * agg["dead_clusters"]
    agg_out = {
      "pairs": N, "log2_pairs": math.log2(N),
      "exceptions": k, "rate": rate, "rate_log2": math.log2(rate),
      "ub95_binomial": ub_binom, "ub95_binomial_log2": math.log2(ub_binom),
      "ub95_cluster_conservative": ub_clust, "ub95_cluster_log2": math.log2(ub_clust),
      "dead_share_measured": agg["dead_clusters"] / agg["clusters"],
      "dead_share_proved": float(Fraction(19, 32)),
      "dead_partner_pass2": agg["dead_partner_pass2"],
      "dead_partner_pass2_nonexc": agg["dead_partner_pass2_nonexc"],
      "dead_partner_pairs": dead_partner_pairs,
      "dead_partner_pass2_rate": agg["dead_partner_pass2"] / dead_partner_pairs,
      "dead_partner_pass2_rate_log2": math.log2(agg["dead_partner_pass2"] / dead_partner_pairs),
    }
    print(json.dumps(agg_out, indent=1))
