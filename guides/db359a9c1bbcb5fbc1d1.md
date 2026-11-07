# d4export

Source: `research/fifties/perspectives/data/d4export.py`

Public SHA-256: `d92f948444ba84dd771167663a1f6b827c08e7be63e0892993fa5670539296cf`

## Purpose recorded in the source

Export the residual words of the D4 partial constructions in fifties/d4_local/dump_*.bin (read-only).

No completed D4 construction exists (d4_local/RESULT.md); the 1,577 dumped records each have one solved diagonal.
For every record, with the ORGANIZER blake3.py (_g traced, cross-checked against _compress, rounds=2):
  D0..D3  = (XA[k+12] ^ (XA[k]+XA[k+4]+m1A[2k])) ^ (same for B)   (verify_organizer.py formula; the D4 residual checks)
  digest A, digest B (8 words each), their XOR (8 words), and the solved-diagonal checks (b,c equal; S_k = 0).
Output d4/d4_partial.u32, 76 u32 per record:
  arm (0 none, 1 len, 2 flags), seed, record index in its file, flags, D0..D3, dXOR[8], digA[8], digB[8],
  mA[16], mB[16], hA[4], hB[4], e[4] (the C program's stored D values; meaningful only when flags bit 8 is set)
and d4/d4_partial.csv (arm, seed, idx, flags, D0..D3, dXOR0..7 in hex).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "glob",
  "importlib.util",
  "os",
  "struct",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "trace",
    "line": 27,
    "arguments": [
      "words",
      "h"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 43,
    "arguments": [],
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
