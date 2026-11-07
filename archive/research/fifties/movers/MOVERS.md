# Movers: which drawn words move the 18 constants of K and the target k (2026-10-09)

Scripts: `movers.py` (exact map + bit-flip perturbation, 10,000 steps, seed 1), `scan.py` (full 2^32 scans, seed 7).
Sources traced: halfsearch.ctr_outer L732-812, ctr_trial L813-837; check_ak.kfun/hfun; the K form of
CLOUD_BRIEF_BATCH_S.md L44-64 (read only to name the 18 constants).

## 1. Exact map (code trace; `consts()` reproduces K(g) = Y1 + w12 on 10,000/10,000 steps, 0 mismatches)

| const | = (ctr_outer line) | const | = |
|---|---|---|---|
| q  | D2.b1 + W13 | N   | S10 = K2C + S14 |
| A  | ROL8(X13) | X1  | X1 (L784) |
| C  | D2.c1 | X9  | drawn X9 |
| M  | S9 | X13 | X13 (L750) |
| I1, I5, E | IV[1], IV[5], IV[4] (fixed) | S6 | S6 (L783) |
| P  | C0.a1 | D   | D1.d1 |
| Q4 | X4 | T   | drawn S4 |
| X15 | global X15 (fixed) | c0 | S2 + S7 |

Target k (AK*, check_ak.hfun): k = u - (ROL12(a - u - w5) ^ c1), u = ROL16(c1 - Y11) ^ Y12, a = E1.a2.
Context inputs of k: Y12, w5 only. w5 = S2 - K2A - K2B and S2 = ROL8(N - K2C) ^ K2D, so w5 is a function of N.

## 2. Movers (perturbation, one random bit flipped per word per step, 10,000 steps; matches the trace)

| drawn word | constants moved | target k (c1, a held) | K(g) |
|---|---|---|---|
| C0.d1 | P, X1, D | moves | moves |
| D2.a1 = g | none | no | moves (it is the variable) |
| D2.b1 | q, A, C, P, X1, X13, D | moves | moves |
| S11 | A, C, M, P, Q4, N, X1, X13, S6, D, c0 | moves | moves |
| S4 | M, P, Q4, N, X1, S6, D, T, c0 | moves | moves |
| X9 | M, P, Q4, N, X1, X9, S6, D, c0 | moves | moves |
| w6 | A, C, M, P, Q4, N, X1, X13, S6, D, c0 | moves | moves |
| member (Y4) | P, X1, D | moves | moves |
| c1 (cube member, 21 free bits), a held | none | moves 10,000/10,000 | no |
| a (prescribed E1.a2) | none | moves 10,000/10,000 | no |
| c1 with g held (forward trial, a = E1.a2(g,c1)) | none | no: H(c1, E1.a2) = K(g) 10,000/10,000 | no |

I1, I5, X15, E never move (fixed).

## 3. Can the eight outer words move k with all 18 constants fixed?

Triangular rebuild (`movers.invert`, 10,000/10,000 exact): the constants fix D2.b1 (q), S4 (T), X9, hence X8, D2.c1 (C),
X13, S7 (from D2.c1), D3.b1 (from Q4 = X4), D3.a1, S3. Given w6, S11 = ROL7(S7) ^ K3.b1(w6) and the
constants then fix C0.d1 (from D, S11, P) and Y12, hence Y4. So the only freedom is w6 with S3(w6) = S3, and the
rebuilt Y4 must also be a class member (2^17 of 2^32). Full 2^32 scan of w6 on 8 random steps (scan.py seed 7):
w6 solutions 3, 4, 2, 1, 3, 1, 2, 1 (17 in all, mean 2.1, size-biased Poisson(1) as for a random map);
Y4 in class: 1 in every step (the original only). Expected extra outer tuples per constant tuple about 1.1 * 2^-15.
So, apart from g, the eight words give m = 1 outer tuple (and one k map) per constant tuple, up to about 2^-15.

## 4. Answer

- No outer word other than g moves k without moving constants: every one of C0.d1, D2.b1, S11, S4, X9, w6, member
  moves at least P, X1, D. The constants fix Y12 and w5 (w5 through N), so they fix the target map k(c1, a).
- g = D2.a1 moves no constant (it is the variable). Forward: k = K(g), m = |Im K| per constant tuple, measured on two
  tuples by full 2^32 scan (scan.py seed 11, 400 targets each): image fraction 0.624 and 0.614 (random-map
  1 - 1/e = 0.632), so m ~ 0.62 * 2^32 ~ 2^31.3; preimage histogram matches size-biased Poisson(1). Cost per k: one
  K evaluation (29 g-lines).
- Per-trial words move k with all 18 constants fixed: c1 (21 free cube bits) and a prescribed a (the converse of
  check_ak). For each c1, a -> k is a bijection of 32-bit words, so with a free m = 2^32 exactly (every k), cost per
  k O(1) (hfun: one ROL16, one ROL12, 2 adds, 2 subs, 2 XOR). In the forward trial a = E1.a2(g, c1) and
  H(c1, E1.a2) = K(g) on 10,000/10,000, so c1 alone never moves k; the freedom exists only if the attack prescribes a.
- Not tested: which (c1, a) pairs the E1 filter accepts (ctr_filter/ctr_lane not read under the brief), so the
  number of useful targets per constant tuple is bounded only by m <= 2^32.

## 5. Independent check (2026-10-09; own code: scratchpad indep_movers.py, gen_img.py + C full scans)
- AGREE 1, 2, 5: kfun K = Y1+w12, 0/10,000 bad; flip movers identical word by word (g none; all 7 move K); E1.a2 gives k = K(g) 10,000/10,000; c1 and a each move k 10,000/10,000.
- AGREE 3 (m=1), sharper: constants invert in closed form, 0/10,000 bad: D2.b1=q-W13, S7=C^ROL12(D2.b1), X12=ROR8(X1^D), S11=X11-X12-D, w6 from S7,S11 via K3 lines, C0.d1=ROR16(X12^P), Y4 from P,Q4. w6 needs no S3 scan; extras are exactly 0, not ~2^-15.
- AGREE 4: full 2^32 image scans of K on 6 tuples all give 0.6321 (random map), m = 2^31.34; the 0.624/0.614 above are 400-target samples, within noise.
- 6: not tested here either (filter outside brief). 7: noted, no claim to check.
