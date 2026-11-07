# hostile-judge lens: size of the judge evidence of the last local intake in the validation mirror (read-only, stat only)

Source: `research/pkg5/review/judge_size.sh`

Public SHA-256: `69f0dc9ad73faba3021b70c8646760b85a7d70698ae2958c7eece45876e0eedf`

## Purpose recorded in the source

hostile-judge lens: size of the judge evidence of the last local intake in the validation mirror (read-only, stat only)

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
