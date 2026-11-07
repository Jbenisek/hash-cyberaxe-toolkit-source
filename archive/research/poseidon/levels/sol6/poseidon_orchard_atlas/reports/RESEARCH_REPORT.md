# Orchard Poseidon: round-interaction research atlas

## Result and scope
This package transfers the **questions, audit discipline, grid format and experiment layers**, not the SHA/BLAKE numerical conclusions. It contains 64 round dossiers,4096 directed round-pair records, exact native field identities, native finite tests, a deliberately separate exhaustive small-field experiment, cost ledgers, literature/source provenance, and an explicit list of unfinished mathematical questions.

It is not merely a list of tasks: the native tests and exact algebra below were run in this session. It is also **not a complete cryptanalysis of 64 rounds**, an accepted score, a native collision campaign, or a claim about funds/transactions. No omitted question is silently labeled resolved.

## 1. Which contest target was actually retrieved?
The public addition is HashSmash PR923, head `01f736268b7086d97f38837d343d63a81bf31649`. The connector reports **open, unmerged**. Its text says the targets are locally defined but not registered in Yukon and require organizer baselines; the field-specific cost rule is an organizer decision still open. The user's UI may have moved ahead of this source snapshot. All contest-facing conclusions here are conditional on the pinned proposal, not a claim to have verified current live ranking. [S01]

The proposal uses Orchard's P128Pow5T3 over the Pallas base field, three state elements, exponent 5, rate 2 and one capacity element. Exactly two canonical field elements form the message, with capacity 2^65. There are 64 deployed rounds:4 full,56 partial,4 full. A full round applies the fifth power to all three coordinates; a partial round only to coordinate 0. The proposed one- and two-round targets are **the first one and two full rounds**, keeping deployed constants. [S02-S04]

The canonical input count is exactly p^2 and output alphabet size is p. Since p is just above 2^254, the generic birthday reference is approximately 2^127. The 32-byte encoding does not give 2^256 output values. This baseline is not an estimate of resistance at one or two rounds. [S01-S04]

Orchard's production `prf_nf(nk,rho)` calls the full parameter set in a ConstantLength<2> mode. A contest with both field inputs freely chosen is not the same goal as compromising that keyed protocol use. [S14]

## 2. The row model
Number every deployed round 0..63. For round r and state s_r in Fp^3, let z_r=s_r+c_r. Let f_r fifth-power the active coordinate(s), leaving other coordinates unchanged. Then

    s_(r+1) = M f_r(s_r+c_r).

For a paired state with additive difference Delta, the exact differential update is

    Delta_out = M D_r(s_r+c_r,Delta),

where active D_j=(z_j+Delta_j)^5-z_j^5 and inactive D_j=Delta_j.

This replaces the SHA carry/XOR/selector grid with a **prime-field addition, power and linear-mixing grid**. Machine multiplication carries matter for implementation cost, but they are not the intrinsic differential-coordinate system of this primitive. A single independent field equation under a uniform law costs log2(p), about 254 bits, not one Boolean bit. Dependence and distributions still must be proved before applying that cost.

Every round uses all three incoming coordinates through M. The pair grid records direct and transitive structural reach separately from sampled finite changes. Its upper triangle has 2080 forward cells,24 internal interventions per cell; its lower triangle has 2016 no-forward-causal-path cells. Those lower cells can still participate in **backward constraint implications**. Neither triangular entry is an optimality or necessity certificate.

## 3. PROVED: full-state merging is the wrong endpoint
The calculation gcd(5,p-1)=1 gives a unique fifth root for every field value. The inverse exponent is

    d = 0x333333333333333333333333333333334e9ee0c9a10a60e2e0f0f3f0cccccccd.

All 19 square minors of M are nonzero, so M is invertible and has branch number 4. Undo M, apply d to active coordinates, then subtract c_r to invert a round. This was checked on 1024 independently chosen native states. [S03-S06, local certificate]

Consequently every prefix permutes Fp^3, and the p^2 legal initial states remain distinct **as full states** at every round. Two distinct legal inputs can collide only because the hash exposes coordinate 0 and discards coordinates 1,2. Requiring all three outputs equal would remove every nontrivial candidate. Conversely a coordinate 0 equality at an intermediate row is not preserved for free by later nonlinear rounds.

The full-state inverse is not automatically cheap: ordinary left-to-right exponentiation for d uses 253 squarings and 124 further multiplications,377 field multiplications per active lane, excluding control/load costs. It is exact, not a performance record. A primitive inverse is not a hash-preimage algorithm because two output coordinates remain unknown.

## 4. PROVED and COMPUTED: the first-round image is an affine plane
Put

    X=(m0+c[0,0])^5,
    Y=(m1+c[0,1])^5,
    Z=(2^65+c[0,2])^5.

X,Y independently range over Fp because the fifth power is bijective; Z is fixed. Thus s_1=M(X,Y,Z), and

    row2(M^-1) * s_1 = Z.

There are exactly p^2 legal states on this affine plane. Its coordinate 0 is the nonconstant linear form

    H1=M00 X + M01 Y + M02 Z.

Because M01 is nonzero, each digest has exactly p canonical input messages. For two distinct uniformly selected messages the one-round collision probability is exactly 1/(p+1). This is an exact counting statement about the whole native input domain, derived without enumerating p^2 inputs. It is not a claim that generic sampling is an optimal way to use the formula.

## 5. PROVED and COMPUTED: two rounds have a quintic coordinate description
Using the same X,Y and k_j=M_j2 Z+c[1,j], the second-round digest is exactly

    H2(X,Y) = sum_(j=0..2) M_0j (M_j0 X + M_j1 Y + k_j)^5.

In original message coordinates the straightforward composition has degree up to 25. In these **bijective power coordinates** it is degree 5. This is a change of coordinates, not omission of the first round. All 21 bivariate monomial coefficients were produced in the native field and saved. Both X^5 and Y^5 coefficients are nonzero.

For fixed X and target output, this is a genuine quintic in Y with at most 5 roots. The complete native two-round fibre histogram is **OPEN**. Averaged over all p possible digests the number of inputs is exactly p by counting, but that average does not prove that every digest is attained or equally frequent. No solver runtime or improved attack exponent is inferred from the small degree.

The algebraic identity was checked on 2048 independent legal messages against the full first-two-round reference. This directly addresses the previous project's request to test a different perspective rather than keep multiplying the apparent degree.

## 6. PROVED and COMPUTED: partial rounds have a precise silent horizon
For a partial round write e0=(1,0,0)^T, v=M e0, b_r=M c_r, and n(x)=x^5-x. Then

    s_(r+1)=M s_r+b_r+v n(s_r[0]+c_r[0]).

If paired inputs agree on coordinate 0 before the S-box, the nonlinear differences vanish in that layer and their state difference advances by M. To avoid the active S-box for k consecutive partial rounds, Delta must satisfy

    e0^T M^j Delta=0 for j=0..k-1.

The native observability matrix O=[e0^T; e0^T M; e0^T M^2] has rank 3. Exact remaining dimensions are 2 for one constraint,1 for two,0 for three. The supplied vector(0,M02,-M01) spans the two-constraint kernel and fails the third constraint.

That proves **this exact S-box-avoidance mechanism cannot remain nontrivial through three successive partial rounds**. It does not prove no other differential family, invariant, or nonlinear relation works. There are 432 native two-step checks across all 54 three-partial-round windows.

## 7. PROVED: three active values are coordinates, not three free message words
Let q0=s_r[0], q1=s_(r+1)[0], q2=s_(r+2)[0] in an all-partial three-round window. Set n0=n(q0+c_r0), n1=n(q1+c_(r+1),0). Then

    k1=(b_r)_0+v_0 n0
    k2=(M b_r)_0+(M v)_0 n0+(b_(r+1))_0+v_0 n1
    O s_r=(q0, q1-k1, q2-k2)^T.

Since O is invertible, every(q0,q1,q2) has exactly one unrestricted internal state. The reconstruction was checked 432 times,8 times at each of 54 windows.

**The legality obstruction is exact:** only p^2 of these p^3 triples lie on the image of legal canonical messages. Uniformly selecting unrestricted triples gives legal membership probability 1/p. This is cardinality, not a conjectured random-map heuristic. A useful new generator would have to traverse that legal subset cheaply; the chart alone does not do so.

This is the direct Poseidon analogue of the SHA fixed-CV correction: a convenient internal coordinate must not be counted as a freely editable input.

## 8. PROVED and COMPUTED: exact local differential counts via a quartic
For nonzero additive difference delta, set beta=eta/delta^5, z=x/delta+1/2, y=z^2. Then

    (x+delta)^5-x^5=eta
    <=> 80y^2+40y+1-16beta=0.

The discriminant is 1280+5120 beta. Solve the quadratic fory, then requirey to be a square and recoverz andx. The implementation removes duplicates, including discriminant-zero and square-root-zero cases. There are at most 4 preimages. Roots pair under x -> -x-delta; a repeated symmetric point can give an odd number of distinct roots. Eta 0 has no root for nonzero delta because fifth power is bijective.

All 65,792(delta,eta) pairs for p257, delta nonzero, were compared against brute force. There were zero mismatches. The exhaustive toy root-count histogram is 0 roots:40,960;2 roots:16,640;3 roots:256;4 roots:7,936. Separately 256 native delta/eta cases were exactly solved and each root replayed, half random targets and half known-image targets. The native table is a selected finite set, not an exhaustive native DDT.

These local root counts do not multiply into an end-to-end success rate unless the conditional input law at each nonlinear layer supports that multiplication. The same absolute state is mixed and reused; layers are not independent lotteries by default.

## 9. PROVED and COMPUTED: zero derivative can be a false freedom
At an active input z=0, derivative 5z^4=0. A differential/Jacobian calculation can therefore show an apparent direction of zero first-order response. Yet for a finite nonzero displacementt, (0+t)^5-0=t^5 is nonzero. Since M's column entries are nonzero, this displacement changes all three mixed coordinates.

One such native counterexample is recorded at every round index:64 checks. The whole round remains a permutation despite a singular derivative at the chosen point. Thus a Jacobian kernel is not a certificate of an exact finite neutral subspace. The test uses internal states and does not assert that the chosen singular state is cheaply reached by legal messages.

## 10. SAMPLED: native sensitivity and a deliberately limited signature screen
2048 uniformly sampled canonical message pairs were evaluated with m0 incremented by 1 modp, keeping m1 and capacity fixed. Every prefix 0..63 is recorded:262,144 native round transitions. This measures finite sensitivity from legal inputs, not collision-search success.

Eight features chosen in code before the sample were input bits 0/8, input popcount parities, sum parity, and m0<m1. They were tested against output-coordinate 0's canonical least-significant bit for every prefix. Across 512 tests, **zero** had a Bonferroni-adjusted normal-approximation p-value below.05. This is not a proof of no useful signature; it neither tests an actual conditioned attack population nor has power to observe a2^-127 event. All raw group sizes, counts, p-values and seeds are in signature_screen.csv.

Uniform-field binary encodings need the right null model: p is a255-bit integer just above 2^254. Bit 255 is alwayszero; bit 254 is extremely rare. Independent uniform field words have expected XOR Hamming weight approximately 127, not 128. Per-bit exact numerator and denominator are saved. Observed low activity in those high encoding bits is not a cryptanalytic bias.

## 11. EXACT TOY: collision-versus-trash conservation on all inputs
A separatep 257 model uses width 3,exponent 5,the same full/partial schedule,nativeconstants reduced modulo 257,a different small Cauchy MDS,and capacity 2. All 66,049 message inputs were advanced through all 64 rounds:4,227,136 state updates. All 19 toy MDS minors are nonzero and every round retains 66,049 distinct full states.

Each row partitions the 2,181,202,176 unordered distinct message pairs into projected collisions and noncollisions. The counts add exactly on all 64 rows. At the first round all 257 digest buckets have 257 members; at the second their sizes range 204..493. Those observations show why generator-dependent distributions must be measured rather than presumed; **they are not native Orchard probability estimates**.

The toy data are histogram counts, not a deployed collision submission, and use a plainly separate configuration file. No native failed-pair collection or second-stage correction has been claimed.

## 12. Cost ledger: keep arithmetic, implementation time and scores separate
A straightforward full-state round needs 3 round-constant additions,6 MDS accumulation additions,9 MDS multiplications,and 3 multiplications per active fifth-power S-box. Thus fullround=9 adds+18 muls=27;partial=9 adds+12 muls=21. All 64 rounds total 576 adds+816 muls=1392. These reproduce the proposal's reference arithmetic convention; the proposal itself says the final field-operation scoring policy needs organizer resolution. [S01,S09]

If only the endpoint digest is requested and constants are precomputed, the first-round formula uses 12 online field operations(4 adds+8 muls),with 5 precomputeops. The two-round expression uses 34(10 adds+24 muls),with 10 precomputeops. These counts are **not emitted contest scores**: they exclude loads,branches,encoding,initialization and operation-type weights. They are endpoint-specialized arithmetic opportunities, not a collision-search speedup.

Benchmarks were run with Python 3.13.5 arbitrary-precision modular integers, one process, AMD EPYC 9V74. Each entry uses 512 repetitions after parameter initialization. Example:~118,422 one-round permutations/s, ~60,367 two-round/s, ~2,688 full 64-round/s in this environment. Millisecond timings are noisy; seven actual CPU/wall records are supplied. Do not use them as optimized C/GPU performance or convert them to a cryptanalytic success exponent.

Canonical storage alone is 96 bytes per state and 6,432 bytes for 192 constants plus 9 MDSentries. A backward table adds 288 bytes for M^-1. Language objects and any search lists have separate memory costs. Nothing here establishes a low-memory collision method or charges protocol operations.

## 13. Literature: what was read and what was not
The official implementation, generator and vectors supply the concrete instance. The Poseidon design paper, HADES algebraic analysis(2023/537), and Graeffe/CICO challenge analysis(2025/950) were identified and their landing abstracts reviewed. **Their full proofs and implementations were not audited in this pass.** Different width,field,round schedule,security level,CICO/preimage/collision goals and memory model prevent direct transfer of their claimed exponents. The 2024/310 record is withdrawn and is not used as support. [S10-S13]

No worldwide best full-round Orchard collision result is asserted. Likewise a reference's nominal 127 is not a tested reduced-round strength.

## 14. What has and has not reached bedrock
Completed: exact target identity for the proposal;64 structural cards;4096 indexed paircells;19 nativeMDSminors;whole-state invertibility;first-roundfibre law;two-roundquinticidentity;partialobservabilityhorizon;54 internalcoordinatecharts;localquarticrootlaw;finite-change derivativecounterexample;recordednativechecks;all-inputsmall-fieldbookkeeping.

Not completed: exact native multi-round digest fibres; full joint differential population; legality-preserving multi-round inverse generator; useful route selection on an attack population; proof that no other useful interactions exist; or fully priced accepted collision algorithms. The workbook does not invent an overall percentage of mathematical understanding. Every open obligation is a row in unknowns.csv.

The highest-information next cells are the **legal subset inside the partial chart**, **two-round projected fibre multiplicities**, and **conditional rather than marginal nonlinear constraints**. This is a test priority, not a claim that other rows lack value. All 64 rows remain in the atlas, including the leading and trailing full rounds and the input/output boundary.

## Reproduction
From the package root, run `python check_all.py`. Python's standard library is sufficient for native arithmetic; the full toy enumeration also needs a C11 compiler called `cc`. Each computation is deterministic apart from timing. The code regenerates parameters instead of fetching a network dependency. The 14 test-vector copies are local transcriptions with their own manifest hashes, not an authenticated upstream checkout. No workbook library is needed to replay the mathematics.

## Sources

[S01] HashSmash Orchard target proposal #923
https://github.com/Layr-Labs/hash-smash/pull/923
Scope: LIVE CONNECTOR SNAPSHOT. Open/unmerged when queried; no Yukon registration or baselines in this PR; field-cost question explicitly open. Head 01f736268b7086d97f38837d343d63a81bf31649.

[S02] Proposed contest verifier
https://github.com/Annkkitaaa/hash-smash/blob/01f736268b7086d97f38837d343d63a81bf31649/verifier/poseidon.py
Scope: PINNED PROPOSAL SOURCE. Exact target encoding, schedule, constants and output. Reviewed source; not copied as an authenticated full checkout.

[S03] Official P128Pow5T3 parameters
https://github.com/zcash/halo2/blob/halo2_poseidon-0.2.0/halo2_poseidon/src/p128pow5t3.rs
Scope: PRIMARY SOURCE. RF=8, RP=56, exponent 5; official parameter and vector tests.

[S04] Official Poseidon round and hash mode
https://github.com/zcash/halo2/blob/halo2_poseidon-0.2.0/halo2_poseidon/src/lib.rs
Scope: PRIMARY SOURCE. Round constants -> S-box -> MDS; ConstantLength<2> capacity=2^65; one output field element.

[S05] Official Grain constant generation
https://github.com/zcash/halo2/blob/halo2_poseidon-0.2.0/halo2_poseidon/src/grain.rs
Scope: PRIMARY SOURCE. 80-bit self-shrinking LFSR; reproduced in poseidon_core.py.

[S06] Official Cauchy MDS generation
https://github.com/zcash/halo2/blob/halo2_poseidon-0.2.0/halo2_poseidon/src/mds.rs
Scope: PRIMARY SOURCE. Cauchy 1/(x_i+y_j), secure_mds selection 0 for this parameter set; reproduced locally.

[S07] Official permutation vectors
https://github.com/zcash/zcash-test-vectors/blob/master/test-vectors/json/orchard_poseidon.json
Scope: PRIMARY SOURCE / TRANSCRIBED SUBSET. First 3 of 11 vectors transcribed into local JSON and replayed. Do not report all 11 as tested.

[S08] Official constant-length hash vectors
https://github.com/zcash/zcash-test-vectors/blob/master/test-vectors/json/orchard_poseidon_hash.json
Scope: PRIMARY SOURCE / TRANSCRIBED COPY. All 11 vectors transcribed and replayed. Source master is not a pinned commit; local manifest pins the copy used.

[S09] Proposed contest regression tests
https://github.com/Annkkitaaa/hash-smash/blob/01f736268b7086d97f38837d343d63a81bf31649/tests/test_poseidon.py
Scope: PINNED PROPOSAL SOURCE. 22-vector suite and 27/54 reference arithmetic described there; our run separately replayed 14 official vectors.

[S10] POSEIDON design paper
https://eprint.iacr.org/2019/458
Scope: PRIMARY RESEARCH / LANDING ABSTRACT ONLY. Design context, not a new native attack or a transferred numeric bound. Full paper not reviewed in this pass.

[S11] Algebraic Cryptanalysis of HADES Design Strategy: Application to POSEIDON and Poseidon2
https://eprint.iacr.org/2023/537
Scope: PRIMARY RESEARCH / LANDING ABSTRACT ONLY. Algebraic complexity revisions for specified settings; no Orchard collision result established here.

[S12] Breaking Poseidon Challenges with Graeffe Transforms and Complexity Analysis by FFT Lower Bounds
https://eprint.iacr.org/2025/950
Scope: PRIMARY RESEARCH / LANDING ABSTRACT ONLY. Challenge/CICO targets and memory-access costs are not automatically this two-input collision target.

[S13] A Zero-Dimensional Groebner Basis for Poseidon
https://eprint.iacr.org/2024/310
Scope: WITHDRAWN. Landing record reports withdrawal on 2024-12-23. Not used to justify a bound.

[S14] Orchard native PRF use
https://github.com/zcash/orchard/blob/main/src/spec.rs
Scope: PRIMARY SOURCE / LIVE BRANCH. prf_nf(nk,rho) uses P128Pow5T3 ConstantLength<2>. Protocol usage is not the same as freely chosen two-field contest inputs.
