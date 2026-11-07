# lens EVERY FIGURE: run the recomputation (one thread, read only)

Source: `research/pkg5/review/fig_run1.sh`

Public SHA-256: `b062737479e39586a07f791c11e42be24baf07305f51685c462a2ff7a7fb75d1`

## Purpose recorded in the source

lens EVERY FIGURE: run the recomputation (one thread, read only)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/pkg5/review/fig_diff_manifest.txt
- research/pkg5/review/fig_diff_proof.txt
- research/pkg5/review/math_proof.txt
- research/pkg5/review/fig_schema.py
- research/pkg5/review/math_proof.py
- research/pkg5/review/math_proof.sh

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
