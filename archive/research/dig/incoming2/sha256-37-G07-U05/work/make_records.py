
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
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G07-U05')
W = 'research/dig/incoming2/sha256-37-G07-U05/work/'
PK = 'research/tools/build_pkg/scratch/'
base = dict(hash='sha256-37', row_i=None, row_j=None, labels=[], source='our workflow: scan-once-wave2', own_test=True,
            date='2026-10-12', lever=False, gain_bits=None)


def rec(cell, obj, q, status, number, evidence, notes):
    r = dict(base)
    r.update(id=cell, object=obj, question=q, status=status, number=number, evidence=evidence,
             notes='universe cell %s. %s' % (cell, notes))
    return r


H2o = 'judge cause NOT_EVALUABLE: H2 variant Step-3 probability (+H3, H9) of b74a016c (pkgR37c), checked on the r37 packages'
H2ev = (W + 'jh2_scan.py; ' + W + 'jh2_scan_out.txt; ' + W + 'jh2_sens.py; ' + W + 'jh2_sens_out.txt; research/dossiers/b74a016c/review.zip; ' +
        'research/sol_answer_D109_r37c_fix.md; ' + PK + 'pkgR37X2/pkg/sha256-r37/claim.json; ' + PK + 'pkgR37M3/pkg/sha256-r37/claim.json')
Sto = 'stale ledger values / stale sentences in the re-staged R37M3 package (hand-fixed stale H5 sentence)'
Stev = (W + 'jstale_scan.py; ' + W + 'jstale_out.txt; ' + W + 'jstale_sens.py; ' + W + 'jstale_sens_out.txt; ' + PK + 'pkgR37M3/pkg/sha256-r37/experiments/lowm.py (ledger, memory_bytes); ' +
        PK + 'pkgR37M3/pkg/sha256-r37/claim.json; ' + PK + 'pkgR37M3/pkg/sha256-r37/proof.md; ' + PK + 'pkgR37M/pkg (control lineage)')
R = []
R.append(rec('sha256-37|JUDGE.JH2|JUDGE|R1', H2o, 'R1: is the cause present in the current package?', 'COMPUTED',
 'b74a016c ruling (not_evaluable, lane_evaluability, 3 reasons H2/H3/H9; minor finding F-EVAL-SFS-COUNT-MISMATCH). Text scan of claim.json + proof.md. STRUCTURAL cause (no organizer experiment estimates q3, H3 late-round dependence or table means; organizer report probability_inference "none" for a0-sfs-r37 and a0-online-r37): PRESENT in every r37 package by construction, it cannot be removed. DECLARATION state of H2/H3/H9 limitations (stated-premise sentence / organizer-scope sentence): failing b74a016c H2 yes/yes, H3 yes/yes, H9 no stated-premise sentence (organizer-scope wording only); retry c22f86a2 all three yes/yes; filed fcbc9c83 (pkgR37X2, passed) H2 yes/yes, H3 yes/yes, H9 no stated-premise sentence (the same state as the failing b74a016c H9); staged pkgR37M3 H2 yes/yes, H3 stated-premise yes but NO organizer-scope sentence, no H9 (table-free). Count sentence: b74a016c and c22f86a2 both say "organizer experiment a0-sfs-r37: 127 of 128 local trials"; fcbc9c83 says "128 of 128 trials in our replay" and "85 of 128 ... outside the printed cells" (replay-qualified, not an organizer count); R37M3 has no such sentence.',
 H2ev,
 'Label: exact text scan (regex proxy, 4 packages). Organizer report numbers read from the b74a016c experiment-report.json. The organizer report for fcbc9c83 is not in the local store, so its 85-of-128 statement could not be compared with an organizer count (UNKNOWN, not checked). The proxy tests wording presence only; it cannot read the judge.'))
R.append(rec('sha256-37|JUDGE.JH2|JUDGE|R2', H2o, 'R2: margin number measured on the package (organizer count; score slack)?', 'COMPUTED',
 'Organizer a0-sfs-r37 in b74a016c: 256 active trials, 124 returned a pair; trials 0..127: 124 of 128 returned a pair (96.9 percent), none flagged as a success at target level, 132 trials absent. The proof sentence said 127 of 128: overstated by 3 trials (2.3 percent of 128), exact. Score margin of the H2 charge in the filed table line (xtab.py ledger, exact rationals): charged q3 = 2^-72.04 x 2.4331 gives 60.17144; at the measured kept-fibre point (cell factor 2^-71.974, ratio 2.46455) it gives 60.16229, i.e. 0.00915 bit of unused slack; the 5th-decimal slack of the claim itself is 0 (tight_up and tight_down true). Staged R37M3 (lowm.py): q3 2^-71.47 gives 60.99099.',
 H2ev,
 'Label: exact (report counts; ledger arithmetic). The 0.00915 bit is an outcome-informed value (a point estimate from a rerun), NOT a chargeable shave under the no-outcome-informed-caps rule; recorded for sensitivity only. Tool validated first: xtab.py ledger reproduces the proof Section 11.2 table in 11 of 11 rows to 5 decimals (see R3).'))
R.append(rec('sha256-37|JUDGE.JH2|JUDGE|R3', H2o, 'R3: did the check fire on the known failing dossier and on a passing one?', 'COMPUTED',
 'Proxy check = (a) H2/H3/H9 limitations lack the stated-premise or organizer-scope sentence, (b) an organizer-attributed "N of 128" with N != 124. On the FAILING b74a016c: fires (a: H9; b: 127 of 128). On the PASSING retry c22f86a2 (D109 sentences added): fires on (b) only, wording complete. On the PASSING filed fcbc9c83: fires on (a: H9 has no stated-premise sentence). Result: the proxy fires on pass and fail alike and does NOT separate the ruling; D109 added same-meaning sentences to H2 and H3 that b74a016c already had (claim.json diff: only the 3 limitations appends) and the package passed with unchanged numbers -> the ruling was reviewer variance (consistent with FILINGS: premises inherited from passed f2fe1d4d). Known-answer control of the sensitivity tool: xtab.py ledger(q3_log2, exq, safety, ac_log2) reproduces 11 of 11 values of the proof Section 11.2 table (60.16846, 60.23041, 60.31551, 60.57978, 64.01134, 57.59403, 60.38458, 60.17365, 60.17000, 60.16957, 60.18547).',
 H2ev,
 'Label: exact, but the control is weak by nature: the real check is an LLM judge that cannot be run here. UNKNOWN is not a pass: no local test predicts the reviewer. Do not use the proxy as a gate for H2/H3; it is a wording checklist only.'))
R.append(rec('sha256-37|JUDGE.JH2|JUDGE|R4', H2o, 'R4: score sensitivity per unit and distance to the threshold?', 'COMPUTED',
 'No numeric threshold exists (LLM verdict). Score sensitivity of the H2 premise, filed table line (xtab.py, exact): 0.1114 bit of score per bit of q3 near the charge (60.17144 at 2^-72.04; 60.23040 at 2^-72.5; 60.31550 at 2^-73; 60.42788 at 2^-73.5; 60.57320 at 2^-74.0; 60.75654 at 2^-74.5; 60.98154 at 2^-75; 60.08722 at 2^-71.0). Staged R37M3 (lowm.py): 0.4963 bit per bit near q3 = 2^-71.47 (one bit lower 61.57158; Table 15 value 2^-74.03 gives 62.76763; four patterns alone 2^-72.02 gives 61.28957; all three reproduced). Judge-side statement for b74a016c: 61.51355 (study A), 61.80684 (2^-74.5), 62.18051 (2^-75).',
 H2ev,
 'Label: exact ledger arithmetic. Time-only scoring. Under the live Pareto score (time_log2 + max(0, log2 mem - 20)) the filed table line (memory 2^52.1) would add 32.1 bits of memory term, so its sensitivity rows are for the old time-only challenge; R37M3 (memory 2^19.21 < 2^20) has memory term 0 and the slopes above. Slack candidates: none chargeable (see R2).'))
R.append(rec('sha256-37|JUDGE.JSTALE|JUDGE|R1', Sto, 'R1: is a stale value or stale sentence present in the current staged package?', 'COMPUTED',
 'pkgR37M3 (staged, claim time_log2 60.99099): 59 ledger-class values found in claim.json, proof.md and the note were compared with what the shipped lowm.py executes (ledger(): time_log2, vbar 46070.09, fixed 615, N_FB 60,951,875,249,131,685, V_MAX 2,808,743,648,446,227,477,989, vmax_fb 94,072,525,785; memory_bytes() 607,744; len(FEASIBLE_L) 32, enumerated pairs 2,097,152): 0 stale (0 flags). 22 of 22 evidence_ids line ranges of claim.json start on a heading line of the 1,435-line proof. The H5 text now carries 607,744 bytes, 46070.09 operations, the 32-l enumeration of 2,097,152 pairs and 61.01195 for the NOT-flip sensitivity.',
 Stev,
 'Label: exact scan of 11 value kinds (59 values). Not covered by the detector: prose claims without a ledger number, and the sensitivity value 61.01195 (all inversion flips priced as NOT), which was NOT independently recounted (implied extra cost 1,454.3 ops per first block, about 17.7 W6 programs of 82 flips; unverified). Three other sensitivity values (61.57158, 62.76763, 61.28957) were recounted and match (R2).'))
R.append(rec('sha256-37|JUDGE.JSTALE|JUDGE|R2', Sto, 'R2: own re-measurement or exact recount of the ledger values (metered run of the shipped program)?', 'COMPUTED',
 'Shipped program lowm.py ledger (exact, rerun here): time_log2 60.99099 (log2 T 60.990989434), tight_up and tight_down true, N = 6,058,690,054,895,037,231,741 over C = 2644, N_FB 60,951,875,249,131,685 (2^55.75852), mu 0.49558494, g 830.988, vbar 46070.085 (parts: class variable 21.14, per class 24,666.75, groups 16,269.77, survivors 4,879.12, rare 233.31), fixed 615, pcap 2^-10.797, success lower bound 0.390000001931, preprocessing 2^60.00141. memory_bytes() 607,744 = 2^19.21313, headroom to 2^20 440,832 B. Recounted sensitivity sentences of the proof: q3 2^-72.47 61.57158, 2^-74.03 62.76763, 2^-72.02 61.28957, all MATCH.',
 Stev,
 'Label: exact (deterministic ledger, no sampling). This is the ledger as the program executes it (best case, no cap added); no fresh-seed run is involved. Tool control: see R3.'))
R.append(rec('sha256-37|JUDGE.JSTALE|JUDGE|R3', Sto, 'R3: control: does the stale-value check fire on the known stale lineage and stay quiet on a consistent one?', 'COMPUTED',
 'Control A (known stale): the text of pkgR37M (the pre-fix lineage, score 61.24102) checked against the M3 ledger: 29 flags of 53 values (N_FB 5, row-16 l count 28 vs 32: 5, vbar 43309.60 vs 46070.09: 6, V_MAX 3, vmax_fb 3, memory 607,232 vs 607,744: 5, time_log2 and title 61.24102 vs 60.99099: 2): the check fires on every class of value the hand fix touched. Control B (negative): the same pkgR37M text against its own ledger (lowm.py of pkgR37M: 61.24102, 43309.60, 607,232, 28 l): 0 flags of 53. Object: pkgR37M3 text vs its ledger: 0 flags of 59. The first version raised 3 false positives on M3 (ledger part values 24,666.75 and 16,269.77, and the 2^20 limit 1,048,576 read as a memory value); these were whitelisted from the ledger parts and the limit and the controls rerun.',
 Stev,
 'Label: exact. Control A is not the pre-fix state of R37M3 itself (that snapshot was edited by hand and not kept); it is the nearest earlier lineage whose values legitimately differ. The row-16 pairs rule (2,097,152 vs 1,052,672) is applied only to packages with R16x, so it did not fire in control A.'))
R.append(rec('sha256-37|JUDGE.JSTALE|JUDGE|R4', Sto, 'R4: score sensitivity per unit and slack candidates for stale values?', 'COMPUTED',
 'Stale text carries no score by itself: the score is the ledger. Value of one stale ledger number: +1 operation per first block of data-dependent work moves time_log2 by 1.452e-05 bit (N_FB (1+2^-12) / N / ln 2); the 61.26678 -> 61.01195 style statement in H5 (all 81-82 W6 inversion flips priced as NOT) is 0.02096 bit, equal to about 1,454 ops per first block. Memory: 607,744 B = 2^19.21313; the Pareto memory term max(0, log2 mem - 20) is 0 and stays 0 for up to 440,832 more bytes (72.5 percent); beyond 2^20 it costs 1 bit per doubling. time_log2 has 0 slack in the 5th decimal (tight both ways). q3 slope 0.4963 bit per bit.',
 Stev,
 'Label: exact arithmetic. Slack candidates: none found; the 5th decimal is tight in both directions. The hazard is a judge or reader finding a stale sentence, not score.'))
os.makedirs(OUT, exist_ok=True)
existing = add_cell.load()
bad = 0
for r in R:
    fn = r['id'].replace('|', '_').replace('.', '_').replace('-', '_') + '.json'
    p = os.path.join(OUT, fn)
    json.dump(r, open(p, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    errs = add_cell.validate(json.load(open(p, encoding='utf-8')), existing)
    print(fn, errs)
    bad += bool(errs)
print('bad', bad)
