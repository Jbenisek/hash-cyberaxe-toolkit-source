# fw check

Source: `research/poseidon/orchard/exec_r5u/test/fw_check.py`

Public SHA-256: `dd281904f2efe7bc4522fb4f1ef819e359452c5f0287c34c149ae4cde2405d5a`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "os",
  "poseidon_ref",
  "sys"
]
```

## Read alongside

- research/poseidon/orchard/exec_r5u/proof_template_exec.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
