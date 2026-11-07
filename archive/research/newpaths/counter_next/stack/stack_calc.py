#!/usr/bin/env python3
"""stack_calc.py   (counter_next/stack; research only) - own gain of each lever on the counter arrangement, and
candidate variants.  One formula for everything, per WALKED OUTER STEP (2^21 cube trials in VALUE.md's design):
    T = log2( S * c_step / 430 ) + 0.02,   S = lambda / (m_step / margin),  lambda = 0.5, margin = 2.0
    m_step = 2^32 * r * 2^-128  (r = the beta*-part count of the Y4 cube; 2^21 trials x 2^11 x r x 2^-128)
c_step = word operations per walked outer step on the filed counting machine (VALUE.md: 6.5 charged per trial).
Reproduces VALUE.md's 84.96 for V0.  Every input is named with its source and tag in the comments.
"""
from math import log2

LAM, MARGIN, UNIT, ONE = 0.5, 2.0, 430, 0.02

def T(r, c_step, margin=MARGIN):
    m = 2 ** 32 * r * 2 ** -128
    return log2(LAM / (m / margin) * c_step / UNIT) + ONE

# ---- inputs -------------------------------------------------------------------------------------------------------
R_SUB = 67_698_688            # beta* part, sub-class 07ef8303/030c0303 (pkg10 count; Sol Y 2.1)            COMPUTED (team)
R_Q01B2 = 76_161_024          # beta* part, cube 07ef8307/070c0307, 14 rows (run_cube.sh, this folder)        COMPUTED
R_Q01 = 75_698_176            # cube 07ef8303/070c0303 (bit 21 = 0, bit 26 = 1)                              COMPUTED
R_Q01_RULEA = 67_698_688      # rule A (S8) pass in that cube                                                COMPUTED
R_CLASS = 71_698_432          # whole class (VALUE.md +0.083)                                                COMPUTED (team)
R_CLASS_RULEA = 33_849_344    # rule A (S8) pass over the whole class (scan_y4.txt, first line)              COMPUTED
R_S9 = R_SUB - (6_291_456 + 1_048_576 + 65_536) // 2   # rule S9 (9th condition) on beta*: a15 N3_S9 column   DERIVED
R_TOP4 = 183_119_872          # four heaviest betas, sub-class (outer_filter_top4.txt)                       COMPUTED (team rows)
CH = 6.5                      # VALUE.md charge per trial (stage A 41/7, stage 2 72 at 1/32 per word, x1.04)  COMPUTED (team)
BUD = (41 + 72 / 32) / 7      # 6.1786 budgeted
TRIALS = 2 ** 21
OUTER = 400                   # outer step, 81 lines (VALUE.md "under 400 units"; ctr_gen.inc read here)     DERIVED
CHECK = 35                    # byte-table DFAs for (1) on Y9 and (2) on E, 4 lookups each, + E, + test      DERIVED
P_SUB = 2 ** -9.8132          # outer_filter_bstar.txt, exact over 2^64 (Y9, E)                             COMPUTED
P_Q01B2 = 2 ** -7.5320        # outer_filter_q01b2.txt (14 targets)                                          COMPUTED
P_TOP4 = 2 ** -5.6892         # outer_filter_top4.txt (47 targets)                                           COMPUTED
SOLVE = 2 ** 18.51            # simple E3 solve per passing step (e3solve_out.txt: counts measured, op weights DERIVED)
BITS_GEN, BITS_SPEC = 2.5, 1.6   # bitsliced stage A per trial, generic / constant-specialised (STACK.md 2.4) DERIVED
RULEG = (36 + 0.2) / 7 * (CH / BUD)                     # rule-G stage A ~36 units/word (STACK.md 2.1)        GUESS on ops
TAU_SPLIT = (41 + 22 / 32) / 7 / BUD                    # stage 2 split at listed tau (22 units first)        DERIVED
S9_COST = (41 + 72 / 64) / 7 / BUD

V0_c = TRIALS * CH
base = T(R_SUB, V0_c)
rows = []
def add(name, t, status, needs):
    rows.append((name, t, status, needs))

add('V0  as valued (VALUE.md): enumeration of the beta* cube, rule A, no clusters', base, 'COMPUTED (team)', 'H1\'-H3\'')
print('LEVERS, each alone on V0 (gain = 84.96 - T; positive = better)')
levers = [
    ('L1a rule A built for beta* from h1 bits only: add the 9th condition (S9)', T(R_S9, TRIALS * CH * S9_COST), 'DERIVED', 'none new'),
    ('L1b rule G (condition (1), Y9 known) as the stage-A test, replaces rule A', T(R_SUB, TRIALS * RULEG), 'DERIVED (ops GUESS)', 'machine count'),
    ('L2a Y4 = whole class, filed rule A kept (VALUE.md +0.083 corrected)', T(R_CLASS_RULEA, V0_c), 'COMPUTED', 'none'),
    ('L2b Y4 cube 07ef8307/070c0307 with filed rule A (rule keeps 67.7M only)', T(R_Q01_RULEA, V0_c), 'COMPUTED', 'none'),
    ('L2c Y4 cube 07ef8307/070c0307 with a rule that keeps all rows (rule G)', T(R_Q01B2, V0_c), 'COMPUTED (rate)', 'rule G or E3 solve'),
    ('L3a c1-split proofreading stage (filed design)', base, 'DERIVED', 'n/a: c1 is forced into the cube'),
    ('L3b split of stage 2 at the listed-tau test', T(R_SUB, TRIALS * CH * TAU_SPLIT), 'DERIVED', 'machine count'),
    ('L4a bitsliced stage A, generic constants (256 trials/word)', T(R_SUB, TRIALS * BITS_GEN), 'DERIVED', 'machine count; judge accepts 256-lane bitslicing'),
    ('L4b bitsliced stage A, code specialised per outer step', T(R_SUB, TRIALS * BITS_SPEC), 'DERIVED', 'as L4a + computed jumps'),
    ('L5  exact outer-step filter on (Y9, E), enumeration kept', T(R_SUB, OUTER + CHECK + P_SUB * V0_c), 'COMPUTED (P) + DERIVED (cost)', 'lemma (1)-(2); H3-kind pass budget'),
    ('L6  E3-first solve per passing step (replaces the 2^21 enumeration)', T(R_SUB, OUTER + CHECK + P_SUB * SOLVE), 'DERIVED (measured counts)', 'L5 + solve-work budget (H2-kind)'),
    ('L7  clusters rebuilt on the inner loop (variant D)', base - 2.5, 'GUESS (VALUE 7: 2-3)', 'H4 yield, H5 mass/no clumping, H6 budgets'),
    ('L8  discount 1.4 instead of 2.0 (convention, not a gain)', T(R_SUB, V0_c, 1.4), 'DERIVED', 'owner decision; disclose'),
]
for n, t, s, needs in levers:
    print(f'  {base - t:+7.3f}  T {t:7.3f}  {n}   [{s}; needs: {needs}]')

print('\nVARIANTS (margin 2.0; subtract 0.515 for the field\'s 1.4)')
V = []
V.append(('V0  as valued', base, 'H1\'-H3\''))
V.append(('V0+ rule G + cube 07ef8307 (enumeration, all 14 rows kept)', T(R_Q01B2, TRIALS * RULEG), 'H1\'-H3\'; ops GUESS'))
V.append(('V0+ bitsliced (generic) + tau split', T(R_SUB, TRIALS * BITS_GEN * TAU_SPLIT), 'H1\'-H3\'; machine model'))
V.append(('V0+ clusters (variant D)', base - 2.5, 'H1\'-H3\' + H4-H6 kinds; GUESS'))
V.append(('V3  outer filter + enumeration (rule A, sub-class)', T(R_SUB, OUTER + CHECK + P_SUB * V0_c), 'H1\'-H3\' + filter lemma + pass budget'))
V.append(('V3b V3 + bitsliced inner loop (generic)', T(R_SUB, OUTER + CHECK + P_SUB * TRIALS * BITS_GEN), 'as V3; machine model'))
V.append(('V3c V3 + bitsliced inner loop (specialised)', T(R_SUB, OUTER + CHECK + P_SUB * TRIALS * BITS_SPEC), 'as V3b'))
V.append(('V4  outer filter + E3-first solve (beta*, sub-class Y4)', T(R_SUB, OUTER + CHECK + P_SUB * SOLVE), 'H1\'\' + filter lemma + pass and solve budgets'))
V.append(('V4q V4 on cube 07ef8307 (14 targets, solve x1.22)', T(R_Q01B2, OUTER + CHECK + P_Q01B2 * SOLVE * 1.22), 'as V4'))
V.append(('V4p V4 + 7 outer steps per packed word (outer 65, check 16)', T(R_SUB, 65 + 16 + P_SUB * SOLVE), 'as V4; GUESS on packing'))
V.append(('V4s V4p + a solver at 2^15 per passing step', T(R_SUB, 65 + 16 + P_SUB * 2 ** 15), 'as V4; GUESS on solver'))
V.append(('V4t top-4 betas, simple solve (viable 2 per pass)', T(R_TOP4, OUTER + CHECK + P_TOP4 * 2 * SOLVE / 1.23), 'as V4; GUESS on viable'))
V.append(('V4u top-4 betas, packed outer, solver 2^15 per viable', T(R_TOP4, 65 + 16 + P_TOP4 * 2 * 2 ** 15), 'as V4; GUESS'))
for n, t, needs in V:
    print(f'  T {t:7.3f}  (at 1.4: {t - log2(2 / 1.4):7.3f})  {n}   [{needs}]')


if __name__ == '__main__':
    pass
