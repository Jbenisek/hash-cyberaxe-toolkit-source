# BUILD #1 Poseidon r7 algebraic paper entry: draft staged (nothing submitted, nothing run on the target)

Folder: research\poseidon\pkg_r7_paper\ (ledger.py copy, template copy, ledger_out.txt, LEDGER_copy.md, values_r7_draft.json, out_draft\). algebraic_paper\ was read only.

## Ledger (COMPUTED, ledger.py copy, 7 s; its LEDGER.md output is byte-identical to the one in algebraic_paper)
Validation reproduces: model above measured at r3/r4/r5 by 0.0055/0.0059/0.0072 bit, heap peaks exact.
| r | m | N | memory B (log2) | K | total ops | time_log2 | score |
| 6 | 122,070,312 | 3*2^27 | 36,546,584,276 (35.090) | 1 / 2 | 7.767e13 / 1.5534e14 | 37.72457 / 38.72456 | 52.81457 / 53.81456 |
| 7 | 610,351,562 | 3*2^29 | 159,963,342,164 (37.219) | 1 / 2 | 3.6085e14 / 7.2170e14 | 39.85457 / 40.85457 | 57.07357 / 58.07357 |
r7 K=2: N_BOUND = 721,698,655,708,975 ops, heap peak 135.9 GB, arena 159.96 GB. Generic Poseidon is 127.009. Score = ceil5(time) + ceil3(log2 mem) - 20 (ledger convention, not re-derived).

## Draft package (COMPUTED by template\assemble.py, K=2, Q=0.3934, DMAX=16, Z=64)
out_draft\: proof.md 52,316 B, submission-note.md 9,651 B (>= 5 KiB ok), claim.json 6,079 B. claim.json: time_log2 40.85457, memory_log2_bytes 37.219, success_probability 0.63203 (DERIVED: 1-(1-0.3934)^2). The template has no separate intake/prefile script; assemble.py's own checks passed (placeholders, note size, derived bound >= 0.39). The organizer prefile/intake was NOT run.
The draft is filled with "DRAFT-PENDING" strings (claim 1, proof 10, note 3 occurrences), so it is not fileable.
Premise support (not re-run, taken from the briefs): P14 H_root, P >= 0.434 at K=2 (CLAIMED from RESULT.md, good fraction 0.37-0.41 across rungs); minilab good-centre fraction ~0.3935 (matches 1-e^-1/2).

## Still missing before filing
1. Single-thread source with the template's six deltas (coin-draw centres, K trials, capped isolation DMAX, failed-run exit, no thread code, constant report charge). This is the other agent's algebraic_paper\src. The draft used src\single.c only as a stand-in.
2. Ledger additions: coin-word charge, isolation charge, HGCD_BOUND, and the r7 numbers above must be recomputed after the source delta (the ledger has no coin/isolation terms, so 58.07 is a lower bound on cost). GUESS: small change.
3. Values: COIN_WORDS/COIN_WORD_COST/COIN_RULE, CHARGING_RULES, LEDGER_SECTION/RECOMPUTATION, MEMORY_SECTION, BUILD/RUN_COMMAND, SOURCE_FILES/INTRO, FD0 (reference tool at r7), CREDIT_LINES, MODEL/HARNESS names, EXECUTOR sentence, R6_* rows (r6 run still going).
4. "No experiments": the template ships 2 experiments (and the experiment_manifest in claim.json). Drop them and edit the manifest/proof text; assemble.py always copies them. Alternatively keep (organizer runner bug for Poseidon experiments noted in the template README).
5. Arena/fragmentation at 160 GB is an empirical rule, not simulated; an r7 run needs about 136 GB per trial (box has 128 GB cloud, so the paper entry is unexecuted: the judge decides whether a paper entry without an r7 run passes, i.e. the e51feba1 ruling per the walk).
6. Prefile/intake and the owner's go for the filing.
