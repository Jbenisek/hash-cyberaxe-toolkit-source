# fh

Source: `research/poseidon/certb_fast/tests/fh.py`

Public SHA-256: `735815198ee7c8eb64b99826322fae00bba414b45a1fc7e30690a92331bfc126`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "flint",
  "json",
  "os",
  "random",
  "subprocess",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "write_poly",
    "line": 8,
    "arguments": [
      "path",
      "coeffs"
    ],
    "doc": ""
  },
  {
    "name": "read_poly",
    "line": 11,
    "arguments": [
      "path"
    ],
    "doc": ""
  },
  {
    "name": "to_poly",
    "line": 14,
    "arguments": [
      "coeffs"
    ],
    "doc": ""
  },
  {
    "name": "coeffs",
    "line": 15,
    "arguments": [
      "poly"
    ],
    "doc": ""
  },
  {
    "name": "run_wsl",
    "line": 18,
    "arguments": [
      "args",
      "log"
    ],
    "doc": "run certb_fast via a script file; args: list of strings with paths relative to certb_fast (WSL view)"
  },
  {
    "name": "rand_poly",
    "line": 24,
    "arguments": [
      "rng",
      "d",
      "monic"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/poseidon/certb_fast/README.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
