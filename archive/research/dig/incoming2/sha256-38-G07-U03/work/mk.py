
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
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G07-U03')
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig')); import add_cell
base = dict(hash='sha256-38', row_i=None, row_j=None, source='our workflow: scan-once-wave2', own_test=True, date='2026-10-12', lever=False)
EV = 'research/dig/incoming2/sha256-38-G07-U03/work/scan.py, scan_out.json, fresh_t_pre_d.txt, neg_t_pre_d.txt; research/tools/build_pkg/scratch/pkgR38L/work/src/ledger38.py (shipped fdef4bab, vt38.py 1d8880c0d425e475)'
R = []
def rec(cid, obj, q, labels, status, number, notes, **kw):
    r = dict(base); r.update(dict(object=obj, question=q, labels=labels, status=status, number=number, evidence=EV, notes=notes + ' universe cell ' + cid)); r.update(kw); R.append((cid, r))
rec('sha256-38|LEDGER.NG38|LEDGER|R1', 'N_G pair budget at measured 99% limit of base + D7 pairs-in-group', 'R1: exact charged value of delta and N_G in the shipped ledger',
 ['N'], 'COMPUTED', 'shipped (fdef4bab) delta 0.564 -> N_G = 192411962931188556827 = 2^67.38276, time_log2 71.0725 (exact rational ledger). Slope 0.467 bit per unit delta (0.55 to 0.57), N_G log2 slope 1.0019 per unit delta. D7 delta7 = 2491/8499 = 0.29309, CP99 one-sided 0.30473 recomputed (t4 RESULT 0.3047); the D146 prereg bound 0.296687 was not recomputed (its raw counts not re-tallied); t4 raw_A+raw_B lines 72,531+65,449 = 137,980 successes match the table.',
 'Fresh run of the shipped ledger38.py with freshly metered pre1/pre2 (identical to the shipped json). Value of delta in terms of D7: t4 RESULT supports delta = 0.080*delta7 + 0.484 = 0.5077 (near term only; far term 0.484 unmeasured) -> time 71.04689 (-0.0256 bit), or 0.564*delta7 = 0.1673 (needs delta7 to hold for far pairs, NOT measured) -> 70.9189 (-0.1536). wave2_r38.md sec 3 prices D7 at 70.96278 (-0.110), which equals the ledger with delta set to 0.296687 itself; that matches neither supported reading (delta 0.3 gives 70.964). Far-term premise open.',
 gain_bits=None)
rec('sha256-38|LEDGER.NG38|LEDGER|R3', 'N_G pair budget / D7 pairs-in-group control', 'R3: same tool on a known answer or negative control',
 ['N'], 'COMPUTED', 'filed ledger reproduces 71.0725 (log2_T 71.07249038); delta sweep reproduces sens.out of the shipped package: delta 0.5 -> 71.04348, 1 -> 71.33966, 1.5 -> 71.97822 (sens.out 71.97821, 1e-5 print rounding), delta 0 -> 70.86896. t4 control arm: independent-draw proposal 12,113/1,591,808 = 0.007610 = 2^-7.038 vs product model 2^-7 (harness and bit set clean), against near-variant joint 0.293 (38x product).',
 'Control recomputed from retest/t4/control.json and counts; CP bound recomputed with scipy beta.ppf. Negative direction: delta up raises time monotonically (needed). Not re-run: the t4 sampler itself (hours); this cell re-derives only the arithmetic and control rates.')
rec('sha256-38|LEDGER.PREP38|LEDGER|R1', 'preprocessing executed counts (lean derivative R38L)', 'R1: charged preprocessing value',
 ['N'], 'COMPUTED', 'pre_ops = 385844947273092062201164 word ops = 2^66.93874 target-compression units (C=2728); 5.70% of T (2^71.0725); dominant terms log2: P6_fill 77.339, P6_count 76.651, P6_prefix 75.807, P6_zero 73.087, P5_enum 52.494. Bodies charged: P5 setup 37 / body 57 / append 46 / loop 3; P6 zero 34 per 16 headers, count 144 / fill 232 per iteration, 16 / 17 per variant, prefix 6 / 11.',
 'Fresh ledger38.py run on the freshly metered runs.')
rec('sha256-38|LEDGER.PREP38|LEDGER|R2', 'preprocessing executed counts (lean derivative R38L)', 'R2: own metered recount of the shipped program',
 ['N'], 'LOCAL_ONLY', 'fresh run of t_pre_d.py against the shipped vt38.py (sha256 prefix 1d8880c0d425e475, equal to the validated 65,314 B file): pre1.json and pre2.json byte-equal to the shipped runs (all 11 pre2 values and pre1 G_hit 117, F7_in 25, A2_hit 41, LIVE 21 identical). Body-vs-predicate 0 mismatches on 96,000 E17; P6 toy 9 variant runs 946 headers 1188 entries 0 mismatches.',
 'LOCAL_ONLY: counts are per body/iteration of the executed program on toy and window inputs, multiplied by loop counts (2^32 Y values, SR variants, 256 blocks x 2^64 headers) in the ledger; the full 2^64-iteration loops are not run. Nothing found to lower.')
rec('sha256-38|LEDGER.PREP38|LEDGER|R3', 'preprocessing executed counts (lean derivative R38L)', 'R3: control for the metered recount',
 ['N'], 'LOCAL_ONLY', 'negative control fires: the base-bodies tester t_pre_d.orig.py on the shipped program asserts (16 of 16 list words differ from the base entry layout, AssertionError); the shipped tester passes with 0 mismatches and byte-equal json. The aa0496d3 known-answer chain in sens.out (71.335968 -> 71.072490) was not re-derived here because its old pass keys are not on disk.',
 'LOCAL_ONLY as R2 (window inputs). The package base/ directory now holds the levered program (same hash), so the original base program could not be used; the orig tester serves as the negative control.')
rec('sha256-38|LEDGER.PREP38|LEDGER|R4', 'preprocessing executed counts (lean derivative R38L)', 'R4: score sensitivity bits per unit, slack candidates',
 ['N'], 'COMPUTED', 'per +1 executed op: P6 prefix nonempty-header +0.00100 bit, P6 count/fill iteration +0.00017 each, P6 zero16 +0.00006, all P5, P1-P4 terms and per-variant overheads 0.0 (below 1e-5 rounding). Zero preprocessing entirely would save only 0.08462 bit (5.7% of T); round-up slack to 1e-5 is 9.6e-6 bit.',
 'Hard ceiling on any further preprocessing shave: 0.085 bit total; the realistic ones (prefix 11 -> 6 on nonempty headers) are about 0.005 bit. Shaves of this size only matter as ties.')
rec('sha256-38|LEDGER.CAP38|LEDGER|R1', 'cap margin 2^-16 / Bernstein analogue', 'R1: charged cap margin value',
 ['Z'], 'COMPUTED', 'charged eps: N_E 2^-16, N_W 2^-14, N_1 2^-7, N_2 2^-5; cap_overflow_total 2.8995e-06 of the failure budget (success bound exactly 0.39 enforced by an assert). Cap inflation (NG*E*eps) = 7.06e19 ops = +1.5e-5 bit of T; bucket-bound B terms +4e-14 bit. Uniform eps 2^-8 would cost +0.00162, 2^-4 +0.0260, 2^-3 +0.0516.',
 'Matches S38-CAPan (dead < 1e-5 bit); this is the fresh value from the shipped ledger.')
rec('sha256-38|LEDGER.CAP38|LEDGER|R3', 'cap margin 2^-16 / Bernstein analogue', 'R3: control for the Chebyshev cap bound',
 ['Z'], 'COMPUTED', 'toy known-answer: X in {0,B} per group (worst variance), 200,000 reps. NG 1e4, B 10, E 1, eps 0.5: bound 0.004, empirical 0.0; NG 400, eps 0.25: bound 0.4, empirical 0.0433. Bound holds in both. Negative control: eps = 2^-40 makes the overflow term exceed the 0.61 budget and the ledger raises (decimal InvalidOperation) instead of printing a time.',
 'Own toy only; the real law of N_k (rare, heavy-tailed) is not simulated, bounds there rest on the proof Lemma 6 bucket bound B_k.')
for cid, r in R:
    p = os.path.join(D, cid.replace('|', '_').replace('.', '_') + '.json')
    json.dump(r, open(p, 'w', encoding='utf-8'), indent=1)
    try: add_cell.validate(json.load(open(p, encoding='utf-8')), add_cell.load()); print('ok', os.path.basename(p))
    except Exception as e: print('FAIL', cid, e)
