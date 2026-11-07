# build all8

Source: `research/blake3_r6/b9r6/build_all8.py`

Public SHA-256: `6d0165ed10965ecd5e5248a36bec721bdafe6859f55c500fca725d74d1a56cc2`

## Purpose recorded in the source

Builds proof.md, claim.json, experiments/manifest.json, submission-note.md, dependencies.json of the blake3-r6 entry (rolled round body, ported from B3R7c) from the program's own numbers.
Run:  python -B build_all.py   (after stats_out.txt, appA.out, organizer_summary.txt, gen_c/cport.json exist).

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
    "line": 146,
    "arguments": [
      "text",
      "label"
    ],
    "doc": ""
  },
  {
    "name": "span",
    "line": 160,
    "arguments": [
      "head",
      "nxt"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/blake3_r6/b9r6/proof_t8.md
- research/blake3_r6/b9r6/proof_t8_pre9.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
