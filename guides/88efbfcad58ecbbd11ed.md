# Build the algebraic-paper program for RR=3 (r3 arena, as exec_r6mt/val_r3.sh) and RR=7, RR=8 (build-only: arena and bss link check).

Source: `research/poseidon/algebraic_paper/src/build_all.sh`

Public SHA-256: `13303380f994f23910c56f92c08a395713074b38ce477bc3214bc423621605c6`

## Purpose recorded in the source

Build the algebraic-paper program for RR=3 (r3 arena, as exec_r6mt/val_r3.sh) and RR=7, RR=8 (build-only: arena and bss link check).
Flags are those of exec_r6mt (cycle.sh / build_cloud_r6.sh). Run:  wsl -d Ubuntu -- bash build_all.sh
Optional env: MAXTR_K (K, default 2), SEEDS (space separated coin seeds for extra RR=3 binaries, default "1 2 3")
r7: live peak ~136e9 (README), arena 160e9 ; r8: live peak ~602e9, arena 710e9 (formula of R6_PLAN.md section 2, AMAX 29 / 31)

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
