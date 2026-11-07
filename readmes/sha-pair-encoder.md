# SHA pair encoder & SAT bridge

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Turns paired SHA-256 executions and A/E/W constraints into a solver instance, then decodes a candidate into numerical words.

## What this adds to the workflow

Before: Hand-translating a characteristic into a solver model and inspecting raw assignments.

What we added: Makes pins, initialization, optional native-XOR encoding and decoded values explicit and repeatable. Independent numerical checking remains a separate stage.

## Where to get it

- Starter/replay kit: `downloads/encoder-summary-contracts.zip`
- Starter/replay kit: `downloads/boardpair-teaching.zip`
- Starter/replay kit: `downloads/fulltrail-builder-contracts.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### SHA-256 pair encoder: exact pins, initial states and decoder limits

- Original path: `research/game/climber/guided/minsup/sha_cnf.py`
- SHA-256: `5a6b7373b8aac2312a9c017436c17ed4d29caed27343d959af76de687e33f1aa`
- Usage guide: `guide.html?id=a05b7c7327aa32ada4d4`
- Source/download: `record.html?id=a05b7c7327aa32ada4d4`
- Detailed README in the archive: `guides/a05b7c7327aa32ada4d4.md`
- Finite test report: `verification/minsup-encoder-bounded-runtime.json`

### Encode two SHA-256 trajectories: retained edition, constraints and model boundaries

- Original path: `research/game/climber/guided/kit/sha_cnf.py`
- SHA-256: `5a6b7373b8aac2312a9c017436c17ed4d29caed27343d959af76de687e33f1aa`
- Usage guide: `guide.html?id=b13cabac923ac432d67b`
- Source/download: `record.html?id=b13cabac923ac432d67b`
- Detailed README in the archive: `guides/b13cabac923ac432d67b.md`
- Finite test report: `verification/sha-encoder-bounded-runtime.json`

### Build a full-trail query from a schedule pattern

- Original path: `research/cloud_jobs/API_FULLTRAIL_fulltrail.py`
- SHA-256: `bdbd5f88e455d327080539612c9882e00df24d2ef640da855e15f7e3aaa69e55`
- Usage guide: `guide.html?id=f134331cdfda650b2d08`
- Source/download: `record.html?id=f134331cdfda650b2d08`
- Detailed README in the archive: `guides/f134331cdfda650b2d08.md`
- Finite test report: `verification/fulltrail-builder-contract-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python standard library. Encoding requires a small source characteristic; decoding requires its matching map and model. Solving is a separate operation and is not part of these publication checks.

### Replay the bounded source-contract checks offline

Working directory: The extracted encoder-summary-kit folder

```text
python -I -B replay.py
```

Expected: passed=true; encoder checks include 80 gate assignments, 64 shape assignments, ten traces and four known answers. The demonstrated KOFF mismatch and empty-model trivial output are expected negative controls, not new collision witnesses.

Python 3.10 or later, standard library only. The kit includes the pinned sources and finite data. It writes two small reports inside the extraction folder and uses disposable test directories; no solver or network.


### Generate a one-step standard-IV fixture without solving

Working directory: A new disposable directory containing a copy of the pinned sha_cnf.py

```text
python sha_cnf.py demo.xml demo.cnf demo.map iv
```

Expected: A one-step two-execution formula with standard-IV starts and no imposed collision target. This demonstrates encoding only; no solver is called and no collision is claimed.

Clear inherited encoding-mode environment variables first. demo.xml contains <options><option name="n" value="1"/></options> followed by a new line 0 A: ? E: ? W: ?. The map and formula are newly created outputs, not research inputs to overwrite.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
