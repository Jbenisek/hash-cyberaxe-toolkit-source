# OLD_TRICKS: three old tricks against pkgCA's omega-first batch (2026-10-09)

Read-only survey with exact arithmetic. Labels: PROVED, MEASURED, DERIVED (my arithmetic or my chase, not checked by
anyone else) and GUESS. Sources: HANDOFF.md lines 757, 773, 776, 861, 872, 912, 922 and 1190; pkgCA `proof.md` 8
(1101-1153), 9.8 (2191-2459), 10.3 (2846-2870, 2985-3075) and the 11 table (3172-3179); `sol_answer_CD_stack.md` 9.2;
`impl\outer.py` 33-70. The script is in my scratchpad as `oldtricks.py`.

## 0. Where the cost is (pkgCA 11 table; the shares are DERIVED from its rows)
Total 2^73.681 machine units, about 64.93 time_log2 (PROVED: package ledger). Shares: batch (67 units per 7 members)
51.52 %; solver credit 25.07 %; Q path (67 per lane where mask (2) meets S) 20.85 %; passing lane (450) 2.55 %;
context (600) 0.006 %. One unit per batch is worth 0.0111 bit. One unit per Q path is worth 0.0045 bit. One unit per
context is worth about 1e-7 bit. The front line at about 64.87 has slightly different rows (CD's once-per-positive-batch
Y9 path), so every figure below is about +-5 % (GUESS). The pass share of (2) is p0 = 233,715,456 / 2^32 = 0.0544
(PROVED, 8).

## (a) winglock's D3.d1 = X3 (X14 = 0), and S9 fixed so that X9 = 0
**What it did.** In winglock's layout (old seed words) X14 = ROR(D3.d1 XOR X3, 8) entered every outer step. Fixing
D3.d1 = X3 made X14 = 0, so C2.d1 = ROR(C2.a1, 16) needed no XOR. Their counts: stage A 29 -> 28 per batch, and an
outer step 340 -> 318. We valued it at 0.003 to 0.006 bit and decided not to build it (HANDOFF 922, 1190; DERIVED there).
Fixing S9 as well would make X9 = 0, worth about 0.005 according to winglock (GUESS by them).
**pkgCA equivalent.** None. In step CO, X14 = X9 - D3.c1 and D3.d1 = ROL(X14, 8) XOR X3, so D3.d1 = X3 is the same
restriction as X14 = 0, which is the same as X9 = D3.c1. X9 is one of the seven outer words and is free (proof 1110-1112).
**Does it apply?** Not to the batch. X14 is context line 17 of Lemma Y's 39 context lines, and C2.d1 is not one of the
64 needed lines. Neither the omega side (2322-2332) nor the Y9 path (2354-2369) reads X14 (PROVED by those listings).
The only remaining saving is about 3 units in the scalar rebuild of a passing lane (X14, D3.d1, C2.d1), worth
< 0.0003 bit (DERIVED). It also costs the free outer word X9.
**X9 = 0 does apply, to the Q path.** Since X9 is a context word, it can be set to 0 directly with no S9 step. Then
C1c1 = X9 + C1d1 becomes C1c1 = C1d1, and the Q path drops from 67 to 66 units: **-0.0045 bit** (DERIVED).
**Premise it adds.** The context law becomes six uniform words with X9 = 0, which leaves 192 bits, enough for 2^50.465
contexts. H1'(i) (the rate), the H4' shares and Lemma CX (a), (c) are stated for seven uniform outer words. Each would
have to be restated for the restricted law and the rate measured again, because X9 feeds Y9 (C1c1) and omega (through X4
in A). Restriction text: "X9 = 0" (a few characters). Taking X14 = 0 as well forces D3.c1 = 0, i.e.
S4 = ROL12(D3.b1), a second word spent for < 0.0003 bit. Not worth it.
**The same idea one level down, on the omega side (never tried; DERIVED).** Zero a context operand of a batch line. C0.d1 = 0 (an outer
word) removes the XOR in Y0 and the one in X12: batch 66, Q 66, **-0.0157 bit**. S15 = 0 (S11 = K3.c1(w6)) removes the
XOR in D0a1: batch 66, **-0.0111 bit**. X15 cannot be set to 0 because it is pinned: X15 = 0x40C58500 defines Y3, Y11
and the class (outer.py 38, 59). Each zero restriction adds the same rate premise as X9 = 0. Under the uniform six-word
model the per-lane marginal of omega does not change, because v = U - c stays uniform. The per-context pair law does
change, so H_G and the shares need new counts (DERIVED / GUESS).
**Premise-free by-product (DERIVED, lossless).** C0a1 is read only by X0 in the batch and by X12 in the Q path
(proof 2317). Fold the two additions into X0 = Y0 + (-A) with -A = -C0.b1 - w6 - X4 - w2, and let the Q path rebuild
C0a1 = X0 + (X4 + w2). The number of packed context words stays at 16. Batch 66, Q 68: **-0.0066 bit, no new premise**.

## (b) The cluster design of the 93.5 entry (pkg8)
**What it did.** Representatives and partners. Members that differ in e1 bits 14, 30 and 31 carry the same collision
mass (Sol O: PROVED exact for bits 14 and 31), and these partners passed the h1 rule together with the representative
far more often than chance. Stage A ran on the representatives only, and the partners were examined only when their
representative passed. Cost per trial-equivalent: a(1 + n p0)/(1 + S) + p0 s. Charge 1.71, against the field's 5.2110.
Claim 93.479 at margin 3.75 (HANDOFF 861, 912, 922; DERIVED/MEASURED there).
**pkgCA equivalent.** None. "cluster" appears only in premise wording (proof 91, 127, 2858). Every context walks all
2^19 members, each once (Lemma CX b), with a T2 lane test in every lane.
**Does it apply?** Only as a lossy design, and its gain depends on a co-pass rate c that has not been measured. Exact
partners do not exist (DERIVED). Both masks are exactly invariant under flipping bit 31 of their input, because x31
cancels in (1)_j and in (2)_j (proof 1342-1345). The member flip y XOR 2^31, however, enters the cone as U bit 6
(ROL7). It goes Y12 bit 6 -> Y0 bit 14 -> X0 bit 14 -> D0a1 bit 30, so the best case is
omega' = omega + 2^31 +- 2^30, in about 1/8 of members (GUESS: carries treated as coin flips), and never omega XOR 2^31.
Flips of bits 14 and 30 move the low bits of omega, which the automaton reads first, so c should be about p0 for them
(GUESS). I also looked for an exact partner across contexts (Bp + 2^31 with every Y9 operand fixed). It forces S4 to
flip bits 12 and 24, which moves X4 or X9, a contradiction (DERIVED, my chase, unchecked).
**Saving if it is built.** The batch share is multiplied by (1 + n p0)/(1 + n c). n = 1, c = 0.11: -0.038 bit;
n = 1, c = 0.25: -0.121; n = 7, c = 0.20: -0.356 (DERIVED from GUESSED c). The gain is 0 at c = p0.
**Premise it adds.** The old decisive premise: the mass of a partner that is examined and passes equals the class
average. This is a rate premise (H1'(i)) about a walk that is no longer the whole class. Lemma CX (b) and (c) would no
longer hold, since partners of failing representatives are never walked. A co-pass measurement of mask (2), and of (1)
AND (2), is needed for each partner type before any build: one GPU run of a few minutes on the actual domain (GUESS
on the time).

## (c) The two-level trial arrangement
**What it did.** Words that depend only on the member were tabulated. Words that depend only on the middle (outer) step
were computed once per step. A trial computed only the words that depend on both. Stage A went from 87 to 49 per batch
of seven (MEASURED, HANDOFF 773), estimated at 0.5 to 1 bit then (GUESS). HANDOFF 776 also opened "MORE than two
levels".
**pkgCA equivalent.** Yes, complete at two levels. Member lists U = ROL7(y) and E = Y3 + y (member-only words), the 39
context lines once per context, and the 25 member lines per outer step (Lemma Y, 9.8). The c1 level lives inside the
joint solver. No further two-level gain is left.
**What is left is a third level at the top: families of contexts (never tried; DERIVED).** A family draws
(b, c, d) = (C0.b1, C0.c1, C0.d1). Equivalently it draws (C0.d1, D2.b1, X4): D2.b1 = ROL7(X7) XOR (c - d) and
X4 = ROL12(b) XOR c. Each context in the family draws (D2.a1, S11, S4, w6) fresh and sets X9 = ROL7(X4) XOR D3.b1,
which is 9.2's own reconstruction line. X4 -> X9 is a bijection at fixed D3.b1, so **every context's seven outer
words are exactly uniform** (DERIVED: one-line bijection). The rate H1'(i), the H4' shares and the mean in H_G are
therefore unchanged. Per family, the table P[b] = packed Y0 = ROL8(ROL7(y) XOR b - c) XOR d holds 74,899 words, and
memory is free. It costs 74,899 * 15 = 2^20.10 units per family.
New batch: P load 2, X0 = P + (-A) 1, D0d1 1, D0a1 6, w8 1, E load 2, om 1 = **14 instead of 23**, so the batch costs
**58 instead of 67**. The Q path rebuilds C0a1, so it costs 68. The packed context words drop from 16 to 13.
**Saving (DERIVED):** -0.0876 bit at F = 2^4 contexts per family, **-0.0980 at F = 2^8**, ceiling -0.0986. Adding the
restrictions S15 = 0 and X9 = 0 brings it to -0.115, with their rate premise.
**Premise it adds.** H1'(ii) is restated with the family as the independent unit. The F contexts of a family share
Y8, Y12 and Y0 for each member, and Y12 feeds E1.a1, so listed good trials could cluster across them. This is a GUESS:
it is probably small and is measurable as the variance of good-trial counts per family against independent contexts.
Lemma CX (a) becomes independence of families. Lemma MB has to be re-proved for the new listing, where every lane stays
< 2^36. The 10.3 Bernstein exponents divide by F: N_2 4.5e6/F, N_E 2.4e8/F, credit 4.1e8/F. At F = 2^8 that gives
exp(-17,578) at worst, still far below 0.0005, and at F = 2^16 it gives exp(-68.7) (DERIVED). No restriction text is
needed: this is a change of program order, not a restriction.
Fixing A in the family as well would leave a 7-unit omega side and a batch of 51. It would need 9.2's u-equation per
context, about 2^19 units against 2^23.2 per context, which roughly breaks even. Not recommended (DERIVED, rough).

## Order, if any of this is built
1. The fold (-0.0066, no premise).
2. The family level (-0.098, dependence premise only, which is the same kind as today's).
3. Zero restrictions C0.d1 / S15 / X9 (-0.005 to -0.016 each, rate premise, re-measure first).
4. Clusters, only after a co-pass measurement shows c well above 0.0544.
None of these was run or checked by a second reader. Every figure comes from pkgCA's own ledger, so applying them to
the 64.87 front line moves them by a few percent (GUESS).
