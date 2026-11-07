# TrailLab

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

A C toolkit for inspecting characteristics, replaying pairs, checking state and schedule relationships, and running selected counting experiments.

## What this adds to the workflow

Before: Separate characteristic files, arithmetic checks and one-off diagnostic scripts.

What we added: Brings parsing, 32-bit state reconstruction, schedule checks and signed-difference diagnostics into one command-line workflow.

## Where to get it

- Starter/replay kit: `downloads/traillab-source.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### Traillab CLI: baseline checks and eight-pattern diagnostics

- Original path: `research/tools/traillab/src/main.c`
- SHA-256: `e6e97fea5f753e665d9672233fafa2d9c491fe8354ce5f659793ec7d6d7edce7`
- Usage guide: `guide.html?id=19455d2e5f027f27c948`
- Source/download: `record.html?id=19455d2e5f027f27c948`
- Detailed README in the archive: `guides/19455d2e5f027f27c948.md`
- Finite test report: `verification/traillab-bounded-runtime.json`

### TrailLab's pair engine: consistency, row conditions and collision are separate checks

- Original path: `research/tools/traillab/src/traillab.c`
- SHA-256: `a6a5d4572eadf713c6f039464873bb1632b43f6a3b1d438c3c443c829a2e8341`
- Usage guide: `guide.html?id=4e6f08371462bdc5e40d`
- Source/download: `record.html?id=4e6f08371462bdc5e40d`
- Detailed README in the archive: `guides/4e6f08371462bdc5e40d.md`
- Finite test report: `verification/traillab-bounded-runtime.json`

### Signed differences: distinguish a print limit from an enumeration limit

- Original path: `research/tools/traillab/src/diff.c`
- SHA-256: `3f6e03889125d507cbda62b80cee8dd12c0ce4b3b51182061a06f4fda38d58fa`
- Usage guide: `guide.html?id=61a3c97931a984e75247`
- Source/download: `record.html?id=61a3c97931a984e75247`
- Detailed README in the archive: `guides/61a3c97931a984e75247.md`

### Build TrailLab without confusing quicktest with a small test

- Original path: `research/tools/traillab/Makefile`
- SHA-256: `84e3ee391d6058a080b16ca2d8737a83f522d1cd542e83c71df4bff97e21b1d6`
- Usage guide: `guide.html?id=c54306849197052286c4`
- Source/download: `record.html?id=c54306849197052286c4`
- Detailed README in the archive: `guides/c54306849197052286c4.md`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- GCC with GNU C extensions
- POSIX threads (-pthread)
- libm (-lm)
- matching source bundle and chi37/chi38 inputs

### Build the extracted source bundle

Working directory: The traillab directory extracted from downloads/traillab-source.zip

```text
gcc -O2 -Wall -pthread src/traillab.c src/smc.c src/diff.c src/main.c -lm -o traillab
```

Expected: Exit 0 and a local traillab executable. This is the compiler command used by the bounded publication check.


### Check the three disputed W22 bits

```text
./traillab flip --chi chi/chi37.txt --word W22 --mask 04022000 --threads 1
```

Expected: Exactly eight pattern lines and one surviving pattern, the published one. This is a word-level dependency experiment, not a legal-message sampler or collision search.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
