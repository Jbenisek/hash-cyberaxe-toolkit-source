# run_pin.sh NAME KMAX [BUDGET=1140] [W=2] [SYSTIMEOUT=120] [SAMPLE=300]

Source: `research/newpaths/untried/const_alg/run_pin.sh`

Public SHA-256: `a333d179c033b46413deff3f312ffb1f3595f8f568514cb31bded353edd04300`

## Purpose recorded in the source

run_pin.sh NAME KMAX [BUDGET=1140] [W=2] [SYSTIMEOUT=120] [SAMPLE=300]
One pin through the atlas pipeline (ctr_count.py: research/paths scripts imported unchanged, outputs here):
  filter (betas with k <= KMAX) -> sys (kissat on those with a passing outcome) -> satcount -> report.
W processes at nice 5 (the brief allows at most 2). The calculator step gets what is left of BUDGET seconds
(minus 45 s for the report), so the whole run stays under 20 minutes. Log: status.txt; own PID: pids.txt.
Started with setsid, so the whole run is one process group that can be stopped by its own PGID (never by name).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/newpaths/untried/const_alg/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
