# mkroll8 scripts

Source: `research/blake3_r7/mkroll8_scripts.py`

Public SHA-256: `598eedd23ff70edb5664794da9b185b8e307bc1e92f1304b0373be03b5f64342`

## Purpose recorded in the source

Writes the run scripts of research/blake3_rR/b8rR (tm_run, stage_pre, stage_run, bld, rc_run) and org_summary_b8.py.  usage: python3 -B mkroll8_scripts.py R

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "os",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "w",
    "line": 6,
    "arguments": [
      "f",
      "t"
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
