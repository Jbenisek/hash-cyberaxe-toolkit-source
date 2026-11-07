# SHA3-256 r6, grid cell "SHA3 field x idiff" (marked impossible): scout result, 2026-10-10 01:12

Labels: COMPUTED (run here, outputs in this folder), DERIVED (arithmetic from those or from cited figures), GUESS.
Our own team research. Nothing filed or submitted.

## Verdict: dead. The stated reason for the mark is wrong, but the cell stays closed.
- The mark said "impossible because W40 is not period-closed". W40 itself is not period-closed (COMPUTED, section 2), but other
  period-closed fields exist. A symmetric (z-periodic) 2-round-affine field has dimension **21 at p = 32**, 11 at p = 16 and
  4 at p = 8. The 1-round-affine family has dimension 5p (160 / 80 / 40). So the right mark is "dead", not "impossible".
- What closes it (COMPUTED): on these fields the internal difference is never low degree. On the 1-round-affine family,
  deg delta_r = d_r - 1 at every round, so **31 at round 6** (GPU). On the 2-round-affine family, deg delta_r = d_r, so
  **16 at round 6**: the one degree that the symmetric start buys is spent at round 2. Fixing delta_2 with 22 linear
  conditions gives back that one degree (**15 at round 6**, on a 16-dimensional field). delta cannot be held constant
  through round 3 on any field of dimension above 0: the rank of delta_3 is the full field dimension.
- No bit of the round-6 digest internal difference is biased (largest P[0] is 0.52-0.53, which is sampling noise).
  So a symmetric digest costs 2^-(256-4p). Even at our FES price (57.95 ops per candidate), the birthday on symmetric digests
  costs **>= 2^187.2 at p = 32** (2^219.2 at p = 16, 2^235.2 at p = 8), against the board's 124.04565 (DERIVED, section 6).

## 1. Setup and self-checks (COMPUTED; `symlib.py`, `fields.py`, `out_fields.txt`)
- The embedding follows `lowdegree/cube_degree.py`: the 320-bit source is placed in lanes 0-4 and again in 10-14, lane 16 is a
  constant, and the 135-byte message has byte 135 = 0x86, the organizer's own padding byte.
- For a fully p-periodic input, lane 16 is set to the periodic copy of 0x86: 0x8686868686868686 (p = 8),
  0x8600860086008600 (p = 16), 0x8600000086000000 (p = 32). Bytes 128-134 are ordinary message bytes.
- The sponge matches `hash-smash/verifier/keccak.py` sha3_256(rounds=6) for the native and all three periodic lane-16
  values. Round 0 is affine on all of U320 for every variant: 0 nonzero second differences in 400 random triples.
- The per-row chi1 test (a chi product f*g is affine iff f = 0, g = 0 or f = g on the subspace) reproduces W40:
  0 of 1590 nontrivial pairs fail.
- p = 1, 2, 4 are **impossible for a symmetric input** (DERIVED). The last pad byte (0x86, or 0x80 for shorter messages) is not
  4-periodic, so it breaks periodicity for every p <= 4 and every message length.
  - p = 8 needs L = 135; p = 16 allows L in {134, 135}; p = 32 allows L in {132, ..., 135}.
    For example, L = 132 with bytes 128-131 = 06 00 00 80 gives the 32-periodic lane 16 = 0x8000000680000006.
  - Everything here uses L = 135, the team's embedding. The other lengths only change the lane-16 constant.
  - A second block does not help: the capacity is no longer symmetric.

## 2. Period-closed fields: dimension per period (COMPUTED; greedy minimum hitting subspace, `fields.py`, 45 s per row)
The search finds a smallest dual subspace Q that meets {f, g, f+g} for every chi1 pair, then sets V = Q-perp.
Calibration: on the full native U320 the same greedy finds **45** (re-run: 46), against W40's 40, so its numbers are good
lower bounds (see section 7).

| p | symmetric input possible | dim U_p (1-round-affine) | best 2-round-affine dim, periodic lane 16 | same, native lane 16 (input delta nonzero) |
|---|---|---|---|---|
| 1 | no | 5 | n/a | 1 |
| 2 | no | 10 | n/a | 1 |
| 4 | no | 20 | n/a | 1 |
| 8 | yes | 40 | **4** | 3 |
| 16 | yes | 80 | **11** | 10 |
| 32 | yes | 160 | **21** | 24 |

- W40 against rotation (COMPUTED): dim(W40 cap Sym_p) = 0 for every p.
- dim(W40 cap rot_p W40) = 0 / 1 / 0 / 4 / 3 / 0 for p = 1 / 2 / 4 / 8 / 16 / 32.
- The largest rot_p-invariant subspace of W40 is 0 for every p.
- With the periodic lane 16 the chi1 forms are exactly p-periodic (COMPUTED), so the problem is the Keccak-f[25p] analogue.
  With the native lane 16 they are not.

## 3. Degree of the internal difference per round (COMPUTED; cube sums; `idiff_degree.py`, `gpu_cube.py`, `kernel_field.py`)
Definitions:
- delta_r = S_r xor rot_p(S_r), with the full 1600-bit state after rounds 1-5 and the 256-bit digest after round 6.
- 32 cubes per dimension (16 on basis subsets, 16 on random span elements), each on a random p-periodic coset.
- "deg = k" means the sums are nonzero in all cubes at dimension k and zero in all cubes at k+1. ">= k" means the field is too
  small to test further.

| space (dim) | quantity | r1 | r2 | r3 | r4 | r5 | r6 |
|---|---|---|---|---|---|---|---|
| U32 (160), U16 (80), U8 (40): 1-round-affine, symmetric | state S_r | 1 | 2 | 4 | 8 | 16 | 32 (GPU) |
| same | **delta_r** | 0 | 1 | 3 | 7 | 15 | **31** (GPU) |
| V32 (21): 2-round-affine, symmetric | state | 1 | 1 | 2 | 4 | 8 | 16 |
| same | **delta_r** | 0 | 1 | 2 | 4 | 8 | **16** |
| V16 (11) | delta_r | 0 | 1 | 2 | 4 | 8 | >= 11 |
| V8 (4) | delta_r | 0 | 1 | 2 | >= 4 | >= 4 | >= 4 |
| V'32 (16): 2-round-affine inside K2 (delta_2 constant) | state | 1 | 1 | 2 | 4 | 8 | 16 |
| same | **delta_r** | 0 | 0 | 1 | 3 | 7 | **15** |
| W40 control (40), random non-symmetric cosets, p = 32 | delta_r | 1 | 1 | 2 | 4 | 8 | 16 |

- GPU kernel `cube6.cu`: 13 of 13 cube sums equal to numpy, including dims 21-22, which exercise the per-thread Gray loop.
- On U32, 8 cubes per dimension: digest sums are nonzero at 30, 31 and 32 and zero at 33; delta sums are nonzero at 30 and 31
  and zero at 32.
- On U16 and U8, 4 cubes per dimension: the same pattern.
- Rule (DERIVED): delta_r = D_{delta_{r-1}} R(S_{r-1}), so deg delta_r <= deg S_{r-1} + deg delta_{r-1}, starting from
  deg delta_1 = 0.
- If delta is constant through round R, then deg delta_6 <= d_6 - d_R. The table matches this exactly: a gain of 1 degree on
  U_p, 0 on V_p and 1 on V'.
- The 2-round-affine field loses the gain because F_2's linear part on V depends on RC0, through chi1's c*l terms.

## 4. How far delta can be held deterministic by linear conditions (COMPUTED; `idiff_chain.py`, `out_chain.txt`, 4 base points each)

| space | r2: conditions -> dim left | r3 | delta_2 weight / column-parity weight | delta_3 weight / column parity |
|---|---|---|---|---|
| U32 | 22 -> 138 | delta_3 not affine (64/64 second differences nonzero), chain stops | 42-56 / 38-52 | 568-630 / 148-168 |
| U16 | 22 -> 58 | not affine | 46-52 / 38-46 | 546-594 / 154-174 |
| U8 | 20 -> 20 | not affine | 42-48 / 36-42 | 500-556 / 148-164 |
| V32 | 11 -> 10 | 10 -> **0** | 42-50 / 38-46 | 514-586 / 134-172 |
| V16 | 8 -> 3 | 3 -> **0** | 46-54 / 40-50 | 552-588 / 152-170 |
| V8 | 4 -> **0** | (none left) | 46-48 / 40-44 | 516-564 / 146-158 |
| V'32 (`kernel_field.py`) | 0 (built inside K2) | delta_3 affine, rank **16 of 16** -> 0 | (constant) | (n/a) |

- Weights are on the 1600-bit state; for p = 32 each bit is counted twice.
- delta_2 is never in the CP kernel (column-parity weight 36-52), so theta3 spreads it.
- Holding delta through round 3 costs the whole field every time.

## 5. Door check at rounds 3-6: is any internal-difference bit biased? (COMPUTED; 4096 random points per set, `out_chain.txt`)
- **r3:** biased but not fixed. On U32 there are 322 bits constant 0, 78 constant 1 and 416 biased bits (P[0] >= 0.6),
  with max P[0] = 0.77. U16 and U8 are similar.
- **r4:** random. No constant bit; max P[0] is 0.53, the noise level (sigma 0.0078, so the expected max over 1600 bits is
  about 0.527); mean weight is 800.
  - One exception: on U8's 20-dim chain coset, 13 bits have P[0] >= 0.6 (max 0.638).
- **r5:** random everywhere (max P[0] 0.52-0.53).
- **r6:** digest delta weight 128.0 = random; max P[0] 0.517-0.532 on every field.
  - The V8 (16 points) and V16 (2048 points) "start field" rows show sampling artefacts of tiny fields, not bias.
- So a door that is half open at round 3 shuts at round 4. Nothing survives to the digest.

## 6. Could a collision search use symmetric digests? (DERIVED)
- A p-periodic digest leaves 4p free bits and imposes 256 - 4p conditions (128 / 192 / 224).
- A birthday among symmetric digests needs about 2^(2p) of them (factor 0.994 for success 0.39).
- With no bias (section 5), Pr[delta_6|digest = 0] = 2^-(256-4p), so 2^(256-2p) candidates.
- At the FES price of 57.946 ops/candidate (D19 section 9, 2^-4.81 units): time >= **2^187.2 (p=32)**, 2^219.2 (p=16),
  2^235.2 (p=8). The board is at 124.04565.
- Break-even needs a 6-round internal-differential probability of at least **2^-64.9** at p = 32 (2^-96.9, 2^-112.9).
  That beats random by 63 / 95 / 111 bits.
- From the measured delta_3 (column parity 134-174, about 300 active rows after theta4), a trail through chi4 alone costs far
  more than 64 bits (GUESS: >= 2 bits per active row).
- SHA3R6_MAP 3.1 already puts our best 6-round internal-differential line at 2^172.
- Low degree cannot change the 2^-(256-4p) count. It only enters the FES step (3D+1 ops per plane): D = 15 instead of 16 is
  under 0.1 bit.
- Pairs (x, rot_p x) of non-symmetric messages give no birthday at all (256 conditions per message).
- Rotation-invariant but non-symmetric subspaces put a nonzero, linearly varying difference at the input, which gives
  delta the full degree. The W40 control row shows this.

## 7. Side finding, outside this cell (COMPUTED; `native_bigger.py`, `native_bigger_field.json`)
- The same greedy found a **46-dimensional 2-round-affine field** in the native U320 (W40 = 40). It shares only 3 dimensions
  with W40.
- Checks:
  - per-row test: 0 of 1590 pairs fail;
  - round-2 second differences: 0 on 256 random cosets;
  - cube sums: dim 2 after round 2 = 0; dim 3 after round 3 = 0; dim 16 after round 6 nonzero 8/8; dim 17 = 0 (8/8).
- Effect on the filed-route ledger (DERIVED from D19 section 9): the setup term is 0.37% of N_v, so a bigger n is worth at most
  about 0.005 bit. Pass it on only if some route needs more inner dimensions.

## Not done / limits
- The field dimensions are greedy lower bounds, not proven maxima. They are calibrated by 45-46 found against W40's 40.
- V16 and V8 are smaller than their round-6 degree, so their r6 degree is only bounded below.
- No trail search for rounds 3-6 was run. Section 6 needs one with probability >= 2^-64.9, and sections 4-5 make it hopeless.
- The p <= 4 rows use the native lane 16, because no symmetric input exists there.
- One CPU process at a time. GPU used for about 1 minute (RTX 3090, WSL nvcc).

## Files (all in this folder)
- Code: `symlib.py`; `fields.py` -> `out_fields.txt`, `fields_out.json` (bases).
- Degree tests: `idiff_degree.py` -> `out_degree.txt`; `cube6.cu`, `run_gpu.sh`, `gpu_cube.py` -> `out_gpu_verify.txt`,
  `out_gpu_U32.txt`, `out_gpu_U16_U8.txt`.
- Chain and kernel field: `idiff_chain.py` -> `out_chain.txt`; `kernel_field.py` -> `out_kernel_field_p32.txt`,
  `kernel_field_p32.json`.
- Side finding: `native_bigger.py` -> `out_native_bigger.txt`, `native_bigger_field.json`.
