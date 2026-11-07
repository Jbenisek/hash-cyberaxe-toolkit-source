# SHA3-256-r6: are any chi6-input planes below degree 8 on W40? (s3-plane-degrees, 2026-10-10 01:05)

Labels: COMPUTED (run here), DERIVED (arithmetic from computed or cited figures), GUESS.
Field: W40 exactly as `research/sha3r6/lowdegree/cube_degree.py` builds it (imported, `w40.txt`, rank 40 COMPUTED). Native 135-byte
messages: lanes 0-4 and 10-14 = the 320-bit source, lane 16 = 0x86<<56. Nothing here was filed or submitted.

## Verdict: DEAD for our route. Saving = 0 bit (COMPUTED + DERIVED)
- **Every one of the 320 chi6-input planes B[x,z] has degree exactly 8.**
  - The 8-cube sums are nonzero in 49.8-50.3 % of 400,000 random cubes. The lowest count for any plane is 199,144 (COMPUTED).
  - A nonzero 8-cube sum certifies degree >= 8 on that coset, so this is a certificate for every coset where it fired, not only a statistic.
  - The 7-cube sums are nonzero in 49.7-50.3 % of 200,000 random cubes, so no plane has degree <= 6 (COMPUTED).
- **Qualifying z positions: 0 of 64**, both at <= 7 and at <= 6 (COMPUTED). The key cannot be moved to cheaper z positions.
- **No combination of planes helps either.** Across random cosets, the degree-8 parts have GF(2) rank 320 of 320 for row 0 and 175 of 175 for the D19 key cone (COMPUTED).
  - The same holds on each of 5 fixed cosets, at both degree 8 and degree 7.
  - So no XOR of chi6-input planes has degree <= 7: there is no basis-change trick either.
- **No coset is special for these planes.** On 300 random cosets, with 64 cubes per coset, all 96,000 (coset, plane) pairs have degree 8 (certified) (COMPUTED).
  - This includes the 54 cosets where some chi3 inputs are constant (see the round-3 door below).
- **The degree-8 part changes with the coset (COMPUTED).** Take the same 8 directions on 16 cosets: 100 % of the (direction set, plane) pairs give different sums.
- **Ledger effect (DERIVED, `ledger.py`):** 0 planes qualify, so Fv is unchanged and **time_log2 stays 123.18243**.
  - The step formula is D19 section 5, 3L+1 per plane-word per Gray step, with L = min(D, popcount).
  - The ceiling, had planes qualified, is small. It assumes 2^48 candidates per group and the 57.946279567 ops/candidate of D19 section 9:

| drop | per plane | per z (5 planes) | all 175 key-cone planes |
|---|---|---|---|
| 8 -> 7: 3 x 1,099,488,385,737 ops/plane/group | 0.01172 ops/cand = 0.00029 bit | 0.0586 = 0.00146 bit | 2.0507 ops/cand = **0.0520 bit** (123.1304) |
| 8 -> 6 | 0.02344 = 0.00058 bit | 0.1172 = 0.00292 bit | 4.1015 = **0.1059 bit** (123.0765) |

Even a full drop of every plane would have been worth at most 0.05 bit (0.11 bit at degree 6). The FES chain is 16.785 of the 57.946 ops per candidate.

## Per-round table (COMPUTED; span = random independent elements of span W40, fresh random coset per cube)
"zero bits" = bits whose k-cube sums were ALL zero (degree < k). Fractions are per bit, min/max over the bits. Rank = GF(2) rank of the k-cube-sum matrix (span of the top-degree parts). "Per coset" = 300 cosets x 64 cubes.

| stage | bound | k: zero bits / min-max nonzero fraction (cubes) | k+1 (sanity) | rank of degree-k parts: random cosets / one fixed coset | per coset: (coset,bit) pairs below bound |
|---|---|---|---|---|---|
| after R1 (1600) | 1 | k=1: **1140 bits constant on every coset**; 460 at 0.50 | k=2 all zero | 40 (linear part independent of the coset) | - |
| after R2 (1600) | 1 | k=1: **382 bits constant on every coset**; 759 bits at 0.24-0.26 (constant on half the cosets); 459 at 0.50 | k=2 all zero | 956 (linear part depends on the coset) | - |
| chi3 input (1600) | 1 | k=1: 0 / 0.489-0.510 (20k) | k=2 all zero | 956 | **92 of 480,000 constant** (18 distinct bits) |
| after R3 (1600) | 2 | k=2: 0 / 0.363-0.385 (= 3/8, rank-2 forms) (20k) | k=3 all zero | 1600 / **780 = C(40,2)** | **184 of 480,000 affine** (36 distinct bits) |
| chi4 input (1600) | 2 | k=2: 0 / 0.488-0.512 | k=3 all zero | 1600 / 780 | 0 of 480,000 |
| after R4 (1600) | 4 | k=4: 0 / 0.480-0.505; k=3: 0 / 0.481-0.502 | k=5 all zero | 1600 / 1600 | 0 of 480,000 (k=4) |
| chi5 input (1600) | 4 | k=4: 0 / 0.489-0.512; k=3: 0 / 0.488-0.511 | k=5 all zero | 1600 / 1600 | 0 of 480,000 (k=4) |
| after R5 (1600) | 8 | k=8: 0 / 0.497-0.503 (400k); k=7: 0 / 0.496-0.504 (200k) | k=9 all zero | 1600 / 1600 (k=8 and k=7) | 0 of 480,000 (k=8 and k=7) |
| chi6 input, all 1600 | 8 | k=8: 0 / 0.497-0.504; k=7: 0 / 0.496-0.504 | k=9 all zero | 1600 / 1600 | 0 of 480,000 |
| **chi6 input row 0 (320 planes)** | 8 | **k=8: 0 / 0.4979-0.5030 (400k)**; **k=7: 0 / 0.4970-0.5028 (200k)** | k=9 all zero | **320 / 320** (k=8 and k=7) | **0 of 96,000** (k=8 and k=7) |
| D19 key cone (175) | 8 | k=8: 0 / 0.4979-0.5020; k=7: 0 / 0.4974-0.5028 | k=9 all zero | 175 / 175 | 0 |
| digest after R6 (256) | 16 | k=16: 0 / 0.483-0.519 (8k); k=15: 0 / 0.481-0.513 (8k) | k=17 all zero (400) | 256 / 256 | - |

- Monomial check, random k-subsets of the 40 basis vectors (COMPUTED). At k=8 every row-0 plane is nonzero in 0.4978-0.5029 of 400k cubes, and at k=7 in 0.4971-0.5032 of 200k.
  - So the degree-8 and degree-7 monomial coefficients are dense. No sparse-table saving is possible: a zero word over 256 cosets has probability about 2^-256 (DERIVED).
- The digest after R6 has degree exactly 16 on all 256 bits and full rank, so option a (D = 16) has no lever either.
- Options c/c' (degree 4) and d (degree 2) get nothing either: every chi5-input and round-3/4 bit is at its bound.

## The only door seen: round 3 on special cosets (COMPUTED, `analyze3.py`); it closes at round 4
- **18 chi3-input bits can be constant on a whole coset t + W40.** Each one is constant on 3-8 of the 300 random cosets (about 1-2.7 %).
  - 54 of 300 cosets have at least one; the maximum is 6 on one coset.
- Each constant chi3 input makes exactly the 2 chi3 outputs that multiply it affine. Every one of the 184 affine (coset, bit) pairs is explained this way (92 + 92, 0 unexplained).
  - The top bits: chi3 input (x,y,z) = (4,1,1) on 8/300 cosets, (4,4,28), (0,4,2), (4,1,32) and (1,2,41) on 7/300 each.
- **It does not propagate.** Chi4 inputs (11-bit theta sums) are never affine: 0 of 480,000 pairs. No bit after R4 is below degree 4, and no chi6 plane on those 54 cosets is below degree 8.
- On a fixed coset, the 1600 quadratic parts after R3 span all C(40,2) = 780 quadratic forms. That leaves 820 affine combinations per coset.
  - These combinations are coset-specific: two cosets share 40 dimensions, the generic 820 + 820 - 1600. Over 4,000 random cosets they share none (rank 1600).
- Value for our FES route: 0, because the route never computes round 3.
- GUESS: in a route that computes chi3 explicitly (the leader's 53.3-op block), 36 affine outputs out of 1600 are worth at most about 1.2 ops/message (about 0.016 bit).
  - It would also need conditions on t to fix the about 18 conditionally-constant inputs; their total cost is unmeasured.

## Obstruction (DERIVED from the numbers above)
- A chi6-input plane is a theta sum of 11 chi5 outputs. Its degree-8 part is a sum of products of degree-4 chi5-input parts.
- Lowering it needs those products to cancel. The measured rank of the degree-k parts is full at every round from 4 to 6, on random cosets and on fixed cosets alike.
- A cascade that lowers the degree would need roughly 11 x 11 x 11 chi3 outputs to be affine, which is essentially all of round 3. That is the 3-round affine structure already capped at rank 1-2 (`SHA3R6_MAP.md` 3.5/3.7).
- What is actually available: at most 6 constant chi3 inputs per coset (12 affine outputs), none of which reach chi4.

## Method and checks
- `cubes.cu` (GPU, RTX 3090) evaluates every point of each cube t + span(d1..dk). It records the cube's XOR sum at 10 stages: the state after R1-R6 and the chi inputs of R3-R6.
- Self-check (`selfcheck.py`, `out_selfcheck.txt`), COMPUTED:
  - 64 random points x 15 stage comparisons against the ORGANIZER `hash-smash/verifier/keccak.py` (`permutation(rounds=r)`, `sha3_256(rounds=6)`): 0 mismatches;
  - 600 cube-sum stage comparisons against `cube_degree.cube`: 0 mismatches.
- Runs: `runs.sh`, `runs2.sh` (5 cosets x 2400 cubes, per-coset rank) and `runs3.sh`. Total GPU time is under 1 minute; every run is seeded and deterministic.
- Analysis: `analyze.py` -> `out_analysis.txt`, `analysis.json`; `analyze2.py` -> `out_analysis2.txt`; `analyze3.py` -> `out_analysis3.txt`; `ledger.py` -> `out_ledger.txt`.
- `runs/*.vec.bin` take about 0.5 GB. They can be deleted and regenerated with the run scripts in about 1 minute.

## Not done / limits
- The claim covers random cosets: certificates on about 400k cosets per plane, plus 300 fixed cosets. It is not a proof for all 2^280 cosets.
  - A coset family conditioned to lower the degree would have to beat a per-(coset, plane) rate below about 3e-5 (0 of 96,000). It would also gain at most 0.05 bit.
- The cost of the conditions that fix the 18 conditionally-constant chi3 inputs was not computed.
- The leader-route price of the round-3 door is a GUESS.
