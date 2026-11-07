# W11 local class tools

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Enumerates free W11 assignments and counts modular small-sigma difference classes; companion tools retain representative-sampling history.

## What this adds to the workflow

Before: Inferring a class population from a handful of sampled members.

What we added: Makes exact local enumeration and representative sampling separate operations with separate result contracts.

## Where to get it

- Starter/replay kit: `downloads/w11-class-recount.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### W11 class enumerator: exact local counts, explicit resource and sanity limits

- Original path: `research/game/climber/guided/n39steer/classes.py`
- SHA-256: `b56fdf584d0e81e35b15b1ad49d60057f887989ae7b0af2b3605e4ae72fc83dc`
- Usage guide: `guide.html?id=26b81cfd182739b2b075`
- Source/download: `record.html?id=26b81cfd182739b2b075`
- Detailed README in the archive: `guides/26b81cfd182739b2b075.md`
- Finite test report: `verification/w11-producers-contract-report-bounded-runtime.json`

### W11 representative sampler: historical seed and subset stopping defect

- Original path: `research/game/climber/guided/n39steer/classvals3.py`
- SHA-256: `1426268bf71aa102111997cf52647467e245e3db73ddf1d2a040feb0a14defb7`
- Usage guide: `guide.html?id=2adead1c1c7c9db253cb`
- Source/download: `record.html?id=2adead1c1c7c9db253cb`
- Detailed README in the archive: `guides/2adead1c1c7c9db253cb.md`
- Finite test report: `verification/w11-representative-contract-report-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python with NumPy; the publication's bounded producer controls used NumPy 1.26.2.
- The separate downloaded rank-and-table replay uses only Python's standard library. It does not distribute or execute this NumPy enumerator.

### Verify the historical full count without a large allocation

Working directory: The extracted w11-class-kit folder

```text
python -B replay.py
```

Expected: passed=true, rank=7, classes=128, members_per_class=65536, total_word_inputs=8388608 and representatives_checked=1152.

This is the independent algebraic certificate and saved-table checker, not a replay of the NumPy producer. It verifies the exact historical signed row and all saved representatives.


### Run the original only in a resource-budgeted disposable tree

Working directory: An isolated n39steer directory with the validated relative inputs above

```text
python -B classes.py
```

Expected: A fresh class_set_W11.tsv with exact local multiplicities for the supplied row; no collision certification.

Confirm free-bit count and available memory first. Preserve the input hashes, inspect the printed pair sanity, and check that the output multiplicities sum to 2^f. The publication ran only a four-value synthetic enumeration.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
