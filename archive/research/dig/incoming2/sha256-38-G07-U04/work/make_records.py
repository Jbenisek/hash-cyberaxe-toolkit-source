
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
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G07-U04')
W = 'research/dig/incoming2/sha256-38-G07-U04/work/'
PK = 'research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/'
EV_L = '; '.join([W + 'g07_ledger.py', W + 'g07_ledger.out.txt', W + 'g07_ledger.json', W + 'g07_meter.py', W + 'g07_meter.json', W + 'g07_nohit.out.txt', W + 'g07_w7check.out.txt', PK + 'experiments/a0lean38.py', PK + 'proof.md (Sections 9, 11)', PK + 'claim.json'])
EV_J = '; '.join([W + 'g07_judge.py', W + 'g07_judge.json', 'research/dossiers/1393e83b/judge-dossier.json', 'research/dossiers/cfeb996a/judge-dossier.json', PK + 'claim.json', 'research/FILINGS.md'])
base = dict(hash='sha256-38', row_i=None, row_j=None, labels=[], source='our workflow: scan-once-wave2', own_test=True, date='2026-10-12')
R = []


def add(cell, obj, q, status, number, ev, notes, lever=False, gain=None, basis=None, topic=None):
    r = dict(base)
    r.update(id=cell, object=obj, question=q, status=status, number=number, evidence=ev, lever=lever, notes='universe cell ' + cell + '. ' + notes)
    if gain is not None:
        r['gain_bits'] = gain
        r['gain_basis'] = basis
    if topic:
        r['topic'] = topic
    R.append(r)


L = 'staged R38M3 a0lean38 ledger (35 fixed + vbar 132,300.19)'
add('sha256-38|LEDGER.LM3|LEDGER|R1', L, 'R1: value charged or stated (exact line)?', 'COMPUTED',
    'EXACT as charged (proof.md Section 9/11, Appendix B): per first block 35 fixed ops + vbar 132,300.1864 data-dependent ops = W7 tests 1497.66 + hit list 12.041 + scalars and planes 278.94 (920 x Pr[some class passes]) + plane programs 128,796.72 + passing lanes 1714.3396 + row-16 passes 0.48729 (g 2^-27 x 2829); N_FB 5,840,904,760,525,073,226,269,327 (2^82.27247); V_MAX 772,764,579,970,529,091,929,220,381,051; class max 12,113,647; allowances A_C 2^78, A_S 2^74, DEV 2^64; PRE 4,515,430,400; N 789779068018615953003308365799; time_log2 87.90374 (claim.json 87.90374).',
    EV_L, 'Reading of the charged line only; the same numbers regenerate from the shipped program in R2 (identical N). The ledger charges the passing-lane term at the per-shape MAXIMUM lane cost (296/308/320), not the mean (see R4).')
add('sha256-38|LEDGER.LM3|LEDGER|R2', L, 'R2: own re-measurement or metered recount (fresh seeds, rule before the run, control arm)?', 'COMPUTED',
    'EXACT recount: running the shipped a0lean38.py calibrate+ledger in WSL reproduces N = 789779068018615953003308365799, vbar 132300.1864, V_MAX, certificate 2^8790373 x 2728^100000 <= N^100000 < 2^8790374 x 2728^100000, time_log2 87.90374 (log2(N/C) 87.9037359544): zero difference. METERED (SAMPLED, fresh seed 20261012, 17,945 random first blocks through the shipped process_fb, check off): mean ops minus the 35 fixed = 130,276.9 +- 1,700.1 (1 se) against charged 132,300.19 (z -1.19; the sample mean is 1.5% below the charge, in the direction of the lane-max slack in R4). Exact identities in the metered run: 1,500 of 1,500 no-hit first blocks cost exactly 35 + sum of the 90 W7 tests + 4 per class; 42,079 of 42,079 classes with no passing lane cost exactly 7 + 15 x (program + 6) ops (0 mismatches); hit fraction 0.2995 (exact Pr[some class passes] = 0.30295); 5.948 passing classes per first block (expected 6.0205); 99,512 passing lanes costing 219.54 / 227.35 / 235.34 ops each by shape (charged max 296 / 308 / 320); row-16 passes 5 (about 3.1 expected).',
    EV_L, 'Rule written before the run (g07_meter.py header): the no-lane class identity exact; mean within 3 sigma of vbar. Both held. The header rule 3 (w7-phase mean vs 1497.66) was mis-specified by me (hit-list appends and the hook point are mixed into the estimate) and read z +7.7; it was replaced by two cleaner checks that both pass: the exact no-hit identity above and an independent mean of the W7 term on 20,000 real chaining values x 90 classes = 1497.486 (charged 1497.66; the exact 20-bit distribution mean 12.640625 against 400,000 random 32-bit words 12.6489 +- 0.0096). The metered run uses the Python counting machine (Mach) of the shipped program, so it recounts the program as charged, not a physical CPU.')
add('sha256-38|LEDGER.LM3|LEDGER|R3', L, 'R3: control (same tool on a known answer / negative control)?', 'COMPUTED',
    'PASS. Known answers: (a) the ledger tool with A_C = 2^84 returns 87.99563 (+0.091894 over base), the value printed in proof.md Section 11; (b) the HIT0 constant: the hits.out histogram over A_{-1} gives 2,992,758,256 zero-hit values, the number in the ledger; (c) the metered counter reproduces the calibrated per-class cost exactly on 42,079 lane-free classes and the exact no-hit identity on 1,500 first blocks. Negative control: the pre-run z test against a charge inflated by 5% (1.05 x 1497.66) rejects (z -66), and the one-op perturbations in R4 move the certificate, so the recount is sensitive to the quantities it checks.',
    EV_L, 'Control scope: known answers are the proof\'s own printed rows plus exact identities; no outside implementation was run (own code only). The negative control used the flawed w7-phase estimator of R2 (rule 3), so only its rejection direction is relied on, not its z value.')
add('sha256-38|LEDGER.LM3|LEDGER|R4', L, 'R4: score sensitivity in bits per unit and slack candidates?', 'COMPUTED',
    'EXACT (ledger re-run with one input changed): +1 fixed op per first block +0.000011 bit; +10 scalar ops +0.000032; +10 plane-load ops +0.000032; +1 instruction in every plane program +0.000963; +10 on each lane cost cap +0.000602; +1 op in every W7 test +0.000960; +100 ops in step3b +0.000000; cap margin 2^-16 -> 2^-14 +0.000065; success 0.39 -> 0.40 +0.047403; q3 -1 bit +0.999200; A_C 2^78 -> 2^74 -0.001413, A_C doubled +0.00151, A_C 2^84 +0.091894. SLACK CANDIDATE: the lane term 1714.3396 is charged at the per-shape MAXIMUM lane cost (296/308/320 ops); the exact mean over the 256 lane positions is 219.375 / 227.375 / 235.375 (metered run: 219.54 / 227.35 / 235.34). Charging the mean (rounded up to 220/228/236): lane term 1270.83, time_log2 87.89900, saving 0.00474 bit (exact scan of 256 positions per shape).',
    EV_L, 'One measurement, not chased. The saving applies only if a mean-based expected charge is accepted for the lane term (V_MAX is built from vbar, so the expected value is what enters; the max may have been chosen as a bound on purpose). Rule of the unit: charge what the program executes (best case) supports the mean.',
    lever=True, gain=0.00474, basis='T', topic='sha256-38 R38M3 lane term max vs mean')
J = 'NOT_EVALUABLE: H4a allowance-characteristic-search (R38E 1393e83b, R38N cfeb996a, R38C); package R38M3 carries single-form H4 (A_C 2^78)'
add('sha256-38|JUDGE.JH4A|JUDGE|R1', J, 'R1: is the cause present in the current package?', 'COMPUTED',
    'PRESENT in form. R38M3 claim.json carries one heuristic H4-advice-allowances (role supporting), A_C = 2^78 as a bound by comparison; its limitations text reads "Bounds by comparison, not measurements of the unpublished searches" and the proof cites no metered characteristic-search record (no mention of the metered pair search, Grok 115, 2^31.96 word ops; 0 hits). This is the single-form H4 that was ruled not_evaluable on 1c8889ab, 8bc7d6c5, fc4632b4, fd3ac033, de030a60 and that was eligible on 0ae69bcb and c99df2dc; the split H4a/b/c form was ruled H4a not_evaluable on 1393e83b (cryptanalysis + experiments lanes) and cfeb996a (experiments lane only).',
    EV_J, 'Structural reading of the package and the stored dossiers; the judge itself was not run (not available). R38M3 is staged, not filed.')
add('sha256-38|JUDGE.JH4A|JUDGE|R2', J, 'R2: margin number measured on the current package?', 'COMPUTED',
    'EXACT arithmetic on R38M3: A_C x C / N = 2^78 x 2728 / 789779068018615953003308365799 = 0.0010439 (0.104% of T; preprocessing 2^78.08755 is 0.111% of T). Compare cfeb996a: preprocessing 92.9% of T (A_C 82.8%), 1393e83b: preprocessing 43.8%, c99df2dc: 97.9% (eligible), 0ae69bcb: 34.9% (eligible). A_C at R38M3 is 2^37 times the 593,858 CPU-second predecessor re-run quoted in the proof.',
    EV_J, 'Margin of the stated allowance, not a measurement of the search itself (none exists in the package). Dossier shares use preprocessing_log2 against time_log2 from each dossier claim.')
add('sha256-38|JUDGE.JH4A|JUDGE|R3', J, 'R3: check fired on the known failing dossier and a passing one?', 'COMPUTED',
    'Rule (aggregate reasons list a heuristic/H4* entry not suffixed ": plausible") over the 12 stored r38 dossiers: fires on 7 not_evaluable dossiers (1393e83b, 1c8889ab, 8bc7d6c5, cfeb996a, de030a60, fc4632b4, fd3ac033), silent on the 3 eligible ones (0ae69bcb, c99df2dc, def724e5) and on 3b532546 (other cause) and 426af47b (refuted, other cause). It reads a ruling after the fact; it cannot predict one: the same single-form H4 with the same bound-by-comparison text was eligible on 0ae69bcb and c99df2dc and fatal on five others.',
    EV_J, 'Control is a post-hoc classifier on stored dossiers, so it validates only the reading of rulings. def724e5 (T 124) came through the dossier filter although it is not an H4 target; it has no H4 entry.')
add('sha256-38|JUDGE.JH4A|JUDGE|R4', J, 'R4: distance to the threshold?', 'COMPUTED',
    'No numeric threshold is observable: the preprocessing share of T does not separate rulings (fatal at 13.6%, 25.9%, 35.5%, 43.8%, 52.8%, 52.9%, 92.9%; eligible at 34.9% and 97.9%). R38M3 sits at 0.111%, 122 times below the lowest fatal share (13.6%, 8bc7d6c5). A_C needed for R38M3 to reach a 20% / 39.3% / 82.8% A_C share: 2^85.90 / 2^87.28 / 2^90.17. Score cost of raising A_C in R38M3: +0.00151 bit per doubling, +0.0919 bit at 2^84. The open item is evidence, not size: the dense characteristic derivation stays unmeasured in the package.',
    EV_J, 'Because the ruling does not track the share, a larger allowance is a cheap, partial hedge only; the missing piece in the judge text (EXP-F5 of cfeb996a: no trusted timing or complete resource record for H4a) is not addressed by size. An evidence candidate recorded in LEVERS.md (Grok 115 metered 38-step pair search, 2^31.96 word ops) is not in the R38M3 proof.')
for r in R:
    safe = r['id'].replace('|', '_').replace('.', '_')
    p = os.path.join(OUT, safe + '.json')
    json.dump(r, open(p, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    add_cell.validate(json.load(open(p, encoding='utf-8')), add_cell.load())
    print('ok', p)
