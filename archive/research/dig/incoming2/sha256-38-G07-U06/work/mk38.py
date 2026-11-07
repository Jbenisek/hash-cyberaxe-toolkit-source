
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

import json,sys
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
OUT=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G07-U06')
W='research/dig/incoming2/sha256-38-G07-U06/work/'
ev=W+'ev38.py; '+W+'est38.py; '+W+'mkreq38.py; '+W+'reqchk.py; '+W+'cpu38.sh (cpu38_out.txt); '+W+'dock38.sh (dock38_out.txt); '+W+'ctl38.py (ctl38_out.txt); hash-smash/experiments/runner.py (ExperimentLimits 64 KiB, 20.0 s); hash-smash/verifier/intake.py line 199; research/dossiers/cfeb996a/runs/*/experiment-report.json (organizer_limits)'
ctx=("Packages: shipped = pkgR38L (fdef4bab PASSED 71.0725, single declared source experiments/vt38.py, no stored dossier); latest filed with a stored dossier = pkgR38N (cfeb996a NOT_EVALUABLE on H4a, evidence stored); staged = pkgR38M3 (a0lean38.py). "
 "Brief text says 10 s; organizer_limits recorded in the cfeb996a experiment report say timeout_seconds 20.0, max_source_bytes 65536, memory_mb 128, pids 32, trials 256, max_output_bytes 2097152; the other-hash figures (B3V 84 B / 14.5 s, S5T2 218 B / 12.06 s) were not re-measured here. Traps: pure margin cell, no schedule or UNSAT/UNKNOWN content; != trap not relevant. ")
R={
'R1':("Value charged or stated: what are the evidence-size and experiment-time margins in the current sha256-38 package (limits, shipped values)?",'COMPUTED',
 "Exact: shipped experiment source vt38.py (pkgR38L, fdef4bab) = 65,314 B of 65,536 B (margin 222 B, 0.34 %); experiments/manifest.json 4,500 B is not summed (only declared program files are). Same limit on the other r38 lines: pkgR38N vt38.py 65,478 B (margin 58 B, 0.09 %, the tightest), pkgR38M2 a0lean38.py 65,239 B, pkgR38E vt38.py 65,330 B, pkgR38d vt38.py 65,352 B, staged pkgR38M3 a0lean38.py 64,824 B (712 B). Judge evidence (judge-evidence.json = canonical JSON bytes): largest stored sha256-r38 dossier cfeb996a 505,918 B of 524,288 B (margin 18,370 B, 3.50 %); other r38 dossiers 268,970 to 425,602 B (de030a60 278,432; 8bc7d6c5 268,970; 1393e83b 425,602; 0ae69bcb 347,754). No dossier is stored for the shipped fdef4bab; its evidence size is only a rough estimate (label: estimate): prefile-style sum 439,356 B, plus the 17,579 B (3.6 %) by which the same formula under-counts cfeb996a (488,339 vs 505,918), i.e. about 457,000 B, margin about 67,000 B. Time limit in code and in the organizer report: timeout_seconds 20.0 per experiment run (each experiment is run twice, byte-identical required)."),
'R2':("Own re-measurement: experiment run time (and size) of the shipped sha256-38 program, repeated, with a rule written before the run (pass iff CPU seconds < 20 on the organizer's one-CPU limit).",'SAMPLED',
 "Sampled, rule written before the run in cpu38.sh (pass iff CPU user seconds < 20.0 per experiment run). Host load average about 25 on 24 cores, so inflated (a fixed CPU-bound control loop took 6.00 and 8.30 s, +38 %). Shipped vt38.py (pkgR38L), organizer public-seed requests (256 trials): vt-q3-smc-r38 CPU 12.30 and 14.90 s; fresh seeds 15.78 s; vt-ram-r38 3.59, 7.09 s (fresh 5.23 s). Max 15.78 s, margin 4.22 s of 20 s: PASS under the rule. Outputs byte-identical across the two public reps (sha 69ee1d21e961, 0fb3d9e91abe). pkgR38N (cfeb996a) q3 16.84 s, ram 4.73 s; staged pkgR38M3 a0-q3-r38 15.64 s, a0-online-r38 0.93 s. Max RSS 25.5 MB (q3), 45.3 MB (ram) vs 128 MB. NOT PASSED in the replica of the organizer wall-clock watchdog: Docker one-CPU, same host load, shipped program, wall 35.2 s (q3) and 12.5 s (ram); with timeout_seconds=20.0 the runner raised ExperimentError after 21.63 s. This is host contention (CPU user 12-16 s, wall 1.1-2.9 x CPU under load) and the organizer passed the same program at fdef4bab, but the unloaded wall time was not measurable here, so the organizer-side margin is not known from our data."),
'R3':("Control: does the same check machinery fire on a known failing case and pass on a known passing one (timeout watchdog, evidence-size recount, request reconstruction)?",'COMPUTED',
 "Exact: (a) our rebuilt organizer requests (mkreq38.py) reproduce the request_sha256 recorded in the organizer's own report for cfeb996a on both r38 experiments (0b5937d707cf95b2... and 4feb4c02a0ec40a9...), so the run inputs are the organizer's. (b) repo canonical_json_bytes recomputed on all 50 stored judge-evidence.json files equals the file size byte for byte (50/50, e.g. cfeb996a 505,918). (c) timeout watchdog fires on a known failing setting: runner._run_docker with timeout_seconds=1.0 on the shipped program RAISED 'Python experiment exceeded organizer timeout' after 1.76 s. The passing arm did NOT pass: timeout_seconds=20.0 also raised, after 21.63 s, because of host load (see R2); so the positive control is missing for the wall-clock arm. (d) size rule sum(len)>65536 is arithmetic: shipped 65,314 passes, a 223 B pad would fail; no padded copy was pushed through intake."),
'R4':("Score sensitivity: bits per unit of margin, and slack candidates, distance to each threshold.",'COMPUTED',
 "Exact: score sensitivity is 0 bits per byte and 0 per second (pass/fail intake gates, not terms of time_log2 or of the memory term max(0, log2(memory bytes) - 20)); the second objective (rounds) is not touched either. Distance to threshold: source 222 B (0.34 %) for the shipped vt38.py, 58 B for pkgR38N, 712 B for staged pkgR38M3; CPU time 4.22 s of 20 s (21 %, measured under load; about 3 to 4 s per the manifest text when unloaded) for the shipped q3 experiment; evidence about 67,000 B (estimate) for the shipped line, 18,370 B (exact) for the largest stored r38 dossier cfeb996a. Tightest is source bytes: any program text beyond 222 B added to vt38.py fails intake (58 B on the N line), so a ledger shave that needs code must be paid by deleting comments or docstrings. Evidence for lines like N grows about 9 B per proof line plus content: 18,370 B is roughly 2,000 extra proof lines of slack."),
}
for k,(q,st,num) in R.items():
    d=dict(hash='sha256-38',row_i=None,row_j=None,object='JUDGE.JMARGIN evidence-size and experiment-time margins',
      question=q,labels=['N'],status=st,number=num,source='our workflow: scan-once-wave2',own_test=True,evidence=ev,date='2026-10-12',lever=False,gain_bits=None,
      notes="universe cell sha256-38|JUDGE.JMARGIN|JUDGE|%s. "%k+ctx+"Labels: sizes exact; evidence for the shipped line is an estimate; CPU times sampled under load. Requests: organizer public-seed (verified by request hash) plus one fresh-seed arm; the manifest.json size was left out of the source sum as intake.py sums only declared program files.",topic='JUDGE.JMARGIN')
    fn=OUT+'\sha256-38_JUDGE.JMARGIN_JUDGE_%s.json'%k
    json.dump(d,open(fn,'w',encoding='utf-8'),indent=1)
    add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load()); print(k,'valid')
