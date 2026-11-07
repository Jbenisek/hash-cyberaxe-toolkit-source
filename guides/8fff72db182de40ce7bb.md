# stage_r7alg3.sh SLOT (WSL): stage the Poseidon r7 algebraic paper package (v2/out) into the NEW slot pos_<slot> (a slot is never reused) (base pos_posgen2), run the organizer intak

Source: `research/poseidon/pkg_r7_paper/v4/stage_r7alg3.sh`

Public SHA-256: `1c4fa297840797b62ea42c5e1766f40bcd999732f2d0c66dbf2a0b7e825179e2`

## Purpose recorded in the source

stage_r7alg3.sh SLOT (WSL): stage the Poseidon r7 algebraic paper package (v2/out) into the NEW slot pos_<slot> (a slot is never reused) (base pos_posgen2), run the organizer intake,
prefile_check and rulecheck, and write (NOT run) research/launch/submit_pareto_posr7alg5.sh. Submits nothing; runs no yukon command.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/pkg_r7_paper/RESULT.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
