
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

import json, math, os, re
from math import log2, comb, exp, sqrt

WS = _hca_public_path_text('__HCA_WORKSPACE__/')
OUT = WS + '/research/dig/incoming4'
WORK = 'research/dig/incoming4/work'
SRC = 'our workflow: dig-scan-poseidon'
DATE = '2026-10-12'
LO = 'research/poseidon/orchard/lean_r2/'
H = 'poseidon-r2'

# ------------------------------------------------------------------ numbers
N = json.load(open(OUT + '/work/nums.json'))
A = json.load(open(OUT + '/work/testA.json'))
B = json.load(open(OUT + '/work/testB.json'))
C = json.load(open(OUT + '/work/testC.json'))
D = [json.loads(l) for l in open(OUT + '/work/testD_real_j0.txt') if l.startswith('{')]

T4 = 303746130782
UNITS = T4 / 258
TL2 = log2(UNITS)
P = 75889107582                 # worst-case charge of one centre
MEM = 40934171
MEML = log2(MEM)
SCORE = TL2 + MEML - 20
ST = {'line': 3999, 'rand': 3, 'build': 121473076, 'power': 54638630504, 'gcdobs': 19035935044,
      'gcdbud': 21108000000, 'gap': 21000000, 'init': 662427, 'rootbud': 187665120, 'rootgap': 1172907, 'fg': 200000}
assert 4 * P + ST['init'] + ST['rootbud'] + ST['rootgap'] + ST['fg'] == T4


def sv(x):  # bits of time_log2 saved if x ops are removed from the worst-case total
    return log2(T4 / (T4 - x))


def f(x, d=4):
    return f'{x:.{d}f}'


def wilson(k, n, z=1.96):
    ph = k / n
    den = 1 + z * z / n
    c = ph + z * z / (2 * n)
    r = z * sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))
    return (c - r) / den, (c + r) / den


def binom_cdf(k, n, p):
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


# samples: GPU d192 (12 centres, r=2), CPU r2 first centres (11 complete runs), r1 d189 (20), r1 per-line (180)
G_good, G_n = 4, 12
C_good, C_n = 4, 11
PP = 1 - exp(-0.5)
pool_k, pool_n = G_good + C_good, G_n + C_n
wl = wilson(pool_k, pool_n)
wl99 = wilson(pool_k, pool_n, 2.576)
r1_k, r1_n = 57, 180
r1z = (r1_k - r1_n * PP) / sqrt(r1_n * PP * (1 - PP))
r1p = binom_cdf(r1_k, r1_n, PP)
pool_p = binom_cdf(pool_k, pool_n, PP)

# memory items
items = {'twiddle': 2097152, 'Y': 12582912, 'tmp': 4194304, 'MU': 6249952, 'g': 6250016, 'F': 6249984}
pow_peak = sum(items.values())
assert pow_peak == 37624320
gcd_peak = 40741792
fixed_mem = 122747 + 65536 + 4096
assert MEM == gcd_peak + fixed_mem

# types (2-centre observed run, evaluations charged as units excluded)
TY = dict(add=13435325042, sub=12622540897, mul=12274801600, sqr=284827007, ld=15396537559, st=8656647975, ctl=84719163718)
TY_ALL = 147592743256
TY_SUM = sum(TY.values())
UNIT_OPS = TY_ALL - TY_SUM       # = 202,899,458 (evaluations x 258 + 2 reference hashes' units)
assert UNIT_OPS == 2 * 393216 * 258 + 2


def tsav(x):  # bits saved on the observed run if x ops removed
    return log2(TY_ALL / (TY_ALL - x))


records = []


def rec(unit, loc, obj, q, question, status, number, own, notes, held, reopen, labels=('N',), ev=None, lever=False,
        gain=None, gain_basis=None, topic=None, prior=None, pot=None, label=None, confirmed=None):
    cell = f'{H}|{loc}|{obj}|{q}'
    if status in ('CLAIMED-UNTESTED', 'OPEN'):
        own = False
    r = {
        'hash': H, 'row_i': None, 'row_j': None,
        'object': label or f'{loc} ({obj})', 'question': f'{q}: {question}',
        'labels': list(labels), 'status': status, 'number': number, 'source': SRC, 'own_test': own,
        'evidence': ev or (WORK + '/ledger_numbers.json; ' + LO + 'logs/ledger_r2.txt'),
        'date': DATE, 'lever': lever, 'gain_bits': gain,
        'notes': f'Universe cell {cell}. ' + notes,
        'held_fixed': held, 'reopen_if': reopen,
    }
    if gain_basis:
        r['gain_basis'] = gain_basis
    if topic:
        r['topic'] = topic
    if prior is not None:
        r['prior'] = prior
    if pot is not None:
        r['potential_bits'] = pot
    records.append((unit, cell, r))


HF_L = ('r2 sampled-probability package pkg_stage_r2 as built 10-12 19:42 (C(2)=258 ops/unit, up to 4 centres, halt budgets D 21,108,000,000 and E 187,665,120, '
        'line j=0, ledger run seed 7 with 2 centres); not the two-family template that r2 will use')
RO_L = 'the r2 entry is rebuilt (two-family template), the charging rules change (control ops, dispatch, address ops), or an r2 run disagrees with these numbers'

# ================================================================== U35 ROOT.SPLIT
U = 'poseidon-r2-U35'
hist_cpu = {0: 7, 1: 3, 2: 1}
rec(U, 'ROOT.SPLIT', 'ROOT', 'Q1', 'exact gcd degree seen and the splitting cost charged', 'COMPUTED',
    'gcd(g, S^h-1) degree over 11 complete first-centre CPU runs at r=2 (line 0): deg 0 x7, deg 1 x3, deg 2 x1; GPU d192 (12 centres): F_p-roots of g 0 x6, 1 x4, 2 x1, 4 x1 and nonzero square roots 0 x8, 1 x4. '
    'Root finder charged at most 1,172,907 ops per random shift at deg 16 (bound_root.c), observed 7 ops at deg 1.', True,
    'Tabulated from lean_r2/logs/r2_s20*.txt and poseidon/d192_r2_results.jsonl; the deg-2 case is seed 201003 (verified collision). The halt allows deg G <= 16 (otherwise the centre is abandoned).',
    HF_L + '; first centre of each execution only', 'a run with gcd degree above 4 appears or the sampled mix of degrees changes (more samples)',
    ev=WORK + '/ledger_numbers.json; ' + LO + 'logs/bound_root.txt; research/poseidon/d192_r2_results.jsonl; ' + LO + 'logs/r2_s201000.txt..r2_s202005.txt', topic='poseidon-r2 root split degrees')
rec(U, 'ROOT.SPLIT', 'ROOT', 'Q2', 'is the splitter necessary: drop it (abandon the centre when deg G != 1) and recount', 'COMPUTED',
    f'Splitting is used in 1 of the 8 observed successes (CPU seed 201003, deg 2). Dropping it loses 1/8 of successes = {f(log2(8/7))} bit of expected time; '
    f'its whole charged budget is 187,665,120 + 1,172,907 ops = {f(sv(ST["rootbud"]+ST["rootgap"]),5)} bit. Keep it.', True,
    'Success set pooled over CPU r2 first centres (4) and GPU d192 centres with a nonzero square root (4); only the CPU deg-2 case needs a split. Bound is a ratio of two counts, small sample.',
    HF_L, 'a larger sample shows deg G >= 2 in under 1 percent of successes', ev=WORK + '/ledger_numbers.json; research/poseidon/d192_r2_results.jsonl; ' + LO + 'logs/')
rec(U, 'ROOT.SPLIT', 'ROOT', 'Q3', 'degrees of freedom: probability one random shift splits a degree-d product of distinct roots', 'COMPUTED',
    'model 1 - 2^(1-d): d=2 0.5, d=3 0.75, d=4 0.875, d=8 0.9922, d=16 0.99997; 40 shifts per centre fail with probability 2^-39 at d=2.', False,
    'Cantor-Zassenhaus character model for a uniform shift (Weil-bounded); not measured at r=2. 40 shifts per centre is the implemented cap.',
    HF_L + '; roots modelled as independent quadratic characters', 'a measured shift-failure rate above the model at d=2 on the real g', labels=('B',),
    ev=LO + 'logs/bound_root.txt')
rec(U, 'ROOT.SPLIT', 'ROOT', 'Q4', 'alternatives to splitting (new centre instead, other splitter)', 'COMPUTED',
    f'A new centre costs {P:,} ops charged ({f(P/ST["rootgap"],0)} times one deg-16 shift). Splitting always wins when deg G >= 2; no alternative splitter could save more than {f(sv(ST["rootbud"]+ST["rootgap"]),5)} bit (total root budget).', True,
    'Upper bound: assumes the splitter were free. Trace/Berlekamp splitters not built.', HF_L, 'splitter cost grows above 1 percent of a centre (it does not at deg <= 16)', labels=('Z',))

# ================================================================== U36 ROOT.NEWTON
U = 'poseidon-r2-U36'
NEWT = 377843160
nsh = NEWT / ST['power']
rec(U, 'ROOT.NEWTON', 'ROOT', 'Q1', 'exact cost of the Newton reciprocal of the modulus', 'COMPUTED',
    f'377,843,160 ops per centre at r=2 (99,688,065 arith) = {f(100*NEWT/ST["power"],3)} percent of the S^((p-1)/2) stage (54,638,630,504) and {f(100*NEWT/73796042626,3)} percent of an observed centre; '
    'r=1 strict recount: 86,672,156 (ratio 4.36 for a 5x modulus). Stage sum check: 377,843,160 + 3,906,435 (prefix, scale) + 54,256,880,909 (236 loop steps) = 54,638,630,504.', True,
    'Read from the lean-pow breakdown line of logs/ledger_r2.txt; identity verified by my arithmetic.', HF_L, 'a different reduction scheme is used for the power stage', ev=WORK + '/ledger_numbers.json; ' + LO + 'logs/ledger_r2.txt')
rec(U, 'ROOT.NEWTON', 'ROOT', 'Q2', 'necessity: drop the reciprocal (schoolbook division per step) and recount', 'COMPUTED',
    f'Schoolbook division of degree 2m by m costs about m^2 = {195312**2:,} multiplies, {f(195312**2/NEWT,1)} times the whole Newton cost, and would be needed at each of 236 steps unless a reciprocal exists. Newton is necessary.', True,
    'Order-of-magnitude comparison with m = 195,312 only; not a full ledger of the schoolbook alternative.', HF_L, 'a division-free power schedule is found', labels=('Z',))
rec(U, 'ROOT.NEWTON', 'ROOT', 'Q3', 'degrees of freedom: how much score can this stage ever move', 'COMPUTED',
    f'If the reciprocal were free: {f(sv(4*NEWT),4)} bit of time_log2 (4 centres charged). Precision doubles 1 -> 195,312 in 18 steps; the modulus changes with the centre, so no amortisation across centres.', True,
    'Upper bound on any improvement of this stage.', HF_L, 'never for this stage alone (bound 0.0072 bit)', labels=('Z',))
rec(U, 'ROOT.NEWTON', 'ROOT', 'Q4', 'alternatives (reuse across the 236 steps, Montgomery/Shoup form)', 'COMPUTED',
    'The reciprocal is already computed once per modulus and reused in all 236 steps (that is why it is 0.69 percent of the stage). Any other form is bounded by the same 0.0072 bit.', True,
    'Reading of the ledger structure plus the bound from Q3.', HF_L, 'never for this stage alone', labels=('Z',))

# ================================================================== U37 INIT / SETUP
U = 'poseidon-r2-U37'
init_t = 662427
for q, ques, st_, num, nt in [
    ('R1', 'value charged', 'COMPUTED', f'init: 66,509 arith + 595,918 other = 662,427 ops once per run (table of 65,536 twiddles rho^j, roots of unity); r=1 filed 17,359 + 20,480 = 37,839 under the old loose control charge.', 'Charged once, not per centre.'),
    ('R2', 'own recount', 'COMPUTED', f'arith + other = 662,427 reproduced from the INIT line; share of the worst-case total {init_t/T4:.3e} = {sv(init_t):.2e} bit.', 'Sum identity and share recomputed by me from logs/ledger_r2.txt; the C source of the stage was not re-instrumented here.'),
    ('R3', 'control (scaling check)', 'COMPUTED', f'r1 recount in logs/ledger_r1.txt: 17,359 arith + 153,554 other = 170,913; r2/r1 ratios arith {66509/17359:.2f}, other {595918/153554:.2f} for a 4x larger table (65,536 vs 16,384) - consistent with linear growth.', 'Control is the same code at r=1 under the same (strict) control charge.'),
    ('R4', 'score sensitivity', 'COMPUTED', f'dropping init entirely: {sv(init_t):.2e} bit of time_log2, 0 bits of memory (table counted in MEM.TWID). No lever.', 'Bound by removal.')]:
    rec(U, 'LEDGER.INIT', 'LEDGER', q, ques, st_, num, True, nt, HF_L, RO_L, labels=('Z',) if q == 'R4' else ('N',))
setup_t = 4 * 3999 + 4 * 3
for q, ques, st_, num, nt in [
    ('R1', 'value charged', 'COMPUTED', 'line setup (constants of the line, 1 inversion): 391 arith + 3,608 other = 3,999 ops per centre; random centre 3 ops.', 'r=1 old charge 391 + 1,564 = 1,955.'),
    ('R2', 'own recount', 'COMPUTED', f'arith + other = 3,999 reproduced; four centres charge 15,996 + 12 = 16,008 ops = {16008/T4:.2e} of the total ({sv(16008):.2e} bit).', 'Arithmetic on the ledger line.'),
    ('R3', 'control', 'COMPUTED', 'under the same strict charge the r1 recount (logs/ledger_r1.txt) gives 391 arith + 3,608 other = 3,999, identical to r2: the stage is size independent (one inversion, line constants). The old r1 filing charged 391 + 1,564 = 1,955 (loose control charge).', 'Size-independence is the control.'),
    ('R4', 'score sensitivity', 'COMPUTED', f'free setup saves {sv(16008):.2e} bit. No lever.', 'Bound by removal.')]:
    rec(U, 'LEDGER.SETUP', 'LEDGER', q, ques, st_, num, True, nt, HF_L, RO_L, labels=('Z',) if q == 'R4' else ('N',))

# ================================================================== U38 BUILDG / POWER
U = 'poseidon-r2-U38'
evals = 393216 * 258
ntt_part = ST['build'] - evals
for q, ques, st_, num, nt in [
    ('R1', 'value charged', 'COMPUTED', 'build g: 6,421,153 arith + 115,051,923 other = 121,473,076 ops per centre; of this 393,216 line evaluations x 258 = 101,449,728 are charged as target-compression units and 20,023,348 are the inverse NTT (size 196,608) and normalisation.', 'Split derived by me: 121,473,076 - 101,449,728.'),
    ('R2', 'own recount', 'COMPUTED', f'393,216 x 258 = {evals:,}; TYPES perm counter 202,899,456 over two centres = 2 x 101,449,728 (exact match). Share of worst-case total {4*ST["build"]/T4*100:.3f} percent.', 'The perm counter of the run confirms the evaluation count and unit charge independently of the stage line.'),
    ('R3', 'control', 'COMPUTED', 'r1 strict recount (logs/ledger_r1.txt): build g 28,998,130 = 98,304 x 237 = 23,298,048 evaluations + 5,700,082 NTT/normalisation. r2: 101,449,728 + 20,023,348. Evaluation ratio 4.354 = 258/237 x 4 exactly; NTT part ratio 3.51 for a 4x longer transform.', 'Same builder family, same strict control charge.'),
    ('R4', 'score sensitivity', 'COMPUTED', f'free build: {sv(4*ST["build"]):.4f} bit; evaluations alone ({sv(4*evals):.4f} bit). The evaluation unit cannot go below the cost of the 8 non-skipped rounds out of 10 (a cheaper direct evaluation of F from the affine state would charge fewer than 258, not tested).', 'Upper bound by removal; direct-evaluation variant OPEN.')]:
    rec(U, 'LEDGER.BUILDG', 'LEDGER', q, ques, st_, num, True, nt, HF_L, RO_L, labels=('Z',) if q == 'R4' else ('N',))
pw = ST['power']
rec(U, 'LEDGER.POWER', 'LEDGER', 'R1', 'value charged', 'COMPUTED',
    f'S^((p-1)/2) mod g: 16,131,772,597 arith + 38,506,857,907 other = {pw:,} ops per centre = {100*pw/P:.2f} percent of a centre\'s worst-case charge and {100*4*pw/T4:.2f} percent of the 4-centre total; 236 loop steps at 229,902,037 each; run took 531-586 s.', True,
    'Dominant stage; r=1 filed number was 6,241,583,567 under the loose charge.', HF_L, RO_L)
rec(U, 'LEDGER.POWER', 'LEDGER', 'R2', 'own recount', 'COMPUTED',
    f'Sum identity 377,843,160 + 3,906,435 + 54,256,880,909 = {377843160+3906435+54256880909:,} = stage total. 236 x 229,902,037 = {236*229902037:,} (differs from the loop line by {54256880909-236*229902037} ops, data-dependent steps).', True,
    'Arithmetic on the lean-pow breakdown; stage not re-instrumented.', HF_L, RO_L)
rec(U, 'LEDGER.POWER', 'LEDGER', 'R3', 'control (same stage under the r1 recount)', 'COMPUTED',
    'Strict r1 recount (logs/ledger_r1.txt): power stage 12,639,379,434 (arith 3,536,772,927), 238 steps at 52,739,184 each. r2: 54,638,630,504, per step 229,902,037. Stage ratio 4.32, per-step ratio 4.36 for a 5x longer modulus; arith ratio 4.56. (The filed r1 number 6,241,583,567 used the loose control charge and is not comparable.)', True,
    'Clean control: same code family and charge; ratios sit just under the degree ratio 5, as expected when the 236/238 step count is nearly fixed.', HF_L, RO_L)
rec(U, 'LEDGER.POWER', 'LEDGER', 'R4', 'score sensitivity', 'COMPUTED',
    f'free stage: {sv(4*pw):.3f} bit; a 10 percent cut of the stage: {sv(0.4*pw):.3f} bit; control ops are {100*TY["ctl"]/TY_ALL:.1f} percent of all observed ops (see MACHINE.CTL), so a straight-line kernel acts mainly here.', True,
    'This is the stage where any ledger lever must live.', HF_L, RO_L, labels=('N',), ev=WORK + '/ledger_numbers.json; ' + LO + 'logs/ledger_r2.txt')

# ================================================================== U39 GCD / ROOTS
U = 'poseidon-r2-U39'
gslack = 4 * (ST['gcdbud'] - ST['gcdobs'])
rec(U, 'LEDGER.GCD', 'LEDGER', 'R1', 'value charged', 'COMPUTED',
    'half-gcd: observed 3,170,520,858 arith + 15,865,414,186 other = 19,035,935,044 per centre; charged as a halt budget 21,108,000,000 (derived normal-case tree 19,187,264,087 by bound_gcd.c + scan + 10 percent) plus gap bound 21,000,000.', True,
    'Budget, not observation, enters the worst-case total.', HF_L, RO_L)
rec(U, 'LEDGER.GCD', 'LEDGER', 'R2', 'own recount', 'COMPUTED',
    f'derived 19,187,264,087 x 1.10 = {int(19187264087*1.1):,} (+ scan) vs budget 21,108,000,000; observed is {100*(1-19035935044/19187264087):.2f} percent below the derived tree; maxgap 16,747,965 observed vs 21,000,000 bound.', True,
    'Arithmetic on logs/bound_gcd_r2.txt and ledger_r2.txt.', HF_L, RO_L)
rec(U, 'LEDGER.GCD', 'LEDGER', 'R3', 'control', 'COMPUTED',
    'Same bound program at r=1: derived tree 2,435,877,439 (logs/bound_gcd_r1.txt) vs strict r1 observation 2,413,235,457 (arith 355,770,866); r2/r1 ratios: derived 19,187,264,087 / 2,435,877,439 = 7.877, observed 19,035,935,044 / 2,413,235,457 = 7.888, consistent for a 5x size (n log^2 n-like growth). Observation is 0.93 percent below the derived tree at r1, 0.79 percent at r2.', True,
    'Two-point control with the same bound program at both round counts.', HF_L, RO_L)
rec(U, 'LEDGER.GCD', 'LEDGER', 'R4', 'score sensitivity (slack and stage)', 'COMPUTED',
    f'Charging the observation instead of the 10 percent budget: slack {gslack:,} ops over 4 centres = {sv(gslack):.4f} bit; free stage {sv(4*ST["gcdbud"]):.3f} bit. The tightening pass can win about 0.04 bit only if the stage is made halt-free (data independent).', True,
    'Candidate tightening (owner rule: exact counts); not applied here.', HF_L, 'the half-gcd recursion tree is proved data independent so no budget margin is needed', labels=('E',), lever=True,
    gain_basis='T')
rt_obs = 7 + 33383
rec(U, 'LEDGER.ROOTS', 'LEDGER', 'R1', 'value charged', 'COMPUTED',
    'root finding at deg 1: 7 ops; sqrt + map back 3,133 arith + 30,250 other = 33,383; budgets: shifts 4 x 40 x 1,172,907 = 187,665,120 plus gap 1,172,907 plus allowance 200,000 for sqrt/back-map.', True,
    'Budgets charged once for the whole run.', HF_L, RO_L)
rec(U, 'LEDGER.ROOTS', 'LEDGER', 'R2', 'own recount', 'COMPUTED',
    f'4 x 40 x 1,172,907 = {4*40*1172907:,} (= 187,665,120 in the ledger); observed success path {rt_obs:,} ops; budget {sv(ST["rootbud"]+ST["rootgap"]+ST["fg"]):.5f} bit of the total.', True,
    'Arithmetic only.', HF_L, RO_L)
rec(U, 'LEDGER.ROOTS', 'LEDGER', 'R3', 'control', 'COMPUTED',
    'bound_root.c cost for a deg-16 shift 1,172,907 vs r=1 deg-8 shift 1,000,000 bound (old note); consistent with the d <= 16 cap doubling.', True,
    'Compared two bound figures from our own files.', HF_L, RO_L)
rec(U, 'LEDGER.ROOTS', 'LEDGER', 'R4', 'score sensitivity', 'COMPUTED',
    f'free root stage: {sv(ST["rootbud"]+ST["rootgap"]+ST["fg"]):.5f} bit; cutting the cap from 40 to 10 shifts per centre saves {sv(4*30*1172907):.5f} bit. No lever.', True,
    'Bound by removal.', HF_L, RO_L, labels=('Z',))

# ================================================================== U40 VERIFY / TOTAL
U = 'poseidon-r2-U40'
rec(U, 'LEDGER.VERIFY', 'LEDGER', 'R1', 'value charged', 'COMPUTED', 'two reference hashes: 516 arith + 2,064 other = 2,580 ops (1,290 per hash = 5 x 258), success path only.', True,
    'r=1 old charge 474 + 1,896 = 2,370.', HF_L, RO_L)
rec(U, 'LEDGER.VERIFY', 'LEDGER', 'R2', 'own recount', 'COMPUTED',
    'arith 516 = 2 x 258 is consistent with the unit cost. I also ran the reference: verify_collision.py (poseidon_ref.hash_reduced r=2 and the organizer digest) accepts the collision printed in logs/ledger_r2.txt: "collision verified reference ok organizer ok". Pinned permutation vectors 11/11 (orchard/math/t0.py).', True,
    'Validation first: both checks run by me today before any Poseidon-based statement in this workflow.', HF_L, RO_L, ev=WORK + '/testA.json; ' + LO + 'verify_collision.py; ' + LO + 'logs/ledger_r2.txt', labels=('0',) if False else ('N',))
rec(U, 'LEDGER.VERIFY', 'LEDGER', 'R3', 'control', 'COMPUTED', 'the same stage counted 2,370 at r=1 (old charge) and 2,580 at r=2: ratio 1.0886 = 258/237, the ratio of the per-hash unit costs C(2)/C(1).', True,
    'Ratio equals C(2)/C(1) = 258/237 = 1.0886, as it must.', HF_L, RO_L)
rec(U, 'LEDGER.VERIFY', 'LEDGER', 'R4', 'score sensitivity', 'COMPUTED', f'free verification: {sv(2580):.2e} bit. Must be kept (a verified output is what the claim states).', True, 'Bound.', HF_L, RO_L, labels=('Z',))
rec(U, 'LEDGER.TOTAL', 'LEDGER', 'R1', 'value charged', 'COMPUTED',
    f'4 centres: {T4:,} ops = {UNITS:,.1f} units (C(2)=258), time_log2 {TL2:.4f} (note 30.133); one centre {N["log2_1"]:.4f}; memory 40,934,171 B = 2^{MEML:.4f}; score {SCORE:.4f} (note 35.420).', True,
    'Numbers of the stopped r2 sampled package; claimed success probability there 0.00 (3 samples, 0 hits).', HF_L, RO_L, topic='poseidon-r2 package total')
rec(U, 'LEDGER.TOTAL', 'LEDGER', 'R2', 'own recount', 'COMPUTED',
    f'Recomputed to the digit: 662,427 + 4 x {P:,} + 187,665,120 + 1,172,907 + 200,000 = {T4:,}; per-centre {P:,} = 3,999 + 3 + 121,473,076 + 54,638,630,504 + 21,108,000,000 + 21,000,000. Observed 2-centre run 147,592,743,256 = 662,427 + 73,796,042,626 + 73,796,038,203 (exact).', True,
    'Script research/dig/incoming4/work/nums.py.', HF_L, RO_L, topic='poseidon-r2 package total')
rec(U, 'LEDGER.TOTAL', 'LEDGER', 'R3', 'control', 'COMPUTED',
    'r1 strict recount (logs/ledger_r1.txt) total_all 30,163,371,723 for 2 centres, log2 units 26.9233; r2 observed 147,592,743,256, log2 units 29.0916; difference 2.168 bits for a 5x degree (log2 5 = 2.322; n log n factor offset by the fixed budget terms).', True,
    'Both runs by the same builder family under the same strict control charge.', HF_L, RO_L)
rec(U, 'LEDGER.TOTAL', 'LEDGER', 'R4', 'score sensitivity (where a bit comes from)', 'COMPUTED',
    f'score = time_log2 + (memory_log2 - 20) = {TL2:.3f} + {MEML-20:.3f} = {SCORE:.3f}. One bit = halving ops or memory. Centres 4 -> 2: -1.000 bit; ctl share {100*TY["ctl"]/TY_ALL:.1f} percent of observed ops (halving it: {tsav(TY["ctl"]/2):.3f} bit; quartering: {tsav(TY["ctl"]*0.75):.3f}); r=1 precedent: straight-lining took the r1 entry from 28.781 to 27.954 (-0.827 bit, HANDOFF 19:37).', True,
    'The ctl row is the largest single lever visible in the r2 ledger; the r2 numbers above predate any straight-lining of the r2 kernels (ledger run 19:42).', HF_L,
    'a r2 build with straight-lined kernels is measured', labels=('E',), lever=True, gain_basis='T')

# ================================================================== U41 CENTRES
U = 'poseidon-r2-U41'
k_need = lambda p, tgt=0.5: math.ceil(log2(1 - tgt) / log2(1 - p))
rec(U, 'LEDGER.CENTRES', 'LEDGER', 'R1', 'value charged', 'COMPUTED', 'r2 sampled package charges 4 centres (28.133 for one, 30.133 for four); r1 refile charged 4 centres per line (fix2); the first r1 entry 2.', True,
    'Four centres = exactly +2 bits over one.', HF_L, RO_L)
rec(U, 'LEDGER.CENTRES', 'LEDGER', 'R2', 'own recount: centres needed for success 1/2 and 0.8', 'COMPUTED',
    f'at p = {PP:.4f} (Poisson(1/2)) 2 centres give {1-(1-PP)**2:.3f}, 4 give {1-(1-PP)**4:.3f}; at the measured pooled rate {pool_k}/{pool_n} = {pool_k/pool_n:.3f} 4 centres give {1-(1-pool_k/pool_n)**4:.3f}; at the Wilson 95 percent lower limit {wl[0]:.3f}: 4 centres give {1-(1-wl[0])**4:.3f}.', True,
    'Pooled sample = GPU d192 (4/12) + CPU r2 first centres (4/11), line 0 only.', HF_L, 'more samples move the pooled rate', topic='poseidon-r2 centres',
    ev=WORK + '/ledger_numbers.json; research/poseidon/d192_r2_results.jsonl; ' + LO + 'logs/r2_s20*.txt', labels=('B',))
rec(U, 'LEDGER.CENTRES', 'LEDGER', 'R3', 'control (r1 per-line sample against the model)', 'SAMPLED',
    f'r1 per-line sample 57/180 = 0.317 against Poisson 0.3935: z = {r1z:.2f}, one-sided binomial P = {r1p:.3f}. r2 pooled {pool_k}/{pool_n} is P = {pool_p:.3f}. The model may be mildly optimistic.', True,
    'r1 figure from research/poseidon/orchard/lean_r1_fix/per_line_sample.md (HANDOFF 10-12 20:30); binomial computed by me.', HF_L, 'a sample of 100+ r2 centres per line', labels=('B',),
    ev=WORK + '/ledger_numbers.json; research/poseidon/orchard/lean_r1_fix/per_line_sample.md')
rec(U, 'LEDGER.CENTRES', 'LEDGER', 'R4', 'score sensitivity', 'COMPUTED',
    f'k centres cost log2 of ops: 1 {N["log2_1"]:.3f}, 2 about {TL2-1:.3f}, 4 {TL2:.3f}. Each doubling of centres is +1 bit and raises 1-(1-p)^k only from {1-(1-PP)**2:.2f} to {1-(1-PP)**4:.2f} (model). The two-family template (success theorem, one attempt) removes this tradeoff but has its own, larger ledger (r2 not built).', True,
    'Success probability is not a score term; it is a claim the judge accepts or not.', HF_L, RO_L, labels=('N',))

# ================================================================== U42 MEM.GBUF / PEAK
U = 'poseidon-r2-U42'
HFM = 'r2 package memory table (Y 3x2^17, tmp 2^17, MU, g, F dense 32-byte elements, twiddles 2^16); heap peak 40,741,792 in the half-gcd stage; the score term is log2(bytes) - 20'
ROM = 'a different buffer layout or a measured smaller peak'
rec(U, 'MEM.GBUF', 'MEM', 'M2', 'necessity: drop the stored g (recompute from F per use) and recount', 'COMPUTED',
    f'g = 195,313 x 32 = 6,250,016 B. Recomputing it each loop step costs one build g (121,473,076 ops) x 236 steps = {236*121473076:,} ops per centre ({100*236*121473076/P:.0f} percent of a centre): memory saving log2({MEM}/{MEM-6250016}) = {log2(MEM/(MEM-6250016)):.4f} bit vs time cost log2(1+{236*121473076/P:.3f}) = {log2(1+236*121473076/P):.3f} bit. Not worth it.', True,
    'Assumes the recompute is a full build g (upper bound on the cost).', HFM, ROM, ev=WORK + '/ledger_numbers.json; ' + LO + 'pkg_stage_r2/submission-note.md')
rec(U, 'MEM.GBUF', 'MEM', 'M3', 'time cost of shrinking: pack 254-bit elements', 'COMPUTED',
    f'packing 32 -> 31.75 bytes (254 bits) saves {195313*0.25:,.0f} B of g = {log2(MEM/(MEM-195313*0.25)):.5f} bit of memory; every pack/unpack is at least 2 extra ops per element per pass, so the time cost exceeds the gain. Not a lever.', True,
    'Back-of-envelope on the byte count; no build.', HFM, ROM, labels=('Z',))
rec(U, 'MEM.GBUF', 'MEM', 'M4', 'alternatives: g in the transform domain, or half-precision g', 'OPEN',
    'g in the NTT domain would need 3 x 2^17 elements = 12.6 MB (twice the coefficient form). No alternative that holds less than the 6.25 MB dense vector is known; not built.', False,
    'Listed, not tested.', HFM, 'a streaming reduction schedule that never holds g whole is designed and counted', prior=0.03, pot=0.2)
rec(U, 'MEM.PEAK', 'MEM', 'M2', 'necessity: which stage sets the peak', 'COMPUTED',
    f'The peak is the half-gcd stage, 40,741,792 B, not the power stage (37,624,320 B = twiddles 2,097,152 + Y 12,582,912 + tmp 4,194,304 + MU 6,249,952 + g 6,250,016 + F 6,249,984). Build g peaks at 14,638,624 B. Bringing the gcd stage down to the power peak would give {fixed_mem+pow_peak:,} B = 2^{log2(fixed_mem+pow_peak):.4f}, i.e. {MEML-log2(fixed_mem+pow_peak):.4f} bit.', True,
    'Peaks read from the stage lines; sums recomputed by me; 122,747 text/data/bss + 65,536 stack + 4,096 slack added on top as in the note.', HFM, ROM, ev=WORK + '/ledger_numbers.json; ' + LO + 'logs/ledger_r2.txt; ' + LO + 'pkg_stage_r2/submission-note.md')
rec(U, 'MEM.PEAK', 'MEM', 'M3', 'time cost of shrinking the gcd peak by 3.1 MB', 'OPEN',
    'Target: gcd peak down to the power-stage level (-3,117,472 B, 0.1143 bit of memory). Time cost not measured; replacing half-gcd by classical Euclid in place costs of the order m^2 = 3.8e10 multiplies against the stage 1.9e10 total ops, so it is not free. Net sign unknown.', False,
    'Untested; allocations of the gcd matrices not yet inspected line by line.', HFM, 'a gcd schedule with peak <= 37.6 MB at <= 1.08x time is found (break-even 0.1143 bit)', prior=0.1, pot=0.11, labels=('E',))
rec(U, 'MEM.PEAK', 'MEM', 'M4', 'alternatives: peak of the power stage', 'COMPUTED',
    'Power-stage items: Y 12,582,912 B (33.4 percent of the 37,624,320 B power-stage total) and the three 6.25 MB vectors (49.8 percent). Because the heap peak is set by the half-gcd stage, shrinking any power-stage item alone does not change the score term until the gcd stage falls too (the gcd peak is the floor).', True,
    'Item arithmetic only.', HFM, ROM)

# ================================================================== U43 MEM.TWID / RULE
U = 'poseidon-r2-U43'
rec(U, 'MEM.TWID', 'MEM', 'M1', 'bytes held', 'COMPUTED', '65,536 entries x 32 B = 2,097,152 B (rho^j, j < 2^16), 5.12 percent of the 40,934,171 B total; r=1 16,384 entries = 524,288 B.', True,
    'Table item of the memory table.', HFM, ROM)
tab_drop = log2(MEM / (MEM - 2097152))
mulshare = (TY['mul'] + TY['sqr']) / TY_ALL
rec(U, 'MEM.TWID', 'MEM', 'M2', 'necessity: drop the table (tableless NTT) and recount', 'COMPUTED',
    f'Memory gain {tab_drop:.4f} bit. A running-product twiddle costs at least one extra multiply per butterfly; multiplies are {100*mulshare:.1f} percent of all observed ops, and the butterfly multiplies are most of them, so the time cost is up to {tsav(0.9*(TY["mul"]+TY["sqr"])):.3f} bit (90 percent of the multiplies repeated) - larger than the gain.', True,
    'Lower bound on the time cost; real cost also adds loads/stores/control. Net: not worth it.', HFM, 'twiddles are generated at < 1 op per butterfly', labels=('Z',))
rec(U, 'MEM.TWID', 'MEM', 'M3', 'time cost of shrinking the table (half table, sqrt table)', 'OPEN',
    f'Half table (2^15 entries) saves 1,048,576 B = {log2(MEM/(MEM-1048576)):.4f} bit; cost: one extra multiply for the odd-index twiddles in the last layer of each pass, not counted in the ledger source. Not built.', False,
    'Candidate, untested.', HFM, 'built and counted at < 0.02 bit', prior=0.1, pot=0.03)
rec(U, 'MEM.TWID', 'MEM', 'M4', 'alternatives: smaller field-size transform (2^16 -> radix-3 combined)', 'OPEN',
    'The transform length is 3 x 2^17 (Good-Thomas); the table is for 2^17 via 2^16 entries (root powers up to half). A table of 2^15 plus symmetric use is the only variant considered. Not built.', False,
    'Listed.', HFM, 'built and counted', prior=0.05, pot=0.03)
rec(U, 'MEM.RULE', 'MEM', 'M1', 'value of the memory term', 'COMPUTED', f'log2(40,934,171) - 20 = {MEML-20:.4f} bits of the {SCORE:.3f} score ({100*(MEML-20)/SCORE:.1f} percent); r=1 filed: 3.042 of 28.879.', True,
    'Rule: memory term = max(0, log2 bytes - 20).', HFM, ROM)
rec(U, 'MEM.RULE', 'MEM', 'M2', 'necessity: is the 2^20 floor reachable', 'COMPUTED',
    f'To zero the term the program would hold at most 1,048,576 B; the three 6.25 MB vectors alone are 18.7 MB. Each halving of the heap is -1 bit of score and its time price is unmeasured; the 40.9 MB peak is {MEM/1048576:.1f} times the floor.', True,
    'Counting.', HFM, 'an algorithm with a streaming dense-vector schedule is found', labels=('Z',))
rec(U, 'MEM.RULE', 'MEM', 'M3', 'time cost of one bit of memory', 'OPEN',
    'No measured trade curve at r=2. Rough: halving the 6.25 MB vectors needs a two-pass half-length schedule; the repeat factor is unknown, so no number.', False,
    'No test run.', HFM, 'a measured (bytes, ops) point pair', prior=0.1, pot=1.0, labels=('E',))
rec(U, 'MEM.RULE', 'MEM', 'M4', 'alternatives: trade memory for time at the other end (use more memory to cut ops)', 'COMPUTED',
    f'Spending more memory only pays if one extra bit of memory (x2 bytes = +1 bit) saves more than half the ops. The time terms that could be bought with memory (twiddle tables, spectra of operands) are at most the transform share; storing spectra (the memory-hungry schedule) was rejected in the r1 lean build for exactly this reason.', False,
    'Argument from the rule; r1 lean_r1 trade documented in its note.', HFM, 'a table that removes > 50 percent of ops costs under 2x memory')

# ================================================================== U44 MEM.SHRINK
U = 'poseidon-r2-U44'
rec(U, 'MEM.SHRINK', 'MEM', 'M1', 'bytes held by the smaller-memory variants at r=2', 'COMPUTED',
    f'No r=2 variant built. Components: streamed shift saves F-type vector 6,249,984 B ({log2(MEM/(MEM-6249984)):.4f} bit); in-place Euclid targets the {gcd_peak-pow_peak:,} B by which the gcd stage exceeds the power stage ({MEML-log2(fixed_mem+pow_peak):.4f} bit); tableless NTT 2,097,152 B ({tab_drop:.4f} bit). All three together would reach about {fixed_mem+pow_peak-6249984-2097152:,} B = 2^{log2(fixed_mem+pow_peak-6249984-2097152):.3f}, a gain of {MEML-log2(fixed_mem+pow_peak-6249984-2097152):.3f} bit if free.', True,
    'Arithmetic on the item table; time costs unknown (MEM.SHRINK M3).', HFM, 'any of the three is built and counted', ev=WORK + '/ledger_numbers.json; research/poseidon/orchard/lean_r1_mem/')
rec(U, 'MEM.SHRINK', 'MEM', 'M3', 'time cost of shrinking', 'OPEN',
    'Not measured at r=2. Break-evens in bits (memory gain that a time cost must stay under): dropping the F vector 0.2390 (only valid if the peak stage also loses it), gcd-peak reduction 0.1143, tableless 0.0759. The tableless variant is bounded above by the multiply share (see MEM.TWID M2) and fails the break-even. Priced by Luna 3 for r=1; lean_r1_mem was running.', False,
    'No r=2 build.', HFM, 'lean_r1_mem results (r=1) transfer: a measured r1 time ratio < 2^bits_saved', prior=0.15, pot=0.2, labels=('E',))

# ================================================================== U45 PREM
U = 'poseidon-r2-U45'
HFP = 'r2, line j=0, first centre of each execution (CPU lean_r2 logs: seeds 201000-201004, 202000-202005) and GPU d192 centres (12), centres uniform, halts counted as failure'
ROP = 'a sample of 100+ r2 centres per line shows a rate outside the model band'
hist_p = {0: 15, 1: 7, 2: 1}
expP = {k: 23 * exp(-0.5) * 0.5 ** k / math.factorial(k) for k in range(3)}
chi = sum((hist_p[k] - expP[k]) ** 2 / expP[k] for k in range(3)) + (0 - (23 - sum(expP.values()))) ** 2 / max(23 - sum(expP.values()), 1e-9)
rec(U, 'PREM.HPOIS', 'PREM', 'R2', 'own recount: root-count histogram of the odd-part polynomial', 'SAMPLED',
    f'pooled 23 centres: zero square roots 15, one 7, two 1; Poisson(1/2) expects {expP[0]:.1f}, {expP[1]:.1f}, {expP[2]:.1f} (+{23-sum(expP.values()):.2f} for 3+). r1 note histogram (65 runs): 37/20/7/1 vs Poisson 39.4/19.7/4.9/0.8.', True,
    'GPU nonzero_square_roots (12) + CPU degG (11). No contradiction at this size; sample is small.', HFP, ROP, topic='poseidon-r2 H1 histogram',
    ev=WORK + '/ledger_numbers.json; research/poseidon/d192_r2_results.jsonl; ' + LO + 'logs/')
rec(U, 'PREM.HPOIS', 'PREM', 'R4', 'score sensitivity of the Poisson premise', 'COMPUTED',
    f'H1 gives one-centre success {PP:.4f} and two-centre {1-(1-PP)**2:.3f}. If the true rate were the sample lower limit {wl[0]:.3f}, 4 centres give {1-(1-wl[0])**4:.3f}; to keep 0.866 would need {k_need(wl[0], 0.866)} centres (+{log2(k_need(wl[0],0.866)/4):.2f} bit). A theorem-level claim replaces H1 (Paley-Zygmund 1/3 route, see JUDGE.JHEUR).', True,
    'Arithmetic from the pooled sample.', HFP, ROP, labels=('E',))
rec(U, 'PREM.HSQ', 'PREM', 'R2', 'own recount: P(g has a nonzero square root) per centre', 'SAMPLED',
    f'r2 pooled {pool_k}/{pool_n} = {pool_k/pool_n:.3f}, Wilson 95 percent [{wl[0]:.3f}, {wl[1]:.3f}], 99 percent [{wl99[0]:.3f}, {wl99[1]:.3f}]; model {PP:.4f} lies inside. Components: GPU 4/12, CPU 4/11. r1 D189 8/20; r1 per-line 57/180 = 0.317.', True,
    'Counts as above. The r1 per-line 0.317 is below the model at z = %.2f.' % r1z, HFP, ROP, topic='poseidon-r2 HSQ rate',
    ev=WORK + '/ledger_numbers.json; research/poseidon/d192_r2_results.jsonl; ' + LO + 'logs/')
rec(U, 'PREM.HSQ', 'PREM', 'R4', 'score sensitivity', 'COMPUTED',
    f'Per +0.05 of the one-centre rate the 4-centre success moves {1-(1-PP-0.05)**4-(1-(1-PP)**4):+.3f}; going from 2 to 4 centres costs +1.000 bit of time. Rate at the lower limit {wl[0]:.3f} would need {k_need(wl[0],0.5)} centres for 1/2 and {k_need(wl[0],0.8)} for 0.8.', True,
    'Arithmetic.', HFP, ROP, labels=('E',))
for q, ques, num, nt in [
    ('R1', 'value charged', 'g squarefree is assumed in the stage D budget (the half-gcd tree and the root splitter treat g as squarefree); no probability term is charged for it.', 'It is a supporting premise.'),
    ('R2', 'own recount', f'squarefree in 12/12 GPU d192 r2 centres (field "squarefree": true); 20/20 at r1 (D189). CPU: gcd degrees consistent (no repeated factor seen in 11 runs).', 'Counted from the JSONL.'),
    ('R3', 'control', f'random polynomial of degree n over F_p is non-squarefree with probability about 1/p: n/p = 195,312 / 2^254 = 2^{log2(195312)-254:.1f}; no mechanism making g non-squarefree on this family is known (the odd part of F(c+s)-F(c-s) is a bivariate resultant-type object, indecomposable F at all inner degrees tested, see ALT.FUNCDEC).', 'Heuristic bound; the tested squarefree rate is 12/12.'),
    ('R4', 'score sensitivity', 'if g had a repeated factor the gcd stage would return it and the centre fails; at probability 2^-236 per centre, no effect on any score.', 'Negligible.')]:
    rec(U, 'PREM.HSQFREE', 'PREM', q, ques, 'SAMPLED' if q in ('R2',) else 'COMPUTED', num, q in ('R2', 'R4'), nt, HFP, 'a repeated factor in any r2 centre', labels=('Z',) if q == 'R4' else ('N',),
        ev='research/poseidon/d192_r2_results.jsonl; research/poseidon/d189_gpu_results.jsonl')

# ================================================================== U46 HCENT / HUNIF
U = 'poseidon-r2-U46'
HFC = HFP + '; centres independent (fresh random centre each)'
rec(U, 'PREM.HCENT', 'PREM', 'R1', 'value charged', 'COMPUTED', 'r2 sampled package: 4 independent centres on line 0, claim 0.00 (smallest Wilson limit with 0 of 3 samples). r1 refiles: 2 then 4 centres.', True,
    'From claim.json and submission-note.md of pkg_stage_r2.', HFC, RO_L)
rec(U, 'PREM.HCENT', 'PREM', 'R2', 'own recount: what 4 centres give at the measured rate', 'COMPUTED',
    f'4 centres at {pool_k}/{pool_n}: {1-(1-pool_k/pool_n)**4:.3f}; at the model {1-(1-PP)**4:.3f}; at the lower limit {1-(1-wl[0])**4:.3f}; the stopped package claimed 0.00 because its own 3-run sample on line 0 had 0 hits (Wilson lower limit 0).', True,
    'Arithmetic; sample includes later runs (r2_s2010xx, s2020xx) not in the package.', HFC, RO_L)
rec(U, 'PREM.HCENT', 'PREM', 'R3', 'control: independence of centres', 'OPEN',
    'Independence is assumed (fresh uniform centre); the 11 CPU runs use distinct seeds and showed no pattern, but no test of independence (e.g. repeated-centre collision rate) was run. Proved lower bound for the centre-based route is only about 1/78,124 per centre (HANDOFF 10-12 19:35).', False,
    'Not tested.', HFC, 'a test that finds dependence between the line-j centres', prior=0.05, pot=0.2)
rec(U, 'PREM.HCENT', 'PREM', 'R4', 'score sensitivity', 'COMPUTED',
    f'1 centre {N["log2_1"]:.3f}, 2 centres {TL2-1:.3f}, 4 centres {TL2:.3f} bits of time; the proved-only route would need about 38,600 centres (+{log2(38600/4):.1f} bits over 4, score about 46 per HANDOFF), the two-family template removes centres altogether.', True,
    '38,600 figure from HANDOFF 10-12 19:35, not recomputed.', HFC, RO_L, labels=('E',))
rec(U, 'PREM.HUNIF', 'PREM', 'R2', 'own recount: random-coefficient model of g against the real g', 'SAMPLED',
    f'toy p=257 one-centre 0.367-0.404 (earlier work); real r2 pooled {pool_k/pool_n:.3f} (n={pool_n}) and r1 0.317-0.40 (n=180/20): all within about two standard errors of 0.3935 except r1 per-line (z={r1z:.2f}).', True,
    'No new toy run; only the real samples were recounted.', HFC, ROP, topic='poseidon-r2 HSQ rate')
rec(U, 'PREM.HUNIF', 'PREM', 'R4', 'score sensitivity', 'COMPUTED',
    f'If coefficients of the real g are not uniform and the true rate sits at 0.30, 4 centres give {1-0.7**4:.3f} (vs {1-(1-PP)**4:.3f}); matching 0.866 would need {k_need(0.30,0.866)} centres: +{log2(k_need(0.30,0.866)/4):.2f} bit.', True,
    'Scenario arithmetic.', HFC, ROP, labels=('E',))

# ================================================================== U47 JUDGE
U = 'poseidon-r2-U47'
HFJ = 'rulings of the r1 filings as recorded in HANDOFF.md 10-12 18:20 .. 20:25; no r2 entry has been filed'
ROJ = 'an r2 entry is filed or a new ruling on r1 appears'
EVJ = 'HANDOFF.md (lines 414-431); research/dig/incoming4/work/ledger_numbers.json'
rec(U, 'JUDGE.JFILED', 'JUDGE', 'R1', 'ruling on the filed entries', 'BEDROCK',
    'r1: 651c0ca6 REFUTED (fail 1 of 2; sole fatal lane_cost/F-COST-1: per-element control charged 4-12 per 16 elements); refile 142889b7 not_evaluable (first submit refused: note under 5 KiB; refile 28.781 + 3.043 = 31.824); 56ddf2d0 REFUTED (fatal: uncharged NTT switch dispatch, +0.005 bit; 27.954 + 3.047 = 31.001). r2: nothing filed; the sampled r2 package was stopped.', False,
    'Recorded from HANDOFF; I did not fetch the dossiers.', HFJ, ROJ, ev=EVJ, labels=('N',))
rec(U, 'JUDGE.JFILED', 'JUDGE', 'R2', 'own recount: does the stopped r2 package charge what each ruling named', 'OPEN',
    'Facts: the r2 staged source charges the NTT dispatch (ntt.c CTL(7) "call, switch on k ..." comments) and loops 8 per element; I did not recount the whole proof.md against the executed C. The 56ddf2d0 defect size, 0.005 bit = 0.35 percent, would be about 1.1e9 ops at this total.', False,
    'Greps only (ntt.c, proof.md lines 88-90, 993-1036).', 'r2 pkg_stage_r2 as of 19:42', 'a line-by-line charge audit of the r2 source (the F-COST class) is run', prior=0.3, pot=0.01, labels=('E',),
    ev=LO + 'ntt.c; ' + LO + 'pkg_stage_r2/proof.md')
rec(U, 'JUDGE.JFILED', 'JUDGE', 'R3', 'control: did r1 get through where the ledger was the same', 'BEDROCK',
    'No r1 entry has been judged accepted; the three tries failed on different fatal items (control charge, probability note length, dispatch). The r2 package was built with the stricter charging from the first refile.', False,
    'From the HANDOFF sequence.', HFJ, ROJ, ev=EVJ)
rec(U, 'JUDGE.JFILED', 'JUDGE', 'R4', 'score sensitivity of the rulings', 'COMPUTED',
    f'Each fatal item cost one filing, the numbers moved: control-charge recount x7.3 ops (25.837 -> 28.781, +2.944 bits), straight-lining -0.827 bit, dispatch +0.005 bit. At r2 the ctl share is {100*TY["ctl"]/TY_ALL:.1f} percent of observed ops.', False,
    'Numbers from HANDOFF plus own ctl share.', HFJ, ROJ, ev=EVJ)
rec(U, 'JUDGE.JRUNNER', 'JUDGE', 'R1', 'value: runner cannot size the Orchard digest', 'COMPUTED',
    'The organizer digest takes exactly 64 bytes (two LE field encodings) and rejects non-canonical elements; our digest_bytes mirror raises ValueError for any other length, including b"". The r2 note states "No Python experiment is declared".', True,
    'Behaviour of our mirror (poseidon_ref.digest_bytes) read and exercised in verify_collision; the organizer runner itself was not run (yukon).', 'poseidon_ref.py digest_bytes; r2 package note', 'the organizer changes the runner or adds an Orchard sizing hook', ev=LO + 'poseidon_ref.py; ' + LO + 'pkg_stage_r2/submission-note.md')
rec(U, 'JUDGE.JRUNNER', 'JUDGE', 'R2', 'own recount', 'COMPUTED', 'Run today: poseidon_ref.digest_bytes raises ValueError("need exactly 64 bytes") for lengths 0 and 63, accepts 64, and raises ValueError("non-canonical field element") for 0xff x 64 (work/test_digest_empty.txt). The organizer module is called with 64-byte messages in verify_collision.py (collision verified).', True,
    'Local call of our mirror, not the organizer runner (not run: yukon is off limits).', 'poseidon_ref mirror', 'the runner is found to call a different entry point', ev=WORK + '/test_digest_empty.txt; ' + LO + 'poseidon_ref.py')
rec(U, 'JUDGE.JRUNNER', 'JUDGE', 'R3', 'control: whether a Python experiment could be declared instead', 'OPEN',
    'A declared experiment would need to size a digest with a valid 64-byte input; not tried because candidate files and experiments are limited to 64 KiB and the C program is far larger. A 4-line Python experiment that only reports counts could be declared; judge reaction unknown.', False,
    'Not tested.', 'intake limits', 'a judge ruling names the missing experiment as material', prior=0.15, pot=0.0)
rec(U, 'JUDGE.JRUNNER', 'JUDGE', 'R4', 'score sensitivity', 'COMPUTED', 'No score term. The missing experiment was listed as a non-fatal material in the r1 ruling.', False,
    'From HANDOFF 10-12 18:20 ("Materials (not fatal)").', HFJ, ROJ, ev=EVJ)

# ================================================================== U48 JHEUR
U = 'poseidon-r2-U48'
rec(U, 'JUDGE.JHEUR', 'JUDGE', 'R1', 'value: score-critical heuristic declared', 'BEDROCK',
    'r2 package: H1 per-line success fractions (score-critical), H2 charging rules, H3 stage budgets enforced as halts. Claimed probability 0.00 (smallest line limit 0.0000 from 3 samples).', False,
    'claim.json of pkg_stage_r2.', 'r2 sampled package', 'a different template is filed', ev=LO + 'pkg_stage_r2/claim.json')
rec(U, 'JUDGE.JHEUR', 'JUDGE', 'R2', 'own recount: the premise against our data', 'SAMPLED', f'pooled r2 rate {pool_k}/{pool_n} = {pool_k/pool_n:.3f} [{wl[0]:.3f}, {wl[1]:.3f}] (95 percent); a claim at the Wilson limit with 20 samples per line was planned and not made.', True,
    'See PREM.HSQ R2.', HFP, ROP)
rec(U, 'JUDGE.JHEUR', 'JUDGE', 'R3', 'control: judge verdict on sampled-rate claims', 'BEDROCK',
    'HANDOFF 10-12 20:25: all materials on the SAMPLED probability were named; "sampled rates are not accepted by the judges" (per_line_sample.md note 20:30). The proved route is the two-family template (success p/(2p-1), theorem).', False,
    'From HANDOFF.', HFJ, ROJ, ev=EVJ)
rec(U, 'JUDGE.JHEUR', 'JUDGE', 'R4', 'score sensitivity: proved vs sampled', 'COMPUTED',
    f'Proved-only single-family route about 38,600 centres (+{log2(38600/4):.1f} bits over 4 centres) vs the two-family template (one attempt, 2 lines, success >= 0.4999999999): its r1 ledger worst case is a W^p mod (f-y) of degree 78,125 per line (92.25e9 ops at the top level, logs/calib.txt) against 45.56e9 for the odd part; r2 not built (top level would scale about 5x).', False,
    'Calibration read from twofam_r1/logs/calib.txt; r2 scaling is a statement, not a measurement.', HFJ, 'the r2 two-family ledger is built', ev='research/poseidon/orchard/twofam_r1/logs/calib.txt; ' + EVJ, labels=('E',))

# ================================================================== U49-54 MACHINE
def machine(unit, loc, label_, cnt, share_note, q2, q3, q4, labs_q4=('E',)):
    HFM2 = HF_L + '; counts are from the two-centre observed run (evaluation units excluded), per centre = half'
    ev = WORK + '/ledger_numbers.json; ' + LO + 'logs/ledger_r2.txt'
    rec(unit, loc, 'MACHINE', 'Q1', f'{label_}: operations charged', 'COMPUTED', cnt, True, share_note, HFM2, RO_L, ev=ev)
    for q, t, qq, lab in (('Q2', q2, 'necessity (drop or change, recount)', ('Z',)), ('Q3', q3, 'degrees of freedom', ('N',)), ('Q4', q4, 'alternatives', labs_q4)):
        st_, num, nt = t[0], t[1], t[2]
        own = st_ != 'OPEN' and not (len(t) > 3 and t[3] is False)
        opn = st_ == 'OPEN'
        rec(unit, loc, 'MACHINE', q, f'{label_}: {qq}', st_, num, own, nt, HFM2, 'built and counted with a fresh ledger run' if opn else RO_L, ev=ev, labels=lab,
            prior=0.1 if opn else None, pot=0.05 if opn else None)


mul = TY['mul']; sqr = TY['sqr']
machine('poseidon-r2-U49', 'MACHINE.FMUL', 'field multiplication and squaring',
        f'mul {mul:,} + sqr {sqr:,} = {mul+sqr:,} ops (1 op each) in the 2-centre run, {100*(mul+sqr)/TY_ALL:.2f} percent of all {TY_ALL:,} observed ops; per centre about {(mul+sqr)//2:,}.',
        'TYPES line of logs/ledger_r2.txt; evaluation units (202,899,458) excluded from the type rows.',
        (f'COMPUTED', f'If multiplications were free the observed run would drop {tsav(mul+sqr):.4f} bit; so no multiplication-count change (Karatsuba, radix choice) can gain more than that.', 'Bound by removal.'),
        ('COMPUTED', f'Where the arithmetic (add, sub, mul, sqr) lives: share of one centre arith ops: power stage {100*16131772597/19308714999:.1f} percent, half-gcd {100*3170520858/19308714999:.1f} percent, build {100*6421153/19308714999:.2f} percent (stage arith lines).', 'Which parts of the program the count depends on.'),
        ('OPEN', 'Radix-4 / split-radix butterflies cut NTT multiplies by about a quarter; with the 0.1283-bit total multiply bound that is at most 0.03 bit. Not built.', 'Listed, untested.'))
machine('poseidon-r2-U50', 'MACHINE.FADD', 'field addition and subtraction',
        f'add {TY["add"]:,} + sub {TY["sub"]:,} = {TY["add"]+TY["sub"]:,} ops = {100*(TY["add"]+TY["sub"])/TY_ALL:.1f} percent of observed ops (1 op each).',
        'In the source an add/sub field operation is one charged op; whether a modular conditional correction is a second op is the charging rule of proof.md section 4 (not re-audited here).',
        ('COMPUTED', f'Free add/sub would save {tsav(TY["add"]+TY["sub"]):.3f} bit; lazy reduction can only remove the correction part of it.', 'Bound by removal.'),
        ('COMPUTED', f'add:sub ratio {TY["add"]/TY["sub"]:.3f}; add + sub per multiply {(TY["add"]+TY["sub"])/(TY["mul"]+TY["sqr"]):.2f} (a radix-2 butterfly has 1 multiply and 2 add/sub, plus pointwise and reduction work).', 'Structure of the count.'),
        ('OPEN', 'Lazy-reduction NTT (values in [0, 2p) between layers) would remove compares in the add/sub path; gain bounded by the add/sub share. Not built.', 'Listed, untested.'))
machine('poseidon-r2-U51', 'MACHINE.LDST', 'loads and stores',
        f'ld {TY["ld"]:,} + st {TY["st"]:,} = {TY["ld"]+TY["st"]:,} ops = {100*(TY["ld"]+TY["st"])/TY_ALL:.1f} percent of observed ops (one per 256-bit element).',
        'Loads 1.78 per store; transform passes are blocks of up to 4 butterfly layers in a 16-element register block.',
        ('COMPUTED', f'Free loads/stores would save {tsav(TY["ld"]+TY["st"]):.3f} bit; a wider register block (5 layers per pass) removes at most 1/5 of the NTT pass traffic: <= {tsav(0.2*(TY["ld"]+TY["st"])):.3f} bit.', 'Bound; assumes all ld/st are pass traffic.'),
        ('COMPUTED', 'Passes: a transform of 2^17 points with 4 layers/pass is 5 passes (4,4,4,4,1), with 5 layers/pass it is 4 (5,5,5,2).', 'Pass count arithmetic.'),
        ('OPEN', 'Fusing the pointwise multiply into the last forward pass and the first inverse pass saves one load/store round per squaring; not built, size unknown.', 'Listed, untested.'))
machine('poseidon-r2-U52', 'MACHINE.ADDR', 'addressing arithmetic and index computation',
        'Not a separate row in the ledger: all address calculations are inside CTL (proof.md line 88: every comparison, branch, loop update, shift, add, subtract, multiply, reduction and address calculation on indices and pointers is charged 1), 84,719,163,718 ops in the run.',
        'Straight loops (loopc) are charged 8 per element (increment, compare, branch, up to 3 pointer updates); constant-stride kernels are charged none for constant displacements (proof.md lines 1018-1019).',
        ('OPEN', 'No separate count exists, so a recount without addresses is not possible from the ledger; an instrumented rerun with a separate ADDR counter was not made.', 'Untested.', None),
        ('OPEN', 'Degrees of freedom: stride class per pass (constant stride none, variable stride 1 per element load/store when s > 1), loop style (straight 8 per element vs nested).', 'Read from proof.md only.', False),
        ('OPEN', 'Fully unrolled constant-stride kernels per layer pattern; part of the straight-line lever (MACHINE.CTL).', 'Listed.'))
ctl = TY['ctl']
machine('poseidon-r2-U53', 'MACHINE.CTL', 'loop control and branches',
        f'ctl {ctl:,} ops = {100*ctl/TY_ALL:.2f} percent of all observed ops ({100*ctl/TY_SUM:.1f} percent of the non-unit ops); r1 strict recount 17,668,344,662 of 30,163,371,723 = 58.6 percent.',
        'The largest single row of the ledger; per element charges, not per block.',
        ('COMPUTED', f'Halving ctl: {tsav(ctl/2):.3f} bit; to a quarter: {tsav(ctl*0.75):.3f} bit; to zero: {tsav(ctl):.3f} bit. The r1 entry gained 0.827 bit from straight-lining (28.781 -> 27.954).', 'Projection on the observed run; budgets scale about the same.'),
        ('COMPUTED', 'The share is almost identical at r1 (58.6) and r2 (57.5 percent): the control cost is per element, independent of the degree.', 'Two runs, same builder.'),
        ('OPEN', 'Apply the r1 straight-lining (constant-stride, unrolled kernels) to the r2 build; expected gain by transfer about 0.5-0.8 bit. Not built; the r2 source in lean_r2 was edited after the ledger run (ntt.c 20:21) so a fresh ledger is needed before any number is filed.', 'Candidate lever.'),
        labs_q4=('E',))
machine('poseidon-r2-U54', 'MACHINE.REGS', 'register budget and spills',
        'Not stated in the ledger; the model assumes a register file of 16 field words per transform block (note: "the register file of 16 words per transform block is the one structural assumption"). No spill traffic is charged separately: a block that does not fit would show as extra ld/st that the model does not count.',
        'Assumption listed by the filed r1 note as a limit.',
        ('OPEN', 'Recount with an 8-word register file: 3 layers per pass instead of 4 raises NTT pass traffic from 5 to 6 passes per 2^17 transform (+20 percent of the ld/st share), at most %.3f bit worse on the observed run if all ld/st are pass traffic.' % log2(1 + 0.2 * (TY['ld'] + TY['st']) / TY_ALL), 'Arithmetic, not a build.'),
        ('OPEN', 'Dof: words per block (8, 16, 32) = layers per pass 3, 4, 5. A 32-word block is the AVX-512 register count and 16 words is the plain x86-64 SIMD count: the assumption is hardware-legal only on 16-register machines.', 'Reading.', False),
        ('OPEN', 'Replace the assumption by a charged spill model; not done.', 'Listed.'))

# ================================================================== U55-U62 ALT
HFD_T = 'toy F_103, r=2 schedule (4 full, 2 partial, 4 full), random Cauchy MDS, random constants, seeds 1-5, trail direction u = (0, M02, -M01) after R3.M'
HFA = 'the r=2 line polynomial F_j(W) (j = 0, 1, 2; degree 5^8 = 390,625, leading coefficient nonzero) on Pallas; other round counts only as stated'
dec_rows = {r['inner']: r for r in D}
dtxt = '; '.join(f'inner {r["inner"]}: {r["nonconst"]} of {r["digits"]} digits nonconstant ({r["secs"]} s)' for r in D)
U = 'poseidon-r2-U55'
rec(U, 'ALT.FUNCDEC', 'ALT', 'Q1', 'is F_j at r=2 functionally decomposable: inner degrees tested', 'LOCAL_ONLY',
    f'No decomposition. Earlier runs: inner 5, 25, 125 at r=2 for j=0,1,2 (levels/decomp/RESULT.md). New today, j=0, validated tool: {dtxt}. 78125 was started and stopped by me after the 3-minute limit (no result, OPEN). Remaining proper inner degrees of 5^8 not yet run: {", ".join(str(d) for d in (625,3125,15625,78125) if d not in dec_rows) or "none"}; j=1,2 at those degrees OPEN.', True,
    'Kozen-Landau test on the real F (flint), tame case so one candidate per degree is exhaustive; tool validated by planted decompositions at r=1 (math/decomp_625_3125.md) and by the earlier controls. Planted control at r=2 degree: see Q3.',
    HFA + '; j=0 for the new degrees', 'any inner degree of 5^8 returns zero nonconstant digits', ev=WORK + '/testD_real_j0.txt; research/poseidon/levels/decomp/RESULT.md; research/poseidon/math/decomp_625_3125.md; research/poseidon/levels/decomp/decomp.py', topic='poseidon-r2 FUNCDEC', labels=('N',))
rec(U, 'ALT.FUNCDEC', 'ALT', 'Q2', 'necessity: what a decomposition would be worth', 'COMPUTED',
    'If F = G(H) with deg H = d, collisions F(a) = F(b) include all H(a) = H(b) (a free collision family of equation degree d instead of 390,625) plus G-collisions on the image; none exists, so the odd-part route stays the only one. The proof of the good-centre fraction also needs indecomposability (Burnside-Schur chain).', False,
    'Argument; HANDOFF 10-12 19:35.', HFA, 'a decomposition is found', ev='HANDOFF.md', labels=('K',))
rec(U, 'ALT.FUNCDEC', 'ALT', 'Q3', 'degrees of freedom: coverage of the divisor lattice and the control', 'COMPUTED',
    f'Divisors of 5^8: d = 5^k, k = 1..7 (7 inner degrees). Covered at r=2 j=0: k = 1,2,3 (earlier) and {sorted(dec_rows)} (today) = {3+len(dec_rows)} of 7; j=1,2: k = 1,2,3 only. Control run by the same code at r=1 with planted G.H (625, 3125, 15625) recovered H exactly.', True,
    'Coverage count; control from math/decomp_625_3125.md (the r=2 size was not separately planted in this run).', HFA, 'the missing (j, d) cells are run (about 100 s each)', labels=('N',))
rec(U, 'ALT.FUNCDEC', 'ALT', 'Q4', 'alternatives: additive decomposition / other composition types', 'OPEN',
    'Only composition F = G.H was tested. Additive (linearized) and Dickson-type factors: in characteristic p with degree 5^k the additive case needs degree a power of p, which exceeds 390,625; Dickson/Chebyshev types not tested.', False,
    'Argument; no test.', HFA, 'a Dickson or Chebyshev structure is suspected on a toy', prior=0.02, pot=1.0)

U = 'poseidon-r2-U56'
rec(U, 'ALT.FREELUNCH', 'ALT', 'Q1', 'FreeLunch applied to r=2: degree and cost', 'CLAIMED-UNTESTED',
    'Poseidon is not in the FreeLunch paper (Griffin, Anemoi, Arion, XHash8). For forward x^5 the free Groebner basis is vacuous: ideal degree D_I = 5^(6+r) = 390,625 at r=2, the same univariate polynomial we already have. FGLM cost O(D_I^3) or the faster char-poly route is worse than gcd with x^p - x.', False,
    'Scout reading of the CRYPTO 2024 slides and abstract (research/poseidon/levels/freelunch/FREELUNCH.md); the paper PDF was not retrievable. No code run.', HFA, 'a Poseidon-specific partial-round model in the full paper gives ideal degree below 5^8', ev='research/poseidon/levels/freelunch/FREELUNCH.md', labels=('K',))
rec(U, 'ALT.FREELUNCH', 'ALT', 'Q2', 'necessity: could the method be used without the line trick', 'CLAIMED-UNTESTED',
    'Without the two-free-round skip the ideal degree is 5^(8+r) = 5^10 = 9,765,625; our exact plane-degree tracker (testA.json) gives total degree 5^10 for the digest in (nk, rho), matching D_I of the generic model.', True,
    'Degree tracker is my arithmetic (dense MDS assumed); the FreeLunch side is read, not tested.', HFA, 'a skip better than two rounds exists in the plane', ev=WORK + '/testA.json; research/poseidon/levels/freelunch/FREELUNCH.md')
rec(U, 'ALT.FREELUNCH', 'ALT', 'Q3', 'degrees of freedom of the system', 'CLAIMED-UNTESTED',
    'CICO-1 fixes one output with 1 free input; our collision has 2 free inputs and 1 compared lane. The only variable left after the skip is W (one), so the system has 1 degree of freedom and the GB is the univariate polynomial.', False,
    'Derived in the scout note; not tested.', HFA, 'a collision-specific FreeLunch variant is published', ev='research/poseidon/levels/freelunch/FREELUNCH.md', labels=('K',))
rec(U, 'ALT.FREELUNCH', 'ALT', 'Q4', 'alternatives: inverse-S-box variable trick', 'OPEN',
    'The gain mechanism of FreeLunch is the inverse-power component (huge forward degree, small implicit form). Poseidon has only forward x^5; adding a variable per S-box output does not lower the final univariate degree. See ALT.BACKSKIP for the inverse direction.', False,
    'No test; derived.', HFA, 'a backward model with an implicit S-box form lower than 5^8 is built', prior=0.02, pot=1.0)

U = 'poseidon-r2-U57'
rec(U, 'ALT.CHEAPLUNCH', 'ALT', 'Q1', 'CheapLunch ideal degree at r=2', 'CLAIMED-UNTESTED',
    'Paper bound D_I <= d^(k*RF + RP) with k=1: 5^(8+2) = 9,765,625; with its first-variable skip s = 1: 5^9 = 1,953,125. Ours: 5^8 = 390,625, i.e. smaller by 5 times (and 25 times).', True,
    'Formula from the paper (Sect. 4.2, read by the scout from the Wayback PDF); evaluation by me. The paper bound is conjectured tight, not proved.', HFA, 'a CheapLunch Poseidon table with RP = 2 and k = 1 shows D_I < 5^8', ev='research/poseidon/levels/cheaplunch/CHEAPLUNCH.md', labels=('K',))
rec(U, 'ALT.CHEAPLUNCH', 'ALT', 'Q2', 'necessity: does the method need CICO-(t-k, k)', 'CLAIMED-UNTESTED',
    'Yes: it is built for k >= 1 outputs constrained; our collision compares one lane (k = 1) and leaves two lanes free, which turns the system underdetermined and returns us to the fixed-free-variable trick already used.', False,
    'Scout reading, no code.', HFA, 'a collision (not CICO) variant is published', ev='research/poseidon/levels/cheaplunch/CHEAPLUNCH.md', labels=('K',))
rec(U, 'ALT.CHEAPLUNCH', 'ALT', 'Q3', 'degrees of freedom', 'CLAIMED-UNTESTED',
    'Variables k + RP = 3 at r=2 (one y per partial round plus x). Weighted degree of regularity <= d*k*(d^RF - 1) + 1 = 5 * (5^8 - 1) + 1 = 1,953,121 (paper formula; my arithmetic).', True,
    'Formula arithmetic only.', HFA, 'experiment at RP=2 in a 64-bit field contradicts the bound', ev='research/poseidon/levels/cheaplunch/CHEAPLUNCH.md')
rec(U, 'ALT.CHEAPLUNCH', 'ALT', 'Q4', 'alternatives: FGLM memory', 'CLAIMED-UNTESTED',
    'The paper states no memory figure; FGLM holds at least D_I-sized matrices (>= 9.8e6 field elements = 312 MB at 5^10 and 62 MB at 5^9) against our 40.9 MB total: the memory term alone is >= 0.6 bit worse.', True,
    'Arithmetic: 1,953,125 x 32 B = 62.5 MB; log2(62.5e6/40.9e6) = 0.61. Lower bound.', HFA, 'a sparse-FGLM variant with memory below 40 MB is shown', ev='research/poseidon/levels/cheaplunch/CHEAPLUNCH.md', labels=('K',))

U = 'poseidon-r2-U58'
rec(U, 'ALT.GKR', 'ALT', 'Q1', 'subspace trail at r=2: dimension', 'BEDROCK',
    f'Trail dimension 2, 1, 0 for k = 1, 2, 3 partial rounds (PROVED, levels/LEVELS.md); at r=2 the dimension is 1 (direction u = (0, M02, -M01) at the R3.M output). Real MDS checks today: all 9 + 9 + 1 minors nonzero (so MDS), pinned permutation vectors 11/11.', True,
    'Minors recomputed by me on the pinned MDS (testA.json); det[e0; e0M; e0M^2] = 0xebe164ab9dff92f6...8ba recomputed by me and equal to the LEVELS value, nonzero; (M u)_0 = 0 and (M^2 u)_0 != 0 on the real MDS (testF.json).', HFA, 'a nonzero invariant subspace of M is found (it would raise the dimension)', ev=WORK + '/testA.json; ' + WORK + '/testF.json; research/poseidon/levels/LEVELS.md', labels=('N',))
rec(U, 'ALT.GKR', 'ALT', 'Q2', 'necessity: is the trail needed by the attack', 'COMPUTED',
    'No: the line attack does not use it. The trail is a differential: a difference t*u survives P1 and P2 unseen, but the four tail full rounds activate all lanes (tail minimum: weights over s0..s3 sum to 8, i.e. at least 8 active S-box positions in 4 rounds).', True,
    f'Tail chains recomputed by me with the pinned MDS: {A["tail"]["mds_ok"]} support chains pass the MDS constraint, {A["tail"]["with_lane0_zero_output"]} also end with lane 0 zero, {A["tail"]["weight_patterns"]} weight patterns, min total active {A["tail"]["min_total_active"]} (LEVELS: 337 / 25).', HFA, 'a trail through the tail is found', ev=WORK + '/testA.json', labels=('N',))
rec(U, 'ALT.GKR', 'ALT', 'Q3', 'degrees of freedom: do trail pairs collide more often than random pairs', 'LOCAL_ONLY',
    'Toy F_103, r=2, 5 random Cauchy MDS/constant seeds, exhaustive: pairs of inputs whose states after R3 differ by t*u (u = (0, M02, -M01), t != 0): 26,146 pairs, 266 digest collisions = 0.01017; random-direction controls (15 directions): 79,402 pairs, 719 collisions = 0.00906; random rate 1/103 = 0.00971 (expected 254 +- 16, z = +0.77). Trail property confirmed on every seed ((M u)_0 = 0). The trail gives pairs with equal lane-0 S-box input in both partial rounds, but the digest collides at the random rate.', True,
    'Toy only; the real field cannot be enumerated. Matches LEVELS OQ-W-1 note that toys show only the random collision rate.', HFD_T, 'a toy or real-field test shows a collision rate on trail pairs above random', ev=WORK + '/testE.json; research/poseidon/levels/LEVELS.md (OQ-W-1)', labels=('Z',))
rec(U, 'ALT.GKR', 'ALT', 'Q4', 'alternatives: GKR (sumcheck-based) as an attack', 'OPEN',
    'GKR is a verification protocol, not a collision finder; no attack route from it was found or built. Subspace-trail collision search is covered by Q3.', False,
    'No test.', HFA, 'a trail-based collision criterion with success above the random rate is found', prior=0.02, pot=1.0)

U = 'poseidon-r2-U59'
rec(U, 'ALT.BACKSKIP', 'ALT', 'Q2', 'necessity: why not skip rounds backwards', 'COMPUTED',
    f'The inverse S-box is x^e with e = 5^-1 mod (p-1) = (4(p-1)+1)/5 (checked), e/(p-1) = {A["e5inv_over_pm1"]}: a dense polynomial of degree about 0.8p. Backward the S-box is full-size, not degree 5, so there is no cheap backward skip; the forward degree 5^k grows slowly, which is why only forward skipping works.', True,
    'Exact exponent identity on Pallas, checked by me.', HFA, 'a backward family whose inverse S-box outputs stay affine in a parameter is exhibited', ev=WORK + '/testA.json; 3rd_openai_workspace/luna3/ANSWER.md (P3.12)', labels=('K',))
rec(U, 'ALT.BACKSKIP', 'ALT', 'Q3', 'degrees of freedom: backward output lines', 'COMPUTED',
    'P3.12 (Luna 3): backward output lines are affine after one inverse x^5; on toys q = 23/43 their two-sided intersections capture only a small fraction of collisions. Output lane fixed to y leaves 2 free lanes after the last MDS: a 2-parameter family, one inverse S-box layer deep.', False,
    'Cited from ANSWER.md; not rerun.', HFA, 'two backward layers stay low degree on a toy', ev='3rd_openai_workspace/luna3/ANSWER.md', labels=('N',))
rec(U, 'ALT.BACKSKIP', 'ALT', 'Q4', 'alternatives: meet-in-the-middle with one backward layer', 'OPEN',
    'One inverse layer is cheap per point (one exponentiation ~ 254 squarings) and the front reaches R4 after the free skip; but the join is the fibre of the digest (about p points) and finding a point on it is the original problem. See DOOR.t31.', False,
    'Not tested beyond the P3.12 toy.', HFA, 'a join condition with a low-degree description is found', prior=0.03, pot=1.0)

U = 'poseidon-r2-U60'
rec(U, 'ALT.ZEROSUM', 'ALT', 'Q1', 'zero-sum identity on the real r=2 line', 'COMPUTED',
    f'Verified: sum over a coset aH of F_j(W), |H| = 2^19 = 524,288 > 390,625, equals |H| F_j(0) exactly: j=0 {B["r2_n2^19"]["sum_minus_n_F0_is_zero"]} ({B["r2_n2^19"]["secs"]} s), j=1 {B["r2_n2^19_line1"]["sum_minus_n_F0_is_zero"]}. r=0 (|H| = 2^14 > 15,625) also true. Reproduces Luna 3 P3.14 at r=1.', True,
    'Direct evaluation of the line digest F_j at 524,288 points; reference validated first (pinned vectors 11/11, r=2 collision verified).', HFA + '; one coset parameter a', 'a coset sum that fails for degree < |H| - 1 (it cannot)', ev=WORK + '/testB.json; 3rd_openai_workspace/luna3/P3_14.md', labels=('P',), topic='poseidon-r2 zero-sum')
rec(U, 'ALT.ZEROSUM', 'ALT', 'Q2', 'necessity: subgroup size', 'COMPUTED',
    f'Control: |H| = 2^18 = 262,144 < 390,625 gives sum != |H| F(0) (confirmed: {not B["r2_n2^18_control"]["sum_minus_n_F0_is_zero"]}); r=0 with |H| = 2^13 < 15,625 also fails. The identity needs |H| > degree.', True,
    'Same code as Q1.', HFA, 'never (algebraic identity)', ev=WORK + '/testB.json', labels=('P',))
rec(U, 'ALT.ZEROSUM', 'ALT', 'Q3', 'degrees of freedom', 'COMPUTED',
    '2^254 coset parameters a, 3 lines j, subgroup orders 2^19 .. 2^32 (2-adicity of p-1 is 32). It is one linear relation on 524,288 outputs: no collision follows (P3.14: all 2,097,152 digests on an r=1 coset were distinct).', False,
    'Cited P3.14 plus own identity check.', HFA, 'a relation among outputs that forces two equal values', ev='3rd_openai_workspace/luna3/P3_14.md', labels=('P',))
rec(U, 'ALT.ZEROSUM', 'ALT', 'Q4', 'alternatives: pair the coset by x -> -x', 'COMPUTED',
    'On H (which contains -1) pair W with -W: F(W) - F(-W) is the odd part, and the zero-sum says nothing about individual odd-part zeros. This is the odd-part route we already use (collision W, -W around the centre).', False,
    'Structural remark.', HFA, 'never', labels=('K',))

U = 'poseidon-r2-U61'
rec(U, 'ALT.INTERP', 'ALT', 'Q2', 'necessity: interpolate the full bivariate polynomial', 'COMPUTED',
    f'Full plane degree 5^10 = 9,765,625 (tracker); a dense bivariate interpolation has up to C(9,765,627, 2) = {comb(9765627,2):.3e} monomials; the line needs 393,216 evaluations. LEVELS lists AB-support sizes (e.g. 4,887,501 monomials after R5 at r=2, 196,251 at R4). No bivariate route comes near the line.', True,
    'Degree tracker today (testA.json), support counts from LEVELS.md section 2.', HFA, 'a sparse support below 1e6 monomials after the last round', ev=WORK + '/testA.json; research/poseidon/levels/LEVELS.md', labels=('K',))
rec(U, 'ALT.INTERP', 'ALT', 'Q3', 'degrees of freedom: evaluation count of the line', 'COMPUTED',
    f'g has 195,313 coefficients; the build evaluates F(c+s_i) and F(c-s_i) at an NTT of size 196,608 = 3 x 2^16: 2 x 196,608 = 393,216 evaluations. Lower bound 2 x 195,313 = 390,626; the surplus is 2,590 evaluations = {2590*258:,} ops per centre = {sv(4*2590*258):.2e} bit.', True,
    'Reading of the build stage (pkg_stage_r2 note) plus arithmetic.', HFA, 'a non-power-of-two transform that removes the surplus is built (gain below 1e-6 bit)', labels=('Z',), ev=LO + 'pkg_stage_r2/submission-note.md')
rec(U, 'ALT.INTERP', 'ALT', 'Q4', 'alternatives: fewer evaluations of the digest', 'COMPUTED',
    f'The build charges 393,216 line evaluations = 101,449,728 ops per centre = {sv(4*evals):.5f} bit of the total, and both signs c +- s are needed for the odd part; the only saving is the 2,590-point surplus ({sv(4*2590*258):.2e} bit). Direct evaluation of F from the affine state (skipping the 2 free rounds) would charge fewer than 258 ops per point: bounded by the whole evaluation cost {sv(4*evals):.5f} bit. Negligible either way.', True,
    'Bound by removal.', HFA, 'never for the score', labels=('Z',))

U = 'poseidon-r2-U62'
rec(U, 'ALT.GROEBNER', 'ALT', 'Q2', 'necessity: Macaulay / resultant elimination of the round system', 'CLAIMED-UNTESTED',
    'P3.9 (Luna 3): m = 52 + 6r = 64 variables at r=2, q = 48 + 2r = 52 quintics + 4r = 8 linears; conditional degree of regularity d = 1 + 4q = 209; Macaulay matrix N = C(m+d, d) columns. Regularity of the system is unproved; the dense matrix is astronomically larger than the line route.', True,
    f'Cited formulas; I recomputed N = C(64+209, 209) = {comb(273,209):.3e} columns.', HFA, 'regularity is proved and the matrix is shown sparse enough', ev='3rd_openai_workspace/luna3/P3_9_lowmem.md', labels=('K',))
rec(U, 'ALT.GROEBNER', 'ALT', 'Q3', 'degrees of freedom of the elimination', 'COMPUTED',
    'After the two-free-round skip one variable remains; elimination of the tail variables is a composition of degree-5 polynomials, giving exactly the univariate F of degree 5^8. A resultant of F(a) - F(b) over (a - b) has degree 390,624 per variable: no cheaper than the odd-part gcd.', False,
    'Argument from the degree count; the 390,625 degree itself was confirmed in degree_r2.txt (fresh-point Horner check True for j = 0,1,2).', HFA, 'a resultant structure with low-degree factors', ev='research/poseidon/orchard/math/degree_r2.txt')
rec(U, 'ALT.GROEBNER', 'ALT', 'Q4', 'alternatives: weighted-order free basis', 'OPEN',
    'See ALT.FREELUNCH and ALT.CHEAPLUNCH: both reduce to the same univariate degree; no Groebner route has a lower degree than 5^8.', False,
    'No new test.', HFA, 'regularity measured at a toy size against 1 + 4q', prior=0.02, pot=1.0)

# ================================================================== U63-65 DOORS
HFD = 'r=2 target, 4 full + 2 partial + 4 full rounds, Pallas MDS and constants pinned; toy tests use random Cauchy MDS and random constants over F_103'
ROD = 'a door-specific test on the real field disagrees with the statement'
U = 'poseidon-r2-U63'
rec(U, 'DOOR.t31', 'DOOR', 'D1', 'meet in the middle at a level boundary, r=2', 'COMPUTED',
    'Front surface (inputs mapped to the state after R3, after R5 or at R60 entry) is 2-dimensional and injective (every round is a bijection of F^3, x^5 permutes F_p). The backward family from a digest y is a 2-parameter family (lane 0 = y). The join is the digest fibre: about p inputs per y (p^2 inputs / p values); any two points of it collide, but finding even one is the original problem. Nothing depends on r except one more partial round inside the front.', False,
    'Counting argument (exact); the door is closed by the T39 statement "no independent inputs". No new run.', HFD, 'a join test cheaper than one root-find on the line is found', ev='research/poseidon/levels/LEVELS.md (T31, T39, OQ-B-3)', labels=('Z',))
rec(U, 'DOOR.t32', 'DOOR', 'D1', 'alternative parametrisations and host curves, r=2', 'BEDROCK',
    'The three canonical lines (constant coordinate j of the round-1 S-box input) are complete for affine families (proved earlier); (A,B) coordinates done. Higher-degree curves: Cloud 46 claims degree rigidity for all polynomial state curves at the two-round cut; Luna 3 P3.19 reports the certificate checks (toy q = 1,000,003 and Pallas r=2 constants) match. Not checked by me beyond reading.', False,
    'Cited, not rerun by me.', HFD, 'a curve of degree > 1 with S-box outputs of degree < 5 per cut round is found', ev='3rd_openai_workspace/luna3/P3_19_verify_degree_rigidity.md; HANDOFF.md 10-12 21:05', labels=('K',))
U = 'poseidon-r2-U64'
rec(U, 'DOOR.t33', 'DOOR', 'D1', 'symmetries (i-symmetry, mu4 scaling, Frobenius twist of M), r=2', 'COMPUTED',
    f'p mod 4 = {A["p_mod_4"]} so i exists and S(ix) = i S(x); the symmetry needs all round constants zero: 0 of 30 constants in the r=2 schedule are zero, and the capacity 2^65 is not scaled: broken. Frobenius twist: Aut(F_p) is trivial, so the twist of M is M itself and gives nothing over the prime field.', True,
    'Zero-constant count by me on the pinned constants; Frobenius statement is field theory.', HFD, 'a field automorphism or a scaling that fixes constants and capacity is found', ev=WORK + '/testA.json; research/poseidon/levels/LEVELS.md (T33)', labels=('K',))
rec(U, 'DOOR.t34', 'DOOR', 'D1', 'forcing S-box inputs to chosen values by root-finding, r=2', 'COMPUTED',
    'Aimed hits at R1..R3 and equal lane 0 at R1..R4, R60, R61 by one univariate root-find are known (LEVELS T34). Forcing both partial-round S-box inputs to 0 ("freeze") means two conditions on a 2-dim input: degrees in the plane: lane 0 at P1 entry 625, at P2 entry 3125 (tracker), Bezout 625 x 3125 = %s = 5^9 points over the closure; solving costs a resultant of that size, worse than the line. Cloud 46: freeze impossible/rigid (CLAIMED, Luna 3 P3.19 checks it).' % f'{625*3125:,}', True,
    'Degrees from my tracker (plane, generic dense MDS); the freeze impossibility is not tested by me.', HFD, 'a freeze solution is found at toy size', ev=WORK + '/testA.json; research/poseidon/levels/LEVELS.md (T34)', labels=('K',))
U = 'poseidon-r2-U65'
rec(U, 'DOOR.t36', 'DOOR', 'D1', 'branch number / minimal active S-boxes in R60-R63, r=2', 'BEDROCK',
    f'Real MDS: all minors nonzero (9, 9, 1), branch number 4. Support chains over the four tail rounds: {A["tail"]["mds_ok"]} pass the MDS rule, {A["tail"]["with_lane0_zero_output"]} of 2401 end with lane 0 zero, {A["tail"]["weight_patterns"]} weight patterns; minimum total active S-box positions across the four rounds is {A["tail"]["min_total_active"]}. The tail is the same for every r, so the table is identical at r=1 and r=2. Reproduces LEVELS (337 / 25).', True,
    'Exact enumeration with the pinned MDS; supports realised for a large field by the MDS property (exact-support vectors exist when |A| + |B| >= 4).', HFD, 'a different MDS or round layout', ev=WORK + '/testA.json; research/poseidon/levels/LEVELS.md (J6, OQ-T-1)', labels=('N',))
bal = C['1']['R4']; bal2 = C['1']['R5']
rec(U, 'DOOR.t38', 'DOOR', 'D1', 'balance of the partial block on the real surface, r=2', 'LOCAL_ONLY',
    'Toy F_103, r=2, 3 seeds, all 10,609 inputs: restricting to the R3 surface (inputs sharing lane 0 after R3, 103 groups of 103) the number of distinct lane-0 values after R4 / R5 / final averages %s / %s / %s per group against the random expectation 65.29; globally the histogram of lane 0 after R4 has min-max 80-136 around mean 103 (seed 2), the width of a random map. No excess structure on the surface.' % (
        '/'.join(str(C[s]['R4']['surf_avg_distinct']) for s in ('1', '2', '3')), '/'.join(str(C[s]['R5']['surf_avg_distinct']) for s in ('1', '2', '3')), '/'.join(str(C[s]['final']['surf_avg_distinct']) for s in ('1', '2', '3'))), True,
    'Toy only (q = 103, random Cauchy MDS, random constants, seeds 1-3); the real-field balance is not testable by enumeration.', HFD + '; surface = fixed lane 0 after R3', 'a toy with a real-MDS-like determinant coincidence shows excess balance, or a real-field test', ev=WORK + '/testC.json; research/poseidon/levels/U12/', labels=('Z',))

# ------------------------------------------------------------------ write
os.makedirs(OUT, exist_ok=True)
seen = set()
cnt = 0
for unit, cell, r in records:
    assert cell not in seen, cell
    seen.add(cell)
    if r['status'] == 'KILLED':
        assert r['own_test']
    d = os.path.join(OUT, unit)
    os.makedirs(d, exist_ok=True)
    fn = cell.replace('|', '_') + '.json'
    json.dump(r, open(os.path.join(d, fn), 'w', encoding='utf8'), indent=1, ensure_ascii=False)
    cnt += 1
print('wrote', cnt, 'records', len(set(u for u, _, _ in records)), 'units')
