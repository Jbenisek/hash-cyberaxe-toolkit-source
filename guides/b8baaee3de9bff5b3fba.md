# step 0: R4 check

Source: `research/poseidon/levels/U9/u9_toplayers.py`

Public SHA-256: `5f8a9f4203b1656eea092d9f7f463470034db59887705a5a146a492084c3939e`

## Purpose recorded in the source

U9 Q2/Q5: the TOP s+1 homogeneous layers (total degree D, D-1, ..., D-s) of the (A,B)-polynomials at every later round.
Constants only enter at degree 0, i.e. at layer k=D > s, and lanes 1,2 of a partial round are lower degree by a factor 5, so for D large:
   output top layers (A,B coords) = kappa * (top layers of lane 0 after R3)^(5^n), n = 5 (r=1) or 6 (r=2)  (S-box layers R4, [R5,] R60..R63).
Series in y (layer index) whose coefficients are dehomogenised polynomials in x=A/B. Truncate y^(s+1).
Step 0 verifies the shortcut against the exact bivariate lanes at R4 (D=625). Then reports zero coefficients per layer of the final output.
usage: python u9_toplayers.py s r

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

## Entry points

```json
[
  {
    "name": "layers_of",
    "line": 15,
    "arguments": [
      "f",
      "D",
      "s"
    ],
    "doc": ""
  },
  {
    "name": "smul",
    "line": 22,
    "arguments": [
      "a",
      "b"
    ],
    "doc": ""
  },
  {
    "name": "spow5",
    "line": 31,
    "arguments": [
      "a"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
