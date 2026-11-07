# b3-fold: can the output fold make the 128-bit residual cheaper? (2-round BLAKE3)

Scout result, 2026-10-10, for the grid cells layer fold x tech sym, alg, heur, cost. This is our own research only:
nothing was filed or submitted. Labels: PROVED (algebra), COMPUTED (I ran it), DERIVED (arithmetic on computed or
cited numbers), GUESS. "cited" means quoted from BLAKE3_2ROUND_MAP.md. All runs were one process at a time:
validate 0.3 s, measure 158.9 s, heur_sym 12.6 s.

## Verdict: impossible

The fold equality ΔZ_w = ΔZ_{w+8} on words 1, 3, 4, 6 does not relax anything. It is exactly the collision
condition, and the front line already counts this event.

- The front line's residual R = (E1 key) XOR (E3 key), word by word, is Δh_w = ΔZ_w ⊕ ΔZ_{w+8} by definition of the
  fold. The ratio of the fold event to the front-line event is therefore exactly 1. PROVED, and COMPUTED with
  0 mismatches in 4 x 2^26 word checks on real pairs.
- The "both differences zero" event the question compares against cannot happen on words 1, 3, 4, 6. PROVED (P2,
  P3 below). COMPUTED: 0 of 2^26 pairs have zero E1 output difference, and 0 of 2^26 have zero E3 output difference.
- The front line does use "both zero", but on words 0, 2, 5, 7, and there it holds with probability 1 because the
  pins leave E0 and E2 with no difference. COMPUTED: 2^26 of 2^26. A fold-matching version would have to drop the
  pins and would then add conditions (P4).
- The fold's exact algebra is already in the front line. The XOR-linear rewrite below gives Lemma N's constant
  exactly: L(eps) = beta* ⊕ ROR(eta,1) = d931617f (COMPUTED). A change of coordinates cannot change P(R = 0)
  (cited, Section 5 item 9).
- The fold adds no correlation beyond independence. On every word the real same-pair rate and the cross-pair
  (independence) prediction agree within 0.13 bit at 16 and 20 bits (COMPUTED).

Effect on the next submission: none. The brief's next row is 62.7934 against 62.9459 filed, a gap of 0.1525 bit
(DERIVED), and this cell does not change it.

## 1. Structure (PROVED unless marked otherwise)

Notation: h_w = Z_w ⊕ Z_{w+8}. In round 1, E1 = G(Y1,Y6,Y11,Y12; w12,w5) writes Z1,Z6,Z11,Z12 and
E3 = G(Y3,Y4,Y9,Y14; 0,w8) writes Z3,Z4,Z9,Z14. With the pins, C3's outputs are constants for both messages:
ΔY3 = fff8ffff and ΔY11 = fff77ffb (COMPUTED from the map's C3 values; reproduced on every generated pair).

- **P1 (fold identity).** Δh1 = ΔE1.a ⊕ ΔE3.c, Δh3 = ΔE3.a ⊕ ΔE1.c, Δh4 = ΔE3.b ⊕ ΔE1.d and Δh6 = ΔE1.b ⊕ ΔE3.d.
  The fold involution i <-> i+8 maps E1 to E3 and E0 to E2 with the role swap (a c)(b d) (COMPUTED index check
  in heur_sym S1). The input differences sit on fold partners (E1.c is position 11, E3.a is position 3).
- **P2 (E3 cannot cancel).** E3's only input difference is ΔY3, and its message words are equal. For fixed
  message words G is a bijection, so ΔE3 ≠ 0 always.
- **P3 (E1 cannot cancel).** E1 has Δa1 = Δd1 = 0 and Δc1 ≠ 0. If Δa2 = 0 then Δd2 = 0, so Δc2 = Δc1 ≠ 0.
  Hence ΔE1 ≠ 0 always. Together with P2, the only way to collide is ΔZ_w = ΔZ_{w+8} with nonzero values.
- **P4 (words 0, 2, 5, 7).** Making these fold-matched instead of both-zero means allowing ΔY7 or ΔY15 ≠ 0. Then
  E0 or E2 has a nonzero input difference with equal message words, so its output differs by P2's argument.
  - If only one of E0 and E2 differs, no collision is possible.
  - If both differ, the change adds 4 fold-matching word conditions to the 4 the pins already leave. The
    four-checks theorem (k ≥ 4, cited item 3) is already met exactly by the pins.
- **P4' (dual pin is impossible).** Suppose the pins cleaned Y3 and Y11 instead of Y7 and Y15. Lemma L's w5
  difference (w5' = w5 − 8) still enters E1 as y (round-1 slot 11), so ΔE1.a2 = −8 ≠ 0. Meanwhile E3 would carry
  no difference at all, so words 1, 3, 4, 6 could never match. The fold forces E3 to carry a difference, and only
  C3.a (Y3) can supply one.
- **P5 (E1 rotation identity).** Because Δd1 = 0 inside E1, ΔZ12 = ROR(ΔZ1, 8) exactly. COMPUTED: 0 violations
  in 2^26.
- **P6 (fold rewrite).** (r1, r3, r4, r6) -> (r1, r3, w4' = r4 ⊕ ROR(r1,8), w6' = r6 ⊕ ROR(r3,8)) is invertible
  and XOR-linear, with:
  - w4' = ROR(ΔE3.B1 ⊕ L(ΔZ9), 7), which depends on E3 only;
  - w6' = ROR(ΔE1.b1 ⊕ ROR(ΔE3.D1,1) ⊕ L(ΔZ11), 7), which depends on E1 and E3's eta;
  - here L(x) = x ⊕ ROR(x,1). COMPUTED: 0 violations of either identity in 2^26.

  With eta = 830303cf and beta* = 18b0e098 fixed, w6' = 0 holds iff Δc2 is in {6e21be55, 91de41aa}. That is
  Lemma N's eps (or its complement), applied to word 6 given word 3. With eta and beta* fixed, words 3, 4' and 6'
  become one-sided, which leaves word 1 as the only true cross key, matching the map's item 1 of Section 5.
- **P7 (parity).** L has even-weight image, so two parity relations follow:
  - parity(r1 ⊕ r4) = parity(ΔE3.B1);
  - parity(r3 ⊕ r6) = parity(ΔE1.b1 ⊕ ΔE3.D1).

  COMPUTED: each parity is even in 0.500002 and 0.500107 of pairs. GUESS: these are the two exact linear relations
  behind the map's "affine rank 126".
- **Symmetry obstruction.** G is not equivariant under (a c)(b d). The d word rotates by 16 and 8 while the b word
  rotates by 12 and 7, and message words enter only through a. COMPUTED: swap(G(a,b,c,d)) and G(c,d,a,b) agree on
  0.4999994 of bits, with 0 equal words in 4 x 2^20 word comparisons. The same holds with x = y = 0 (0.49997).

## 2. Generator (real pairs, checked against the organizer reference)

b3fold_gen.py builds real 55/63-byte pairs for the last-chunk compression of F||A and F||B (counter t, flags 3).
Round-0 inversion hits all four pins, w4 = W4 and w13 = W13, from 9 free words with no search. validate.py checked
3,000 pairs against hash-smash\verifier\blake3.py at rounds = 2 (COMPUTED, all 0 failures):

- X is identical for both messages (Lemma L), and the pins hold.
- C3 outputs equal the map's constants: 8127c181/7edf3e7e, 76f7aefd, 7af77f38/850000c3, bbfbdffe.
- Digest words 0, 2, 5, 7 agree.
- Both messages are legal 55 and 63-byte strings.
- The numpy bulk path matches the reference word for word.
- Framing: with t = 1 the reference blake3(F||A) equals the hand-built parent root (20/20).

## 3. Measurements on 2^26 real pinned pairs (COMPUTED; seed 2026; measure_out_n26_s2026.txt)

Rates are log2 values. "same" counts the real event within each pair. "cross" is the independence prediction,
Σ_δ n_p(δ) n_q(δ) / (N^2 − N), built from value histograms.

| word | fold pair | fold, full width (cross) | fold 20 bits (same / cross) | fold 12 bits (same) | both-zero 12 bits (same / cross) | both-zero, full width |
|---|---|---:|---:|---:|---:|---:|
| 1 | E1.a ~ E3.c | −32.16 | −20.17 / −20.30 | −12.02 | −21.14 / −21.53 | 0 of 2^26 |
| 3 | E3.a ~ E1.c | −29.77 | −17.50 / −17.59 | −11.28 | none / −31.75 | 0 of 2^26 |
| 4 | E3.b ~ E1.d | −31.81 | −19.89 / −19.88 | −11.95 | −26.00 (1 hit) / −29.25 | 0 of 2^26 |
| 6 | E1.b ~ E3.d | −32.13 | −20.39 / −20.33 | −12.34 | −25.00 (2 hits) / −28.63 | 0 of 2^26 |

- **Both-zero against fold.** Already at 12 bits, both-zero is rarer than the fold event by 9.1 to 20.5 bits
  (DERIVED from the table). At full width no residual output word ever had a zero difference: 0 of 2^26, so the
  95% upper bound is 2^−24.4 per word (DERIVED, rule of three). At 8 bits and above, the share of the fold mass
  sitting at δ = 0 is at most 0.008.
- **Full residual.** R = 0 was seen 0 times in 2^26. That is expected, since the cross-pair per-word sum is 125.87
  bits (DERIVED). The map cites 31.76, 28.62, 31.98 and 32.20 (sum 124.55); my word 3 is 1.15 bits dearer
  (GUESS: a different family or estimator).
- **Joint low bits of all four words.** At 16 bits the rate is 2^−16.12 (940 hits) against a per-word product of
  2^−16.00. At 24 bits there were 9 hits (2^−22.83). No usable dependence between words.
- **Concentration sits on one side only.** ΔE1.a takes 15,842,608 distinct values in 2^26 pairs (top multiplicity
  6,040), while ΔE3.c takes 66,456,050 (top multiplicity 5). The match rate follows the flat E3 side (2^−32.16).
  The front line's class and cube conditioning is what concentrates E3. That is not a fold-layer tool.
- **Fold-algebra words in this unconditioned family.** P(w4' = 0) = 2^−24.00 and P(w6' = 0) = 2^−24.42 at 24 bits,
  which looks random. They become one-sided filters only after eta and beta* are fixed (P6).

## 4. Cells

| cell | status | number |
|---|---|---|
| fold x sym | impossible | G is not (a c)(b d)-equivariant: 0.4999994 of bits agree. The swap-collision special case occurred in 0 of 2^22 pairs, and 181 low-8-bit swap events against 256 expected at random (COMPUTED) |
| fold x alg | impossible (already used) | The rewrite reproduces Lemma N (d931617f). A coordinate change leaves P(R=0) unchanged. Both-zero has rate 0 |
| fold x heur | dead | Avalanche of R is 63.82/128 (sd 5.85, min 36 in 2^18). Greedy descent on HW(R) ends at mean 45.10, worse than random sampling's 41.80 at the same 5,760 evaluations per start (COMPUTED, 1,024 starts) |
| fold x cost | dead | The fold check is not on the per-trial path. The front line charges 2^−18.18 machine units per trial on average (DERIVED from the cited 2^71.935 units over 2^90.115 trials) |

## 5. Not tested / limits

- I did not read proof.md or frontline.py (they were outside my reading list). It is therefore a GUESS that the
  front line's E3 carry equations contain w4' = 0. Lemma N's match was checked from the map's constants only.
- Full-width per-word rates are cross-pair estimates. A same-pair full-width event is expected fewer than once in
  2^26.
- The family is unconditioned (no Y4 class and no Q* cube). Class-conditioned rates were not re-measured.
- t_hi = 0 and t_lo is free. t_lo = 0 would be the root case; its chance is 2^−32 per pair and it was not
  excluded.

## 6. Files (this folder)

b3fold_gen.py (generator plus numpy path), validate.py and validate_out.txt, measure.py and
measure_out_n26_s2026.{txt,json} (main run; the n20 runs are timing tests; console copy in measure_run26.log),
heur_sym.py and heur_sym_out_s99.json (console copy in heur_sym_run.log).

Tool calls: none refused or stopped. One PowerShell exit code 255 was my own pipe closing early on a timing run;
its output files were complete.
