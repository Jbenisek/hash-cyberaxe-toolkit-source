# Critic: blake3-r3 and poseidon-r1/r2 (2026-10-12). Read-only audit, no heavy runs.

## (a) Scanned but not backed by a CELLS test
- blake3-r3: all 721 dig-scan-b3r3 records have own_test=true, evidence paths exist, held_fixed and reopen_if are filled. Clean on form.
- But 65 of 533 "scanned" universe cells are basis FILE (INIT 16, OUT 9, MACHINE 6, LEDGER 5, PIN 4, MEM 3, GENERIC 2...): taken from the submission note, not re-run. Label LOCAL_ONLY/CLAIMED until an own run.
- poseidon-r1 (241) and r2 (229): ALL scanned cells are basis FILE; CELLS.jsonl holds 0 poseidon records. Sources are atlas/LEVELS "OBSERVED" (81+81 cells from one degree tracker, 28/31 sample points), the filed r1 note, D189, Luna 3 answers. Nothing here is a dig record: the poseidon "scanned" count (470) is ASSUMED. SCHEMA hash enum was to be extended; ingest records first.
- C1247 is BEDROCK on 350 random/adversarial batches = SAMPLED at best; its own text says op 507 passes all 350, only a hill-climb/SMT witness shows it matters. Relabel SAMPLED (SMT part COMPUTED).
- 76 SAMPLED records: crude text check finds ~58 whose number states no interval; add intervals.
- C1517 (door 24), C1520 (door 45) are LOCAL_ONLY: 3 outer steps x 2^22 words; N=2^24 with k<=48 bits. Not the full path.

## (b) KILLED
- Only one: C1580 GENERIC.ATT (more attempts/restarts). Number: a=2 +0.4986 bit ... a=8 +1.4993 (ideal 0.5 log2 a), success 0.39. It is a cost model of the filed circuit, not a search; it closes "amplification at fixed success 0.39" only. Reword as COMPUTED, or KILLED with held_fixed = this circuit, success 0.39. Does not close other attempt structures.
- OPEN not KILLED (correct): C1488 first block, C1507 parent, C1514 tree (only generic step cost measured).

## (c) Missing dimensions
- blake3-r3: no differential/characteristic cells at all (ALT.DIFF Q2/Q4 unscanned); ALT 34/36 unscanned (ROTAT, ALGDEG...); message-word-pair/word-tap WORD 48/64; no per-bit (not just per-word) axis; no counter/flag variants beyond 11/3; no multi-chunk (counter t>0) axis; no memory-vs-time trade axis beyond one bound.
- poseidon: no CELLS records; ROUND cells lack the Q2 "can layer be skipped" tests (affine/line solutions) done by code; LEDGER r2 0/36, JUDGE r2 0/12, MACHINE r2 0/24 (not even file evidence); IN dimension (m0,m1,2^65, canonical < p) has no family; lane-0-only partial S-box (P1/P2) polynomial-root axis (POLY 20-23 open) thin; PR 923 variant target unmapped.

## (d) Five unscanned cells most likely to move a score
1. poseidon-r1|LINE (12 open): line/subspace through the full rounds; board 30.71 vs our est ~27.
2. poseidon-r1/r2|POLY + ROOT (33-38 open): degree 5^k root finding, D189 only 8/20 centres.
3. poseidon-r2|LEDGER 0/36: exact op counts unmeasured; "exact counts" rule would tighten slack.
4. blake3-r3|R2C/R2D step cells (128 open) : round 2 is where the full diffusion lies; no measurement.
5. blake3-r3|ALT.DIFF Q2/Q4 + MODE parent/tree: only structural line that escapes the 595-op generic circuit.
Next: write poseidon own-test records first (new ground), then R2 steps.
