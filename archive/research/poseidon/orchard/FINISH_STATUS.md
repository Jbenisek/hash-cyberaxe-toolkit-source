# Poseidon counted runs: status, ETA, finish commands (written 2026-10-15 06:25Z)

Nothing was stopped or submitted. The programs print ONLY at the end (one write), so there is no log to read; the stage/trial/op counters were read live and read-only from /proc/PID/mem with `peek_run.py PID BINARY` (run it again any time, in WSL: `python3 peek_run.py 1503097 exec_r4b/single`).
Scale: finished r3 run (exec_r3f): one trial = 462.1e9 ops, stages B 1.3e9 / C 390.1e9 / D 70.8e9 (84.4% / 15.3%), 5813 s, 7.95e7 ops/s. r4 trial scaled by transform size (3*2^22 vs 3*2^20, x4.4) ~ 2.0e12 ops (consistent with the cloud counter, below); r5 (3*2^24, x19.2) ~ 8.9e12. Each centre succeeds with p ~ 0.39, so a run needs 1, 2, 3 ... trials (expected 2.5); the time to the end is "the rest of the current trial + k further trials".

| run | where / PID | stage now (06:19-06:21Z) | ETA (all ETAs are GUESSES from op-count scaling and the current ops/s) | expected peak memory (what the filing will report) | what the filing needs |
|---|---|---|---|---|---|
| r4b | local, python memmeter 1503095 -> single 1503097, nice 10, up 6h53 | trial 2 (centre 1 already FAILED, so the run is past its first trial), stage C, ~7% into trial 2: ops 2.152e12, rate now 6.7e7/s (avg 8.7e7/s) | end of trial 2 ~ 4.05e12 ops: 6-8 h -> **~12:30-14:30Z** if centre 2 succeeds (p 0.39). If not, +6.5 h per further trial: trial 3 ~19-21Z, trial 4 ~ 02Z | arena 1,227,182,400 B reached already (arena_hwm), RSS 1.18 GB; memmeter (wraps `bash -c 'ulimit -s 64; exec ./single 1'`, whole tree, ru_maxrss + VmHWM) covers the whole run incl. all trials; claim = max(counted sum, memmeter peak) ~ 1.23e9 B | run ledger + mem.json in data/cache/<hash>/ (cycle.sh writes them at exit; it then also builds pkg_stage_exec itself with its own SIM_EXTENT), then FINISH |
| r5b | local, memmeter 1498211 -> single 1498213, nice 10, up 7h30 | trial 1 (first centre), stage C, ~21% of an est. 8.9e12-op trial: ops 1.897e12, rate 6.0e7/s (avg 7.0e7/s) | rest of trial 1 ~ 7e12 ops = 28-35 h -> **~Oct 16 10:00-18:00Z** if centre 1 succeeds; centre 1 at r4 failed, r5 is unknown; each further trial ~ +36-40 h. Weakest ETA | arena 6.4 GB (arena_hwm 4,759,669,504 so far, RSS 4.65 GB, still growing to ~6 GB); memmeter covers the whole run. NOTE: HANDOFF 10-14 23:06 says r5b arena slack is 0.47 bit ("needs rerun"): check before filing, the note has no SIM_EXTENT margin line for r5 | same as r4b (build_package of r5b has ARENA_MARGIN empty, SIM_EXTENT not used) |
| r4mt | cloud root@108.61.192.253 /root/hs/mt/run_r4_T6, memmeter 55682 -> single 55689 (6 threads), started 05:02Z, up 1h19 | trial 1, stage D (half-gcd), main-thread ops 1.71e12 (~84% of a 2.0e12 trial: C is done), main-thread rate 2.1e8/s; mem_peak 1,072,730,624 | trial 1 ends ~**06:50-07:15Z**. Same centre order as r4b, whose centre 1 failed, so trial 1 should FAIL (inference, not checked on the cloud) and trial 2 starts: ~1.5-2 h -> **~08:30-09:30Z** if centre 2 succeeds (p 0.39); trial 3 ~10-11:30Z. Counter sampled from the main thread only: totals may differ | memmeter (/root/hs/mt/memmeter, `ulimit -s 64; exec ./single 1 6`) covers all 6 threads (wait4 ru_maxrss + sampled VmHWM); expected ~1.1-1.23e9 B (arena 1,227,182,400 B). The cloud box also ran the r3 mt/baseline tests (smaller than 290 MB, fine) | run.tmp/mem.tmp/end.txt/single on the cloud; THREADS line in the ledger (build_package asserts it); the note must disclose that it ran on another machine with 6 threads, and r4b/r4mt both being runs of the r4 program |

## Memory check (task 3)
- Local r4b/r5b: memmeter is the parent of `bash -c 'ulimit -s 64; exec ./single 1 > run.tmp'`, so its peak is the peak RSS of the whole counted process over all trials. Cloud r4mt: same memmeter, copied to /root/hs/mt/memmeter, wraps `single 1 6`; ru_maxrss counts all threads. build_package takes `mem_bytes = max(counted parts, memmeter peak)` and FINISH_r4r5.sh asserts claim >= memmeter peak.
- Judges count all runs of the entry (dev runs too). The big ones already running for r4: r4b (1.23 GB) and r4mt (about the same) - both are within one claimed peak. r5b (6.4 GB) belongs to the r5 entry, not r4. Stopped/aborted runs and the probe runs must be listed in the note (build_package PROBES env) and none may exceed the claimed peak; check this before filing.

## Previous filing path (POSR3F), from exec_r3f
`w_run.sh` (cycle.sh under memmeter) -> `w_finish.sh` (wait for the run, EXT = `extent=` of the ARENA line, `SIM_EXTENT=$EXT bash cycle.sh` using the cached run -> collect.py -> verify_collision.py -> build_package.py -> prefile_check) -> copy pkg_stage_exec to pkg_stage_exec_fix -> `research/launch/slotstage/slotstage_pareto.sh POSR3F poseidon 3 <pkg> <note> pos_posr3e` (stages, writes out/submit_POSR3F.sh, never runs it). FINISH_r4r5.sh follows the same steps with its own file names (logs/fin_*, pkg_fin) so it cannot clobber cycle.sh's output.

## Commands (WSL), run when the run has ended; each refuses with a message if it has not
```
cd './research/poseidon/orchard'
bash FINISH_r4r5.sh r4b        # collect, verify, build exec_r4b/pkg_fin + submission-note_fin.md, prefile, rulecheck, memory check; prints the stage command
bash FINISH_r4r5.sh r5b
bash FINISH_r4r5.sh r4mt       # pulls run.tmp/mem.tmp/single from the cloud first
```
Stage (needs the owner's go; admission of the round must be re-read from `yukon benchmark show` first; this only stages and writes an unrun submit script):
```
bash research/launch/slotstage/slotstage_pareto.sh POSR4E poseidon 4 research/poseidon/orchard/exec_r4b/pkg_fin research/poseidon/orchard/exec_r4b/submission-note_fin.md pos_posr3e
bash research/launch/slotstage/slotstage_pareto.sh POSR5E poseidon 5 research/poseidon/orchard/exec_r5b/pkg_fin research/poseidon/orchard/exec_r5b/submission-note_fin.md pos_posr3e
bash research/launch/slotstage/slotstage_pareto.sh POSR4M poseidon 4 research/poseidon/orchard/exec_r4mt/pkg_fin research/poseidon/orchard/exec_r4mt/submission-note_fin.md pos_posr3e
```
(or `bash FINISH_r4r5.sh <run> --stage`, which asks for a y before staging.) Only one r4 entry should be filed unless CyberAxe wants both (r4b is the single-thread run, r4mt the faster one; whichever ends first with the lower cost).

## What was tested / not tested
- Tested: `bash FINISH_r4r5.sh r3f-test` on the finished r3f output: parse, collect (1 collision), verify (reference ok, organizer ok), package (time 30.62543, mem 290,356,404 = score 38.73943, identical to the filed POSR3F numbers), prefile ALL PASS, memory check OK. It wrote only exec_r3f/logs/fin_*, data/*_fin.json, pkg_fin_test, pkg_fin_test_check, submission-note_fin.md.
- NOT tested: the r4b/r5b cache lookup (data/cache/<hash>/run.txt + mem.json appear only when cycle.sh finishes), the cloud pull for r4mt, the r4mt/r5 build_package paths on a real finished run (THREADS line, r5 SIM_EXTENT-less margin), the --stage branch. Not covered: trackcheck.py (a scratchpad script, not in the orchard folder) and the bench admission parse.
- If cycle.sh finishes first it already builds exec_rX/pkg_stage_exec itself (with the SIM_EXTENT it was started with: r4b used 1210405184, below the run's own extent 1,227,182,400); FINISH uses the run's own extent, as w_finish.sh did.
