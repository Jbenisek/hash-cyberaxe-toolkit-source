# STRUCTURE: independent check of the chunk-counter lever (folder counter\structure)

Written 2026-10-08. Research only: no yukon, nothing submitted or posted, trace untouched, nothing written
outside this folder. All code here is my own (b3own.py, tree64.c, model.py, cone.py, arrange_check.py,
e2e_small_t.py, tdist.py, big_*.py/sh). The only outside code that runs is the organizer's
hash-smash\verifier\blake3.py, used as the referee. Tags: COMPUTED = run here (file named); DERIVED = follows by an
argument given here or is read from a named source; GUESS = judgement, not checked.

## 0. Answer

1. Tree mode (COMPUTED). For M = P||X and M' = P||X', where P is t full 1024-byte chunks, the last chunk's
   compression is (cv = IV, block X, v12 = t mod 2^32, v13 = t >> 32, v14 = 55 or 63, v15 = 3), and the organizer's
   digest is a function of that chunk's CV alone (the prefix is fixed). So equal last-chunk CVs give equal
   digests. Checked on the organizer's verifier for 25 values of t from 1 to 1025 (150/150 messages, 75/75
   planted-CV pairs), and at t = 2^32 + 5 (v13 = 1) through my validated C tree hash plus the organizer's own
   final-merge functions (4/4).
   The converse ("only if") holds unless a parent compression collides separately (DERIVED).
   The shortest pair has t = 1: 1079 and 1087 bytes.
2. Bases (COMPUTED in my own word model, decided exactly by reverse peeling and validated against brute force).
   - Counter fixed: Y4 plus any of E1.d1, E1.b1, E3.h1, E3.g1, E3.e2, Y6, Y14, Y9, Y1, w8 has NO basis.
     This matches the team.
   - With t free: Y4 plus each of E1.d1, E1.a1, E3.h1, E3.g1, E3.f1, E3.e2, Y2, Y6, Y10, Y14 has a basis.
     E1.b1, E1.a2, Y1, Y5, Y9, Y13 and w8..w11 still have none. Three words (Y4, E1.d1, E3.h1) have none, even
     with v13 free too. This agrees with the scout on every item it lists.
3. Arrangement (COMPUTED, real 32-bit arithmetic; the organizer's _chunk_output/_compress are the referee).
   Y4 (a sub-class member) and the context are fixed per outer step; c1 is drawn inside the T1 cube and
   E1.d1 = c1 - Y11; t is solved per trial.
   - 3,000/3,000 trials (60 outer steps, v13 = 0), 1,200/1,200 (v13 = 1) and 1,200/1,200 (v13 = 2^18 - 1):
     CV words 0, 2, 5, 7 of the 55-byte and 63-byte last chunks are equal.
   - In every trial: Y4, E1.d1 and c1 are as prescribed, beta = 18b0e098, eta = 830303cf, round-0 states
     are equal for A and B, and 0 internal-word mismatches.
   - Complete messages hashed by the organizer's blake3(): 4 trials with t = 4, 10, 51, 133 and 2 trials with
     t = 1 (1079 / 1087 bytes). The organizer's digest equals root(stack, CV_t), and CV words 0, 2, 5, 7 agree.
4. Net value (GUESS on cost; DERIVED from team counts that I did not re-derive): forcing T1 multiplies the
   per-trial rate by 2048 x 67,698,688 / 185,350,144 = 748 (9.55 bits) against the board's sub-class count.
   The per-trial cost of the new inner loop, about 3 to 5 packed ops, is not counted on a program.
   - Best estimate of the net gain: about +9.3 bits at the board's conventions (93.0 -> about 83.7),
     uncertainty about 1.5 bits.
   - The counter-claim measured rates per random trial at a fixed t, and the cluster model's co-pass. Neither
     touches the prescription, so it does not refute the lever (section 4).

## 1. Tree mode (tree_check.py -> tree_check.txt; tree64.c; big_check.py -> big_check_t2p32p5.txt)

Each item gives its check, its result and its tag.

- (a) Organizer digest(P||X) == own root_from_stack(own stack(P), own CV_t(X)). 150/150 for t in
  {1..9, 15, 16, 17, 31, 32, 33, 63, 64, 65, 100, 255, 256, 257, 1000, 1024, 1025}, 3 random 55-byte X and
  3 random 63-byte X (ending in 8 zero bytes) per t. COMPUTED.
- (b) Organizer last-chunk descriptor == (IV, words(X), counter t, len, flags 3), and the organizer's CV
  equals mine. 150/150. COMPUTED.
- (c) Planted CV collision: the organizer's _compress is patched so that only the last-chunk call of X'
  returns X's output. The organizer's digests of P||X and P||X' are then equal: 75/75. COMPUTED.
- (d) Unpatched pairs give different digests: 75/75. COMPUTED.
- (e) My C program tree64 (4 threads x 8 SIMD lanes) equals the organizer's digests and stack:
  25/25 values of t. COMPUTED.
- (f) The last-chunk CV for t >= 2^32 (2^32, 2^32 + 5, 2^33 + 12345, 2^51 - 1, one random value) is the same
  in the organizer's code and mine: 10/10. v12 = t mod 2^32 and v13 = t >> 32. COMPUTED.
- (g) t = 2^32 + 5, with v12 = 5 and v13 = 1, on messages of 4,398,046,516,279 and 4,398,046,516,287 bytes.
  The C program computed the full tree: 2^36 chunk compressions in 85 s. Its digest equals the organizer's
  final merge (_chunk_output, _compress, _parent_output, ROOT) from the C prefix stack: 4/4. Same at
  t = 2^26 + 3: 4/4. COMPUTED.

The prefix stack at 2^32 chunks can only come from the C program. Its trust rests on (e).

Facts used and their tags:
- The verifier rejects byte lengths >= 2^61, so t <= 2^51 - 1 and v13 < 2^19. DERIVED from blake3.py
  line 70.
- Flags are 3 for a one-block last chunk. The digest is the root PARENT compression (flags 12) over the
  stack and CV_t. DERIVED.
- P can be any 1024t bytes; identical chunks are only convenient. DERIVED.
- With t = 1 the messages are 1079 and 1087 bytes, with v12 = 1, v13 = 0, v14 = 55/63, v15 = 3. DERIVED;
  real instances in e2e_t1.txt.
- "Digest words 0, 2, 5, 7 equal" becomes "last-chunk CV words 0, 2, 5, 7 equal". The final digests of the
  pair are unrelated until all 8 CV words agree (e2e files: digests differ, as expected). So an
  organizer-run experiment must show the half-collision through the verifier's internal functions, not
  through blake3(). DERIVED.

## 2. Bases (model.py -> model_out.txt; cone.py -> cone_out.txt)

How the model is built (DERIVED):
- Each G assignment is one equation over its unknown words, solvable for any one of them.
- E1 and E3 first halves are modelled with Y11, Y3 and w15 substituted.
- Constants: the IV, the length, the flags, X3, X7, X11, X15, w4, w13, w15 and w14 (w14 is free in the
  variant), K2's first four values and C3.
- The counter: v12 = T0 and v13 = T1 are unknowns or constants.
- Sizes: 100 words and 92 equations at counter 0, so the basis has 8 words. The team's 104/96 includes K2's
  4 constant lines.

The algorithm:
- A basis containing a forced set F exists iff reverse peeling removes every equation. Reverse peeling
  repeatedly deletes an equation that owns a word outside F that no other remaining equation contains.
- Proof (DERIVED): in any triangular order, the last equation's output occurs in no earlier equation, so
  peeling can undo any order. Conversely, a peeling read backwards is a triangular order whose basis is the
  unclaimed words. A private word stays private when other equations are deleted, so greedy peeling is
  complete.
- Validation: against brute force over all bases, 600 random systems, 0 mismatches. COMPUTED.

Results (COMPUTED). The YES column lists words T that can join Y4 in a basis. Basis size: 8 at counter 0,
9 with T0 free, 10 with T0 and T1 free (one more each with w14 free).

| counter | YES (Y4 + T) | NO |
|---|---|---|
| fixed (0) | Y0 Y8 Y12 w0..w3 w5..w7 w12 X2 X9 X14 | E1.d1 E1.a1 E1.b1 E1.a2 E3.h1 E3.g1 E3.f1 E3.e2 Y1 Y2 Y5 Y6 Y9 Y10 Y13 Y14 w8..w11 |
| T0 free | the above + E1.d1 E1.a1 E3.h1 E3.g1 E3.f1 E3.e2 Y2 Y6 Y10 Y14 | E1.b1 E1.a2 Y1 Y5 Y9 Y13 w8 w9 w10 w11 |
| T0, T1 free | the above + w8 | E1.b1 E1.a2 Y1 Y5 Y9 Y13 w9 w10 w11 |

- Pairs with Y4, in every case: (E1.d1, E3.h1), (E1.d1, E3.g1), (E1.d1, E3.e2), (E1.d1, Y14), (E3.h1, E3.g1)
  and (E1.d1, E1.b1) are all NO. So t buys exactly ONE extra prescribed word.
- With w14 free the pattern is the same; w11 joins the YES list.
- w8 is YES only with T1 free. T1 is limited to 19 bits, so the solver can fix it only within that range;
  as a solved word it is a 2^-13 filter. Not useful.
- The filed 8 words plus E1.d1, with T0 determined, are triangular (0 checks). So are the filed 8 plus E3.h1,
  and the filed 8 plus T0. COMPUTED.
- Cone (cone_out.txt): 16 words move with E1.d1. They are E1.a1, E1.a2, E1.b1, E1.d1, E3.e2, E3.f1, E3.g1,
  E3.h1, K0.a1, T0, Y2, Y6, Y10, Y14, w0 and w1. No word of round 0 (S or X) moves. Per-trial equations up
  to each test: E1.b1 3, E1.a2 4, E3.h1 5, E3.e2 8, T0 8. This matches the scout's 3 / 5 / 8. COMPUTED.

Why it works (DERIVED):
- K0.d1 = ROR(t ^ K0.a1, 16). With t free, K0.a1 (and so w0) is free while all of round 0 stays fixed.
- w0 enters round 1 only in C2's y word: Y2 = C2.a1 + C2.b1 + w0. The chain Y2 -> Y14 -> Y10 -> Y6 -> E1.a1
  -> E1.d1 is a bijection at each step, so any E1.d1 is reachable. The same chain, the other way, reaches
  E3.h1, E3.g1 and E3.f1. One word, one prescription.

## 3. Real arithmetic of the arrangement (arrange_check.py -> arrange_check*.txt; e2e_small_t.py -> e2e_*.txt)

The construction is proof.md section 4, rewritten here with three changes:
- K3.a1 = ROL(K3.d1, 16) ^ 3 (flags 3).
- K1.a1 = ROL(K1.d1, 16) ^ v13.
- K0.a1 is left for the trial.

The trial:
- c1 is drawn uniformly in the cube (c1 AND 0e09818b) = 02008000, and E1.d1 = c1 - Y11.
- E1.a1 = ROL(d1, 16) ^ Y12; Y6 = E1.a1 - Y1 - w12; Y10 = ROL(Y6, 7) ^ C2.b1; Y14 = Y10 - C2.c1;
  Y2 = ROL(Y14, 8) ^ C2.d1; w0 = Y2 - C2.a1 - C2.b1.
- K0.a1 = IV0 + IV4 + w0; t = ROL(K0.d1, 16) ^ K0.a1; w1 = S0 - K0.a1 - K0.b1.

Results:
- Seed 11, 60 outer steps x 50 trials, v13 = 0. COMPUTED. Every item is 3000/3000:
  - organizer descriptor (IV, words, t, 55/63, flags 3);
  - the zero bytes;
  - CV words 0, 2, 5, 7 equal;
  - Y4 = prescribed and Y4 in the sub-class;
  - E1.d1 = prescribed, and c1 in the cube;
  - beta = 18b0e098 and eta = 830303cf (forward);
  - equal X for A and B;
  - S, X and w2..w15 constant within an outer step.

  Also: about 75 internal words per trial checked against the forward trace, 0 mismatches; 0 full CV
  collisions; t = 0 never; t spans 3.7e6 to 4.29e9, mean log2 30.5.
- v13 = 1 (1200 trials) and v13 = 262143 (1200 trials): all checks pass. t up to 2^50. COMPUTED.
- The map E1.d1 -> t is a bijection per outer step (composition of bijections, DERIVED). On the cube, t
  took 2^21 distinct values in 6/6 outer steps. COMPUTED.
- t over the cube is NOT spread like random numbers. The minimum over 2^21 cube values was 2.1e6 to 1.1e9
  in 6/6 outer steps and 51,266 to 1.1e9 in 8 more. Uniform values would give about 2^11. COMPUTED
  (tdist.py).
  - Small t still occurs. With t = 1..512 in the cube, 4 hits came in 620 outer steps. t = 1 hits came in
    2 of 4580 outer steps (2.2 expected). COMPUTED.
  - Hits cluster in a few outer steps. GUESS: the reason is the near-affine map (net rotation ROR 1).
  - Consequence: a real collision found by this search has t about uniform below 2^32, so its messages
    are about 2^41 bytes (2 TiB) on average. Hashing them costs about 2^36 compressions, negligible in the
    cost model; how a judge reacts is a GUESS / risk.
- Complete messages (e2e_small_t.txt, e2e_t1.txt). COMPUTED. Six real trials of the arrangement, with
  t = 4, 10, 51, 133, 1, 1. P is t random identical chunks. Each check holds in 6/6:
  - the organizer's blake3(P||A) and blake3(P||B) equal the own root(stack, CV_t);
  - CV_t words 0, 2, 5, 7 are equal;
  - Y4, E1.d1, the cube, beta and X are as prescribed.

  The digests differ, as expected. The shortest of these pairs are 1079 / 1087 bytes; the last-chunk bytes
  are printed in the file.

## 4. Net effect

Gain in rate. DERIVED from team counts quoted in HANDOFF (16:15 and 852-line bullets); I did not recount
them.
- The counts: beta 18b0e098 (c1 ^ c1' = 0e09818b, the T1 cube, P = 2^-11) carries 67,698,688 of the
  sub-class count 185,350,144, and 71,698,432 of the class count 162,266,764.
- Forcing c1 into that cube makes the per-trial rate mass x 2048.
- Against the board's F count (C15, 185,350,144): 748x = 9.55 bits.
- With Y4 taken from the whole class (Y4 is no longer a loop variable): 792x = 9.63 bits. Rule A, which
  needs the sub-class, would then have to be replaced.
- The HANDOFF's "905x" is the same mass against the class count: 2048 x 71.70M / 162.27M = 904.9.
  Re-derived arithmetic.

Assumption: the H1 model treats c1 as uniform, so conditioning on the cube is exact inside the model.
- In this arrangement, the six non-Y4 residual words (d1, Y6, a1 + w5, Y14, Y9, w8) are uniform over outer
  steps:
  - Y6 through Y12 and Y1 + w12;
  - a1 + w5 through w5;
  - Y14 through C2.b1 and C2.c1;
  - Y9 and w8 through the context.
- Inside one outer step only d1, Y6, a1 + w5 and Y14 move. That is the same "average over outer steps"
  premise as the filed path. DERIVED.
- With 2^21 trials per outer step and a per-trial rate of about 2^-91, clumping inside outer steps does not
  matter. DERIVED.

Cost. GUESS: not built or counted.
- Per trial: one step of the cube counter (4 ops), d1, a1 (rotation + xor), Y6, Y10 (rotation + xor), Y14,
  and rule A on Y14 ^ e1 (about 9 ops as in Lemma A). That is about 22 to 26 vector ops per 8 lanes, so
  about 3 to 3.5 per trial.
- Stage 2 (Lemma N on E1 for both messages) runs on 2^-8 of the trials.
- The outer step (about 250 ops per 2^21 trials) is negligible.
- The board's 93.0451 implies about 3.39 ops per trial (118.25 - log2(132,392,960) + log2(ops) + 0.012).

Result. GUESS:
- time_log2 = 118.2515 - log2(67,698,688 x 2048 / 1.4) + log2(3.4) + 0.012, about 83.5.
- With the cost anywhere in 2.7 to 5.5 ops: 83.2 to 84.2.
- Net gain about +9.3 bits (range 8.8 to 9.9). Uncertainty about 1.5 bits, which also covers a model
  failure for one forced beta.

Counter-claim (scout_cross):
- 1b (rates unchanged across counters) is consistent with this. A counter only relabels random trials, and
  the lever does not claim a rate change per random trial.
- 1c (t = 0 best; random t lowers the X2 co-pass and x30/x31) is about the cluster lever (H4) at a constant
  t. The board's 93.0 entries use no clusters (HANDOFF 15:55), and this arrangement uses none either. So 1c
  does not reduce the gain against the board.
- Against our own cluster package (92.3 to 92.6 at the field's margin), the gain would be about 1 to 1.5
  bits smaller, unless clusters can be rebuilt on the new inner loop. Unknown.

Not done here, and so not established:
- No program counts the trial.
- No toy end-to-end collision with the counter (the toy folder's job).
- No organizer-run evidence. Organizer-run experiments would have to show the CV half-collision through the
  verifier's internal functions (section 1).
- The judge's view of 2-TiB messages and of a non-root colliding compression.
- Better cube choices (a richer Y4 set for this beta, or a sub-cube of c1): could add a little. GUESS 0 to
  1 bit.

## 5. Files and commands (Windows python 3.14 + numpy; C via WSL Ubuntu)

| file | what | run |
|---|---|---|
| b3own.py | own 2-round compression, chunk CV, stack, root | imported |
| tree_check.py | part 1 (a)-(f) | `python -B tree_check.py 3 > tree_check.txt` (~20 s) |
| tree64.c, build.sh | C tree hash, 4 threads x 8 lanes | `wsl -d Ubuntu -- bash .../build.sh` |
| big_prep.py, big.sh, big_check.py | large-t run and check | `python -B big_prep.py`; `wsl -d Ubuntu -- bash .../big.sh 4294967301 big_t2p32p5.txt 600` (85 s); `python -B big_check.py big_t2p32p5.txt` |
| model.py | word model, peeling, brute-force validation, basis table | `python -B model.py > model_out.txt` |
| cone.py | order and per-trial cone of the arrangement | `python -B cone.py > cone_out.txt` |
| arrange_check.py | part 2c (env THI = v13) | `python -B arrange_check.py 60 50 6 11 > arrange_check.txt`; `THI=1 ... 30 40 0 12`; `THI=262143 ... 30 40 0 13` |
| e2e_small_t.py | complete messages with small t | `python -B e2e_small_t.py 512 50000 4 22 > e2e_small_t.txt`; `... 1 200000 2 23 > e2e_t1.txt` |
| tdist.py | distribution of t over the cube | `python -B tdist.py 8 3` |

All processes I started have finished. No GPU was used: nothing here needed it.
