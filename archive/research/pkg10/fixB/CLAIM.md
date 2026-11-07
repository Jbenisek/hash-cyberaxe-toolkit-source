# claim.json changes for fix 4 (selection preprocessing)

## 1. The figure

`claim.preprocessing_log2`: 63 -> **80**.

SEL (SECTION9.md) costs fewer than 2^88.45 primitive operations, which is
below 2^79.71 target-compression units; 80 is that bound rounded up.

## 2. Passages of claim.json that say the selection is unbounded or estimated

Only one: in `restrictions[5]` (the restriction that begins "Six 32-bit
constants, the word eta ..."). A search of claim.json for "estimate", "not
bounded", "preprocess", "2^60" and "selection" finds nothing else; the
heuristics H1 to H3 say nothing about the cost of the selection.

Old passage (verbatim):

> The constants were found by a participant's solver search and chosen by a
> participant's count of the solutions of a seven-word system; the sub-class and
> rule A were proposed by another AI model (GPT Sol 6.1) from exact counts of
> the same kind, which the participant's counter reproduces. preprocessing_log2
> 63 bounds only the recomputation of the two pinned message words at the four
> given inputs; the selection of the constants, the sub-class and the rule is
> not bounded, and its work is the participant's estimate (below 2^60
> operations). memory_log2_bytes 35 covers the memory of that selection as
> observed by the participant; the search itself needs less than 2^23 bytes.

Replacement (one JSON string, no line breaks; wrapped here only for reading):

> The constants were found by a participant's solver search and chosen by a
> participant's count of the solutions of a seven-word system; the sub-class and
> rule A were proposed by another AI model (GPT Sol 6.1) from exact counts of
> the same kind, which the participant's counter reproduces. preprocessing_log2
> 80 bounds the selection procedure of proof.md Section 9, in which every search
> runs over a stated range and every program run halts at a stated cap of
> operations and at 2^34 bytes: 116 capped solver runs and a count for each
> solver set give the six constants and eta; the exact rate of every member of
> the class, and from it of every sub-cube, the exact mass of every rule of
> eight affine conditions on sixteen bits of h1, and the yield of every set of
> at most six flips with every gate that rule A implies are computed, and the
> stored sub-class, rule A, flips and gate are among these candidates, named by
> the stored bytes. The procedure costs fewer than 2^88.45 operations, below
> 2^80 units, whatever its programs return; that it returns the stored
> constants rests on the participant's solver log and counts, and its steps for
> the sub-class, the rule and the flips have not been run. Choosing a sub-class
> from the rate of every member follows winglock (entries 2125212 and
> 2bb5d604). memory_log2_bytes 35 bounds the memory of that procedure and of
> the search, which needs less than 2^23 bytes.

The rest of `restrictions[5]` (the first sentence on the 48 bytes of advice,
and the sentences on priority, Section 11 and Section 13) stays as it is.

## 3. Effect on time_log2

Formula, as asked: new total = existing total + 2^80 units, so

    new time_log2 = log2(2^T0 + 2^80) = T0 + log2(1 + 2^(80 - T0)),

where T0 is the exact exponent of the existing total before rounding.

- Current package: the existing bound is 2^92.5714 + 2^64 (Section 8). With
  2^80 added: log2(2^92.5714 + 2^64 + 2^80) = 92.57164. The claim stays
  **92.58**. If the 2^63 and the 2^60 terms are dropped as in companion edit C
  of SECTION9.md, the bound is 2^92.5714 + 2^81 < 2^92.5719, still 92.58.
- In general the increase is below 1.4427 * 2^(80 - T0): +0.00024 at
  T0 = 92.5714, below 0.00036 for any T0 >= 92, below 0.0056 for T0 >= 88.
- Room: the claim 92.58 holds for any added term up to
  2^92.58 - 2^92.5714 = 2^85.18 units, so the 2^80 of SEL uses about 1/36 of
  that room. If fix A or fix C raises T0, recompute with the formula above.

## 4. How the leading entries bound the same selection (read-only, by HTTPS)

All three declare preprocessing_log2 = 86, memory_log2_bytes = 100 and
nonuniform_advice_log2_bytes = 6, and none gives an algorithm or a range.

- 1d5e54ce (Subflatus3, 94.167, commit 27d987aa), proof Section 9,
  "Preprocessing (declared charge)": the stored values are the six constants of
  Fact P, eta, the rule-A, filter and stage-test words and the S8 conditions.
  Constants "found by c66f230d with solver searches and chosen with model
  counts"; rule A, S8 and the filter "chosen with counts of the same kind (S8
  by winglock from the exact per-member factors of all 524,288 class members,
  best of 8,992,320 candidate sub-classes)". "This work is not reconstructed
  from run records. A declared upper bound of 2^86 units (2^94.75 word
  operations) is charged for all of it", argued as more than 2^34 times our
  own estimate below 2^60 and more than 2^3.5 times ten years at 2^63
  operations a second (over four times the fastest listed supercomputer), "so
  it exceeds any computation physically performed for this selection before
  the submission date. This is a declared upper-bound charge, not a premise."
  Adds 0.0050 to its scalar. Memory 100: every stored byte is written by a
  charged operation, 32 * 2^94.75 = 2^99.75 bytes.
- 2125212 (winglock, 94.1982, commit 1d0dbe58): the same text and the same
  2^86, covering the selections of c66f230d, 60f94c5c, 52bb50ee, 5266c5ce and
  its own; adds 0.0049.
- 2bb5d604 (winglock, 96.75, commit 124a032b): the same, 2^86, "instead of
  2^88" in its previous version d26a3c5f; adds 0.0009; also states 2^5.9 times
  the measured 2^60.6 of the fastest supercomputer.
- What fix 4 takes from them: the choice of a sub-class from the exact rate of
  every member of the class (winglock, 2125212 and 2bb5d604), credited in
  step 4 of SECTION9.md and in companion edit F. The declared-charge argument
  is not used: SEL is an algorithm whose cost is bounded by its ranges and
  caps.
