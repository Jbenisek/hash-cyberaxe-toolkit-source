
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

import json, os, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G04-U02')
W = 'research/dig/incoming2/sha256-37-G04-U02/work/'
EV = W + 'scan.c, ' + W + 'dep.out, ' + W + 'bucket0.out, ' + W + 'bucket1.out, ' + W + 'bucket2.out, ' + W + 'bucket3.out, ' + W + 'bucket4.out, ' + W + 'real.out (head: retest/close37/job5/job5.c helpers); ' + 'research/retest/close37/job5/RESULT.md (E_-4 bucket, 2^31 pairs)'
SRC = 'our workflow: scan-once-wave2'
RAW = ('Own code scan.c (job5.c helpers + traillab library, validated first: Lemma 4.1 map reproduces the published W0..W7; '
       'our R16 table rebuilt = 1,052,672 (u,l) pairs / 1,042,240 distinct u / 28 of 32 l nonempty). ')
DEP = ('Dependency matrix (20,000 random (CV, a0 in G) with one CV word redrawn; entries are exactly 0.0000 or 1.0000, as the algebra '
       'W_i = A_i - T2_i - E_{i-4} - S1(E_{i-1}) - CH(E_{i-1},E_{i-2},E_{i-3}) - K_i, E_i = A_{i-4} + A_i - T2_i predicts; A_{i-4} cancels in W_i): '
       'E_-4 -> W0 only; E_-3 -> W0,W1; E_-2 -> W0..W2; E_-1 -> W0..W3; A_-4 -> W1..W4 (not W0, not W5..W7); A_-3 -> W0..W5; A_-2 -> W0..W6; A_-1 -> W0..W7. '
       'Partner of each word (the W it is a bijection onto with the other 7 words held): E_-4->W0 E_-3->W1 E_-2->W2 E_-1->W3 A_-4->W4 A_-3->W5 A_-2->W6 A_-1->W7; '
       'checked injective on 4 x 2^22 distinct input values per word (all outputs distinct). ')
GATE = 'The two gates (W7x in F7, W6x in F6) read only A_-1 and (A_-2, A_-1); no other CV word enters them. '
recs = []
def add(cid, row_i, obj, q, labels, status, number, notes, basis='count'):
    recs.append(dict(hash='sha256-37', row_i=row_i, row_j=None, object=obj, question=q, labels=labels, status=status, number=number,
        source=SRC, own_test=True, evidence=EV, date='2026-10-12', lever=False, gain_bits=0.0, gain_basis=basis,
        notes='universe cell ' + cid + '. ' + RAW + notes))
BK = {'A3': ('A_-3', 'hi8 chi2 241.4 (255 dof) p 0.72, max bucket ratio 1.0554 min 0.9506; low8 chi2 219.4 p 0.95, max 1.0676 min 0.9516'),
      'A4': ('A_-4', 'hi8 chi2 253.4 (255 dof) p 0.52, max bucket ratio 1.0619 min 0.9403; low8 chi2 271.9 p 0.22, max 1.0637 min 0.9250')}
# ---------------- A_-3
add('sha256-37|CV.A-3|CV|Q1', -3, 'CV word A_-3 (enters E0 via MAJ and E1 = A_-3 + A1 - T2_1) as the attack uses it',
    'Count / size of A_-3 as the ordinary collision uses it (which words and gates read it)',
    ['D', 'I', 'N'], 'COMPUTED',
    'A_-3 reaches W0..W5 (6 of 8 words), never W6/W7; partner W5 (injective); every one of the 2^32 values passes the gates; real first blocks uniform (2^29.00 blocks)',
    DEP + GATE + 'So A_-3 is one of the six words (A_-3, A_-4, E_-4..E_-1) that Lemma 4.1 maps bijectively onto (W0..W5); it carries 32 bits and no condition. '
    'Real first blocks CV = F_37(IV, M0), 536,669,149 blocks: A_-3 hi8 chi2 244.1 (255 dof) p 0.68, low8 222.7 p 0.93; among the 569,856 gate-passing blocks hi8 p 0.58, low8 p 0.44; '
    'gate rate 2^-9.8792 [2^-9.8830, 2^-9.8755] vs exact 2^-9.8796. Window: dependency measured on the Lemma 4.1 map (rows 0..13 words), not on rows 14..36.')
add('sha256-37|CV.A-3|CV|Q2', -3, 'CV word A_-3: drop or pin it',
    'Necessity of A_-3: pin it to a constant and recompute the row-16 event and the W4/W5 marginals',
    ['D', 'I', 'N', 'Z'], 'LOCAL_ONLY',
    'A_-3 pinned (a4299297, then 0), other five free words random, 2^29.00 good pairs each: row-16 any-l 2^-12.0158 [2^-12.0236, 2^-12.0079] and 2^-12.0114 [2^-12.0192, 2^-12.0035] vs table 2^-12.0087; W4,W5 per-group marginals uniform (chi2 p 0.07..0.93, 8 tests)',
    'Pinning changes nothing measurable in the row-16 event or the W4/W5 marginals (W5 = f(A_-1,A_-2,a0) - A_-3 stays uniform over the gate sample). The value is not individually necessary; '
    'the six-word block is jointly necessary (6 words for W0..W5): removing A_-3 as a free word leaves 5 words for 6 W-words, and forcing a given A_-3 from a real first block costs 2^32 hashes of M0, so no saving. '
    'LOCAL_ONLY: checked on rows 0..16 and the W4,W5 marginals only; rows 17..36 with a pinned word were not run (the row-17 factor 2^-13 is from job5, with W17 uniform via E_-3).', 'q3')
add('sha256-37|CV.A-3|CV|Q3', -3, 'CV word A_-3: log2 freedom left and row-16 pass rate by A_-3 bucket',
    'Freedom left in A_-3 after the gates (exact) and homogeneity of the row-16 pass by A_-3 value (sampled)',
    ['D', 'N', 'Z'], 'LOCAL_ONLY',
    'freedom 32.00 bits (exact: gates do not read A_-3); row-16 any-l rate 2^-12.0066 [2^-12.0105, 2^-12.0027] on 2,147,549,184 good pairs (table 2^-12.0087); by-bucket homogeneity ' + BK['A3'][1],
    'Forward model (Lemma 4.1 map, a0 walks G, F7/F6 by rejection, K=256 draws of the other six words per good (a0,A_-1,A_-2); seed 7370401), ~8.4M good pairs and ~2,040 passes per bucket of 256. '
    'No steering: spread is the ordinary maximum over 256 buckets. Gain 0. Window rows 0..16.', 'q3')
add('sha256-37|CV.A-3|CV|Q4', -3, 'CV word A_-3: alternatives',
    'Alternatives to a random A_-3: pre-selecting first blocks by A_-3, other sources of the W5 freedom',
    ['D', 'I', 'N', 'Z'], 'LOCAL_ONLY',
    'no alternative found: bucket steering flat (see Q3), pinning neutral (see Q2); A_-3 is the W5-coordinate, choosable only by a free-start attacker; gain 0',
    'Because A_-3 <-> W5 is a bijection (injective on 4 x 2^22 inputs), choosing A_-3 would equal choosing W5, which an ordinary collision cannot do (CV = F_37(IV, M0) is drawn, not chosen). '
    'Selecting first blocks by A_-3 bucket would need the row-16 rate to differ by bucket; it does not (chi2 p 0.72 / 0.95). Window rows 0..16 plus W4,W5 marginals.', 'q3')
# ---------------- A_-4
add('sha256-37|CV.A-4|CV|Q1', -4, 'CV word A_-4 (enters only E0 = A_-4 + A0 - T2_0) as the attack uses it',
    'Count / size of A_-4 as the ordinary collision uses it (which words and gates read it)',
    ['D', 'I', 'N'], 'COMPUTED',
    'A_-4 reaches W1..W4 only (not W0, not W5..W7); partner W4 (injective); no gate reads it; 32 bits; real first blocks uniform',
    DEP + GATE + 'A_-4 enters only through E0 = A_-4 + A0 - T2_0: nonlinearly into W1..W3 (S1(E0), CH) and linearly into W4 (term -E0). It does not touch W0, so the row-16 lookup u = W0 + s0(W1) sees A_-4 only through W1. '
    'Real first blocks (536,669,149): A_-4 hi8 chi2 232.8 (255 dof) p 0.84, low8 278.7 p 0.15; gate-passing (569,856) hi8 p 0.71, low8 p 0.32. Window: Lemma 4.1 map.')
add('sha256-37|CV.A-4|CV|Q2', -4, 'CV word A_-4: drop or pin it',
    'Necessity of A_-4: pin it to a constant and recompute the row-16 event and the W4/W5 marginals',
    ['D', 'I', 'N', 'Z'], 'LOCAL_ONLY',
    'A_-4 pinned (4e8c576e), other five words random, 2^29.00 good pairs: row-16 any-l 2^-12.0043 [2^-12.0121, 2^-11.9965] vs table 2^-12.0087; W4,W5 marginals uniform (p 0.54..0.75)',
    'Not individually necessary (E0 stays uniform via the other words that enter it); jointly one of the six words that map onto (W0..W5). Pinning from a real first block costs 2^32 hashes. '
    'LOCAL_ONLY: rows 0..16 and W4,W5 marginals; rows 17..36 with the pinned word not run.', 'q3')
add('sha256-37|CV.A-4|CV|Q3', -4, 'CV word A_-4: log2 freedom left and row-16 pass rate by A_-4 bucket',
    'Freedom left in A_-4 after the gates (exact) and homogeneity of the row-16 pass by A_-4 value (sampled)',
    ['D', 'N', 'Z'], 'LOCAL_ONLY',
    'freedom 32.00 bits (exact: gates do not read A_-4); row-16 any-l rate 2^-12.0066 [2^-12.0105, 2^-12.0027] on 2,147,549,184 good pairs; by-bucket homogeneity ' + BK['A4'][1],
    'Same run as the A_-3 cell (seed 7370401, forward model). No steering; gain 0. Window rows 0..16.', 'q3')
add('sha256-37|CV.A-4|CV|Q4', -4, 'CV word A_-4: alternatives',
    'Alternatives to a random A_-4: pre-selecting first blocks by A_-4, other sources of the W4 freedom',
    ['D', 'I', 'N', 'Z'], 'LOCAL_ONLY',
    'no alternative found: bucket steering flat, pinning neutral; A_-4 is the W4-coordinate (free-start only); gain 0',
    'A_-4 <-> W4 is a bijection (injective on 4 x 2^22 inputs); W0 does not depend on A_-4, so no coordinate of the first block moves the row-16 key u = W0 + s0(W1) independently of W1. '
    'Bucket homogeneity p 0.52 / 0.22. Window rows 0..16 plus W4,W5 marginals.', 'q3')
# ---------------- E_-4
add('sha256-37|CV.E-4|CV|Q1', -4, 'CV word E_-4 as the attack uses it',
    'Count / size of E_-4 as the ordinary collision uses it (which words and gates read it)',
    ['D', 'I', 'N'], 'COMPUTED',
    'E_-4 reaches W0 only (W0 = f - E_-4, partner W0, injective); no gate reads it; 32 bits; real first blocks uniform',
    DEP + GATE + 'E_-4 is a pure additive shift of W0 and so of the row-16 key u = W0 + s0(W1). Real first blocks (536,669,149): E_-4 hi8 chi2 264.6 (255 dof) p 0.33, low8 236.6 p 0.79; '
    'gate-passing (569,856) hi8 p 0.14, low8 p 0.74. The earlier per-bucket row-16 test of this word is research/retest/close37/job5 (2^31 good pairs, p 0.035 / 0.91); not repeated. Window: Lemma 4.1 map.')
add('sha256-37|CV.E-4|CV|Q2', -4, 'CV word E_-4: drop or pin it',
    'Necessity of E_-4: pin it to a constant and recompute the row-16 event and the W4/W5 marginals',
    ['D', 'I', 'N', 'Z'], 'LOCAL_ONLY',
    'E_-4 pinned (418d9ce7), other five words random, 2^29.00 good pairs: row-16 any-l 2^-12.0101 [2^-12.0179, 2^-12.0023] vs table 2^-12.0087; W4,W5 marginals uniform (p 0.44..0.96)',
    'Not individually necessary for the event, but E_-4 is the only word that moves W0 alone: with it pinned, W0 is set by the other words (A_-3, E_-3.., A_-1, A_-2, a0) and stays uniform. Pinning from a real first block costs 2^32 hashes. '
    'LOCAL_ONLY: rows 0..16 and W4,W5 marginals.', 'q3')
add('sha256-37|CV.E-4|CV|Q4', -4, 'CV word E_-4: alternatives',
    'Alternatives to a random E_-4: pre-selecting first blocks by E_-4, other sources of the W0 shift',
    ['D', 'I', 'N', 'Z'], 'LOCAL_ONLY',
    'no alternative found: pinning neutral (row-16 2^-12.0101), job5 bucket flat, E_-4 is the W0-coordinate (free-start only); gain 0',
    'E_-4 <-> W0 is a bijection; the a0 variants already supply an independent family of shifts of the row-16 key (counted elsewhere). Window rows 0..16.', 'q3')
os.makedirs(OUT, exist_ok=True)
ex = add_cell.load(); bad = 0
for r in recs:
    cid = r['notes'].split('. ',1)[0].replace('universe cell ', '')
    fn = os.path.join(OUT, cid.replace('|', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    e = add_cell.validate(json.load(open(fn, encoding='utf-8')), ex)
    print(os.path.basename(fn), 'OK' if not e else e); bad += bool(e)
print(len(recs), 'records', bad, 'bad')
