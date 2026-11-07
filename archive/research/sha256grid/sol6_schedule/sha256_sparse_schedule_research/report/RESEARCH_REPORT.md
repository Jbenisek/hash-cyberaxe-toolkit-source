# Sparse SHA-256 message schedules: exact late-support classification and linear minima

## Scope and result

**For the question as written, sparse schedules with at most two differing words at indices >=16 exist through N=40, in both the XOR-linearized and genuine modular recurrences. They do not exist for N>=41.** This is a property of the specified support restriction, not a bound on SHA-256 collision attacks.

The XOR-linearized problem was solved completely for the possible exact word supports and for the global minimum bit weight at each requested length. The genuine modular problem was solved for the possible *late* supports and their population sizes; its global bit-weight minima and complete exact *early*-support classification were not solved.

| N | Admissible exact late supports | Exact full word supports, XOR model | Minimum bits, XOR model | Proved bounds, modular model |
|---:|---:|---:|---:|---:|
| 37 | 14 | 99 | **25** | **6 <= minimum <= 25** |
| 38 | 7 | 44 | **44** | **6 <= minimum <= 44** |
| 39 | 3 | 12 | **159** | **11 <= minimum <= 120** |
| 40 | 2 | 9 | **173** | **11 <= minimum <= 133** |
| >=41 | 0 | 0 | No nonzero admissible difference | No nonzero admissible difference |

The modular lower bounds count necessarily nonzero *words* and therefore also bound differing bits; they are deliberately weak, not claimed optimal. The upper bounds are complete native schedules recomputed from their initial 16 words. In particular, the 120-bit and 133-bit examples are strictly below the corresponding exact linear minima: carries invalidate using the XOR minimum as a lower bound for the true recurrence.

### Definitions

* All indexing is zero-based; N=40 means W0 through W39.
* S is the **exact** set of differing word positions. An allowed superset is a different object.
* T = S intersect {16,...,N-1}; the hypothesis is |T| <= 2. Index 16 counts as late.
* The weight in **both** models is sum_t popcount(W_t XOR W'_t). It is not popcount of the modular difference W'_t-W_t.
* The 16 initial words are unrestricted; no chaining value, compression-state condition, padding constraint, or characteristic is imposed.
* All arithmetic in the native recurrence is modulo 2^32. The linearized recurrence replaces its additions by XOR, but retains the exact rotations and logical shifts.

The standard schedule is specified in FIPS 180-4 section 6.2.2. The supplied paper reproduces it in its message-expansion definition. [S1, S2]

## 1. A boundary correction in the supplied literature

The supplied reference card's 37-step pair has support

    {6,7,8,9,10,14,15,22,24}.

Its two late positions are 22 and 24. Recomputing its expansion confirms weight 25 through W36. Extending this *same* pair to W37 introduces a new difference.

The supplied paper's 38-step construction has support

    {7,8,9,10,11,15,16,23,25},

so it has **three**, not two, differing positions at or beyond 16. Its 39-step construction has

    {8,9,10,11,12,16,17,24,26},

with **four** such positions. These published constructions cannot establish the claimed two-late-position boundary at 38. Nor is the paper's unfavorable 39-step SHA-256 attack cost an impossibility theorem for message schedules. [S2, sections 3 and 4.3; S3]

## 2. PROVED: any consecutive 16-word window determines the schedule

The recurrence can be solved backwards without inverting either sigma:

    W_(t-16) = W_t - sigma1(W_(t-2)) - W_(t-7) - sigma0(W_(t-15)).

For the XOR model, replace subtraction by XOR. Thus arbitrary W16,...,W31 determine W15,...,W0, in that order, and then determine every subsequent word by forward expansion.

Consequences:

1. The map from initial messages to W16,...,W31 is bijective, in both models.
2. Two distinct schedules cannot have 16 consecutive equal words anywhere in a valid interval: invert to the beginning, then expand forward.
3. To classify sparse late differences, begin with W16,...,W31 and inspect only equations t=32,...,N-1. The earlier equations construct the initial words rather than adding unknown feasibility constraints.

The reconstruction code was checked on 1,024 random windows in each model, with 2,048 successful inverse/forward round trips.

## 3. COMPUTED EXACT: both small-sigma maps are permutations of 32-bit words

Represent sigma0 and sigma1 by 32x32 binary matrices, using bit 0 as the least significant bit. Exact elimination gives rank 32 for each.

`certificates/sigma_inverses.json` contains both matrices and both inverse matrices. Each inverse is independently checked on all 32 unit vectors. By linearity, these 64 checks certify the two matrix identities on all 2^32 inputs.

Therefore changing an input to either sigma changes its output. Logical shifting inside sigma does not make the complete sigma map noninjective.

This fact is required below. The argument would not automatically apply to a replacement sigma with a nontrivial kernel.

## 4. PROVED: complete late-support classification by incidence signatures

For each late position j define its equation-incidence signature

    v_N(j) = {t in [32,N-1] : j is one of t,t-2,t-7,t-15,t-16}.

A schedule equation cannot have exactly one differing participating word. If it did, exactly one summand (or the output) would change; addition is cancellative, and the sigma maps are injective.

With at most two late positions, this gives a particularly strong test:

* A singleton {j} requires v_N(j) empty.
* A pair {a,b} requires v_N(a)=v_N(b).

For N=37,...,41, the equal-signature groups are:

| N | Empty-signature group | Nonempty equal-signature groups |
|---:|---|---|
| 37 | {22,23,24} | {16,25,30}; {21,29,36}; {26,31}; {28,35} |
| 38 | {23,24} | {16,25}; {22,37}; {26,31}; {29,36} |
| 39 | {24} | {16,25}; {23,38} |
| 40 | none | {16,25}; {24,39} |
| 41 | none | none |

Choose a singleton or two-element subset of the empty-signature group, or a two-element subset of any listed nonempty group. These are **all** admissible T. `data/late_supports.csv` lists them individually.

### Why necessity is sufficient here

Every nonempty signature shared by two positions in this table contains just **one** equation. That equation relates either two differing inputs, or a differing input and a differing output.

For two inputs, fix a base window and change the first participating input. There is one value of the second participating input restoring the equation: the participating maps are identity, sigma0, or sigma1, all bijective. The second input necessarily changes. For an input/output pair, the forward recurrence supplies the changed output. All other post-31 equations have zero differing participants.

For an empty signature, choose one or two arbitrary changed words in W16,...,W31. They do not occur in any post-31 equation under consideration.

Finally invert W16,...,W31 to obtain valid initial messages. This proves existence for every listed T in **both** models, not just absence of a simple obstruction.

### Exact partner counts

Let q=2^32. For **each fixed base message**, the number of companion messages with exact late support T is:

* q-1 for a singleton or a two-position nonempty-signature group;
* (q-1)^2 for a pair in an empty-signature group.

The counts are independent of the base message and are identical in both models. There are q^16 base messages. Thus multiplying by q^16 gives ordered message-pair counts; dividing that result by two gives unordered pair counts.

These counts do not assert equal early-support distributions or equal bit-weight distributions.

## 5. PROVED: the cutoff is 40/41

The table gives a finite, complete support argument. There is also an immediate final-step check.

At N=40, only T={16,25} and T={24,39} remain.

* For {16,25}, equation t=40 contains the changed sigma0(W25) and no other changed term. W40 must therefore differ.
* For {24,39}, equation t=40 contains changed W24 and no other changed term. Again W40 must differ.

Both create a third late position. Consequently no N=41 schedule obeys the cap.

For N>41, restrict to the first 41 words. If the messages are distinct, their W16,...,W31 windows cannot be identical. The restriction is therefore a nonzero schedule with at most two late differences, contradicting the N=41 result.

This cutoff arises from the recurrence taps and the fixed first-block boundary. It is **not** a claimed security boundary at 40 compression rounds.

### Two explicit construction families at N=40

1. Choose two W16,...,W31 windows equal except at W24. Expanding W32,...,W39, the only additional changed word is W39 through sigma0(W24). Invert both windows to obtain the initial blocks. Exact late support is {24,39}.
2. Choose a base window, a nonzero d, set W16'=W16+d and W25'=W25-d, and leave the other window words equal. Their differences cancel in equation 32. Exact late support through W39 is {16,25}.

These are proofs for every admissible choice, not heuristic searches. Their early words are generally dense.

## 6. COMPUTED EXACT: every full word support in the XOR model

For a fixed admissible T, the linear schedules supported inside {0,...,15} union T form a binary vector space of dimension 32 or 64.

Let U={0,...,15} union T. Let H_Z collect all output-bit linear forms for the words in a subset Z of U. The number of parameter vectors vanishing on Z is

    D(Z) = 2^(d - rank(H_Z)).

The number whose exact zero-word set is Z is the superset Mobius transform

    E(Z) = sum_(J subset U\Z) (-1)^|J| D(Z union J).

An exact support S occurs if and only if E(U\S)>0. This handles the finite-field union-of-subspaces issue: checking that each word can individually be nonzero would not suffice.

All zero-word subsets were enumerated with exact binary elimination. All resulting E values were nonnegative, and their sum was checked against 2^d. After requiring both late words nonzero where appropriate, the full support counts are:

    N=37: 99
    N=38: 44
    N=39: 12
    N=40: 9.

`data/linear_full_supports.csv` is the complete list of all 164 (N,S) records, with the exact number of difference vectors for each. These are difference-vector counts, not counts of native modular pairs.

### Example: the optimal N=37 linear pattern

One minimum-weight difference is zero outside the following words:

| t | XOR difference | Bit weight |
|---:|---|---:|
| 6 | 80000000 | 1 |
| 7 | 11002000 | 3 |
| 8 | 80000000 | 1 |
| 9 | 14044aa8 | 9 |
| 10 | 00205000 | 3 |
| 14 | 11002000 | 3 |
| 15 | 80000000 | 1 |
| 22 | 0a020000 | 3 |
| 24 | 80000000 | 1 |

Total weight: 25. This particular table is a **linearized** schedule. The separate supplied native pair also has weight 25, with different absolute words and masks; they must not be conflated.

## 7. COMPUTED EXACT: minimum linear bit weights

The complete minima for the 32-dimensional late-support classes were computed by enumerating all 2^32-1 nonzero parameter vectors, using Gray-code updates and popcount. There are 22 length/class records of this type. Every returned minimum witness and every generator basis vector was independently expanded from W0,...,W15.

For the three distinct 64-dimensional cases, exhaustive 2^64 enumeration was unnecessary.

### Disjoint-information-set certificate

Find r mutually disjoint sets of 64 output-bit positions, each giving an invertible restriction of the code. If a nonzero codeword has weight less than r(L+1), at least one information set has weight at most L.

For every information set, enumerate its binary assignments of weights 1 through L and use its inverse to reconstruct the unique codeword. If the best enumerated weight is at most r(L+1), no smaller codeword can have been missed.

| Late support | Length used | Disjoint sets r | Maximum enumerated information weight L | Completeness threshold | Exact minimum |
|---|---:|---:|---:|---:|---:|
| {22,23} | 37 | 8 | 4 | 40 | 34 |
| {22,24} | 37 | 8 | 3 | 32 | 25 |
| {23,24} | 38 | 9 | 4 | 45 | 44 |

The last certificate also applies at N=37, because its W37 difference is identically zero. A total of 11,894,992 reconstructed candidates, including repetitions across information sets, was examined. The saved information sets and invertibility checks make the completeness argument replayable.

Combining all late-support classes gives global linear minima:

    25, 44, 159, 173  for N=37,38,39,40.

The sharp jump at N=39 is an actual feature of this *restricted linear code*, not just a search timeout: the 64-dimensional empty-signature pair classes have disappeared.

The full per-T minima are in `data/late_supports.csv`; all corresponding witnesses are in `data/results.json`.

## 8. The true modular recurrence: proved support, incomplete weight optimization

Write d_t=W'_t-W_t modulo 2^32 and

    D_sigma(x,d)=sigma(x+d)-sigma(x) mod 2^32.

Then exactly

    d_t = D_sigma1(W_(t-2),d_(t-2)) + d_(t-7)
        + D_sigma0(W_(t-15),d_(t-15)) + d_(t-16).

Unlike sigma applied to an XOR difference, D_sigma depends on the base word. The incidence proof still works because D_sigma(x,d) is nonzero whenever d is nonzero, but the bit-weight code and its minimum-distance certificate do not transfer.

### Native upper-bound evidence

* N=37: supplied Table 17 messages, expanded anew, weight 25 and exact late support {22,24}.
* N=38: an exact bit-vector model realized the 44-bit linear mask as a native pair. The complete model was independently recomputed, giving exact late support {23,24}. The solver took approximately 0.168 process CPU seconds; this is a witness, not a proof of minimality.
* N=39: a deterministic bounded search over native W16,...,W31 windows returned weight 120, exact late support {23,38}.
* N=40: the same type of bounded search returned weight 133, exact late support {24,39}.

The selected N=39 and N=40 runs each examined 25,600,000 local proposals with seed 20261012. These are correlated optimization proposals, **not independent random samples**. No success probability, expected search time, or global minimum is inferred from their best result.

The small initial runs, deeper runs, and an unsuccessful warm-start improvement of the N=38 pair are all logged. Their outputs were independently recomputed. This is a transparent bounded search record, not an exhaustive modular search.

### Proved modular lower bounds

For every admissible T, enumerate all 2^16 early word-support masks and reject any mask making an equation contain exactly one differing word. The smallest remaining word counts are 6,6,11,11 at N=37,38,39,40.

Every differing word contains at least one differing bit, yielding the lower bounds in the summary. The surviving candidate word-support counts are 1691,931,417,354 respectively. They are **necessary-condition catalogues**, not claims that every candidate is realizable. They are deliberately stored separately from the exact linear support catalogue.

A bounded native solver attempt at weight <=24 for T={22,24}, N=37 timed out. Timeout is recorded as UNKNOWN, never UNSAT. The exact modular minima remain OPEN.

## 9. What shifts and carries explain—and what they do not

* The 16-word recurrence explains why an arbitrary later window is a coordinate system and why a 16-word equality band forces identical messages.
* The taps {2,7,15,16}, together with the first-block boundary at 16, explain the exact two-late-word cutoff at N=41.
* The actual sigma shifts/rotations determine binary ranks, Hamming weights, and the detailed linear support catalogue. They matter strongly to the numbers 25,44,159,173.
* Logical shifts break the naive idea that rotating every difference word preserves a solution. For example sigma0(ROTR1(1)) differs from ROTR1(sigma0(1)).
* Carries change the attainable bit-weight geometry. The native 120-bit and 133-bit witnesses demonstrate that the exact linear minima 159 and 173 are not native lower bounds.
* Sparse expanded messages do not themselves establish compression collisions, characteristic feasibility, a first-block match, or an attack cost.

## 10. Evidence labels and remaining questions

**PROVED:** reversible-window parameterization; the incidence necessity rule; its sufficiency for the listed groups; all admissible late supports at N=37..40; nonexistence at N>=41 under the two-late-word cap; exact per-base partner counts; the information-set completeness argument.

**COMPUTED EXACT:** two sigma ranks/inverses; the 164-record complete linear support catalogue and its exact multiplicities; all per-T linear minima and therefore global minima; native witness weights; exhaustive word-level necessary-support lower bounds.

**OPEN:** exact global bit-weight minima in the true modular recurrence; complete early-support feasibility for native pairs; minimal bit weight for every individual full support S; any claim about full compression collisions or scores. No probabilistic conjecture is needed for the cutoff theorem or linear minima.

## Sources

[S1] NIST, FIPS 180-4, Secure Hash Standard, section 6.2.2. Public source: https://csrc.nist.gov/pubs/fips/180-4/upd1/final

[S2] User-supplied ePrint 2026/1120, *Pushing Collision Attacks on SHA-2 to 39 Steps*: recurrence at file lines 313-323; 38-step support at 367-393; 37-step support at 594-602; 39-step support and distinction between characteristic existence and attack effectiveness at 826-858. The report does not import its attack-cost estimates as schedule-minimum proofs.

[S3] User-supplied verified reference card, Table 17 message words at lines 17-20 and support at line 12. Only those inputs are reused; the old contradictory relaxation notes are not premises of this study.

All numerical results beyond those cited inputs are newly computed for this report. `data/source_index.json` identifies the supplied PDF bytes and local evidence paths.
