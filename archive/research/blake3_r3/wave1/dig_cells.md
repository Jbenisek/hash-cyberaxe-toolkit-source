# BLAKE3-r3 wave 1: dig cells walk (2026-10-13)

Labels: SEEN = read in a named file; COMPUTED = run here (1 process, nice 19, no GPU, each run < 5 min, own code only); INFERRED = my reasoning, untested.
Files read: research/dig/LEVER_CELLS.md (13 blake3-r3 rows, lines 211-223), luna2 L2_102 (3 files), L2_103/104/105/106/110/113, bigpicture/paths_blake3_r3.md and b3r3_defense.md, ATLAS_BLAKE3.md (r2 atlas, used for method only), sol_answer D207/D215/D220/D231, candidate_blake3/experiments/rho.py (own tracer, run read-only).
Scratch tools (outside the workspace, in the session scratchpad): rotsearch.cpp, rotsearch2.cpp, dirtyin.py, addorder.py, maskaudit.py.

## 1. State of the cells
- SEEN: Luna 2 blake3_r3_dig holds 253 records, ALL status SAMPLED, 0 OPEN, every gain_bits null or "0 (no lever)" (L2.103/104; my own count of the json files agrees). L2.102 resume, L2.105 (5 probes reproduce byte-equal), L2.106 (G-quarter inverse 10,000/10,000 each), L2.113 (memory 966,272 B < 2^20) are controls, not levers. L2_10_plus / L2_11_plus are SHA r37 files, not BLAKE3.
- SEEN: the 253 cells are 34 ALT (counter, flags, chunk, rotations, diff, multi, near, neutral, algdeg), 3 MODE, 64 msgword (16 words x Q1-4), and R1/R2 step cells (G calls, q1-q4). The "ceiling" in L2.110 is only a free-domain width (2^64 counter, 2^32 operand): a search-space size, not a score. Almost all cells are one-flip sensitivity controls; none prices a technique.
- SEEN: LEVER_CELLS has 13 blake3-r3 rows, all COMPUTED/SAMPLED, none built. COMPUTED: one operation = log2(595/594) = 0.002423 bit (5 ops = 0.01208, matches D231).
- So no cell is OPEN in the status column. The open work is gaps: premise, build, ruling, or an area with no cell.

## 2. Ranked list (potential = best estimate of the score move if it works)
Baseline: filed 125.1087 (unrounded 125.10856, PH = 595).

| # | Item (source) | Best estimate | Status | What it needs |
|---|---|---|---|---|
| 1 | Last-block mode + tuned chaining value, 3 zero sites, PH 595 to 590 (rows INIT.v0 0.01202, MODE.last 0.00241, free first block 0.0024; D231 path 4) | 125.09648 (-0.0121) | COMPUTED, conditional | prefix search ~2^96 not run; judge ruling that a two-block message (prefix + 0^32 x) is a legal collision input; register high-water mark. INFERRED: 3 sites is the budget cap (one site = 2^32 search; a 4th site would cost ~2^128, more than the whole ledger) |
| 2 | D220 full stack (1 + grouped filter + 25 B entries + fractional DP + margin removed) | 125.08441 (-0.0242) | COMPUTED, conditional | all of 1; 25 B layout built; grouped replay code built; lemma 2 restated for density 2^-113.34; owner OK to drop the margin |
| 3 | Safe sub-stack without CV and without margin removal: grouped filter 125.10407 (-0.0045), 25 B entries 125.10467 (-0.0039), fractional DP 125.10658 (-0.0020); combined ~125.100 | -0.002 to -0.009 | COMPUTED, not built | built code for each; restated lemma; the 25 B and fractional-DP rows both use the 2^20 boundary so they are not additive |
| 4 | Operation-level work inside the 595-op body (no cell in any file: a gap) | each op saved = -0.00242; 1 op off all 80 rotations = about -0.19 | COMPUTED, partial (section 3) | a cheaper packed rotation or a representation change; none found yet |
| 5 | Margin removal alone, lambda 0.4945 (GENERIC.SUCC) | 125.10494 (-0.0036) | COMPUTED, premise-sensitive | owner decision only |
| 6 | MACHINE.CMPBR grouped filter alone | 125.10407 (-0.0045) | COMPUTED | see 3 |
| 7 | R2D2.q3 / R2D3.q3 internal mask (1 op each) | -0.00241 each | SAMPLED | op-level replay in the tracer; the row says 9 ops with, 8 without; check it is not already inside 595 |
| 8 | DPTAB sweep, DPFRAC, CHAINLEN, RECOV, SETUP residues | -0.0049 to -0.0004 each, overlapping | COMPUTED | same bucket as 3; CHAINLEN and RECOV eat the same 1.65e-3 probability margin as 5 |
| 9 | Register-fallback text (b3r3_defense R1) | no score change | text only | tracer live-word count; defence, not a technique |
| 10 | Differential / connector lines at r3 | none | NULL (SEEN, dig 10-12) | nothing; the only structure found (6 of 8 digest words silenced at <= 3 message words) gives no collision |
| 11 | ALT.* free-domain cells (counter, flags, rotation constants, 2-bit masks) | none credited | SAMPLED | target fixes them (counter 0, flags 11, rotations 16/12/8/7); ALT.DIFF Q4 "broader difference-family search" is the only text-open item and is NULL by 10-12 |
| 12 | r4 feasibility (D207, 125.1752) | n/a | not an admitted track | only if r4 opens |

Ranking by potential: 2 > 1 > 4 > 3 > 5 > 7 > 8 > the rest. Item 4 ranks high only for the size of the prize; the evidence so far says the 5-op rotation is tight.

## 3. What I computed here
All on the packed 36-bit, 7-lane model of research/blake3_r3/candidate_blake3/experiments/rho.py.

C1 (COMPUTED, rho.py --selftest). PH = 595 = add 100, xor 88, shr 80, shl 80, or 80, and 167. So 80 rotations x 5 ops = 400 of 595 ops (67%). 160 of the 167 ands are rotation masks; 7 are guard-bit masks (3 inside adds late in round 3, 4 on digest words 0-3, which are unrotated sums).

C2 (COMPUTED, rotsearch.cpp). Exhaustive search over straight-line programs of shl/shr (7 shift amounts), and (28 window masks), or/xor/add of two earlier values; checked on the middle of 3 lanes with 8 random inputs. For r = 16, 12, 8, 7, clean inputs and dirty inputs (random 36-bit lanes): NO program of length <= 4 rotates correctly (92,248,926 programs for r=12; 13,246,050 for r=16). Length-5 programs exist (r=12 dirty: 126 found among 22.1 billion; the tracer's shr/and/shl/and/or is among them and its sanity run matches 8/8). So 5 ops is minimal in this operation family with these immediates. Limits: restricted immediates, 3-lane model, 8 random tests, not a proof.

C3 (COMPUTED, partial; rotsearch2.cpp). Fused forms rotate(a xor b) and rotate(a)+b with two inputs, r = 16, 12, 8, 7, dirty: no program of <= 4 ops. The decisive bound is <= 5 ops (current cost 6); that run (r=12, xor-fused) hit my 285 s cap unfinished, so the 5-op case is OPEN.

C4 (COMPUTED, dirtyin.py). Leave digest words 0-3 unmasked and let the next batch accept guard-dirty x. The self-consistent input bound is 36 bits and PH rises to 603 (+8); partial variants ({0}, {0,1}, {0,1,2}, {2,3}, {1,2,3}) give 597-601. Worse than 595. 0 mismatches against the scalar digest (200 random batches x 7 lanes x 8 words).

C5 (COMPUTED, addorder.py). Coordinate descent over the operand order of all 48 three-operand adds (6 orders each, 3 passes): PH stays 595; digest still matches (0 mismatches).

C6 (INFERRED, not run). 8 lanes x 32 bits needs a carry-safe add (about 6 ops per two-operand add instead of 1) plus the same 5-op rotations: about 1100 ops per 8 lanes = 137 per lane against 85 now. Pitches 33-36 all give 7 lanes. A split-half representation makes rot16 free (at most 20 rotations, -100 ops) but every add then needs a carry between halves and the 12/8/7 rotations get worse: INFERRED net loss.

## 4. Cheapest exact test for each of the top 5 (ranked list order: 2, 1, 4, 3, 5)
1. Last-block CV (item 1). Under a minute, no search: with the organizer blake3 (kit organizer_blake3.py, rounds = 3) hash a 128-byte message P || 0^32 || x as one chunk with two blocks and check the last compression equals our rho.py model with h = cv(P), flags CHUNK_END|ROOT, counter 0, block length 64. Then run the tracer with a synthetic h that zeros 3 sites and confirm PH = 590 and 0 mismatches. This closes the mechanics; the 2^96 search and the legality of a two-block collision input cannot be shown here and must be stated in a filing.
2. D220 stack (item 2). Rerun rho.py --ledger with the D220 parameters (per_body 9477, tmax 26885, d 113.33689254483488, lambda 3932553/7952696) and compare N with D220's printed value; then run the n = 22 organizer protocol (rho.py main with patched constants) for 20 seeds and confirm collisions still come out. Minutes. Two premises (H1 margin, built grouped filter) stay open.
3. Safe sub-stack (item 3). Ledger rerun for the exact combination (grouped filter + 25 B + fractional DP, lambda unchanged), because D220 has no row for it. Memory must stay <= 2^20: 25 x 26885 + 374,400 + 2048 = 1,048,573 B leaves only 3 B, so check the code size of the unrolled body at the new per_body. Seconds.
4. Op level (item 4). Finish the C3 fused search at length 5 (split by first op into 4-minute chunks or write meet-in-the-middle), then widen the immediate set (masks of up to 3 runs) for plain rotate at length 4. A hit means -1 op x 80 = about -0.19 bit with a clean tracer swap; a miss closes the family.
5. Item 5 / 7. For item 7: dump the ops of G call 3 round 2 and G call 3 round 3 in the tracer and see whether the "9 vs 8 ops" is already inside 595; if not, -1 op each (-0.0048 for both). For item 5 (margin removal): no test exists; it is an owner decision, exact arithmetic already in D231.

## 5. Techniques to record that no cell holds
- Rotation / representation search (item 4): 67% of the cost, no row. Closed so far: 4-op plain rotate (C2). Open: fused 5-op (C3), wider immediates.
- CV zero-site cap of about 3 sites from the search budget (item 1, INFERRED).
- KILLED by own test: output-mask elision (C4), add-order reshuffle (C5), 8-lane pitch-32 (C6, INFERRED only).

## 6. What this does not claim
No score change is proven. Everything in the table other than the 595-op baseline is conditional on a build, a ruling, or an owner decision. C2 is a bounded search, not a proof of 5-op optimality on every machine model.

## 7. New symmetry probe (2026-10-19)

`research/luna/item3237_blake3_invariant_schedule_autocorrelation.md` records
a bounded full-state test of the schedule-invariant message/difference
subspace.  Over 240 structured and 32,768 random pairs, eight-round traces
had zero exact repeated differences or pair states.  The largest lag
similarity was 311/512 equal bits (lag 2/3), consistent with an extreme-value
sample rather than a period.  This is COMPUTED/DIAGNOSTIC only: carry
dependence on the base state remains, so the subspace is not an autonomous
difference map and no all-round lever is established.
