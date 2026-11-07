# combo-finder: pairs of closed routes whose obstructions could compensate (SHA3-256 r6, 2-round BLAKE3)

Scout, 2026-10-10 (clock read 01:55 at start). Our own team's research; nothing filed or submitted; no yukon, no network,
`.key` not opened. Labels: COMPUTED (run here, outputs in this folder), DERIVED (arithmetic or short algebra on computed or
cited numbers), GUESS. "cited" = quoted from the named map or scout RESULT.md (its own label kept).
Owner's rule applied: a route that is dead alone was NOT assumed dead in combination; each pair below is judged on whether one
route's surplus pays for the other's missing condition.

## Verdict: open. SHA3 pair dead; BLAKE3 pair unresolved, paper cost below the front line

- **25 pairs listed** (12 SHA3, 13 BLAKE3; tables in sections 1-2). Each has a one-line mechanism and a quick cost bound.
  Two are open beyond this budget: SAT x LD (weeks-scale), and the BLAKE3 local-collision joint (TEST 1). The rest are dead
  or impossible, by derivation from cited numbers or by TEST 2.
- **TEST 1, BLAKE3: local collision {m2,m3,m4,m6} (D4/V5 family) x instance freedom (counter/CV/flags)** (section 3).
  I built every stage, checked it on the real G call, and measured it at the root (a full 2-round collision of two 64-byte
  messages if all stages pass).
  - K2 is solvable for only **1,270 of 2^32** forced differences (COMPUTED, exhaustive; each has about 450,000 bases).
  - K3: 2^-37.92 per sample, but a large D set (202 distinct D over 22 deltas, none shared).
  - K1: 9 of 1,408 (delta, dv6) problems, about 10 solutions per scan for a K1-good delta.
  - D3: 2^-18.1 per attempt (2^-10.7 x 2^-7.4) on inputs with D from K2's set (COMPUTED).
  - **The joint (-D in K2's set) was never observed: 0 of 202 distinct D** (0 of 7,990 K3 solutions).
  - Paper cost about **2^54-2^56 units** if K3's D set is independent of K2's (GUESS), against pkgCM 62.7934.
  - Decisive next test: a targeted K3 solver for D in -D2, then K1/D3/D1/C0 and assembly on a real joint (section 6).
  - The instance levers do not raise per-instance rates. What helps is that each joint brings unlimited K1/D3 retries.
- **TEST 2, SHA3: low degree x connector** (section 4): dead.
  - Even the lightest field differences found (round-2 difference of 28-52 bits) keep 1 of 40 dimensions through chi3
    (rank 39). Differences from outside W40 cost 25-40 of the 40 dimensions at round 2, then 0 dims are left after chi3.
  - Rounds 4-6 are unbiased (COMPUTED). The connector's DF deficit is not paid.
- Owner's rule respected: the D4 / V5 route (closed alone by clumping) was rebuilt and re-measured in combination with every
  instance lever, not assumed dead.

## 1. SHA3-256 r6: closed routes used (ids) and pairs

Routes (cited: SHA3R6_MAP.md 3-4, s3-* RESULT.md, D19/D20):
LD low-degree FES on W40, 122.98920 (alive; obstruction: it is a birthday, Q = 2^127.99 candidates; surplus: 2^280 cosets x 40
inner dims, 50.68 ops/candidate = 2^-5.00 units) | ID period-32 internal differential (2^105 at r5; 2^172 at r6: 4th-chi
branching 2^-16, quotient rank 118, reduced first block kills 120/160 S-boxes) | CONN GLST 2-round connector + 4-round trail
(2^197-2^206; 5 DF left, 3-round connector >= 33 DF short) | LIN 2-round linear structure as leader patch (<= +0.08 bit) |
3R three-round structure, identity or non-identity chi1/chi2 (rank <= 2; theta3 adjacency, >= 50 persistent chi3 bits per
direction) | DK triple-kernel space (dim 186, min weight >= 262) | FIX fixed round-3 difference in the 35-space (34 conditions ->
1 pair) | CAP 2-block capacity (reshapes the 2-round field; 3-round dim 1 at random capacity) | PD chi6 plane degrees (0/320
below 8) | SYM symmetric fields x idiff (>= 2^187.2) | DDS DDS trails (>= 2^140.6 rigorous, 234-253 realistic; digest-round lone
bits at x <= 3) | SAT SAT tail after a 2-round connector (bar T <= 128.2-131.1, best known about 132).

| pair | different obstructions? | one-line mechanism | quick cost bound | status |
|---|---|---|---|---|
| LD x CAP (owner) | yes: LD lacks sub-birthday structure, CAP lacks a 3-round field | capacity re-gates chi1 so block 2 could hold a 3-round-affine field; FES degree 8 -> 4 | ceiling: FES chain is 16.79 of 50.68 ops/cand, degree 4 saves about 8.2 ops = 0.25 bit (DERIVED); needs rank >= ~16 at round 3, but capacity only selects chi transitions and s3-chi-transitions already let chi2 constants be free (z3 superset): 0 triangles -> rank 2 | dead (subsumed; <= 0.25 bit even if it worked) |
| LD x ID with chosen first block (owner) | yes: ID dies at chi4 branching, LD has cheap trials | FES makes each ID trial 2^-5 units; first block chosen to make the capacity symmetric | ID r6 2^172 -> 2^167 with FES pricing (DERIVED); a symmetric capacity needs 256 conditions at p=32 (2^256 first blocks, DERIVED); symmetric fields give >= 2^187.2 (cited) | dead |
| LD x CONN (owner) | yes: CONN lacks DF, LD has 40 surplus dims and cheap pairs | keep the pair difference constant on the field through round 2, pay chi3 conditions as linear field conditions, FES the pairs | needs dim >= 16 left after chi3 and a tail <= 129 bits (DERIVED from s3-tda-sat's bar with k = 5). TEST 2: 0-1 dims survive chi3, including for the lightest field differences found (28-52 bits after round 2) (COMPUTED) | **dead (TEST 2)** |
| trail x LD (owner) | same as above from the trail side | per-pair price k: 3.1 -> 5 moves the bar to T <= 129 | best known tail about 132 (cited), DDS >= 134.6/140.6 (cited); no FES-priced pair family survives chi3 (TEST 2) | dead |
| 3R x CAP (owner) | no: both stop at theta3 adjacency | capacity changes which chi1/chi2 transitions occur | s3-chi-transitions enumerated all 64 kernel-preserving chi1 transitions per 6-bit seed and left chi2 constants free: 1,552 rank-2 pairs, 0 triangles (cited) | impossible as a pair (same obstruction) |
| CONN x CAP | partly | prepared first blocks buy connector DF | >= 2^156 (cited, MAP 3.3) | dead |
| DDS x LD | yes: DDS dies at the digest round, LD cuts per-pair cost only | FES-priced DDS pairs | DDS realistic 234-253 bits; rigorous floor 140.6 -> >= 2^133.6 even at k = 6 (cited) | dead |
| ID x SYM x LD | no | symmetric field, low degree idiff | deg 16 at r6, no bias, >= 2^187.2 (cited) | dead |
| LIN x LD | no (same 2-round field) | patch saving is on chi2, which FES never computes | 0 bit (DERIVED) | dead |
| PD x conditions | yes | fix the 18 conditionally constant chi3 inputs | they never reach chi4 (0 of 480,000); <= 0.05 bit ceiling (cited) | dead |
| FIX x CAP | partly | capacity re-gates the 35-space | chi3 polarization rank 595 full -> 1 pair per 34 conditions (cited) | dead |
| SAT x LD | yes | SAT tail priced at FES speed | same bar as trail x LD; weeks-scale search (cited) | open (beyond budget) |

## 2. 2-round BLAKE3: closed routes used (ids) and pairs

Routes (cited: BLAKE3_2ROUND_MAP.md section 5, b3-* RESULT.md): FL front line pkgCM 62.7934 (pins + class + counter; 4 checks,
2^-91.126 per trial) | MITM E1/E3 split (2^128 per split point; lift peak 4 words) | 4C four-checks theorem (round-0 cancel ->
k >= 4) | PIN5 no fifth forced word | CV CV/tree differences (>= 63.6) | FIXE3 fix E3, search E1 (84.61) | D4 local collision
across the round boundary (2^-63.7 projection, about 2^65; strong clumping) | SPIR periodic/spiral (0 of 1,048,575; 0 of 252
tau) | TRL counter/flag trails (case Z >= 2^64.1; case NZ open) | JOIN const x join (q = 0 -> 2^129) | FOLD (impossible) | HEUR
class heuristic (flat) | MODE parents (2^129) and V5 internal block {m2,m3,m4,m6} (open, GUESS 2^50-2^62) | R1C lift (2^128),
t_hi walk (<= 1.21 bit, open).

| pair | different obstructions? | one-line mechanism | quick cost bound | status |
|---|---|---|---|---|
| MITM x member loop (owner) | no: both are "E1 and E3 move together" | split the member walk into E1-only and E3-only moves | inside one outer step E1/E3 inputs are a bijection (cited, SOLCLOUD_14); t_hi frees {Y4, E1.c1, w8} but never Y1/Y9 (cited, b3-r1c): lift peak 4 words = 2^128 | dead |
| D4 x counter freedom (owner) | yes: D4 dies on clumped per-instance solvability, the counter re-rolls instance constants for free | counter t enters only K0 (t_lo) and K1 (t_hi); in the {m2,m3,m4,m6} local collision K0 is a free call and K1 is a forced stage, so t_hi re-rolls K1 | t_hi legal only for messages >= 4 TiB (t >= 2^32). TEST 1: K2 solvable on 1,270 of 2^32 dm4; joint 0 of 202 distinct D; K1 9 of 1,408 problems; D3 2^-18.1 per attempt (COMPUTED); paper cost about 2^54-2^56 units if the joint behaves independently (GUESS) | **open (TEST 1)** |
| D4 x CV freedom (internal block) | yes: same | each prefix block redraws h, i.e. the K1/K2/K3 instances, for 1 compression | re-rolls cost a 2^32 K2 enumeration each (2^28.3 units); K3 rate 2^-37.9..-39.9 over 4 instances, the root best (TEST 1) | no per-instance gain; open with the joint |
| SPIR x pins (owner) | yes | periodic part only in the residual half | 0 of 252 periodic tau satisfy both front-line E3 carry equations (cited) | dead |
| internal-block LC x length cancellation (owner) | yes: V5's K2 stage is forced, Lemma L cancels a v14 difference in K2 with probability 1 | use a 55/63-type length difference so K2 is clean; w4 must then be absorbed at C3 by dX3 and w5 at E1 by (Y1, Y12, w12) | E1 absorption needs dY1 + dw12 = dw4 and an E1 compat, i.e. a final-step (round-1 diagonal) condition, so the route re-enters the four-check family; b3-mode's truncated search with a v14 difference gives B >= 3 round-1 word conditions, same as message-only (cited). Lemma L does lift the {m2,m4,m13} infeasibility (the "b1 injective in a1" step needs v14 equal, DERIVED) | dead at word level (B >= 3 = message-only); not tested at bit level |
| TRL (flags) x pins | yes | pins make G4/G6 deterministic | the flag route's parent side has no free message words; 6 prescribed words (X3, X7, X11, X15, w4, w13) via child search >= 2^192 (DERIVED) | dead |
| TRL (case NZ) x local collision | yes: TRL's floor is for case Z only | V5 is an explicit case-NZ route with a clean final step | the NZ route exists algebraically; every stage but the K3 x K2 joint was measured passable (TEST 1) | open (TEST 1) |
| FIXE3 x t_hi walk | yes | walk 2^19 steps per outer step while E3 stays fixed | the walk moves D0 (w8) and C1 (Y9), both E3 inputs (cited, b3-r1c) | dead |
| JOIN x counter | no | counter adds a free word to the split | q = 0 with t free (cited) | dead |
| MODE parents x pins | yes | pins at a parent | parents have no free words: 8 conditions, 2^129 (cited) | dead |
| FOLD x anything | - | fold = collision condition | impossible (cited) | impossible |
| HEUR x class | no | - | S flat on 2,997 points (cited) | dead |
| CV x local collision | partly | CV difference absorbed by a local collision | 224-bit near-collision first block about 2^64 (cited) | dead |

## 3. TEST 1 (BLAKE3): local collision {m2,m3,m4,m6} (D4 / V5 family) x instance freedom

Instance: the ROOT compression of a 64-byte message (h = IV, t = 0, b = 64, flags 11), so a full compression collision
there is a full 2-round BLAKE3 collision of two 64-byte messages.  The instance levers (CV re-roll per prefix block,
counter t_hi for K1, flags for K3) are the "freedom" side of the combination; at the root they are fixed, and delta (32
bits) is the free difference.  Tools: b3lc.h (stage solvers, self-tests 0 bad), k3gpu.cu, k1gpu.cu, b3lc_stats.c,
d3test.c, b3final.c.

Stage table (filled as measured):

| stage | what is measured | result |
|---|---|---|
| self-tests | compat cube, carry DP, rotation DP (exact vs 2^32 brute force x4), D1 DPs | 0 bad (COMPUTED) |
| K3, CPU, random h7/flags/delta | 2^33.7 samples | 0 non-trivial solutions (the 5 hits were delta = 0, now excluded) (COMPUTED) |
| K3, GPU, root, uniform delta | 2^42.38 samples in 120 s | 22 solutions: 2^-37.92 per (A,delta) sample; compat alone 2^-13.92 (COMPUTED) |
| K3, GPU, root, my guessed structured delta | 2^42.60 samples | 0 solutions (guess wrong; compat falls to 2^-18.73) (COMPUTED) |
| K3 solution shape | 22 solutions | v2(delta) in {1,2} (15/7), v2(D) in {0,1} (18/4), popcount(delta) 13-21, 1-32 m7 values each (COMPUTED) |
| K1, CPU, random everything | 2^33.4 samples | 0 solutions (COMPUTED) |
| K2, root, exhaustive | all A2 in 2^32 (F2 collisions by bucketed sort, 627 s) | 5,380,950,122 ordered K2(a) pairs (2^32.33); 570,922,486 also pass K2(b) (2^29.09): P(b given a) = 2^-3.24, NOT the 2^-13.7 an independent compat would give (COMPUTED) |
| K2 valuations | all 570.9M K2-solvable records | v2(dm4) = 0: 214.4M, 1: 198.5M, 2: 18.1M, 3: 139.9M, none above 3; K3 forces v2(D) in {0,1}, which 72% of K2 records share (COMPUTED) |
| **K2 clumping** | distinct dm4 among the 570.9M records | **only 1,270 distinct dm4 (2^10.31)**, about 450,000 bases A2 each; density 2^-21.7 of all forced differences; the set is closed under negation; popcount 9-24 (COMPUTED) |
| K2 on the real G | first 1,000,000 records | 0 bad (outputs a,c equal, b,d differ, values match the model) (COMPUTED) |
| K3 clumping (GPU full A-scan) | each of the 22 good deltas, all 2^32 A | 4 to 1,592 K3 solutions per delta (total 7,990) but only 1 to 35 distinct D per delta (about 200 in all) (COMPUTED) |
| **K3 x K2 joint** | is -D in the 1,270-value K2 set? | **0 of the ~200 distinct D (0 of 7,990 K3 solutions)** (COMPUTED); random-overlap expectation 200 x 2^-21.7 = 0.00006 (DERIVED) |
| K3 x K2, whole root instance | size of K3's achievable D set | about 2^20.8 good deltas (2^26.1 solutions / harmonic-mean 40 per delta) x ~5-10 D each, so about 2^22-2^23 D values; expected overlap with 1,270 values about 1-2 values per instance if independent (DERIVED/GUESS) |
| K1 (GPU full scans, stage-marginal) | 352 problems = 22 good deltas x 16 real K2 outputs (dv6) | 93 K1 solutions, but in only 2 problems (91 and 2), i.e. 2 of 22 deltas; 25 s for 2^40.5 evaluations (COMPUTED) |
| D3 (stage-marginal) | 93 K1 solutions x K2 cube elements keeping dv6 (1,648 runs) | 0 runs with any D3(i) solution; D1/C0 not reached (COMPUTED). Caveat: here K2's dm4 is not -D, so v14^v14' is not the joint one |
| D3, K2-consistent | same 1,648 runs with D := -dm4 of the K2 record (so v14^v14' has the joint structure) | 0 runs with any D3(i) solution (exact rotation-DP counts over all 2^32 m14) (COMPUTED) |
| D3, with K1's own M | all 93 K1 solutions | v2(M) = 0 for all (M = v9 - v9'); with D from -D2 of matching valuation and eta = 0: 0 of 62,496 exact counts (COMPUTED) |
| D3(i) baseline (d3base.c, out_d3base.txt) | 100,000 to 2,000,000 random inputs per row | random (v2 = 0): 52/100,000 = 2^-10.9; eta = 0: 1/100,000 = 2^-16.6; D in -D2, random eta and M: 1,186/2,000,000 = 2^-10.7; K1's M with eta = 0: 0/100,000 (COMPUTED). So the zeros above match the generic rate (1,648 x 2^-10.7 = 1.0 expected); they are NOT a structural wall |
| D3(ii) given D3(i) | the 1,186 solvable (D in -D2) cases, 64 resamples of m14 each | 7 of 1,186 (2^-7.4) pass (ii) (3 on the first sample) (COMPUTED). D3 per attempt about 2^-18.1 (DERIVED) |
| K1, larger sample | 1,408 problems = 22 good deltas x 64 real dv6 | 2,522 solutions in only 9 problems; 4 of 22 deltas solvable within 64 dv6 (6 of 22 over both runs); mean 1.8 solutions per 2^32 scan (heavy-tailed); about 10 per scan for a K1-good delta (COMPUTED) |
| K3, other instances (CV / flags lever) | 90 s GPU each, uniform delta | h7 = 8f1bbcdc flags 0: 2^-38.68 (6 solutions); h7 = 2a5b9c13 flags 2: 2^-39.88 (3); h7 = IV7 flags 0: 2^-39.36 (4); root (IV7, flags 11): 2^-37.92 (22) (COMPUTED) |

**Reading (DERIVED from the table; GUESS where marked).** The combination leaves the clumping D4 reported in place, but it
shows where it bites. It does NOT close the route.
- Two stages are solvable only on tiny sets: K2 on 1,270 forced dm4 (of 2^32), and K1 on a few (delta, dv6) pairs (9 of 1,408).
  K3's achievable D set is large: 202 distinct D over 22 deltas, none shared, so about 2^22-2^23 values per instance.
  D3 is rare but generic: 2^-18.1 per attempt.
- The instance levers do not raise any per-instance rate. K3 varies 2^-37.9 to 2^-39.9 over 4 instances; the root is the
  best seen. The counter enters only K0 (a free call) and K1 (t_hi, legal only for messages >= 4 TiB). Their value is that
  every joint brings unlimited K1/D3 retries: about 450,000 K2 bases per dm4 give endless dv6 and v14 choices.
- **Paper cost (GUESS-heavy).** Steps, in 2-round-compression units:
  - One K3 solution: 2^37.92 samples x 2^-4.1 units = 2^33.8. A full scan of its delta (2^27.9) reveals about 9 D values,
    so about 2^30.6 per distinct D.
  - One joint (-D in the K2 set): about 2^21.7 distinct D if K3's D set is independent of K2's (GUESS), so about 2^52.4.
  - K1-good deltas: about 6/22, so about 3.7 joints are needed: about 2^54.3.
  - Inside one joint: D3 needs about 2^18.1 attempts. A K1 scan (2^27.9) yields about 9.9 solutions x 17.7 v14 choices
    (2^7.45 attempts), so about 2^10.7 scans = 2^38.6 units (DERIVED).
  - D1 and C0 have 96 free bits for about 78 bits of conditions and were not measured (GUESS: pass).
  - **Total about 2^54-2^56 units.** That is below pkgCM's 62.7934, but it rests entirely on the joint (G1), which was never
    observed: 0 of 202 distinct D, against an expectation of 0.00006.
- So my earlier ">= 2^73.4" was wrong (it multiplied D3 per joint instead of retrying it inside a joint); I withdraw it.
  The honest status is OPEN with a priced next test.

## 4. TEST 2 (SHA3-256 r6): low degree x connector (fixed pair difference carried on the 2-round-affine field)

Question: can the 40 surplus dimensions of W40 (rounds 1-2 affine on every coset) pay the connector's missing degrees of
freedom, so that a FIXED pair difference reaches round 3 on a large sub-field, chi3's conditions become linear field
conditions, and FES enumerates the pairs at about 2^-4..2^-5 units each?  For a coset t + W40 and a pair difference Delta,
delta_r(w) = S_r(t+w) xor S_r(t+Delta+w) is affine in w for r <= 2 and (on the sub-field where delta_2 is constant) for
r = 3.  Script: sha3_ldconn.py (imports research/sha3r6/lowdegree/cube_degree.py: W40 and the organizer round function);
output out_sha3_ldconn.txt, summary by sha3_summary.py.  4 random cosets x 7 difference families, 3 cosets for the
minimum-weight search; sponge self-check against the organizer keccak: True; W40 rank 40.  All numbers COMPUTED.

| stage | difference family | result |
|---|---|---|
| r1 | any source difference (in W40, one source bit, theta2-kernel, random) | delta_1 constant on all of W40: dim 40 (round 1 is affine on the whole 320-bit source) |
| r1 | one bit outside the source lanes (lanes 5-9, 15) | dim 33-38 |
| r2 | Delta in W40 | dim 40 (delta_2 = L_t Delta, constant, checked 16/16), weight 370-509, odd columns 144-165, theta3 output 729-809 |
| r2 | lightest delta_2 FOUND over all Delta in W40 (Lee-Brickell, 3 cosets x 2 runs; an upper bound on the true minimum) | 26-30 odd columns, theta3 output 266-394 bits |
| r2-r6 | those lightest Delta (6 cases), run through the full pipeline | delta_2 weight 28-52 (one bit per odd column), dim 40 at r2, theta3 output 276-394; chi3 rank 39 -> **dim 1**; delta_3 weight 465-567; r4 weight 796-822 of 1600 |
| r2 | one source bit | rank 25-35, dim 5-15; weight 74-92, odd columns 62-78, theta3 output 514-567 |
| r2 | theta2-kernel source differences (identity chi1; the kernel has dim 193, basis words of weight 4+) | basis words: dim 0-23 (median 17.5), odd columns 86-148; random kernel combos: dim 0 |
| r2 | random dense source difference; one bit outside the source | dim 0 |
| r3 | every family with dim > 0 after r2 | the linear chi3 conditions take every remaining dimension: dim 1 for Delta in W40 (rank 39 of 40), 0 for all others |
| r4-r6 | pairs sampled on the surviving sub-field | mean difference weight 798-807 of 1600 (r4, r5), 124.5-132 of 256 (digest); no bias above sampling noise (128 samples) |

Verdict for the pair (DERIVED from the table): dead.  The field cannot carry a fixed pair difference into the theta3 kernel.
Even the lightest round-2 differences found inside W40 (28-52 bits, one per odd column, 266-394 chi3-input bits after theta3)
keep only 1 of 40 dimensions through chi3.  Every Delta outside W40 costs 25-40 of the 40 dimensions at round 2, and the
chi3 conditions then use up whatever is left (0-1 dims).  (The Lee-Brickell weights are the lightest FOUND, so they bound
the minimum from above.  The dimension count, not the weight, is what closes the pair.)
From round 4 on the pair difference is dense and unbiased, so a pair collides with probability about 2^-256, against 2^-128
per candidate-pair for the birthday that LD already prices at 122.98920.  The connector's 33-DF deficit is therefore not paid:
the 40 surplus dimensions are consumed by the difference itself, about 2 per active chi1/chi2 bit and 1 per chi3 condition.
"trail x LD" falls with it (no sub-field survives chi3, so there are no FES-priced pairs to feed a 4-round tail).

## 5. Derived structure of the {m2,m3,m4,m6} local collision (DERIVED; every condition checked on the real G call)

Message differences (modular): dm6 = delta (free), dm2 = -delta (C0 needs a2 equal), dm4 = -D where D = K3's a-output
difference (C3 absorbs X3 with w4, and D3 passes dX3 = dv3 = D), dm3 forced by C1: 2*dm3 = -((S1'-S1) + dv6), S1 = K1's
a1 + b1 (so dm3 exists only when the right side is even; two roots).  All other words equal.
Round 0: K3 = G(h3,h7,IV3,flags; m6,m7) outputs differ in a,c only; K2 = G(h2,h6,IV2,blen; m4,m5) in b,d only;
K1 = G(h1,h5,IV1,t_hi; m2,m3) in a,c only; K0 is a free call (its m1 sets v12 for D1); D0 and D2 see no difference;
D1 = G(v1,v6,v11,v12; m10,m11) outputs differ in a,d only; D3 = G(v3,v4,v9,v14; m14,m15) in a only.
Round 1: C0 absorbs X12 with (m2,m6), C1 absorbs X1 with m3, C3 absorbs X3 with m4, C2 sees nothing, and no round-1
diagonal reads m2, m3, m4 or m6, so all 16 output words agree (a full compression collision, final step free).

Stage conditions (each solved by its own free word; a = value of the call's first a-word):
- K3: (a) compat(D, d1^d1') on m7, i.e. D must be a signed sum over the bits of d1^d1'; (b) (c1+d2)^(c1'+d2) = b1^b1'.
- K2: (a) F2(A2+dm4) = F2(A2) with F2(A) = A + b1(A) (a 32-bit collision of a known function); (b) compat(c1-c1', ror(d1^d1',8)).
- K1: parity, then (a) compat(Dm, d1^d1') and (b) as K3(b).
- D3: (i) ror(v14'^(A+D),16) - ror(v14^A,16) = v9 - v9' over m14 (rotation carry DP, exact); (ii) compat(D, d1^d1') over m15.
  D3(i) depends on K1 only through c1-c1', so different K1 cube elements do NOT give D3 retries.
- D1: (i) (v11 + q) ^ (v11' + (q ^ x)) = v6^v6' over v12 (via K0) and m10; (ii) rotation DP (R = 8) over m11.
- C0: compat(-delta, X12^X12') over X0 (via D0's m9).

2-adic valuation constraints (v = lowest set bit; S(e) = signed sums over the bits of e have valuation lsb(e)):
- K3(b) forces lsb(eps_c) = lsb(ror(eps_c,12)) for eps_c = c1^c1', i.e. m := lsb(eps_c) < 12, bit m+12 set, no bits in
  [12, m+11].  K3(a) then forces v(D) = m and v(delta) > m.  For m >= 4 this contradicts bit m+28 of A^(A+delta), so m <= 3.
  COMPUTED check: all 22 K3 solutions found at the root have v(delta) in {1,2} and v(D) in {0,1}.
- D3(i) and D3(ii) together force K1's valuation m1 = v(D) = m.
- K2(b) forces lsb(eps2) < 8 with bit lsb+8 set (eps2 = d1^d1' of K2), and K2(a) forces v(dm4) = lsb(ror(eps_c2,12)).
No contradiction was found between these; the rates in section 3 are what decide the route.

## 6. Not done / limits
- BLAKE3, the missing number: no true joint (K3 and K2 agreeing on D) was found. D3, D1 and C0 were therefore measured on
  stage-marginal and K2-consistent inputs, not on a joint. D1 and C0 were never reached.
  **Next test (more than this budget):** a targeted K3 solver for D in -D2, run per target D over the about 2^16 XOR patterns
  compat allows. It needs a carry DP with three chains (offsets 0, 16, 28; est. 2^19 ops per (D, pattern), so about
  2^36-2^37 units per instance, GUESS). It decides whether the 1-2 joint values the independence GUESS predicts exist at the
  root (or at flags 1 or 3, which share K2's set). On a joint, run k1gpu (dv6 from the about 450,000 K2 bases), then b3final:
  D3, D1, C0, assembly, and verify_ref.py against the organizer blake3.py. A found pair would be a 2-round BLAKE3 collision
  of two 64-byte messages.
- BLAKE3: only the root instance's K2 set was enumerated. The other instances were measured for K3's rate only.
- BLAKE3: the per-sample cost 2^-4.1 units (about 25 word ops) and the K1 scan cost 2^27.9 units are DERIVED op counts, not
  metered.
- SHA3: 4 cosets x 7 families plus 3 cosets of minimum-weight search. Lee-Brickell gives the lightest word FOUND (an upper
  bound on the true minimum, not a proof). Theta2-kernel words were tested as basis words and random combos only.
- Files deleted after use: d2_root.bin (4.6 GB, all 570.9M K2 records) and d2_root.bin.bm (512 MB bitmap). Regenerate in
  about 16 min with `./b3stats k2enum 0x1F83D9AB 64 d2_root.bin`. The 1,270 distinct values are kept in d2_root_distinct.txt.

## 7. Files (all in this folder)
- BLAKE3: b3lc.h (stage solvers and DPs), b3lc_main.c (self-tests), b3lc_stats.c (stage check, K2 enumeration, rotation-DP
  test), k3gpu.cu (K3 sampler and per-delta scan with K2 bitmap), k1gpu.cu (K1 full scans), mkk1prob.c, mkjoint.c,
  k2check.c, d3test.c, d3val.c, b3final.c, b3pipe.c (full assembly and verification, unused: no joint), verify_ref.py
  (organizer blake3.py check, unused), dbg_k3.c, run_joint.sh, run_k3inst.sh, build_all.sh, k3recs.py.
- BLAKE3 outputs: out_rottest_stage.txt, out_k3gpu_root.txt, k3gpu_root_uniform.txt (22 K3 solutions),
  k3scan_root22.txt (all 7,990 K3 solutions of the 22 deltas), out_k2enum_root.txt, err_k2enum_root.txt,
  d2_root_distinct.txt (the 1,270 K2-solvable dm4), k1prob_marg.txt / k1sol_marg.txt / out_k1gpu_marg.txt (352 problems),
  k1prob_big.txt / k1sol_big.txt / out_k1gpu_big.txt (1,408 problems), out_d3base.txt, out_k3inst.txt,
  k3gpu_inst_*.txt.  d3base.c = D3 baseline rates; d3val.c = valuation check of K1's M.
- SHA3: sha3_ldconn.py, sha3_summary.py, out_sha3_ldconn.txt.

## 8. Tool calls blocked or stopped (stated plainly)
- One foreground `sleep 60` was blocked by the harness ("use Monitor with an until-loop"); I did not retry it and used
  background monitors on my own jobs instead.
- I stopped my own jobs with TaskStop: the first `b3lc stagecheck` (sample counts too large for the 20-minute rule, no
  time cap), and the first `b3stats stage` run (block-buffered output, no progress visible; replaced by a time-capped,
  line-buffered run).  I also stopped several of my own redundant monitor tasks.  No other process was touched; no pkill,
  no kill by name; after each stop I checked that none of my binaries was left running.
- Nothing was refused.
