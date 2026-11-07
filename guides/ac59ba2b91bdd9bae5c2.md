# build all8

Source: `research/blake3_r7/b8/build_all8.py`

Public SHA-256: `0e8a36b5be7366c7f739c0ad5070bfd52fe8ba1e1f9f453ed85eeb69a083d79b`

## Purpose recorded in the source

Builds proof.md, claim.json, experiments/manifest.json, submission-note.md, dependencies.json of the blake3-r7 entry B3R7b (rolled round body) from the program's own numbers.
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
  "string",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "need",
    "line": 121,
    "arguments": [
      "text",
      "label"
    ],
    "doc": ""
  },
  {
    "name": "span",
    "line": 135,
    "arguments": [
      "head",
      "nxt"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/blake3_r7/b8/proof_t8.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
