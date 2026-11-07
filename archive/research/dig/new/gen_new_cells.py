#!/usr/bin/env python3
"""gen_new_cells.py - generate the per-row question cells for the live Pareto rows that have no row-dig grid yet.

Writes (next to this file, NEVER into ../CELLS.jsonl): poseidon-generic.jsonl poseidon-algebraic.jsonl blake3.jsonl sha256.jsonl sha3.jsonl,
and ../GRID_<FAMILY>.md is written by gen_grid_md.py (same spec, imported).  Read only on: ../../FILINGS.md, ../../rivals/boards_*_pareto_live.json
(rival rows are read as DATA; nothing is run), ../CELLS.jsonl (for "existing cells of this hash" pointers).
Re-runnable.  Status rules follow ../SCHEMA.md: a cell is COMPUTED/KILLED/LOCAL_ONLY only where one of OUR files records the number;
everything else is OPEN.  Evidence paths are relative to the workspace.  Date of generation 2026-10-17.
"""
import json, os, re, collections, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIG = os.path.dirname(HERE)
WS = os.path.abspath(os.path.join(DIG, '..', '..'))
DATE = '2026-10-17'
SRC = 'main session: new-row dig generator (reads our files)'

# ------------------------------------------------------------------------------------------------ families
FAMS = collections.OrderedDict()
FAMS['poseidon-generic'] = dict(hash='poseidon', board='poseidon', rows=list(range(3, 57)), title='Poseidon generic collision rows (rho / route2d2 template)')
FAMS['poseidon-algebraic'] = dict(hash='poseidon', board='poseidon', rows=list(range(3, 22)), title='Poseidon algebraic rows (line restriction + powering + half-gcd)')
FAMS['blake3'] = dict(hash='blake3', board='blake3', rows=list(range(3, 8)), title='BLAKE3 Pareto rows (rolled and 5-byte compact lines)')
FAMS['sha256'] = dict(hash='sha256', board='sha256', rows=list(range(39, 65)), title='SHA-256 Pareto rows (rolled bit-sliced roll3/roll4, 5-byte u5 line)')
FAMS['sha3'] = dict(hash='sha3', board='sha3-256', rows=list(range(6, 25)), title='SHA3-256 Pareto rows (LS1 v3/v4 line and generic v3/v4b)')

# ------------------------------------------------------------------------------------------------ the question template
# (key, short name, generic question text with {R} {HASH}); family-specific Q13/Q14 added per family.
QCORE = [
    ('Q1', 'cost ledger', 'Cost ledger of the row {HASH} r{R}: where does every op go, term by term (per step / per trial / per batch, plus recovery, setup, preprocessing), and what is the exact total of the filed or best program? Give shares in percent and bit value of one op.'),
    ('Q2', 'dispatch and control charge', 'Which control ops does r{R} charge (loop counter, branch, DP/filter test, handlers, dispatch, loads/stores, register moves) and is each charged at best-case exact count, per the organizer cost model as written?'),
    ('Q3', 'memory peak and drain', 'What is the peak-memory phase of r{R} (which stage, which buffers live), what is the measured or modelled peak in bytes, and do drain / stream / alias / free-early options lower the peak that binds (peak = max over stages, so all binding stages must drop)?'),
    ('Q4', 'table / entry packing', 'How is the table, entry or code packed on r{R} (bits per entry, entries, bytes per instruction, code bytes versus table slots), and what does a different packing change in the ledger?'),
    ('Q5', 'success-bound slack', 'How far is the proven success probability of r{R} above the required premise, and what time bit does the slack cost (which proof terms F1.. and which are looser than needed)?'),
    ('Q6', 'premise and evidence', 'What premise (H-statements, probability model, statistic) does r{R} rest on, what organizer-executed evidence supports it, and what would a judge need to see that is missing?'),
    ('Q7', 'preprocessing / advice', 'What preprocessing, advice or nonuniform data does r{R} use, how is it charged (time, memory, advice size), and is any of it free or hidden?'),
    ('Q8', 'rival best on this row', 'Who holds the best rival entry on r{R} on the board, at what score, and where does it save against us (ledger term by term, convention, premise)? If no rival is on the row, record the empty square.'),
    ('Q9', 'levers applied vs unapplied', 'Which levers are applied in our r{R} entry, and which recorded levers (LEVERS.md, levers_1016/*/RESULT.md) are not applied, each with its measured gain in bits and what a refile needs?'),
    ('Q10', 'judge findings and status', 'What have the organizer judges said about r{R} entries (ruling, fatal or material findings, status on the board), and which fix is the one the ruling names?'),
    ('Q11', 'transfer from neighbouring rows', 'Which finding or lever measured on a neighbouring row (r{R_minus}, r{R_plus}) transfers to r{R} unchanged, which needs re-measurement, and which does not transfer?'),
    ('Q12', 'structurally special at this round count', 'Is anything structurally special at r{R} (a boundary round count, a changed free-round budget, a regime change between straight and rolled, a changed C(r) unit, a rule edge)?'),
]
QFAM = {
    'poseidon-generic': [
        ('Q13', 'step program: partial-round / hidden-basis cut', 'Step program of r{R} (140+12r field ops in the filed route): how many ops does the partial-round body, the entry/exit of the partial form and the four full-round layers cost, and which basis / form choice lowers it (hidden-basis cut -4 ops, fixed function, monomial forms)?'),
        ('Q14', 'DP test, gap budget and recovery', 'Distinguished-point test cost (AND+compare+branch vs compare+branch), gap-law (geometric) budget 3*gmax versus a sum tail, and the recovery share of the ledger at r{R}.'),
    ],
    'poseidon-algebraic': [
        ('Q13', 'powering / half-gcd / NTT stage costs', 'For r{R}: degree m = (5^(6+r)-1)/2 odd part, NTT plan (2^a or 3*2^a), cost of the Euler-exponent powering (squarings, Barrett reductions) and of the half-gcd / root-certificate stage, as shares of the trial.'),
        ('Q14', 'line restriction, centres and trial count', 'Line restriction at r{R}: free rounds spent, centre choice and number of trials K charged (centre-1 vs anchored centre), per-trial success probability bound and its premise (plane / complete-intersection genus bound), and the cross-over against the generic row.'),
    ],
    'blake3': [
        ('Q13', 'gate count: adders, XOR, rotations', 'Gate count of the r{R} step (ripple adders at 5 gates/bit, XOR, free rotations in bit-sliced form, digest XOR), the gate mix, and the value in bits of one gate / one adder.'),
        ('Q14', 'first-collision / cut lemma and trail table', 'Cut lemma / first-collision route (B reduction), trail table and entry size, kappa tail, and the 5-byte compact instruction line at r{R}: what each is worth and what is unproven.'),
    ],
    'sha256': [
        ('Q13', 'step and schedule gates (Ch, Maj, adds, K)', 'Gate anatomy of the r{R} kernel: schedule words (sigma0/1, adds), compression step (6 FA rows, Sigma, Ch, Maj), folded-constant steps, T stores; straight versus loop share.'),
        ('Q14', 'rolled vs unrolled / instruction width', 'Rolled kernel (roll3/roll4) versus unrolled straight line and the 5-byte u5 instruction: loads/stores/control records versus code bytes versus table slots at r{R}; which is the cheaper regime.'),
    ],
    'sha3': [
        ('Q13', 'polarity / lane complementing and NOT count', 'Chi polarity handling at r{R}: NOTs per round versus the 320 floor (one NOT per chi row), mixed-polarity terms, message-constant (K) choice for uniform polarity.'),
        ('Q14', 'linear-structure line (LS1) vs generic bit-sliced', 'Which line applies at r{R} (LS1 v3/v4 linear-structure step with 5-byte instructions, or generic v3/v4b bit-sliced 256-lane): ops per evaluation, replay / DP / hit-budget shares, and the F1..F6 failure terms.'),
    ],
}

# ------------------------------------------------------------------------------------------------ data from our files
def read(p):
    try:
        return open(os.path.join(WS, p), encoding='utf-8', errors='replace').read()
    except OSError:
        return ''

# ---- our filings (FILINGS.md), keep the last line per submission id, attribute rows by label
FIL = collections.OrderedDict()
for ln in read('research/FILINGS.md').splitlines():
    if not ln.startswith('|'):
        continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    if len(c) < 5 or not re.match(r'\d{4}-', c[0]) or c[2] in ('none', 'note'):
        continue
    FIL.setdefault(c[2], []).append(dict(when=c[0], label=c[1], tl=c[3], res=c[4]))


def classify(label):
    """label -> (family, row, line) or None"""
    L = label.replace(' ', '').upper()
    m = re.match(r'POSGEN\w*?_R(\d+)', L)
    if m:
        return ('poseidon-generic', int(m.group(1)))
    m = re.match(r'POSR(\d+)ALG', L)
    if m:
        return ('poseidon-algebraic', int(m.group(1)))
    m = re.match(r'POSR(\d)[A-Z]$', L)
    if m:
        return ('poseidon-algebraic', int(m.group(1)))
    m = re.match(r'R5N\d?$', L)
    if m:
        return ('poseidon-algebraic', 5)
    m = re.match(r'B3R(\d)', L)
    if m:
        return ('blake3', int(m.group(1)))
    m = re.match(r'S256U5_?R(\d+)', L) or re.match(r'S256R(\d+)', L)
    if m:
        return ('sha256', int(m.group(1)))
    m = re.match(r'(?:SHA3GENV\d\w?|SHA3)_?R(\d+)', L)
    if m:
        return ('sha3', int(m.group(1)))
    m = re.match(r'SHA3R(\d+)', L)
    if m:
        return ('sha3', int(m.group(1)))
    m = re.match(r'LS1V\dR(\d+)', L) or re.match(r'LS1R(\d+)', L)
    if m:
        return ('sha3', int(m.group(1)))
    return None


MY = collections.defaultdict(lambda: collections.defaultdict(list))   # fam -> row -> [(id,label,score,res)]
for sid, lst in FIL.items():
    last = lst[-1]
    best_res = ''
    for e in lst:
        if e['res'] and not e['res'].startswith('validating'):
            best_res = e['res']
    k = classify(lst[0]['label'])
    if k:
        MY[k[0]][k[1]].append(dict(id=sid, label=lst[0]['label'], tl=lst[-1]['tl'], res=best_res or lst[-1]['res'], when=lst[0]['when']))

# ---- the board (rival rows as DATA)
BOARD = {}
for fam in ('poseidon', 'sha3-256', 'blake3', 'sha256'):
    BOARD[fam] = {}
    try:
        d = json.load(open(os.path.join(WS, 'research', 'rivals', 'boards_%s-pareto_live.json' % fam), encoding='utf-8'))
    except Exception:
        continue
    BOARD[fam]['_n'] = len(d['submissions'])
    for x in d['submissions']:
        om = x['officialMetrics'] if isinstance(x.get('officialMetrics'), dict) else {}
        j = x['judgment'] if isinstance(x.get('judgment'), dict) else {}
        rounds = om.get('rounds')
        score = None
        if isinstance(j.get('scores'), list) and len(j['scores']) == 2:
            rounds = rounds or j['scores'][0]
            score = j['scores'][1]
        BOARD[fam].setdefault('_by_id', {})[x['id'][:8]] = dict(user=x['solverUsername'], status=x['status'], valid=j.get('valid'), reason=(j.get('reason') or '')[:200],
                                                                 rounds=rounds, score=score, review=om.get('reviewStatus'), mem=om.get('memoryLog2Bytes'), t=om.get('timeLog2'))
        if rounds is not None and score is not None and j.get('valid'):
            BOARD[fam].setdefault(rounds, []).append(dict(id=x['id'][:8], user=x['solverUsername'], status=x['status'], score=score, t=om.get('timeLog2'),
                                                          mem=om.get('memoryLog2Bytes'), review=om.get('reviewStatus')))

OURS = 'Jbenisek'


def rival_line(famkey, row, algebraic=None):
    fam = FAMS[famkey]['board']
    lst = BOARD.get(fam, {}).get(row, [])
    if famkey == 'poseidon-generic':
        lst = [e for e in lst if e['score'] >= 100]
    if famkey == 'poseidon-algebraic':
        lst = [e for e in lst if e['score'] < 100]
    ours = sorted([e for e in lst if e['user'] == OURS], key=lambda e: e['score'])
    riv = sorted([e for e in lst if e['user'] != OURS], key=lambda e: e['score'])
    return ours, riv


# ---- existing cells per hash (pointers only)
EXIST = collections.defaultdict(list)
try:
    for ln in open(os.path.join(DIG, 'CELLS.jsonl'), encoding='utf-8'):
        if ln.strip():
            r = json.loads(ln)
            EXIST[r['hash']].append(r['id'])
except OSError:
    pass


def exist_note(hash_, row):
    h = '%s-r%d' % (hash_, row)
    ids = EXIST.get(h, [])
    if not ids:
        return 'No cell of this row exists in CELLS.jsonl under hash %s (no earlier grid).' % h
    return 'CELLS.jsonl already holds %d cells under hash %s (e.g. %s); this PR-cell does not replace them.' % (len(ids), h, ', '.join(ids[:3]))


# ------------------------------------------------------------------------------------------------ pre-fill facts (ours)
# every entry: (status, number, evidence, notes, lever_gain or None, labels)
def A(status, number, evidence, notes='', gain=None, labels=None, own=True, held=None, reopen=None):
    return dict(status=status, number=number, evidence=evidence, notes=notes, gain=gain, labels=labels or ['N'], own=own, held=held, reopen=reopen)


PRE = collections.defaultdict(dict)     # (famkey, row) -> {Qn: A(...)}


def put(fam, rows, q, a):
    for r in rows:
        PRE[(fam, r)][q] = a


R = lambda a, b: list(range(a, b + 1))

# ============================ POSEIDON GENERIC (rows 7..56 built by the factory; 3..6 not built) ============================
DPG = 'research/levers_1016/dig_posgen/RESULT.md'
# Q1 structural: step ops 140+12r for every row 7..56 (allrows.py), exact split only at r7/r23/r56
put('poseidon-generic', R(7, 56), 'Q1', A('COMPUTED',
    'step ops = 140 + 12r field ops (ADD+MUL) for the filed route2c/2d2 template on every row r7..r56 (allrows.py base reproduces it with KAT true); score = S*(N+3.75), S = 1.393*2^127; table scan / insertion / constants / setup are ~1e-31 of the total, preprocessing ~1e-29; trail share 99.76-99.79 %, recovery 3*gmax 0.21-0.24 %',
    DPG + ' (section 1); research/levers_1016/dig_posgen/w/allrows.py',
    'Exact op split measured at r7 (224 = 87 ADD + 137 MUL, C 363), r23 (416 = 167+249, C 699), r56 (812 = 332+480, C 1392); other rows by the 140+12r law. 140 = 3 (round-2 inputs) + 9 + 15 + 9 + 12 + 7 + 72 + 9 + 4. One op per step is worth log2(1-1/(N+3.75)): r7 0.00634, r23 0.00344, r56 0.00177 bit.',
    labels=['D'], held='factory route2c code, tune.py recomputed, no package build'))
for r, (ops, a, m, c, tl) in {7: (224, 87, 137, 363, '126.80890'), 23: (416, 167, 249, 699, '126.74586'), 56: (812, 332, 480, 1392, '126.71116')}.items():
    PRE[('poseidon-generic', r)]['Q1'] = A('COMPUTED', 'r%d step %d ops (%d ADD + %d MUL), C = %d, time_log2 %s (reproduces the filed number)' % (r, ops, a, m, c, tl),
                                            DPG + ' (section 1)', 'Exact; loop adds 3 ops per step + 3 per 4-step block (N + 3.75).', labels=['D'], held='factory route2c code')
# Q2 control
put('poseidon-generic', R(7, 56), 'Q2', A('COMPUTED',
    'control per step: AND-with-mask + compare + branch = 3 ops, plus block (add, compare, branch) = 3 per 4 steps = 0.75 per step (N+3.75); a compare-only DP test x<T saves 1 op/step (r7 -0.00634, r23 -0.00343, r56 -0.00177 bit); block as add+branch -0.25 op (rule-dependent)',
    DPG + ' (sections 1-2, cuts 2, 3, 3b)', 'Delta computed on the factory ledger only; the compare-only DP needs a table/DP text change and a re-measure of the gap law with top-bit DPs.', gain=0.00634, labels=['E'], held='step program unchanged'))
# Q3 memory
put('poseidon-generic', [7, 23, 56], 'Q3', A('COMPUTED',
    'memory stays at 2^20 (table + code + registers); memsens.py: even unlimited memory with the 16-bit side field gives only -0.0018 (r7) / -0.0021 (r23) / -0.0026 (r56) bit; memory over 2^20 costs log2(mem/2^20) so the lever is closed',
    DPG + ' (section 2 cut 6; w/memsens.py)', 'Peak phase is the table plus code; no multi-stage peak as in the algebraic rows.', labels=['Z'], held='16-bit side field, 36 B instructions'))
# Q4 packing
put('poseidon-generic', [7, 23, 56], 'Q4', A('COMPUTED',
    'entry word = ((x>>16)<<128) | index (126+128 bits) + 16-bit side field; larger MCAP at +25 % entries gives -0.001 (r7/r23) / -0.0013 (r56); unroll U=6..8 vs 4: -0.0023 (r7, U=8), -0.0010 (r23), ~0 (r56; U=8,16 lose to code size)',
    DPG + ' (section 2 cuts 3, 6; section 3.2)', 'Code bytes are 36 B per instruction; step 224..812 ops means code size eats table slots as r grows.', labels=['Z']))
# Q5 slack
put('poseidon-generic', [7, 23, 56], 'Q5', A('COMPUTED',
    'filed n = 1.393*n0 = 0.4846 bit above the 0.39 premise (random-function bound 0.62); that margin is the largest single number on these rows but it is the promotion-first margin, not a per-step cut; recovery budget 3*gmax vs sum tail: GUESS about -0.001 bit',
    DPG + ' (section 2, budget slack row and cut 5)', 'Cut 5 is a GUESS (needs a sum-tail proof sentence).', gain=0.4846, labels=['E']))
# Q6 premise: H1 random coin rho0
put('poseidon-generic', R(7, 56), 'Q6', A('COMPUTED',
    'premise H1 = average over the random constant rho0 (function randomised by one ADD); fixing e_0=0 would drop one ADD (-0.00635 at r7) but removes the coin of H1 (premise change, judge risk); gap law: DP gaps geometric (measured with low-bit DPs, proof Section 8)',
    DPG + ' (cut 4, section 3.2)', 'The judges refused route2 r9 on H2-finite-preprocessing and route2b r9 on H1 (10-bit walk): see Q10 of rows 9 and 23.', labels=['P'], held='H1 as filed'))
# Q7 prep
put('poseidon-generic', R(7, 56), 'Q7', A('COMPUTED',
    'preprocessing ~1e-29 of the ledger and other_fixed (table scan, insertion, bisection, constant loads, message roots, setup) ~1e-31; irrelevant at every measured row',
    DPG + ' (section 1)', 'Measured r7/r23/r56 only; the route2 r9 ruling on finite preprocessing (H2) is about the statement, not the size.', labels=['Z'], held='r7, r23, r56 measured; others by template'))
# Q9 levers
put('poseidon-generic', R(7, 56), 'Q9', A('LOCAL_ONLY',
    'levers recorded, NOT applied in the filed ROUTE2D2 rows: hidden-basis -4 ops/step (KAT passed on every r 7..56): r7 -0.02557 / r23 -0.01382 / r56 -0.00710 bit; compare-only DP -0.00634/-0.00343/-0.00177; U=6..8 unroll -0.0023/-0.0010/~0; stack 1+2+3 -0.03355/-0.01799/-0.00892 (with fixed function -0.04005/-0.02148/-0.01070)',
    DPG + ' (section 2); research/levers_1016/posledger/RESULT.md', 'Delta measured only at r7, r23, r56; the other rows are covered by KAT but their delta is not recorded (it scales with 1/(N+3.75)). Refile needs build_step edit in work/rho_body.py, proof_head/sec5 text, selftest len(STEP)==136+12*PARTIAL, gen_row.py rerun, stage_row.sh per row.',
    gain=0.02557, labels=['E'], held='factory tune.py rerun, not a staged package', reopen='a judge ruling that the basis choice changes the premise'))
for r, g in {7: 0.02557, 23: 0.01382, 56: 0.00710}.items():
    PRE[('poseidon-generic', r)]['Q9'] = A('COMPUTED', 'hidden-basis -4 ops/step: %+.5f bit; compare-only DP %+.5f; stack 1+2+3 %s' % (-g, -{7: .00634, 23: .00343, 56: .00177}[r], {7: '-0.03355', 23: '-0.01799', 56: '-0.00892'}[r]),
                                           DPG + ' (section 2)', 'Not applied in the filed entries; KAT passed on this row.', gain=g, labels=['E'], held='factory ledger + tune.py rerun')
# Q13 hidden basis structure
put('poseidon-generic', R(7, 56), 'Q13', A('COMPUTED',
    'partial round = 12 ops (3 + 4M + 5A); four full-round layers 6M+6A+3 each; entry to partial form 12, exit 7 (hidden-basis variants: entry 8 or exit 3, saving exactly 4 ops because each direction serves one end); round-2 as monomials of x costs 31 vs 27 (worse); closed: full-round linear layers, partial-round form (9 coefficients, 5 gauge params), third free round via line',
    DPG + ' (sections 3.1, 4)', 'Closures are DERIVED (not exhaustively searched by program) for the layers and partial round: EMPTY SQUARES, derived.', labels=['Z']))
put('poseidon-generic', R(7, 56), 'Q14', A('COMPUTED',
    'DP test 3 ops (AND, compare, branch) vs 2 (compare, branch with DP={x<T}, T about 2^141.2): saves 1 op/step; recovery 3*gmax = 0.21-0.24 % of the ledger; handler/scan 1e-31',
    DPG + ' (sections 1, 3.2)', 'Top-bit DP gap-law needs a cheap re-measure.', labels=['E']))
# Q12 specials
put('poseidon-generic', [3, 4, 5, 6], 'Q12', A('COMPUTED',
    'the factory generic route builds r>=7 only (partial-round program of 140+12r ops); at r3..r6 the algebraic line scores 38.6 / 42.9 / 47.1 / 52.8 against generic 126.7-127.0, so no generic row has been built or filed',
    'research/levers_1016/posledger/RESULT.md; research/levers_1016/dig_posgen/RESULT.md; research/dig/CELLS.jsonl GW1015-POS-CROSSOVER',
    'Empty square by decision, not by test: a generic r3..r6 row is dominated by 80+ bits.', labels=['0']))
put('poseidon-generic', [7], 'Q12', A('COMPUTED', 'r7 is the first built generic row; also the algebraic r7 line (58.07) beats it by 68.9 bits', 'research/levers_1016/pos_far_rows/RESULT.md; ' + DPG, 'Rows of the generic line are all dominated by the algebraic line through r21.', labels=['0']))
put('poseidon-generic', [56], 'Q12', A('COMPUTED', 'r56 is the last built generic row (step 812 ops, C 1392); full-round count fixed at 8 (rounds 0..3 and 60..63), 56 partial rounds', DPG, 'Filed POSGEN_ROUTE2_R56 56fb07fc.', labels=['0']))
# round-specific specials from rulings are in Q10 (auto)

# ============================ POSEIDON ALGEBRAIC (r3..r21) ============================
PL = 'research/levers_1016/posledger/RESULT.md'
PMC = 'research/levers_1016/pos_memcut/RESULT.md'
PFR = 'research/levers_1016/pos_far_rows/RESULT.md'
PAR = 'research/levers_1016/pos_alg_rows/RESULT.md'
base_scores = {3: 38.58536, 4: 42.87211, 5: 47.12610, 6: 52.81457, 7: 57.07357, 8: 61.35502}
for r, s in base_scores.items():
    put('poseidon-algebraic', [r], 'Q1', A('COMPUTED', 'ledger.py row (K=1, every trial dG=0) score %.5f for r%d (K=2 doubles the time term by 1 bit: r7 58.07357, r8 62.35501)' % (s, r), PL + ' (baseline line); research/poseidon/algebraic_paper/ledger.py',
                                           'Reproduced exactly by levers.py on a scratch copy of ledger.py. Filed lines: see Q10.', labels=['D'], held='ledger.py conventions, arena factor 1.177'))
put('poseidon-algebraic', R(9, 21), 'Q1', A('LOCAL_ONLY', 'modelled only (Grok 129 abstract model, our /36 and /8 unit mapping, K=2): MID score r9 66.96, r10 72.41, r11 76.73, r12 81.04, r13 86.49, r14 90.80, r15 95.51, r16 101.20, r17 105.50, r18 109.81, r19 115.33, r20 119.81, r21 124.11 (LOW/HIGH in the file)',
                                          PFR, 'Not a C program: no model-never-below-measured guarantee; HIGH multiplier 3.33 is a one-point calibration. Row-specific MID values are in the table of pos_far_rows.', labels=['E'], own=True, held='Grok 129 model.py counts, one-point overhead calibration'))
# per-row far table values
FAR = {9: (64.01, 66.96, 68.69), 10: (69.42, 72.41, 74.15), 11: (73.74, 76.73, 78.46), 12: (78.08, 81.04, 82.78), 13: (83.48, 86.49, 88.22), 14: (87.80, 90.80, 92.53),
       15: (92.51, 95.51, 97.24), 16: (98.16, 101.20, 102.93), 17: (102.47, 105.50, 107.24), 18: (106.78, 109.81, 111.54), 19: (112.28, 115.33, 117.06), 20: (116.78, 119.81, 121.55), 21: (121.08, 124.11, 125.85)}
for r, (lo, mid, hi) in FAR.items():
    PRE[('poseidon-algebraic', r)]['Q1'] = A('LOCAL_ONLY', 'modelled score r%d: LOW %.2f / MID %.2f / HIGH %.2f (K=2); generic 127.009 => margin %.1f / %.1f / %.1f' % (r, lo, mid, hi, 127.009 - lo, 127.009 - mid, 127.009 - hi),
                                              PFR, 'Model rows, not a ledger program; r21 margin 5.9/2.9/1.2 survives about 1 bit; r22 loses under MID/HIGH.', labels=['E'], held='Grok 129 abstract model + our unit mapping')
put('poseidon-algebraic', [21], 'Q12', A('COMPUTED', 'r21 is the last row where algebraic beats generic in all three mappings (margin 5.9 / 2.9 / 1.2); at r22 it wins only under LOW (+0.4) and loses under MID (-2.6) and HIGH (-4.3); memory at r21 about 2^70 bytes (paper value)', PFR,
                                         'Half-gcd (about 25 % of the r22 trial) is a recurrence upper shape; a cheaper real one could move the r22 verdict by tenths of a bit.', labels=['E']))
put('poseidon-algebraic', R(9, 20), 'Q12', A('LOCAL_ONLY', 'score exceeds about 100 from r16 on: rows r16..r21 matter only as paper values; margin over generic 127.009 (MID): r9 60.0, r10 54.6, r11 50.3, r12 46.0, r13 40.5, r14 36.2, r15 31.5, r16 25.8, r17 21.5, r18 17.2, r19 11.7, r20 7.2, r21 2.9', PFR, 'Modelled margins.', labels=['E']))
# memory Q3
MC = {3: ('244,745,344', '244,745,792', 38.58501), 4: ('1,072,730,176', '1,072,730,560', 42.87204), 5: ('4,759,669,504', '4,759,669,952', 47.12608), 6: ('31,046,103,232', '31,046,103,616', 52.81456)}
for r, (c, d, s) in MC.items():
    put('poseidon-algebraic', [r], 'Q3', A('COMPUTED', 'stage C peak %s B, stage D peak %s B (D binds, 448 B apart); removing tmp (and F) from stage C does NOT lower the program peak; score %.5f unchanged' % (c, d, s), PMC + ' (table)',
                                           'Measured heap_peak at r3 and r5; model reproduces both. Any memory lever must lower C AND D (apply_inv allocates c_, d_ while g and F are live).', labels=['Z'], held='ledger.py allocation model; r3/r5 executed logs'))
    put('poseidon-algebraic', [r], 'Q9', A('COMPUTED', 'ledger levers r%d: two-level twiddle (memory only) %s, +1 op/load %s; (b1) one N buffer fewer in C only 0 (D binds); (d) cached spectra worse (+%s); ideal (b3) both C and D minus N: %s (GUESS)' % (
        r, {3: '-0.100', 4: '-0.092', 5: '-0.083', 6: '-0.104'}[r], {3: '-0.028', 4: '-0.023', 5: '-0.021', 6: '-0.037'}[r], {3: '0.374', 4: '0.351', 5: '0.332', 6: '0.428'}[r], {3: '-0.747', 4: '-0.675', 5: '-0.595', 6: '-0.774'}[r]),
        PL, 'Honest 3-op two-level lookup loses 0.08-0.11; only a hoisted combine reaches -0.03..-0.06. D buffer composition verified at r3 only.', gain=0.028, labels=['E'], held='ledger arithmetic, nothing run on the C code'))
for r in (7, 8):
    put('poseidon-algebraic', [r], 'Q9', A('COMPUTED', 'ledger levers r%d: twiddle memory-only %s, +1 op/load %s; cached spectra +%s (worse); b3 ideal %s (GUESS)' % (r, {7: '-0.094', 8: '-0.085'}[r], {7: '-0.032', 8: '-0.029'}[r], {7: '0.400', 8: '0.373'}[r], {7: '-0.687', 8: '-0.604'}[r]), PL, 'D composition above r3 unverified.', gain=0.032, labels=['E']))
# Q5/Q14 success
put('poseidon-algebraic', [7], 'Q5', A('COMPUTED', 'filed r7 success 0.43348 (plane genus bound, Appendix D) at K=2 trials; time 40.85457, mem 37.219, score 58.07357', PAR + ' (section 1)', 'Algebraic r7 filed as POSR7ALG* (05a41d88 family).', labels=['P']))
put('poseidon-algebraic', [8], 'Q5', A('COMPUTED', 'r8 staged (not filed): success >= 0.434736614 (premise H_ci(w=2) of Grok 134: e1<1.095e-19, e2<6.682e-10, CS 0.2499999998, Markov tail 0.0018382353, q=0.24816), time 42.98801, memory 39.367 (708,802,245,068 B), score 62.35501', PAR + ' (section 1)', 'Algebraic beats best r8 generic by about 83 bits; slot pos_posalg_r8b is file-ready, submit script NOT run.', labels=['P']))
put('poseidon-algebraic', [8], 'Q14', A('COMPUTED', 'r8 line j=0, 150 antipodal pairs, widths 6/8/10/12; intake counts lowbits 256, line-ladder 231/117/39/8 of 256 vs predicted 232/114/35/9; generator gen_row.py computes everything for R in 3..11 (refuses outside)', PAR + ' (sections 2-3)', 'Experiments passed organizer intake; the ruling for r7 (POSR7ALG8D) was lane_experiments only.', labels=['P']))
put('poseidon-algebraic', R(3, 11), 'Q13', A('LOCAL_ONLY', 'stage costs are in ledger.py (stages A..I: NTT plan 2^a or 3*2^a, Barrett squarings for S^((p-1)/2) mod g, half-gcd); half-gcd about 25 % of the r22 trial in the Grok model; CACHED_POW worsens (+0.33..0.43 bit r3..r8)', 'research/poseidon/algebraic_paper/ledger.py; ' + PL + '; ' + PFR, 'Per-row stage shares are not tabulated in one file.', labels=['D']))
# memory Q3 r7..r8 : peak
put('poseidon-algebraic', [7], 'Q3', A('COMPUTED', 'r7 peak about 136 GB (2^37.219 B); twiddle table 8.59 GB = 6.3 % of the peak; C and D tie within 448 B by design', PL + ' (notes (a))', 'Single-row figure from the ledger.', labels=['Z']))
put('poseidon-algebraic', [8], 'Q3', A('COMPUTED', 'r8 memory 39.367 log2 (708,802,245,068 B); same C/D tie structure', PAR, 'From the staged package cost model.', labels=['D']))
put('poseidon-algebraic', R(9, 21), 'Q3', A('LOCAL_ONLY', 'modelled memory (MID, log2 bytes): r9 41.88, r10 44.27, r11 46.56, r12 48.85, r13 51.24, r14 53.53, r15 55.94, r16 58.39, r17 60.64, r18 62.91, r19 65.36, r20 67.70, r21 69.97', PFR, 'Elements*32 B*1.177 arena, abstract model.', labels=['E']))

# ============================ BLAKE3 ============================
B = 'research/levers_1016/dig_b3r4r7/RESULT.md'
B3 = 'research/levers_1016/dig_b3r3/RESULT.md'
put('blake3', [3], 'Q1', A('COMPUTED', '17,238 gates per step (reachable, matches the filed 595-op SWAR / 17,238 gate circuit): adders 14,678 (85.1 %), XOR d^a,b^c 2,304 (13.4 %), digest XOR 256 (1.5 %); round 0/1/2 = 2,614 / 7,184 / 7,184 (round 0 small because the column G calls fold to constants); whole loop body 17,275; main loop 99.08 % of N, recovery 0.92 %; 1 gate = 0.000084 bit',
                          B3 + ' (section 1)', 'Front 124.8123 (B3R3PV), v2 124.83986. r3 is at its floor: every remaining lever is below 0.02 bit.', labels=['D'], held='filed circuit, zero prefix 0^32, m8..m15 free'))
put('blake3', [3], 'Q9', A('COMPUTED', 'levers: shorter instruction encoding 36 -> 20 B with re-planned Tp: -0.0173 (<= -0.03 plausible, needs a judge-accepted encoding rule; 5 B was a rival text); probability margin <0.001 closed; unroll 16->64 <0.0003 closed; fewer ripple adders: 0.0129 bit per adder, EMPTY',
                          B3 + ' (ranked levers)', 'Planner is not an optimiser: scan Tp/kappa per tmax before claiming.', gain=0.0173, labels=['E']))
put('blake3', [3], 'Q13', A('BEDROCK', 'full adder cannot go below 5 gates over {AND,OR,XOR,NOT} (Red\'kin bound); the filed pivot adder attains 5; carry-save for a+b+x = 10 gates/bit same as two adders; rotations are free renamings in bit-sliced form; message placement m8..m15 is rank 0 of 12,870', B3 + ' (r3 empty squares)', 'SWAR forms: 7 lanes x 36 bits = 595 ops = 85/instance; a 4-op rotation needs pitch >= 64.', labels=['Z', '0']))
put('blake3', [3], 'Q4', A('COMPUTED', 'instruction bytes 36 -> 20 gives 124.83985 -> 124.82258 (table 12,494 -> 24,708 entries, recovery 0.92 -> 0.46 %); 10/5 B and bigger memory give worse numbers because plan() is not an optimiser', B3 + ' (section 1)', 'Peak memory of these planner runs is a Python tracer estimate (~150 MB), not the program.', gain=0.0173, labels=['E']))
put('blake3', [4], 'Q1', A('COMPUTED', 'r4d straight: 24,422 ops/step, main loop 95.05 % of N, recovery 4.95 %; code 954,072 B (26,502 instr: body 24,459 = 84.0 % of memory, handlers 1,000, recovery circuit 836+47, setup 160), regs 25,600 B, counters 16,384 B, table 52,450 B (5,245 entries x 10 B) = 5.0 %; memory 1,048,506 B; score 125.060',
                          B + ' (sections 0-1)', 'r4 is straight and fits 2^20 so pays no memory term.', labels=['D'], held='bsrho.py --ledger of the filed v2 program'))
put('blake3', [5], 'Q1', A('COMPUTED', 'r5b straight: 31,606 ops/step, main loop 97.5 %, recovery 2.5 %; code 1,221,192 B; table 100,000 B; memory 1,363,176 B = 2^20.3785 (memory term +0.37854); scalar score 125.388', B + ' (section 1)', 'Straight program exceeds 2^20, so it pays a memory term; rolled r5c 125.19806 filed.', labels=['D']))
put('blake3', [6], 'Q1', A('COMPUTED', 'r6b straight: 38,790 ops/step, main loop 97.7 %, recovery 2.3 %; code 1,488,276 B; table 105,000 B; memory 1,635,260 B = 2^20.6411 (memory term +0.64109); scalar score 125.680', B + ' (section 1)', 'Rolled r6c 125.25234 filed.', labels=['D']))
put('blake3', [7], 'Q1', A('COMPUTED', 'r7c rolled: 55,210 ops/step (rounds 1-2 straight 9,798 = 17.7 %; 5 generic rounds 42,080 = 76.2 %, 87.8 % of each round is the 48 ripple adders at 154 gates; message-permutation moves 2,304 = 4.2 %; slot setup 512 + polarity complements 240 = 1.4 %; digest XOR 256 = 0.5 %; loop control 20 ops = 0.0005 bit); main loop 98.7 %, recovery 1.26 %; code 812,844 B; table 159,890 B (15,989 entries) = 15.2 %; memory 1,048,510 B; score 125.2911',
                          B + ' (section 1)', 'Waste of the generic round versus a straight one: 8 zero-word adds = 6,160 ops (11.2 % = 0.16 bit); unrolling to fold them costs 259-303 KB per round and loses (walk_a item 13: +0.031 worse).', labels=['D']))
put('blake3', [4], 'Q9', A('COMPUTED', 'cut lemma first-collision route -0.0535 (r4d B 1.4578e36 -> 1.4020e36, P_lower 0.39002; r4d has the most slack: filed B gives 0.4153 under the lemma); 7-byte entry kappa 14: -0.0683; rolled recovery circuit (836 -> ~280-300 instr) listed', B + ' (ranked cuts 2-4)', 'Cut lemma needs Lemma 2 Steps 2-6 rewritten as first-collision proof and an independent read (author-only check so far). Stacks with roll.', gain=0.0683, labels=['E']))
put('blake3', [5], 'Q9', A('COMPUTED', 'ROLL the r5 body (r7c program at ROUNDS 5, prefix 2): 125.388 -> 125.19806 = -0.190; cut lemma -0.0296; both stack. Rolled r5c 77fb5c02 filed at 125.19806 (review)', B + ' (ranked cuts 1-2)', 'Selftest/KATs not run at r5 at the time of the dig; machine reading and convention risk equal r7c.', gain=0.190, labels=['E']))
put('blake3', [6], 'Q9', A('COMPUTED', 'ROLL the r6 body: 125.680 -> 125.25234 = -0.428; cut lemma -0.0284. Filed B3R6c 1cf99082 (125.25234), B3R6d a5248fe7 first-collision 125.2309; B3R6u5 a0398a27 (5-byte) 124.94974 refuted on F1-trail-index-overflow', B + ' (ranked cuts 1-2); research/FILINGS.md', 'Fix named by the ruling: 16-bit trail id < 76,231-entry table.', gain=0.428, labels=['E']))
put('blake3', [7], 'Q9', A('COMPUTED', 'cut lemma -0.0216 (r7c B 1.3673e36 -> 1.3468e36); B3R7d 125.26917 first-collision filed; B3R7e 124.97458 (straight step, 5-byte gates, 2^20) filed', B + ' (ranked cuts); research/FILINGS.md', 'r7 board: leader 616120b2 TheTradoor 125.18448 (see Q8).', gain=0.0216, labels=['E']))
put('blake3', [4, 5, 6, 7], 'Q14', A('COMPUTED', 'cut lemma rows r4..r7 (interval lemma, lemma_rows.py): r4 -0.0535, r5 -0.0296, r6 -0.0284, r7 -0.0216; time from the filed ledger with only B changed', B + ' (cut 2); research/levers_1016/cutlemma', 'Author-only check; independent read pending.', gain=0.0216, labels=['E']))
put('blake3', [4, 5, 6, 7], 'Q11', A('COMPUTED', 'cut-lemma and roll levers measured on four rows (r4..r7) with the same scan.py; r3 transfer: B3R4-10 in CELLS (r3 to r4 transfer COMPUTED); r3 itself is at its floor', B + '; research/dig/CELLS.jsonl B3R4-10', 'Roll does not apply to r4 (straight fits 2^20) and r3.', labels=['N']))

# ============================ SHA-256 ============================
S = 'research/levers_1016/dig_s256step/RESULT.md'
G64 = 'research/levers_1016/gap_s256r64/RESULT.md'
put('sha256', [39], 'Q1', A('COMPUTED', 'rolled r39 kernel (124.37646: nit 8, ss 7, kappa 15, Tp 139, tmax 10013): main = body*B is 98.61 % of N; recovery 1.386 %; kernel 55,153 = straight 14,286 + 3 + 8 x 5,108; loop step 1,244 gates (6 adds = 924 = 74 %, Sigma 128, Ch 96, Maj 96, +32 loads, 4 control); code 759 KB of 1 MiB; table 10,013 x 22 B; 1 op/batch = 2.6e-5 bit, 1 loop-body gate = 2.1e-4 bit',
                          S + ' (where the cost goes)', 'Real generator (bssha_t.py) reproduced 124.37645507.', labels=['D'], held='filed ROLL2 kernel, 3 batches x 256 lanes KAT'))
put('sha256', [39], 'Q9', A('COMPUTED', 'Ch/h shared XOR: -0.02596 bit (124.37646 -> 124.35050; loop body 5,108 -> 4,985, tmax 10,162, Tp 141); program equal to scalar r39 compression on 3 batches x 256 lanes; nothing else above 0.005 bit in the kernel; code-for-table sensitivity only -0.016..-0.058 bit for 50..500 KB',
                          S + ' (ranked levers, sensitivity)', 'Run on this PC: bit-exact recheck on the cloud box still due. Needs hg word as 10th state word in Python AND C generator, Appendix A rerun, wasm VM run, intake; est 4-6 h.', gain=0.02596, labels=['E']))
put('sha256', [39], 'Q12', A('COMPUTED', 'prefix choice: all-zero prefix is already the minimum straight cost (12,656 gates; 243 patterns tried, best other +19; the rival prefix gives kernel 55,208, +55); chain-word order in W5..W12 identical cost (60 random permutations); polarity majority for loop W\' inputs +0.046 worse', S + ' (empty squares)', 'Closed squares recorded; all COMPUTED.', labels=['Z']))
put('sha256', [39], 'Q13', A('COMPUTED', 'straight 14,286: schedule+K gates 11,681 (W16..W38: 23 words, ~640 gates each; sigma0 976, sigma1 1,134, 3 adds 7,772, K adds 1,830), steps 5,6: 944 (steps 0..4 fold to constants), T stores 928, N 541, S 128, M 33; 6 FA rows/step is the floor for two outputs sharing t1; FA = 5 gates optimal; K fold >= 2 gates/bit', S + ' (where the cost goes, empty squares)', 'Floor arguments DERIVED.', labels=['Z', 'D']))
put('sha256', [64], 'Q1', A('COMPUTED', 'roll4 r64 model 124.6384 (nit 14, 36 B/instr, 579 regs, 118,845 ops per 256-lane batch = 464.09/trail; 118,808 records incl. 9,472 loads, 3,488 stores, 209 NOT, 64 set, 30 moves, 254 control; schedule loop 48 it; table 17,791 x 22 B; Tp 257; recovery 3,354 ops/call); filed unrolled feaf14f3 124.99212', G64 + ' (side-by-side ledger)', 'Rival 6b678689 124.41766 (unrolled, 5-byte body, 100,260 ops/batch = 391.64/trail).', labels=['D'], held='roll4 r64 package read-only; not filed'))
put('sha256', [64], 'Q8', A('COMPUTED', 'rival 6b678689 (dariolina, Claude Fable 5.1) 124.41766 review; gap to us: filed 0.575, roll4 0.2207. Ranked: rolling overhead records 13,517 vs 48 = +0.1796; constants not folded in the rolled schedule loop (+4,461 gates) +0.0624; unrolled gate count 618 higher +0.0089; ours better: table size -0.0248, recovery ~0.004', G64 + ' (sections 1-2)', 'Rival read as DATA from its note (rival_note.txt). Check 0.2455-0.0248 = 0.2207 = observed gap.', gain=0.2207, labels=['E']))
put('sha256', [64], 'Q14', A('COMPUTED', 'roll4 covers 0.354 of the 0.575 gap (62 %); the remaining 0.2207 is entirely the rival\'s declared 5-byte body instruction (fully unrolled kernel, 1,024 declared regs, 866 used, code 712,980 B); our u5 line S256U5R64B d76f9105 124.39014 filed and judged REJECTED not_evaluable (only lane_experiments H3-machine-convention unsupported)', G64 + ' (sections 1, 3); research/FILINGS.md', 'Credit 6b678689 for the 5-byte encoding and full unroll.', gain=0.2207, labels=['E']))
put('sha256', [64], 'Q7', A('COMPUTED', 'preprocessing 2^11.0 units inside time (rival 2^14.2); walk = digest minus IV (744875ec device, credited), identical', G64, '', labels=['N']))
put('sha256', [64], 'Q5', A('COMPUTED', 'success 0.390000003722 certified (rival claims 0.39152 vs premise 0.39)', G64, '', labels=['P']))
put('sha256', [64], 'Q3', A('COMPUTED', 'memory 1,048,562 B (roll4) vs rival 1,048,570 B: both full at 2^20; registers 579 = 18,528 B, arrays W\',W,K 172,032 B, counters 16,384 B', G64, 'Code 450,216 B (12,506 instr) vs rival 712,980 B.', labels=['Z']))

# ============================ SHA3 ============================
L = 'research/levers_1016/dig_ls1rows/RESULT.md'
S7 = 'research/levers_1016/dig_sha3r7/RESULT.md'
G24 = 'research/levers_1016/gap_sha3r24/RESULT.md'
put('sha3', [7], 'Q1', A('COMPUTED', 'LS1R7 step 35,517 ops (XOR 26,083 / AND 4,954 / OR 3,302 / NOT 1,178) = 138.7 per eval on a 2,192-register no-load/store convention (H_reg, contested); old entry 3183c941 was 44,940/step = 175.5/eval at 1,024 regs; rival non-memory ops 34,364 (XOR 24,148 / AND 4,325 / OR 3,923 / NOT 1,964)', S7 + ' (sections 0-1)', 'Per full round 6,940 vs ideal 6,720; round-0 linear stage tiny (128+34 XOR). Verify.py: 0 bad bits vs Python 7-round Keccak on 64 random inputs.', labels=['D'], held='LS1R7 generator, trial 192'))
put('sha3', [7], 'Q8', A('COMPUTED', 'rival 84a44ee0: 39,165 ops/step = 153.0 per eval on 1,024 regs (599 LD + 599 ST per middle round = 18.72/eval of memory traffic); apples-to-apples we are 1,153 ops (3.4 %, 0.048 bit) heavier on pure logic, rival heavier in machine convention', S7 + ' (section 0)', 'Rival read as DATA from its note.', gain=0.0476, labels=['E']))
put('sha3', [7], 'Q13', A('COMPUTED', 'polarity: chi mixed-polarity costs about 540 extra ops/round vs the 320 floor; PROVEN by brute force over 2^25 lane-uniform polarity states that every 5-cycle row needs >= 1 NOT; DP finds 3 consecutive rounds at the floor, 5 rounds at 26; no exact fixed point; gen_v6 measured WORSE (35,9xx-36,2xx vs 35,517) because round-2 input polarity is random from the message constants', S7 + ' (section 2)', 'Needs K chosen (GF(2) elimination / polarity search) so each lane\'s planes share one polarity after rounds 0-1: ~1 day, upper bound -700..-1,150 ops.', gain=0.0476, labels=['E']))
put('sha3', [7], 'Q9', A('COMPUTED', 'lever 1 lane complementing with copy-NOTs: derived ceiling -1,153 ops = -0.0476 bit (124.286 -> ~124.238), practical ~-0.029; random constant search spread only 35,517..35,729 (0.6 %); rival\'s other claims do not apply to LS1R7. Filed successors LS1V4R8..R19 etc. are rows 8+', S7 + ' (section 2)', 'STATUS PARTIAL.', gain=0.0476, labels=['E']))
put('sha3', [8], 'Q1', A('COMPUTED', 'LS1v3 r8 124.2656: main steps 97.73 % (40,602 ops/step) | replay 2.23 % (0.032 bit) | hit budget (HMAX incl. +Lc) 0.036 % | setup/DP/restart/preproc ~0; versus ideal birthday (0.994*2^128 evals at p=.39) Tb is 1.0038*2^128 (+0.0137 bit): DP latency ~0.011 + failure terms F1..F4 ~0.002 bit', L, 'Model reproduces the certificate (124.26560 vs 124.26561); exact_check.py re-evaluates with cert3 Decimal success(): p = 0.3900000004. Not run through a rebuilt factory row.', labels=['D'], held='model.py = cert3.py --scan formulas, float'))
put('sha3', [18], 'Q1', A('COMPUTED', 'LS1v3 r18: H=114/kappa 17 forced by the table (6.3k..10.5k words because the straight line is 107k..134k ops x 5 B); replay share 3.4-3.5 %', L, 'Same for r19..r22 (H=114 forced by the table).', labels=['D']))
put('sha3', [22], 'Q1', A('COMPUTED', 'LS1v3 r22: H=114/kappa 17, straight line 134k ops x 5 B, replay share 3.4-3.5 %', L, 'r22 table words ~6.3k.', labels=['D']))
lev = {8: ('-0.0145', '-0.0209', '-0.0287', '-0.0327'), 18: ('-0.0217', '-0.0314', '-0.0442', '-0.0533'), 22: ('-0.0200', '-0.0048', '-0.0235', '-0.0352')}
for r, (c, a, ac, abc) in lev.items():
    put('sha3', [r], 'Q9', A('COMPUTED', 'LS1v3 levers r%d: C (decouple replay cap from trail cap) %s; A (real-valued H) %s; A+C %s; A+B+C %s' % (r, c, a, ac, abc), L, 'Refile needs other3.py separate replay constant, cert3 F1->F6 and a proof paragraph for F6 (union bound on points in long trails).', gain=-float(abc), labels=['E'], held='model.py float, not a rebuilt row'))
put('sha3', R(9, 17), 'Q9', A('LOCAL_ONLY', 'rows r9..r17 behave like r8 (H=113, replay share 2.0-2.2 %): expect A+C about -0.029..-0.030, with B about -0.033', L, 'Extrapolated by the dig author from r8/r18/r22; not individually run.', gain=0.03, labels=['E']))
put('sha3', R(19, 21), 'Q9', A('LOCAL_ONLY', 'rows r19..r21 behave like r18/r22 (H=114 forced by the table): A+B+C about -0.04..-0.05', L, 'Extrapolated; not individually run. Sum over 15 rows about -0.5 bit (the board counts rows, not the sum).', gain=0.04, labels=['E']))
put('sha3', [8, 18, 22], 'Q4', A('COMPUTED', 'memory +2000 table words on top of A+C: r8 -0.0010 / r18 -0.0063 / r22 -0.0089, NOT available: setwalk (1,283) and gather (1,022) are unrolled because registers are statically addressed, 74 of 86 KB other code; shaving 1 op/plane gives ~16 KB = 500 words = -0.0003 (r8) .. -0.002 (r22); MARGIN 4096 -> 0 at most -0.0006 (r22)', L, 'A rolled round body (straight line 667 KB at r22 -> table 3x) would add about -0.01..-0.02 (not tried).', labels=['Z']))
put('sha3', [24], 'Q1', A('COMPUTED', 'ours v4b r24 0bd0022d: 181,720 ops per 256 evaluations = 709.84/eval (AFF 3,084 + 11 x GB 7,871 + 11 x GA 8,298 + R23 701 + 33,206 load/store/move + loop 56 + prefilter 17 + counter 3); looped 2-round body x 11 at 32 B/instruction; unit 6,504 = 24 x 271 (organizer contract); time 124.85542 = log2(N/6504); Tb = 1.0113 x 2^128', G24 + ' (ledger table)', 'Exact integer certificate, executed selftest 0/300 digest, 0/512 lane diffs.', labels=['D']))
put('sha3', [24], 'Q8', A('COMPUTED', 'rival sraiw ac6d8975 124.56303 (review, plausible_not_refuted, 24 unresolved obligations): the 0.292 bit saving is not adoptable; their T does not follow from their own parameters (walk term 2^8.015 too small, a factor ~256; with it fixed 2^132.57 in their unit, 7.7 bits WORSE than ours); cost 13,686 word ops per eval in a 64-bit lane model vs our 709.84 bit-sliced; their unit 13,706 vs contract 6,504', G24, 'Rival read as DATA from board snapshot 19:53 MDT; nothing run.', labels=['K'], own=True, held='arithmetic on their printed numbers'))
put('sha3', [24], 'Q12', A('COMPUTED', 'r24 is the last row; the contract unit is 24 x 271 = 6,504; rival divides by 13,706; evaluations count for 256-bit collision cannot be below ~2^128 (their R x L is 2^132.58)', G24, '', labels=['E']))

# nothing else is pre-filled by hand; Q8 / Q10 are filled from the board and FILINGS below.

# ------------------------------------------------------------------------------------------------ build cells
def mk_cells(famkey):
    spec = FAMS[famkey]
    out = []
    qs = QCORE + QFAM[famkey]
    rows = spec['rows']
    for R_ in rows:
        mine = MY[famkey].get(R_, [])
        ours, riv = rival_line(famkey, R_)
        for qk, qname, qtext in qs:
            cid = 'PR-%s-r%d-%s' % (famkey, R_, qk)
            q = qtext.format(R=R_, HASH=famkey, R_minus=R_ - 1, R_plus=R_ + 1)
            a = PRE.get((famkey, R_), {}).get(qk)
            # auto-filled cells
            if qk == 'Q10':
                a = q10(famkey, R_, mine)
            if qk == 'Q8' and a is None:
                a = q8(famkey, R_, ours, riv)
            elif qk == 'Q8' and a is not None:
                # keep the hand answer, append the board facts
                extra = q8(famkey, R_, ours, riv)
                a = dict(a)
                a['notes'] = (a['notes'] + ' | Board snapshot: ' + extra['number']).strip(' |')
            rec = dict(id=cid, hash='%s-r%d' % (spec['hash'], R_), row_i=R_, row_j=None,
                       object='[PR %s r%d %s] %s' % (famkey, R_, qk, qname), question=q)
            if a:
                rec.update(labels=a['labels'], status=a['status'], number=a['number'], source=SRC, own_test=a['own'], evidence=a['evidence'], date=DATE,
                           lever=a['gain'] is not None, gain_bits=a['gain'], notes=(a['notes'] + ' ' + exist_note(spec['hash'], R_)).strip(),
                           peak_mem='UNKNOWN row memory not part of this record' if a['status'] != 'OPEN' else 'UNKNOWN')
                if a['gain'] is not None:
                    rec['gain_basis'] = 'T'
                if a.get('held'):
                    rec['held_fixed'] = a['held']
                if a.get('reopen'):
                    rec['reopen_if'] = a['reopen']
            else:
                rec.update(labels=['N'], status='OPEN', number='not run', source=SRC, own_test=False,
                           evidence='research/dig/new/QUESTION_TEMPLATE (GRID_%s.md section "Pareto-row questions")' % famkey.upper().replace('-', '_'),
                           date=DATE, lever=False, gain_bits=None,
                           notes=('Template question, no answer in our files yet. Candidate sources: ' + sources_hint(famkey, qk, R_) + ' ' + exist_note(spec['hash'], R_)).strip(),
                           peak_mem='UNKNOWN')
            rec['topic'] = 'PR %s r%d %s' % (famkey, R_, qk)
            out.append(rec)
    return out


def sources_hint(famkey, qk, R_):
    base = {
        'poseidon-generic': 'research/rows_1016/factory/posgen_route2d2 (ledger.txt/counts for r%d), research/levers_1016/dig_posgen/RESULT.md, research/FILINGS.md, research/dossiers/<id>.' % R_,
        'poseidon-algebraic': 'research/poseidon/algebraic_paper/ledger.py, research/levers_1016/pos_alg_rows (gen_row.py %d), research/levers_1016/r7alg_refile, research/grok/work (Grok 133-141).' % R_,
        'blake3': 'research/blake3_r%d/, research/levers_1016/dig_b3r3, dig_b3r4r7, research/FILINGS.md.' % R_,
        'sha256': 'research/rows_1016/factory/s256roll*/s256u5 (r%d), research/levers_1016/dig_s256step, gap_s256r64, research/FILINGS.md.' % R_,
        'sha3': 'research/rows_1016/factory/ls1v4/ls1v3 (r%d), research/levers_1016/dig_ls1rows, dig_sha3r7, gap_sha3r24, research/FILINGS.md.' % R_,
    }[famkey]
    return base


def q8(famkey, R_, ours, riv):
    fam = FAMS[famkey]['board']
    snap = 'board snapshot research/rivals/boards_%s-pareto_live.json (2026-10-17 ~01:00 MDT)' % fam
    if riv:
        b = riv[0]
        n = 'best rival valid entry on r%d: %s %s score %s (time %s, mem log2 %s, %s/%s); %d rival entries; our best on the row: %s' % (
            R_, b['user'], b['id'], b['score'], b['t'], b['mem'], b['status'], b['review'], len(riv),
            ('%s %s (%s)' % (ours[0]['id'], ours[0]['score'], ours[0]['status']) if ours else 'none valid on board'))
        return A('LOCAL_ONLY', n, 'research/rivals/boards_%s-pareto_live.json' % fam,
                 'Holder and score read from the board as DATA (no code run). WHERE the rival saves is NOT yet analysed for this row; add a ledger comparison (gap_* dig files show the format) to close the cell.', labels=['E'])
    n = 'no valid rival entry on r%d in the %s; our best valid entry: %s' % (R_, snap, ('%s %s (%s)' % (ours[0]['id'], ours[0]['score'], ours[0]['status']) if ours else 'none'))
    return A('COMPUTED', n, 'research/rivals/boards_%s-pareto_live.json' % fam, 'EMPTY SQUARE for rivals on this row (as of the snapshot); a rival may appear later - re-read the board before filing.', labels=['0'])


def q10(famkey, R_, mine):
    if not mine:
        return A('COMPUTED', 'no filing of ours on %s r%d in research/FILINGS.md (as of 2026-10-17 ~01:00 MDT): no judge finding exists for this row' % (famkey, R_), 'research/FILINGS.md', 'Empty square: nothing filed on this row.', labels=['0'])
    fam = FAMS[famkey]['board']
    parts = []
    anyrul = False
    for e in mine:
        b = BOARD.get(fam, {}).get('_by_id', {}).get(e['id'])
        if b:
            ft = e['res'] if (e['res'] and not e['res'].startswith('validating') and e['res'] != 'review') else ''
            s = '%s %s [%s] board:%s%s%s' % (e['id'], e['label'], e['tl'][:24], b['status'], (' reason=' + b['reason'][:60].replace('Original HashSmash judge: ', '') if b['reason'] else ''), (' | FILINGS: ' + ft[:150] if ft else ''))
            if b['status'] not in ('validating',):
                anyrul = True
        else:
            s = '%s %s [%s] filings:%s' % (e['id'], e['label'], e['tl'][:24], e['res'][:110])
            if e['res'] and not e['res'].startswith('validating'):
                anyrul = True
        parts.append(s)
    num = '%d filing(s) on r%d: ' % (len(mine), R_) + ' ; '.join(parts[:6]) + (' ; +%d more' % (len(parts) - 6) if len(parts) > 6 else '')
    st = 'COMPUTED' if anyrul else 'OPEN'
    note = 'Status read from the board snapshot where our id is present, else from FILINGS.md (the ruling column may be stale: reconcile each heartbeat). Dossier: research/dossiers/<id> (fetch the hashsmash-review artifact for the full findings).'
    if st == 'OPEN':
        num = num + ' ; no ruling recorded yet'
    return A(st, num, 'research/FILINGS.md; research/rivals/boards_%s-pareto_live.json' % fam, note, labels=['E'])


def write_all():
    summary = collections.OrderedDict()
    for famkey in FAMS:
        cells = mk_cells(famkey)
        path = os.path.join(HERE, famkey + '.jsonl')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            for c in cells:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
        cnt = collections.Counter(c['status'] for c in cells)
        summary[famkey] = dict(rows='r%d..r%d' % (FAMS[famkey]['rows'][0], FAMS[famkey]['rows'][-1]), nrows=len(FAMS[famkey]['rows']), cells=len(cells), by_status=dict(cnt), path=path)
    return summary


if __name__ == '__main__':
    s = write_all()
    print(json.dumps(s, indent=1))
