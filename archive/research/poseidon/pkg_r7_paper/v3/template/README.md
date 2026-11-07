# Poseidon "algebraic paper" package template (rounds r >= 7)

Status: TEMPLATE, nothing staged, nothing submitted, nothing run on the cloud box. Built 2026-10-15 from the executed r = 5 package (`orchard/exec_r5tt/`: `pkg_fin/proof.md`, `claim.json`, `submission-note_fin.md`) and the organizer docs `CANDIDATE_QUALIFICATION.md` (items 1-5) and `HEURISTIC_EXPERIMENTS.md`.

## Files

| file | what it is |
| --- | --- |
| `proof_template.md` | proof.md with placeholders. Sections 2, 3, 4.3, 4.4 are copied verbatim from `exec_r5tt/proof_template_exec.md` (lines 15-56 and 96-124); 1, 4.1, 5-11 are new. |
| `claim_template.json` | claim.json (schema v3, exploratory lane): score-critical `H_root`, supporting `H1-charging-rules`, empty certificates, experiment manifest. Not valid JSON until the numeric placeholders are filled. |
| `note_template.md` | submission note (about 9.7 KB, rule: at least 5 KiB), credits first, "A credit is not an endorsement" line. |
| `experiments/manifest.json` | experiment manifest (2 entries, `python-message-pairs-v1`, event `full-collision`). |
| `experiments/replay_pairs.py` | experiment (a): replay of the recorded r = 3, 4, 5 pairs (7.4 KB). |
| `experiments/toy_root_fraction.py` | experiment (b): small-field analogue, exact fraction of centres with a usable root (5.3 KB). Sources total 12.7 KB, limit 64 KiB. |
| `certificates/manifest.json` | empty manifest (copied from an organizer candidate). |
| `values_example.json` | every value `assemble.py` needs, with `TODO` where another agent or the filing day supplies it. |
| `assemble.py` | `python assemble.py VALUES.json SRC_DIR OUT_DIR`: fills placeholders, derives the sizes, appends the C sources as the proof appendix, computes the proof line ranges that claim.json cites, refuses on any leftover placeholder or `TODO`, checks the note is at least 5 KiB, copies experiments and certificates. Runs nothing from the sources. |

Dry run done: with dummy values for the TODO items it produced a claim.json that parses, a 37.5 KB proof body and a 9.5 KB note with no leftover placeholder.

## The shape of the claim (decisions to confirm)

* Event of the premise. The brief said "g has a root in F_p with probability >= q (1 - 1/e asymptotically)". The collision needs a root that is a NONZERO SQUARE (the gcd is against S^((p-1)/2) - 1; a nonsquare root gives s outside F_p). For a random polynomial the usable roots are Poisson with mean 1/2, so the asymptotic value of the usable event is 1 - e^(-1/2) = 0.39347, not 0.63212. The template uses the usable event, with `1 <= deg G <= DMAX` (`DMAX = 16`, Poisson tail below 2^-60) so that the root-isolation step has a provable cap. Default `Q = 0.3934`. The 1 - 1/e wording appears in the premise only as the "a root of any kind exists" value.
* Centres are the algorithm's coins (pattern 3), not `c_i = i`: only then does "P over the algorithm's coins for the fixed target" exist, and the K events become independent by construction (parameter rho = fraction of good centres of the fixed F; the premise is `rho >= q`). Cost: coin words must be charged and the source differs from the r5 source (below).
* Isolation lemma (proof section 9.3) is a proved statement (character sum), not a premise: failure of stage E, given a usable root, is at most 2^-48 for `DMAX = 16`, `Z = 64`.
* `K` default 2: bound 0.63203; K = 1 gives 0.3934, only 0.0034 above 0.39, which the sensitivity table shows is a thin margin. K = 2 survives q down to 0.21898. Time bound grows by log2(K).

## Placeholders (all)

Derived by `assemble.py` from `R`, `K`, `Q`, `N_BOUND`, `MEM_BYTES` (checked against the r = 3, 4, 5 values of `build_package.py`): `DEXP D M M1 H HEXP N2 N2_HALF AEXP VEXP STEPS C PARTIAL PARTIALRS PARTIAL_WORD LAYERS LINE UNITS TIME_LOG2 TIME_LOG2_EXACT MEM_LOG2 MEM_PEN SCORE P_SUCC P_SUCC_EXACT EPS_SUM Q_MIN_K Q_RATIO_K` and the proof line ranges `LN_PREMISE LN_EVIDENCE LN_LEDGER LN_SOURCE_HEAD` (evidence_ids of claim.json). `C = 216 + 21 R` is the reduced-permutation charge of the earlier packages; confirm it for the r >= 7 cost model before using it.

From `..\LEDGER.md` (the ledger agent): `N_BOUND` (integer N_max), `MEM_BYTES`, `HGCD_BOUND`, `COIN_WORDS`, `COIN_WORD_COST`, `COIN_RULE` (the template suggests a 320-bit word reduced mod p, eps_coin below 2^-65), `CHARGING_RULES` (section 4.2 without threads, plus coin and isolation charges), `LEDGER_SECTION`, `LEDGER_RECOMPUTATION`, `MEMORY_SECTION`.

From the build: `BUILD_COMMAND`, `RUN_COMMAND`, `SOURCE_FILES` (names under SRC_DIR), `SOURCE_INTRO`, `FD0` (leading coefficient of F on the line at this r, the r5 build tool computes it with the reference).

Fixed per round, in `values_example.json`: `R`, `K`, `Q`, `DMAX`, `Z`, `EPS_COIN`, `EPS_ISO` (+ numeric `EPS_*_NUM`), `TRIAL_MEM` (about 136 GB at r = 7) and `TRIAL_WORK` (about 4.3 x the r = 6 trial), both from the coordinator, not measured by this template.

Filing-day items:
* `R6_*` (`R6_MAX R6_PHRASE R6_NOTE_SENTENCE R6_CENTRES R6_OUTCOMES R6_SUCCESSES R6_N R6_TIME R6_MEM R6_THREADS_WALL R6_STATUS R6_COLLISION`). Defaults say "run in progress". The r = 6 run started 2026-10-15 18:53:11 UTC, 24 threads, 40-55 h per trial; its numbers come from `orchard/exec_r6mt` run.tmp on the cloud box (not touched here). When it ends set `R6_MAX` to 6, `R6_PHRASE` to " and 6", fill the row.
* `R6_PAIR` (the comment in `experiments/replay_pairs.py`): append `(6, centre, nk1, rho1, nk2, rho2, digest)` to `PAIRS`, then re-run the replay locally. Only if r = 6 finishes with a collision.
* `REPLAY_RESULT`, `TOY_RESULT`: our local plain-Python results, prefilled (see below); re-fill after any change to the sources.
* `EXECUTOR_STATUS_SENTENCE`: say what is true on the filing day about the organizer executor.
* `MODEL_NAME HARNESS_NAME CREDIT_LINES`: note header and credits (the r5 note had no credits block, only the inline citation of Bariant et al.; the credit-first form and the "not an endorsement" line are copied from the accepted sha3 dossiers).

## Source delta the ledger agent must build (not done here)

The r5 source cannot be shipped as is: (1) the centre is `c_i = i` and must become a coin draw; (2) `MAXTR` 64 becomes `K`, tested at the start of each trial; (3) stage E (random shifts for `deg G >= 2`, seeded constant, uncapped) must become the capped isolation of proof 4.1.2, with `deg G > DMAX` a failed trial; (4) a failed-run exit (status 2, no output) and a success exit; (5) single thread, with all thread code, `thread_control` and `split_extra` removed from the source and the ledger (the proof says "no dispatch"); (6) the report/exit charge becomes a worst-case constant. The proof sections 4.1, 4.2, 6, 7, 11 are written for that program.

## What was run, and what was not

Run here (plain Python 3.14.3 on this machine, not through the organizer executor):
* `replay_pairs.py` fed a request on stdin: 3 of 3 pairs verified, 0.07 s. The same three pairs also agree with the organizer's own `verifier.poseidon.digest` in `pareto_clone` (run locally on our own pairs).
* `toy_root_fraction.py`: about 5 s on this machine; p = 8017, L = 3 and 4; line check, degree check pass; 3,145 / 8,017 and 3,166 / 8,017 centres with a usable root (random table: 3,145 and 3,179).
* `assemble.py` with dummy values (output discarded).
* The claim.json shape (with numeric placeholders replaced) parses as JSON and its heuristic statements are under the 4096-character limit; its restriction strings are under 1024.

NOT tested:
* Neither experiment has run through the organizer executor (Docker, 128 MiB, 1 CPU, 20 s default timeout, run twice for the reproducibility check). The runner in `pareto_clone/experiments/runner.py` calls `digest_fn(b"")` for every `python-message-pairs-v1` experiment; the Orchard digest accepts only 64-byte messages and raises on the empty one, so every Poseidon experiment fails until the organizers fix the runner. These experiments cannot run through the executor until that fix lands. The toy experiment takes about 5 s here; the executor is slower and runs it twice, with an unmeasured margin to the 15 s target (reduce `next_prime(8000)` if the first run is slow).
* Whether the executor accepts experiments whose trials all return null messages (the runner code says a null pair is a failed trial, `no_pair_returned`, which is allowed). Whether the judge treats two experiments with zero checked successes as adequate support is unknown.
* The Python experiment `observations` limit (16 numeric keys per trial) is met (toy: 13 keys); the toy sources use `random.Random(str)` seeding, stable across CPython 3.x.
* `claim.json` against `pareto/schemas/claim.json` with real numbers; `local_tracks.py check`; the r >= 7 target profile claim shape (the clone has profiles up to r56, the claim schema lists poseidon-orchard-r0..r56).
* No small faithful analogue at the deployed field exists in pure Python within 15 s: building the odd part and testing its roots at the deployed 255-bit prime costs about a second per centre even at degree 125 (254 squarings modulo a degree-62 polynomial, estimated, not measured), too few centres to say anything. The toy experiment therefore changes the field, the constants and the degree (a 13-bit prime, seeded random constants, degree 125 and 625) and says so in its docstring and in the proof.
* The premise itself, at any r: unproved and untested at the claimed degrees. Statements about r = 1 and r = 2 in proof 10.3 and in the note ("settled by a proved bound or by the executed run") were taken from the coordinator's brief and the r5 note and were not re-verified against those filings.
* The worst-case ledger formula (another agent).
