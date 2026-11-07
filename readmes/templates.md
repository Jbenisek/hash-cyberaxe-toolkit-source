# Template & row assembly tools

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Extracts common text and per-row values, fills templates and assembles derived experiment directories.

## What this adds to the workflow

Before: Copying and editing near-identical row files independently.

What we added: Separates shared structure from varying values and makes extraction/filling steps replayable. The guides distinguish actual file fits from summary labels.

## Where to get it

- Starter/replay kit: `downloads/template-contracts.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### Template extractor: check an actual fit before accepting a held-out row

- Original path: `research/launch/port/extract.py`
- SHA-256: `defe4d79fffa4ea40b37abab8f781b137f9ac2044d0d1faf0795ed24dd9cc5cb`
- Usage guide: `guide.html?id=d93c038e30d7da29c954`
- Source/download: `record.html?id=d93c038e30d7da29c954`
- Detailed README in the archive: `guides/d93c038e30d7da29c954.md`
- Finite test report: `verification/template-extract-contract-report-bounded-runtime.json`

### Template filler: string substitution with explicit output and schema limits

- Original path: `research/launch/port/filltmpl.py`
- SHA-256: `4622198f9a101ee7d2ab09f87cf61bb70a9bb4ba9b0df828e3c155314781ad79`
- Usage guide: `guide.html?id=487edecb5afae3a6c430`
- Source/download: `record.html?id=487edecb5afae3a6c430`
- Detailed README in the archive: `guides/487edecb5afae3a6c430.md`
- Finite test report: `verification/template-filltmpl-contract-report-bounded-runtime.json`

### Template alignment: preserve shared text and identify row-key collisions

- Original path: `research/launch/port/mktmpl.py`
- SHA-256: `ca6dfd7f02ff33d4089376f0a50cec6e02002fc2402715c21423e7f6b34812f8`
- Usage guide: `guide.html?id=b93d4972bda61a34e283`
- Source/download: `record.html?id=b93d4972bda61a34e283`
- Detailed README in the archive: `guides/b93d4972bda61a34e283.md`
- Finite test report: `verification/template-mktmpl-contract-report-bounded-runtime.json`

### Row assembler: offline copying with partial-output and trusted-path limits

- Original path: `research/launch/port/newrow.py`
- SHA-256: `003eab8c9a3a92639e8b8d372e05b5ba9b900acdc12840093c20782363f795fe`
- Usage guide: `guide.html?id=fc03f1fed1b354401f69`
- Source/download: `record.html?id=fc03f1fed1b354401f69`
- Detailed README in the archive: `guides/fc03f1fed1b354401f69.md`
- Finite test report: `verification/template-newrow-contract-report-bounded-runtime.json`

### Leave-one-out summary: reported FITS is not an actual held-out extraction

- Original path: `research/launch/port/loo_test.py`
- SHA-256: `28d5c805933dccba30da90e28bef48613f6296ccd1fdc7807d81b1f5503db88a`
- Usage guide: `guide.html?id=3ed00dea2fc87d054e34`
- Source/download: `record.html?id=3ed00dea2fc87d054e34`
- Detailed README in the archive: `guides/3ed00dea2fc87d054e34.md`
- Finite test report: `verification/template-loo_test-contract-report-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python standard library. Use filltmpl.py for the independent refill side of the round trip.

### Replay actual held-out fit versus the summary

Working directory: Extracted template-contracts-kit folder

```text
python -I -B replay.py
```

Expected: Ten controls pass, including a positive extract/refill round trip and the held-out rejection.

The kit includes a row reported FITS by loo_test.py that this extractor correctly rejects against its training template.


### Extract a synthetic known row

Working directory: A scratch tree with tools/, a reviewed template and synthetic r39/note.txt

```text
python -B tools/extract.py templates/note.txt.tmpl r39/note.txt r39 extracted.json
```

Expected: An extracted count and one-row JSON object on fit; otherwise DOES NOT FIT and exit 1.

Require exit zero, refill from extracted.json into a fresh file, and compare bytes. Do not reuse an old extracted.json on failure.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
