# stats win

Source: `research/pkg_r39_best_work/stats_win.py`

Public SHA-256: `f58ecc41190cec161b71c9d1a08ccea4fdbe929c01f430a5878fa03f57a4d34a`

## Purpose recorded in the source

stats_win.py SEED OUT.json : per-claw side-condition statistics of one full ledger window of the shipped program
(owner 10-27: re-measure 0b2616e3's offline uniformity block on OUR windows, not cut it). Runs Attack(win=P.WIN, seed=SEED,
check=True) exactly as `r39joint.py --windows 1 --seed S` does (seed = S*1000), then for every distinct claw recomputes
W8 in F8, W9 in F9, W17, W18 with the program's own functions (the same code path as r39-window-small).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "os",
  "r39joint",
  "sys"
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
