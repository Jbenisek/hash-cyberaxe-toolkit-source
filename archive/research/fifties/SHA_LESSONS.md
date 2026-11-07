# SHA lessons for blake3-r2 (2026-10-09)
Scope: the 3 lowest review/accepted entries per SHA track (board files research\rivals\boards_<track>.json), first 80 note lines each. Rulings were fetched into research\dossiers\<id8>\ for 1c368173, c99df2dc, 08c9e7c1 and def724e5. For r31/r32 the script found no run (the run is older than the last 100 Actions runs).

## Standing
- sha256-r31: 1347c47e ACCEPTED 31.61 (winglock+5: replays a pair that a pre-registered chain built on the published characteristic; the chain is charged as preprocessing). 61f8775b 33.676 and d2382c73 33.914 are in review (jungjipdo: z3 runs priced from callgrind).
- sha256-r32: 58c83d12 ACCEPTED 39.964; adbc6f0a 39.976; 3873e7f5 39.995 (its successor calls it passed, plausible_not_refuted). All jungjipdo: relaxed conditions plus a 7-lane SWAR online phase.
- sha256-r37: 087a18c4 63.45545 (GordoAR, de-pad of 1c368173); 1c368173 63.47455 (itseasypop, A0 variants; ruling plausible_not_refuted); b947b377 64.0687 (qkniep, 2^18 variants per first block). All in review.
- sha256-r38: c99df2dc 78.12 (qkniep, variants plus a row-16 table; plausible_not_refuted); deb673ae 99.91651 (winglock, bit-sliced); 20dbd783 100.06593 (GordoAR de-pad). All in review.
- sha3-r5: 83697db1 32.94842 (GordoAR port); 08c9e7c1 32.97491 (Th0rgal; plausible_not_refuted); 017f48c9 32.98298 (Jbenisek is a listed co-author). All in review. Method: MITM with Gray-code enumeration and counted SWAR kernels.
- sha3-r6: 335b32f0 124.0457 (GordoAR, K=13 rung); def724e5 124.05198 (Th0rgal; plausible_not_refuted); c9416d9d 124.05199. All in review. Method: generic birthday at below one unit per hash.

## A. Judge patterns
- Every ruling read is plausible_not_refuted with 8-12 "material" findings that did not block: participant-run evidence that the organizer did not execute, extrapolation beyond the tested regime, organizer reports marked no_attack_cost_inference, and unmeasured allowances. A package became not_evaluable only when a lane rated some premise "unsupported" (all 4 rulings; histories in the 1c368173 and c99df2dc notes).
- Unsupported, then fixed:
  - An inherited allowance with no evidence (76407c7c, 8bc7d6c5). Fixes: bound it against an accepted measurement or by a scale envelope. 1c368173 used r32 6eeefb64's rerun of a predecessor search: 593,858 solver CPU-s, at 1 CPU-s = 2^32.796 ops. c99df2dc argued from ten-year CPU/GPU envelopes. An allowance at 98.5% of T was still rated plausible (c99df2dc).
  - A numeric bound resting only on participant runs (3b532546, H5 = 0.0079). Fix: a weak premise, delta = 1, about 500x above the measured 0.0018 (c99df2dc).
  - A declared premise with no direct support (r32 v10c's selected-tuple transfer). Fix: derive it from measured moments (Bhatia-Davis plus Cauchy-Schwarz) and charge the loss (3873e7f5).
- Rare-event premise: a lower bound on an averaged probability ("mean over variants of q3 >= 2^-102").
  - Estimate it with a preregistered multi-stage SMC on independent streams. Take the one-sided 99% Student bound and set the model value at or below it. c99df2dc went 1 bit below, so the organizer's reduced replica confirms it with margin (1c368173, c99df2dc).
  - Rebuild every success as a full collision with reference code: 975,395 S successes replayed, 7.8M variant pairs rebuilt (b947b377).
- Dependence premise: "given one success, the expected number of other successes in the same block or group is <= delta". The success bound follows by Bonferroni/Chen-Stein plus Hoeffding over independent groups. Evidence: replay successes over their neighbours (0 co-successes in 32,911) and measure the pairwise correlation factor (1.001) (1c368173, c99df2dc, deb673ae).
- Rate premise: "the CV from a uniform first block behaves as uniform for these events", checked on 2^21-2^23 real first blocks against model rates (1c368173). Gains are charged at one-sided 99% lower bounds, 1.1810 against a point value of 1.1839 (58c83d12).
- Success and caps: use the exact floor mu0 = -ln(0.61 - allowances)/(1 - dep) instead of E[X] = 0.5, declared as a heuristic (087a18c4, 20dbd783). Set work caps by Bernstein or Chebyshev with an explicit failure term (b947b377).
- Selection and preprocessing:
  - r31 v7 (6d554419) was refuted for "model constants left free, development selection uncharged, programs not shipped". The accepted 1347c47e fixed all three:
    - it hashed every program and input before the first process;
    - it made one solver call with the default seed, "not picked from alternatives";
    - it fixed the trial cap N = 2/q before the online phase;
    - it charged every process and shipped all sources.
  - r5 premise H2-development-ledger, rated plausible: "the listed terms contain every target-specific run whose result fixed, or could have changed, a number read by the algorithm; old runs repriced at the counted routines" (08c9e7c1). The trail-search output is read as nonuniform advice, so it is charged once (017f48c9).
  - These packages charge executed work, not caps: callgrind counts per instruction form plus a kernel line (61f8775b, d2382c73); development measured below 4.1e5 CPU-s and bounded by DEV = 2^64 (c99df2dc).
  - Not done by us: our SEL is charged at its caps, 2^79.71. Whether charging its executed runs (every alternative tried) would be accepted is UNTESTED.
  - A parameter rung picked with outcomes known is declared as a heuristic, with Bonferroni over the decisions (83697db1).
- Experiments they ship:
  - the counted program run step by step on organizer seeds, every decision checked and op counts asserted exactly (b947b377, adbc6f0a). r5 v23 failed review over 50 declared vs 49 executed (08c9e7c1).
  - a scaled analogue of the full event on the real target: 18-bit masked collisions among 2^9 messages, accepted as witness evidence (def724e5). Not done by us; this answers our "no organizer experiment can show the counter half-collision" with a masked CV analogue.
  - a reduced organizer replica of the SMC (c99df2dc); 48 complete label-seeded runs (39 hits) with a CP bound (08c9e7c1).
- Memory is claimed in the counted 256-bit-word layout, not native RSS; d2382c73 was refuted on this once. The ledger uses exact rationals, with the 5-decimal claim proved tight both ways (T^100000 against 2^p) (087a18c4, 20dbd783).

## B. Methods that may transfer to 2-round BLAKE3
- Free-word variants: words in the dense part that carry no conditions. Each valid variant is another copy of the attack on the same CV (12.1M for r37). Classes that share one filter constant let one test serve 3,600 variants (1c368173, b947b377).
- A table indexed by the CV-dependent word, whose bucket lists exactly the variants passing the next condition. One load replaces a search of 2^29.5; the build is charged and memory is free (c99df2dc; table pricing "established").
- Relaxed conditions: drop the characteristic's sufficient-but-not-necessary conditions for the weakest ones that still give the collision. Charge the measured gain at its lower bound and rebuild every pass (3873e7f5, 58c83d12).
- Carry-length table: x + D = x xor Delta, where Delta takes only a few values, so L(x + D) = L(x) xor T[carry length] for any XOR-linear L. In ARX this covers rotations after an add of a fixed difference (adbc6f0a).
- Starting points: exact per-word condition sets over 2^32, one STP+CryptoMiniSat call, then a local-search move set that gave 483 starts and 5.7M tuples (1347c47e).
- Solved family: per group, solve some words so group-constant terms vanish. Hoist lane-independent gates into the group setup and fold a 5-bit batch value into 32 straight-line programs (deb673ae). For BLAKE3: fix early-G words, vary late ones.
- Packing: 7 x 36-bit SWAR lanes per word (1347c47e). 256-lane bit-slicing with 5-gate full adders, column adders, allocation onto 64 registers and every load and store counted (deb673ae; rated established in 1c368173).
- Birthday below one unit per hash: Gray-code message order and compiled straight-line bodies, about 26,850 ops per 256 messages with C = 1626. A last-writer-first table and an out-of-line candidate path priced per unit (335b32f0, def724e5).
- MITM with half-vector keys packed in 256-bit words and a SWAR popcount match (49 ops per match) (08c9e7c1, 017f48c9).
- Cost conventions: a compression is 1 unit and any other word op is 1/C (C = 1355 to 2728 by track). Preprocessing counts in time, memory is reported only, advice is 2^8-2^13 bytes. r31's replay framing (preprocessing = the whole build, success 1) fits only a practical-size attack.
