"""ledger.py - pkgCM's charged time and the t_hi-walk rows that replace part of it (research only, nothing filed).

pkgCM's rows, budgets and N are taken from the shipped experiments/frontline.py (asserted equal to proof.md Section 11).
The walk rows are THIS scout's schedule (DERIVED from the blocks written below, not audited by anyone):

  walk context (one fresh draw = 7 outer words + member y; walks its 7 full X0 blocks, 7 * 2^16 outer steps):
      the front line's context allowance 547 (39 context lines, packing, saves, loop, W test) + the 10 C0/D1 member
      lines on scalar words (6 rotations at 5, 4 single, at most 60 with stores) + the walk constants (K1.d1 rotation,
      hi13/r19, Cc, x_top, j0, A = e1 - S0 - S5, S15', the folded Y9-path constants, at most 64) + broadcasting 12
      packed operands into seven lanes (8 each, 96) + C2.a1, C2.d1, X6 for the shortcut (24): 791, charged 1,024
  block (7 per context, every block charged as live): omega mod 2^16 of the block, the two byte-table loads of test
      (2)'s automaton up to bit 16, the live test and branch, the list base of the state, the carry constant of the
      block (32); plus, for a live block, at most 19 partial list words of 96 (one per (state, mask2) list,
      lane_check L3): 1,856, charged 2,048
  walk-lane word (7 listed steps of a live block that pass (2), every lane used except a list's last word):
      load 1; X0 lanes from the listed omega >> 16: add the block constant, AND 0xffff per lane, XOR S15'_hi, OR the
      block's X0 >> 16 (4); the Y9 path from X0 on packed words, D0.d1 D0.c1 D0.b1 X10 X5 C1.a1 (X0 + c4 + X5)
      C1.d1 C1.c1 C1.b1 Y1 Y13 Y9 (five PROR at 5 with their XOR, 30, and 9 single, 39); seven lane tests on T1 at
      2^34 + Y9 priced as pkgCM's E lane without its W add: shift, AND with 2^34 + M, load T1, AND with the list's
      mask2, compare, branch (6 each, 5 for lane 0: 41); pointer, end test, branch (3); W (1): 89, charged 96 =
      13.71 per (2)-passing step (an earlier draft of this file charged 84 with 5-unit lane tests; corrected)
  passing lane (filter pass): 53, as pkgCM (shortcut, pre-check, preflight); solver credit: pkgCM's formula
  final step: two complete evaluations of messages of up to 1024 (2^51 - 1) + 63 bytes: 2 (17 t + 1) compressions,
      t <= 2^51 - 1, plus writing 2^62 bytes as 2^57 stores; charged 2^56.1 units of time (conservative, as pkgCM
      charges its two evaluations), or the lean variant without the two evaluations (writing only)
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import math
import os
import sys
from fractions import Fraction
from math import isqrt

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCM/pkg/blake3-r2/experiments'))
import frontline as F  # noqa: E402


def lg(x):
    return math.log2(x)


def cdiv(a, b):
    return -(-a // b)


# ---------------- pkgCM as shipped ----------------
RC, RS = F.RUN_CONTEXTS, F.RUN_STEPS
rows_cm = {
    "context": F.U_CONTEXT * (RC + 1),
    "representative batch": (F.U_REP * (F.REP_BATCHES - 1) + F.U_REP_TAIL) * RC,
    "opened cluster": F.U_OPEN * (F.A_BUDGET + 16384),
    "E lane": F.U_E * (F.E_BUDGET + (1 << 19)),
    "fill": F.U_FILL * (F.G_BUDGET + 84261),
    "passing lane": F.U_PASS * (F.PASS_BUDGET + (1 << 19)),
    "solver credit": F.CREDIT,
    "once": F.ONCE,
}
SUM_CM = sum(rows_cm.values())
N_CM = SUM_CM + F.S_OLD + 430 * 2 ** 38
assert N_CM == F.N == 3436742575482187376270
assert SUM_CM == 3431255947038643164814


def show(rows, n_total, label, steps):
    print("%s: rows sum 2^%.4f machine units; per outer step %.5f" % (label, lg(sum(rows.values())), sum(rows.values()) / steps))
    for k, v in rows.items():
        print("   %-34s %28d  2^%7.3f  share %6.2f%%  per step %.5f" % (k, v, lg(v), 100 * v / sum(rows.values()), v / steps))
    print("   N = %d, time_log2 = log2(N / 430) = %.5f" % (math.ceil(n_total), lg(Fraction(n_total) / 430)))


show(rows_cm, N_CM, "pkgCM (shipped)", RS)

# ---------------- the walk ----------------
STEPS_PER_CTX = 7 * 65536
RCW = cdiv(RS, STEPS_PER_CTX)          # contexts so that the walk visits at least RUN_STEPS outer steps
RSW = RCW * STEPS_PER_CTX
SW = isqrt(10 * RCW - 1) + 1           # pkgCM's Hoeffding-reserve multiplier, on the walk's contexts
U_WCTX, U_BLOCK, U_WORD, U_PASS = 1024, 2048, 96, F.U_PASS


def walk_rows(e_factor_ppm, pass_factor_ppm, lean_final):
    # (2)-passing steps: mean share pi_E = E_COUNT / 2^32 times the premise factor, plus pkgCM's reserve form
    e_budget = cdiv(e_factor_ppm * RSW * F.E_COUNT, 10 ** 6 << 32) + SW * STEPS_PER_CTX
    words = cdiv(e_budget + STEPS_PER_CTX, 7)           # full words; partial words are in the block row
    pass_budget = cdiv(pass_factor_ppm * RSW * F.SHARE, 10 ** 6 << 64) + SW * STEPS_PER_CTX
    mc0 = cdiv(101 * RSW * F.U_M, 100 << 46)
    mc = cdiv(478 * mc0, 487)
    lc = 15296 << 19
    credit = mc + isqrt(40 * lc * mc - 1) + 1 + 14 * lc + 15296
    rows = {
        "walk context (1,024)": U_WCTX * (RCW + 1),
        "blocks (7 x 2,048)": 7 * U_BLOCK * RCW,
        "walk-lane words (96 per 7)": U_WORD * words,
        "passing lane (53)": U_PASS * (pass_budget + STEPS_PER_CTX),
        "solver credit": credit,
        "once (+2^26 walk lists)": F.ONCE + (1 << 26),
    }
    final_units = Fraction(2 ** 57, 430) if lean_final else None
    return rows, final_units


def final_step_units():
    t = 2 ** 51 - 1
    comps = 2 * (17 * t + 1)
    writes = Fraction(2 ** 57, 430)
    return comps, writes


comps, writes = final_step_units()
print("\nfinal step: messages of up to 1024*(2^51-1)+63 = %d bytes (< 2^61 = %d: %s); two complete evaluations"
      " = %d compressions = 2^%.4f; writing 2^62 bytes = 2^57 stores = 2^%.3f units; sum 2^%.4f units"
      % (1024 * (2 ** 51 - 1) + 63, 2 ** 61, 1024 * (2 ** 51 - 1) + 63 < 2 ** 61, comps, lg(comps), lg(writes),
         lg(comps + writes)))
FINAL_CONS = Fraction(math.ceil(2 ** 56.1))   # charged 2^56.1 units of time (an integer just above it)
assert comps + writes < FINAL_CONS

for label, eppm, pppm, lean in (("walk, premise factors as pkgCM (1.000026, 1.000176), conservative final step", 1000026, 1000176, False),
                                ("walk, E factor 1.03 (3 SE above this scout's 1.0047 +- 0.0102), conservative", 1030000, 1030000, False),
                                ("walk, premise factors as pkgCM, lean final step (writing only)", 1000026, 1000176, True)):
    rows, fin = walk_rows(eppm, pppm, lean)
    s = sum(rows.values())
    fin_mu = 430 * (fin if lean else FINAL_CONS)
    n_w = s + F.S_OLD + fin_mu
    print()
    show(rows, n_w, label, RSW)
    print("   SEL %d (unchanged); final step %.4g machine units (2^%.3f units of time)" % (F.S_OLD, float(fin_mu), lg(fin_mu / 430)))
    print("   time_log2 %.4f vs pkgCM %.4f: saving %.4f bit" % (lg(Fraction(n_w) / 430), lg(Fraction(N_CM, 430)),
                                                               lg(Fraction(N_CM, 430)) - lg(Fraction(n_w) / 430)))

print("\nwalk geometry: contexts %d = 2^%.4f (pkgCM %d = 2^%.4f), outer steps %d = 2^%.4f (pkgCM 2^%.4f, ratio %.9f)"
      % (RCW, lg(RCW), RC, lg(RC), RSW, lg(RSW), lg(RS), RSW / RS))
print("pkgCM rows removed by the walk: representative batch, opened cluster, E lane, fill (= %.2f%% of the rows); context replaced"
      % (100 * (rows_cm["representative batch"] + rows_cm["opened cluster"] + rows_cm["E lane"] + rows_cm["fill"]) / SUM_CM))
