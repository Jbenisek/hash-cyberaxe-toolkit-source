# nb_verify_nature_0 - recompute the numbers behind NATURE.md row 11 (kinetic proofreading):

Source: `research/newpaths/nb_verify_nature_0/stage_math.py`

Public SHA-256: `21ca48759519e93d70bad1b5dde7efbd72fd4d5d8a9ae7b0426fbf0c8eaec0ec`

## Purpose recorded in the source

nb_verify_nature_0 - recompute the numbers behind NATURE.md row 11 (kinetic proofreading):
"already the leaders' stage A / stage 2 with rule A; cost factor only; at most 0.77 bit left; projected 90.8".
Sources: research\pkg10\pkg\blake3-r2\proof.md section 8 (ledger), 6.5 (part table), 2302-2317 (c1 split);
         END_OF_LINE.md 3.1; rivals\since_2100Z\93.5891_Subflatus3_ef81f589.md (leader ledger).
proof.md 8: T <= charge*N*(1+2^-7)/430 + 2^81 ; claim = that, rounded up to 2 decimals

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "fractions",
  "math",
  "numpy"
]
```

## Entry points

```json
[
  {
    "name": "tlog",
    "line": 13,
    "arguments": [
      "charge",
      "N"
    ],
    "doc": ""
  },
  {
    "name": "with_price",
    "line": 44,
    "arguments": [
      "price"
    ],
    "doc": ""
  }
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
