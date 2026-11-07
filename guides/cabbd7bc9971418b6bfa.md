# bf unit

Source: `research/newpaths/audit/bf_unit.py`

Public SHA-256: `8c45353cbc17fdb8208828fffdf58433952032ec7916a16d784d1f5e95002ed9`

## Purpose recorded in the source

bf.c DFS vs brute-force kmin (itertools + gd_order.propagate) on random small systems: bf at kmax=kmin must find
a covering set of size kmin and none smaller.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "os",
  "random",
  "rules",
  "sat_unit",
  "subprocess",
  "sys"
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
