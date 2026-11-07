# CheapLunch (ePrint 2025/2040) - learning pass, 2026-10-12

Authors: Bak, Bariant, Boeuf, Briaud, Oygarden, Phanse. "The Algebraic CheapLunch: Extending FreeLunch Attacks on AO Primitives Beyond CICO-1".

## What I could and could not read
- eprint.iacr.org PDF/ia.cr direct: Cloudflare challenge (403/HTML) - blocked. WebFetch of the PDF: 403. WebFetch of the abstract page worked.
- Full PDF obtained via Wayback Machine (web.archive.org/web/2025/https://eprint.iacr.org/2025/2040.pdf), saved here as cl.pdf, text cl.txt (pdftotext -enc UTF-8 -layout). Read: abstract, intro, Table 1, 2.1-2.3, 3.4, all of 4.2 (Poseidon), Table 2 comparison, App. A (sponge/CICO), App. D.1 (round skipping), App. E.1 Table 4. NOT read in detail: 3.1-3.3 proofs, 4.1 XHash8, 4.3 Neptune, 5 Griffin/Arion, App. C (FGLM refinement), E.2-E.4 experiments. Page numbers below are the paper's printed numbers (approximate +-1 for table pages). Their code (github atharva-simulauib/algebraic-cheaplunch) was NOT run or opened.

## (1) New versus FreeLunch
- FreeLunch (k=1): custom order makes the CICO system already a Groebner basis; bottleneck = change of ordering (FGLM), cost ~ D_I^omega. Needs inverse-power component (we already noted: no gain for forward x^5).
- CheapLunch: CICO-(t-k, k) with k outputs, k>=1. Model with k+RP variables (x_1..x_k and one y_i per partial round, y_i = lane0 after previous partial round), weighted order (wt x = d, wt y = d^Rf1). After reduction the top-weight parts form a regular "CheapLunch system": GB of the top part is cheap (weighted Macaulay/Bezout, no free lunch but much less than full), then bottleneck is FGLM. [PROVED in paper, p.20; regularity checked experimentally only (Table 4), ideal-degree tightness is a CONJECTURE "we conjecture this bound is achieved" p.21].
- Also: tighter ideal-degree bounds via weighted Bezout; proves/gives the bound claimed in Ethereum report [11].
- For k=1, y-variables = exactly the "one variable per partial round" trick; it does NOT lower degree below forward univariate elimination, only makes the GB step cheap.

## (2) What they do on Poseidon
- Problem: CICO-(t-k,k) (input (x_1..x_k,0..0), first k outputs zero), sponge-mode, forward permutation, Rf1 + RP + Rf2 round structure with the initial linear layer M_E. Not a collision on two free inputs; Appendix A.3 only says collision attack = CICO-(c,c) (capacity zeroed), p.34.
- Ideal degree (p.21): D_I <= d^(k*RF + RP) (RF = total full rounds), conjectured tight, no round skipping. With skipping s = floor(t/k) - 2 first variables each drop a factor d: D_I / d^s (App. D.1, p.41; the skip is the Khovratovich/[9] trick, "following [9]"). For compression mode with subspace trails: 4^{(k-1)Rf1+Rf2}... (Table 1 row, Neptune-style) d^{RP-(t-k)}.
- Weighted degree of regularity <= d*k*(d^{RF}-1)+1 (matched experimentally) (p.21).
- Cost: Eq. (8)/(10) = GB step + FGLM; FGLM dominates ("Step 1 negligible vs change of ordering for most parameters"). Time formula only; the paper states NO memory figure (grep for memory/storage/RAM finds nothing). FGLM memory is implicitly >= D_I (multiplication matrix / sparse), i.e. not small.
- Instances: only large-parameter estimates. Table 2 (p.22): lambda=1024 d=3 t=24 k=8 RF=8 RP=85 (GB 2^368, FGLM 2^456-673); lambda=512 d=5 t=12 k=4 RP=57; lambda=384 d=7 t=9 k=3; lambda=256 d=3 t=49 k=7 RF=6 RP=46 -> 2^219 / 2^253.6 (conservative omega=2). Experimental regularity tests (Table 4): 64/254/255-bit fields, RF/2 in {2,3}, RP=20, alpha in {3,5}, t in {24,3,5}, k in {2,3}. Nothing near Orchard (t=3, alpha=5, RF=8, RP=56, k=1). Their conclusion: no attack on any full-round Poseidon incl. margin.
- Comparison to [36] (Poseidon and Neptune, subspace trails, ePrint 2025/954): theirs lower than [36] unless a nontrivial invariant subspace of M_I exists (l > t-2k), "avoided in new Poseidon instances" (p.22-23).

## (3) Applicability to OUR target (Orchard P128Pow5T3, Pallas, t=3, d=5, RF=8, RP=56, state [nk,rho,2^65], lane 0, collision)
- Collision is not CICO. We would need two inputs with equal lane 0 - a 2-input equation f(a)=f(b), or a CICO-1 against a target we choose. CheapLunch gives no collision-specific technique. [DERIVED]
- "Multi-output" gives nothing: it speeds the case where k>=2 outputs are constrained at once. We compare one lane only (out = 1), so k=1; lanes 1,2 free just means the system is underdetermined (t-in > out), and App. A.1 (p.32) says the standard answer is to fix extra free inputs - that is the existing two-round-skip / free-variable trick we already use. Constraining free lanes would only ADD equations. [DERIVED]
- k=1 specialisation: D_I <= d^(RF+RP) = 5^(8+r) (r partial rounds counted after our skip); their generic skip s = floor(3/1)-2 = 1 gives 5^(7+r). Our univariate degree after the ToSC 2022 two-round skip is 5^(6+r), i.e. already LOWER than the CheapLunch degree by factor 5. So their ideal degree is not better than ours. [DERIVED from Sect. 4.2 formula + D.1 p.41; check that their s=1 vs our 2 skipped rounds is not a different convention - GUESS on exact round bookkeeping, one could verify in 10 min]
- Algorithm: after the Groebner step, FGLM on a degree-D_I ideal costs >= D_I^omega and memory >= D_I-sized matrices, versus our direct univariate polynomial of degree D_I and root-finding (gcd with x^p - x, ~D log D multiplications). CheapLunch is therefore strictly more expensive in time and memory than what we do at k=1; it solves problems we do not have (multi-variable shape). Does not lower memory or degree. [DERIVED]
- Possible leftover idea: App. D.1 non-MDS skipping (Poseidon2 style, 2 rounds skipped at t=16,k=1) - Orchard uses the original MDS matrix, t=3, so s=1 only. Nothing. [DERIVED]
- Verdict: CLAIMED by paper analysis, untested by us (no code run): no new path for Orchard collision. Worth a one-line entry in LEVERS as "CheapLunch k=1 reduces to FreeLunch-style Poseidon model; degree 5^(7+r) worse than ours 5^(6+r)".

## Labels summary
- PROVED (paper, Sect. 4.2 p.19-21): CheapLunch structure, weighted Bezout bound D_I <= d^{k RF + RP}.
- Paper CONJECTURE: bound tight; also regularity only experimental (Table 4).
- DERIVED (mine): k=1 gives no gain vs our univariate; multi-output irrelevant when only lane 0 compared; no memory statement exists in the paper.
- GUESS: exact skip bookkeeping equivalence (7+r vs 6+r).
