"""S9: effect of a bitsliced representative path on the filed cost table (pkg10 proof.md section 8).
All rows per representative.  Filed rows copied from research/pkg10/sec8_ledger.md.  Bitsliced stage-A figures are
the COMPUTED counts of bs_stageA.py (R = 14, worst case over extreme constants); dispatch and stage-2 rows are
DERIVED hand counts stated below."""
from math import log2

F = 92_675_904
TE = 41.02
G_SHARE = 0.0749556            # GATE_BUDGET per representative (1.2 * 0.0624630)
PASS = 2 ** -8                 # rule A per lane


def time_log2(total, round_up=True):
    charge = total / TE
    if round_up:
        charge = -(-round(charge * 1e6) // 10000) / 100      # round up to 2 decimals as the filed text does
    return 123.339 - log2(F) + log2(charge / 34) + 0.012, charge


filed = {
    "group": 0.076294 + 0.000001,
    "rep stage A + store z": 6.858398,
    "rep gate test + load z": 1.428833,
    "rep stage 2": 0.602789,
    "dispatch": 2.323623,
    "cluster entry/exit": 2.473534,
    "neighbour stage A": 31.724992,
    "neighbour stage 2": 22.096795,
}
base = sum(filed.values())

# bitsliced stage A per trial (bs_stageA.py, R = 14): J mean 3.242 worst 3.324 (+ JIT, not counted);
# D mean 3.700 worst 3.969; G 5.574.  Route the gate mask: 1 store + 1 load per 256 lanes.
route = 2 / 256
# dispatch per word: 8 chunks x (shift, AND, compare, branch) + 1 load = 33; per open gate: negate (2), AND, clear,
# lookup of the lane in a 2^32-entry one-hot table (1 load), add chunk base, loop test (2) = 8; or 27 with a
# 5-step binary search instead of the table.
disp_table = 33 / 256 + G_SHARE * 8
disp_bsearch = 33 / 256 + G_SHARE * 27
# stage 2 of passing representative lanes: scan of the pass mask 33 per word + 8 per pass; then either
#  (1) one lane per filed packed word: filed stage A + stage 2 again (47 + 135) + 5, or
#  (2) seven passing lanes gathered into one packed word: 6 table words x (load + OR) + 5 = 17 per lane,
#      then (47 + 135) / 7 per lane.  Budget 1.2 x the expected passes.
s2_one = 33 / 256 + 1.2 * PASS * (8 + 47 + 135 + 5)
s2_gath = 33 / 256 + 1.2 * PASS * (8 + 17 + (47 + 135) / 7)

scen = {
    "filed (pkg10)": {},
    "claim: stage A row -> 3.5": {"rep stage A + store z": 3.5},
    "measured D worst, stage A row only": {"rep stage A + store z": 3.969},
    "measured G (no specialisation), stage A row only": {"rep stage A + store z": 5.574},
    "D worst + gate test folded": {"rep stage A + store z": 3.969, "rep gate test + load z": route},
    "D worst + gate folded + table dispatch + gathered stage 2": {
        "rep stage A + store z": 3.969, "rep gate test + load z": route, "dispatch": disp_table,
        "rep stage 2": s2_gath},
    "D worst + gate folded + binary-search dispatch + one-lane stage 2": {
        "rep stage A + store z": 3.969, "rep gate test + load z": route, "dispatch": disp_bsearch,
        "rep stage 2": s2_one},
    "J worst (+0.11 JIT) + gate folded + table dispatch + gathered stage 2": {
        "rep stage A + store z": 3.324 + 0.11, "rep gate test + load z": route, "dispatch": disp_table,
        "rep stage 2": s2_gath},
    "G + gate folded + table dispatch + gathered stage 2": {
        "rep stage A + store z": 5.574, "rep gate test + load z": route, "dispatch": disp_table,
        "rep stage 2": s2_gath},
    "G + gate folded + binary-search dispatch + one-lane stage 2": {
        "rep stage A + store z": 5.574, "rep gate test + load z": route, "dispatch": disp_bsearch,
        "rep stage 2": s2_one},
    "ceiling: whole representative side free (rows 2-5 = 0)": {
        "rep stage A + store z": 0, "rep gate test + load z": 0, "dispatch": 0, "rep stage 2": 0},
    "claim's redesign GUESS: all stage A x1.9": {"rep stage A + store z": 6.858398 / 1.9,
                                                 "neighbour stage A": 31.724992 / 1.9},
}
print("dispatch rows: table %.4f, binary search %.4f; rep stage-2 rows: one lane %.4f, gathered %.4f"
      % (disp_table, disp_bsearch, s2_one, s2_gath))
print("%-72s %9s %8s %8s %9s %9s" % ("scenario", "total", "gain", "charge", "time", "exact"))
for name, ch in scen.items():
    rows = dict(filed)
    rows.update(ch)
    tot = sum(rows.values())
    t, c = time_log2(tot)
    te, ce = time_log2(tot, round_up=False)
    print("%-72s %9.4f %8.4f %8.2f %9.4f %9.4f" % (name, tot, log2(base / tot), c, t, te))
