# u9 topform factor

Source: `research/poseidon/levels/U9/u9_topform_factor.py`

Public SHA-256: `a5e041a9006af86b1ca626894e175cf69479217862dff8c946dc6e11c30aac79`

## Purpose recorded in the source

U9 Q5 (real field): factor the top forms Phi_k(z) (z=U/V, U=X^5, V=Y^5) of lane 0 after each round up to formal degree 625 over F_p.
Also tests the proportionality claim: after the first partial round all three lanes' top forms are scalar multiples of ONE polynomial, and stay so through the full rounds that follow, so the output top form = c * Phi_R3,0 ^ (5^(rounds after R3)) (a perfect power).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "sys",
  "u9lib"
]
```

## Read alongside

- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
