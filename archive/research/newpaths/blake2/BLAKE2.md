# BLAKE2.md - what BLAKE2 / BLAKE / BLAKE3 / ChaCha-Salsa cryptanalysis offers a 2-round BLAKE3 collision

Folder: research\newpaths\blake2 (agent "blake2"). Written 2026-10-08. Research only: no yukon, nothing
submitted, no trace. Labels: COMPUTED = measured by a program in this folder; DERIVED = follows by argument
from stated facts or read from the cited source; GUESS = judgement or extrapolation.

Read first and not redone: ..\..\NEW_PATHS.md, ..\..\END_OF_LINE.md, ..\literature\LITERATURE.md (the BLAKE
family table, LX09 template, MITM / Autoguess lineage), ..\fringe\RESULTS.txt (rotational pairs, neutral bits,
symmetry, CV tables, angle 10 multi-block), ..\shape_odd\NOTES.txt, ..\separable\NOTES.txt, ..\variants\METHOD.txt,
Grok's job28 (greedy carry-free trails, never output-zero).

## 0. Bottom line

1. DERIVED. Nothing in the BLAKE2, BLAKE, BLAKE3 or ChaCha/Salsa literature gives a fixed-IV collision at 2
   rounds. Every published collision-type result either has a chosen IV / chaining value / symmetric state
   (free-start, fixed points, rotational, internal-differential "squeeze"), or is a distinguisher / key recovery
   (boomerang, impossible differential, differential-linear, PNB), or is a preimage (HOD-MITM).
2. DERIVED. The board's free half (55/63 bytes, digest words 0,2,5,7 equal for free) IS the transfer of Li-Xu
   2009's free-start trick (an initial-state difference cancelled by message words in the first column step) to
   the one initial-state word BLAKE3 lets two messages differ in: v14, the block length. Section 2 (TEST T3) shows it is
   the ONLY such source for a one-compression root, and that the other candidate (flags 11 vs 12: one-block
   message against a two-chunk parent root - a new path) is dead by structure (DERIVED + COMPUTED on toys).
3. COMPUTED. The standard collision tool of this literature - XOR-linearised characteristics with the output
   fold, first round passed by message modification (Chabaud-Joux; Su et al. 2010; Rumba, AFKMR08; GKNWW14 sec. 6)
   - is dead here: (a) exactly NO probability-one characteristic exists for a 2-round collision or for either
   half, with or without a length difference, at w = 8, 12, 16, 32, not even if all of round 0 or all of round 1
   is exempt (exact GF(2) ranks); (b) the best characteristics found by information-set decoding have round-1
   weight 122-141 at w = 8, 233-248 at w = 12, 357-365 at w = 16 (generic birthday: 4w = 32, 48, 64) and look
   like those of a random linear code. The only sparse structure is the all-ones (complement) class; its best
   member (m3, m10, m14 complemented) is the best linear collision characteristic found: at w = 32 it costs
   2^-527 with round 0 free and 2^-155 even if every round-1 column were also free (ISD: 821 and 263) - all far
   above the generic 128.
4. COMPUTED + DERIVED. Why the literature's trail numbers miss the board: the board's path is value-dependent.
   In the XOR-linear model the K2 local collision exists (dm4 = dm5 = dv14, a 7-dimensional space at every
   width) but NO linear characteristic with differences in m4, m5, v14 only keeps digest half A or E0/E2's
   inputs equal (dimension 0 at w = 8..32, board_lin.txt). The free half comes only from pinning C3 to the
   output pattern (a, c differ; b, d equal), which random inputs hit at 2^-19 at w = 8 and < 2^-22 at w = 12, 16
   (pins_toy.txt). So trail tables (spec 2^-185, GKNWW14 2^-198) say nothing about the board, and XOR-linear
   search cannot find its relatives. The one transferable TOOL is signed-difference search with automatic bit-condition
   deduction (Hao-Wang-Jiao-Gong 2023, used on full 7-round BLAKE3's keyed permutation), aimed at pinned
   round-1 calls - not run here (section 3).

## 1. Published attacks and properties: what each does, and what could transfer

"IV": fixed = real hash, standard IV; chosen = the attacker sets the chaining value / salt / counter / state.
Cost in the paper's units. Transfer = the precise part that could move to a 2-round, single-block, fixed-IV
BLAKE3 collision under the contest cost model (1 unit per 2-round compression, 1/430 per word op, memory free).

| # | Ref | Result | Rounds | IV | Cost | Transfer to us |
|---|---|---|---|---|---|---|
| 1 | [LX09] | collision BLAKE-32: 2 output words held by message modification, birthday on the other 192 bits | 1.5 | fixed | 2^96 | = IDEA 1 template; at 2 rounds holding 4 words costs 4 checks (separable, exact). Dead as a sampler. DERIVED |
| 2 | [LX09] | free-start collision: differences in h0, h2 cancelled by m0, m2 in the first column step | 2.5 | chosen | 2^112 (BLAKE-32) | The mechanism IS the board's 55/63 trick with v14 instead of h. Classified completely in section 3. DERIVED |
| 3 | [AGKMM10] | G and one round invertible; only probability-1 G characteristics are local collisions with MSB differences in (x,a), (y,a,d), (x,y,d); no probability-1 collision characteristic (Props 5, 7); impossible differentials 5-6 rounds; near-collisions 4 rounds | 1-6 | fixed / perm / chosen | - | Prop 5 local collisions checked at 2 rounds with the fold: none survives (TEST C, exact). DERIVED + COMPUTED |
| 4 | [GM09], [SWWD10] | near-collisions by linearisation (difference 88888888 / low weight), message modification in round 1 | 4 | chosen | 2^56 / 2^21 | Method = TEST A; only dense trails, plus the all-ones (complement) class at (w-1) per active addition. COMPUTED dead |
| 5 | [TU10] | near-collision 184/256 by hill climbing | 2 | chosen | 2^26 | near is not a collision; needs IV. No. DERIVED |
| 6 | [DK11] | iterative differentials, symmetries, message modification (rebound-like) | 3 (c.f.) | chosen (GUESS) | 2^60 | Needs state freedom. No. DERIVED (abstract) |
| 7 | [BNR11], [Leu12], [Hao14] | boomerangs on BLAKE-32 / BLAKE2 permutations and compression functions; Leurent shows some published trails impossible | 6-8.5 | perm / chosen | 2^44 .. 2^456 | Distinguishers, not collisions; lesson kept: check value compatibility of any trail on toys. DERIVED |
| 8 | [KLN11] | rebound + local collisions | 10 (perm) | perm | - | inbound = inside-out construction; for us that is the GD problem (separable: no split). DERIVED |
| 9 | [VNP10] | collisions for BLOKE, BRAKE (weakened BLAKE: fixed points without constants / feed-forward) | full | fixed (weakened design) | low | Relies on removed constants/permutation. No. DERIVED |
| 10 | [GKNWW14] sec. 3 | rotational distinguisher; internal differential "squeeze" (4 equal columns stay equal; collisions in 2^{2w} for a free state) | 12 (perm) | perm / symmetric state | 2^511 / 2^128 | Needs IV0..3 rotational or equal; BLAKE3's are not (paper itself: "not applicable to the compression/hash function"). fringe angles 4, 5 and shape_odd (a),(b) measured it dead. DERIVED |
| 11 | [GKNWW14] sec. 4 | fixed points of G repeated in all columns + iterative rotational characteristic -> 208-bit partial collisions | 12 | chosen (IV = fixed point) | 2^64 | Needs the IV to equal a fixed point. BLAKE3's analog "v_i = v_{i+8}" is a preimage of 0. No. DERIVED |
| 12 | [GKNWW14] sec. 5.4 | probability-1 G characteristic (MSB, 0, MSB, MSB^(MSB>>>16)) -> (MSB, 0, 0, 0) | 0.5 | - | 1 | Included in TEST C (all MSB-only behaviour is free in the model): nothing reaches a collision. COMPUTED |
| 13 | [GKNWW14] sec. 6 | trail search in the hash setting, first-round message additions free: BLAKE2b best 2-round 2^-198; "message modification beyond round 1 very hard due to fixed IV" | 2-4.5 | fixed | 2^-198 (2 rounds) | Same conclusion as TEST A, which is more generous (all of round 0 free) and adds the fold. COMPUTED |
| 14 | [B3spec] Table 5 | best trails, BLAKE3 hash setting: 0.5..2 rounds 2^0, 2^-1, 2^-29, 2^-185; compression function (chosen CV) 2 rounds 2^-1, 2.5 rounds 2^-32 | <= 2 | fixed / chosen | - | Not collision trails (any output difference). The 2^-1 at 2 rounds needs CV/counter differences (unreachable, TEST T3). DERIVED |
| 15 | [EFK15] | higher-order differential MITM preimages BLAKE-512 / BLAKE2b; pseudo-preimage BLAKE2s c.f. | 2.75 / 6.75 | fixed / chosen | 2^510.3 / 2^253.8 | Preimages at the generic level; a 2-round collision would need a split, and separable proved none. Dead. DERIVED |
| 16 | [HWJG23] | approximate signed-difference MILP + digraph bit-condition deduction; boomerang on keyed permutations, full 7-round BLAKE3 2^180 | 7 (perm) | keyed perm | 2^180 | The tool transfers (search signed paths with pinned calls, like the board's C3); the attack does not. GUESS: worth one build (section 3) |
| 17 | [HTQ08] | Salsa20 core: 2^32 invariant inputs (core acts as 2x) -> 2^31 collisions; probability-1 differential | 20 | fixed-function | trivial | Needs symmetric inputs and Salsa's add-rotate-xor order; BLAKE3's G + IV give no probability-1 path (TEST C). Dead. COMPUTED |
| 18 | [AFKMR08] | PNB (Salsa20/8, ChaCha7 key recovery); Rumba (XOR of 4 Salsa cores) 3-round collisions 2^79 via the SAME low-weight linear differential in two branches whose outputs XOR-cancel, round 1 by linearisation, later rounds by neutral bits | 3 | fixed | 2^79 | Our fold = XOR of two branches (E0/E2 and E1/E3); the board's Lemma D is this. Linear version measured dead (TEST A); neutral bits dead (END_OF_LINE 4.1, fringe angle 6). COMPUTED |
| 19 | [BLT20], [DGM23] | differential-linear key recovery / distinguishers on ChaCha 6-7 rounds | 6-7 | keyed | 2^99.48 (6 rounds) | Needs one biased bit, a collision needs 256. No. DERIVED |
| 20 | [KN10], [AL16], [BBB22] | rotational and rotational-XOR (RX) differences through additions with constants | - | - | - | fringe measured 2^-9 per G (r=1) at w=32, IV breaks rotation. Dead. DERIVED |
| 21 | [MP13] | SAT search for optimal ARX characteristics (Salsa20) | - | - | - | Tool behind the spec's Table 5. Same purpose as TEST A. DERIVED |

## 2. What was tested (three techniques)

Toy BLAKE3 as in the brief: width w, rotations floor(r*w/32) of (16,12,8,7), IV = low w bits, block length 2w,
flags 11. Programs: lin.py (XOR-linear model; selfcheck against a concrete XOR-linearised compression on 50
random (M, dM, dlen) per width: passed), step1_exact.py, isd.py / batch_isd.py, sparse_full.py, board_lin.py, pins_toy.py, toy_flags.py.

### TEST C - probability-one characteristics (AGKMM10 Prop. 5, GKNWW14 5.4, Salsa20-core invariants). DEAD

Model: every addition replaced by XOR; an addition whose inputs have no difference outside the MSB is passed
with probability 1. Collision = dout_i = dv_i ^ dv_{i+8} = 0, so the fold is inside the linear map. Variables:
dM (16w bits) and, in the "len" setting, the low 7 bits of dv14.

COMPUTED (step1_exact.txt, exact GF(2) ranks): the collision kernel has dimension 8w (+7 with the length); the
subspace of it with no non-MSB difference on the additions of {all | round 1 | round-1 diagonals E | round-1
columns C | round 0} has dimension **0 in every case**, for full collisions and for each half, equal length or
not, at w = 8, 12, 16 and 32. So: no 2-round collision or half-collision characteristic passes even one of those
groups with probability one. DERIVED: the MSB-only local collisions of AGKMM10 cannot be chained into a collision
with BLAKE3's fixed initial state, and the Salsa20-core style "free" invariant has no BLAKE3 analog.

### TEST A - linearised collision characteristics with message modification (Su et al., Rumba, GKNWW14 sec. 6). DEAD

Weight of a characteristic = sum over additions of hw((p|q) & ~MSB) (xdp+ for the XOR output, Lipmaa-Moriai);
a 3-input add a+b+x is scored in its cheapest evaluation order. Objectives: W_r1 = round-1 additions only
(round 0 assumed fully solved by message modification - more generous than GKNWW14, who free only round-0 message
additions), W_E = round-1 diagonals only (round 0 and all round-1 columns assumed pinned - an upper bound on what
any pinning can give), W_all (no modification), W_gk (GKNWW14 convention). Search: Lee-Brickell information-set
decoding (p <= 2) on the code dM -> addition-input differences restricted to the collision kernel, best exact
weight kept (isd.py; isd_w8.jsonl, isd_w12_16.jsonl, isd_w32.jsonl).

COMPUTED, best exact weights found (upper bounds on the true minimum; equal length / with length difference):

| w | iters | W_r1 | W_E (C free too) | W_all | W_gk | generic 4w |
|---:|---:|---|---|---|---|---:|
| 8 | 3000 | 141 / 125 | 30 / 23 | 288 / 276 | 191 / 194 | 32 |
| 8 | 20000 | 134 / 122 | - | - | - | 32 |
| 12 | 1500 | 248 / 233 | 55 / 54 | - | - | 48 |
| 16 | 800 | 365 / 357 | 99 / 89 | - | - | 64 |
| 32 | 2500 (r1), 1500 (E) | 821 / 822 | 277 / 263 | - | - | 128 |

Convergence (best after 10, 100, 1000, last iterations): w = 8 r1 len 149, 135, 131, 122 (20000); w = 32 r1
equal 860, 831, 825, 821. Gilbert-Varshamov distance of a random code of the same size, Hamming proxy
(hw p + hw q): w = 8 about 170, w = 12 about 270, w = 16 about 375, w = 32 about 780; the exact weight of a
dense random characteristic is about 3/4 of the proxy, so the found values are what a random code gives
(DERIVED). At w = 32 Lee-Brickell has not reached that level (821 against roughly 600), so the true minimum
there may be near 600 (GUESS) - still more than four times the generic 128.

Every best ISD characteristic is dense (15-16 message words active, all 16 G calls active); the only sparse
structure is the all-ones class of TEST A2, which is slightly better. W_r1 grows like 15-23 w, so at w = 32 a
linear collision characteristic costs far beyond 2^128 even with round 0 free (GUESS by extrapolation; the
w = 32 ISD bound is in the table). Even the over-generous W_E (every column call free) exceeds 4w from w = 12 on.
Validation on real (carry) arithmetic was not run: nothing below 2^-W = 2^-30 exists to measure at w = 8.

TEST A2 - sparse message differences (every published BLAKE trail uses 1-3 active words; GM09 / DK11 / GKNWW14
use rotation-invariant differences 88888888, 04040404). COMPUTED (sparse_full.py; sparse_full_w8.txt for
|S| <= 5, sparse_full_w32.txt for |S| <= 4): sets S of active message
words whose XOR-linear full-collision kernel is nonzero although the generic dimension is 0: none for |S| <= 2,
1 for |S| = 3, 18 for |S| = 4, 156 for |S| = 5 (w = 8); the same 1 and 18 sets at w = 32. EVERY such kernel
vector has each word difference 0 or all-ones (0xff..f) - the rotation-invariant (complement) class, the
period-1 member of the 88888888 family. Best: dm3 = dm10 = dm14 = all-ones, W_r1 = 119, W_E = 35, W_all = 210
at w = 8 and exactly (w-1)/7 times that at w = 32: **W_r1 = 527, W_E = 155, W_all = 930** (each active
addition costs w-1). This is the best linear collision characteristic found by any method here (ISD at w = 32:
821), and it is still 2^-527 with round 0 free and 2^-155 even if every round-1 column were free. Dead.
(A first exhaustive run over all |S| <= 8, step3_sparse.py, was stopped by me - too slow - and replaced by this.)
Half-collision kernels show the same all-ones excess (e.g. 1376 of 1820 four-word sets for half A at w = 8).

### TEST T3 - initial-state differences absorbed in round 0 (LX09 free-start mechanism). ONE SOURCE ONLY; NEW PATH DEAD

DERIVED. Two different messages hashed to the same root output by one compression each can differ in the
initial state only where the mode puts message-dependent data: v0..v7 = key words (IV; same for both), v8..v11 =
IV0..3, v12, v13 = counter (0 for a root: a one-block root has chunk counter 0, a parent root has counter 0),
v14 = block length (any 0..64 for a one-block root, 64 for a parent), v15 = flags (11 for a one-block root,
12 = PARENT|ROOT for a parent root; 10 for the last block of a multi-block chunk, but that block's CV is not
the IV). Two-block and multi-chunk variants with CV differences are fringe angle 10 (dead); counter differences
need two different tree positions, i.e. a collision between a parent and a chunk compression (2^128). So:

- v14 (length): absorbed in K2 = G(IV2, IV6, IV2, v14; m4, m5). DERIVED: a d-difference can be cancelled in one G
  call only by both message words (x keeps d ^ a1, y keeps a2); with x alone a2 differs and all four outputs
  differ. So m4, m5 must differ, and the permutation sends them to C3.x and E1.y: the 55/63 structure is the
  unique length path in which round 0 collides with only the absorbing words changed (letting K2's output
  differ and cancelling later in D0..D3 needs more message differences, hence more active round-1 calls); the
  other "families" (delta 16, delta 6) are the same structure with other dv14.
  DERIVED (exact, inverting G): a call whose only difference is in x cannot have c2 and d2 both equal, nor b2
  and c2 both equal; its minimal output patterns are (a, c differ) and (b, d differ). Half B can never be free
  (m5 is E1's y, so E1's a2 always differs). Half A is free iff C3's b and d outputs (Y7 -> E2, Y15 -> E0) are
  equal, i.e. exactly the board's pinned pattern. So the board's skeleton is forced; only dv14 and the pin
  constants are choices (which the main line has swept).
- v15 (flags 11 vs 12) - NEW PATH F: one-block 64-byte message M against a two-chunk message whose root has
  message R = CV0 || CV1 (sampled cheaply, preprocessing free); M copies R except m6, m7, which absorb dv15 in
  K3 = G(IV3, IV7, IV3, v15; m6, m7). Round 0 then collides exactly (COMPUTED). But m6 goes to C0.y and m7 to
  C2.x. DERIVED: a call whose only difference is in y has da2 = dy != 0 (mod 2^w) and therefore dd2 != 0, for
  every value - so C0 always sends differences into Y0 (E0, half A) and Y12 (E1, half B). No pin can save either
  half. COMPUTED (toy_flags.txt, 2^19 samples at w = 8, 12, 16): dY0, dY4, dY8, dY12 nonzero in 100.0 % of
  samples, C2's outputs nonzero in 99.5-100 %, E0/E2 inputs all equal in 0 samples and E1/E3 state inputs all
  equal in 0 samples; the control (length path, unpinned) has differences only in Y3, Y7, Y11, Y15 as expected.
  Per-word digest equality rates are uniform (0.4-2.3 x 2^-w, noise at w = 16). pins_toy.txt (2^22 random
  inputs per row, w = 8, 12, 16): a difference in y only (+1 or random) gave all four outputs different in
  every sample - exact, since a2 differs by dy, then d2, c2 = c1 + d2 and b2 = (b1 ^ c2) >>> 7 differ - so no
  choice of constants can protect C0's outputs; a difference in x only reaches the board's pattern
  (a, c differ; b, d equal) in 8 of 2^22 samples at w = 8. Path F would have to pay
  probability on both halves: dead (exponent > 128, GUESS from the board's 100.5 bits for ONE half with fewer
  active calls).

## 3. Answer to "what is worth trying"

- Dead, measured or derived here: probability-one / MSB characteristics; XOR-linear (carry-free) collision
  characteristics with the fold, with or without round-0 message modification or column pinning; the flags
  path; counter paths; rotational, RX, internal-differential, squeeze, fixed-point (need a chosen or symmetric
  IV); boomerang, impossible-differential, differential-linear, PNB (distinguishers or key recovery); HOD-MITM
  (preimage; no split).
- Already transferred: LX09's initial-state cancellation (= the board's path, unique) and Rumba's "same
  difference in two branches that XOR-cancel" (= the board's Lemma D on E1/E3).
- One tool left untested, GUESS worth one build: a signed-difference (Wang-style) search with automatic bit
  conditions [HWJG23], [LLW24], restricted to the unique length structure and asked for something the XOR
  model cannot see: a different E1/E3 cancellation pattern (or Y4 class / sub-class) with a larger counted
  rate. The C3 pattern itself is forced (TEST T3). That is a refinement of the existing path (rate, item 6 of
  END_OF_LINE), not a new path.
- Not tested here, for the record: a validation of the XOR-linear weights against real carries (nothing was
  cheap enough to sample); ISD at w = 32 is not converged (upper bounds only).

## 4. Files

| file | what |
|---|---|
| lin.py | XOR-linear 2-round BLAKE3 model at width w; GF(2) helpers; exact weight |
| step1_exact.py, step1_exact.txt | TEST C (exact ranks, all widths) |
| isd.py, batch_isd.py, isd_w8.jsonl, isd_w12_16.jsonl, isd_w32.jsonl (+ .log) | TEST A (ISD), best characteristics with per-call weights |
| sparse_full.py, sparse_full_w8.txt, sparse_full_w32.txt (+ .log) | TEST A2 (sparse message differences, exact kernels, enumerated weights) |
| step3_sparse.py | first version of A2 over all |S| <= 8 and both halves; stopped (too slow), no output kept |
| board_lin.py, board_lin.txt | the board's skeleton in the XOR-linear model (K2 local collision yes, free half no) |
| pins_toy.py, pins_toy.txt | output-difference patterns of one G call reachable by pinning (x-only, y-only differences) |
| toy_flags.py, toy_flags.txt | TEST T3 (new flags path and the length control on toys) |
| afkmr08.pdf / afkmr08.txt | local copy of AFKMR08 (Rumba section read from it) |
| my_pids.txt | PIDs of the background jobs I started (all mine) |

## 5. References

- [LX09] Li Ji, Xu Liangyu, Attacks on round-reduced BLAKE, ePrint 2009/238. https://eprint.iacr.org/2009/238
- [AGKMM10] Aumasson, Guo, Knellwolf, Matusiewicz, Meier, Differential and invertibility properties of BLAKE, FSE 2010. https://eprint.iacr.org/2010/043
- [GM09] Guo, Matusiewicz, Round-reduced near-collisions of BLAKE-32, WEWoRC 2009. http://www.jguo.org/docs/blake-col.pdf (as listed by eHash)
- [SWWD10] Su, Wu, Wu, Dong, Near-collisions on the reduced-round compression functions of Skein and BLAKE, CANS 2010. https://eprint.iacr.org/2010/355
- [TU10] Turan, Uyan, Practical near-collisions for reduced round Blake, Fugue, Hamsi and JH, 2nd SHA-3 conference 2010. http://csrc.nist.gov/groups/ST/hash/sha-3/Round2/Aug2010/documents/papers/TURAN_Paper_Erdener.pdf
- [DK11] Dunkelman, Khovratovich, Iterative differentials, symmetries, and message modification in BLAKE-256, ECRYPT2 Hash Workshop 2011. https://cris.haifa.ac.il/en/publications/iterative-differentials-symmetries-and-message-modification-in-bl/
- [BNR11] Biryukov, Nikolic, Roy, Boomerang attacks on BLAKE-32, FSE 2011. https://orbilu.uni.lu/handle/10993/17513
- [Leu12] Leurent, Analysis of differential attacks in ARX constructions, ASIACRYPT 2012. https://www.iacr.org/archive/asiacrypt2012/76580221/76580221.pdf
- [KLN11] Khovratovich, Leurent, Naya-Plasencia, Observations on Blake (slides), 2011. https://www.microsoft.com/en-us/research/wp-content/uploads/2011/03/blake-slides.pdf
- [VNP10] Vidali, Nose, Pasalic, Collisions for variants of the BLAKE hash function, Information Processing Letters 110(14-15), 2010, 585-590. https://plus.cobiss.net/cobiss/si/en/bib/1024263252
- [GKNWW14] Guo, Karpman, Nikolic, Wang, Wu, Analysis of BLAKE2, CT-RSA 2014. https://eprint.iacr.org/2013/467 (sections 3-6 read from ..\literature\papers\2013_467.txt)
- [Hao14] Hao, The boomerang attacks on BLAKE and BLAKE2, Inscrypt 2014. https://eprint.iacr.org/2014/1012
- [HWJG23] Hao, Wang, Jiao, Gong, Approximate modeling of signed difference and digraph based bit condition deduction: new boomerang attacks on BLAKE, ePrint 2023/299. https://eprint.iacr.org/2023/299
- [EFK15] Espitau, Fouque, Karpman, Higher-order differential meet-in-the-middle preimage attacks on SHA-1 and BLAKE, CRYPTO 2015. https://espitau.github.io/bin/HOD.pdf
- [B3spec] O'Connor, Aumasson, Neves, Wilcox-O'Hearn, BLAKE3 specification, sec. 4.4, Tables 4-5. https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/blake3.pdf (read from ..\literature\papers\blake3_spec.txt)
- [HTQ08] Hernandez-Castro, Tapiador, Quisquater, On the Salsa20 core function, FSE 2008. https://www.iacr.org/workshops/fse2008/docs/papers/day_3_sess_3/29_Lausanne_FSE08_camera_ready.pdf
- [AFKMR08] Aumasson, Fischer, Khazaei, Meier, Rechberger, New features of Latin dances: analysis of Salsa, ChaCha, and Rumba, FSE 2008. https://eprint.iacr.org/2007/472 , https://www.aumasson.jp/data/papers/AFKMR08.pdf (section 4 read)
- [BLT20] Beierle, Leander, Todo, Improved differential-linear attacks with applications to ARX ciphers, CRYPTO 2020. https://eprint.iacr.org/2020/775
- [DGM23] Dey, Garai, Maitra, Cryptanalysis of reduced round ChaCha - new attack and deeper analysis, ToSC 2023(1). https://eprint.iacr.org/2023/134
- [KN10] Khovratovich, Nikolic, Rotational cryptanalysis of ARX, FSE 2010 (cited via GKNWW14 [21]; GUESS for the exact venue)
- [AL16] Ashur, Liu, Rotational cryptanalysis in the presence of constants, ToSC 2016(1), 57-70. https://tosc.iacr.org/index.php/ToSC/article/view/535
- [BBB22] Barbero, Bazzanella, Bellini, Rotational cryptanalysis on ChaCha stream cipher, Symmetry 14(6), 2022. https://www.mdpi.com/2073-8994/14/6/1087
- [MP13] Mouha, Preneel, Towards finding optimal differential characteristics for ARX: application to Salsa20, ePrint 2013/328. https://eprint.iacr.org/2013/328
- [LLW24] Li, Liu, Wang, New records in collision attacks on SHA-2, EUROCRYPT 2024. https://eprint.iacr.org/2024/349
- eHash BLAKE page (archived lists of BLAKE results). https://ehash.iaik.tugraz.at/wiki/BLAKE.html
