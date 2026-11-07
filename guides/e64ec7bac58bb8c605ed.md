# math sat

Source: `research/pkg5/review/math_sat.py`

Public SHA-256: `414ec88435e19c89093efa127143d74bb452d72f5d8e7324b6cd16742ce27cee`

## Purpose recorded in the source

Reviewer check, lens MATHEMATICS AND COST, part (a): rule A against the solutions of the E3 side, per outcome.

Nothing of the package's encoder (research/r2_sat.py) or of tools/rule_a_sat.py is imported. The CNF is written
here, gate by gate, from proof.md 6.2 and Section 10, in a formulation that differs from the package's:

    unknowns Y4, h1, Y9, w8 (h1 = second value of E3 on the 60-byte message A)
    e1 = Y3 + Y4, e1' = Y3' + Y4          (Y3, Y3' computed here with G from the six constants of 3.2)
    class by its definition:  e1 XOR e1' = ROL(eta, 16)
    Y14 = ROL(h1,16) XOR e1,  h1' = ROR(Y14 XOR e1', 16)
    E3 on both messages to all four outputs e2, f2, g2, h2
    R = 0 for an E1 with (beta, tau, eps):   g2^g2' = tau,  e2^e2' = eps,  f2^f2' = ROR(tau,8),
                                             h2^h2' = ROR(beta XOR eps, 7)
(the package forces the first-half difference psi instead of the b and d output differences).

    math_sat.py run MODE SOLVER THREADS [LIMIT]   MODE violate | all | keep ; SOLVER cadical | kissat | cms
                                                  -> review/math_sat_<MODE>_<SOLVER>.txt
    math_sat.py count                             rebuilds the count that the claim uses from my own answers
Outcomes: every OUT line of review/math_calc2_mass.txt (my own run of the calculator binary) with a nonzero E1.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "concurrent.futures",
  "math",
  "os",
  "pathlib",
  "subprocess",
  "sys",
  "time"
]
```

## Entry points

```json
[
  {
    "name": "ror",
    "line": 39,
    "arguments": [
      "v",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "rol",
    "line": 43,
    "arguments": [
      "v",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "G",
    "line": 47,
    "arguments": [
      "a",
      "b",
      "c",
      "d",
      "x",
      "y"
    ],
    "doc": ""
  },
  {
    "name": "rule_a",
    "line": 60,
    "arguments": [
      "h1"
    ],
    "doc": ""
  },
  {
    "name": "const",
    "line": 109,
    "arguments": [
      "v"
    ],
    "doc": ""
  },
  {
    "name": "bror",
    "line": 113,
    "arguments": [
      "bits",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "brol",
    "line": 117,
    "arguments": [
      "bits",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "build",
    "line": 121,
    "arguments": [
      "beta",
      "tau",
      "eps",
      "mode"
    ],
    "doc": ""
  },
  {
    "name": "plain",
    "line": 155,
    "arguments": [
      "beta",
      "tau",
      "eps",
      "y4",
      "h1",
      "y9",
      "w8"
    ],
    "doc": "The model in 32-bit arithmetic: E3 of 6.2 on both messages from Y14, and the four digest-word conditions."
  },
  {
    "name": "solve",
    "line": 169,
    "arguments": [
      "args"
    ],
    "doc": ""
  },
  {
    "name": "outcomes",
    "line": 193,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "run",
    "line": 205,
    "arguments": [
      "mode",
      "solver",
      "threads",
      "limit"
    ],
    "doc": ""
  },
  {
    "name": "count",
    "line": 221,
    "arguments": [],
    "doc": "The count the claim uses, from my answers; and my answers against the package's file."
  }
]
```

## Read alongside

- research/pkg5/review/fig_diff_manifest.txt
- research/pkg5/review/fig_diff_proof.txt
- research/pkg5/review/math_proof.txt
- research/pkg5/review/fig_schema.py
- research/pkg5/review/math_proof.py
- research/pkg5/review/math_proof.sh

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
