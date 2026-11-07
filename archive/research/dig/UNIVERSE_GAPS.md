# UNIVERSE_GAPS - what "everything scanned" would still miss

Critic pass, 2026-10-12, over `coverage.py`, `UNIVERSE.jsonl` (2,100 cells, read in full by reason/kind), `COVERAGE.md`, `SCHEMA.md`, plus
the target profiles, the paper facts, the r37 package proof (pkgR37M3), CLOSED_DOORS, LENSES, HANDOFF 10-12 and the Poseidon material.
Nothing was scanned or run. No CELLS.jsonl write. Labels: FACT (read in a named file), COUNT (I counted UNIVERSE/CELLS/chi files),
GUESS (my estimate of hidden size; not a measurement). "Scan cost": M = mapping of existing records only (no new compute),
A = one agent, <= 1 h, B = GPU or multi-hour job, C = research with an open outcome.

## 0. The one-paragraph answer

The universe is a grid over ONE object per hash: the published sha256 characteristic (chi37/chi38 rows), the Keccak round/step map of the
current leader lines, the 64 BLAKE3 quarter-steps of the current record. Everything outside that object is invisible to it: the
**live Poseidon target** (0 cells, 0 CELLS records), the **memory axis** the score is moving to, the **choice of characteristic** itself
(support, bit position, signs, step count), the **CV / first-block layer** (64+ cells wrongly marked "structurally empty"), the
**BLAKE3 initial state, output fold and mode/tree choices** (all 16 init words, flags, counter, length pair), the **SHA3 message format,
digest lanes and sub-round granularity**, the **statistical premises and op ledgers** that produced every judge failure, and whole
**neighbouring tracks** (blake3-r1, Keccak[800], other round counts). Section 1 ranks them; section 2 lists cells the universe calls
trivial that are not; sections 3-10 give the cells; section 11 lists what I checked and found NOT to be a gap.

## 1. Ranked gaps (by how much unknown they hide)

| rank | id | missing dimension | cells to add | hides (GUESS unless noted) | scan cost | first test |
|---|---|---|---|---|---|---|
| 1 | G01 | Poseidon Orchard, the live target (and the PR 923 variant) | ~60 (compact) to ~260 (round x step) | whole target: board r1 30.71 / r2 34.89 vs our unverified est. ~27 / ~31.7 (HANDOFF 10-12 12:00) = up to ~4 bits per track | C | own arithmetic count of the skip-two-rounds line on the live profile |
| 2 | G02 | Memory axis S = T + max(0, log2 bytes - 20) on every target | ~90 stage objects (5 hashes) | tens of bits on the line that switches regime: FACT r37 table 93.28 vs table-free R37M3 60.99; r38 131.49 -> 87.90; r6 128.03 -> 124.6 (HANDOFF) | A per hash | per stage: bytes held, time to recompute instead, S-optimal point |
| 3 | G03 | The characteristic family (support, bit position, signs, step count, neutral bits) | ~700 (see 3.x) | FACT: dense part not derived (4 solvers x 2 h UNKNOWN); bit-31 variant +0.913 late-event, tail rank 73 vs 74, "up to ~1.9 bits if a dense part exists" | B/C | U (uncontrolled weight) and tail rank per bit position b = 0..31 |
| 4 | G04 | CV / first block / block count / padding layer of the ordinary collision | ~110 (72 re-opened + 40 new) | H1 (CV uniformity) rests on <= 2^23 real first blocks (FACT, proof H1 limitations); A0-variant family, gate, third block | M + B | GPU test of F37 output words to 2^36+ first blocks |
| 5 | G05 | BLAKE3 initial state v0..v15, output fold, mode/tree/length-pair choices | ~120 | doors 21, 22, 24, 37, 38, 45 are CLAIMED-UNTESTED (CLOSED_DOORS RELABEL 10-12) and have no cell; 160 "I" cells hide design choices | A + B | init-word table with the pinned values and their alternatives |
| 6 | G06 | SHA3 message format, digest lanes, sub-round (row/slice) cells, stage ledger | ~150 | r6 chi: 19 cells unscanned only because the unit is a round; r5 127 + 24 + 520 counts have no per-row cell | A | row-level necessity of the r5 M4 conditions (127) and the r6 prefix conditions (128) |
| 7 | G07 | Statistical premises and op ledgers (H1, H2/q3, H3, success floor, caps, per-category ops) | ~80 | every NOT_EVALUABLE ruling so far; Th0rgal's four morning shaves were all ledger cells (0.001-0.17 bit each) | A/B | premise cells with fresh seeds + control |
| 8 | G08 | Differential clustering at "=" bits, triple interactions, lever composition and r37<->r38 transfer | ~150 | FACT: rows 18/19 +1.93, rows 22+ x2.465 came from exactly this lens; the grid only asks "same modular difference" and pairs | B | drop-one on "=" bits of rows 17..24 (~1,500 printed "=" bits) with full-path check |
| 9 | G09 | Neighbouring tracks and round counts: blake3-r1 (live), Keccak[800] r5/r6 (packages built, unregistered), SHA-256 r33-36/r39-40, SHA3 r3/r4/r7+, BLAKE3 r3-r7, md5/sha1 controls | per track ~100-250 | new paths (many-paths goal); K8 and r1 have packages/filings and no cell | C | register the hash names; reuse the same universe builders |

## 2. Cells the current universe calls "structural" or "scanned" but that are not trivial

These inflate "scanned" (928 structural cells in the 1,595 scanned). Re-open before declaring the dig complete.

| # | where (UNIVERSE reason) | count | why it is not trivial | what to do |
|---|---|---|---|---|
| S1 | sha256-37/38 `r-4..r-1` A/E Q1-Q4 "CV coordinate: no step, no word, no condition (BEDROCK by structure)" | 32 + 32 | true for the SFS pair; false for the ordinary collision. The CV is `F37(IV, M0)` of a random first block and the attack gates on it: x = A_{-1} must lie in F7 (|F7| = 68,157,440 = 2^26.02 of 2^32), cb = C6 - A_{-2} in the F6 test, then 222 classes / 782,800 variants (FACT pkgR37M3 proof Lemmas 5.1, 8.x; S37-DB-P0FACTS recounts them) | replace by G04 cells; map C0016, C0018, C0019, C0022, S37-DB-P0FACTS as the first records |
| S2 | same hashes, Q5 `CV rows -4..-1` pair cells "no difference" (ATLAS cell D) | 16 + 16 | the (-k, 0..3) cells are labelled D (direct state read) in the atlas, i.e. the CV does feed row 0..3; "no difference" is the SFS fact only | keep the label, drop "structural" |
| S3 | rows 0..3 "free base word / no condition" | 12+12 (37), 12+12 (38) | W0..W5 are NOT free in the attack: they are the bijective image of a0 (Lemma 4.1, 5.1) and are solved from the row 4/5 conditions; the a0 family is the largest lever family found (G, "all 128" families) | map the family records to row-0 A/W cells |
| S4 | blake3 "I" quarter-steps (K0-K3, D0-D3, C0, C2): Q2, Q3, Q4 "no characteristic layer, no alternative" | 160 | inside the "I" steps sit choices: the length pair 55/63 (XOR 8, K2.q1, Lemma L), the pins X3, X7, X11, X15 (D0-D3), w4 = 97475638 and w13 = 0007c006, the K = IV[2]+IV[6] cancellation. Door 33 searched only the C3 (Y3,Y11) cells inside H8's profile | one `INIT/PIN` object per pin (section 6) |
| S5 | blake3 E0/E2 "zero difference by identical inputs" Q1, Q3 | 18 | stricter than the event (ATLAS_BLAKE3 says so); Q2/Q4 are LOCAL_ONLY records and doors 22/24 are CLAIMED-UNTESTED | keep Q1/Q3 structural, do not count Q2/Q4 as done |
| S6 | sha256 Q2 "no printed condition ... (trivially empty)" | 75 + 79 | only 0/1/n/u count as "conditions" (cond_bits). "=" (difference forced to zero) and "+" are not examined; about 1,500 "=" bits in the 20 printed rows alone (COUNT: chi37 A 615, E 304, W 605; chi38 A 613, E 330, W 612) | G08 cells |
| S7 | Q5 sha256-37 `ATLAS37.md` basis FILE | 95 | scanned because the atlas matrix cell is decided (code not "?"), not because a joint-drop test of that pair exists; the Q5 text asks for singles vs pair. Only PAIR-B0..B4 and the 30-group sweep are such tests | label these "matrix-decided", not "joint-drop tested"; spot-test 10 pairs |
| S8 | LOCAL_ONLY records counted as scanned (rows 14 Q2 C0096-C0098, blake3 C0036/C0037/E2 rows) | COUNT 3 + 1 + ~10 | window or row-local only; REFERENCE_CARD: "count a gain only after a full-path check" | status column "scanned (local)" |
| S9 | 318 cells scanned by a FILE of a running job, not yet ingested | 318 | not reviewed by the ingest step; 117 sha256-38 Q1 cells rest on one check.txt | ingest first |
| S10 | 371 EXCLUDED cells (jobs rows38-full-dig, close-open-rows-37, dense-dig, Luna 2, D180, D181) | 371 | "everything scanned" is false until these land | track as a separate gate |

## 3. G03 - the characteristic family (hash sha256-37, sha256-38; new objects `CHAR`)

The grid is the published characteristic. Anything it proves is conditional on it. Cells to add (id pattern `sha256-NN|CHAR.<kind>.<arg>|CHAR|Qx`):

| group | cells | question | existing material | scan cost |
|---|---|---|---|---|
| 3.1 support | message-difference support S0 = {W6,W7,W8,W9,W10,W14,W15,W22,W24} (r37). Add: support shifted by +-1..3 words, supports with dW14 = dW15 = 0 (compatible with the padded last block), supports without W22/W24, supports of the r38 table | does a characteristic with this support exist, with what U (uncontrolled weight, paper: 75 printed / 74 rank) and tail rank? answer SAT / UNSAT / UNKNOWN, never "no" | Luna 2 task L2.5 (new ground, running, not in the universe); Grok 116/118, long solve 4 x 2 h UNKNOWN | C |
| 3.2 bit position | bit position b = 0..31 of the dense part (published b = 29): 32 cells x (U, tail rank, late-event gain, dense part exists) | alt-char agent 10-12: bit 31 gives late event +0.913 and tail rank 73; "published one provably cannot carry over"; bit-29 control also UNKNOWN | job117/119 | C |
| 3.3 signs | independent negation of each modular difference in S0 (2^9 patterns; global member swap = BEDROCK, so only the relative signs are new); Q4 keeps the modular difference and never asks this | consistency by traillab sdiff/backward, then window to the event | traillab modes sdiff/backward | A |
| 3.4 step counts | chi36 (paper: first practical 36-step, 2^57, negligible memory), chi39 (SFS only, no collision route per sha256grid/GRID.md F06), chi35 (LLWS26 2^48.3) | Pareto "rounds" axis; no chi file for them exists in `traillab/chi` | paper 2026/1120; sha256grid/GRID.md | B |
| 3.5 neutral bits | the 512 free message bits x rows: which W0..W15 bit can be flipped keeping rows <= k (recompute the schedule from W0..W15; never vary W16+ with later words held) | the standard message-modification map; the grid has Q3 counts only, no bit identity | tighten/r37_unforced.md, r38_unforced.md ("all necessary"); retest/expansion_audit | A/B |
| 3.6 "+" free values | the 20 (r37) / 26 (r38) "+" cells: the free value is a selector | late-choice bits (5 in the card) are counted, not located | REFERENCE_CARD | A |

## 4. G04 - CV, first block, block count, padding (hash sha256-37/38; objects `CV`, `BLK`, `PAD`)

| cell | question | note |
|---|---|---|
| `sha256-NN|CV.gate|F7|Q1..Q4` | count, necessity, freedom, alternatives of the gate x in F7 (and cb in F6) | M: S37-DB-P0FACTS (COMPUTED, own), C0016 |
| `sha256-NN|CV.classes|c7|Q1..Q4` | 222 classes >= 3456 / 22,976 classes / 782,800 variants; larger families (a),(b),(c),"all 128" | M: C0016, C0018 (ledger arithmetic), C0019, C0022 (KILLED for the real generator, +0.434 for G' unbuilt) |
| `sha256-NN|CV.H1|uniform|Q1` | are the CV words of the 37/38-step compression of random 512-bit blocks uniform and (x, cb) independent? proof H1 evidence is 2^21 and 2^23 real first blocks only | B: GPU, 2^36 blocks is minutes; also a bias here is a LEVER, not only a risk |
| `sha256-NN|CV.diff|nonzero|Q4` | characteristics with a NONZERO chaining-value difference (first block leaves a near-collision, second block absorbs it). The universe fixes dCV = 0 at rows -4..-1 | C: unmapped; real SHA-2 attacks used this shape |
| `sha256-NN|BLK.count|n|Q1,Q4` | 2 data blocks + padding block (current). Alternatives: difference block in block 3 of a longer message, extra free block between | cost model: padding block equal CV in both members, one extra compress only on a hit |
| `sha256-NN|PAD.len|W14W15|Q2` | W14/W15 are data in block 2 only if the message tail is >= 56 bytes (then a third block holds padding); supports with dW14 = dW15 = 0 could end in block 2 | FACT profile: padding FIPS 180-4, length < 2^64 |
| `sha256-NN|OUT|rows33-36|Q1` | feed-forward adds the equal CV to both members, so the digests are equal iff A33..A36, E33..E36 are equal; no truncation is allowed (profile) | BEDROCK; add one cell so the end of the chain is in the universe |

## 5. G02 - memory objects (every hash; object `MEM`, questions M1 bytes held, M2 time to recompute instead, M3 S-optimal point, M4 breakpoint at 2^20)

The universe asks only about difference structure. The score is `time_log2 + max(0, memory_log2_bytes - 20)` (PR #858 open; Pareto live;
hashsmash-orchard-tm-v1). A lever that is a loss time-only can win under S, and the reverse (FACT: R37M3 S 60.99 at 607,744 B vs 93.28).

| hash | stage objects to add |
|---|---|
| sha256-37/38 | F7 set (68,157,440 entries; bitmap vs decision tree), F6 set (287,309,824), G (12,103,680), class lists (222 / 26 added classes), row-16 set (1,052,672 (u,l) pairs; 4096-word chunk tables), per-first-block pair lists (831 on average), cube sums, plane registers (64-register budget) |
| sha3-r5 | connector / FES key tables, Gray tables, 24-equation stage-1 split (R5-E1 OPEN) |
| sha3-r6 | 140-bit key, 35-plane table, DP-rho (R6-DPrho OPEN), K13 (R6-K13 OPEN), distinguished-point generic line S6R (mem 20) |
| blake3-r2 | typed omega lists (23,820,160 / 34,028,800 words), preprocessing 2^54, B3M stream/replica cells (B3-STREAM, B3-replica OPEN) |
| poseidon | root-finding state (NTT length, polynomial degree 5^k), ties to G01 |

## 6. G05 - BLAKE3 (hash blake3-r2; new objects `INIT`, `OUT`, `MODE`)

The universe has 64 quarter-steps and 16 message words. It has no state before round 0, no output fold, no mode.

| cell group | cells | question |
|---|---|---|
| INIT | `blake3-r2|INIT.h0..h7|Q1-4` (8 CV words), `INIT.iv0..iv3`, `INIT.t_lo`, `INIT.t_hi`, `INIT.b` (block_len, v14), `INIT.d` (flags, v15) | what each word is in the current record (h = IV, t = 0, b = 55 or 63, d = CHUNK_START or CHUNK_END or ROOT = 11), which alternatives exist (flags 11 vs 12 delta 7, door 21; counter classes, ctr_class transfer; non-IV h from a multi-block chunk, door 6 covers h = IV only, door 37 prices a fresh CV per context at 0.007-0.1 bit) |
| PIN | `X3, X7, X11, X15`, `w4 = 97475638`, `w13 = 0007c006`, `K = IV[2] + IV[6]`, length pair (55, 63) | necessity and alternatives of each pin. Door 33 covers only (Y3,Y11) inside H8's profile |
| OUT | digest word i = Z[i] ^ Z[i+8], i = 0..7: 8 cells x Q1-Q4 = 32 | the 4 pinned words (0,2,5,7: E0/E2) and 4 residual (1,3,4,6: E1/E3); FACT profile: digest = first 32 bytes of root output, so the second half v[i+8] ^ h[i] (where h enters) is NOT in the digest; legal 55/63 family has exactly 4 digest pins (door 24) |
| MODE | single-block root; first / middle / last block of a multi-block chunk (h free per block); chunk index t >= 1; parent compression (flags 4+8, b = 64, left||right CV) | door 3 (parent: >= 8 word conditions = 256 bits, dominated by a chunk-block host), door 23 (CV/tree differences, none below 63.6), door 38 (separability bias, smoke only), door 45 (224-bit near-collision first block ~2^64). Rows 21, 22, 24, 37, 38, 45 are CLAIMED-UNTESTED since the 10-12 relabel: they ARE the unscanned part |
| MSG | per-round read table: round 0 reads m in order, round 1 in the permuted order (m2 m6 m3 m10 m7 m0 m4 m13 m1 m11 m12 m5 m9 m14 m15 m8); 32 reads | one cell per (round, G, position) so a word's two uses are visible; the existing word cells merge them |

## 7. G06 - SHA3 (hash sha3-r5, sha3-r6; objects `MSG`, `DIG`, `ROW`, `STAGE`)

| cell group | cells | question |
|---|---|---|
| MSG | block count and length: all current work is ONE 135-byte block, byte 135 = 0x86, 1,080 free bits, 512 capacity bits = 0 (SHA3R6_MAP). Alternatives: shorter message (more fixed padding bytes, no gain expected), 2 blocks. "Obstruction 1 (PROVED): the first block breaks at r = 6" because the reduced permutation also runs on the first block, so a prepared capacity is impossible | M: SHA3R6_MAP section; add cells so the choice is in the universe. Capacity = 0 at the input of round 0 is a structural help for r5 and r6 |
| DIG | digest = lanes (x,y) = (0..3, 0) of the final state only, 256 of 1600 bits; 1,344 bits are don't-care. Cells per lane 0..3 and one don't-care cell: Q1 which final-chi inputs matter (cone), Q3 freedom | r5 "4 of 5 bits per plane-0 row", r6 "8 digest-determined bits (z = 0,1, lanes 0..3)" and the round-5 cone (2.19 ops/message) are these cells under another name |
| ROW | chi acts on 320 rows. r5: 24 FES equations, 127 linear round-1 conditions M4 (59 rows), 520 fixed F bits, 33 DF needed vs 45-60 typical. r6: 128 prefix conditions (rank 128, 4 per z-bit), 132 free bits, 140-bit key, 8 forms of degree 8. Add a cell per condition group with Q2 (drop one: does the rank/affine property fail) | the SHA-256 grid is bit-level, the SHA3 grid round-level: this asymmetry is why r6 chi shows 19 unscanned cells |
| STAGE | the r6 route ledger blocks (ops/message): prefix chi1 affine (z-flip, 22-word footprint), chi2 patch + theta3 7.30, chi3 block 53.30, round-4 cone 46.11, round-5 cone 2.19, round 6 on 35 planes 3.12, transpose 14.32, probes 6.00 (sum 132.44 vs stated 124.62: SHA3R6_MAP lines 34-35 flag the mismatch) | one cell per block, Q1 count, Q2 necessity, Q4 alternative |
| ALT | architectures with no cell: zero-digest cores (C0020 closes the kernel class at 145 and parity-2 w2 <= 16 at 150 only; open: HW3 >= 165, kernel >= 230 beyond one prefix, parity-2 w2 >= 20, unrestricted 4-round search, round-5 term); near-collision + digest bits (ePrint 2026/2107, 2^117.85 + 6 bits, door 20) | owned partly by D180; the unrestricted search is not in the universe at all |

## 8. G01 - Poseidon (new hashes `poseidon-r1`, `poseidon-r2`; SCHEMA `hash` enum must be extended)

FACT-check first: `research/tighten/poseidon_pr923.md` (10-12 morning) describes PR 923's exploratory target: round 0 only (r1) / rounds 0-1 (r2), both FULL,
price C = 27 per full round, claim 127 nominal. HANDOFF 10-12 12:00 (Stratum) says Poseidon is now live as its own Pareto challenge
(`research/poseidon/pareto_clone`, clone ac95110a) with a DIFFERENT target: Orchard P128Pow5T3, eight full rounds (0-3 and 60-63) plus
the first r partial rounds starting at index 4, r = 1, 2 admitted, `C(r) = 216 + 21 r`, omega = 2.8, score `time_log2 + max(0, mem_log2 - 20)`,
orchard-cost-v2 (field add/sub/mul and 256-bit word ops each weigh 1). The PR 923 brief's day-one routes (fifth-root line at ~390 ops / 27, score ~4.0;
r2 odd-part quadratic, ~6-7) were priced for the PR 923 target and do NOT transfer to the live one without recount. Build the universe on the live
profile; keep PR 923 as a labelled side hash only if someone files it.

Live-profile facts (FACT, `pareto/target-profiles/poseidon-orchard-r*-prefix-v1.json`): state [m0, m1, 2^65], x^5 on all three lanes in full rounds and lane 0 in partial rounds,
dense deployed MDS, no feed-forward, digest = state[0] as 32 LE bytes, both inputs canonical < p (aliases out of scope), p = 0x4000...224698fc094cf91b992d30ed00000001,
(p-1) mod 5 = 1 (x^5 bijective, inverse exponent d), 2-adicity of p-1 is 32.

| cell group | cells (per r in {1,2}; round list F0 F1 F2 F3 P4 [P5] F60 F61 F62 F63) | question |
|---|---|---|
| IN | `m0`, `m1`, `capacity 2^65`, `canonical < p` | Q1 free dimensions (2 inputs, 1 output lane: the collision set is a curve, generic cost 2^127 from p ~ 2^254), Q2 necessity of the canonical bound, Q3 freedom left, Q4 alternative parametrisations (line, conic) |
| ROUND | ARK, SBOX, MDS for each round: 3 x (9 or 10) x Q1-Q4 = 108 / 120 | Q1 degree contributed (5, 5^3 per full round, 5 per partial), Q2 can this S-box layer be skipped (its input vanishing at one point of a line, bijective x^5 lets the first layer be free), Q3 spare dimension, Q4 alternative lines/subspaces |
| OUT | lane 0 only: the two other lanes at the end are don't-care | Q1 which pre-MDS lanes enter state[0] (all three after F63: row 0 of the MDS), Q3 freedom |
| TECH | skip rounds 0 and 1 (U, V fifth powers); odd-part trick on a symmetric line; Cantor-Zassenhaus on the resulting quartic/degree-5^k polynomial (P(root) ~ 5/8); NTT-based root finding (2-adicity 32); resultants/Groebner; partial-round invariant subspace (CICO style); plain birthday 2^127 | each: finite operation count under orchard-cost-v2 and success >= 0.39, with memory term. Luna 3 (P3.1-P3.6): no third-round skip via rational curves (bounded proof), r1 squarings 2^32.2, r2 2.27e10, r3 floor ~35 |
| COST | `C(r)` = 216 + 21 r, omega = 2.8, finite-coefficient rule, log factors kept | where the tuple (rounds, T+M) is read: r >= 3 is not admitted |

Rank-1 because: no cell, no CELLS record (COUNT: 0 hits for "poseidon" in object/question/notes), a live board, and our numbers are workflow estimates (not own_test).

## 9. G07 - premises and ledgers (all five hashes; objects `PREM`, `LEDGER`)

| cell group | cells | question |
|---|---|---|
| PREM | H1 uniform CV; H2 q3 (r37 2^-71.47 four-pattern, 2^-70.. bounds; r38 2^-101.35, 2^-101.025 own replicate); H3 multiplicity <= 2^-9.4 (measured factor 0.98-1.00 at row 16, thin margin 2^-9.68 vs 2^-9.4); success floor mu0 = 0.49558494 from -ln(0.61 - Pcap - 2^-60)/(1 - 2^-10.4), Pcap 0.00056206; caps A_C = 2^60, A_S = 2^50, DEV = 2^40; SMC resampling correlation | each premise is "score-critical" in the proof text; each as a cell with fresh seeds + control; "measure what others copy" |
| LEDGER | per package category: FIXED 615 (first block and control 46, class test 397, scalars and planes 172), data-dependent 46,070.09 (scan, gather, group 16,269.77 ...), V_MAX, vmax_fb; r5 17-vs-14-vs-19 key words; blake3 U_WORD 45-48, U_MEMBER, SETUP | exact count vs charged; the Th0rgal shaves (checklist kinds 1-7) are ledger cells; CHECKLIST.md items 1-10 are the questions |
| JUDGE | NOT_EVALUABLE causes seen: H4a unmeasured (dense characteristic), stale ledger transcript, F-SURVIVOR-MEAN-MISSING, evidence margins (218 B, 12.06 s) | a cell per cause so a package is checked before filing |

## 10. G08 and G09

**G08 (analysis dimensions the grid lacks).**
1. `=`-bit relaxation (S6): for each of the ~1,500 printed "=" bits of rows 6..24 (A, E, W) ask whether the event survives with the difference allowed there (path multiplicity; the 75/32 carry effect; rows 18/19 four-pattern +1.93; rows 22+ exact event 2.465x the cells). Q4 covers only n/u signings with the same modular difference. Full-path check required. Cost B.
2. Triples: Q5 is pairwise at distance <= 4 plus four schedule taps. Long-range and three-way coupling (rows 16/17/18 through E-driven choices; 22/23/24 through W24 = s1(W22) + ...) has no cell. Start with the triples around the 18/19 parity and the 22-24 block.
3. Composition and transfer (keep-every-lever): `COMPOSE(lever_a, lever_b)` and `XFER(r37 -> r38)`, `XFER(r38 -> r37)`; LEVERS rows exist, the dig has no object for them.

**G09 (neighbouring tracks, same universe builders).**
- `blake3-r1`: live and competing; our filings R1F 31acfdbb (flags, 4.7545), R1C c8160a0a (counter, 6.2351), R1V 6b039da2 (chaining value, 3.1334), f0dab7bd promoted score 2; the three lines (flags, counter, CV) are the r2 `INIT` alternatives of G05.
- `keccak800-r5`, `keccak800-r6`: local lanes only, packages pkgK8 r6 122.45 / r5 121.71 (26-dim field, executed bit-slicing), baseline 149; Grok 102's 28.2 was WRONG (difference nonzero on 131 of 264 fixed bits; connector 585 equations / 536 unknowns inconsistent). 32-bit lanes: new round/step map and digest lanes (8 lanes). File the minute lanes are registered.
- Round-count axis (Pareto: rounds 1-64 sha256, 1-24 sha3, 1-7 blake3, 0-56 Orchard; accepted list starts empty, original dev SHA-256 31/32 closed): SHA-256 r33-r36, r39, r40 (G03.4), SHA3 r3, r4, r7 (first-block obstruction at r6 suggests r7 needs a different route), BLAKE3 r3-r7 profiles exist in `pareto_clone/pareto/target-profiles`.
- md5-s63/s64, sha1-r79/r80: control tracks outside the manifest; lowest value, listed only for completeness.

## 11. Checked, NOT gaps

- SHA-256 feed-forward and digest truncation: CV_in is equal in both members, so digests are equal iff the last eight state words are equal; the profile forbids truncation. One OUT cell (section 4) is enough.
- SHA-256 IV, round constants K, standard schedule: fixed by the profile; no cell.
- Schedule beyond the printed rows: W16..W36 (W37 for r38) are in the universe as 172 schedule links; W38+ are not computed by a 37/38-step hash.
- SHA3 iota constants per round: 40 structural cells already; fine. SHA3 capacity/rate lanes as FIXED input facts: covered once the MSG cells of section 7 exist.
- Traps respected by the existing builder: != printed as "=" + U+0338 (chi files, not the PDF), errata A15[29] = A17[29] (r37) and W25[4] = W25[6] (r38), no W16+ varied with later words held, UNKNOWN is not UNSAT. New cells in 3.1-3.2 must report UNKNOWN as UNKNOWN.
- Known coverage numbers for orientation (COVERAGE.md 12:26): universe 2,100, scanned 1,595 (structural 928, CELLS 349, FILE 318), excluded 371, unscanned 134.

## 12. Order I would run it in

1. M (no compute): map existing records onto G04 (CV gate, classes, H1 evidence), re-label S1-S3, S7-S9 as above. Add the OUT and INIT/OUT cells.
2. G01 and G02 first scan: Poseidon live-profile arithmetic count and one memory-object table per hash (one agent each).
3. B (GPU): H1 uniformity test of the 37/38-step compression outputs; U and tail-rank per bit position b for G03.2 when the long solves allow.
4. A: G05 INIT/PIN/OUT/MSG and G06 ROW/DIG cells (one agent per hash, narrow brief: one question each).
5. G07 premises with fresh seeds, G08 "=" relaxation on the full path, G09 only after the owner picks the track.

Limits of this pass: I did not run any tool, did not re-read the paper tables, and did not verify the per-bit counts of G03.1-3.6 (they are cell proposals, sizes are COUNT from the chi files or GUESS). The relative size of the Poseidon and memory gaps is taken from HANDOFF 10-12 and the package proofs; none of those numbers is an own_test.
