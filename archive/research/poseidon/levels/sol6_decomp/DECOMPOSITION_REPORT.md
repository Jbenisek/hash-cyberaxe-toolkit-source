# Scalar polynomial decomposition of a three-coordinate fifth-power circuit

## Main conclusion

**Both decomposable and absolutely indecomposable restrictions occur.** A composition of vector rounds does not imply a composition of scalar polynomials after restricting to a line and projecting one coordinate. Conversely, a dense invertible Cauchy matrix does not forbid scalar decomposition.

There are three distinct cases to retain in the research grid:

1. A common scalar factor of the **whole intermediate state**. Such a factor must be a permutation of the base field, because the complete state evolution is injective on a nonconstant input line.
2. A factor of the **selected output coordinate only**. Such a factor need not be a permutation and can account for actual collisions.
3. No nontrivial scalar polynomial factor at all. This can be certified exactly and does not itself establish collision resistance.

The results below concern the abstract family in the question and explicitly specified synthetic instances. No Orchard production constants or production collision-search implementation are used in these experiments.

## 1. Definitions and assumptions

Let K = F_p, p > 5, and gcd(5,p-1)=1. Let M be a valid, nonsingular 3 by 3 Cauchy matrix. Each round is

    s_(r+1) = M S_r(s_r + c_r),

where S_r raises all three coordinates to the fifth power in a full round, or coordinate 0 only in a partial round. Let

    s_0(W) = a W + b,   a != 0,
    F(W) = e_j^T s_k(W).

The generic degree bound is deg F <= 5^k. We adopt the question's additional hypothesis deg F = 5^k where explicitly indicated. A partial round whose active coordinate is constant on the line need not increase the degree, and leading coefficients may cancel. One concrete two-round PF example below has degree 5, not 25.

### Polynomial identity versus equality of finite functions

Here a decomposition means the identity F = A(B) in K[W], with deg A, deg B > 1. It does not mean equality merely at the p base-field points.

Two polynomials induce the same function on K exactly when their difference is divisible by W^p-W: division by this polynomial gives a remainder of degree < p; a nonzero such remainder cannot have p roots. As a function, W^p is the identity, so unrestricted function-level decomposition already admits F = F o W^p. The degree condition by itself would not exclude this vacuous construction.

When degree is < p the polynomial representing a function with degree < p is unique, but a proposed decomposition still needs degree bounds or a formal identity test. All primary toy circuit examples have degree <= 625 < 1009. The later synthetic large-degree screens also have formal degree below their stated prime.

The phrase "large prime" matters: p=5 also satisfies gcd(5,p-1)=1, but fifth power is Frobenius there, and the tame arguments requiring division by powers of 5 do not apply.

## 2. Exact classification test for any fixed polynomial

**PROVED.** Put n=5^k. Every nontrivial decomposition has

    deg B = d = 5^i,
    deg A = m = 5^(k-i),    1 <= i < k.

This follows from deg(A o B)=deg A * deg B. In particular, degree 5 is formally indecomposable.

There is at most one possible right component of each degree after normalizing B to be monic with B(0)=0. This does not say that different inner degrees cannot occur.

### Proof and exact procedure

Divide F by its leading coefficient, obtaining a monic polynomial f of degree n. Normalize a hypothetical decomposition so

    B(W) = W^d + b_(d-1) W^(d-1) + ... + b_1 W,
    f(W) = B(W)^m + a_(m-1) B(W)^(m-1) + ... + a_0.

The terms below B^m have degree at most n-d. Therefore, for j=1,...,d-1, the coefficient of W^(n-j) determines b_(d-j) uniquely. Its previously undetermined contribution is m*b_(d-j); m is invertible in K because p != 5.

After deriving this sole candidate B, repeatedly divide F by B. There is a unique B-adic expansion

    F(W) = R_0(W) + R_1(W) B(W) + ... + R_m(W) B(W)^m,
    deg R_i < d.

Then F is in K[B] **if and only if every R_i is constant**. In that case the constants are the coefficients of A. Otherwise this degree split is impossible.

Testing all k-1 splits is necessary and sufficient. This is a direct coefficient form of the classical tame decomposition/approximate-root approach [S1, S2]. The supplied implementation uses a truncated-series Newton root at infinity and exact polynomial division.

**Descent consequence.** The uniquely reconstructed coefficients lie in K. Thus if a decomposition of the specified degrees existed over an extension field, it would normalize to the same candidate and descend to K. Failure of all these tests proves absolute polynomial indecomposability, not just failure over the base field [S3].

**Complexity caution.** Classical decomposition algorithms are polynomial in the *expanded degree* n; the Kozen-Landau result supplies an O(n^2) algorithm under the relevant invertibility assumption [S1]. Since n=5^k, this is not a polynomial-in-round-count cost claim.

### Why testing only an inner quintic is insufficient

Consider the general polynomial

    F(W) = (W^25 + W)^5.

It has inner factor of degree 25. Its sole possible normalized inner factor of degree 5 is W^5, but its W^101 coefficient is nonzero when p>5, so it is not a polynomial in W^5. All possible inner degrees must be considered. This example is a general polynomial control, not asserted to be a restriction of the fixed Cauchy circuit.

## 3. Exactly when the first full round gives a shared quintic

Write each pre-S-box affine coordinate as

    L_j(W)=a_j W+b_j+c_(0,j).

**PROVED.** For p>5, the whole state after the first full round has a common polynomial right factor of degree >1 if and only if all its nonconstant L_j have the same zero, equivalently all ratios

    (b_j+c_(0,j))/a_j   for a_j != 0

are equal.

### Sufficiency

If the common ratio is beta, set B(W)=(W+beta)^5. Each nonconstant L_j(W)^5 is a scalar multiple of B, and every other coordinate is constant. Applying M yields

    s_1(W)=v B(W)+u.

All subsequent additions, fifth powers, and linear mixtures preserve membership in K[B]. Hence F(W)=A(B(W)); under deg F=5^k and k>=2, deg A=5^(k-1)>1.

### Necessity for a factor shared by all three state coordinates

Invert M. A shared factor of the state is a shared factor of the three polynomials L_j^5. A nonconstant one has degree 5, so any nontrivial common right factor must have degree 5, and

    L_j(W)^5 = alpha_j B(W)+gamma_j.

Differentiating shows B' is proportional to each L_j^4. Each L_j^4 has its only root at the zero of L_j; those zeros must agree.

This is a statement about a common factor of the *entire first-round state*. It is not a theorem that every later output-only factor arises this way.

### Consequences for natural line choices

An input line varying only one coordinate satisfies the condition automatically in a first full round. It therefore gives a quintic right factor irrespective of how dense M is and irrespective of later round constants. An aligned line varying two or three coordinates does too.

By gcd(5,p-1)=1, the resulting B=(W+beta)^5 is a permutation. The factor is real algebraic structure, but it contributes no collisions of its own.

### First partial round

If a nonactive coordinate varies on the line, inverting M reveals a nonconstant degree-one polynomial. Such a polynomial cannot have a right factor of degree >1. Thus there is no common first-state polynomial bottleneck in that case. If only the active coordinate varies, the quintic bottleneck exists exactly as above. Later output-only decomposition is still a separate question.

## 4. A fully specified indecomposable Cauchy example

**PROVED by finite exact certificates.** Work in F_1009. Define

    M_ij = 1/(i+j+3),  i,j = 0,1,2,

so

    M = [[673, 757, 202],
         [757, 202, 841],
         [202, 841, 865]].

These are a Cauchy matrix with x=(0,1,2), y=(3,4,5), and no zero denominator. Use two full rounds,

    c_0=(1,2,3),  c_1=(4,5,6),
    s_0(W)=(W,W+1,13),

and read coordinate 0.

The resulting F has degree 25 with leading coefficient 163. Its only possible split is 5 by 5. The unique candidate normalized right quintic is

    B(W)=W^5+702 W^4+703 W^3+380 W^2+673 W.

Exact division gives

    F mod B = 605 W^4+866 W^3+568 W^2+71 W+497.

This remainder is not constant. Therefore no decomposition exists, even over an algebraic closure. The circuit specification, all 26 coefficients of F, the candidate B and the remainder are in data/results.json.

### Independent critical-value certificate

For this same F, F' is squarefree. In the 24-dimensional algebra K[W]/(F'), form the matrix of multiplication by F. Its characteristic polynomial records the critical values. That polynomial is also squarefree. Both gcd certificates and its coefficients are saved in data/morse_certificate.json.

The reason this proves indecomposability is elementary. If F=A(B), take a root alpha of A'. Every root of B(W)-alpha is critical for F and has the same value A(alpha). If B-alpha has a repeated root, F' has a repeated root. Otherwise it has d>=2 distinct roots with the same critical value. Both alternatives contradict squarefree F' and pairwise distinct critical values. This argument works in the present tame finite characteristic. Critical-value criteria are classical; [S4] gives related characteristic-zero results.

### The example is not just a finite-function alias

Degree 25 is below 1009, and the proof is a formal remainder certificate. It does not infer polynomial identities from output-table coincidences.

The same rational construction with entries 1/(i+j+3) is indecomposable over Qbar: a normalized degree-5 right factor would be recovered using only inverses of the leading coefficient and 5, both units modulo 1009, and would reduce to the impossible factor above. The nonzero rational remainder certificate then survives reduction at all but finitely many primes. In particular, there are counterexamples at large admissible primes, not a universal small-field exception. No list of all excluded primes was computed.

## 5. Decomposable examples with very different collision behavior

All examples here use the same M over F_1009 and coordinate-0 output.

### A. A genuine decomposition with no collisions anywhere on the line

Use two full rounds, zero constants, and s_0(W)=(W,0,0). The output is

    F(W)=446 W^25 = (446 Z^5) o W^5.

Both fifth powers are permutations, and 446 is nonzero. Therefore F is a permutation and there exist no W_1 != W_2 with F(W_1)=F(W_2). Complete enumeration of the 1009-point field agrees: 1009 distinct outputs, zero unordered distinct collisions.

### B. An inherited permutation factor with collisions in the outer polynomial

Use c_0=(1,2,3), c_1=(4,5,6), two full rounds, and s_0(W)=(W+7,11,13). The normalized decomposition is

    B(W)=W^5+40 W^4+640 W^3+75 W^2+300 W
         =(W+8)^5-8^5,

    A(Z)=446 Z^5+920 Z^4+425 Z^3+262 Z^2+998 Z+133.

B is a permutation. Exact enumeration gives F image size 644 and 510 unordered distinct colliding pairs. Those are precisely the collisions of A under the relabeling B; the quintic B does not supply additional collisions.

### C. An output-only factor that really is noninjective

Use two **partial** rounds, zero constants, and

    s_0(W)=(W,786 W,193 W).

Then

    F(W)=609 (W^5-W)^5+381 (W^5-W).

Thus B(W)=W^5-W is a nonpermutation right factor. B(0)=B(1)=0, and hence F(0)=F(1)=0.

This does not contradict invertibility of the three-coordinate rounds. B is a factor of the selected output, not a common factor of the whole state; the other coordinates retain the distinction.

A compact algebra check: the first active coordinate is (1/3)(W^5-W). With lambda=134, the linear contribution of the two inactive coordinates to the second selected output is lambda times that first active coordinate. Substitution yields coefficients 609 and 381 above.

This is a two-partial-round synthetic example. It is not a claim about Orchard's leading full-round schedule or its deployed constants.

## 6. Exact collision accounting for a decomposition

Let

    mu_z = #{W in K : B(W)=z},
    N_y  = sum_(z:A(z)=y) mu_z.

Then the total number of unordered pairs of distinct inputs colliding under F is

    C_F = sum_y binom(N_y,2)
        = sum_z binom(mu_z,2)
          + sum_({z,t}: z!=t, A(z)=A(t)) mu_z mu_t.

**PROVED:** partition colliding pairs by whether their B-values are equal or unequal. No independence assumption is involved. The exact probability for a uniformly chosen distinct pair is C_F/binom(p,2).

Consequences:

* If B is a permutation, every mu_z=1 and C_F=C_A. Any outer collision corresponds to a unique input collision. Inverting a translated fifth power takes modular exponentiation using the inverse of 5 modulo p-1, which is polynomial in log p; this changes representation cost, not collision multiplicity.
* If A is injective on B(K), only same-B-fibre collisions remain and C_F=C_B.
* If B is noninjective, collisions exist, but decomposition alone does not prove a cheap search. Fibre sizes, which outer values are actually attained, and the cost of obtaining preimages still matter.
* F is a permutation of K if and only if A and B are both permutations of K. One direction is composition. Conversely, injective F forces injective B; because K is finite, B is then surjective, and injectivity of A follows.
* Algebraic roots over extension fields do not establish distinct base-field collisions. W^5-W'^5 factors over an algebraic closure, but under gcd(5,p-1)=1 its base-field zero set is only W=W'.

A decomposition of the whole intermediate state has an additional restriction. Every round is a bijection of K^3, and a nonconstant affine line injects K into K^3. If all three state coordinates were functions of B and B had a base-field collision, the complete state would have the same collision, a contradiction. **Any common whole-state factor must therefore be a base-field permutation.**

Finally, indecomposability is not a security bound. The prime-degree polynomial W^5-W is indecomposable yet has the explicit equality at 0 and 1. A line projection may also be a permutation even though the full two-message-coordinate hash has a larger input space than output space.

## 7. Exact rejection without expanding the enormous polynomial

**PROVED one-sided test; COMPUTED on small and large-degree synthetic cases.** For a chosen inner degree d, the unique candidate B requires only the top d coefficients of F. Once B is available, a nonconstant remainder F mod B immediately rejects that split.

Both quantities can be computed on the original three-coordinate circuit.

### Leading-coefficient jet

Let D_r=5^r and

    H_(r,j)(t)=t^D_r s_(r,j)(1/t) mod t^d.

An added constant becomes c_(r,j) t^D_r. A powered coordinate updates by taking fifth power modulo t^d. An unpowered coordinate in a partial round is multiplied by t^(4D_r) to express it relative to the next bound 5D_r. Apply M to the three jets.

After k rounds the first d coefficients of H_(k,output) are precisely the top d coefficients of F relative to degree 5^k. Its constant coefficient certifies that the claimed full degree is attained. If that coefficient is zero, the procedure must not silently claim degree 5^k.

### Small quotient-ring evaluation

Run the same circuit with its affine inputs in K[W]/(B), reducing after each polynomial multiplication. The output is exactly F mod B. If nonconstant, no degree-d right component exists. Repeating with B^L reveals the first L B-adic digits and permits deeper exact rejections.

For fixed small d, these arithmetic operations depend on k and d rather than 5^k; naive fixed-width polynomial arithmetic and the root-at-infinity construction give a polynomial cost, with an O(k d^2) field-operation implementation available. This is a screening upper bound, not an operation-metered contest claim for the Python code.

**Critical limitation:** constant remainder is only inconclusive. For instance F=W^25+W^6 has candidate B=W^5 and F mod B=0, but its next B-adic digit is W, so F is not decomposable. Rejecting d=5 does not reject d=25 or any larger candidate degree.

### Executed screen results

On all 1,456 degree-split tests from the small randomized circuit sample, leading jets matched explicit coefficients and quotient-ring evaluation matched dense division. The screen rejected 840 splits exactly. All 616 screen passes in that sample were genuine decompositions, but the explicit false-pass control above demonstrates that this coincidence cannot be used as a theorem.

For a separate synthetic Cauchy instance over p=2^127-1, with four leading full rounds followed by partial rounds, the screen rejected inner degrees 5 and 25 at k=8,16,32. At k=32 the formal degree is

    5^32 = 23283064365386962890625 < p.

Only those two inner degrees were ruled out. No claim of complete indecomposability of the 32-round projection was made. The saved certificates contain the leading jets, sole candidates B, and nonconstant remainders, so they can be replayed without expanding 5^32 coefficients.

## 8. Small-case evidence

All randomized circuit tests use the same toy Cauchy matrix over F_1009. Constants, affine offsets and the nonzero second slope are sampled with saved seed 20261012212057. Each instance is classified by *all* proper degree splits; successful decompositions are recomposed exactly. Complete case data includes every generated polynomial and every candidate/remainder certificate.

| Schedules | Degree | Axis-line cases | Axis decomposable | Two-moving-coordinate cases | Two-moving decomposable |
|---|---:|---:|---:|---:|---:|
| FF, FP, PF, PP | 25 | 512 | 512 | 512 | 0 |
| FFF, FPP, PPP | 125 | 96 | 96 | 96 | 0 |
| FFFF, FPPP | 625 | 8 | 8 | 8 | 0 |
| Total | — | 616 | 616 | 616 | 0 |

F means full, P means partial. All 1,232 sampled instances attained the advertised formal degree. The zero decomposition count in the sampled two-moving-coordinate family is not a theorem about all directions or all constants: the aligned two-coordinate and projection-only examples are explicit exceptions.

### A whole finite line family, not only a random sample

Fix two full rounds, c_0=(1,2,3), c_1=(4,5,6), and input (W,W+b,13). Exactly all 1009 values of b were classified. Every polynomial has degree 25. Precisely b=1008=-1 is decomposable, corresponding to aligned first-layer forms W+1 and W+1. The other 1008 polynomials are absolutely indecomposable by the complete tame test.

### Algorithm validation

* All 2401 monic quartics over F_7 checked against exhaustive normalized-factor enumeration: zero disagreements; exactly 343 decomposable.
* 256 random monic sextics over F_7, both nontrivial splits checked against exhaustive normalized-factor enumeration: zero disagreements.
* 96 deliberately composed cases over F_7, F_13, F_257, F_1009: recovered factors recompose exactly. Includes inner degrees exceeding the characteristic, avoiding a hidden factorial-division assumption.
* 16,919 circuit-evaluation comparisons between symbolic polynomials and an independently expressed direct field recurrence: zero disagreements.
* 128 random small-field checks of the fibre collision identity: zero disagreements.
* Optional SymPy critical-value certificate independently establishes the explicit indecomposable example.

The main experiment and validation script took about 5.92 process CPU seconds on the recorded environment. The 1009-line exhaustive offset scan took about 0.28 CPU seconds. These are local mathematical experiments, not target-normalized collision costs.

## 9. What is proved generically, and what remains conjectural

For an unrestricted uniformly chosen monic degree-25 polynomial over a field of characteristic other than 5, exactly p^9 of the p^25 possibilities are decomposable: choose a monic degree-5 outer polynomial (p^5 choices) and a monic constant-zero degree-5 inner polynomial (p^4), and use uniqueness of the normalized split. Thus the exact fraction is p^-16. More generally the union over degree splits has the usual dimension/count bounds [S3, S5].

**Do not transfer that fraction to this circuit family.** Its axis-line subfamily is 100% decomposable, not p^-16. The parameterized circuit distribution is highly structured.

On a fixed nonzero-leading-coefficient parameter chart, the normalized candidate and zero-remainder requirements are algebraic equations. A single certified indecomposable example therefore shows that the decomposable locus is proper for the particular two-full-round parameter family containing that example. This is an algebraic generic statement for that specified family, not a probability estimate for fixed deployed constants.

**CONJECTURAL / OPEN:** after removing a structurally forced permutation factor, sufficiently nonaligned restrictions of a given long-round fixed-constant instance usually have no further right factors. The experiments support this for the toy samples but do not prove it for all schedules, all k, or Orchard. Nor do they prove that decompositions are the only useful algebraic structure.

The following remain open for any requested concrete production instance: all untested inner degrees, its line-specific image/fibre distribution, the cost of enumerating reachable outer values, and any resulting end-to-end collision cost. No security claim or contest score follows solely from the present decomposition results.

## 10. Reproduction and grid feed

From the extracted package root:

    python code/run_experiments.py
    python code/scan_line_offsets.py
    python code/check_jet_screen.py

Optional independent certificate, with SymPy installed:

    python code/check_morse.py

The standard-library scripts generate JSON and CSV results. The compact grid feed is data/findings.csv and data/findings.json. Every statement carries its scope, evidence level, and what it does not establish.

## Sources

[S1] Dexter Kozen and Susan Landau, *Polynomial decomposition algorithms*, Journal of Symbolic Computation 7 (1989), 445–456. DOI: 10.1016/S0747-7171(89)80027-6. Author publication record: https://www.cs.cornell.edu/~kozen/Papers/papers_by_area.htm

[S2] Arnaud Bodin, *Decomposition of polynomials and approximate roots*, arXiv:0910.1676 (2009). https://arxiv.org/abs/0910.1676

[S3] Joachim von zur Gathen, *Normal form for Ritt's Second Theorem*, Finite Fields and Their Applications (2014). DOI: 10.1016/j.ffa.2013.12.004. The tame uniqueness and descent statements are relevant; the elementary coefficient proof used here is given in Section 2.

[S4] Dijana Kreso and Robert F. Tichy, *Diophantine equations in separated variables*, Periodica Mathematica Hungarica 76 (2018), 47–67. DOI: 10.1007/s10998-017-0195-y. Related critical-point/value arguments are stated there in characteristic zero; Section 4 above supplies the proof under the present finite-field hypotheses.

[S5] Joachim von zur Gathen, *Counting decomposable univariate polynomials*, Combinatorics, Probability and Computing 24 (2015), 294–328; arXiv:0901.0054. https://arxiv.org/abs/0901.0054

These references supply classical background, not claims of originality for the algebraic tests. All circuit examples, finite counts, remainders and timing records in this package are calculations from this run.
