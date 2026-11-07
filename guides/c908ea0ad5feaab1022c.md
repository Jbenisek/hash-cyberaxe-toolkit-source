# usage: wsl_run.sh <script-in-this-dir> args...   (runs inside WSL with cwd = this directory)

Source: `research/poseidon/orchard/single_r1_mem/wsl_run.sh`

Public SHA-256: `7ad1c43e02b3ba409c448364e570a9c98f7103a7a0155f02e80845194df965d5`

## Purpose recorded in the source

usage: wsl_run.sh <script-in-this-dir> args...   (runs inside WSL with cwd = this directory)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
