# ---- the outcomes

Source: `research/pkg8/pkg/review/judge_counts.py`

Public SHA-256: `e2bcc80bb6e0ad38d948b9d7ceac594fd07caa1b5b81a06dc4119e78a1d19333`

## Purpose recorded in the source

Review helper (lens: judge). Reads only; writes review/judge_counts.txt.

Recomputes, from the files in evidence/ and with exact fractions, the figures of the count that the text prints:
the count of all solutions, its parts per beta, the conservative count per rule (an outcome is kept only if all
three solver files say that no solution violates the rule, and its beta holds no estimate), the comparison with
the recount of the other model beta by beta, and it evaluates every model that the solver files print in plain
arithmetic (E3 for A and B from the definitions of proof 6.2). Also the arithmetic of Sections 7 and 8 and the
figures of the long self-test.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "fractions",
  "json",
  "math",
  "pathlib",
  "re",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "say",
    "line": 28,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "ror",
    "line": 32,
    "arguments": [
      "v",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "e3",
    "line": 36,
    "arguments": [
      "a",
      "y4",
      "y9",
      "h1",
      "w8"
    ],
    "doc": "E3 = G(a, Y4, Y9, Y14; 0, w8) with its second value h1 given: returns (e1, f1, e2, h2, g2, f2)."
  },
  {
    "name": "rule",
    "line": 48,
    "arguments": [
      "h1",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "is_solution",
    "line": 58,
    "arguments": [
      "tau",
      "eps",
      "y4",
      "h1",
      "y9",
      "w8"
    ],
    "doc": "The E3 system of an outcome: Y4 in the class, and the differences psi, eps, tau (and eta, by the class)."
  }
]
```

## Read alongside

- research/pkg8/pkg/review/judge_common_proof.txt

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
