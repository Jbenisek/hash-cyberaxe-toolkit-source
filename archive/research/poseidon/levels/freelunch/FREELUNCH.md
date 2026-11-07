# Algebraic FreeLunch vs Orchard Poseidon (single fast pass, learning only)

SOURCE LIMITS (say plainly): the paper PDF itself was NOT retrievable (eprint.iacr.org PDF 403 via WebFetch/curl, Springer paywalled, ia.cr 404).
What I could read: the eprint abstract page and the authors' CRYPTO 2024 talk slides (https://iacr.org/submit/files/slides/2024/crypto/crypto2024/246/slides.pdf, 18 slides; "slide N" below).
The CheapLunch follow-up abstract (ePrint 2025/2040) was read only as an abstract. So: no paper page numbers, no complexity table, no memory section seen.
Items marked PROVED = stated on the slides/abstract. DERIVED = my reasoning from them. GUESS = unverified.

Right number: ePrint 2024/347, "The Algebraic Freelunch: Efficient Groebner Basis Attacks Against Arithmetization-Oriented Primitives", authors Bariant, Boeuf, Lemoine, Manterola Ayala, Oygarden, Perrin, Raddum (CRYPTO 2024). (2024/559 not checked; not needed.)
Note: the author list in the ask (Bariant, Bouvier, Leurent, Perrin) is the ToSC 2022 round-skipping paper, a different paper.

## (1) Method in plain terms
- PROVED (abstract): choose the monomial order so "the natural polynomial system encoding the CICO problem already is a Groebner basis"; plus a dedicated solver cheaper than FGLM.
- PROVED (slides 8-12, 16-17): model CICO-1 (one free input, one output branch fixed, c=1) with one new variable per high-degree S-box; weighted-degree order; no F4/F5 step; then change order to lex (FGLM-like), take the univariate polynomial in x0, root-find (Berlekamp-Rabin). Their algorithm: sysGen, matGen (multiplication matrix of x0), polyDet (characteristic polynomial), uniSol.
- PROVED (slide 3): three ideas: free GB; better solver than generic FGLM; bypass first rounds of Griffin/Arion with "symmetric-like" tricks.

## (2) Targets
- PROVED: Griffin, Anemoi, ArionHash, XHash8 (abstract). Poseidon is NOT in the FreeLunch paper. Results: Griffin up to 7 of 10 rounds (slide 16, 4 h one core per abstract), Anemoi up to 7 of 21 rounds. "do not threaten any full-round function" (CheapLunch abstract).
- PROVED (abstract of ePrint 2025/2040, "The Algebraic CheapLunch", Bak, Bariant, Boeuf, Briaud, Oygarden, Phanse): extends to CICO with multiple outputs, applied to Poseidon, Neptune, XHash8; "assumptions experimentally verified". Details (round counts, formulas) not read. This is the paper to get next if anyone wants Poseidon-specific numbers.

## (3) Mechanism and the condition
- PROVED (slide 11): "If LM(p1),...,LM(pk) are pairwise coprime, then G is a Groebner basis." Free GB = pick a weighted order making the leading monomials pairwise coprime.
- PROVED (slides 7-8, 12): the variable comes from the INVERSE S-box x^(1/d) (Griffin: "(.)^(1/d) is the only high-degree operation = add one variable per (.)^(1/d)"). Equations then look like x_i^d = P_i(x_0..x_{i-1}); with weights wt(x_0)=wt(x_1)=1, wt(x_2)=3 the leading monomials are x1^3, x2^3, x0^49 (slide 12), coprime.
  Anemoi needs a repair (slide ~12 of second deck): x0^2 cancels, so multiply the last equation by x1^2 and reduce (adds parasitic solutions x1=0).
- Deciding statement (DERIVED from the above, not a verbatim quote of a "framework section" I could not see): the freeness comes from the S-box layer being given in "low-degree implicit form" (the inverse power map, plus Flystel/split-power structure), not from the linear layer. The MDS only makes the system dense; it does not create coprime leading terms.
- DERIVED for Poseidon x^5 (forward): if the variable is the S-box INPUT s_{i+1} = M(s_i^5)+c, give weight 5^i; each equation's leading monomial is the single variable s_{i+1} (coprime trivially) and the closing equation has leading monomial x0^(5^R). That IS a Groebner basis, with ideal degree D_I = 5^R, but it is just "substitute the round map", i.e. the univariate polynomial of degree 5^R that we already have. So the condition is met vacuously and gives nothing: FreeLunch's gain exists where the forward-expanded degree is huge (inverse S-box ~p) and the implicit form is small. Our partial rounds have forward x^5 only, so no gain either.
  With CICO-1 shape: our collision has 2 free inputs and 1 output, not a zero-dimensional CICO-1 system (GUESS on how to cast it: fix 3 of 4 unknowns of two copies -> univariate; same as the current line).

## (4) Cost formulas (as given on slides 14-17)
- PROVED: FGLM O(nvar * D_I^3), D_I = product of leading-monomial degrees of the GB. Their faster route: O~(d0 log(d0)^2 d1...dN) for the determinant/char poly (slide 16), plus matGen ("hard to evaluate", slide 17), plus Berlekamp-Rabin O~(D_I). No omega or constants stated on slides; memory not stated; sparse FGLM (Faugere-Mou) memory formula not seen anywhere I could read -> unknown.
- COMPUTED at our sizes: single variable, D_I = 5^(6+r): r=1 -> 5^7 = 78125 (2^16.26); r=2 -> 5^8 = 390625 (2^18.58). With one variable the char-poly step degenerates to the polynomial itself; the cost is the univariate root find, ~ what ATTACK_NOTES.md already uses (time 2^24-27). So FreeLunch gives no speedup.

## (5) Collision variant
- Slide (extra deck "Collision from the CICO problem"): a CICO solution P(x||0^c)=(y||0^c) gives a collision of the sponge when the hash outputs the rate and capacity is zero... i.e. collisions only via CICO of size c; nothing for an ordinary collision on a one-call hash with free capacity-input constraint like ours. No collision-specific variant of FreeLunch found. GUESS: use F(W)-F(W0) as in the notes.

## Subsume or stack with the ToSC 2022 skip line
- DERIVED: after the skip line the system is univariate; FreeLunch's GB for it is trivial. FreeLunch SUBSUMES nothing new and stacks on nothing: it is the multivariate-generalisation of what the skip line already collapses. Griffin's analogue of the skip line is exactly what the FreeLunch paper adds as its idea 3 (slide 3), so the two methods are already combined there; for us the skip line is the whole benefit.

## Bottom line
Does not apply usefully. Poseidon not in the paper; mechanism is inverse-power implicit form (round COMPONENT), absent in x^5 Poseidon; vacuous GB gives the same degree-5^(6+r) univariate. Only open lead: ePrint 2025/2040 (CheapLunch) might have Poseidon-specific partial-round modelling; full text unread. Honest limit: the PDF was not read, so conclusions on (3)-(5) are DERIVED from slides + abstracts.
