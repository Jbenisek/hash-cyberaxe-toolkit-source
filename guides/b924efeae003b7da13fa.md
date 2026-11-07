# ---------------------------------------------------------------- scalar

Source: `research/dig/incoming3/blake3-r3-U46/work/b3scan.py`

Public SHA-256: `0d624c1ce38121bc8faa17f0874aa4bf69c2e3fc5110b33d0c452e32697e14e6`

## Purpose recorded in the source

b3scan.py - own tools for the blake3-r3 dig (units U46-U54).
1. scalar BLAKE3 compress, written from the spec, with skip/override hooks;
2. a tracer of the packed circuit (same rules as research/blake3_r3/candidate_blake3/experiments/rho.py, rewritten
   here), with per-step op attribution, variants (pitch, lanes, mask policy, skipped steps, message-word modes) and an
   optional numpy 'real' mode that keeps the unreduced lane values;
3. validation: 7-round vectors and verifier blake3.py, 3 rounds, packed circuit vs scalar.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "collections",
  "hashlib",
  "json",
  "math",
  "numpy",
  "os",
  "rho",
  "struct",
  "sys",
  "verifier.blake3"
]
```

## Entry points

```json
[
  {
    "name": "ror",
    "line": 20,
    "arguments": [
      "v",
      "k"
    ],
    "doc": ""
  },
  {
    "name": "digest_words",
    "line": 25,
    "arguments": [
      "m",
      "rounds",
      "flags",
      "blen",
      "counter",
      "skip",
      "mover"
    ],
    "doc": "skip = set of (round, call, quarter) steps left out; mover = {word index: replacement value}"
  },
  {
    "name": "word_positions",
    "line": 51,
    "arguments": [
      "rounds"
    ],
    "doc": "for each original message word: list of (round, call, 'x'|'y')"
  },
  {
    "name": "build",
    "line": 162,
    "arguments": [
      "words",
      "skip",
      "policy",
      "pitch",
      "lanes",
      "swar",
      "rounds",
      "inputs",
      "mover",
      "final_mask"
    ],
    "doc": "words: dict original word index -> 'z' (zero const), 'v' (variable), or int (nonzero constant).\ndefault: 0..7 zero, 8..15 variable. inputs: dict word -> uint64 numpy array (real mode)."
  },
  {
    "name": "rho",
    "line": 215,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "time_log2",
    "line": 224,
    "arguments": [
      "ph"
    ],
    "doc": ""
  },
  {
    "name": "rand_inputs",
    "line": 235,
    "arguments": [
      "n",
      "seed"
    ],
    "doc": ""
  },
  {
    "name": "check_vs_scalar",
    "line": 240,
    "arguments": [
      "tr",
      "inputs",
      "n",
      "rounds",
      "skip",
      "words",
      "nchk"
    ],
    "doc": "compare the real-mode outputs of the traced variant with the scalar function using the same variant"
  },
  {
    "name": "avalanche",
    "line": 258,
    "arguments": [
      "words",
      "skip",
      "n",
      "seed"
    ],
    "doc": "mean number of digest bits (of 256) that differ between the full 3-round function and the variant"
  },
  {
    "name": "validate",
    "line": 280,
    "arguments": [],
    "doc": ""
  }
]
```

## Read alongside

- research/dig/incoming3/D414-SHA3-R6-141-PROOF-ERRATA-20261014.json
- research/dig/incoming3/D415-SHA3-R6-141-PROOF-REFRESH-DRAFT-20261014.json

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
