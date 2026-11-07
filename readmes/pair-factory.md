# 39-step pair factory

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Generates additional pairs along a known signed characteristic, excludes known pairs and checks solver candidates before retaining them.

## What this adds to the workflow

Before: A fixed seed pair and manually managed batches of candidate results.

What we added: Adds corpus-aware exclusion, reproducible candidate generation and independent checking to an existing characteristic.

## Where to get it

- Starter/replay kit: `downloads/scan-driver-contracts.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### Understand and reconstruct the 39-step SHA-256 pair factory

- Original path: `research/game/climber/guided/pairfactory/pf.py`
- SHA-256: `ead64dbd7f9885d9fe9051e7f2cf10def0b27ee8092864b3dc11e264de7cfbeb`
- Usage guide: `guide.html?id=f67c3d8b8d4dd54c827a`
- Source/download: `record.html?id=f67c3d8b8d4dd54c827a`
- Detailed README in the archive: `guides/f67c3d8b8d4dd54c827a.md`

### Audit the middle-band scan: pins, resume identity and shared-state hazards

- Original path: `research/game/climber/guided/midscan/mid_driver.py`
- SHA-256: `e295b1f64fb222d0c87e0994a92181eaa3870f560a7c39c4a93bce9418189cca`
- Usage guide: `guide.html?id=2e71eb45d2f116b185c9`
- Source/download: `record.html?id=2e71eb45d2f116b185c9`
- Detailed README in the archive: `guides/2e71eb45d2f116b185c9.md`
- Finite test report: `verification/mid-driver-bounded-runtime.json`

### Schedule scan driver: query identity, restart rules and cache limits

- Original path: `research/game/climber/guided/scan40_topslide/scan_driver.py`
- SHA-256: `67ec37d0470e8677bf54f4addaefe4e2dd2720a55a43d780946b4e8e8db6f9fa`
- Usage guide: `guide.html?id=f82eac3ed059b8e8ae85`
- Source/download: `record.html?id=f82eac3ed059b8e8ae85`
- Detailed README in the archive: `guides/f82eac3ed059b8e8ae85.md`
- Finite test report: `verification/scan-driver-contract-report-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- A POSIX environment with Python 3, bash, nice, os.wait4 support, a writable shared-memory filesystem and sufficient scratch space. The unchanged driver is not a native Windows script.
- Kissat on PATH for factory solving; its status/model text must match the parser. No solver version or binary hash is pinned by pf.py.
- guided/pinladder/ladder.py and guided/kit/{char_pair_profile.py,sha_cnf.py,indep_verify.py}, preserved in their original relative directory structure.
- research/pkg_r39_newchar/sha256/experiments/r39joint.py. Pairfactory uses its trajectory function; its import also initializes module data and optionally attempts Wasmtime loading if R39_WASM is set. Wasmtime is not required for this trajectory use when that optional configuration is absent.
- The characteristic, seed witness, known-pair registry/corpus, tail source, statistics helper, baseline replicas and two request sets described above.
- PUBLIC DOWNLOAD LIMITATION: pf.py alone is not runnable. The three kit modules are now supplied in the board-pair teaching bundle, but ladder.py, r39joint.py, the characteristic XML, pub39 seed, KNOWN_FILES.txt and complete transitive corpus are not supplied as a tested factory bundle. The small teaching kit is not a complete factory environment.

### Initialization-only reconstruction in an isolated complete tree

Working directory: The root of an isolated, complete research-tree copy in a dedicated POSIX environment

```text
python3 research/game/climber/guided/pairfactory/pf.py 1 1 30 dry
```

Expected: If initialization and all assertions succeed, stdout reports base char: NV ... NC ..., prior known pairs, on-characteristic sources, resumed found count and first-generation job count, then exits. No specific counts or runtime are asserted by this guide.

Source-reviewed syntax, not executed for publication. This is not a harmless help command: it builds a potentially large CNF, creates directories, overwrites base artifacts and reads the known corpus. Use only after restoring the dependencies, checking model environment defaults, and isolating the fixed scratch locations from other work. It does not launch the solver or tail workers.


### Read the full campaign invocation, not a quick-start benchmark

Working directory: The same isolated, complete research-tree copy

```text
python3 research/game/climber/guided/pairfactory/pf.py 1 1 30
```

Expected: Depending on solver outcomes and existing files, the driver appends factory results and may create verified pairs, then drains tail stages and reports the available Stage-B ranking. Empty, partial or failed scientific results are possible; a normal final print or ledger line is not sufficient evidence that every requested measurement completed successfully.

Removing dry launches real solver and tail work. This example documents the interface, not a recommendation to run a cheap test. One lane and a 30-second solver CPU cap do not cap total elapsed time, memory or tail work. Restored found files can satisfy TARGET before any new pair is found. Even with no new pair, Stage B can still measure baseline controls. No campaign was launched during this review.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
