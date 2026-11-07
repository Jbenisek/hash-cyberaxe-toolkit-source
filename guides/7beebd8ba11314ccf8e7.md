# build all

Source: `research/blake3_r5/bsel/build_all.py`

Public SHA-256: `305c557b36e3ee9f5c023070236d155cfd36693cfc4fca5b581675b58ff1e01f`

## Purpose recorded in the source

Builds proof.md, claim.json, experiments/manifest.json, submission-note.md, dependencies.json of the blake3-r5 entry B3R5sel (straight-line step, select-gate full adders) from the program's own numbers.
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
    "line": 150,
    "arguments": [
      "text",
      "label"
    ],
    "doc": ""
  },
  {
    "name": "span",
    "line": 164,
    "arguments": [
      "head",
      "nxt"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/blake3_r5/bsel/proof_t.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
