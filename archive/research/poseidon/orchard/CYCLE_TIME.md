# Poseidon single-centre entry (single_r1, cap 6): cycle time

Measured 2026-10-13 00:15-00:30 on the shared machine (load ~93% from other jobs, jobs run at nice 10, at most 2 heavy processes).
"Before" = the steps run by hand with the old scripts, one after the other. Times are wall seconds from the logs (`logs/*.txt` secs columns) or measured once.
"After" = `bash single_r1/cycle.sh` (WSL), first run `--fresh`, then a second run with everything cached.

| # | step | old script | before (s) | after, fresh (s) | after, cached (s) | depends on |
|---|---|---|---:|---:|---:|---|
| 1 | build + compile (8 C files, -O3) | build_cap.sh | 8 | 9 | 0.1 | all counted C sources and headers |
| 2 | line / polynomial setup | inside the ledger run (stages `line setup`, `B: build g`: 0.7 s) | 0 | 0 | 0 | - |
| 3 | instrumented ledger run, seed A (cap 6; stages init..G, 9.1 MB heap) | run_cap.sh / run_final.sh | 94-100 | 100 (parallel with B) | 0.3 | counted sources + seed |
| 4 | second certificate run, seed B | run_cap.sh again | 94-100 | (in parallel with 3) | 0.3 | counted sources + seed |
| 5 | verbose run for the powering breakdown | run_final.sh seed 1 | ~95 | 0 (every ledger run is verbose; printing only) | 0 | - |
| 6 | 64 KiB stack-limit run (claim of the proof) | run_stack.sh | ~95 | 0 (ledger runs execute under `ulimit -s 64`) | 0 | - |
| 7 | calibration of root isolation levels | run_calib.sh (14 levels, d up to 39062) | 156 | 7 (levels 4, 9 only: all that cap 6 can reach) | 0.4 | libs + calib.c |
| 8 | worst-case gcd/division bounds `gcdbound H` | run_gbH.sh | 297 (with MONO checks) | 71 (MONO skipped under cap; header byte-identical) | 0.3 | libs + gcdbound.c |
| 9 | gcd memory at d = 39062 `test_keep` | run_k.sh / run_misc.sh | 10 (the logged copy was stale: 6.39e9 charge vs 1.51e9 now) | 0 (not reachable under cap 6) | 0 | libs + test_keep.c |
| 10 | half-gcd vs Euclid tests | run_tests.sh | 18 | 18 | 0.3 | libs + test_hgcd.c |
| 11 | split tests (d up to 12000) | run_tests.sh | ~45 | 0 (not reachable under cap 6; still in run_tests.sh) | 0 | - |
| 12 | collect + verify collisions | collect.py, verify_collision.py by hand | ~1 + typing | 0.4 | 0.4 | ledger logs |
| 13 | package: proof.md, claim.json, certificates, note | build_package.py | 0.2 | 0.2 | 0.2 | logs, proof_template.md, note_tail.py |
| 14 | prefile_check | launch/prefile_check.py by hand (needs a hand-built folder) | 0.2 + assembly | 0.2 | 0.2 | package |
| | **total** | | **~920 serial (15 min)** | **181 wall (3 min)** | **2.8** | |

Note-only or template-only change: steps 3-12 are cache hits; the cycle takes about 3 s.
Kernel change (any counted C source): everything keyed on it re-runs: 181 s (before ~920 s plus the hand work between scripts).

## Top 3 time sinks (before)
1. `gcdbound H`: 297 s, of which about 226 s are the monotonicity (MONO) re-derivations for levels > 152. Those levels never run under cap 6 and the MONO lines go to stderr only; the header is unchanged without them (byte-identical, checked).
2. Counted ledger runs: ~95 s each and run 4 times by hand (ledger, verbose breakdown, stack-limit, certificate seeds). The verbose flag only prints (`quiet == 2`, counters untouched) and the stack limit does not change counts, so one run per seed carries all three roles.
3. Calibration `calib` at all 14 levels: 156 s, 122 s of it in levels 19531 and 39062; cap 6 never reaches them (root isolation starts at degree 9). Only levels 4 and 9 are needed and they come out identical to the full run (checked line by line).

Redundant work removed: the three roles of the ledger run, the unreachable big calibration levels, `test_keep` and `test_split` for a capped program, the MONO checks, hand-assembling the folder for prefile, recomputation of anything whose source hash did not change.

## Proof that counts are unchanged
- Uncached (`--fresh`) and cached run: ledger signatures (every stage line without seconds, SUMMARY, TYPES, gcd line, RESULT, COLLISION lines) identical for seeds 110 and 103 (`ledger counts vs previous run: identical`).
- The new fresh run (verbose, `ulimit -s 64`) against the earlier unmodified run `logs/cap6_110z.txt`: all count lines identical (SUMMARY total_all = 10,393,434,884 in both); the only difference is the extra printed `lean-pow breakdown` line.
- No counted source file was edited. Changed files: cycle.sh (new), collect.py, build_package.py, note_tail.py (optional environment variables; defaults reproduce the old behaviour), this file.

## What still takes longest
- The two ledger runs (~100 s each, in parallel): they execute the counted program (238 squaring steps of a 39062-degree powering plus the half-gcd), and they are the evidence itself. With a third lane they would still take 100 s; only a faster counted kernel would shorten them.
- Then `gcdbound H` (71 s with the MONO checks skipped), which runs whenever any library source changes.
- twofam_r1 for comparison: run_calib.sh 322 s, attempts run one after another (`run_attempt.sh`), no cache, then stage_pkg.sh by hand.

## Open items found
- prefile_check.py fails two checks for this entry for reasons that are not the package: its ledger regex needs N of 16+ characters (`N = 12,228,056,351` has 14), and it requires the claim to match the ledger print within 5e-6 / 1e-4 while build_package claims `ceil` to 3 decimals (claim 25.621, exact 25.62073). Evidence estimate ~334,480 B passes.
- The proof template still describes the uncapped program ("Variant with a cap (not the program of this document)", stage E schedule from 39062, calibration at all levels, `PEAK_GCD` printed as 0 in cap mode); the cap-6 numbers are computed, the text needs an author pass.
- The success probability section is still a placeholder (PCLAIM 0.3934 is not adjusted for the cap loss).
- `stage_pkg.sh`-style copy into the WSL clone and `pareto_candidate.py` are not part of cycle.sh.
