# pkg5: what it is, how it is built, and the steps for the day the owner says go

Not part of the package. Written 2026-10-06 by the helper agent that assembled pkg5. Nothing was staged, synced
or submitted, and no `yukon` command was run.

## What pkg5 is

A DRAFT (`"submission_state": "draft"`) that extends the unfiled draft `research\pkg4` (100.4). Same pin B, same
class eta = e7c1815f, same assumed factor 2^23, 2^104 trials. New: the two-stage batch.

| | pkg4 | pkg5 |
| --- | --- | --- |
| batch | one stage, 154 operations + 74 loads | stage A 64 + 36 = 100, stage 2 96 + 42 = 138 |
| test in the batch | early test of Lemma E | rule A (six bit conditions on h1), then the E1 test of Lemma N |
| charged per trial | 34 | 17.4 (budgeted 16.756, expected at most 16.448) |
| count that H1 is set against | 29,977,922 | 29,965,882 (40 of 287 outcomes left out, 12,040) |
| heuristics | H1, H2 | H1, H2 (E1-test passes, 2^-16 of the trials), H3 (stage-2 entries, one eighth of the batches) |
| advice | 2^5 bytes | 2^6 bytes (three constants of rule A) |
| time_log2 | 100.4 | 99.4 (total below 2^99.39) |

Where the figures of this table come from: `tools\pkg5_data.py` (PART A and `derive()`), the self-test of
`blake3-r2\experiments\halfsearch.py`, `evidence\rule_a_sat_e7c1815f.txt`, `evidence\pairs_recount_e7c1815f.txt`.

Three things differ from the brief that the main session wrote for this package, and why:

1. Stage 2 is 138, not 134: the algorithm counts the batches that enter stage 2 against a budget, and that count
   (one addition, a comparison with a loaded constant, a branch: 3 operations and 1 load) is in the machine count.
2. The stage-2 budget is one eighth of the batches (0.125), not 0.115. Seven times the measured pass rate of rule A
   is 0.10937; one eighth is 14% above it, 0.115 would be 5% above. The wider budget costs nothing in the claim.
3. The charge is 17.4, not 17.2: with 138 and one eighth the budgeted cost is 16.756 per trial, and 17.4 keeps a
   margin of 3.8% (pkg4 has 4.4%). The claim is 99.4 either way; the total is below 2^99.39 (with 0.115, 134 and
   17.2 it would be below 2^99.37).

## Files that hold results (all read by `tools\pkg5_data.py`; no figure is typed into a template)

- `evidence\pairs_recount_e7c1815f.txt`: both factors of every outcome with a nonzero product (from pkg4).
- `evidence\rule_a_sat_e7c1815f.txt`: kissat per outcome, with and without "h1 violates rule A"; one complete
  solution that violates rule A (`tools\rule_a_sat.py`, then `tools\rule_a_sat.py example`; WSL, under a minute).
- `evidence\calc2_recount_e7c1815f.txt`, `calc2_total_e7c1815f.txt`, `calc2_flagged_e7c1815f.txt`: recounts with
  the binary `~/hashsmash/bin/night_pair_calc2`, only executed (`tools\recount_calc2.sh mass | all | flagged`;
  "all" took 34 minutes with four threads).
- `evidence\selftest_1200000_61.json`, `_62.json`: the program's self-test with 1.2 million batches each
  (`tools\selftest_big.sh`); quoted only while the program has the SHA-256 written in their first line.
- `evidence\followup\`: copies of the result files of the thread that found rule A (`research\night\cheaper`).
- `evidence\validation_log.txt`: the last local validation; quoted in the note only while the candidate files
  have the SHA-256 listed in it.
- `evidence\rule_a_sat2_cadical_e7c1815f.txt`, `rule_a_sat2_cryptominisat5_e7c1815f.txt`: the questions on rule A
  with a second CNF formula and two other solvers (`tools\rule_a_sat2.py cadical 4`, then `cryptominisat5 4`; WSL,
  under a minute each). The formula is a reviewer's (`review\judge_sat.py`).
- `evidence\rule_share_20261006.txt`: rule A and the batches that enter stage 2 on real trials in the layout of
  6.4, 24 samples of 2^30 trials (`tools\rule_share.sh`; WSL, gcc with OpenMP, two minutes with four threads).
  The C program is a reviewer's (`review\math_rule_share.c`); the file is quoted only while `tools\rule_share.c`
  has the SHA-256 in its first line.
- `evidence\rule_share_seeds_8192_15_0.txt`: the same over 8,192 sets of seed words with 2^15 sampled batches
  each (`python -B tools\rule_share_seeds.py 8192 15 4 0`; Windows Python, it needs numpy; about a minute). The
  program is a reviewer's (`review\judge_h3.py`).
- The reviews of pkg4 are in `research\pkg4\review\`; pkg5 quotes them from there. pkg5 was reviewed once, on
  2026-10-06, by three helper agents (mathematics and cost, figures, a hostile judge); their programs and outputs
  are in `review\`, their findings were worked in the same day (round 1). A fourth helper agent then read proof,
  claim, manifest and note in full, checked round 1 against the files, and ran the validation and the three
  reviewer programs again with the same output (`review\wf6_recheck.json`); its four small findings were worked in
  the same day (round 2, at the end of this file). What was changed in round 2 has not been reviewed.
  `VERSION_REVIEW` and `VERSION_REVIEW_PROOF` in PART A are the sentences of the note and of the proof that say
  so ("what was changed after that check has not been reviewed"); the build stops if one of the three result files
  above is missing while they say this.

## Build and local validation (all of this was run for the state described in the report)

All Windows commands from `./research/pkg5`.

1. Build: `python -B tools\build_pkg5.py`. Last line must read
   `claim: time_log2 99.4, factor 2^23, trials 2^104, charge 17.4, count with rule A 29,965,882 (all solutions 29,977,922), class e7c1815f`.
2. Self-test and cross-checks: `python -B tools\selftest_pkg5.py` (about three minutes). Must end with
   `RESULT: all steps hold`. It runs the program's self-test (2,000 batches, every lane against the complete digests
   of its two messages), the comparison with `research\night\cheaper\night_batch4.py`, the comparison of the
   program's reference values with `check_pkg5.py`, one full class loop, `tools\fmt_pkg5.py`, `check_pkg5.py` and
   `tools\text_scan_pkg5.py`.
3. Validation in the WSL mirror (not the Yukon checkout):
   `wsl -d Ubuntu -- bash "./research/pkg5/validate_pkg5.sh" check tests intake-ready`
   Must show `"status": "mechanically_valid"`, `Ran ... tests ... OK`, `experiment status: passed`, both experiments
   `trials=256 successes=256 ... replay identical=True`, and `exit status 0`. It overwrites the candidate in the
   mirror `~/hashsmash/hash-smash`; `research\validate_track.sh blake3-r2 check` puts the live candidate back.
4. Build once more (only the note may change: its "Checks performed" quotes the log), then
   `python -B tools\fmt_pkg5.py` must end with `RESULT: nothing wrong` and `python -B tools\text_scan_pkg5.py`
   with `findings 0`.

## If the owner says go for THIS package (nothing below was executed or prepared)

- The text as changed after the first review (rule A wording, the three reruns of the reviewers' programs, H3 with
  the measurements in the layout of 6.4) was checked by a fourth helper agent. Only the four changes of round 2
  (at the end of this file) have not been seen by any reviewer; they are small, and the two sentences on the
  reviews say that later changes are unreviewed. After another review, or a change of substance, change
  `VERSION_REVIEW` and `VERSION_REVIEW_PROOF` in PART A.
- The owner has not yet confirmed that the organizer's rules allow a 2-round compression inside the experiment
  program (`compress2`, called only to check the counted batch). `docs\HEURISTIC_EXPERIMENTS.md` of the organizer's
  repository asks for the standard library and deterministic code and says nothing against it.
- Set `SUBMISSION_STATE = "ready"` in PART A, then steps 1 to 4 again (proof.md does not change, claim.json does).
- `research\public_text_scan.py` does not look at pkg5; `tools\text_scan_pkg5.py` applies its word list and
  patterns to pkg5 and adds paths, account names, addresses and keys.
- A full backup with `backup-project.ps1` before staging, as for every major change.
- There is no staging script for pkg5. `research\launch\194_presubmit_4.sh` stages pkg4; a copy for pkg5 would
  call `research\sync_any.sh` with `research/pkg5/blake3-r2` and `research/pkg5/submission-note-r2.md`. The main
  session writes and runs it, and `research\submit_r2.sh` after it, only after the owner's go for this package.

## The cautious variants

- Factor 2^22: `log2_factor=22` in the entry of the class in PART A. The build then writes 2^105 trials and
  time_log2 100.4; nothing in `src\` changes. The line `STAGE_2_BUDGET` of the program is rewritten by the build,
  so the long self-test files no longer match the program and are not quoted until `tools\selftest_big.sh` is
  run again.
- Without rule A the package is pkg4.

## Changing the class or the rule

`ETA` and `RULE_A` in PART A, with entries in `CLASSES`; then `tools\fetch_totals.sh`, `tools\recount_exact.sh`,
`tools\rule_a_sat.py` (both forms), `tools\recount_calc2.sh`, `tools\selftest_big.sh` and all steps above. The
files in `evidence\followup\` are for class e7c1815f and rule A6 only; the data module raises an error or leaves a
sentence out when they do not fit. The three programs taken over from the review (`tools\rule_share.c`,
`tools\rule_share_seeds.py`, `tools\rule_a_sat2.py`) have the constants, the class and the rule typed in; the data
module compares them with PART A and stops, or leaves the measurement out, when they differ. They must be edited by
hand and run again.

## Round 1 after the first review of pkg5 (2026-10-06)

What changed, by file. `blake3-r2\experiments\halfsearch.py`: its opening comment only (no BLAKE3 library is
imported; the file has its own 2-round compression, called only to check the counted batch), so its SHA-256
changed and `tools\selftest_big.sh 1200000 61 62` was run again. `src\`: the wording on what is dropped (a batch,
not a trial), solver answers stated as answers, the table of the 40 outcomes left out, the betas the rule was read
from against those added later, the two measurements in the layout of 6.4, the second formula and two more
solvers, H1 and H3 evidence ranges (6.3, 6.4 and 6.5 added), the sensitivity sentence (total below
2^(122.39 - log2 f)), six decimals for the two logarithms of Section 8, "of rule A" in the meaning of
preprocessing_log2, the manifest's sentence on batch_stage_2_entered. `tools\pkg5_data.py`: the readers of the
three new result files and the sentences above; `tools\build_pkg5.py`: the ranges and one empty line before
Section 10. The claim did not move: time_log2 99.4, total below 2^99.39.
