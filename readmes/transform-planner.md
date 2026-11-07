# Transform pass & convolution planners

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Computes transform-pass compositions, convolution windows and the operation ledgers of retained layouts.

## What this adds to the workflow

Before: Manually choosing a pass split and recomputing its accounting case by case.

What we added: Uses repeatable integer calculations and finite composition checks to compare splits under an explicit charge model.

## Where to get it

- Starter/replay kit: `downloads/poseidon-xconv-lesson.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### Transform pass planner: a finite optimum inside an inherited charge model

- Original path: `research/levers_1029/pos_r15_xconv/tools/geo.py`
- SHA-256: `cdd7ebc0e8172a55f0426afe2dab96b441ec843058912d4967fc3a391e1ead50`
- Usage guide: `guide.html?id=7980333c33f3eebe713a`
- Source/download: `record.html?id=7980333c33f3eebe713a`
- Detailed README in the archive: `guides/7980333c33f3eebe713a.md`
- Finite test report: `verification/xconv-geo-interface-report-bounded-runtime.json`

### One-convolution accounting: replay the integers without allocating the transform

- Original path: `research/levers_1029/pos_r15_xconv/tools/xconv.py`
- SHA-256: `010ef7da265de2774d9519d5c43bba2e2ed50915f0628cb402ff1302634786ad`
- Usage guide: `guide.html?id=5246f7e7ee5abba1e77b`
- Source/download: `record.html?id=5246f7e7ee5abba1e77b`
- Detailed README in the archive: `guides/5246f7e7ee5abba1e77b.md`
- Finite test report: `verification/xconv-guide-bounded-runtime.json`

### Power-of-two convolution counter: valid windows and complete batching

- Original path: `research/levers_1029/pos_r15_xconv/tools/xconv1.py`
- SHA-256: `88535ee7467250a93ce83597feb0c1feeae3f81291043f234b879662fae94e01`
- Usage guide: `guide.html?id=cf04c039d086c39a19ee`
- Source/download: `record.html?id=cf04c039d086c39a19ee`
- Detailed README in the archive: `guides/cf04c039d086c39a19ee.md`
- Finite test report: `verification/xconv-power2-interface-report-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python standard library. The complete teaching kit supplies the two companion counters and fixed numerical ledgers.

### Replay the fixed ledgers and small DP controls

Working directory: The extracted xconv-lesson folder

```text
python -B replay.py
```

Expected: passed=true, small_composition_candidates=1011, impulse_cases=8568 and two historical price rows. These are model checks, not new attack claims.

The existing kit enumerates 1,011 compositions across layer counts 1..10 and compares the minimum to the DP, then checks both historical ledgers and the alias-free output window.


### Import without launching a transform

Working directory: The extracted xconv-lesson folder

```text
python -c "import geo; print(geo.runsplit(3,0,8))"
```

Expected: (0, [])

A zero-layer plan is a valid empty plan. Negative layer counts must be rejected by a caller, despite the original helper accepting -1.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
