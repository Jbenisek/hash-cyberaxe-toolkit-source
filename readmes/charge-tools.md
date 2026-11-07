# Batch, memory & charge calculators

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Replays declared batch costs, shard layouts and memory/time tradeoffs from explicit parameters.

## What this adds to the workflow

Before: A price written as a final number with hidden rounding, table capacity or fixed overhead.

What we added: Exposes the arithmetic and inputs so another researcher can reproduce the row and change one assumption at a time.

## Where to get it

- Starter/replay kit: `downloads/d126-model-replay.zip`
- Starter/replay kit: `downloads/sparsedoor-price-contracts.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### D126 shard pricing: exact arithmetic, conditional models and integer memory

- Original path: `research/luna_jobs/d126_memory_rule/price.py`
- SHA-256: `56585f353df438847d671e56626e10cd5618aea38aa1ea88b0df56beddc9d43f`
- Usage guide: `guide.html?id=a2cd4391514619f11d9c`
- Source/download: `record.html?id=a2cd4391514619f11d9c`
- Detailed README in the archive: `guides/a2cd4391514619f11d9c.md`
- Finite test report: `verification/d126-model-kit-report-bounded-runtime.json`

### A historical door-price calculator: exact fractions do not make sampled inputs exact

- Original path: `research/game/climber/guided/sparsedoor/price.py`
- SHA-256: `4cffee4381b371da3049e646d5f36629492ba93696c8e421bd9adcb215eb5959`
- Usage guide: `guide.html?id=027375f3ccde4846ea56`
- Source/download: `record.html?id=027375f3ccde4846ea56`
- Detailed README in the archive: `guides/027375f3ccde4846ea56.md`
- Finite test report: `verification/sparsedoor-price-contract-report-bounded-runtime.json`

### SHA-256 tail sampler: observation batches, chosen IVs and saved calibration (combined/dk)

- Original path: `research/pkg_r39_combined/work/dk/experiments/r39tail.py`
- SHA-256: `5bbd6117e33476bc77a0933808e95cfce526f00495c0be0dd0434cdb5930a3c0`
- Usage guide: `guide.html?id=218178906990dd60b045`
- Source/download: `record.html?id=218178906990dd60b045`
- Detailed README in the archive: `guides/218178906990dd60b045.md`
- Finite test report: `verification/r39tail-bounded-runtime.json`

### Combined condition counter: literal fields and independently sampled row estimates

- Original path: `research/tools/funnel/count_e2e.py`
- SHA-256: `4f22051c91e57451993cb433d36db29ded2abb053ca499ab6303d105fb09239c`
- Usage guide: `guide.html?id=2f849de0ddc4995673ce`
- Source/download: `record.html?id=2f849de0ddc4995673ce`
- Detailed README in the archive: `guides/2f849de0ddc4995673ce.md`
- Finite test report: `verification/e2e-counter-contract-report-bounded-runtime.json`

### SHA-256 tail sampler: observation batches, chosen IVs and saved calibration (best/dkbase)

- Original path: `research/pkg_r39_best_work/dkbase/sha256/experiments/r39tail.py`
- SHA-256: `5bbd6117e33476bc77a0933808e95cfce526f00495c0be0dd0434cdb5930a3c0`
- Usage guide: `guide.html?id=41a5af6799ff94337007`
- Source/download: `record.html?id=41a5af6799ff94337007`
- Detailed README in the archive: `guides/41a5af6799ff94337007.md`
- Finite test report: `verification/r39tail-bounded-runtime.json`

### Exact historical batch-pricing calculator

- Original path: `research/fifties/batchprice/batchprice.py`
- SHA-256: `615a8dbaa0cc3104a1047e35d28e024a778398e578684d9a32055d9492c4b25c`
- Usage guide: `guide.html?id=6a3590b2c6fe07ec4214`
- Source/download: `record.html?id=6a3590b2c6fe07ec4214`
- Detailed README in the archive: `guides/6a3590b2c6fe07ec4214.md`
- Finite test report: `verification/batchprice-bounded-runtime.json`

### SHA-256 r39 joint walk: source interface, finite identities and limits

- Original path: `research/pkg_r39_best_work/dkbase/sha256/experiments/r39joint.py`
- SHA-256: `538b062d52fecc6cc97ba200175657e13c17483083da6b9e06537ed5b3b0c781`
- Usage guide: `guide.html?id=e4b3eb6d227a87deb21d`
- Source/download: `record.html?id=e4b3eb6d227a87deb21d`
- Detailed README in the archive: `guides/e4b3eb6d227a87deb21d.md`
- Finite test report: `verification/r39joint-bounded-runtime.json`

### SHA-256 r39 joint walk: source interface, finite identities and limits

- Original path: `research/pkg_r39_combined/work/dk/experiments/r39joint.py`
- SHA-256: `538b062d52fecc6cc97ba200175657e13c17483083da6b9e06537ed5b3b0c781`
- Usage guide: `guide.html?id=e6ec7ca0c6fadc5508d2`
- Source/download: `record.html?id=e6ec7ca0c6fadc5508d2`
- Detailed README in the archive: `guides/e6ec7ca0c6fadc5508d2.md`
- Finite test report: `verification/r39joint-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Portable lesson: Python 3.11+ and standard library; no solver, network or mapped drive. Run without -O so assertions stay enabled.
- The kit contains selected arithmetic definitions and numerical inputs, not the full r37/r38 research modules. Original fingerprints appear in PROVENANCE.json; included selected bytes have their own digests.
- The source-bound local audits verify original fingerprints. The offline replay checks only included selected bytes; it cannot establish possession of omitted original files.

### Reproduce the complete grids

Working directory: Extracted d126-model-kit directory

```text
python -I -B replay.py
```

Expected: passed=true, grid_rows=79, rigorous_rounding_certificates=191, best_k={r37:5,r38:19}. The exact r37 winning time is 89459989869750967895523/1322.


### Inspect the integer-memory correction

Working directory: Extracted d126-model-kit directory

```text
python -I -B replay.py
```

Expected: reports.r37.memory_floor_affected_k is [28,29,30,31,32]. Each ceiling correction adds one byte; k=5 remains the exact winner. This is not a proof of actual maximum shard occupancy.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
