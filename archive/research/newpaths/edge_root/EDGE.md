# EDGE (root arrangement): are the counter-filter inputs fixed per outer or middle step?

Question: in the ROOT loop (outer step = six words C0.c1, C0.d1, D3.d1, S15, S9, w5; middle step = X2;
member = Y4 from the 2^17 class), do Y9, w8 and E = Y3 + Y4 + w8 (the inputs of the counter-path filter in
counter_next/knobs/filt2.py: A_t(Y9) and B_t(c = e1 + w8)) stay fixed across the inner trials?

Answer: NO. Both move with every inner trial, so the outer/middle-step skip does not carry over.

From the code (halfsearch.py outer, middle, member, trial; Y9 as in residual_word1):
- Y9 = column G g(X1, X5, X9, X13, w3, w10), c output. X9, X13 are outer words; w3 is a middle word (X2);
  X1 is the member's table row; X5 comes from x0 = C0.a1 - X4 - w2 (C0.a1 from the member, w2 from X2);
  w10 from D1.d1 (member) and S12, S1 (X2).
- w8 = a_d0 - S0 - S5 with a_d0 from x0 again (member and X2), S0 and S5 from X2.
- E = Y3 + Y4 + w8: Y4 is the member itself, w8 as above.

Measured on real root trials (fixcheck.py, fixcheck_out.txt; halfsearch imported read-only, members from
class_member, 20 outer steps x 8 middle steps x 256 members, seed 1):
- distinct Y9, w8, E per middle step: mean 255.7 of 256 (the shortfall is repeated member draws);
- per outer step: mean 2045.6 of 2048;
- member held, X2 varied: 256 distinct (Y9, w8) of 256; X2 held, member varied: 256 of 256.

One line: the member Y4 moves Y9 (via X1, X5, w10) and w8/E (via x0 = C0.a1 - X4 - w2), and X2 moves them too
(via w2, w3, S0, S1, S5, S12); no outer or middle step fixes them.

Consequence: the exact feasibility filter (kept 2^-9.98 of outer steps in the counter arrangement,
filt_real_out.txt) cannot skip whole outer or middle steps in the root arrangement. It could only act as a
per-trial early exit, and its gain would depend on its cost against the rest of the trial; not measured here.

Not done (outside the narrow brief): no per-trial cost comparison, no check on other root words.
Files: fixcheck.py, fixcheck_out.txt (this folder).
