# build package

Source: `research/poseidon/orchard/lean_r1_fix/build_package.py`

Public SHA-256: `c0964e03961853c2c9ca4a19c6acb20163f661d7ab7d6961ee79c85eda7dd947`

## Purpose recorded in the source

Assemble the candidate folder (claim.json, proof.md, certificates/, experiments/) in pkg_stage/ from the ledger run,
the campaign statistics and the stored collisions.  Every number in proof.md and claim.json is computed here.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "math",
  "os",
  "re",
  "shutil",
  "subprocess",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "L",
    "line": 13,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "extract",
    "line": 17,
    "arguments": [
      "fn",
      "sig"
    ],
    "doc": ""
  },
  {
    "name": "appendix",
    "line": 31,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "stages",
    "line": 50,
    "arguments": [
      "block"
    ],
    "doc": ""
  },
  {
    "name": "ceil3",
    "line": 104,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "xcheck_text",
    "line": 124,
    "arguments": [
      "per_step_arith"
    ],
    "doc": ""
  },
  {
    "name": "ln",
    "line": 179,
    "arguments": [
      "prefix"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/poseidon/orchard/lean_r1_fix/proof_template.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
