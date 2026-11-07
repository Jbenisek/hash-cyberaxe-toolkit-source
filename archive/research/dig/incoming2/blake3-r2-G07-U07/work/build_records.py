
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

import json, re, os, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G07-U07')
W = 'research/dig/incoming2/blake3-r2-G07-U07/work/'
PK = 'research/tools/build_pkg/scratch/pkgB3U/pkg/blake3-r2/proof.md'


def rec(cell, obj, q, status, number, evid, notes, labels=('N',), lever=False, gain=None):
    return dict(hash='blake3-r2', row_i=None, row_j=None, object=obj, question=q, labels=list(labels),
                status=status, number=number, source='our workflow: scan-once-wave2', own_test=True,
                evidence=evid, date='2026-10-12', lever=lever, gain_bits=gain,
                notes='universe cell %s. ' % cell + notes, topic=cell)


LIM = (" Not run: the organizer judge itself (it cannot be re-run here; no judge verdict is claimed), any "
       "instruction-count measurement of kissat (WSL has no hardware counters), and the full-size 32-bit joint event.")
R = []
R.append(rec('blake3-r2|JUDGE.JADV|JUDGE|R1',
 'JUDGE.JADV: 5a08fffa REFUTED lane_cost F1-unaccounted-advice-construction (SEL may return other constants/none)',
 'R1: is the cause present in the current package, and what value does the package charge?',
 'COMPUTED',
 'Cause ABSENT as worded in the current filed package pkgB3U (c994a61f, PASSED review 10-12 01:56): SEL is a pinned deterministic call with generator listing (instance sha256 286927dd...), kissat binary sha256 e0458ae2..., seed 506, a replay record, and a 68-byte stored-record comparison. Charged: S_old = 116*(18021/2)*2^42 + 116*(2^51+2^10) + 2^50 = 4,859,252,056,537,550,848 ops (2^53.3272 units of 430 ops), 6.88% of N = 70,643,517,498,710,778,735; preprocessing_log2 = 54 (allowance 2^54 units = 7.746e18 ops, slack 0.673 bit); advice 7 (68-byte record). The refused 5a08fffa charged 116*5*2^53+116*(2^51+2^10)+2^50 = 5,486,510,246,044,225,536 and said its SEL programs are not in the package.',
 PK + ' (Sections 11, 12, 12.2); research/dossiers/5a08fffa/judge-dossier.json (lane_adjudicator confirmed F1); ' + W + 'f1_detector.py; ' + W + 'ledger_recount.py',
 "Dossier ruling: F1 confirmed because the 68-byte record was not tied to the capped SEL (generator, solver log, counter absent; 32 runs without cause records; operation-rate conversion unproved; SEL could return different constants or none). Present-state check is by literal markers in the proof text (see R3), not by the judge. Residual items still stated in the current proof: the 116-line log is not shipped (115 lines are charged as a search omitted from the program), the 2^42 ops/s rate is a stated premise, the kissat call is not metered (bounded via running time), and the organizer experiment cannot run the call (35 min vs 20 s)." + LIM))
R.append(rec('blake3-r2|JUDGE.JADV|JUDGE|R2',
 'JUDGE.JADV: SEL pinned call and S_old ledger row of pkgB3U',
 'R2: own re-measurement / exact recount of the SEL charge and the pinned call',
 'LOCAL_ONLY',
 'EXACT recount: ledger rows WB+W_CTX+credit+ctx+block+once+S_old+final sum to N = 70,643,517,498,710,778,735 exactly; certificate 2^571889*430^10000 <= N^10000 < 2^571890*430^10000 holds; log2(N/430) = 57.18899813 (claimed 57.1890; rounding slack 1.9e-6 bit); S_old recomputed from its formula equals the filed value (term 116*9010.5*2^42 = 4,596,917,378,243,100,672 = 2^61.995). The generator listing of 12.2, run here, regenerated the instance: 24,689 vars, 62,334 clauses, 1,112,377 bytes, SHA-256 286927dd9581cc54055b1db8ca6039d76c712041e14c0cf4cdb285d6bd743ee8 = stated; the function check on the stored model returns True, cost 100 (<=104), x1 weight 13 (<=24), eta 830303cf, beta 18b0e098 = the record. Installed kissat 4.0.3-2 binary sha256 e0458ae23487a6d2a1b38d4ceb46e304e1be4dcb84067686693bc70e0513d572 = stated. Pinned call replayed (kissat --sat --seed=506 --time=2500, one process, WSL, machine load about 23 of 24): status UNKNOWN (NOT UNSAT) after 2504 s wall / 1523 s process time, 2,423,488 conflicts, 314,271,099 propagations (the proof reports SAT at 13,567,518 conflicts, 2,070,017,461 propagations, 2105 s). The SAT result was NOT reproduced here within the time limit.',
 W + 'ledger_recount.py; ' + W + 'gen_listing.py (run20.cnf); ' + W + 'kissat_run.out; ' + W + 'kissat_bin.sha',
 "Window answer: instance/hash/check/binary identity and the ledger arithmetic are complete and exact; the solver run itself is a time-limited prefix (2.42M of 13.57M conflicts, 17.9%), so determinism (same conflict trajectory) and the SAT outcome are untested here. Throughput was 1591 conflicts/s and 206k propagations/s versus the proof's replay 6444 conflicts/s and 983k propagations/s, about 4x slower under load; no conflict-count-at-time reference is shipped to compare the trajectory. Fresh seeds are not applicable (SEL is deterministic by design); the rule written before the run was: instance sha and check must match, the solver may or may not finish." + LIM,
 labels=('N', 'Z')))
R.append(rec('blake3-r2|JUDGE.JADV|JUDGE|R3',
 'JUDGE.JADV: F1 closed-construction-path marker test',
 'R3: control - same check on the known failing dossier and on passing packages',
 'COMPUTED',
 'Marker test (6 literal markers: SEL programs not in package; instance sha; solver binary sha; generator listing; replay record; stored-record comparison). FAIL case 5a08fffa (judge REFUTED F1): closed_path False; M1 (programs not in the package) True, M2-M6 all False, M7 (SEL could return other/none) True. PASS cases pkgB3U (filed, PASSED) and pkgB3V (staged): closed_path True, M1 False, M2-M6 True, M7 False. Stale-text trap: the scratch directory pkgB3L proof.md still holds the refused wording (closed_path False, same as 5a08fffa) and must not be re-staged.',
 W + 'f1_detector.py; ' + W + 'f1_detector_out.json; ' + W + 'proof_5a08fffa.md',
 "The detector separates the one known failing text from the two closed-path texts, which is all a control can show with n=1 failing dossier; it is a literal-text proxy for the judge's reading, not the judge. It does not test whether the pinned call reproduces (see R2) nor whether the rate premise passes." + LIM,
 labels=('Z',)))
R.append(rec('blake3-r2|JUDGE.JADV|JUDGE|R4',
 'JUDGE.JADV: score sensitivity of the SEL charge S_old (pkgB3U ledger)',
 'R4: score sensitivity in bits per unit and slack candidates',
 'COMPUTED',
 "time_log2 = 57.18900 with S_old = 4.859e18. d(time)/d(log2 S_old) = +0.09597 bit per doubling (0.09924 bit per e-fold; share 6.88% of N). S_old x0.5 = -0.0505, x2 = +0.0960, x10 = +0.6952, S_old = 0 = -0.1028 (search alone 57.08618, matches the proof 57.0862). Variants (exact integers): cap-based 116*5*2^53 (5a08fffa form) 57.20175 (+0.01275, so the logged-maxima row is worth -0.01275); one SEL pair at caps 5*2^53+2^51+2^10+2^50 -> 57.08724 (-0.10175); run 20 only 4770 s*2^42 -> 57.08672 (-0.10228). Rate premise on the 116 logged maxima of 9010.5 s: 2^36.5 ops/s -> 57.09414 (-0.09486), 2^38 -> 57.09819 (-0.09081), 2^40 -> 57.11681 (-0.07219), 2^42 (filed) 57.18900. Distance to the F1 cause: binary, no numeric threshold; the logged 4770 s pinned run is 2^1.1 under its 5*2^53 cap at 2^42 ops/s and 2^6.5 under at the proof's own 2^36.5 ops/s instruction ceiling. Rounding: the claim 57.1890 has 1.9e-6 bit of slack, so any ledger change moves the 4th decimal.",
 W + 'ledger_recount.py',
 "Slack candidates (not claimed): (a) the package prices the pinned call at 2^36.5 ops/s (Section 12, Cost of the pinned call) but S_old at 2^42 ops/s (Th0rgal's stated rate, LEVERS.md line 38); one common rate of 2^36.5 would be -0.0949 bit, but the 2^42 value is the conservative reading the judge has accepted on every passing filing and the rate is unproved either way. (b) Charging 1 pair instead of 116 is -0.1017 bit, but the 115 other lines are the search that chose the instance, which is exactly what F1 was about; dropping them risks a repeat of the refusal. Neither is a clean gain." + LIM))
R.append(rec('blake3-r2|JUDGE.JDEP|JUDGE|R1',
 "JUDGE.JDEP: H1prime(ii) dependence clause, fa761365 (pkgCA 65.0407) and 1a92bf64 (pkg16f 101.9196) both NOT_EVALUABLE",
 'R1: is the cause present in the current package, and what value does the package state?',
 'COMPUTED',
 'Cause PRESENT in the current filed package pkgB3U (c994a61f 57.189, PASSED). H1prime part (ii) is stated for contexts with rho_c = E[N_c(N_c-1)]/E[N_c] <= 0.0065; the proof says Part (ii) is an assumption, not measured, and cannot be measured at full size (E[N_c] about 2^-51.87 per context). Stated: lambda = 0.49594, b(0.0065) = 0.99675, exponent 0.4943282, exp(-0.4943282) = 0.609981 < exp(-0.49594)+0.001. Judge on the two failed filings: lane_evaluability rated H1prime-rate-and-dependence unsupported (1a92bf64: the factorial-moment bound 0.0065 has no analytic or experimental support; fa761365: cross-member dependence clause plus the HPRE device-use attestation), status not_evaluable in all lanes. The line later passed five times with the same style of clause (FILINGS rows: 244f068c, a14831c1, 4348a26b, 5f7e222e, c994a61f).',
 PK + ' (10.3, lines 1362-1385); research/dossiers/1a92bf64/judge-dossier.json; research/dossiers/fa761365/judge-dossier.json; research/FILINGS.md',
 "The pass/fail history is read from FILINGS.md rows and the two local dossiers; the texts of the four passing packages other than pkgB3U were not re-opened (their dossiers are not stored), so same clause for those is a label from the filing log, not a verified text match. The 1a92bf64 clause was per outer step (rho <= 0.0065 for one step of 2^21 trials); the pkgB3U clause is stronger (contexts of 2^19 steps)." + LIM))
R.append(rec('blake3-r2|JUDGE.JDEP|JUDGE|R2',
 'JUDGE.JDEP: margin numbers of the rho_c <= 0.0065 clause',
 'R2: the margin number measured on the current package (statistic, exact recount)',
 'COMPUTED',
 'Arithmetic (double precision, 1e-12): the largest rho keeping exp(-0.49594*b(rho)) <= exp(-0.49594)+0.001 is 0.006617, so the stated 0.0065 has a margin of 0.000117 (1.8%); the whole clause is worth 0.00470 bit against rho = 0. Clustering room: rho_x = v*(2^19-1)*E[N_o(U)] with E[N_c] = 2^19*2^21*2^-91.868 = 2^-51.868 (the proof prints 2^-51.874); the clause fails only for v above 2^44.61 (proof 2^44.6; fa761365 states 2^44.21 using its 2^-51.474). Cited participant statistics (not ours, not rerun): cross-step Rx = 1.1641 (upper limit 1.2300) for the listed E1 outcome and 9.0084 (9.7541) for pass-and-E1; fa761365 member loop 597.82 vs 519.81 pairs (ratio 1.1501). No own measurement of the dependence of listed good trials exists or is possible at 32 bits (events about 2^-91 per trial).',
 W + 's8_control.py',
 "Arithmetic answer only. A fresh measurement would need the 2^45-trial GPU runs of Section 13; not repeated (SCAN ONCE, machine load, and the joint event is unreachable anyway)." + LIM,
 labels=('N', 'E')))
R.append(rec('blake3-r2|JUDGE.JDEP|JUDGE|R3',
 'JUDGE.JDEP: Lemma S8 (mean + factorial moment -> success) control',
 'R3: control - the same tool on a known answer and a negative control that must fail',
 'COMPUTED',
 'Positive control: 20,000 random finite laws of N (exact rational probabilities), Pr(N>0) >= mu*b(rho) with b(rho) = (2r-rho)/(r(r+1)), r = floor(rho)+1: 0 violations, minimum ratio Pr/(mu*b) = 1.000000 (equality attained); the two-point law {0,5} with p = 1/1000 meets the bound with equality. Negative control: claiming a rho 10x smaller than the true one makes the bound fail on 4,999 of 5,000 laws (must be above 0). History control: the marker (dependence assumed, unmeasured) is present in the 2 failed filings (1a92bf64, fa761365) and in the passing pkgB3U, so it does not by itself predict the ruling.',
 W + 's8_control.py',
 "This validates the algebra that turns rho_c into the exponent, not the premise rho_c <= 0.0065 itself. The independence of contexts (Lemma CX) used with S8 is not tested here." + LIM,
 labels=('Z',)))
R.append(rec('blake3-r2|JUDGE.JDEP|JUDGE|R4',
 'JUDGE.JDEP: score sensitivity of the dependence bound (run length scales 1/b(rho) at fixed success)',
 'R4: score sensitivity in bits per unit and the cost of a proved fallback',
 'COMPUTED',
 'Extra bits relative to the filed rho_c = 0.0065 (run length times b(0.0065)/b(rho)): rho 0 = -0.0047; 0.05 = +0.0318; 0.5 = +0.4103; 1 = +0.9953; 2 = +1.5803; 23 (N_o <= 24 per step, rho_w <= 23) = +4.5803; 3071 (3,072-member lemma) = +11.5803 (log2 3072 = 11.585). Slope at 0.0065: 0.7237 bit per unit rho (0.000724 per 0.001). The proved fallback on 1a92bf64 cost 101.9196 -> 113.4454 (+11.5258, retry 848bcd76 scored). Applied to the 57.189 line, the proved bound rho_w <= 23 alone would cost +4.58 bits and a proof of the context bound is not available; the clause itself is worth only 0.0047 bit against rho = 0, so the score-critical stake is the existence of any rho bound, not its size.',
 W + 's8_control.py',
 "Sensitivity is in the S8 exponent at fixed target probability 0.39 (other terms of the success calculation unchanged). The context-level proved bound for the walk is not known; 23 and 3071 are the per-step and per-frame bounds of the cited lemmas, used here only as scale." + LIM,
 labels=('N',)))
os.makedirs(OUT, exist_ok=True)
ex = add_cell.load()
for r in R:
    fn = re.sub(r'[^A-Za-z0-9-]', '_', r['topic']) + '.json'
    p = os.path.join(OUT, fn)
    json.dump(r, open(p, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(fn, add_cell.validate(json.load(open(p, encoding='utf-8')), ex))
