# lane bound

Source: `research/pkg7/tools/lane_bound.py`

Public SHA-256: `ac01f051de14bac65c2335919811b480b231267d5ced430b67959d40ba900450`

## Purpose recorded in the source

Largest lane value of every SUM of the two-stage batch of pkg6, per part, for ALL inputs, by interval arithmetic.

The self-test of the program reports the largest lane of a sum that occurred in its random cases. This tool runs
the same function packed_batch of experiments/halfsearch.py on a second machine that holds, for every register,
not a value but an upper bound of its lanes, and so gives a bound that holds for every context and every member:

  - a loaded word whose lanes are below 2^32 (a constant of the batch, a list word) counts as 2^32 - 1 in every
    lane, whatever its value; the word "bit 32" and the two counters are taken as they are;
  - a sum is bounded by the sum of the bounds of its operands;
  - an XOR is bounded bit by bit: below 2^32 it can be anything, above bit 31 it has at most the bits that one of
    the operands can have;
  - an AND with a loaded constant is bounded by the largest lane of that constant, a shift by 2^36 - 1 (bits of the
    neighbouring lane come in; every shift of the batch is followed by an AND with a loaded mask);
  - an OR is bounded by the all-ones word of the longer operand.

It prints, per part, the largest bound of a sum in units of 2^32 next to the bound of the program's TABLE, the
largest bound of all, and the largest bound of a word that enters the flag computation (it must be below 2^32).
It then runs the program's own machine on random batches and checks that every sum that occurs is at most the
bound found here. Nothin

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "importlib.util",
  "pathlib",
  "random",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "load",
    "line": 37,
    "arguments": [
      "path",
      "name"
    ],
    "doc": ""
  },
  {
    "name": "units",
    "line": 120,
    "arguments": [
      "top"
    ],
    "doc": "A bound written as q * 2^32 - r."
  },
  {
    "name": "main",
    "line": 126,
    "arguments": [],
    "doc": ""
  }
]
```

## Read alongside

- research/pkg7/tools/proof_lines_check.py
- research/pkg7/tools/proof_lines_pkg7.py

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
