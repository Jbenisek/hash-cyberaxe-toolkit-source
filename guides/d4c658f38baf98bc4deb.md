# tiny expression AST: ("w", name) | ("c", int) | ("neg", e) | ("mul", k, e) | ("add", [e]) | ("xor", [e]) | ("rol", k, e)

Source: `research/fifties/combos/solvers-GROK-R3/smt_inst.py`

Public SHA-256: `26b1e3182a03079d44dbe0a7348bf005c062a8773c71d4e8c49cd64ef6b15885`

## Purpose recorded in the source

R3 (medium confidence): word-level SMT (z3, QF_BV) on one split-point inversion of BITS.md section 1.
Closure G = (C0.a1, C0.b1, C1.a1, D3.a1) as four free 32-bit vars; the 8 split-point coordinates fixed to a real
ctr_outer point (generated as pkg13/mitm/bits/verify.py does: random.Random(seed), rels.point); the other 75 words built
by the triangular reconstruction (core.prop_order) as define-fun terms (bvadd / bvneg / bvxor / rotate_left); the 4
leftover relations asserted as checks.  Variants written:
  inst_true   : free guess words                         (expected sat, exactly 1 solution per BITS.md 5)
  ctl_pinned  : guess words fixed to the true values      (control 1: must be sat at once)
  ctl_bad     : true guess words with bit 0 of C0.a1 flipped, the sttest.py/tocnf.py corruption (control 2: unsat)
  part_bNN    : low NN bits of each guess word free, rest fixed to truth (4*NN free bits; scaling curve)
Also self-tests the term construction in Python against ctr_outer values and the real ctr_outer round-trip.
Usage: python smt_inst.py [seed] [index]   (index = which point of the seeded stream; default seed 99 index 0)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "core",
  "halfsearch",
  "json",
  "os",
  "random",
  "rels",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "ev",
    "line": 23,
    "arguments": [
      "e",
      "v"
    ],
    "doc": ""
  },
  {
    "name": "smt",
    "line": 36,
    "arguments": [
      "e"
    ],
    "doc": ""
  },
  {
    "name": "scaled",
    "line": 49,
    "arguments": [
      "x",
      "c"
    ],
    "doc": ""
  },
  {
    "name": "definitions",
    "line": 54,
    "arguments": [],
    "doc": "triangular reconstruction: list of (word, expr in earlier words)"
  },
  {
    "name": "check_exprs",
    "line": 71,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "write",
    "line": 83,
    "arguments": [
      "path",
      "v",
      "defs",
      "chks",
      "pin",
      "lowfree",
      "flip"
    ],
    "doc": ""
  },
  {
    "name": "make",
    "line": 100,
    "arguments": [
      "seed",
      "index",
      "stem",
      "parts"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/fifties/combos/solvers-GROK-R3/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
