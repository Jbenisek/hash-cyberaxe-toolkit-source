# BLAKE3 schedule-invariant difference autocorrelation (2026-10-19)

Status: `SAMPLED-ONLY`, no score credit and no package/submission action.

## Question

The BLAKE3 message permutation has two 8-cycles.  Does choosing a nonzero
message difference constant on those cycles produce an exact or near-periodic
round difference trajectory?

The cycles, verified from the owned reference permutation, are

```
(0, 2, 3, 10, 12, 9, 11, 5)
(1, 6, 4, 7, 13, 14, 15, 8)
```

Thus the tested difference family has two 32-bit parameters.  The run used
the owned scalar BLAKE3 implementation, the fixed IV/counter/length/flags
single-block state, 32 rounds, eight deterministic trials per case, and a
single process.

## Cases

* `delta_only`: the difference is permutation-invariant, but the base message
  is a random 16-word message.  This tests the proposed weaker condition.
* `both_invariant`: both the base message and its partner are invariant, so
  the absolute round map really is the same map on every round.
* `control`: random 16-word message difference, as a control.

For each lag in `{1,2,4,8,16}` the script records centered XOR-difference
similarity, exact difference equality, exact pair-state equality, and exact
carry-signature equality.  The centered score is

```
1 - 2*HW(delta_r XOR delta_{r+lag})/512
```

so random behavior is near zero and exact repetition is one.

## Result

The latest run (after adding an explicit two-round cross-check against
`b3own.compress_full`, which printed `owned_reference_check True`) used eight
trials per case.  Across all 24 trials and all tested lags:

* exact difference repeats: `0`;
* exact pair-state repeats: `0`;
* exact carry-signature repeats: `0`.

The largest centered-difference spike was `0.144531` in `delta_only`,
`0.128906` with both messages invariant, and `0.140625` in the random
control.  The means were close to zero in every case.  Therefore this short scan found
no period candidate and no evidence that the invariant-difference family
outperforms the random control.

## Interpretation

This does not prove that no period exists.  It does establish the key
distinction needed for a valid follow-up: invariant `Delta W` alone does not
make the differential recurrence autonomous, while making the absolute
message invariant does make the value map repeat.  Even in the latter case,
the sampled trajectories did not enter a short exact cycle.

Evidence and reproducibility:

* `research/dig/b3_schedule_invariant_autocorr.py`
* command: `python research/dig/b3_schedule_invariant_autocorr.py`
* owned implementation imported by the script:
  `research/catalogue/verify_5/b3own.py`

The next meaningful test would need a solver or structured search for a
reachable pair orbit, not a larger random autocorrelation scan.  A lone
Hamming spike must not be priced as a periodic characteristic unless the
pair-state and carry signatures repeat as well.
