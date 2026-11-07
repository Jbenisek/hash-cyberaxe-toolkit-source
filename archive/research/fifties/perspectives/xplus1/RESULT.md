# Lens xplus1: (x+1)-adic valuation of the front-line residual

2026-10-09 20:05 MDT. Labels: COMPUTED = measured by `analyze.py` on `../data`; DERIVED = algebra; GUESS = not verified.
The full log is in `analyze_out.txt` (sections 0-12). The run takes 2-3.5 minutes with numpy and does not use the GPU, because
every statistic here is one O(N) pass over at most 2^20 rows.

## Answer

1. **In this ring the residual has exactly one fixed bit: parity(R3) = parity(R6) on every row.** COMPUTED on all 2^20 `rand`
   rows and all 262,092 distinct `ctx` rows, with 0 exceptions. R therefore lies in a 127-dimensional linear subspace of GF(2)^128.
   Measured as P(all four R words in (x+1)^k) / 2^-4k, the ratios are 2.00, 1.98, 1.95 and 1.94 for k = 1..4 (z = +256, +63, +15, +3.8).
   The CONTROL gives 1.00, 1.00, 0.90 and 0.88.
2. **The bit has an exact cause (DERIVED; each identity also checked on every row).** The last two steps of G are XOR followed by
   a rotation, so they are linear in the ring. In E1 the first-half differences are constant: db1 = beta = 18b0e098, dc1 = 0e09818b
   and da1 = dd1 = 0. In E3, dh1 = eta = 830303cf. With these,
   `V := x^-8 R3 + R6 = x^-8 (1+x) (dc2 + c*)`, where `c* = 6e21be55`. The factor (1+x) always gives even parity.
3. **The front line already credits this bit, so it brings no new gain.** c* = 6e21be55 is the eps of all 14 outcomes in the
   pkgCG proof (Section 10.1). The proof's rate is an exact count, so the bit is already inside 63.95. The equation also allows
   a second solution, ~c* = 91de41aa, and it is impossible (DERIVED, with each step checked on the data). At R = 0, df1 equals
   tau XOR ROR(tau,1), so bit 0 of df1 is tau0 XOR tau1 = 0 (tau bits 0-3 are always 0). Bit 0 of de2 is then
   bit 0 of de1 (03cf8303) XOR 0 = 1, but ~c* has bit 0 = 0. **No new outcome or path.**
4. **Nothing further shows up in the lens.** Every other test is at CONTROL level, or is a confirmed effect that moves no
   probability toward R = 0. The numbers are in the table below.

**Effective bits in this lens: 127 = 128 - 1, and the front line's exact rate already contains that 1 bit.** Beyond the
parity bit, the joint lens folds are uniform up to 40 bits. Their collision counts against the 127-dimensional law give
z = +0.67, +0.14, +1.03, +1.31, +1.25 and +1.00 at 20, 24, 28, 32, 36 and 40 bits on `rand`, and |z| <= 1.0 on `ctx`.

## Ring form of the check (DERIVED; every identity COMPUTED on every row of both sets)

Notation: ROR r = multiplication by x^-r, + = XOR. Let R1 = da2+dg2, R3 = dc2+de2, R4 = dd2+df2 and R6 = db2+dh2. The steps
d2 = x^-8(d1+a2) and b2 = x^-7(b1+c2) then give, **for any pair** (not only this family):

    U = x^-8 R1 + R4 = x^-8 [ (1+x) dg2 + dd1(E1) + x df1(E3) ]
    V = x^-8 R3 + R6 = x^-8 [ (1+x) dc2 + x db1(E1) + dh1(E3) ]

(R1, R3, U, V) is an invertible linear image of R, so

    R = 0  <=>  da2 = dg2 = tau,  dc2 = de2 = eps,  (1+x) tau = dd1 + x df1,  (1+x) eps = x db1 + dh1.

- **A general parity gate for any 2-round route (DERIVED).** A collision on words 1, 3, 4 and 6 needs
  parity(dd1_E1) = parity(df1_E3) and parity(db1_E1) = parity(dh1_E3). When a gate holds, its equation has exactly two solutions,
  y and ~y. A route whose fixed first-half differences break a gate can never close. A route whose differences are fixed
  and satisfy a gate gets one free bit, as this family does on (3,6). The same algebra applies to words 0, 2, 5 and 7
  through E0 and E2 (not computed here).
- **The front line, (1,4) gate (COMPUTED).** dd1 = 0, and df1 varies (140,466 distinct values in 2^20 rows), with odd parity
  on 0.5001 of rows. On those rows U != 0 holds by algebra. This is an E3-only abort after half a G, but it removes 1 bit of
  probability rather than gaining one, and it is the same condition as the proof's df1 = tau XOR ROR(tau,1).
- **v(V) = 1 + v(dc2 + c*) on every row (COMPUTED).** The V check reduces to dc2 agreeing with c* digit by digit.

## Tests (each with a uniform CONTROL; train = first half and test = second half of `rand`; `ctx` as a replicate)

| test | residual | CONTROL | verdict |
|---|---|---|---|
| valuation law of R1, R3, R4, R6 and U vs P(v=k)=2^-(k+1), sec. 2 | chi2/df13 p = 0.02-0.78 on both halves; mean v within +-1.5 sd | p = 0.11-0.98 | uniform (COMPUTED) |
| valuation law of V | P(v=0) = 0 exactly | 0.50 | the parity bit |
| descent P(v>=k+1 \| v>=k), k = 0..17, sec. 3 | all |z| < 3 for R1, R3, R4, R6 and U (largest +2.8, k=14) | largest +2.8 | at control level |
| same for V | k=7: 0.472 (train z -5.1, test z -4.5; ctx -1.7/-2.5); k=8: 0.519 / 0.534 | none | confirmed, but P(v(V)>=9)·2^8 = 0.97 / 1.02: it moves weight between v=7 and v=8, not toward 0 |
| single digit c_j biases, 6x32, sec. 4 | 6 confirmed (V c0 = 1.000; R3 c31, c30 at -0.174; R3 c15, c14 at +0.019; R3 c29 at -0.014) | 0 confirmed, max \|z\| 2.6 | sum of (1-H) over R's 128 digits = 0.045 bit, against 1.57 bits for the 128 raw bits |
| R3 top digits c31 = w31 and c30 = w30^w31 | biased toward 1, which works against R = 0 | | no help |
| joint folds R mod (x+1)^m, 4m <= 16 bits, histogram, sec. 5 | entropy deficit 1.000, 1.000, 1.000 and 1.000 bits (m=1..4), on both rand and ctx | 0.000-0.0009 on rand | exactly the parity bit |
| joint folds, 20-40 bits, collisions vs 127-dim law | z <= +1.31 (rand), <= +1.01 (ctx) | | nothing beyond 1 bit |
| random linear 4m-bit projections of R | deficit 0.00 at 20-24 bits | | the bit hides from a generic projection; the lens finds it at m = 1 |
| XOR view, raw low m bits (reference) | per word, 20 bits: collisions x4.15 (R3), x2.15 (R6), x1.34 (R1), x1.16 (R4) | | XOR-view structure is stronger, and the lens dilutes it (lens 20 digits: x1.013 R3, x1.005 R6) |
| P(zero) on raw low bits (reference) | P(low 4m bits = 0)/2^-4m = 0.60-0.84 | | the XOR-view bias points away from 0 |
| E1/E3 share valuation? P(v(K1)=v(K3)), sec. 6 | 0.3336/0.3340 vs independence 0.3342/0.3333 (\|z\| <= 1.8; G p >= 0.18 on rand, >= 0.06 on ctx) | shuffle 0.3338 | independent |
| fold sharing P(K1 = K3 mod (x+1)^m), m = 1..16 | obs/indep within \|z\| <= 2.1 | | independent; K1w1 alone has a 3.64-bit deficit at 16 digits, but K3 is flat there, so the matching probability stays 2^-m |
| cross-word valuation coupling, sec. 7 | G p >= 0.69 for every pair except (3,6), which is the parity bit; (3,6) restricted to rows with both v >= 1: G p = 0.94 | p >= 0.03 | none besides the parity bit |
| rotation ("spiral") scan, 384 (a,b,r) cells, parity bit removed | (R1,R4), r ≡ 7 mod 8: z_train +5.8, z_test +4.1 (a mean-valuation excess of 0.016) | max \|z\| 1.9 | confirmed but tiny, and not part of the R = 0 condition (GUESS: comes from the da2 and df1 laws) |
| dependence on (context, member), ctx, sec. 8 | homogeneity p >= 0.05; split-half \|z\| <= 2.0 | one control at z -3.9 | no group effect |
| input bits k, j, t, c1, Y4 -> digits, 4,896 pairs, sec. 9 | max \|z_train\| 3.5, 0 confirmed | Bonferroni 4.4 | none |
| where the ideals break, sec. 10 | the E1 first half is constant (da1 = dd1 = 0; db1 and dc1 odd); E3 df1 and dg1 are already uniform in valuation | | the 4 additions of the second half randomize everything else |
| D4 partials (1,577), D0..D3 and digest XOR, sec. 11 | chi2/df8 p = 0.49 / 0.68 | p = 0.35 | uniform |

## The spiral question (the user's "different perspective")

DERIVED. The valuation gives a non-Archimedean absolute value |w| = 2^-v(w). Under it XOR is ultrametric
(|a+b| <= max(|a|, |b|)) and every rotation is a unit, so |x^r w| = |w|. In polar terms, rotation is a pure change of angle
and leaves the radius alone. An Archimedean spiral (radius growing with angle) is therefore impossible under XOR and
rotation in this ring. Only carries can couple angle and radius. The scan in section 7 searched every word pair and rotation
for such a coupling. Apart from the parity bit, it found only a 0.016 mean-valuation excess at r ≡ 7 mod 8 on (R1,R4).
The period-4 remark has a matching reading. Period-4 words are the ideal (x+1)^28. The nibble fold w mod (x^4+1) is the
quotient in which ROR 16, 12 and 8 act as the identity and ROR 7 acts as multiplication by x. That fold is the m = 4 lens
projection, and on the residual it carries exactly the parity bit and nothing more (deficit 1.0002 bits over 16 bits).

## Not tested / limits

- P(v >= k) per word is measurable only up to k ≈ 18, and the joint folds only up to 40 bits. Membership of a residual
  word in the period-4 ideal (v >= 28, probability 2^-28) cannot be observed directly.
- These are compression-level pairs (counter t). The organizer's whole-message `blake3()` was not run.
- The parity gate for words 0, 2, 5 and 7 (E0/E2) is derived only. It was not computed, because those words are already equal in this family.
- "Already credited" rests on reading pkgCG `proof.md` Section 10.1 (eps = 6e21be55 for every outcome, with an exact-count rate).
  I did not rerun the proof's count.

## Files

- `xplus1lib.py`: the ring digits (a superset-sum transform), valuation, folds, and a self-test (22,042 words, 0 failures).
- `analyze.py`: all sections. It reads `../data` only, and its CONTROL seed is fixed.
- `analyze_out.txt`: the full numeric log.
