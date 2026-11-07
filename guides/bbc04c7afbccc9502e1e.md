# Lemma Q by a direct test of the definition on random words and on all members

Source: `research/pkg6/review/judge_misc.py`

Public SHA-256: `a4bab1a1e42ae6d4f0e02c5c70f69b0848f372cbe879d41e42f26f56cbfbd4cd`

## Purpose recorded in the source

Review helper (lens: judge). Reads proof.md only; writes review/judge_misc.txt.

Fact P as displayed, Lemma Q and Lemma A (b), (c) by exhaustion over what they quantify, the two solutions that
Section 10 prints (E1 and E3 for A and B from 6.2, R = 0, beta, tau, eps, h1, rule A), the table of the heaviest
beta (Adds = N1 * N3 / 2^83), and the tables' sums.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "fractions",
  "pathlib",
  "random",
  "re",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "say",
    "line": 21,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "ror",
    "line": 25,
    "arguments": [
      "v",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "rol",
    "line": 29,
    "arguments": [
      "v",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "G",
    "line": 33,
    "arguments": [
      "A",
      "B",
      "C",
      "D",
      "x",
      "y"
    ],
    "doc": ""
  },
  {
    "name": "solution",
    "line": 90,
    "arguments": [
      "text"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/pkg6/review/judge_common_proof.txt

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
