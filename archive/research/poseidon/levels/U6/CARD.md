# CARD U6 - the constants table (192 round constants, 9 MDS entries, Cauchy parameters)

Learner U6, 2026-10-12. Folder `./research/poseidon/levels/U6`. Learning only: no attack scores. Labels: OBSERVED (command given) / PROVED / DERIVED / GUESS. Every script is in this folder, every output saved as `*_out.txt`; run with `python <script>` there (needs `sympy` for LLL; `common.py` imports `poseidon_ref.py` as data).

## 0. What this level is

The "constants table" is not a round; it is the object every round reads: 64 rows x 3 lanes of F_p elements (`RC[r][l]`) plus the MDS (Cauchy) matrix. The target uses rows R0..R5, R60..R63 (10 rows, 30 values), in the form "add original round r's constants" and never regenerates them for the reduced r.

- reads: nothing (pure data, pinned JSON, sha256 `b19d4e50...acd5`). writes: constants into the C step of each round.
- conditions: none, but they decide which fixed translations the S-boxes see; only 2^65 + c0,2 (via K = (2^65+c0,2)^5) plus the carried form of the others matter structurally (atlas X2, X5, X11).
- freedom: none (fixed). What moves when it changes: translations only; no linear/degree structure of the cipher depends on them.

## 1. Re-derivation by Grain-LFSR (question 1)

Script `grain.py`, `exp1b.py`, `mds_search.py`, `mds2.py` -> `exp1b_out.txt`.

- **OBSERVED** All **192/192** constants reproduce exactly from the halo2/Poseidon reference generator: 80-bit Grain state = field(2 bits)=1, sbox(4)=0 (x^alpha), n(12)=255, t(12)=3, R_F(10)=8, R_P(10)=56, then 30 ones; discard the first 160 output bits; LFSR feedback taps at state positions 0,13,23,38,51,62; output bit pairs (b1,b2): emit b2 if b1=1 else drop both; a field element = 255 emitted bits read **big-endian**, **rejected if >= p** (rejection sampling), drawn in order round 0 lane 0,1,2, round 1 lane 0,1,2, ... `python grain.py`.
- **OBSERVED** Wrong readings all fail: little-endian bit order gives 0/192; changing warm-up to 159 or 161 bits, t=2, R_F=6, sbox=1, field=0, n=254 each gives a different first constant (`exp1b.py`). Regenerating with R_P = 1, 2, 55 or 57 also gives different constants: the reduced target uses the **R_P = 56 seed** constants (pinned JSON), as the atlas assumed. PROVED consequence: constants for r=1,2 are not "the first constants of a shorter Poseidon".
- **OBSERVED** 212 rejected draws were skipped in total (expect ~192 with p/2^255 ~ 1/2 acceptance: unremarkable). Per-round rejection counts R0..R63: 7,1,2,5,2,0,3,5,1,3,8,5,9,2,0,1,3,12,9,... (`exp1b_out.txt`); in used rounds R0:7 R1:1 R2:2 R3:5 R4:2 R5:0 R60:3 R61:3 R62:3 R63:2 (28 total). 411,658 LFSR steps for the 192 constants.
- **OBSERVED, boring but decisive** The Cauchy parameters come from the same stream right after the 192 constants but are drawn **without rejection**: 255 bits, big-endian, then **reduced mod p**. Six draws x0,x1,x2,y0,y1,y2; three of them (x0, x1, y1) were >= p and got reduced. With rejection sampling for the MDS draws the MDS does not match (0/9); first trial found it by noticing one difference y2-y0 of M^-1 structure sat in the stream. M_ij = 1/(x_i + y_j) then matches **9/9** (`mds2.py`). Parameters:
  - x0 = `0x4ed363e2dba5e0c33ea93e01a687ca41033a36de858e8f6bcbfbcf79f56aab8` (raw `0x44ed363e...aab9`, reduced)
  - x1 = `0x82d2c638520fa4f40e7126ac7c40d3d50149148671252f528070717d96cf75` (raw `0x4082d2c6...cf76`, reduced)
  - x2 = `0x1d5e8f3cea81955dbc3f49ca7869e0f5b9912fa1b95820287f2749e41352fd`
  - y0 = `0x1f91faac992dd42021f16d20e960a18a380e5f61f1eaa9fa880e11ee465f2d6`
  - y1 = `0x13e83d61e6d9aca3db67c4da8570e1799ca82b1ba5143d0eda542ec144e466bb` (raw `0x53e83d61...66bc`, reduced)
  - y2 = `0xa8555c849ada2780f4e8fd99bd15d06f236bd77d53d8fb80c0fc5b33c18357d`
  Distinct, no x_i+y_j = 0. (The atlas's x=(0,..),y=.. was the shifted gauge; same matrix.)
- DERIVED: the x_i are 251-254 bit, so the "Cauchy structure" gives no small parameters; the reduction of x0,x1,y1 mod p means raw draws near 2^254..2^255 were folded - harmless.

## 2. Lattice search for small-integer relations (question 2)

Method: for numbers v_1..v_k find small integer a with sum a_i v_i = 0 mod p, via LLL on rows (e_i | W v_i), (0 | W p), W=2^40, sympy `DomainMatrix.lll`. Scripts `exp2.py`, `exp2b.py`, `exp2c.py`, `planted_power.py`, `planted192.py`.

- **Tool validation (OBSERVED, `planted_power_out.txt`)**: a planted 3-term relation (5,-7,2,-1) is recovered as a basis vector for k <= 65 values and **missed for k >= 97**. So the single k=192 reduction is *blind* (it reports norm 2^5.6, ratio 5.9 above the Gaussian heuristic and cannot see planted small relations). Do not read "all192: nothing" as evidence. The valid, covering nulls are below.
- **OBSERVED null, valid**: calibration on random elements: shortest vector sits at 1.05-1.3 x Gaussian heuristic for k=6..40 (`exp2_out.txt`).
- **OBSERVED null**: the 10 used rounds, 30 values: norm 2^8.98 vs heuristic 2^8.87; +1, +2^65: 2^8.71 vs 2^8.39; + 9 MDS entries (k=41): 2^7.10 vs 2^6.83. MDS alone k=9: 2^27.99 vs 2^27.76. Per round (lanes + 1): 2^61.9..2^63.3 (heuristic 2^62.45). Lane columns over the 10 used rounds (+1): 2^22.8-2^23.3 vs 2^22.8. R0 lanes + 2^65 + 1: 2^49.95 vs 2^49.91. All generic.
- **OBSERVED null, full coverage (`exp2c_out.txt`)**: the 192 constants cut into 16 blocks of 4 rounds (12 values); every 3-block union + the number 1 (560 LLL runs, k=37) and every 4-block union + 1 (1820 runs, k=49). Shortest relations seen 2^7.39 (floor 2^7.42) and 2^6.05 (floor 2^5.94); none below norm 30. Since detection works up to k=65, this **excludes any integer relation of norm < ~30 (e.g. up to 4 constants with coefficients of size ~10, or any constant against 1) among any subset of at most 36/48 of the constants lying in <= 3/4 blocks** - which includes every 3-term and 4-term relation among all 192. Relations spread over more blocks, or with large coefficients, are not excluded. Pairs: the 2D version (c_a = (n/m) c_b) over all 36,672 ordered lane pairs: shortest (n,m) 2^118.6 at lane indices (115,129) [= R38 lane 1 vs R43 lane 0], median 2^126.5 (expected minimum over ~18k pairs ~2^120.4): **no small rational ratio**.

## 3. Statistics of the table (question 3)

`exp3.py` -> `exp3_out.txt`.

- **OBSERVED** top byte of the 32-byte value is always in [0x00,0x3f]; no constant is >= 2^254 (p - 2^254 = 2^125.1, chance 2^-128.9 each). Chi-square against uniform on [0,0x40): 64 bins (3 expected each) chi2 = 72.67, df 63, p = 0.190; 16 bins p = 0.382; 8 bins [24,20,33,24,28,21,26,16] p = 0.340; 4 bins p = 0.425; 2 bins p = 0.470. Uniform.
- **OBSERVED** bit lengths: 243:1, 247:1, 248:1, 249:1, 250:12, 251:8, 252:20, 253:57, 254:91 (halving law expected 96,48,24,12,6,3,...): chi-square p = 0.114 (the 250 bin has 12 vs 6 expected - the one mild bump; unremarkable for 8 bins). Shortest is 243 bits (smallest signed value 2^242.55).
- **OBSERVED** Hamming weight mean 127.23 (se 0.58, expected 127); low byte 8-bin p = 0.253; 94 odd of 192.
- Used rows only (30 values) top byte 8 bins: [3,3,5,4,4,8,2,1] - too few values for a test; no claim.

## 4. Relations among the effective (carried) constants for r=1 and r=2 (question 4)

Normal form (atlas X5): lanes 1,2 constants of a partial round move into the next round. `exp3.py` section 4.
- r=1: effective set X=2^65+c0,2; R1..R3 (9); c4,0; R60eff = c60 + M(0,c4,1,c4,2) (3 values, **reproduces the atlas values** `0x2b65...6811`, `0xa57e...8f9`, `0x9659...0161`); R61..R63 (9) = 23 values.
- r=2: same but R5eff = c5 + M(0,c4,1,c4,2) = (`0x39dce27c...37ee`, `0x11e554ad...20f1`, `0xc3d82f13...7c6`), then R60eff = c60 + M(0, R5eff lanes 1,2) = (`0x316d25f0...4d0e`, `0x2c284cc1...4c83`, `0x36c5e753...6831`); 24 values.
- **OBSERVED null**: r=1 set k=23: 2^11.46 vs 2^11.26; with 1 + MDS (k=33): 2^8.37 vs 2^8.17. r=2 set k=24: 2^10.99 vs 2^10.83; +1+MDS (k=34): 2^8.13 vs 2^7.97. Carried vectors and raw R4/R5 constants (k=13): 2^19.40 vs 2^19.34. All generic. Tool check: a planted relation in the effective set is found at norm 2^2.45; the definitional relation R60eff = R60 + carried is found at once (control).
- Bit lengths of effective constants: r=1 R60eff 254/252/252; r=2 R5eff 254/253/252, R60eff 254/254/254. Legendre symbols: r=1 R60eff (-,-,-); r=2 R5eff (+,-,-), R60eff (-,+,-). Nothing structural.

## 5. Special properties of 2^65 + c0,2, and Legendre symbols (question 5)

- **OBSERVED** X = 2^65 + c0,2 = `0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5f0939d92753cc5dc8` (253 bits), K = X^5 = `0x1bb8b655...108c`. Note the atlas R0 card prints c0,2 as `...766c5d0939d...` and X as `...766c5f0939...`; these are different by exactly 2^65 (consistent).
- **OBSERVED, odd but probably chance**: X **as an integer is divisible by 2, 3 and 5** (X mod 2,3,5 = 0; trailing zero bits 3; c0,2 also has 3 trailing zero bits, since 2^65 is divisible by 8). Chance about 1/120 for 8|X and 15|X together; no mathematical reason seen (GUESS: coincidence; as a field element this is a statement about the integer representative only, irrelevant for the S-box). The other small residues: mod 7:2, 11:5, 13:7, 17:11, ...
- **OBSERVED** distance from the fixed points of x -> x^5 ({0,1,-1,i,-i}) and from 2^64, 2^65, 2^254, p/2, p/3: all 2^246 .. 2^253 (far; X is not near a fixed point of S or a small element). X is a quadratic **residue**; so is K (5 is odd). X is not a cube, not a 4th power, not a 463rd power.
- **OBSERVED** order structure: kill the unfactored 212-bit part by raising to C; the remaining order of X (and of K, same since gcd(5,.)=1 on these primes) is 2^31 * 3 * 463. Under x -> x^5, X does not return to itself within 3000 steps (as expected: ord(5) mod 2^31 alone is 2^29). Over the 192 constants the 2-part of the order shows 2^32:102, 2^31:45, 2^30:23, 2^29:12, 2^28:6, 2^27:3, 2^26:1 (halving law 96,48,24,12,6,3,...: matches).
- **OBSERVED** Legendre symbols: 90 of 192 constants are residues (two-sided binomial p ~ 0.43); by lane over 64 rounds QR counts 28, 34, 28; runs 92 (expect 96 +- 7). Cubes among constants: 72 of 192 (expect 64); 4th powers 45 (expect 48); one 463rd power (expect 0.41). Used rounds' lane patterns (+QR, -NR): R0 +++, R1 --+, R2 ---, R3 ++-, R4 ---, R5 --+, R60 ++-, R61 -+-, R62 --+, R63 -+-. MDS entries (row-major): -,-,+ / -,+,+ / +,-,+; det is a non-residue (atlas G3 said M_0,0, M_0,1 non-residues, M_0,2 residue: consistent). All look random.

## 6. All-pairs relations between rounds' constant vectors (question 6)

`exp3.py` section 6. Constant vector of round r is c_r in F^3.
- **OBSERVED null**: c_s = M^k c_r exactly for **all 64*63 ordered pairs and k = -8..8**: 0 hits of 68,544; collinearity (c_s = lambda M^k c_r, any scalar lambda, k=0 means plain scalar relation): 0 hits of 68,544; c_s in the plane spanned by (c_r, M c_r), (c_r, M^-1 c_r), (M c_r, M^2 c_r): 0 hits of 12,096; det[c_a,c_b,c_c] = 0 (three constant vectors coplanar through the origin): 0 of 41,664 triples. (M^-1 is MDS as well; powers up to 8 only.)
- **Calibration on toy copies (OBSERVED, `exp1b_out.txt`)**: the same Grain generator over q = 257, 12289, 65537, 1000003, 7340033 (all with gcd(5,q-1)=1; 2-adicity 8, 12, 16, 1, 20), same detectors. Accidental hits scale as predicted: coplanar triples 166 of 41,664 at q=257 (expected ~162), 3 at q=12289 (expected 3.4), 0 at larger q; collinear (pair,k) hits 2 at q=257 (expected ~1), 0 elsewhere; exact c_s = M^k c_r never. So at p (255 bits) the expected number of accidental hits is ~10^-70; zero hits is the null, and a hit would have been structural.
- For the ratio test of any two single lane constants: smallest rational (n/m) vector 2^118.6 (see section 2).

## 7. Boring facts to keep

- Rows R4, R5 hold 253/253/254 and 254/254/252-bit constants; R62 lane 0 is the shortest used constant (250 bits, `0x2e0e121b...d15`); R1 lane 1 is 251 bits.
- No constant is 0, +-1, +-i, a small integer, or equal to another or its negative (atlas G4, re-checked implicitly by the 2-term search).
- The Grain stream is **deterministic and shared**: all 192 constants and the six Cauchy parameters are one stream, so "special" values in the stream can't be chosen independently; if any hidden structure existed it would live in the LFSR linear structure (80-bit state, period ~2^80), not in the field arithmetic. GUESS (not tested): the constants are linear over GF(2) in the 80-bit seed; this is the only algebraic structure of the table and is invisible over F_p.

## 8. Most surprising / useful observations

1. The 192 constants reproduce exactly from Grain (R_F=8, R_P=56, 255 bits, big-endian, rejection >= p) and the Cauchy parameters are drawn from the continuing stream **without rejection, reduced mod p** (3 of 6 draws were >= p). Regenerating with R_P = 1 or 2 gives entirely different numbers, so the reduced target's constants are a slice of the R_P=56 table, not "short Poseidon" constants.
2. Every algebraic search is null, and **a single wide LLL is blind**: a planted 3-term relation is invisible for k >= 97. With block-covering (all 3- and 4-block unions of 12-value blocks) the nulls are real for any relation of at most 4 constants and norm < 30; wide-spread or large-coefficient relations remain untested.
3. Round-to-round: no c_s = M^k c_r, no scalar multiples, no coplanar triple in 68,544 + 12,096 + 41,664 tests; toy primes q = 257, 12289 show the same detectors do fire at the expected accidental rate, so the nulls are calibrated.
4. Statistics are uniform (top byte chi-square p 0.19-0.47, bit lengths p 0.11, 90/192 QR), so no bias to exploit in the table itself.
5. The one oddity is X = 2^65 + c0,2 being divisible by 2*3*5 as an integer (8 | X) - GUESS chance 1/120; X is a QR but not a cube/4th power/463-power, order smooth part 2^31*3*463, far from all fixed points of the S-box.

## 9. Questions raised

- Is the 2-adic order spectrum of the effective constants (2^32 | 102 of 192 elements) relevant to the 2-adic structure of x -> x^5 on the dense block (x^5 has period 2^30 on the 2-part)? i.e. do constants with high 2-adic order create fixed-point-like behaviour in S-box orbits?
- The wide relation search is tool-limited (blind above k~65); would a BKZ with block size 20+ (fpylll not installable here) or a meet-in-the-middle on sparse 3-5 term relations over all 192 + MDS close the gap?
- Which relations should be tested that involve products, not just linear combinations (c_a c_b = c_c c_d; c_a^5 in terms of other constants; relations with the Cauchy x_i, y_j rather than M_ij)? Only M_ij were included; x_i,y_j and their differences untested in the lattice.
- Does any (r, s) satisfy c_s = M^k c_r only on two of three lanes (partial relations)? Not tested.
- Is the integer-divisibility of X by 30 meaningful for any structure of the 2^65 capacity entry (e.g. different capacity encodings L*2^64 for other lengths)? Likely not; unchecked.
- Do the MDS entries reduced mod p (x0, x1, y1) hint that the organiser's halo2 version draws MDS without rejection - and does that change anything for tests against other Poseidon instances (e.g. the Vesta constants)? Not looked at.
