# ---------------- GF(2) linear algebra on python ints ----------------

Source: `research/newpaths/untried/s3-deg-idiff/symlib.py`

Public SHA-256: `c827c8b23a316eaf21f43282ef2570c30a5a7e594c2e6659c59a612454ac923a`

## Purpose recorded in the source

s3-deg-idiff scout: shared code for z-periodic (symmetric) sub-fields of the SHA3-256 r6 message families.

Embedding = research/sha3r6/lowdegree/cube_degree.py: 320-bit source u0..u4 in lanes 0-4 AND 10-14 (column parities
constant -> round 0 affine on all of U320), lane 16 constant, all other lanes 0, zero capacity; message = first 135
bytes of lanes 0..16, so byte 135 = 0x86 is the organizer's own 0x06|0x80 padding byte.
Lane 16: native 0x86<<56, or its p-periodic extension (0x86 at the top byte of every p-bit block; bytes 128..134 are
ordinary message bytes) so that the whole 1600-bit input is p-periodic in z.
Round function: organizer's round (cube_degree.rnd, vectorised); end-to-end check against
hash-smash/verifier/keccak.py sha3_256(rounds=6).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "cube_degree",
  "importlib.util",
  "numpy",
  "random",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "lane16_for",
    "line": 24,
    "arguments": [
      "p"
    ],
    "doc": "p-periodic lane 16 whose top byte is the padding byte 0x86 (p in 8,16,32); None/64 -> native."
  },
  {
    "name": "lanes",
    "line": 35,
    "arguments": [
      "u",
      "l16"
    ],
    "doc": ""
  },
  {
    "name": "unpack_src",
    "line": 44,
    "arguments": [
      "ts"
    ],
    "doc": "list of 320-bit ints -> 5 lane arrays"
  },
  {
    "name": "prechi",
    "line": 49,
    "arguments": [
      "A",
      "i"
    ],
    "doc": "theta/rho/pi of round i (no chi, no iota); returns the 25 chi-input lanes B[x+5y]"
  },
  {
    "name": "states",
    "line": 60,
    "arguments": [
      "u",
      "l16",
      "upto"
    ],
    "doc": "yield (r, A) for r = 1..upto: full 25-lane state after round r (1-indexed: after organizer round r-1)"
  },
  {
    "name": "rotl",
    "line": 68,
    "arguments": [
      "v",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "msg_bytes",
    "line": 72,
    "arguments": [
      "t",
      "l16"
    ],
    "doc": ""
  },
  {
    "name": "selfcheck",
    "line": 80,
    "arguments": [
      "l16",
      "rng",
      "npts"
    ],
    "doc": "vectorised round function on this embedding == organizer sha3_256(rounds=6) on random sources"
  },
  {
    "name": "bits_of",
    "line": 93,
    "arguments": [
      "B"
    ],
    "doc": "25 lane arrays (n,) -> uint8 bit matrix [n, 1600], position = 64*lane + z"
  },
  {
    "name": "affine_map",
    "line": 99,
    "arguments": [
      "l16",
      "stage"
    ],
    "doc": "Affine map U320 -> 1600 bits. stage='r1': state after round 1; 'chi1in': chi input of round 2 (theta/rho/pi\nof organizer round 1 applied to the round-1 output). Returns (const_int, [form_int per position]) with forms over\nthe 320 source bits (bit i of the form <-> source bit i). Valid only because round 0 is affine on U320."
  },
  {
    "name": "round0_affine_check",
    "line": 115,
    "arguments": [
      "l16",
      "rng",
      "ntrip"
    ],
    "doc": "second differences of the state after round 1 over random a,b in U320 at random base points: must be 0"
  },
  {
    "name": "sym_basis",
    "line": 129,
    "arguments": [
      "p"
    ],
    "doc": "basis of the p-periodic part of U320: e_{x,j} = all bits 64x + j + kp; index 5? -> x*p + j"
  },
  {
    "name": "restrict",
    "line": 141,
    "arguments": [
      "f",
      "basis"
    ],
    "doc": ""
  },
  {
    "name": "chi_pairs",
    "line": 149,
    "arguments": [
      "forms_r"
    ],
    "doc": "non-trivial adjacent pairs (f,g) of chi input forms: product f*g is affine on the subspace iff f=0, g=0 or f=g"
  },
  {
    "name": "rank",
    "line": 163,
    "arguments": [
      "vs"
    ],
    "doc": ""
  },
  {
    "name": "span_basis",
    "line": 175,
    "arguments": [
      "vs"
    ],
    "doc": ""
  },
  {
    "name": "annihilator",
    "line": 187,
    "arguments": [
      "Q",
      "N"
    ],
    "doc": "basis of {v in GF(2)^N : <q,v> = 0 for all q in Q}"
  },
  {
    "name": "intersect",
    "line": 212,
    "arguments": [
      "Abasis",
      "Bbasis",
      "N"
    ],
    "doc": "basis of span(A) cap span(B) in GF(2)^N via annihilators"
  },
  {
    "name": "combine",
    "line": 218,
    "arguments": [
      "coef",
      "basis"
    ],
    "doc": ""
  },
  {
    "name": "rot_src",
    "line": 228,
    "arguments": [
      "t",
      "r"
    ],
    "doc": "rotate each of the 5 source lanes of a 320-bit source by r"
  },
  {
    "name": "hitting_greedy",
    "line": 239,
    "arguments": [
      "pairs",
      "rng",
      "slack"
    ],
    "doc": "Find a small subspace Q (list of ints) of the dual such that every pair (f,g) has f, g or f^g in span(Q).\nThen V = annihilator(Q) is a subspace on which every chi product f*g is affine (per-row test).\nGreedy maximum coverage, random tie-break among candidates within `slack` of the best count.\nPair values are kept as canonical representatives modulo span(Q) (pivot = leading bit)."
  },
  {
    "name": "check_pairs_on",
    "line": 267,
    "arguments": [
      "pairs",
      "Vcoef"
    ],
    "doc": "count pairs whose restriction to span(Vcoef) is not dependent (should be 0)"
  }
]
```

## Read alongside

- research/newpaths/untried/s3-deg-idiff/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
