# BLAKE3 half-digest construction & clusters

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Constructs structured two-round message families and investigates the remaining residual with representative/neighbour diagnostics.

## What this adds to the workflow

Before: Treating every complete message trial as an unrelated candidate.

What we added: Exposes a reusable algebraic family and cluster geometry, separating the representative gate, retained rule and neighbour count.

## Where to get it

- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### BLAKE3 pkg10: the representative-and-neighbour counting model

- Original path: `research/pkg10/pkg/blake3-r2/experiments/halfsearch.py`
- SHA-256: `f6ba1d3353e35d008f64c5aef7d989e5df989332eb563813214ff35453ab3616`
- Usage guide: `guide.html?id=d2181b119a3a37345fe3`
- Source/download: `record.html?id=d2181b119a3a37345fe3`
- Detailed README in the archive: `guides/d2181b119a3a37345fe3.md`
- Finite test report: `verification/pkg10-cluster-bounded-runtime.json`

### BLAKE3 halfsearch: construction, toy residual search and counted batches (pkg9/pkg/work/fix4/prev/blake3-r2)

- Original path: `research/pkg9/pkg/work/fix4/prev/blake3-r2/experiments/halfsearch.py`
- SHA-256: `31d6f21dbfb71502fe9318a7238794855c89c9ac4fa1ef828cf7919722a8d902`
- Usage guide: `guide.html?id=4921863d0baec7bcf826`
- Source/download: `record.html?id=4921863d0baec7bcf826`
- Detailed README in the archive: `guides/4921863d0baec7bcf826.md`
- Finite test report: `verification/halfsearch-bounded-runtime.json`

### BLAKE3 halfsearch: construction, toy residual search and counted batches (pkg7/work/fix3/prev/blake3-r2)

- Original path: `research/pkg7/work/fix3/prev/blake3-r2/experiments/halfsearch.py`
- SHA-256: `31d6f21dbfb71502fe9318a7238794855c89c9ac4fa1ef828cf7919722a8d902`
- Usage guide: `guide.html?id=187bdf5e0f4ba9aaae40`
- Source/download: `record.html?id=187bdf5e0f4ba9aaae40`
- Detailed README in the archive: `guides/187bdf5e0f4ba9aaae40.md`
- Finite test report: `verification/halfsearch-bounded-runtime.json`

### BLAKE3 halfsearch: construction, toy residual search and counted batches (pkg9/pkg/work/fix3/prev/blake3-r2)

- Original path: `research/pkg9/pkg/work/fix3/prev/blake3-r2/experiments/halfsearch.py`
- SHA-256: `31d6f21dbfb71502fe9318a7238794855c89c9ac4fa1ef828cf7919722a8d902`
- Usage guide: `guide.html?id=382bf8ce285274a0a5b8`
- Source/download: `record.html?id=382bf8ce285274a0a5b8`
- Detailed README in the archive: `guides/382bf8ce285274a0a5b8.md`
- Finite test report: `verification/halfsearch-bounded-runtime.json`

### BLAKE3 halfsearch: construction, toy residual search and counted batches (pkg8/pkg/work/fix3/prev/blake3-r2)

- Original path: `research/pkg8/pkg/work/fix3/prev/blake3-r2/experiments/halfsearch.py`
- SHA-256: `31d6f21dbfb71502fe9318a7238794855c89c9ac4fa1ef828cf7919722a8d902`
- Usage guide: `guide.html?id=4d42bccd18fa9274b43d`
- Source/download: `record.html?id=4d42bccd18fa9274b43d`
- Detailed README in the archive: `guides/4d42bccd18fa9274b43d.md`
- Finite test report: `verification/halfsearch-bounded-runtime.json`

### BLAKE3 halfsearch: construction, toy residual search and counted batches (pkg10/pkg/work/fix3/prev/blake3-r2)

- Original path: `research/pkg10/pkg/work/fix3/prev/blake3-r2/experiments/halfsearch.py`
- SHA-256: `31d6f21dbfb71502fe9318a7238794855c89c9ac4fa1ef828cf7919722a8d902`
- Usage guide: `guide.html?id=53cda766ffefd38d31ef`
- Source/download: `record.html?id=53cda766ffefd38d31ef`
- Detailed README in the archive: `guides/53cda766ffefd38d31ef.md`
- Finite test report: `verification/halfsearch-bounded-runtime.json`

### BLAKE3 halfsearch: construction, toy residual search and counted batches (pkg7/blake3-r2)

- Original path: `research/pkg7/blake3-r2/experiments/halfsearch.py`
- SHA-256: `31d6f21dbfb71502fe9318a7238794855c89c9ac4fa1ef828cf7919722a8d902`
- Usage guide: `guide.html?id=705e7a4020c96be1cae2`
- Source/download: `record.html?id=705e7a4020c96be1cae2`
- Detailed README in the archive: `guides/705e7a4020c96be1cae2.md`
- Finite test report: `verification/halfsearch-bounded-runtime.json`

### BLAKE3 halfsearch: construction, toy residual search and counted batches (pkg10/pkg/work/fix4/prev/blake3-r2)

- Original path: `research/pkg10/pkg/work/fix4/prev/blake3-r2/experiments/halfsearch.py`
- SHA-256: `31d6f21dbfb71502fe9318a7238794855c89c9ac4fa1ef828cf7919722a8d902`
- Usage guide: `guide.html?id=882d65558867201d08fa`
- Source/download: `record.html?id=882d65558867201d08fa`
- Detailed README in the archive: `guides/882d65558867201d08fa.md`
- Finite test report: `verification/halfsearch-bounded-runtime.json`

### BLAKE3 early halfsearch (pkg5): 60/62-byte construction and diagnostic counts

- Original path: `research/pkg5/blake3-r2/experiments/halfsearch.py`
- SHA-256: `8b1b4a16e203f6984d00f05a4ea83634b17282fa30504c18b797c9d014c35328`
- Usage guide: `guide.html?id=b4df8f14b6a9715c01b2`
- Source/download: `record.html?id=b4df8f14b6a9715c01b2`
- Detailed README in the archive: `guides/b4df8f14b6a9715c01b2.md`
- Finite test report: `verification/halfsearch-pkg5-bounded-runtime.json`

### BLAKE3 pkg9 halfsearch: a declared cluster-yield budget, not a new cluster driver

- Original path: `research/pkg9/pkg/blake3-r2/experiments/halfsearch.py`
- SHA-256: `d79e79743692f7a8224573e99820c62d8bf90565927da87512ac328831056863`
- Usage guide: `guide.html?id=cabecf75541ba186282a`
- Source/download: `record.html?id=cabecf75541ba186282a`
- Detailed README in the archive: `guides/cabecf75541ba186282a.md`
- Finite test report: `verification/halfsearch-pkg9-bounded-runtime.json`

### BLAKE3 halfsearch: construction, toy residual search and counted batches (pkg8/pkg/work/fix4/prev/blake3-r2)

- Original path: `research/pkg8/pkg/work/fix4/prev/blake3-r2/experiments/halfsearch.py`
- SHA-256: `31d6f21dbfb71502fe9318a7238794855c89c9ac4fa1ef828cf7919722a8d902`
- Usage guide: `guide.html?id=e179db8eba799f87e04b`
- Source/download: `record.html?id=e179db8eba799f87e04b`
- Detailed README in the archive: `guides/e179db8eba799f87e04b.md`
- Finite test report: `verification/halfsearch-bounded-runtime.json`

### BLAKE3 pkg8 halfsearch: a declared cluster-yield budget, not a new cluster driver

- Original path: `research/pkg8/pkg/blake3-r2/experiments/halfsearch.py`
- SHA-256: `f2a207685af251288f88380550bc574eaa6ae3defa52b6cd84a3439e3fb2fda3`
- Usage guide: `guide.html?id=e39e9f522d3cff62d6ed`
- Source/download: `record.html?id=e39e9f522d3cff62d6ed`
- Detailed README in the archive: `guides/e39e9f522d3cff62d6ed.md`
- Finite test report: `verification/halfsearch-pkg8-bounded-runtime.json`

### BLAKE3 early halfsearch (pkg6): 55/63-byte construction and diagnostic counts

- Original path: `research/pkg6/blake3-r2/experiments/halfsearch.py`
- SHA-256: `b578641896edf4d4d56209bb93b57b8e70fa90a9beb3fc0db862664d862800db`
- Usage guide: `guide.html?id=e9a7845fca0e9458cb30`
- Source/download: `record.html?id=e9a7845fca0e9458cb30`
- Detailed README in the archive: `guides/e9a7845fca0e9458cb30.md`
- Finite test report: `verification/halfsearch-pkg6-bounded-runtime.json`

### BLAKE3 halfsearch: construction, toy residual search and counted batches (pkg7/work/fix4/prev/blake3-r2)

- Original path: `research/pkg7/work/fix4/prev/blake3-r2/experiments/halfsearch.py`
- SHA-256: `31d6f21dbfb71502fe9318a7238794855c89c9ac4fa1ef828cf7919722a8d902`
- Usage guide: `guide.html?id=f809a9b08803b9b55e87`
- Source/download: `record.html?id=f809a9b08803b9b55e87`
- Detailed README in the archive: `guides/f809a9b08803b9b55e87.md`
- Finite test report: `verification/halfsearch-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python 3 standard library. The source imports hashlib, json, struct and sys; its ledger also uses fractions and its larger test uses math. No local module or solver dependency.
- The publication's independent digest comparison uses Node.js and the pinned blake3-replay.js. That is a checker dependency, not a halfsearch.py runtime dependency.

### Check the JSON interface without generating trials

Working directory: A disposable directory containing the downloaded, hash-checked halfsearch.py

```text
'{"schema_version":1,"target_profile":"blake3-r2-prefix-v1","event":{"kind":"digest-xor-mask"},"experiment_id":"half-collision","trials":[]}' | python -I -B halfsearch.py
```

Expected: JSON with schema_version=1 and trials=[]. Both empty experiment modes passed. This minimal syntax check is not a complete event declaration, collision test or solver run.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
