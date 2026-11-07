# SHA-3 lane & low-bit experiment tools

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Retains reduced-round lane experiments, low-bit controls and documented walk/search interfaces.

## What this adds to the workflow

Before: A single experiment script with implicit lane choices and loosely comparable output labels.

What we added: Documents selected inputs, event widths, lane representations and finite interface checks so related experiments can be compared on the same terms.

## Where to get it

- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### SHA3 r7 memory program: embedding, local Boolean checks and execution limits

- Original path: `research/checks_1015/pa_src/pos_sha3r7p/experiments/s7ls.py`
- SHA-256: `fbfae670f4b545e0009c7e17e84ad517bdb3d972c1452264ecba88a424010cd4`
- Usage guide: `guide.html?id=53c3f17d7fbc89d106b4`
- Source/download: `record.html?id=53c3f17d7fbc89d106b4`
- Detailed README in the archive: `guides/53c3f17d7fbc89d106b4.md`
- Finite test report: `verification/s7ls-bounded-runtime.json`

### SHA3 r8 memory program: embedding, local Boolean checks and execution limits

- Original path: `research/checks_1015/pa_src/pos_sha3r8/experiments/s8ls.py`
- SHA-256: `23d51e336be6ec67c99f858afdaabe7f1b9f97295fa81db1b8b099222af2c3a0`
- Usage guide: `guide.html?id=8056aaff9be69d4fb873`
- Source/download: `record.html?id=8056aaff9be69d4fb873`
- Detailed README in the archive: `guides/8056aaff9be69d4fb873.md`
- Finite test report: `verification/s8ls-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python 3 standard library; no third-party package or local module imports are required by the archived source.
- The bounded test uses a disposable copy and standard-library unittest.mock; hashlib supplies the independent full-round scalar reference.

### Bounded scalar reference check without setup or search

Working directory: A disposable directory containing the downloaded, hash-checked s7ls.py

```text
python -I -B -c "import hashlib,runpy; m=runpy.run_path('s7ls.py',run_name='bounded_copy'); assert m['digest'](b'abc',24)==hashlib.sha3_256(b'abc').digest(); print('single-block reference check passed')"
```

Expected: single-block reference check passed

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
