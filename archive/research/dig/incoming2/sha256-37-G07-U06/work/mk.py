
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
OUT=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G07-U06')
W='research/dig/incoming2/sha256-37-G07-U06/work/'
ev_common=W+'ev2.py; '+W+'cpu_ship.sh; '+W+'time_ship.sh; '+W+'ctl_timeout.py; hash-smash/experiments/runner.py (ExperimentLimits: 64 KiB, 20.0 s); hash-smash/verifier/intake.py line 199; hash-smash/scripts/hashsmash_pipeline.py line 138'
ctx=("Packages: shipped = pkgR37X (fcbc9c83 PASSED, xtab.py only declared source); staged later = pkgR37X2 (5 experiments, not filed here). "
 "Brief text says time limit 10 s and cites B3V/R5T2 figures from other hashes; the organizer code default is timeout_seconds=20.0 per experiment run and sources are summed over declared files against 65536 B; those other-hash figures were not re-measured here. "
 "Traps checked: none involve a schedule (pure margin cell); numbers labelled exact/sampled below. ")
recs={
'R1':dict(q="Value charged or stated: what are the evidence-size and experiment-time margins in the current sha256-37 package (limits, shipped values)?",
 labels=['N'],status='COMPUTED',
 number="Exact: experiment source xtab.py = 64,859 B of 65,536 B (margin 677 B, 1.03 %), single declared file, manifest.json 5,875 B is not summed; pkgR37X2 xtab.py 64,977 B (margin 559 B). Judge evidence (judge-evidence.json = canonical_json_bytes, dossier b43280d0 of the R37X line): 482,521 B of 524,288 B (margin 41,767 B, 7.97 %). Limits in code: ExperimentLimits.max_source_bytes 65,536, timeout_seconds 20.0 (not 10 s), evidence 512 KiB.",
 gain=False,
 notes="universe cell sha256-37|JUDGE.JMARGIN|JUDGE|R1. "+ctx+"Other sha256-r37 dossier evidence sizes (exact): 1c368173 223,874; 04441cbc 272,871; 7319bba9 274,900; b74a016c 283,458; b43280d0 482,521. Largest margin pressure anywhere in dossiers: f1346045 524,010 B (278 B left; not sha256-37). No judge-failure cause is present for sha256-37 on these margins (fcbc9c83 passed). The paper-style != trap not relevant."),
'R2':dict(q="Own re-measurement: experiment run time (and size) of the shipped sha256-37 program, repeated, with a rule written before the run (pass iff CPU seconds < 20 on the organizer's one-CPU limit).",
 labels=['N'],status='SAMPLED',
 number="Sampled (2 reps each, machine load average 25-37 on 24 cores, so inflated): pkgR37X xtab.py CPU user seconds a0-sfs-r37 15.72 and 14.57, a0-online-r37 11.12 and 14.10 (max 15.72 s, margin 4.28 s of 20 s); outputs identical across reps (hash f9f932a9db3a, c2bf1f7cf966). Docker one-CPU wall under same load, 3 reps: sfs 38.8/36.9/40.4 s, online 34.3/29.7/33.6 s - above 20 s only because of host contention (CPU-seconds are the load-independent figure; unloaded wall not measured). pkgR37X2 (1 run each, CPU s): sfs 7.29, online 5.03, cv 1.95, ctl 4.77, dep 4.14, max 7.29 s. Memory max RSS 40.9 MB (limit 128 MB).",
 gain=False,
 notes="universe cell sha256-37|JUDGE.JMARGIN|JUDGE|R2. "+ctx+"Requests are the organizer public-seed requests built by mkreq.py (256 trials); fresh seeds were not run. Caveat: under load the control loop itself varied 7.4-7.9 s (7 %), online run 11.1-14.1 s (27 %), so the sampled interval is wide; the unloaded value is lower. Evidence margin recount: exact only for dossier b43280d0 (R1). For pkgR37X2 evidence size is an estimate only: proof +17,363 B and +88 lines (about +792 B numbering), manifest +4,736 B, claim +2,230 B gives at most about +25 KB, so margin roughly 16-17 KB, but its 3 extra experiments add report bytes that were not measured; the intake pipeline was not run on X2."),
'R3':dict(q="Control: does the same check machinery fire on a known failing case and pass on a known passing one (timeout watchdog, evidence-size recount)?",
 labels=['N'],status='COMPUTED',
 number="Exact: (a) organizer runner _run_docker with timeout_seconds=1.0 on the pkgR37X2 a1-cv request RAISED ExperimentError 'Python experiment exceeded organizer timeout' after 1.21 s; with timeout_seconds=20.0 the same run PASSED (10.06 s wall under load, 80,403 B output). (b) repo canonical_json_bytes recomputed on 6 stored judge-evidence.json files equals file size byte for byte (6/6, e.g. b43280d0 482,521). (c) size rule sum(len)>65536 is plain arithmetic: shipped 64,859 passes, a 678 B pad would fail; no padded copy was pushed through intake.",
 gain=False,
 notes="universe cell sha256-37|JUDGE.JMARGIN|JUDGE|R3. "+ctx+"Not done: no run of the real intake on an over-limit package and no replay of the known failing B3V dossier (none stored locally: FILINGS 896db2cb had no artifact)."),
'R4':dict(q="Score sensitivity: bits per unit of margin, and slack candidates, distance to each threshold.",
 labels=['N'],status='COMPUTED',
 number="Exact: score sensitivity to these margins is 0 bits per byte and 0 per second (they are pass/fail intake gates, not terms of time_log2 or memory). Distance to threshold: source 677 B (1.03 %) in the shipped program, 559 B in pkgR37X2; CPU time 4.28 s of 20 s (21 %, measured under load, shipped) or 12.7 s (X2); evidence 41,767 B (7.97 %) on the R37X line. Tightest is source bytes: any code added to xtab.py beyond about 677 B fails intake, so a ledger shave that needs more program text must be paid for by deleting comments/docstrings (past 40 % comment finding in memory).",
 gain=False,
 notes="universe cell sha256-37|JUDGE.JMARGIN|JUDGE|R4. "+ctx+"Slack candidates (not tested): comment/docstring stripping in xtab.py to buy source bytes; evidence margin can be spent only on proof text (about 9 B numbering per line plus content). No gain claimed."),
}
for k,r in recs.items():
    d=dict(hash='sha256-37',row_i=None,row_j=None,object='JUDGE.JMARGIN evidence-size and experiment-time margins',
      question=r['q'],labels=r['labels'],status=r['status'],number=r['number'],source='our workflow: scan-once-wave2',own_test=True,
      evidence=ev_common,date='2026-10-12',lever=False,gain_bits=None,notes=r['notes'],topic='JUDGE.JMARGIN')
    fn=OUT+'\sha256-37_JUDGE.JMARGIN_JUDGE_%s.json'%k
    json.dump(d,open(fn,'w',encoding='utf-8'),indent=1)
    add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load()); print(k,'valid')
