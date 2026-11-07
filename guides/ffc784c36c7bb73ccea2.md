# ---------------------------------------------------------------- 1 generator

Source: `research/blake3_r3/bitslice/bitslice.py`

Public SHA-256: `54e50539ea55cadbd5675668a89e2bd56eb2ff94bafb457d22d9d638ec1e5586`

## Purpose recorded in the source

256-lane bit-sliced 3-round BLAKE3 chain step (blake3-r3-prefix-v1), run-time generator in the style of rho.py's Tracer.

A plane is a 256-bit integer: bit l of plane j is bit j of the chain value of lane l.  A 32-bit word is 32 planes, so
rotations are renaming (no operation), XOR/AND/OR are one operation each, an add is a ripple of full adders.
The chain input is the 256 digest planes of the previous step (low n planes; planes >= n are the constant 0), so the chain
feed is renaming too.  Signals carry a polarity bit (stored plane = true plane xor all-ones if neg); the input polarity
vector is iterated to a fixed point so that the step needs no NOT operations: the stored output plane j has the same
polarity as the stored input plane j.

Sections: 1 gate generator and straight-line emitter, 2 analysis (op count, peak live, spill_ops(R)), 3 lane packing,
4 validation against the scalar chain (rho.py).  Run: python bitslice.py [--validate] [--analyse]

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "bisect",
  "os",
  "random",
  "rho",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "ror",
    "line": 91,
    "arguments": [
      "A",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "constw",
    "line": 95,
    "arguments": [
      "v"
    ],
    "doc": ""
  },
  {
    "name": "trace",
    "line": 99,
    "arguments": [
      "n",
      "pin",
      "rounds"
    ],
    "doc": "Build the network for the digest of 0^32 || x (x = low n bits of the input planes, the rest 0)."
  },
  {
    "name": "trace_stats",
    "line": 124,
    "arguments": [
      "g",
      "out",
      "n"
    ],
    "doc": "Operation nodes reachable from the low n output planes, in creation (program) order."
  },
  {
    "name": "find_pin",
    "line": 134,
    "arguments": [
      "n",
      "iters",
      "seed",
      "rounds"
    ],
    "doc": "Hill climb on the input polarity vector minimising gates + NOT fixes (output planes whose polarity differs from the\ninput plane they feed).  Zero fixes is not reachable (the polarity map does not settle); about 125 remain at n = 256."
  },
  {
    "name": "pack_lanes",
    "line": 272,
    "arguments": [
      "xs",
      "n",
      "pin"
    ],
    "doc": "Stored input planes (low n) for up to 256 lane values (n-bit integers); missing lanes are 0."
  },
  {
    "name": "lane_value",
    "line": 283,
    "arguments": [
      "planes",
      "l",
      "pol",
      "n"
    ],
    "doc": "The n-bit chain value of lane l from n stored planes with polarity pol."
  },
  {
    "name": "set_lane",
    "line": 291,
    "arguments": [
      "planes",
      "l",
      "x",
      "pol",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "digest_int",
    "line": 297,
    "arguments": [
      "out_planes",
      "pol",
      "l",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "validate",
    "line": 301,
    "arguments": [
      "st",
      "lanes_total",
      "steps",
      "seed"
    ],
    "doc": "Compare the bit-sliced step with the scalar chain f (rho.f_scalar) on lanes_total random lanes; steps > 1 chains\nthe steps with the feed by renaming.  Returns (ok, lanes checked, chained steps)."
  },
  {
    "name": "validate_full_digest",
    "line": 319,
    "arguments": [
      "st",
      "lanes_total",
      "seed"
    ],
    "doc": "n = 256 only: all 256 digest bits against rho.digest_words (the 3-round digest of 0^32 || x)."
  }
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
