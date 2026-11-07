# pkg6: state on 2026-10-06 (18:55), how to build it, what is owed before filing

Not part of the package. Nothing was staged, synced or submitted, and no `yukon` command was run. pkg6 is a
DRAFT: `SUBMISSION_STATE = "draft"` in `tools\pkg6_data.py`, and `blake3-r2\claim.json` says "draft".

## What pkg6 is

A package for the family with messages of 55 and 63 bytes (length XOR 8), pin H8, class eta = 830303cf (2^19
members), built from the filed `research\pkg5` (submission c47c1a80, 99.4) and the groundwork in `research\h8`.

| | pkg5 (filed) | pkg6 (draft) |
| --- | --- | --- |
| messages | 60 and 62 bytes | 55 and 63 bytes; B ends in eight zero bytes; w14 = w15 = 0, top byte of w13 zero |
| construction | nine state words, then alpha | context of seven words (vc, vd, S11, S4, X13, X14, w0), step T from y |
| trial replaces | w6..w11, w14 | w8..w11 |
| class | e7c1815f, 65,536 members | 830303cf, 524,288 members, 74,899 list words |
| count under the model | 29,977,922 | 162,266,763.66 (60 betas, 453 outcomes; 0.28 of it estimates) |
| count that H1 is set against | 29,965,882 | 126,003,600 (rule with five conditions) |
| assumed factor, margin | 2^23, 3.57 | 2^25, 3.75 |
| stage A, stage 2 | 64 + 36, 96 + 42, one eighth | 55 + 32, 115 + 48, one quarter |
| charged per trial | 17.4 | 19.1 (budgeted 18.2521) |
| time_log2 | 99.4 | 97.6 (total below 2^97.5186, stated bound 2^97.52) |

State of the rendered files at 18:51: `blake3-r2\proof.md` SHA-256 3e11b684...3fa2 (2,059 lines), `blake3-r2\claim.json`
1120292a...15ec, program d7a0e96a...16eb (unchanged since 14:44), manifest a87d654d...9338 (unchanged), note
5c4aa534...3e81. Local validation of 18:50 on exactly these files (`evidence\validation_log.txt`):
`mechanically_valid`, 176 repository tests OK (5 skipped), intake with the mirror copy marked ready: both experiments
passed, 256 of 256 each, replay identical. `evidence\selftest_pkg6_all.txt` (18:49): all steps of
`tools\selftest_pkg6.py` hold, exit status 0, on the proof and claim above; `evidence\selftest_pkg6_text_final.txt`:
the text steps once more after the last build (only the note changed in it: it quotes the validation log).

## Who did what

1. A helper agent built the experiment program and was cut off; a second finished its checks (three long self-tests
   of 1,000,000 batches, one per rule).
2. A third helper agent ported the text and wrote the data module `tools\pkg6_data.py` for this family.
3. Three reviewing helper agents (construction and exact part; count and cost; figures and public text) reviewed the
   files of 17:10. All three said "ready after minor fixes" and returned 22 findings, none above "minor". Their
   scripts and outputs are in `review\` (prefixes `construction_`, `count-cost_`, `judge_`).
4. A fourth helper agent began to apply the findings and was cut off at 17:56; a fifth (the author of this file's
   present form) finished at 18:55. THE CHANGES OF STEP 4 HAVE NOT BEEN REVIEWED. The sentences `EXACT_REVIEW`,
   `REVIEW_CLAIM`, `VERSION_REVIEW` in PART A of the data module say what was reviewed and by whom; change them
   when that changes.

## What the review changed (all 22 findings applied; none changed a claimed figure)

- `evidence\conservative_h8.txt` now has 453 of 453 base answers for cadical; `tools\conservative_h8.py` reports a
  problem when a base answer is missing.
- Extremes of one sample are worded as such ("in that sample"); a second seed of `tools\rule_share_h8.py` and the
  reviewers' programs give larger values (1.46 times 2^-4 and 2^-5), and the text says so.
- Rule A in the layout runs: all 24 runs and the 8 spread runs, from the raw run files, with three yardsticks
  (binomial; the runs' own scatter: 1.9 standard errors for the first eight, 1.0 for all 24; independent contexts).
  The eight spread runs are now described; four of the nine "beyond three standard deviations" lines are theirs.
- The shared structure of step S1 (the 2^19 pairs with one difference vc - vd give the same S, w0..w7, w12) is in the
  limits, the claim and the note. Checked here on 2,000 random contexts with the program's `context()`.
- The 54 answers "no violating solution": a third formula with DRAT proofs and a checker of a reviewing agent
  (`tools\rule_formula3_h8.py`, `rule_drat_h8.py`, `rule_drat_control_h8.py`, run by `tools\rule_drat_all.sh` in WSL),
  and an exact count split by the rule (`tools\n3_rule_h8.py`). The text says that no standard proof checker was used.
- Exact r_A under M is now stated: 144,123,441 for five conditions (162,243,610 for four, 123,244,449 for six). The
  claim still uses the conservative 126,003,600 (87.4% of it).
- "36,263,164 in all" in the introduction is now "about 36.26 million" (Section 10 has 36,263,162.6160 + 0.282).
- The independent recount is said not to have been blind (its request stated the total, four parts and "60 betas":
  `astra-jobs\server_tasks_2026-10-06\brief_for_gpt_sol.md` lines 43 to 58).
- The joint count "listed partial E3 event and the first four conditions" is reported against its exact share under
  M, 0.580935 (`tools\e3_rule_share_h8.py`).
- H3 states that what is budgeted is batches and gives the measured batch shares (0.1216 random contexts, 0.1133
  in the ranges of the algorithm, largest single context 0.1684 of 13,312); the statement itself is unchanged.
- Rule A with five conditions in the ranges of the algorithm (vd below 2^19, shared seed words, consecutive X14): on
  the processor, `tools\rule_share_h8.py layout 8 4 64 1`, and two programs of reviewers run again
  (`tools\rule_share_review_h8.py`, `tools\rule_layout_review_h8.py`).
- Real-message evidence brought up to date: the data module now adds the counts up itself from the raw run files in
  `evidence\h8\runs` (43 files: real40, real42, real45, the runs of 2^45 trials with seeds 8201 to 8205, layout runs
  1 to 24, spread runs 1 to 8, three model runs). Seed 8206 was still running at 18:47 and is not in; the script of
  the GPU agent goes on to 8208. Two per-context files of layout run 1 (`h8_ctx_run1_consecutive.txt`,
  `h8_ctx_run1_spread.txt`) were unused before and are quoted now.
- Section 8 names the step to the next pair (vc, vd), its end test and branch.

## The rule: how it was chosen (TARGET: margin of the conservative count over 2^25 at least 3.5)

`tools\outcomes_h8.py` assembles the 453 outcomes with their two factors, `tools\rule_a_sat.py N` puts the two solver
questions for the rule with N conditions (kissat), `tools\rule_a_sat2.py N solver` repeats them with a second formula
(cadical, cryptominisat5), and `tools\conservative_h8.py` adds up what is kept (`evidence\conservative_h8.txt`). The
seven betas that hold estimates (0.28) are left out.

| rule | outcomes kept of 453 | count for H1 | / 2^25 | / 2^26 | exact r_A under M | / 2^25 | stage A | budgeted (charged) | time_log2 at 2^25 | at 2^26 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 conditions | 132 | 162,241,316 | 4.83 | 2.41 | 162,243,610 | 4.84 | 52 + 31 | 23.503 (24.6) | 97.9 | 96.9 |
| **5 conditions** | 54 | 126,003,600 | 3.75 | 1.87 | 144,123,441 | 4.30 | 55 + 32 | 18.253 (19.1) | **97.6** | 96.6 |
| 6 conditions | 35 | 91,072,901 | 2.71 | 1.35 | 123,244,449 | 3.67 | 58 + 33 | 15.913 (16.7) | 97.4 | 96.4 |

The rule with five conditions is the cheapest one whose conservative count has a margin of 3.5 or more
(`RULE_CONDITIONS = 5`; `derive()` and `build_tokens()` stop if that is no longer true). With factor 2^26 no rule has
the margin by either column. The column "exact r_A" is `evidence\n3_rule_h8.txt` (a reviewer's exact count, run
again here; it agrees with the calculator on every N3 of the betas counted in full and with the solvers on which
outcomes have no violating solution). THE OWNER DECIDES rule, factor and charge.

## Decisions for the owner (facts from the review, not recommendations)

1. Rule, factor, charge (table above). Charges from 18.26 to about 18.85 print 97.5 at factor 2^25; 19.0 and 19.1
   print 97.6 (the 4.6% cushion was meant for the cost per pair, which is a share 2^-40).
2. What H1 is set against. Against the exact r_A the rule with six conditions has a margin of 3.67 at 2^25 and
   would print 97.4. The exact count is one agent's program, rerun here and consistent with the solvers; the rule
   with six conditions has no measurement on the graphics card, and its sixth condition joins bits 0 and 31 of z:
   the build writes Lemma A (c) for it, and nobody has read that text.
3. H3 on trials or on batches. The text keeps the statement on trials (budget 1.142 times 2^-5 on average) and
   reports the batch shares beside it. A batch budget of 3/16 or 1/5 would give 16.80 or 17.09 budgeted per trial
   (recomputed here; that prints 97.4 with a margin of 1% on the charge and 97.5 with the 4.6% of this package),
   but H3 would then rest only on the measured clustering of passes inside batches, with no uniform-word argument
   behind it (the count-cost reviewer's remark).
4. drat-trim is not installed in WSL; with it the 54 proofs could be checked by a standard checker
   (`tools\rule_drat_h8.py` uses it when it finds it).
5. The answer file of the recount names its author as "Codex"; the package credits "GPT Sol 6.1 (OpenAI)", as the
   brief and `research\h8\reports\r4_gpt_sol_recount.txt` do. Confirm the name.
6. Whether the constant X3 = 29d4fa98 may stand (`research\public_text_scan.py` reads three of its digits as a
   listed word; `tools\text_scan_pkg6.py` takes the six constants out of a line before its word test and says so);
   and whether the organizer's rules allow the 2-round compression inside the experiment program (as in pkg5).

## One place each

- The rule: `RULE_CONDITIONS` in PART A of `tools\pkg6_data.py`. The build writes it into the program.
- The factor: `LOG2_FACTOR` in PART A; the program's line `TRIALS_LOG2` is 127 minus it (written by the build).
- The charge: `CHARGE`; the bound on the work per value of X14: `PREP_OPS` (1024; counted 163).
- The runs of `tools\rule_share_h8.py` that are quoted: `RULE_SHARE_H8_RUN`, `RULE_SHARE_H8_SECOND`,
  `RULE_SHARE_H8_LAYOUT`. Their files are used only while they name the SHA-256 of the program AND of the tool.
- A change of rule or factor changes the SHA-256 of the program. Then run again, in this order:
  `tools\selftest_big_launch.sh` (long self-test of that rule, about an hour), the three runs of
  `tools\rule_share_h8.py` (command 3 below), `python -B tools\prep_count.py`, `python -B tools\lane_bound.py 2000`,
  the build, `tools\selftest_pkg6.py`, the validation. The solver files do not depend on the program. The paragraphs
  on rule A on the processor are written for five conditions and stop the build for another rule.

## Commands (Windows, from `research\pkg6`, unless WSL is named)

1. `python -B tools\fetch_h8.py` (copies the groundwork's result files to `evidence\h8` and the raw run files to
   `evidence\h8\runs`; a run file below 3,000 bytes is still being written and is left out). Running it again
   takes the runs that have finished since, and the build then changes every pooled figure of Section 10.
2. `python -B tools\outcomes_h8.py`; in WSL `bash tools/rule_a_sat_all.sh` and `bash tools/rule_a_sat2_all.sh`
   (about two minutes each, three threads); `python -B tools\conservative_h8.py`; `python -B tools\n3_rule_h8.py`
   (two minutes); `python -B tools\e3_rule_share_h8.py`. Only when the count changed.
3. `python -B tools\rule_share_h8.py 2048 1`, `... 2048 2`, `... layout 8 4 64 1` (two minutes each),
   `python -B tools\rule_share_review_h8.py 1024 12 192` (five minutes), `python -B tools\rule_layout_review_h8.py`
   (four minutes; it imports `review\construction_impl.py`). One thread each.
4. `python -B tools\build_pkg6.py` (renders proof, claim, manifest, note; runs the short self-test of the program).
5. In WSL `bash tools/rule_drat_all.sh` (one minute, two workers; after a build, because the first program compares
   the table of kept outcomes printed in proof.md). Its files do not change the text unless a count changes.
6. `python -B tools\proof_lines_check.py` after any change of `src\proof_head.md`, then the build again;
   `python -B tools\fmt_pkg6.py`, `python -B check_pkg6.py --text`, `python -B tools\text_scan_pkg6.py`.
7. `python -B tools\selftest_pkg6.py > evidence\selftest_pkg6_all.txt` (two to three minutes; all steps).
8. `wsl -d Ubuntu -- bash "./research/pkg6/validate_pkg6.sh" check tests intake-ready`
   (mirror `~/hashsmash/hash-smash`, not the Yukon checkout; compare the SHA-256 lines it prints with the files),
   then the build once more: only the note changes (its "Checks performed" quotes the validation log).
9. The independent recount: `evidence\gpt_recount\` holds the program of GPT Sol 6.1 as copied at 16:17
   (`gpt_sol_independent_a.rs`, 36,630 bytes, SHA-256 bd50b209c4aece2e65d8e6da894e5b460117ac058b6903be367a758a270e9fc3),
   the binary rebuilt here with `rustc -O`, and the log of the rerun (`recount_rebuilt.exe all32`, five minutes).
   The file of that name in `astra-jobs\server_tasks_2026-10-06\` was changed by the other model's agent afterwards
   (17:06, 50,360 bytes, SHA-256 576da1ee...7833); two reviewers rebuilt and reran the copy of the package with the
   same result.

## Owed before filing (in order of weight)

1. A check of the changes made after the review (step 4 of "Who did what"), and a reading by a person: no person has
   read any of the text.
2. Scaled-down end-to-end runs for THIS family (lengths 55 and 63, steps S1 and T, a first-stage rule). The filed
   package has them for its own construction; this package has none and says so in the proof, the claim and the note.
3. Rule A with all five conditions on the graphics card, in layout runs. The GPU programs record the first four
   conditions only; the fifth exists only in processor runs of 2^29 to 2^32 trials. And the cause of the dependence
   of the rule's pass rate on the context is not analysed.
4. The owner's decisions above.
5. The work per pair (vc, vd) is bounded in words (below 2^11) and not counted on the machine; it does not show in
   the result (2^62 operations against 2^106).
6. A last `tools\fetch_h8.py` and build when the GPU runs with seeds 8206 to 8208 have finished, if their figures
   are wanted in the text (then commands 4, 6, 7, 8 again).

## Not established (stated in the text as limits)

- H1, H2, H3. The model fails inside one context for rule A; only averages over contexts agree with it. Every
  statement about the rule's pass rate and the stage-2 budget is about averages over contexts.
- The answers "unsatisfiable" behind "no further beta has a part" (129,147 betas) have no certificates. The 54
  answers behind the count of the rule have proofs that only a participant-side checker accepted, and an exact count.
- The independent recount was rerun and compared beta by beta, not reviewed line by line, and was not blind.
- No measurement has the groups of 2^19 pairs with one difference vc - vd, or a whole run with shared seed words.
- In the six processor samples for which a standard error is given, the mean share of rule A is 0.06% to 0.23%
  below 2^-5, each within 1.6 standard errors; over windows of 1,024 consecutive X14 a reviewer's six pair means
  are 0.02% to 0.08% above. Neither was followed up; both are far inside the budget.

## Later improvement, not in this version

A cheaper two-level arrangement of the trial is being built by another agent in `research\h8\twolevel`
(`research\night\main\NOTES.md` section 11); it is not used here.
