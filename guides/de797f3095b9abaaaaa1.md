# build all9

Source: `research/blake3_r7/b9v3/build_all9.py`

Public SHA-256: `62d8b4f6dae0bd8cc20d4f2c1e609f106689d6a0b79018afad53daf63e039493`

## Purpose recorded in the source

Builds proof.md, claim.json, experiments/manifest.json, submission-note.md, dependencies.json of the blake3-r7 entry B3R7d (rolled round body) from the program's own numbers.
Run:  python -B build_all9.py   (after stats_out.txt, appA.out, organizer_summary.txt, gen_c/cport.json exist).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "bsrho",
  "json",
  "math",
  "os",
  "re",
  "string",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "need",
    "line": 141,
    "arguments": [
      "text",
      "label"
    ],
    "doc": ""
  },
  {
    "name": "span",
    "line": 155,
    "arguments": [
      "head",
      "nxt"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/blake3_r7/b9v3/proof_t8.md
- research/blake3_r7/b9v3/proof_t9.md
- research/blake3_r7/b9v3/mk_proof9.py

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
