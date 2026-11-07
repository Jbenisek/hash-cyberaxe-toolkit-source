# Numerical pair → characteristic tools

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Builds inspectable signed schedule/state templates from numerical pairs and applies explicit prefix or state-freeing choices.

## What this adds to the workflow

Before: Editing XML/text masks by hand without retaining the numerical seed and transformation choices.

What we added: Makes the seed, signed differences, fixed-value rows and freeing policy reproducible inputs to the next experiment.

## Where to get it

- Starter/replay kit: `downloads/lawbase-example.zip`
- Starter/replay kit: `downloads/seed-prefix-contracts.zip`
- Starter/replay kit: `downloads/mkxml-contracts.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### Generate a search base without confusing it for a result

- Original path: `research/publication_sources/FROM_HENSEL_1102_B32/lawbase.py`
- SHA-256: `a6e1cf0c62710affe52a7f46640e0892cfeac7b23b2a13f0a3824112a7425d2f`
- Usage guide: `guide.html?id=f8911c7ee7bfe3e32bd0`
- Source/download: `record.html?id=f8911c7ee7bfe3e32bd0`
- Detailed README in the archive: `guides/f8911c7ee7bfe3e32bd0.md`
- Finite test report: `verification/lawbase-kit-contract-bounded-runtime.json`

### Value-seeded SHA-256 trails: pins, closing targets and precedence

- Original path: `research/tools/funnel/nld_seed.py`
- SHA-256: `7a490fd7af31dddceff8c760e376eef6e56b50e11d4e2eda9f408ed40b19c56e`
- Usage guide: `guide.html?id=25b753ef2367b50a4209`
- Source/download: `record.html?id=25b753ef2367b50a4209`
- Detailed README in the archive: `guides/25b753ef2367b50a4209.md`
- Finite test report: `verification/value-seed-contract-report-bounded-runtime.json`

### From numerical pair to characteristic: pin the prefix, inspect the tail

- Original path: `research/tools/funnel/pair2char.py`
- SHA-256: `88133bed956eaefad6f519b1e8afd9adb1faabff48ad84a0e93db64c1c0a3855`
- Usage guide: `guide.html?id=729e429670f58dc5eb02`
- Source/download: `record.html?id=729e429670f58dc5eb02`
- Detailed README in the archive: `guides/729e429670f58dc5eb02.md`
- Finite test report: `verification/pair2char-bounded-runtime.json`

### Generate a schedule-support template without confusing free bits and differences

- Original path: `research/game/climber/guided/minsup/mk_tap.py`
- SHA-256: `f8547f0ea192e61d47c5ed50e287276d0b80e17a53a05dd03c853b43482222e9`
- Usage guide: `guide.html?id=df49d42b437c1536d012`
- Source/download: `record.html?id=df49d42b437c1536d012`
- Detailed README in the archive: `guides/df49d42b437c1536d012.md`
- Finite test report: `verification/tap-generator-bounded-runtime.json`

### SHA-2 XML templates: reproduce mask corrections without inferring collisions

- Original path: `research/levers_1021/s256_r40_search/nldtool/mkxml.py`
- SHA-256: `5bb0481f32e86ddc83e7b02624c0ff437e31dd4785d3233510b28cf931528b4b`
- Usage guide: `guide.html?id=ec2641cda02856777245`
- Source/download: `record.html?id=ec2641cda02856777245`
- Detailed README in the archive: `guides/ec2641cda02856777245.md`
- Finite test report: `verification/mkxml-contract-report-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python 3.9+ standard library for the teaching replay.
- No network, mapped drive, encoder, solver or GPU is needed after extraction.

### Replay the source-specific example

Working directory: Extracted lawbase-example

```text
python -I -B replay.py
```

Expected: passed=true; 44 state rows, 40 signed W words, two source-generator invocations, zero solver runs and zero collision checks.


### Write a fresh XML template

Working directory: Extracted lawbase-example, with no existing fresh-base.xml

```text
python -I -B originals/lawbase.py originals/LIFT_s9.check fresh-base.xml 40 29
```

Expected: An XML query template with the described boundaries. E=29 is supplied by the caller, not checked by the source.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
