# Trail & schedule diagnostics

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Profiles expanded-word differences, compares shifted rows, counts condition symbols and groups related trail files.

## What this adds to the workflow

Before: Comparing large characteristic dumps manually or treating unlike condition counts as the same measurement.

What we added: Produces repeatable row comparisons, named profiles and grouping rules, with each counting convention kept visible.

## Where to get it

- Starter/replay kit: `downloads/profile-contracts.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### Expanded-word profiles and the limits of XML projection

- Original path: `research/tools/schedexact/wdiff_profile.py`
- SHA-256: `0903e60a9c7759289300ba1b95fbb0d95a92bb60d3f15a1ffc4ba6b4a23b437f`
- Usage guide: `guide.html?id=6c77c30841c6c588cadc`
- Source/download: `record.html?id=6c77c30841c6c588cadc`
- Detailed README in the archive: `guides/6c77c30841c6c588cadc.md`
- Finite test report: `verification/wdiff-profile-bounded-runtime.json`

### Compare signed schedule rows at an explicit offset

- Original path: `research/tools/schedexact/cmp_shift.py`
- SHA-256: `6e7dc8410b37f23aa09b5eb050643f299e161b4ff580618edad78a6e98cc9ea7`
- Usage guide: `guide.html?id=5c8b6f0ab5359100587a`
- Source/download: `record.html?id=5c8b6f0ab5359100587a`
- Detailed README in the archive: `guides/5c8b6f0ab5359100587a.md`
- Finite test report: `verification/cmp-shift-bounded-runtime.json`

### Condition-symbol counter: literal counts and an XOR-support check

- Original path: `research/tools/schedexact/condcount.py`
- SHA-256: `0345be26e85c453426b66baf55e9c123317a81b6dc620280f818ae557ab3dd69`
- Usage guide: `guide.html?id=ac29374cdd5e9e5223e9`
- Source/download: `record.html?id=ac29374cdd5e9e5223e9`
- Detailed README in the archive: `guides/ac29374cdd5e9e5223e9.md`
- Finite test report: `verification/condcount-bounded-runtime.json`

### Trail-family index: grouping semantics and representative selection

- Original path: `research/tools/profile/trail_families.py`
- SHA-256: `db96c9a3d3d7670815487cdb43a923918911e6d372dbb131f1bb4f5efbfe7180`
- Usage guide: `guide.html?id=ee3afd6d4124c0f316fb`
- Source/download: `record.html?id=ee3afd6d4124c0f316fb`
- Detailed README in the archive: `guides/ee3afd6d4124c0f316fb.md`
- Finite test report: `verification/trail-family-contract-report-bounded-runtime.json`

### Compare SHA-256 SAT encodings without running a solver

- Original path: `research/sha256grid/check2-1/cnfdiff.py`
- SHA-256: `6cf3641ff312d7058e30435fa861cedce67caee29dbba43d6216b94c29460b0d`
- Usage guide: `guide.html?id=4b4b9d53d3979fb7dae9`
- Source/download: `record.html?id=4b4b9d53d3979fb7dae9`
- Detailed README in the archive: `guides/4b4b9d53d3979fb7dae9.md`
- Finite test report: `verification/cnfdiff-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python standard library; no solver or network.

### Create and inspect a synthetic schedule pair

Working directory: Disposable folder containing the downloaded wdiff_profile.py

```text
python -c "from pathlib import Path; Path('fixture.pair').write_text('M1 '+' '.join(['00000000']*16)+'\nM2 00000001 '+' '.join(['00000000']*15)+'\n')"
python wdiff_profile.py fixture.pair 48
```

Expected: Row 0 differs at bit 0 with symbol n and dmod=-0x1. Later schedule differences and a footer are printed. This fixture is not a compression collision.


### Inspect the signed-symbol projection only

Working directory: Folder containing a validated characteristic and the downloaded tool

```text
python wdiff_profile.py --xml CHAR.xml
```

Expected: Only u/n survive. Do not interpret dropped x/?/0/1 or sequential row numbers as the original characteristic's full semantics.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
