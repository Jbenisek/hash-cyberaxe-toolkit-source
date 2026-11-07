# CARD U8 - the field and its subgroups (Pallas F_p), seen from the Poseidon levels

Written 2026-10-12 by learner U8. Folder `./research/poseidon/levels/U8`. Learning only: no attack score is estimated anywhere. Labels: OBSERVED (measured; script named, re-run to reproduce) / PROVED (short argument given) / DERIVED (follows from labelled facts, not fully written out) / GUESS.

Scripts (all single-process, exact big-int, data read from `pareto_clone\pareto\orchard-pallas-constants.json` through `orchard\impl\poseidon_ref.py`) and their outputs:

| script | content | output |
|---|---|---|
| `fact1.py` | trial division, Pollard p-1, sympy ECM on p-1, p+1, p^2+p+1 (500 s cap per composite) | `fact1_output.txt` |
| `fact2.py`, `fact3.py` | longer ECM on the 412-bit cofactor of p^2+p+1 (split it), then check of the split | `fact2_output.txt`, `fact3_output.txt` |
| `exp1.py` | 2-adic tower, characters of M / Cauchy data / 192 constants, x^5-c, x^3-a, Frobenius on Phi5 and on charpoly(M) | `exp1_output.txt`, `tower.json` |
| `exp2.py`, `exp2b.py` | Cauchy determinant check, cycle lengths of x->x^5, exhaustive toy copies q = 65537, 1000003, 86017, 147457, 270337 | `exp2_output.txt`, `exp2b_output.txt` |
| `exp3.py` | product checks, ord of 5, longest cycle of x->x^5, factorisation of p^2+1 | `exp3_output.txt` |
| `exp4.py` | order of M inside F_{p^3}^* | `exp4_output.txt` |

Tools: Python 3.14, sympy 1.14 (`factorint`, `ecm`, `galoistools`), gmpy2 2.3.2. No external ECM binary, no PARI, no Sage was available (Windows host; WSL has only coreutils `factor`). Everything below with a "probable prime" label was tested with sympy `isprime` (BPSW), not certified.

---

## 1. Factorisations (question 1)

All products re-multiplied and compared (`exp3_output.txt`, and `p^2+1` in a one-liner, True).

| number | factorisation | OBSERVED status |
|---|---|---|
| p - 1 | 2^32 * 3 * 463 * **539204044132271846773** (69 bit) * **8999194758858563409123804352480028797519453** (143 bit) | complete, every factor BPSW-prime. fact1 found the 69-bit prime by ECM in 13 s. |
| p + 1 | 2 * 43 * 257 * 25457 * **798828148463** (40 bit) * **64406061401325646461747376276669182911234205142335110909** (186 bit) | complete, every factor BPSW-prime. 6 s. |
| p^2 + 1 | 2 * 5 * 13 * 132437 * C484 (484-bit BPSW-prime, `exp3_output.txt` line "factor attempt p^2+1") | complete. This is the part of |F_{p^4}^*| that contains 5 (see 3). |
| p^2 + p + 1 | 3 * 73 * 5839 * 12221196943 (34 bit) * 5187662682403 (43 bit) * **487887715480415483992657** (79 bit) * **21186043132281546156793608169660962271252226488966104018788253841360240111557635227669180162173314659** (334 bit) | complete, every factor BPSW-prime (product re-checked). First pass (`fact1.py`, 800 s, B1 up to 250e3, 40 curves per level) left a 412-bit composite C412 = 10336410183878389456389411122965216970727148811023702430995384658173246000781176565624088163903039586972430848856941306458963; the longer run `fact2.py` (B1 = 250e3, B2 = 12.5e6, 25 curves, 216 s) split it into the 79-bit and 334-bit primes (`fact2_output.txt`, `fact3_output.txt`). |

Consequences, OBSERVED/DERIVED:
- The atlas (`ATLAS_POSEIDON.md` G1) lists C (212 bit) of p-1 and C' (225 bit) of p+1 as "unfactored composites". That was only the limit of the small Pollard-rho run: both fall apart in seconds to a 69-bit and a 40-bit prime with plain ECM. p-1, p+1, p^2+1 and (after a second ECM run) p^2+p+1 are now **all fully factored**, so the group orders |F_p^*|, |F_{p^2}^*| = (p-1)(p+1), |F_{p^3}^*| = (p-1)(p^2+p+1) and |F_{p^4}^*| = (p-1)(p+1)(p^2+1) are completely known. [OBSERVED]
- **Largest prime found**: 484 bit (in p^2+1); then 186 bit (p+1), 143 bit (p-1), 43 bit (p^2+p+1). **Smallest unfactored cofactor: none left** (the last open piece, a 412-bit composite of p^2+p+1, split into 79 + 334 bit primes). The reason the first pass failed is only the weak ECM (pure Python, 40 curves): a 79-bit factor needs B1 around 250e3 and more curves.
- The p-1 group order has smooth parts 2^32 * 3 * 463 (all small) and two big primes (69, 143 bits): the multiplicative group F_p^* = Z/2^32 x Z/3 x Z/463 x Z/q69 x Z/q143. The only "small" subgroups, where exhaustive structure can be seen, are those of order dividing 2^32 * 3 * 463. [PROVED from the factorisation]
- Primes in the p^2+p+1 list are all = 1 mod 3 (3 aside): 73, 5839, 12221196943, 5187662682403 [DERIVED: any prime r != 3 dividing p^2+p+1 has ord_r(p) = 3]; so every cube-root-of-unity structure over those fields is genuinely 3-dimensional.

### 1a. The second ECM run
`fact2.py` (single process) called sympy `ecm(C412, B1=250000, B2=12500000, max_curve=25)`; at 216 s it returned 487887715480415483992657 and the 334-bit cofactor. `fact3.py` verified a*b = C412, both BPSW-prime, a = 1 mod 3 as predicted, and a | p^2+p+1. [OBSERVED] Not certified by an ECPP/primality proof; the 334-, 484- and 186-bit primes are BPSW probable primes.

---

## 2. The 2-adic tower (question 2)  [OBSERVED `exp1.py`; full lists in `tower.json`]

p = 1 + 2^32 * t with t odd (223 bit). Smallest quadratic non-residue is z = 5. g = z^t has order exactly 2^32 (checked g^(2^31) = -1, g^(2^32) = 1). Elements of order 2^k are g^(odd * 2^(32-k)): exactly 2^(k-1) of them.

| order | count | values |
|---|---|---|
| 2 | 1 | -1 = `0x40000000000000000000000000000000224698fc094cf91b992d30ed00000000` |
| 4 | 2 | +-i: `0x9423384f0d74a20ce8bb048dcd97d6222ae78c1c3540d2ab8e53c6467324926`, `0x36bdcc7b0f28b5df31744fb72326829dff98203a45f8ebf0e047f48898cdb6db` (agrees with atlas G1) |
| 8 | 4 | `0x70e339f39258d62d9cfeedc219a1265b0a9daaed5ad56f7c18299e8f753a53`, `0x28c44eab3b34e97394eaa8c25744fba55a775171d92b0fe098a524e6b9c52d1`, `0x3d73bb154c4cb168c6b15573da8bb045cc9f23e4ebba481d8fa2de9e9463ad30`, `0x3f8f1cc60c6da729d26301123de65ed9c73bfb511bf223ac1d15074e708ac5ae` (the four roots of x^4 = -1) |
| 16 | 8 | `0x175af5850c48b5312811458ce6b91ca32d6cfe591513b4e62e362a21d6f8f15`, `0x4c91781ddd6cdc625e01428223d2df8327d16ad2328761aa9f1e6c1c384b800`, `0x17e6c570737897f385e789dcbc7a09bd4f82ab3e1182aecd80ec9d0beefa6c6d`, `0x1ff2863fd35bfc59e51f3693bf37e2d841d1b5fbed4138f755a638bec8750abd`, `0x200d79c02ca403a61ae0c96c40c81d27e074e3001c0bc0244386f82e378af544`, `0x28193a8f8c87680c7a1876234385f642d2c3edbdf7ca4a4e184093e111059394`, `0x3b36e87e22293239da1febd7ddc2d207efc9824ee6248300ef3b4a2b3c7b4801`, `0x3e8a50a7af3b74aced7eeba731946e35ef6fc91677fbbdcd3649ce4ae29070ec` |
| 32 | 16 | in `tower.json` (also 64) |

- sqrt(2) exists in F_p (p = 1 mod 8): `0x2fd2824a745a76d66eba979e78df0e0b0b212c20aed866d85a27becfb118d24`; the order-8 element `0x28c44eab...c52d1` satisfies zeta8 = (1+i)/sqrt2 with i = `0x9423...4926`. [OBSERVED, verified s*s = 2 in the script]
- **2-depth** d2(c) = largest d <= 32 such that c is a 2^d-th power. Measured: d2(i) = 30, d2(-1) = 31, d2(zeta8) = 29, d2(zeta16) = 28, d2(an element of order 2^32) = 0; d2(2) = 2, d2(3) = 3, d2(5) = d2(7) = 0. [OBSERVED] In general an element of order 2^k has d2 = 32 - k. [PROVED] So -1 is a 2^31-th power but not a 2^32-th power, i is a 2^30-th power, etc.: **the tower is a chain of nested "is a square" questions, 32 deep**.
- The 2-depth histogram of F_p^* is exactly (p-1)/2^(d+1) at level d for d < 32 and t at d = 32. [PROVED; OBSERVED exhaustively on every toy, e.g. q = 65537: 32768, 16384, ..., 1, 1; q = 86017: 43008, 21504, ... 21, 21]
- The capacity entry: 2^65 is 2 to an odd power, so d2(2^65) = d2(2) = 2 [PROVED, d2 of a power with odd exponent equals d2 of the base].

**The S-box inside the tower.** x -> x^5 acts on the cyclic 2-Sylow group H = <g> (order 2^32) as multiplication by 5 on Z/2^32. [PROVED] Hence: (a) 5 is odd, so S preserves d2 exactly [PROVED; OBSERVED toy exhaustive]; (b) 5 = 1 mod 4, so S preserves the quadratic and the quartic character of every non-zero value [PROVED]; (c) mod 8, 5 != 1, so S sends the octic-character exponent e to 5e mod 8 (1<->5, 3<->7, 0,2,4,6 fixed) [PROVED]. OBSERVED on the real field: the first two asserted, the third held on 2000 of 2000 random x (`exp1_output.txt`). Same for the cube character: e -> 5e = 2e mod 3, i.e. S swaps the two non-trivial cubic classes [DERIVED]. And x -> x^5 does not map H to a smaller subgroup: it is an automorphism of H whose fixed points are exactly the elements of order dividing 4 (those are the 5 fixed points of atlas G2, with 0).
- **Cycle structure of x -> x^5 on F_p^*** [OBSERVED/DERIVED]: the cycle through an element of multiplicative order n has length ord_n(5) (order of 5 in (Z/n)^*), proved on five toys (below, "max cycle = ord of 5 mod (q-1)" matched every time). On the real field: ord_3(5) = 2 (the two primitive cube roots of 1 swap), ord_463(5) = 462, ord_(2^k)(5) = 1 for k <= 2 and 2^(k-2) for k >= 3, ord_q69(5) = q69 - 1 (5 is a primitive root mod the 69-bit prime), ord_q143(5) = q143 - 1 (primitive root mod the 143-bit prime too). q143 - 1 = 2^2 * 3^4 * 11 * 2531 * 115603 * 1197907 * 22160661629 * 325086459374267 and q69 - 1 = 2^2 * 3^5 * 89 * 14923 * 417677162933 (sympy `factorint`, `exp2_output.txt`). Longest cycle of x -> x^5 on F_p^*: lcm = 28141659245774691079001654546646862068247397390777234750164557367345152 (235 bits). So the map has short cycles only on the subgroup of order 2^32 * 3 * 463 (and tiny ones inside it), and astronomically long cycles on the rest. [OBSERVED `exp3_output.txt`, `exp2_output.txt`]
- **Atlas errata found while doing this** (G1 last bullet): "order of 5 modulo 3 is 3, modulo 463 is 463" cannot be true (the order divides phi(m) = 2 and 462); measured values are 2 and 462. [OBSERVED]

---

## 3. F_{p^4} and the fifth roots (question 3)

- p = 2 mod 5, ord_5(p) = 4 [OBSERVED], and (p^2 + 1) mod 5 = 0, so 5 | |F_{p^4}^*| but 5 does not divide p-1, p+1 (and not p^2+p+1); the 5th roots of unity sit in the **p^2+1 part** of the group, not in F_{p^2}. [PROVED] Phi5 = x^4+x^3+x^2+x+1 is irreducible over F_p [OBSERVED, `gf_irreducible_p`; PROVED from ord_5(p) = 4]. Frobenius on its roots: zeta -> zeta^p = zeta^2, the 4-cycle zeta -> zeta^2 -> zeta^4 -> zeta^3 -> zeta [DERIVED].
- **x^5 - c has exactly one root in F_p for every c** [PROVED: gcd(5, p-1) = 1, the root is c^d with d = 5^-1 mod (p-1), OBSERVED: r = c^d satisfies r^5 = c on all 300 random c]. More precisely **x^5 - c = (x - r)(x^4 + r x^3 + r^2 x^2 + r^3 x + r^4) with the quartic = r^4 Phi5(x/r), irreducible for every c != 0** [PROVED from Phi5 irreducible]. OBSERVED with sympy `gf_factor`: factor degree pattern (1,4) for all 300 random c != 0, for all 192 round constants (every one of them), and for c = 1 (x^5 - 1 = (x-1) Phi5). For c = 0 the polynomial is x^5.
- Over F_{p^2} the quartic splits into two quadratics (a degree-2 subfield of F_{p^4}); Q(sqrt5) in Q(zeta5) is inert at p because Legendre(5/p) = -1 [OBSERVED: 5 is a quadratic non-residue, it is also the smallest one]. [DERIVED]
- **Toy confirmation** (exhaustive, q in {65537, 1000003, 86017, 147457, 270337}; all have ord_5(q) = 4): x -> x^5 is a bijection in every case (exhaustive), and x^5-c is (1,4) on 100 random c per toy (`exp2_output.txt`).
- The fact "no non-trivial 5th root of unity in F_p" is what makes the S-box a bijection, and it is the only place where 5 enters the tower of subgroups: the 5-part of every structure we have looked at is **trivial** (5 does not divide |F_p^*|, nor p+1, nor p^2+p+1; the first group containing it is F_{p^4}^*).

---

## 4. Residuosity pattern (question 4)  [OBSERVED `exp1_output.txt`]

Notation: d2 = 2-depth, q4 = e with c^((p-1)/4) = i^e (i = `0x9423...4926`), q8 = e with c^((p-1)/8) = zeta8^e (zeta8 = `0x28c44eab...c52d1`), cub = class of c^((p-1)/3) (0 = cube; 1 = omega, 2 = omega^2 with omega = `0x2d33357cb532458ed3552a23a8554e5005270d29d19fc7d27b7fd22f0201b547`), leg = Legendre symbol.

**MDS matrix entries and Cauchy data** (Cauchy parameters in the gauge x_0 = 0, `exp1_output.txt`; x_1 = `0x3b959c88...24be`, x_2 = `0x3b302851...a846`, y = (`0x6e655e8f...9d8e`, `0x18d573a0...1173`, `0xf728c067...e035`); the gauge-free data are the differences x_j - x_i, y_j - y_i and the sums x_i + y_j = 1/M_ij):

| name | d2 | q4 | q8 | cub | leg |
|---|---|---|---|---|---|
| M00 | 0 | 1 | 7 | 1 | - |
| M01 | 0 | 1 | 3 | 0 | - |
| M02 | 1 | 2 | 2 | 2 | + |
| M10 | 0 | 1 | 7 | 2 | - |
| M11 | **3** | 0 | 0 | 0 | + |
| M12 | **8** | 0 | 0 | 1 | + |
| M20 | 1 | 2 | 6 | 2 | + |
| M21 | 0 | 3 | 1 | 2 | - |
| M22 | 2 | 0 | 4 | 2 | + |
| det M | 0 | 3 | 5 | 2 | - |
| x1-x0 | 0 | 3 | 1 | 2 | - |
| x2-x0 | 1 | 2 | 6 | 0 | + |
| x2-x1 | **5** | 0 | 0 | 0 | + |
| y1-y0 | 0 | 3 | 5 | 0 | - |
| y2-y0 | 0 | 3 | 5 | 0 | - |
| y2-y1 | 1 | 2 | 6 | 0 | + |

- 1/M_ij has the same characters as M_ij up to inversion (q4, q8, cub -> negated; d2, leg equal); the table of 1/M is in `exp1_output.txt`.
- Cauchy determinant formula checked: det M = prod_{i<j}(x_j - x_i)(y_j - y_i) / prod_{i,j}(x_i + y_j) holds with the gauge-x_0 = 0 data (`exp2_output.txt`, True). [OBSERVED] (An earlier line in `exp1_output.txt` printing False is a bug in that one print line, comparing with the wrong product; superseded by `exp2.py`.)
- Unusual-looking, not explained (GUESS: chance): **M12 is a 256th power** (d2 = 8; probability ~2^-8 per entry, ~3.5% that one of 9 entries is this deep), M11 an 8th power, x2-x1 a 32nd power. All four 4th-power-residue entries (M11, M12, M22 and x2-x1) have q4 = 0. det M is a non-residue (agrees with atlas G3; also not a cube). y1-y0 and y2-y0 have identical characters (d2, q4, q8, cub) but are different values. Nothing else visible.

**The 192 round constants** [OBSERVED]: 2-depth histogram (102, 45, 23, 12, 6, 3, 1 for d2 = 0..6) vs expected (96, 48, 24, 12, 6, 3, 1.5, 0.75); quartic exponent counts e = 0..3: (45, 44, 45, 58) vs 48 each (chi-square 2.8, 3 dof); octic counts e = 0..7: (22, 28, 15, 27, 23, 30, 30, 17) vs 24 each (chi-square 9.5, 7 dof); cube-class counts (72, 63, 57) vs 64; Legendre residues per lane over the 64 rounds (28, 34, 28) vs 32, and 12 residues among the 30 constants of the 10 rows R0-R5, R60-R63 (expected 15); rows with all three lanes of equal Legendre symbol 17 of 64 (expected 16); same Legendre symbol in the same lane in adjacent rounds 99 of 189 (expected 94.5). The Legendre grid of the used rows (1 = residue), lanes 0,1,2: R0 111, R1 001, R2 000, R3 110, R4 000, R5 001, R60 110, R61 010, R62 001, R63 010. **Null result: every statistic is within ordinary random fluctuation; constants look like independent uniform field elements as far as characters go.** All 192 x^5-c factor as (1,4) (section 3).

---

## 5. An explicit F_{p^3} and the Frobenius (question 5)  [OBSERVED `exp1_output.txt`, `exp2b_output.txt`]

- p = 1 mod 3, so F_{p^3} is a **Kummer extension**: x^3 - a is irreducible over F_p iff a is a non-cube. 2 is a non-cube (smallest a >= 2: a = 2; sympy `gf_irreducible_p` says x^3 - 2 irreducible). So **F_{p^3} = F_p[theta]/(theta^3 - 2)**, basis 1, theta, theta^2.
- **Frobenius is diagonal in that basis**: theta^p = theta * 2^((p-1)/3) = omega * theta with omega = `0x2d33357cb532458ed3552a23a8554e5005270d29d19fc7d27b7fd22f0201b547` (the same omega as 5^((p-1)/3), so 2 and 5 are in the same cubic class); x^p mod (x^3 - 2) = omega x as printed. So phi(c0 + c1 theta + c2 theta^2) = c0 + c1 omega theta + c2 omega^2 theta^2. The three roots are theta, omega theta, omega^2 theta and Frobenius permutes them cyclically (a 3-cycle); phi^3 = id. [OBSERVED + PROVED] Norm(theta) = 2, trace(theta) = 0.
- **The MDS matrix lives in this field**: charpoly(M) = x^3 - T x^2 + S x - det M is irreducible (atlas G3; re-checked, True), so F_p[M] is a copy of F_{p^3} and M acts as multiplication by an eigenvalue lambda. The Frobenius on the roots of charpoly(M), in the model F_p[x]/charpoly(M) (coefficients high to low, i.e. x^p = c2 x^2 + c1 x + c0):
  - x^p = `0xa5df257584b7c4711f67d9ac67b28b867de93b3320698dab54eba905c0f521` x^2 + `0x2c13efacb01aedd793daf852bd3f94b19d9b7fb6153d434b22222c16c71ecf97` x + `0x37a74b12d391164eb1233c5cac9b0c0f7068a09135fcb2d4d13bfb5685d2643`
  - x^(p^2) = `0x3f5a20da8a7b483b8ee0982653984d749bc8afc0d62c8f8dedd84543fa3f0ae0` x^2 + `0x13ec10534fe512286c2507ad42c06b4e84ab1945f40fb5d0770b04d638e13069` x + `0x28fdb6694a18b897ce0a9c3761b5e64a6d09e03c422e240aa184380ba470ce3e`
  - x^(p^3) = x checked True. So the roots are lambda, lambda^p, lambda^(p^2), and norm lambda^(1 + p + p^2) = det M. [OBSERVED]
- **Order of M** (`exp4_output.txt`): M^(p^3 - 1) = I, and for every prime r of p^3 - 1 = (p-1)(p^2+p+1) (2^32, 3^2, 463, q69, q143, 73, 5839, 12221196943, 5187662682403, the 79-bit and the 334-bit prime) the matrix M^((p^3-1)/r) is not I. Hence **ord(M) = p^3 - 1 exactly** (the product of the measured r-parts equals p^3 - 1, checked, 763 bits): **an eigenvalue lambda of M is a primitive element of F_{p^3}, and M is a Singer cycle of GL_3(F_p)**: its powers M^0..M^(p^3-2) run through all p^3-1 non-zero elements of the field F_p[M]. [OBSERVED; settles the atlas G3 open item "exact order not determined"] Also M^(p^2+p+1) = det(M) * I (scalar) and M^((p^2+p+1)/r) is not scalar for any prime r | p^2+p+1 [OBSERVED]; with ord(M) = p^3-1 the order of M in PGL3(F_p) is exactly p^2+p+1 [DERIVED] (M^k is scalar iff (p^2+p+1) | k).
- Toy check (exhaustive, q = 86017, 147457, 270337, 331777 with q = 1 mod 3): theta^q / theta is a primitive cube root of 1 in every case, x^3 - 2 has no root in F_q (exhaustive count 0). q = 65537 (2 mod 3) has no Kummer cubic; there an irreducible cubic x^3 - x - 4 (smallest a = 4). [OBSERVED `exp2b_output.txt`, `exp2_output.txt`] The toy primes with 3 | q-1 have a different Frobenius diagonal (omega or omega^2) depending on the prime; for the real p it is omega = 2^((p-1)/3).

---

## 6. The other subgroups that matter for the levels (reference table)

| group | order | known structure |
|---|---|---|
| H2 = <g> | 2^32 | cyclic, S acts as x5 on exponents; elements of order 2^k listed above |
| mu_3, mu_463 | 3, 463 | S swaps the two nontrivial elements of mu_3 (5 = 2 mod 3); on mu_463 S is a single 462-cycle on the 462 nontrivial elements (ord_463(5) = 462) [DERIVED from the cycle rule] |
| subgroups of prime order q69, q143 | q69, q143 | S acts on the non-trivial elements of each as multiplication by 5 on Z/q; since 5 is a primitive root mod q, a single cycle of length q-1 (DERIVED from ord_q(5) = q-1) |
| F_p^* total | p-1 | longest S cycle 2^235 (above) |
| mu_5 | 5 | lives only in F_{p^4}^*, in the p^2+1 part |
| F_{p^3}^* | (p-1)(p^2+p+1) | one 412-bit composite unfactored |

---

## 7. Five most useful or surprising observations

1. **p-1, p+1 and p^2+1 factor completely in seconds** (largest primes 143, 186 and 484 bits); the atlas's "unfactored C" were only rho limits. p^2+p+1 needed a second, longer ECM run (a 412-bit composite split into 79 + 334 bit primes). So the group orders of F_p, F_{p^2}, F_{p^3}, F_{p^4} are all completely factored. [OBSERVED]
2. **x -> x^5 preserves the quadratic character, the quartic character and the 2-depth of every value, permutes the octic exponent by e -> 5e mod 8 and swaps the two cubic classes.** All proved from "5 = 1 mod 4 and 5 is odd" and checked on 2000 real values and exhaustively on toys. Translation C and the MDS multiplication M do not respect this, so characters are a quantity the S layers keep and the C and M steps scramble. [PROVED + OBSERVED]
3. **For every c != 0, x^5 - c splits as 1 + 4 over F_p** (the quartic is a scaled Phi5, always irreducible): the S-box's inverse is "take the unique root", and the other four preimage-style roots live only in F_{p^4}. Checked on 300 random c, all 192 round constants, and on the toys. [PROVED + OBSERVED]
4. **Cycle lengths of x -> x^5**: short only on the 2^32 * 3 * 463 subgroup (lengths up to 2^30 from the 2-part); 5 is a primitive root modulo both big prime factors of p-1 (69 and 143 bit), so on the rest of F_p^* the cycles are astronomic (longest 2^235). The atlas' "ord of 5 mod 3 = 3, mod 463 = 463" slip is corrected to 2 and 462. [OBSERVED]
5. **F_{p^3} has a clean Kummer model theta^3 = 2, with Frobenius = diagonal(1, omega, omega^2), and M is a multiplication-by-lambda inside it** (charpoly(M) irreducible, Frobenius x^p printed above, M^(p^2+p+1) = det M * I). **ord(M) = p^3 - 1 exactly**: M is a primitive element (Singer cycle), M^k is scalar only for k a multiple of p^2+p+1. [OBSERVED]

## 8. Questions this raised (for the other learners and the atlas)

1. **Is the 2-adic coordinate useful across a level?** In log coordinates of the 2-Sylow, S is multiplication by 5, a perfectly linear map, but C (add constant) and M (mix lanes) are additive, not multiplicative; is there any set (a coset of H2 or of a smaller subgroup, e.g. all lane values in {+-1, +-i}) that survives C + S + M for a step, and what is the first level where it stops? (The 5 fixed points of S = {0, +-1, +-i} are the natural test set.) What does the constant structure (no constant is +-1, +-i; 2-depths random) say about hitting it?
2. **The Kummer model and M**: M = multiplication by lambda in F_{p^3} acting on the vector space F_p^3 with the lanes as one fixed basis; what is the explicit cyclic-vector basis for lane 0, i.e. beta with output = Tr(beta * z)? Does S (coordinatewise x^5) have any nice description in the theta basis, or only in the lane basis? (GUESS: no; this is exactly what makes the cipher not an F_{p^3}-polynomial.)
3. **M is a Singer cycle (ord M = p^3 - 1)**: what does it buy for the levels? Every power M^k with 1 <= k <= 8 is MDS (atlas G3); for which k does a power of M first have a zero entry, and does the multiplicative structure (log of lambda base a generator of F_{p^3}^*) say anything about the 63 + 1 repeated applications? The discrete log in F_{p^3}^* is conceivable now that the group order is fully factored (the largest prime is 334 bit, so Pohlig-Hellman is not cheap, but the smooth parts are).
4. **Why is M12 a 256th power** (and M11 an 8th power, x2-x1 a 32nd power)? Is that an accident of the Grain-LFSR choice of x_i, y_j, and does it let the row-1 / column-2 entries behave differently under any 2-adic filter?
5. **octic character**: S sends e -> 5e mod 8; what do the characters of states look like along an actual trace (nothing run yet except the invariance test)? Do the Legendre symbols of the 2 or 3 S-box inputs of a full round correlate with anything at the output (checked only: no statistic on the constants themselves).
6. The toys with 2-adicity 12-16 (q = 65537, 86017, 147457, 270337) enumerate completely; a toy with 2-adicity 32 does not exist at this size. Are there effects (e.g. S having orbits of length 2^30 inside H2) that only appear when the 2-adicity is large, and which a smaller toy cannot show?

---

## 9. Boring details
- Python 3.14.3 on Windows; all runs single process, no GPU, a few minutes in total (fact1 800 s, fact2 216 s, exp3 under 10 s, exp2 about 60 s). `fact1.py` ran with Python sympy ecm (not GMP-ECM).
- `fact1_output.txt` ends with the 412-bit item under UNFACTORED and lists 5187662682403 there too, only because the script's work list was not re-checked for primality after the time cap; it is prime.
- `exp1_output.txt` has one wrong printed line ("Cauchy det formula ... False"); fixed in `exp2_output.txt` (True).
- `exp2_output.txt` toy cubic lines print a wrong 'omega' label for toys with a non-cube a (the label used a quadratic non-residue); `exp2b_output.txt` is the corrected run (primitive cube root verified in all four toys).
- Smallest quadratic non-residue 5; smallest non-cube 2; both in cubic class omega.
