# Negative-space map: place every catalogued record on six axes, then build the grids.
# Reads catalogue\catalogue\methods.csv (read-only). Writes records.csv, cells.csv, GRIDS.md here.
# Run: python -B build.py
import csv, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'catalogue', 'catalogue', 'methods.csv')

# id base free part layer tech res goal status   (codes in AXES.md)
CLASS = """
A1 fh len A r0 canc word half alive
A2 fh none B r1d class word resid alive
A3 fh const B r1c class bit resid alive
A4 fh const B r1c class bit resid alive
A5 fh const B r1c class bit resid alive
A6 fh msg B r1d gd word resid alive
A7 fh none B all cost word cost alive
A8 fh msg B r1d class bit cost alive
A9 ctr ctr B r0 gd word resid alive
A10 ctr ctr B r1d class bit cost open
A11 mode cv B mode canc word half alive
A12 fh none B all cost word tool dead
A13 fh const B r1d class word resid dead
A14 fh const B r1d class bit resid dead
F1 fh len A r0 canc word half alive
F2 fh len A r0 canc word half alive
F3 fh len A r0 canc word half alive
F4 fh len A r0 canc word half alive
F5 fh len A r0 canc word half alive
F6 fh len A r0 canc word half alive
F7 fh len A r0 canc word half alive
F8 fh len A r0 canc word half dead
F9 fh len A r1c canc word half dead
R1 fh none B all cost word cost alive
R2 fh none B all cost word cost open
R3 fh none B r1d class bit cost alive
R4 fh const B r1c class word resid open
R5 fh none B all cost bit cost alive
R6 fh msg B r0 gd word cost alive
R7 fh const B r1d class bit resid alive
R8 fh const B r1c canc word resid dead
R9 fh none B r1d class bit cost alive
R10 fh none B r1d class bit cost alive
R11 fh msg B r1d gd word cost alive
R12 fh none B all cost word cost alive
R13 fh none B r1d class bit cost dead
R14 fh msg B r1d class bit cost dead
R15 fh const B r1c class bit resid dead
R16 fh msg B all cost bit cost open
R17 fh const B r1c class word resid dead
R18 mode cv B mode class word resid dead
R19 fh ctr B r0 class word resid dead
R20 fh none B all class word cost dead
R21 fh mem B all cost word cost dead
R22 fh none B all cost bit cost alive
N1 fh msg B r1d gd word resid dead
N2 fh msg B r1d gd word resid dead
N3 fh msg B r1d gd word resid dead
N4 fh mem B r1d join word resid dead
N5 fh msg B r1d gd word cost dead
N6 fh msg B r1d alg bit resid dead
N7 fh msg B r1d alg word resid dead
N8 fh msg B r1d gd bit resid dead
N9 fh msg B r1d gd bit resid dead
N10 fh msg B r1c alg word resid dead
N11 fh const A r1c trail bit half dead
N12 fh len A r1c canc word half dead
N13 fh len A r0 canc word half dead
N14 fh msg B r1c heur word resid dead
N15 fh msg B all heur bit resid dead
N16 fh msg B r1d join word resid dead
N17 fh msg B r1d join word resid dead
N18 gen msg AB r0 canc word half dead
N19 fh msg A r0 canc word half dead
N20 fh len AB r1d trail bit coll dead
N21 gen msg k r1d gd word half dead
N22 gen msg AB all alg bit coll dead
N23 ctr ctr B r1d gd word resid dead
N24 fh msg B r1d gd word cost dead
I1 fam msg A r1d gd word samp dead
I2 fam msg B r1d gd word samp dead
I3 fam msg A r1d gd word samp dead
I4 fam const A r1d gd word samp dead
I5 fam msg A fold gd word samp dead
I6 fam msg A r0 canc word samp dead
I7 fam cv A mode gd word samp dead
I8 fam mem A all gd word samp dead
I9 fam msg A r1d sym word samp dead
I10 fam cv A mode join word samp dead
I11 fam msg k fold gd word samp dead
I12 fam msg A all join word samp dead
I13 fam msg A all join word samp dead
I14 fam msg A all join word tool n/a
I15 fam msg A all gd word tool dead
I16 fam msg A all gd bit samp dead
I17 fam msg A all alg bit samp dead
I18 fam const A fold class word samp dead
I19 fam ctr A r0 gd word samp dead
I20 fam msg A r1d alg word tool open
I21 fam const A r0 class word samp open
I22 fam msg k r1d gd word samp dead
T1 gen msg AB all trail bit coll dead
T2 gen msg AB all trail bit coll dead
T3 gen msg AB r1c trail bit coll dead
T4 gen msg AB all trail bit coll dead
T5 gen msg AB fold trail bit coll dead
T6 gen msg AB all trail bit coll open
T7 fh const A r1c trail bit half open
T8 gen msg AB all sym bit coll dead
T9 fh len B fold canc word resid dead
T10 mode flag A r0 canc word half dead
T11 fh len B r1d trail bit resid open
T12 gen msg AB r1c trail bit coll open
S1 fam msg A all gd word samp dead
S2 fam msg A all gd word samp dead
S3 fam msg A all gd word samp dead
S4 fam msg A all gd word samp dead
S5 gen msg AB all sym word coll dead
S6 gen const AB all sym word coll dead
S7 gen msg AB all sym bit coll dead
S8 gen msg AB all sym word coll dead
S9 fam msg k all gd word samp dead
S10 gen msg AB all sym word coll dead
S11 gen msg AB all sym word coll dead
S12 gen msg AB all sym word coll dead
S13 gen msg AB fold join word coll dead
S14 gen msg AB r1d alg word tool n/a
G1 fam msg A all heur bit samp dead
G2 fam msg A all heur bit samp dead
G3 gen msg A all heur bit half dead
G4 gen msg AB all heur bit coll dead
G5 gen msg AB all join word coll dead
G6 fam msg A all heur word samp dead
G7 gen msg AB r0 sym word coll dead
G8 fam msg k all join word samp dead
G9 ctr ctr B r1d class bit resid open
M1 mode ctr AB mode canc word coll dead
M2 mode cv AB mode canc word coll dead
M3 mode cv AB mode join word coll dead
M4 ctr ctr B r0 gd word resid dead
M5 mode flag AB mode canc word coll dead
M6 mode cv AB mode canc word coll dead
L1 fh msg B r1d join bit resid open
L2 fam msg A all alg bit samp open
L3 fam msg A all gd word tool n/a
L4 gen msg AB all trail bit coll dead
L5 fh msg B r1d gd bit cost dead
L6 gen msg AB all join word coll dead
L7 fh len A r0 canc word half alive
L8 gen none AB all cost word tool n/a
V1 fh none B r1d class bit tool n/a
V2 fh none AB all class word tool n/a
V3 fh none B all class word tool n/a
V4 fh none B r1d class bit tool n/a
V5 fam none A all gd word tool n/a
V6 fh none B r1c class word tool n/a
V7 ctr none B r1d alg word tool n/a
V8 fh none B r1d class bit tool n/a
V9 fh none B all cost word tool n/a
V10 fh none B fold class word tool n/a
O1 r1 len AB r0 canc word coll alive
O2 r1 msg AB r0 alg word coll alive
O3 r1 msg AB r0 sym word coll alive
O4 r1 len AB r0 canc word coll dead
C1 fh len A r0 canc word - n/a
C2 fh none A fold canc word - n/a
C3 ctr ctr B r0 gd word - n/a
C4 gen msg AB r0 alg word - n/a
C5 gen const AB all sym word - n/a
C6 gen msg A r0 canc word - n/a
C7 gen none AB all gd word - n/a
C8 gen none AB all trail bit - n/a
C9 fh len B fold canc word - n/a
C10 fh none B all class word - n/a
C11 mode none AB mode cost word - n/a
C12 gen none AB all - - - n/a
C13 fh const B r1c class bit - n/a
C14 fh const B r1c class word - n/a
C15 gen mem AB all cost word - n/a
C16 gen msg AB r1d alg word - n/a
X1 ctr const B r1d class bit resid alive
X2 ctr ctr B r1d gd word resid alive
X3 ctr const B r1d class bit resid alive
X4 ctr none B all cost bit cost alive
X5 ctr cv B mode gd word resid dead
X6 ctr ctr B r0 gd word resid open
X7 mode ctr A r0 canc word half dead
X8 mode flag AB mode canc word coll dead
X9 ctr ctr B r1d gd word resid open
X10 ctr none AB mode class word tool n/a
X11 ctr const B r1c class bit resid dead
X12 ctr none B r1d class bit cost dead
X13 ctr none B r1d class bit cost alive
K1 mode ctr B mode gd word resid dead
K2 mode ctr A r0 canc word half dead
K3 ctr ctr A r0 gd word half alive
K4 ctr const B r1c class bit resid alive
K5 mode len A mode canc word half dead
K6 fh const A r1c canc word half dead
K9 fh len B r1d canc word half dead
K10 mode ctr AB r0 canc word coll dead
Z1 fh const B r1d class bit resid alive
Z2 fh none B all cost word cost alive
Z3 fh mem B all cost word cost alive
Z4 fh none B r1d cost bit cost alive
Z5 fh none B all cost word cost alive
Z6 fh msg B r1d join word resid dead
Z7 fh msg AB r1d canc word coll dead
Z8 gen msg AB all sym word coll dead
Z9 gen none AB all alg word tool dead
Z10 fh len AB r0 canc word coll dead
Z11 mode flag AB r1c canc word coll dead
Z12 fh msg B r1d join bit resid dead
Z13 fh const B r1d class word resid alive
Z14 fh const B r1d class word resid alive
Z15 ctr ctr B r1d alg word resid dead
Z16 ctr ctr B r1d join word resid dead
Z17 ctr const B r1c alg bit resid alive
Z18 fh none B fold alg word resid dead
Z19 fh none B fold sym word resid dead
Z20 fh none B fold heur word resid dead
Z21 fh none B fold cost word resid dead
Z22 mode msg AB mode canc word coll open
Z23 mode none AB mode trail word coll dead
Z24 fh ctr B r1c cost word cost open
Z25 fh msg B r1c join word resid dead
Z26 fh msg B r1c gd word resid dead
Z27 fh const B r1d heur bit resid dead
Z28 mode flag AB mode trail bit coll dead
Z29 ctr ctr AB r0 trail bit coll dead
Z30 fh const B r1d join word resid dead
Z31 gen none AB r1d class word resid dead
Z32 fh none B r0 cost word cost dead
Z33 gen msg AB all canc word coll dead
"""

CN = r'research\newpaths\counter_next'
CS = r'research\newpaths\counter_swing'
CE = r'research\catalogue\census\CENSUS.md'
# Records not in methods.csv: today's counter_next / counter_swing outputs (X, no summary doc yet) and CENSUS rows (K).
NEW = {
 'X1': ('Counter loop: exact outer-step filter on (Y9, E), enumeration kept (stack L5 / V3)', 75.19, 'DERIVED (pass share COMPUTED)', 'pass 2^-9.835 on 1M real outer steps vs model 2^-9.8132; unadjudicated', CN + r'\stack\stack_calc_out.txt; real_filter_1M.txt'),
 'X2': ('Counter loop: E3-first solve per passing outer step (stack L6 / V4)', 70.99, 'DERIVED', 'planted h1 found 300/300; 0 E3 solutions on 150 + 120 real passing steps; solve 2^18.5-2^19.3 ops per pass', CN + r'\stack\e3solve_out.txt; e3solve2_out.txt; stack_calc_out.txt'),
 'X3': ('Counter loop: rule G + Y4 cube 07ef8307 (all 14 rows kept)', 84.53, 'DERIVED (ops GUESS)', '+0.43 bit on 84.96', CN + r'\stack\stack_calc_out.txt'),
 'X4': ('Counter loop: bitsliced stage A (generic / specialised)', 83.58, 'DERIVED', '83.58 generic, 82.94 specialised; needs the judge to accept 256-lane bitslicing', CN + r'\stack\stack_calc_out.txt L4a, L4b'),
 'X5': ('Chaining-value words as knobs in the counter system', '', 'DERIVED', 'basis with all 8 CV words exists, but a solved CV word is a 2^-32 preimage filter', CN + r'\knobs\knobs_model_out.txt [cv], [cvT]'),
 'X6': ('High counter word T1 chosen or solved per outer step (knobs Q2)', '', 'COMPUTED basis, value unknown', 'w8, C2.b1, C2.c1 need T1 solved (2^-13 filter); no conditional count', CN + r'\knobs\knobs_model_out.txt; census V10'),
 'X7': ('Counter-difference cancellations (low, high, both) at w = 32', '', 'COMPUTED', 'round 0 equal 2^20/2^20, every round-1 call hit, half A and B equal 0', CS + r'\around\route_out.txt; census N5'),
 'X8': ('Leaf-vs-parent placements (last chunk against a parent node)', '', 'COMPUTED', '448 placements lift (planted 52/52); round 0 absorbable 500/500; after 2 rounds 0 of 8 words equal', CS + r'\around\tree_align.txt; absorb32.txt'),
 'X9': ('Counter prescribes E3.h1 instead of E1.d1 (Y4 + E3.h1 basis)', '', 'COMPUTED basis, value unknown', 'basis exists with t free; no 3-word basis; not valued', CS + r'\opposite\constraint_check.txt part 2'),
 'X10': ('Counter toy pairs: prefix content free, other t / suffix / crossing fail', '', 'COMPUTED', '240/240 random prefixes collide (distinct digests); other t 0/58; suffix 0/60', CS + r'\opposite\replicate_toy.txt'),
 'X11': ('Counter loop: Y4 whole class with the filed rule A', 85.96, 'COMPUTED', '-1.0 bit against 84.96', CN + r'\stack\stack_calc_out.txt L2a'),
 'X12': ('Counter loop: rule A with a ninth condition for beta*', 85.00, 'DERIVED', '-0.043 bit', CN + r'\stack\stack_calc_out.txt L1a'),
 'X13': ('Counter loop: split stage 2 at the listed-tau test', 84.91, 'DERIVED', '+0.053 bit; machine count needed', CN + r'\stack\stack_calc_out.txt L3b'),
 'K1': ('Counter solved per trial with a multi-block last chunk', 100.45, 'COMPUTED + GUESS cost', 'circular: chained CV depends on t (0/1000 consistent); 100.45 unforced', CE + ' section 4 N4'),
 'K2': ('Counter-high difference cancelled with two pins (C0, C1)', '', 'DERIVED', 'not a message pair: different chunk indices; 0 pure counter-difference placements', CE + ' N6; ' + CS + r'\around\tree_align.txt'),
 'K3': ('Counter x short length pairs (forced bytes become outer filters)', 86.88, 'DERIVED, GUESS cost', '47/63 86.88; 46/62 90.83; 45/61 98.74; 42/58 122.74', CE + ' L-short'),
 'K4': ('Counter x other pins (L16a, L6c, pin B, L6a, L12a, L4a, L10a)', 86.80, 'DERIVED, GUESS ops', 'L16a 86.80, L6c 87.14, pin B 88.23 ... L10a 92.68', CE + ' section 0 item 3'),
 'K5': ('Parent node as the colliding compression', '', 'DERIVED', 'block length fixed at 64: no length lever', CE + ' N7'),
 'K6': ('Pinned call in pattern "b, d differ"', '', 'DERIVED', 'E0 and E2 active: 0 free words', CE + ' N8'),
 'K9': ('Free half on digest words 1, 3, 4, 6', '', 'COMPUTED + DERIVED', 'impossible: w5 is E1 second word, E1 equal 0/1000', CE + ' N2'),
 'K10': ('Root compression with a nonzero counter', '', 'DERIVED', 'impossible: root counter always 0 (verifier line 86)', CE + ' N3'),
 # 2026-10-09 records (Coset, Residue, Syndrome), from FILINGS.md and research/BLAKE3_2ROUND_MAP.md
 'Z1': ('Front line: member loop + cluster gate + exact-borrow gate (pkgCG..pkgCL)', 62.9459, 'COMPUTED (passed review)', 'pkgCL 89b451ff 62.9459; next row 62.7934 (Sol D18)', r'research\FILINGS.md; research\BLAKE3_2ROUND_MAP.md'),
 'Z2': ('Metered solver credit (H5_exec) on the front line', 62.9459, 'COMPUTED', 'credit row of pkgCK/pkgCL', r'research\BLAKE3_2ROUND_MAP.md'),
 'Z3': ('Y9 cache and register frame (0xshikhar 73d5265f idea)', 63.5184, 'COMPUTED', 'frame loads gone; rival refile answered', r'research\rivals\note_73d5265f.md'),
 'Z4': ('Masked partner walk on opened clusters', 62.9459, 'COMPUTED', 'in pkgCL; Grok 58 found 46 more units (D18)', r'research\grok\work\job58_cl_slack\ANSWER.md'),
 'Z5': ('Slack audit and one-change schedule cuts (49 items; Grok 53, 58)', 62.7934, 'COMPUTED', 'ROW 1 in pkgCK; ranks 1-4 in D18', r'research\grok\ANSWER_job53.md; job58 ANSWER.md'),
 'Z6': ('E1/E3 split of the residual (Opus cloud idea)', 84.66, 'COMPUTED', 'split costs 84.66, worse than the front line', r'research\BLAKE3_2ROUND_MAP.md'),
 'Z7': ('D4 local-collision construction (Sol D4)', '', 'PROVED', 'success probability < 2^-32', r'research\BLAKE3_2ROUND_MAP.md'),
 'Z8': ('Spiral / periodic routes (Sol 5.6 full-rank scan, Opus cloud)', '', 'PROVED', 'no carry-free route', r'research\BLAKE3_2ROUND_MAP.md'),
 'Z9': ('Coordinate changes of the residual (perspective sweep)', '', 'PROVED', 'P(collision) unchanged; round 0 is a bijection', r'research\BLAKE3_2ROUND_MAP.md'),
 'Z10': ('Routes cancelling fully in round 0 (Opus "four checks is a law")', '', 'PROVED', '>= 4 final-step conditions', r'research\BLAKE3_2ROUND_MAP.md'),
 'Z11': ('Counter and flag differences cancelled in round 1 (Grok 48)', '', 'COMPUTED', 'no in-call cancellation', r'research\grok\work (job 48)'),
 'Z12': ('Bit-level partial MITM on the residual split (Sol D4)', '', 'DERIVED', 'no gain', r'public archive D4'),
 'Z13': ('Winner line (pkgW32 117832fb)', 72.1694, 'COMPUTED (passed)', 'filed line', r'research\FILINGS.md'),
 'Z14': ('Extra-beta line (pkgXB 73b196bf)', 78.8913, 'COMPUTED (passed)', 'filed line', r'research\FILINGS.md'),
 # 2026-10-10 scout waves (research\newpaths\untried\<key>\RESULT.md)
 'Z15': ('Counter path: off-the-shelf SAT per passing step (ctr_alg)', 71.23, 'DERIVED', '-0.24 bit vs DFS; free solve ceiling +0.97', r'research\newpaths\untried\ctr_alg\RESULT.md'),
 'Z16': ('Counter path: two-sided split / join with t free (ctr_join)', '', 'COMPUTED', 'no split in any triangular basis (z3, 6 configurations)', r'research\newpaths\untried\ctr_join\RESULT.md'),
 'Z17': ('Counter path: pin N6a found with the counter objective (const_alg)', 82.80, 'DERIVED (construction unbuilt)', '2.08 bit better than H8 on paper; Sol D22 conditional', r'research\newpaths\untried\const_alg\RESULT.md'),
 'Z18': ('Fold: algebraic solve at h_i = v_i xor v_(i+8) (b3-fold)', '', 'COMPUTED', 'fold event = the collision condition itself (ratio 1)', r'research\newpaths\untried\b3-fold\RESULT.md'),
 'Z19': ('Fold: symmetry (b3-fold)', '', 'COMPUTED', 'no extra fold correlation (within 0.13 bit)', r'research\newpaths\untried\b3-fold\RESULT.md'),
 'Z20': ('Fold: heuristic search (b3-fold)', '', 'COMPUTED', 'greedy loses to random', r'research\newpaths\untried\b3-fold\RESULT.md'),
 'Z21': ('Fold: cost trick (b3-fold)', '', 'COMPUTED', "fold's XOR rewrite already used (Lemma N)", r'research\newpaths\untried\b3-fold\RESULT.md'),
 'Z22': ('Internal-block local collision {m2,m3,m4,m6} (b3-mode)', '', 'GUESS 2^50-2^62', 'no final-step conditions; K3 solves on rare combinations; K2/K1 being measured', r'research\newpaths\untried\b3-mode\RESULT.md'),
 'Z23': ('Parent-node collisions (b3-mode)', '', 'DERIVED', '>= 8 word conditions for all 65,535 patterns, about 2^129', r'research\newpaths\untried\b3-mode\RESULT.md'),
 'Z24': ('t_hi walk on the front line (b3-r1c)', 61.98, 'DERIVED (assumption GUESS)', 'up to -1.21 bit on pkgCK rows; gates and legality being checked', r'research\newpaths\untried\b3-r1c\RESULT.md'),
 'Z25': ('Round-1 column join (b3-r1c)', '', 'COMPUTED', 'lift needs 4 guessed words, 2^128', r'research\newpaths\untried\b3-r1c\RESULT.md'),
 'Z26': ('Round-1 column guess-and-determine (b3-r1c)', '', 'COMPUTED', 'only y and w0 come late, both used', r'research\newpaths\untried\b3-r1c\RESULT.md'),
 'Z27': ('Simulated annealing over E3 classes (b3-heur)', '', 'COMPUTED', 'best = known best, 5,794 points', r'research\newpaths\untried\b3-heur\RESULT.md'),
 'Z28': ('Flag-difference trails (b3-trail)', '', 'COMPUTED', 'best 2^-382; round-0-cancel trails >= 2^64.1', r'research\newpaths\untried\b3-trail\RESULT.md'),
 'Z29': ('Counter-difference trails (b3-trail)', '', 'COMPUTED', 'best 2^-757 (counter only), 2^-451 with flags', r'research\newpaths\untried\b3-trail\RESULT.md'),
 'Z30': ('Extra pinned constant to decouple E1/E3 (b3-misc)', '', 'COMPUTED', 'exact ILP: split quality 0, proved optimal', r'research\newpaths\untried\b3-misc\RESULT.md'),
 'Z31': ('Class selection on the generic base (b3-misc)', '', 'DERIVED', '13 word conditions, no 4-check floor', r'research\newpaths\untried\b3-misc\RESULT.md'),
 'Z32': ('Round-0 cost lever on the front line (b3-misc)', '', 'DERIVED', 'per-context round-0 lines 2^59.3 of 2^71.9: no structural lever', r'research\newpaths\untried\b3-misc\RESULT.md'),
 'Z33': ('Cancellation across both rounds (b3-misc; the D4 family)', '', 'DERIVED', 'about 2^65', r'research\newpaths\untried\b3-misc\RESULT.md'),
}

AX = ['base', 'free', 'part', 'layer', 'tech', 'res', 'goal']

def load():
    src = {}
    with open(SRC, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            src[r['id']] = r
    rows = []
    for line in CLASS.strip().splitlines():
        p = line.split()
        rid, vals, status = p[0], p[1:8], p[8]
        d = dict(zip(AX, vals)); d['id'] = rid; d['status'] = status
        if rid in src:
            s = src[rid]
            d['name'] = s['name']; d['kind'] = s['kind']; d['label'] = s['label']
            sc = float(s['score']); d['cost'] = '' if sc == -1 else ('%g' % sc)
            d['cost_note'] = s['score_text'][:110]; d['source'] = s['evidence'][:120]
        else:
            n = NEW[rid]
            d['name'], d['cost'], d['label'], d['cost_note'], d['source'] = n[0], n[1], n[2], n[3], n[4]
            d['kind'] = 'new-' + ('result' if status in ('dead', 'n/a') else 'variant')
        rows.append(d)
    missing = set(src) - {r['id'] for r in rows}
    assert not missing, missing
    return rows

COLS = ['id', 'name', 'kind', 'base', 'free', 'part', 'layer', 'tech', 'res', 'goal', 'cost', 'label', 'status', 'cost_note', 'source']

TECH = ['trail', 'gd', 'join', 'sym', 'class', 'canc', 'alg', 'heur', 'cost']
IVROW = 'row 2 is IV0..IV3 in every compression; no metadata or CV choice makes the state symmetric (C5, S12)'
FEW = 'few legal values fixed by message size or node position: a pair difference only, not a per-trial unknown'
NOFREE = 'no freedom added: measurement, convention or cost only'
TABLES = 'tables cut cost per trial, never the number of trials (R21, C15)'
COSTX = 'cost levers add no freedom (see row none)'
GRIDS = [
 ('free', ['msg', 'len', 'ctr', 'flag', 'cv', 'const', 'mem', 'none'], {
   **{('len', t): FEW for t in ['gd', 'join', 'class', 'alg', 'heur']},
   **{('flag', t): FEW for t in ['gd', 'join', 'class', 'alg', 'heur']},
   **{(r, 'sym'): IVROW for r in ['len', 'ctr', 'flag', 'cv', 'mem']},
   **{(r, 'cost'): COSTX for r in ['len', 'ctr', 'flag', 'cv', 'const']},
   **{('mem', t): TABLES for t in ['trail', 'canc', 'class', 'heur']},
   **{('none', t): NOFREE for t in ['trail', 'gd', 'join', 'sym', 'canc', 'alg', 'heur']},
   ('cv', 'alg'): 'a solved CV word is a 32-bit preimage of the previous block (X5)'}),
 ('base', ['fh', 'ctr', 'mode', 'fam', 'gen'], {
   ('fam', 'trail'): 'the family method has no input difference to propagate',
   ('ctr', 'sym'): IVROW, ('mode', 'sym'): IVROW, ('fh', 'sym'): IVROW,
   ('ctr', 'canc'): 'both messages share t: no extra difference to cancel (METHOD_NOTE M4)',
   ('fam', 'cost'): 'cost saves at most log2(430) = 8.7 bits; best family form is 144 (I4)',
   ('gen', 'cost'): 'cost saves at most 8.7 bits; best generic form is 144 (T8)'}),
 ('layer', ['r0', 'r1c', 'r1d', 'fold', 'mode', 'all'], {
   ('mode', 'sym'): IVROW,
   **{('r0', t): 'round 0 is solved exactly by its cheap inverse (C4, T3): nothing there to search' for t in ['trail', 'join', 'alg', 'heur']}}),
]

def build(rows):
    live = [r for r in rows if r['status'] in ('alive', 'dead', 'open') and r['base'] != 'r1']
    out_cells, md = [], []
    for rowax, rvals, imp in GRIDS:
        cells = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in live:
            if r['tech'] in TECH and r[rowax] in rvals:
                cells[(r[rowax], r['tech'])][r['status']].append(r['id'])
        md.append('\n## Grid: %s x tech\n' % rowax)
        md.append('| %s \\ tech | ' % rowax + ' | '.join(TECH) + ' |')
        md.append('|---' * (len(TECH) + 1) + '|')
        for rv in rvals:
            line = []
            for t in TECH:
                c = cells[(rv, t)]; a, d, o = c['alive'], c['dead'], c['open']
                n = len(a) + len(d) + len(o)
                if a: mk, txt = 'tried-alive', 'A %d/%d' % (len(a), n)
                elif d: mk, txt = 'tried-dead', 'D %d' % n
                elif (rv, t) in imp: mk, txt = 'impossible', 'X'
                elif o: mk, txt = 'untried', 'o %d' % len(o)
                else: mk, txt = 'untried', '.'
                line.append(txt)
                out_cells.append({'grid': rowax + 'xtech', 'row': rv, 'col': t, 'mark': mk,
                                  'alive': ' '.join(a), 'dead': ' '.join(d), 'open_logged': ' '.join(o),
                                  'reason': imp.get((rv, t), '') if mk == 'impossible' else ''})
            md.append('| **%s** | ' % rv + ' | '.join(line) + ' |')
        reasons = collections.OrderedDict()
        for (rv, t), why in imp.items():
            reasons.setdefault(why, []).append('%s x %s' % (rv, t))
        md.append('\nX reasons:')
        for why, cs in reasons.items():
            md.append('- %s: %s.' % (', '.join(cs), why))
    return out_cells, md

def main():
    rows = load()
    with open(os.path.join(HERE, 'records.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
        for r in rows: w.writerow({k: r[k] for k in COLS})
    cells, md = build(rows)
    with open(os.path.join(HERE, 'cells.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(cells[0])); w.writeheader(); w.writerows(cells)
    st = collections.Counter(r['status'] for r in rows)
    mk = collections.Counter((c['grid'], c['mark']) for c in cells)
    head = ['# GRIDS: tried and untried combinations', '',
            'Built by build.py from records.csv (%d records: %s). Grids use the 2-round records with status alive, dead or open'
            % (len(rows), ', '.join('%s %d' % kv for kv in sorted(st.items()))),
            '(tools, concerns and the 1-round track are left out). Cell text: `A a/n` tried-alive (a alive of n), `D n` tried-dead,',
            '`o n` untried but n ideas logged (never run), `.` untried, `X` impossible or provably no gain (reason under the grid).',
            'Record ids per cell: cells.csv. Axis codes: AXES.md. In the layer grid most `.` cells come from methods coded `all`',
            '(no single layer); GAPS.md ranks only the untried cells that have a mechanism.', '',
            'Marks per grid: ' + '; '.join('%s %s %d' % (g, m, n) for (g, m), n in sorted(mk.items()))]
    with open(os.path.join(HERE, 'GRIDS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(head + md) + '\n')
    for c in cells:
        if c['mark'] == 'untried':
            print('UNTRIED', c['grid'], c['row'], c['col'], c['open_logged'])
    print(dict(st))

main()
