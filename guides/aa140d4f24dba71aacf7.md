# analyze stats

Source: `research/poseidon/orchard/lean_r2/analyze_stats.py`

Public SHA-256: `4fa0442ffa189a7e3242854761984899c73a1cf06f19c7247c33262f300622c2`

## Purpose recorded in the source

Summary of the single-centre campaign (data/stats.json by collect.py) against the Poisson(1/2) root-count model.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "math",
  "os"
]
```

## Read alongside

- research/poseidon/orchard/lean_r2/proof_template.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
