# BLAKE3 r3 wave1: structure of the 3-round function (message schedule, free words, CV/flags, truncation)
Date 2026-10-13. NEW GROUND. Labels: SEEN (read in a file), COMPUTED (own run today), INFERRED (reasoned, not run).
Tools: own numpy engine (scratchpad st.py, st2.py, tail.py, tail2.py), checked against an independent scalar round function on 50 inputs at r=1,2,3 (match). Shipped rho.py used only as our own code (tracer import, no edits). 1 process, nice 19, no GPU, total run under 1 min.

## 0. Target facts (SEEN, proof.md s1)
f(x) = 3-round root compression of M(x)=0^32||x: m0..m7=0, m8..m15=x0..x7, CV=IV, counter 0, len 64, flags 11. Digest word i = v[i]^v[i+8] (no input feed-forward). Collision compares all 256 bits (the 22-bit compare is only the organizer's n=22 experiment). Counter/flags/length are fixed by the target, not free inputs.

## 1. Message schedule over 3 rounds (COMPUTED)
G index j uses (m[2j], m[2j+1]). Original message words per round:
- r1: col (0,1)(2,3)(4,5)(6,7), diag (8,9)(10,11)(12,13)(14,15).
- r2: col (2,6)(3,10)(7,0)(4,13), diag (1,11)(12,5)(9,14)(15,8).
- r3: col (3,4)(10,12)(13,2)(7,14), diag (6,5)(9,0)(11,15)(8,1).

x words (m8..15) enter: r1 only in the 4 diagonal Gs, each G sees one disjoint pair (x0,x1)(x2,x3)(x4,x5)(x6,x7). r2: x2 (col G1 first add), x5 (col G3 second add), and x3, x4, x1, x6, x7, x0 in the diagonals. r3: col G1 gets x2,x4; G2 x5; G3 x6; diag G5 x1; G6 x3,x7; G7 x0. Gs with no x word at all: r2 col G0 and G2; r3 col G0 and diag G4. Every x word enters in all 3 rounds, so no x word is late or absent for any output word.

Dependency (flip any bit of x_k, min over probed bits): after 1 round each digest word depends on exactly 4 x words (digest w0 on x0,x1,x4,x5; w1 on x2,x3,x6,x7; alternating pattern, the other flip rates are exactly 0). After 2 rounds every digest word depends on every x word with flip rate 1.00, same at 3. Round-1 state: all 16 words depend on x; the diag Gs touch words 0,5,10,15 / 1,6,11,12 / 2,7,8,13 / 3,4,9,14 from pairs (x0,x1)/(x2,x3)/(x4,x5)/(x6,x7). The round-1 column step is all-constant (already folded, the 116-op round).

Verdict: the only partition structure is the r1 four-way split into independent 64-bit pair blocks. It is gone after round 2. The last two rounds give no inversion (the digest folds 512 -> 256 bits).

## 2. Free / neutral words and neutral bits (COMPUTED + INFERRED)
- All 256 x bits are free, there is no neutral word. Single-bit flip probabilities, 256x256 matrix, 4096 samples per input bit, noise sd 0.0078: r1 has 45,281 cells exactly 0 or 1 (the r1 block structure); r2 and r3 have none; max |p-0.5| = 0.0337 (r2), 0.0325 (r3) = 4.2 sd, equal to the expected maximum of 65,536 normal cells (about 4.3 sd). No neutral bit and no biased bit at r3 for single-bit differences.
- Linear: correlation of each of 256 input bits with each of 256 output bits, 2^16 samples: max |c| 0.0168 vs chance maximum 0.0168. Output-bit pairs max 0.0165. Output bit means 0.4941..0.5055. None.
- Symmetries: all 40,320 permutations of the x words (also combined with all 256 per-word complements, 10.3M evaluations) and 31 uniform per-word rotations: 0 digest words equal (chance 0). No symmetric collision.
- Image size / collision rate of truncations (2^23 samples each, ratio of colliding pairs to uniform expectation; 24-bit expectation about 2^21 pairs, sd about 0.07%): low 24 of w0 1.0002; high 24 of w7 0.9989; 12+12 mixed from w3,w4 1.0001; low 24 of the XOR of all 8 words 1.0005. No image deficit. These are 24-bit slices; nothing is said about 256-bit tail events (INFERRED same as H1: unmeasurable).
- INFERRED, nonzero m0..m7 constants (last-block mode) to make folded sums a+b zero in the 4 diag Gs of r1 (each saves at most 1 op): each nonzero constant message word costs 1 add in r2 and 1 in r3 (all of m0..m7 appear in both), so net at least +1 op per word for at most -1 op per site. Not a gain. Zero m0..m7 is optimal; only the CV can be tuned (LEVER_CELLS "last block of a multi-block chunk" 0.0024 to 0.0120 bit).

## 3. CV / flags / counter / multi-block (SEEN + INFERRED)
Fixed in the filed mode. The legal last-block mode (prefix block gives CV h, second block CHUNK_END|ROOT) is already priced in D220/D231 (PH 595 -> 590 with 3 zero sites, 125.0965, needs a ~2^96 prefix search and a ruling on the mode). INFERRED ceiling: a prefix search buys one zero site per 32 bits, about 1 op per site, each op about 0.0024 bit; 3 sites is the affordable limit (2^96). Joux-type multicollisions help iterated hashes needing many collisions, not a single root collision: no generic gain (INFERRED).

## 4. Output truncation / chain-map freedom (COMPUTED negatives)
The chain map may be g = Q o f for any cheap bijection Q (a g-collision gives an f-collision).
a) Merge the two final rotations of digest words 4..7 (ror 7 of the b branch and ror 8 of the d branch) into one rotation of w = tb ^ ror(td,1): not possible, because the rotated d is still needed for c = c + d inside the same G, so one rotation per word stays. COMPUTED: traced version 599 ops vs shipped 595 (+4 masks); output equals ror25(digest) for words 4..7 on 1400 lanes. Gain 0 (-0.0097).
b) Skip the 4 final masks by letting x carry guard-bit garbage: COMPUTED with input bound 2^33..2^36: ops 595, 599, 612, 615 (the tracer inserts masks inside instead). Gain 0.
c) INFERRED: 8 lanes of pitch 32 instead of 7 of 36: lane carries then need a SWAR add (about 7 ops instead of 1, 6 adds per G): per-G cost 30 -> about 66, far worse than the 8/7 lane gain (0.19 bit). Not a gain.
d) INFERRED: restricting x to a 130-bit subspace to fold more constants: rho needs g: S -> S with |S| = 2^256 to keep a full-digest collision; with |S| = 2^130 a g-collision is only a 130-bit truncation match (about 2^126 repeats); the sort-and-match alternative needs memory 2^128 (score +108). Dead.

## 5. Birthday-exponent verdict
No structure found that cuts the exponent below 2^(n/2): the schedule fully diffuses by round 2; no neutral words or bits; no single-bit or linear bias at 65k-cell resolution (max 4.2-4.3 sd); no symmetry; 24-bit slices collide at 1.000 +- 0.001 of random. Consistent with the dig 10-12 NULL on differential lines (SEEN, paths_blake3_r3.md row 8).

## 6. Per-idea table (each technique with its own estimate)
| idea | label | est. gain (bits) | needs |
|---|---|---|---|
| schedule / late words | COMPUTED | 0 (all x words enter every round; zero-message savings already in 595) | none |
| neutral words/bits | COMPUTED | 0 | none |
| word-permutation / rotation symmetry | COMPUTED | 0 | none |
| linear / bias / image-size at 24-bit slices | COMPUTED | 0 | tail-event premise stays H1 |
| nonzero m0..m7 to zero r1 sites | INFERRED | negative (+1 op per word, -1 per site) | last-block mode |
| CV tuning of zero sites (known) | SEEN | +0.012 (3 sites, PH 590) | ~2^96 prefix search, mode ruling |
| merge final rotations | COMPUTED | -0.0097 | dead |
| skip final masks | COMPUTED | 0 | dead |
| 8-lane pitch 32 SWAR | INFERRED | about -0.19 | dead |
| restricted domain with more folding | INFERRED | infeasible under rho; memory 2^128 otherwise | dead |
| multi-block / Joux | INFERRED | 0 for a single root collision | none |

Not tested: 256-bit-scale differentials (unmeasurable), 2-bit or word-pair differential probabilities (dig 10-12 covers 385 families), degree/cube analysis (not collision-relevant).
