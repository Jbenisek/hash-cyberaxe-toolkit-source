# kp_check.py - skeptic check of "kinetic proofreading -> projected exponent 90.8"
# Inputs: filed ledger of 64c075ac (research\pkg10\sec8_ledger.md, sec8_total_filled.md),
# END_OF_LINE 3.1 formula, RECOUNT.md split 81+12+57 and cheap-test lane rate 105/16384.
from math import log2

L430 = log2(430)
def formula(F, ops):            # board formula (END_OF_LINE section 2)
    return 123.339 - log2(F) + log2(ops / 34) + 0.012

F_kept = 185_351_809            # kept rate with cheap c1 test, units 2^-128 per trial
print("1. formula reproduction")
print("   discount 1, charge 1.00 :", round(formula(F_kept, 1.00), 3))
print("   discount 2, charge 1.00 :", round(formula(F_kept / 2, 1.00), 3))
print("   discount 1, charge 1.65 :", round(formula(F_kept, 1.65), 3))
print("   discount 2, charge 1.65 :", round(formula(F_kept / 2, 1.65), 3), "(filed 92.53)")
print("   log2(1.71) =", round(log2(1.71), 4), " log2(1.65) =", round(log2(1.65), 4))

# 2. filed ledger, per representative (units), 41.02 trial-equivalents per representative
rows = {
    "group": 0.076294 + 0.000001,          # middle steps etc + table build
    "rep_stageA": 6.858398,
    "rep_gate": 1.428833,
    "rep_stage2": 0.602789,
    "dispatch": 2.323623,
    "cluster_entry_exit": 2.473534,
    "nb_stageA": 31.724992,
    "nb_stage2": 22.096795,
}
TE = 41.02
tot = sum(rows.values())
print("\n2. ledger total per representative:", round(tot, 6), " per TE:", round(tot / TE, 6))
first = rows["group"] + rows["rep_stageA"] + rows["rep_gate"] + rows["nb_stageA"]
route = rows["dispatch"] + rows["cluster_entry_exit"]
st2 = rows["rep_stage2"] + rows["nb_stage2"]
print("   first stage (group+stageA+gate) per TE :", round(first / TE, 4))
print("   routing per TE                         :", round(route / TE, 4))
print("   stage 2 per TE                         :", round(st2 / TE, 4))

N2 = 759_300 * 2**81             # trials of the filed run (discount 2)
def total_log2(charge, N, pre_ops=2**94, prep_units=2**80):
    T = (charge * N + pre_ops + 2**28 + 2**11 + 1) / 430 + 2 + prep_units
    return log2(T)
print("   filed total check (charge 1.65, disc 2):", round(total_log2(1.65, N2), 4))

# 3. idealised staging: stage 2 free, first stage and routing unchanged
floor_staging = (first + route) / TE
print("\n3. staging floor (stage 2 -> 0):", round(floor_staging, 4), "per TE")
print("   exponent, discount 2:", round(total_log2(floor_staging, N2), 3))
print("   exponent, discount 1:", round(total_log2(floor_staging, N2 / 2), 3))
print("   charge 1.00 literal total, discount 1:", round(total_log2(1.00, N2 / 2), 3))
print("   charge 1.00 literal total, discount 2:", round(total_log2(1.00, N2), 3))

# 4. realistic staging: one more early-abort stage = split of stage 2 at the cheap c1 test
p_lane = 105 / 16384
p_word = 1 - (1 - p_lane) ** 7
for budget in (1.0, 1.2):
    per_word = 81 + 12 + 57 * p_word * budget
    words = st2 / 135
    new_tot = tot - words * (135 - per_word)
    ch = new_tot / TE
    ch_up = -(-ch * 100 // 1) / 100     # rounded up to 2 decimals, as filed
    print(f"\n4. c1 split, tail budget x{budget}: per stage-2 word {per_word:.3f}, charge {ch:.5f} -> {ch_up:.2f}")
    print("   gain vs 1.65:", round(log2(1.65 / ch_up), 4), "bit")
    print("   exponent, discount 2:", round(total_log2(ch_up, N2), 4), " discount 1:", round(total_log2(ch_up, N2 / 2), 4))
