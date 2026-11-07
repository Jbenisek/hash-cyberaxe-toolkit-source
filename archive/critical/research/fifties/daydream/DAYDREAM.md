# Daydream round: five tested ideas, keepers, remaining ideas

Date 2026-10-09. Each test was bounded (about 45 min). Nothing was filed or submitted. Tags: COMPUTED, DERIVED, GUESS as in the agents' reports.

## Tested (verdict, finding, next step)

1. 1-round new-line audit (paths-1, physicist-1a, contrarian-2, paths-2, magician-4) - PROMISING
   - Finding: the complement fold is a new line for our team (not new to the board; rickmanelius 7e29738c, Subflatus3, pratikgx use it). Staged as pkgR1K, log2 T 2.5477, 2 compressions, 154 data ops. 200/200 collisions at rounds=1, digests differ at rounds=2. Organizer `certificates` passed and `intake` returned mechanically_valid (Windows Python with one st_ino shim). The flags-only shape pair duplicates R1F 31acfdbb: drop it. Inversion (O2) is a separate uncosted candidate. Expect no board movement (rivals do not charge our traffic).
   - Not run: the WSL sandbox intake (writes outside the agent's folder). Owner to check proof.md Section 9 wording of the 6b039da2 ruling.
   - Next: with the owner's go, run check_r1.sh on pkgR1K, stage with stage_pkg_r1.sh, then ask for an explicit go on that one `yukon submit`. Owner decides on a costed inversion filing.
   - Folder: daydream\paths-1 + physicist-1(a) + ... (cluster - 1-round new-line audit, complement fold first)\

2. Amortize the local-collision generator (evolution-2, magician-1, arbitrage-4, engineer-3, contrarian-4, alien-1) - DEAD
   - Finding: static: every message word is in the construction support, 0 free bits against about 46 needed. Dynamic (reduced width): founder rate about 2^-31.7 at W=8 and about 2^-58 at W=16, so it falls about 4 bits per bit of width. Neutral freedom is only cycle-root multiplicity (about 2^11 offspring per founder at W=16). Cost about 2^79 against a 2^32 brute residual: loses by about 2W bits.
   - Not run: full W=8 founders; diagonal pass rates were multiplied as if independent.
   - Next: paste METHODS_LINE.txt into METHODS.md (D4 row). Reopening needs a different founder construction, not amortization.

3. 2-round value-conditioned complement trails (contrarian-3, physicist-1b) - DEAD
   - Finding: exhaustive E/C/X DFS with the exact add rule finds no trail with 6 or fewer round-1 conditions even with round 0 free, and none with 7 or fewer with realistic round 0. At least 217 bits, far above the 4-condition line. Spot checks A-D all matched (add rule exhaustive, wiring 31,289 G-steps, round-0 entry 2^20/2^20, truncated condition rate 2^-8.01).
   - Limits: mixed trails (XOR difference later turning into a complement) and v14/flags entry not enumerated.
   - Next: close; paste the T4b sentence next to T4 in METHODS. comp_trails.py with 1 round could check the 1-round team's pattern count.

4. sha3-256-r6 linear structures (alien-3, engineer-4) - DEAD
   - Finding: premise out of date. Board best is 124.04565 (winglock; GordoAR 124.0457), not 124.295. Leaders already use Guo-Liu-Song structures plus Gray-code steps, incremental round 2 and 256-wide bitslicing. Our plan recounts to 127.54 (127.17 with round 2 shared), about 3 bits worse. A 2-round structure would save at most about 0.01 bit (GUESS).
   - Not run: GF(2) rank and the 1,000-member check (accounting decided first).
   - Next: drop it. Real r6 gain must come from rounds 3-4 (25.4k of 31.9k ops per z-step). Update the fact sheet.

5. Solver-proved kernel superoptimization (alien-2, engineer-2, coding-5) - PROMISING
   - Finding: one z3-proved rewrite of the pkgCK (63.1880) kernel gives log2 T 63.18793 -> 63.16708 (-0.02085 bit, exact integers). Uses Lemma KP identities: omega side 19 -> 17 units, fill 54 -> 56, opened cluster 267 -> 257, no added registers, context charge stays 600. Proofs mutation-tested; a 7-lane 256-bit query timed out (unknown) and is covered by a lane-independence argument. Exhaustive search of all 75 windows of 1-4 lines found no further saving; cheaper programs of up to 2 lines also none. Brief's 0.2 bit per op was about 10x too high for this kernel.
   - Next: owner decides whether to put it in the ~63.10 package (edit 9.8 listings, Lemma MB bounds, Section 11 rows, claim text, frontline.py constants, re-run). Open levers: biased packed SUB (+0.005), branch-if-zero model question (about 0.09 bit per lane-test unit).

## Keepers (one line each)

- coding-2: coincidence premise Pr[E1=E3] as a sum over deltas; worth 1-5 bits only if the premise counts one characteristic; check H1' first, GPU slice test.
- arbitrage-5: GF(2) rank of the 128-bit residual (4096 x 129) and 48-bit projection excess collisions; null expected, each exact relation is 0.5 bit.
- evolution-3: phylogenetic footprinting for new lossless filters; real cost-cut route, instrumentation over 45 min.
- physicist-3 + coding-3 + coding-4 + alien-4: Walsh bias, repair influence and cube degree on the REAL inner-loop free bits, run once (degree.py).
- magician-2 + evolution-4: scale pin/advice-record search on the 3090 and test union-of-top-k growth; dependable but incremental.
- evolution-5: heritability gate (split-half yield repeatability vs binomial null), the kill switch for selection ideas.
- magician-3 + historian-3 + coding-1: length XOR 16/32 families unscanned; 62/64 queued; physicist-5 and magician-5 closed negatives; historian-1 and engineer-1 are N12/N13, closed.
- historian-2: COMPUTED fact for the catalogue: injection lateness decides which half is near-affine ((m4,m5) -> half B, (m6,m7) -> half A, (m0,m1) from v12 -> all 8 words).
- paths-4: sha3-256-r5 internal differential at symmetry period 16 or 8, or after a 1-round connector; possible second r5 line.
- paths-5: sha256-r31/r32 Li-Liu-Wang pair with attribution; Grok job 51 is on it, coordinate, do not duplicate.

## Remaining ideas (lens: title)

- physicist: 2 rate function of the residual (floor, condensed phase); 4 anneal the trail, carry-bought mirror alignment; 5 boundary absorption scan (tested, no gain)
- evolution: 1 niche map / G difference grammar plus any-CV 1-round path (duplicates R1V)
- magician: 5 choose the CV in a prefix block (tested, mostly negative)
- chess: 1 inverse collision tablebase; 2 carry-locked multi-block phase sequencing; 3 syndrome-compressed state clustering; 4 rotated basis sparsification; 5 adaptive neutral bit cartography
- arbitrage: 1 fold-kernel pure-message collision (same as complement fold); 2 tree-mode parent/internal-chunk collisions (shape pair, R1F); 3 free option on starting constants (non-root final chunk)
- coding: 5 sequential (Fano/stack) decoding of the member loop (touched by the kernel test)
- historian: 1 length orbit harvest (closed N12/N13); 4 A-half wall claw between two single-source maps
- child: 1 counter-modulated difference cascade; 2 partial round-0 enumeration with round-1 filter; 3 add-rotation interleaving exploit; 4 cross-round message reuse via permutation; 5 tree-attack leverage for long messages
- engineer: 1 length cube (closed N12/N13)
- paths: 3 five sibling length pairs and the 63-vs-64 additive +1 pair (register-level distinctness, GUESS)
- contrarian: 1 map of hidden assumptions behind closed items (index only); 5 length pair 56 vs 64 (or 61/63, 62/64) with more free bytes
