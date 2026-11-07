# Collision-entropy scan of 3-round BLAKE3 on structured input sets (null result)

Question: is there a structured input set on which the 3-round BLAKE3 output (flags 11, len 64, standard IV, 16 message words, other words 0) is non-uniform enough that a birthday search restricted to it costs about 2^(H2/2) < 2^128?

Code: ceScan\b3np.py (numpy compression), ceScan\scan.py (families + projections), ceScan\retest.py, ceScan\summ.py; raw results ceScan\res_*.json, ceScan\out_*.txt.
Validation: COMPUTED. b3np.comp matches poseidon\pareto_clone\verifier\blake3.py on 64 random 64-byte messages at 3 rounds and at 7 rounds (both True).

## Method (SAMPLED)
Per family: draw N distinct inputs (N = 2^20, or 2^19 for the k2/k3/k4/HW scans; duplicates removed by a 64-bit hash of the message), compute the 8 digest words, and for 9 projections count equal pairs (sum of C(c,2) over buckets). Expected pairs for a uniform projection = N(N-1)/2 / 2^n; z = (obs - exp)/sqrt(exp) (Poisson). Ratio = obs/exp.
Projections (digest words d0..d7, little endian): lo24 = d0 low 24 bits; hi24 = d7 >> 8; xor24 = low 24 of d0^...^d7; lo3each / mid3each (bits 13-15) / hi3each (bits 29-31) = 3 bits from each of the 8 words (24 bits); xorrot24 = top 24 of d0 ^ ror(d1,5) ^ ror(d2,10) ^ ...; lo28 = d3 low 28 bits; xor28 = xor-fold bits 4..31 (28 bits).
All other message words are held at 0 (m0..m7 = 0 unless the family frees them). Digest is the 3-round compression with feed-forward, no chaining.

## Families tried (exact definitions), 385 families x 9 projections = 3465 tests
- k1: one word m_i uniform 32-bit, i=0..15 (16 families, 2^32 inputs each: too small for the real attack).
- k2: all 120 pairs of free words m_i,m_j (2^64 inputs each).
- k3: 90 random triples of free words (2^96). k4: 90 random 4-sets (2^128 exactly, the minimum that matters), plus w8-11, w12-15, w0-3.
- k8 = m8..m15 free (the filed family) and k16 = all words free.
- Low Hamming weight inside m8..m15 (256 bits): exactly w bits set, w = 1,2,3,4,6,8,12,16,24,32,64,100 (sizes C(256,w); w<=~40 is below 2^128 so these are only structural probes).
- Symmetry on m8..m15: m12+i = rot(m8+i, r) for r = 0,1,4,8,13,16,31 (i=0..3, free m8..m11); m12+i = ~rot(m8+i,r) r=1,8,16; chain m(i)=rot(m(i-2),r) r=1,8,16 (m8,m9 free); all 8 equal; m9=m8,m11=m10,...; m9=~m8,...; m12+i=~m8+i; alternating a,b; arithmetic progression m8+i = a + i*d (d random, d a power of two); xor-AP a ^ (i*d); AP across all 16 words; byte-replicated words (c*0x01010101). All of these have only 2^32..2^128 members, mostly far below 2^128.
- Masks / subgroups, all words m8..m15 (2^(8*bits) inputs): low16, high16, even bits, odd bits, bytes 0&2, low8, high8, low24, low20, low4, 0x80007FFF, nibble0 of each byte, 0xF000000F, low1 (only 256 inputs), low s bits zero for s=4,8,16,24; also m0..m7 masked (low16, even, low8, low4, low1), m0..m15 masked (low16, low8); each word in {0, one-hot}; each word HW<=2; each word one-hot.
- Round-1 G positions: covered by the k1/k2/k3/k4 sweeps over every word index (word index fixes which of the 8 G calls and which x/y slot it enters in rounds 1,2,3 through PERM); no word or pair stood out.

## Results (SAMPLED)
- Ratios are 1.000 +/- the sampling error everywhere (typically 0.99-1.01 at 24 bits, 0.95-1.05 at 28 bits). Mean z over all 3465 tests = -0.002, sd = 1.001: the z distribution is exactly the null Gaussian.
- Largest |z| = 4.22 (k2 w7,11, lo24, ratio 0.953, a DEFICIT of collisions, not an excess). With 3465 tests the Bonferroni threshold is about 4.4, and the expected maximum of 3465 Gaussians is about 3.6-3.8. Rerun with N = 2^22 (2 seeds): ratios 0.999/1.000 and z = +1.88/-1.56. Fluctuation. The next largest (3.57, 3.47, 3.31...) are also within expectation; the largest positive-excess z is 3.47 (k2 w4,9 mid3each, ratio 1.038), not re-tested individually, and it is consistent with the null at this test count.
- Nothing flagged (z > 4 for an excess): no family has a collision rate above uniform beyond noise.

## Sensitivity and what it implies
Statistical resolution per test: 1/sqrt(expected pairs) = 0.55% at n=24, N=2^20 (32768 pairs), about 2% at n=28. A family with true collision-probability excess eps on an n-bit projection would show as ratio 1+eps. All families have eps <~ 0.01 at 24 bits, i.e. H2 deficit < ~0.015 bit per 24-bit projection. To make a birthday search beat 2^128 on the 256-bit digest the set would need H2 < 256 with the set size >= 2^(H2/2)... concretely a saving of 1 bit of search cost needs a 2-bit H2 deficit over the whole digest, which would show as a ratio of about 4 on a 24-bit projection if concentrated there, or ratio 1+tiny spread over ~100 projections (not visible here: a per-bit bias b in many bits adds b^2-type terms, 0.01-level ratios on 24-bit projections bound b to ~0.05 per bit in the projected bits). So: no single bias strong enough exists in the projected bits; biases confined to bits outside these 9 projections (e.g. d1,d2,d4,d5,d6 low bits individually, or high-order interactions) are NOT excluded. GUESS: three rounds of BLAKE3 fully diffuse a 32-bit word difference across the state in the 4 first round plus 2 more rounds, so structured-input bias at 3 rounds would not be visible in plain collision counts; the visible-bias regime is probably 1-2 rounds.

## Verdict
NULL (SAMPLED, 385 families, 3465 tests, 2^19-2^22 samples each). No structured family tried shows a collision rate above uniform at 24/28-bit projections, so 2^(H2/2) = 2^128 for every family tried that has >= 2^128 members (k4, k8, k16, mask families of 16+ bits per word, high-HW sets); the smaller families (k1-k3, low HW, symmetric/AP) are uniform too but are too small to host a 2^128 search anyway. The filed 0^32||x chain stays the plain birthday.
Not done / would reopen: (a) projections not covering all bits (only 9 projections of 24-28 bits; full-digest H2 not measured, impossible at 256 bits); (b) bias only at much finer scale (< 0.5% at 24 bits) cannot be seen with 2^20 samples, 2^26 samples would reach 0.07%; (c) two-block / counter / flags variations and sets where m0..m7 take structured nonzero constants (only zero base tried); (d) differential structure (pairs x, x^delta with matching output differences) is a different test, not a uniformity test; (e) GPU-scale sampling of the best candidates. A reopen trigger would be any family with an excess ratio >1.05 at n=24 repeatable on a second seed.
