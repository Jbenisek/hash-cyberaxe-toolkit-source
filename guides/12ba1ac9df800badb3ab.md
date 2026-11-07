# Put the staged candidate (pkg_stage_exec/) into its own copy of the clone and run the organizer's mechanical checks. Nothing is submitted;

Source: `research/poseidon/orchard/single_r1_exec7/stage_pkg.sh`

Public SHA-256: `d55bea3568e3f1b7a6bc35d1ffe67bd89a65087a687172cd4a1615780e4b954f`

## Purpose recorded in the source

Put the staged candidate (pkg_stage_exec/) into its own copy of the clone and run the organizer's mechanical checks. Nothing is submitted;
no yukon command is run; no AI review is run. (Adapted from twofam_r1/stage_pkg.sh; slot layout: ~/hashsmash/yukon/pos_r1_exec7/pareto/candidates/poseidon.)
Called by `cycle.sh --stage` . The slot is created from the pos_r1_pkg copy if missing.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/orchard/single_r1_exec7/proof_template_exec.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
