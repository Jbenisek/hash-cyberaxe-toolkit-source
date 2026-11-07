# waits for w_run.sh, then re-runs cycle.sh with SIM_EXTENT = the run's own arena extent (cached run), copies the package and stages slot POSR3G (no submit)

Source: `research/poseidon/orchard/exec_r3t21/w_finish.sh`

Public SHA-256: `ea2c8395eb453a7251ad9ec91e5a4e552296faed7c3f04054b8b48210fa66bef`

## Purpose recorded in the source

waits for w_run.sh, then re-runs cycle.sh with SIM_EXTENT = the run's own arena extent (cached run), copies the package and stages slot POSR3G (no submit)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/orchard/exec_r3t21/proof_template_exec.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
