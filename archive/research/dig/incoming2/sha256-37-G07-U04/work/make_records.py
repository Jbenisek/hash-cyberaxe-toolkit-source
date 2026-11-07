import json, os
here = os.path.dirname(os.path.abspath(__file__))
t = json.load(open(os.path.join(here, 'main_result.json')))
R = t['rows']

def row(k):
    v = R[k]
    return "%s charged %.2f, raw %.1f (se %.1f), CV-adjusted %.2f (se %.3f, 99%% CI %.2f..%.2f) -> %s" % (
        k, v['charged'], v['raw'], v['raw_se'], v['cv'], v['cv_se'], v['cv_lo'], v['cv_hi'], v['cv_verdict'])

rows_txt = "; ".join(row(k) for k in ['v_scan', 'v_pass', 'v_grp', 'v_surv', 'v_rare', 'v_tot'])
EV = ("research/dig/incoming2/sha256-37-G07-U04/work/ (PREREG.txt, run_main.py, analyze.py, main.csv, main_result.json, "
      "ctrl_*.csv/json, sens.json, lowm.py = copy of research/tools/build_pkg/scratch/pkgR37M3/pkg/sha256-r37/experiments/lowm.py sha256 63c14c31)")
base = dict(hash='sha256-37', row_i=None, row_j=None, source='our workflow: scan-once-wave2', own_test=True,
            date='2026-10-12', evidence=EV)
recs = {}
L = 'sha256-37|LEDGER.LM3|LEDGER|'
J = 'sha256-37|JUDGE.JH1H3|JUDGE|'

recs[L + 'R1'] = dict(
    object='LEDGER.LM3 staged R37M3 lowm.py ledger: value charged',
    question='R1: value charged or stated and where (exact line)', labels=['N'], status='COMPUTED',
    number=('charged: FIXED 615 ops per first block (first block + control 46, class test 397, scalars and planes 172) + vbar 46,070.09 '
            'data-dependent ops (class scans 21.14, passing classes 24,666.75, groups 16,269.77, survivors 4,879.12, row-16 hits 233.31); '
            'N_FB 60,951,875,249,131,685; V_MAX 2,808,743,648,446,227,477,989; vmax_fb 94,072,525,785; time_log2 60.99099 (2^60.990989)'),
    topic='sha256-37 LEDGER.LM3 charged', gain_bits=None, lever=False, gain_basis=None,
    notes=("universe cell @@R1. Read: pkgR37M3 proof.md L23-24 (cost summary), L607 (work cap), L615-L634 (ledger block), L669 (scope of the 46070.09), "
           "L810 (CPREP, CF_CLASS, SWEEP_OVH, FIXED, RUN_CU, SPILL = 410, 6, 195, 615, 7, 64), L892; claim.json restrictions 'Cost'; reproduced by running "
           "lowm.py ledger() here: g 830.98816872, vbar 46070.08522563, time_log2 60.99099, integer tightness asserted. Exact arithmetic of the shipped "
           "program's own closed formulas; the vbar rows are expectations under H1 (exact for scans/classes/survivors/hits, an upper bound for the "
           "group-count ceil, see R2).").replace('@@', L))

recs[L + 'R2'] = dict(
    object='LEDGER.LM3 metered run of the shipped program (best case executed)',
    question='R2: own re-measurement: metered run of the shipped program, fresh seeds, preregistered rule, control arm',
    labels=['N'], status='SAMPLED',
    number=("94,805 real first blocks (all 222 classes, shipped process_cv meter, seed 'scanonce-wave2|G07U04|main'), rule PREREG.txt: fixed part exactly 615 "
            "on all 80,602 blocks without a passing class (min total 615); data-dependent mean raw 46,395.5 (se 651.7) vs charged 46,070.09: COVERED; "
            "control-variate adjusted (exact class and pair moments) 46,063.04 (se 48.39, 99%% CI 45,938.4..46,187.7): COVERED (-7.05). Rows: " + rows_txt +
            ". Excess charge on 3 rows (ceil bound for groups, 4*groups probed lanes for survivors and hits): 65.28 + 20.15 + 5.55 = 91.0 ops per block "
            "(sampled, CV-adjusted; 99%% CIs +-0.03, +-4.9, +-3.1).").replace('%%', '%'),
    topic='sha256-37 LEDGER.LM3 metered', gain_bits=0.00132, lever=True, gain_basis='T',
    notes=("universe cell @@R2. Method: own copy of lowm.py, no checks, no early stop, one stream of fresh seeds, rule written before the run (PREREG.txt). "
           "Blocks are overdispersed (variance/mean of good pairs 23,046; only 15% of blocks have a passing class), so the raw total has se 1.4%; the "
           "control-variate estimator regresses on the exact E[classes]=3.5229 and E[pairs]=830.988 (tests the ledger arithmetic given H1 moments; H1 "
           "itself is tested in the JUDGE cells). Passing classes row +83.95 ops vs charged is inside the CI (z 1.74), not a finding. The three OVER rows "
           "are bounds by construction: groups charged (g+3)/4 groups (true mean groups 207.75 = g/4: members come in cube multiples so N mod 4 is mostly 0 "
           "and the ceil padding is almost never paid), survivors and hits charged for g+3 lanes. Candidate slack 91.0 ops/block x 1.4514e-5 = 0.00132 bit "
           "if the exact E ceil(N/4) were derived and charged; NOT built or proved, one measurement only. The 25 min run used 1 process.").replace('@@', L))

recs[L + 'R3'] = dict(
    object='LEDGER.LM3 meter-vs-ledger comparator control',
    question='R3: control: same tool on a known answer / negative control that must fail', labels=['N'], status='COMPUTED',
    number=("negative control: same seeds, first 4,000 blocks, GROUP_BODY patched 31 -> 32 in the meter only: groups row CV 16,412.24 (se 0.049) vs charged "
            "16,269.77 -> UNDER (+142.47); unpatched meter on the same 4,000 blocks: 16,204.49 -> OVER (-65.28); difference 207.75 ops = groups per block, "
            "as it must be. Total row stays COVERED in both arms at n=4,000 (se 257): power limit stated. Known answers: fixed 615 on 80,602 of 80,602 "
            "no-pass blocks; ledger() reproduces time_log2 60.99099"),
    topic='sha256-37 LEDGER.LM3 control', gain_bits=None, lever=False, gain_basis=None,
    notes=("universe cell @@R3. The row-level comparator detects a 1-op-per-group error (0.45% of vbar, 0.003 bit) at 4,000 blocks; the total-row "
           "comparator detects only about +-0.27% (125 ops) even at 94,805 blocks, so a ledger error below about 125 ops (0.0018 bit) hidden inside "
           "one row is visible only row-wise.").replace('@@', L))

recs[L + 'R4'] = dict(
    object='LEDGER.LM3 score sensitivity',
    question='R4: score sensitivity in bits per unit and slack candidates', labels=['N'], status='COMPUTED',
    number=("1 op per first block (fixed or data-dependent) = 1.4514e-5 bit of time_log2 (exact ledger, share of T that scales with N_FB 0.4964); "
            "GROUP_BODY +1 (208.5 ops) = 0.003018 bit; SCAN_LANE +1 (414.3 ops) = 0.005991 bit; SURV_FIX +1 (75.6 ops) = 0.001095 bit; PAD_OPS +1 (1 op) = "
            "1.45e-5 bit; A_C 2^60 -> 2^59 = -0.4181 bit; slack candidates (R2, sampled): groups 65.28 ops = 0.000948 bit, survivors 20.15 = 0.000292, "
            "row-16 hits 5.55 = 0.0000805; sum 91.0 ops = 0.00132 bit"),
    topic='sha256-37 LEDGER.LM3 sensitivity', gain_bits=0.00132, lever=True, gain_basis='T',
    notes=("universe cell @@R4. All from lowm.ledger() with patched constants (sens.py, sens.json); values are bits of time_log2 before the 5-decimal "
           "ceiling. The V_MAX cap slack (1+2^-12) is worth about 1.6e-4 bit (analytic: V share of T 0.46 x 2^-12 x 1.4427) but is tied to the Chebyshev "
           "cap premise, not free. pre_ops (2^38) is below the 5th decimal. The candidate slack is the same 0.00132 bit as in R2, not an additional one.").replace('@@', L))

recs[J + 'R1'] = dict(
    object='JUDGE.JH1H3 NOT_EVALUABLE cause: H1 uniform CV + H3 first-block dependence, present in staged R37M3',
    question='R1: is the cause present in the current package (exact line)', labels=['N'], status='COMPUTED',
    number=("present: yes. R37M3 claim.json heuristics H1-uniform-chaining-values and H3-first-block-dependence are score-critical with the same support type "
            "as the rulings b43280d0 (R37X, 60.17144) and b74a016c (R37c, 61.4877): inherited 7319bba runs on at most 2^23 first blocks (H1: 2^21 and 2^23 first "
            "blocks, row-16 z +0.88 and +0.51; H3: factor 0.98 / 1.00; replay of 19,620,436 successes, 0 further) plus a 50,000-block simulation of the counted "
            "program (46,965 vs 46,685); R37M3 limitation text: H3 margin thin (delta <= 2^-9.68 vs 2^-9.4). Rulings: b43280d0 lane_evaluability H1 and H3 "
            "unsupported (finding F-EVAL-001: support is participant-reported or inherited, a0-online-r37 expressly does not test H1 at scale or H3); "
            "b74a016c lane_evaluability H3 unsupported, H1 plausible"),
    topic='sha256-37 JUDGE.JH1H3 present', gain_bits=None, lever=False, gain_basis=None,
    notes=("universe cell @@R1. Read: research/dossiers/b43280d0/judge-dossier.json (lanes exploratory and rigorous not_evaluable, reasons "
           "lane_evaluability/heuristic/H1 and H3), research/dossiers/b74a016c/judge-dossier.json, FILINGS.md L50 and L81, pkgR37M3 claim.json heuristics "
           "H1 and H3. The organizer experiments in R37M3 are the same a0-sfs-r37 / a0-online-r37 types whose scope text says they do not test H1 at scale "
           "or H3, so the cause is still present in the package. Passing parent dossiers (ffbe30bb, f2fe1d4d) are not in research/dossiers: not read.").replace('@@', J))

H1txt = ("H1 fresh run (94,805 real first blocks): passing classes per block mean 3.4828 vs exact 3.5229 (z -1.24); good pairs 842.51 vs 830.99 (z +0.81); "
         "variance/mean of pairs 23,046; blocks with a passing class 15.0% (80,602 with none)")
recs[J + 'R2'] = dict(
    object='JUDGE.JH1H3 margin numbers measured on the staged R37M3 program',
    question='R2: margin number measured on the current package (statistic)', labels=['N'], status='SAMPLED',
    number=(H1txt + ". H3(b) row-16 level factor F = [sum r(r-1)/sum N(N-1)]/[sum r/sum N]^2 = 1.0180 (batch se 0.0096, 99% CI 0.993..1.043; 38,146 row-16 "
            "hits in 5,832 blocks), proof states 0.98 and 1.00 against a premise margin of 2^35. Largest check here 94,805 first blocks (2^16.5), vs 2^23 "
            "inherited and 2^55.76 used"),
    topic='sha256-37 JUDGE.JH1H3 margin', gain_bits=None, lever=False, gain_basis=None,
    notes=("universe cell @@R2. Same run as LEDGER.LM3 R2 (main.csv). Rule written first (PREREG.txt): |z|<2.576 passes the H1 moments; the F CI must cover 1. "
           "Both pass. This does NOT discharge the judge's cause: it is a participant measurement of the same kind (the judge asks for organizer-executed "
           "evidence); H3(a) (other l of the same variant) and full-path successes (q3 about 2^-71.47) cannot be observed here. The overdispersion the "
           "judge named reproduces: only 15% of blocks carry any passing class.").replace('@@', J))

recs[J + 'R3'] = dict(
    object='JUDGE.JH1H3 check fired on failing and passing cases',
    question='R3: check fired on the known failing dossier and a passing one', labels=['N'], status='COMPUTED',
    number=("H1 moment test: source with low 12 bits of x zeroed (6,000 blocks) -> classes z +5.43, pairs z +3.08 (flagged); real source z -1.24 (pass); "
            "NOT detected: x top bit forced to 1 (6,000 blocks, classes z -0.24, pairs +0.24: power limit). F test: independent control (r ~ Binomial(N,p) given "
            "real N) F 0.995 (se 0.0064) pass; pair-clustered control (hits in twin lanes) F 1.0887 (se 0.0115) flagged; real 1.018 (se 0.0096) pass. Judge "
            "side: b43280d0 lane_evaluability H1 and H3 unsupported (fail) vs b74a016c lane_evaluability H1 plausible (pass for H1)"),
    topic='sha256-37 JUDGE.JH1H3 control', gain_bits=None, lever=False, gain_basis=None,
    notes=("universe cell @@R3. Controls built from the same run (ctrl_bias*.csv, analyze.py). A passing dossier for H3 was not found: both stored dossiers "
           "have H3 unsupported in lane_evaluability. The moment test cannot see an x top-bit bias, so it is no test of uniformity of every bit of x.").replace('@@', J))

recs[J + 'R4'] = dict(
    object='JUDGE.JH1H3 distance to threshold and score sensitivity',
    question='R4: distance to the threshold (bits)', labels=['N'], status='COMPUTED',
    number=("H3 bound delta <= 2^-11 + 2^-10.42 = 1.218e-3 = 2^-9.681 vs the used 2^-9.4 (1.516e-3): 0.28 bit (factor 1.24) to the threshold; score cost of the "
            "Bonferroni term itself: (1-2^-10.4) -> (1-2^-9.4) would cost 0.00053 bit; H1: good pairs g enters N_FB as 1/g: 1% in g = 0.00713 bit (measured "
            "+1.39% excess is z +0.81, not significant, would be 0.0099 bit); q3 one bit lower costs +0.58 bit (proof.md L634)"),
    topic='sha256-37 JUDGE.JH1H3 distance', gain_bits=None, lever=False, gain_basis=None,
    notes=("universe cell @@R4. Shares from the ledger: the N_FB part of T is 0.4964. The judge cause is about evidence (evaluability lane), so the distance to "
           "the threshold is in evidence terms (organizer-executed runs: none so far for H1 at scale or for H3), not bits.").replace('@@', J))

for cid, r in recs.items():
    rec = dict(base)
    rec.update(r)
    fn = cid.replace('|', '_') + '.json'
    json.dump(rec, open(os.path.join(here, '..', fn), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(fn)
