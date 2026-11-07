# Pin screen & characteristic repair

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Screens a specific contradictory equal-state window and writes explicitly derived variants with selected E pins released.

## What this adds to the workflow

Before: Sending a contradictory pin window to a solver before inspecting its local structure.

What we added: Adds a cheap, replayable preflight check and records targeted edits as derived characteristics instead of overwriting the source.

## Where to get it

- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### Pin screen: detect one contradictory SHA-256 state window

- Original path: `research/tools/screen/pin_screen.py`
- SHA-256: `b55bacce79b858cb762121f5e2c6266ec8f35b31d91a11a1ac338c66475da1ff`
- Usage guide: `guide.html?id=511d91102cba55465cbb`
- Source/download: `record.html?id=511d91102cba55465cbb`
- Detailed README in the archive: `guides/511d91102cba55465cbb.md`
- Finite test report: `verification/pin_screen-bounded-runtime.json`

### Relax flagged E pins without confusing a repair with a solution

- Original path: `research/tools/screen/fix_pins.py`
- SHA-256: `e05bb1aaa35826eee503392e588dfc276c5728eadaf80f2d0e7972f1bc66dab5`
- Usage guide: `guide.html?id=6bad384bfd6fc2702b96`
- Source/download: `record.html?id=6bad384bfd6fc2702b96`
- Detailed README in the archive: `guides/6bad384bfd6fc2702b96.md`
- Finite test report: `verification/fix_pins-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python standard library only. Reads the named inputs, prints stdout and does not write them.

### Create and screen a disposable fixture

Working directory: An empty scratch directory containing the downloaded pin_screen.py

```text
python -c "from pathlib import Path; z='-'*32; Path('fixture.xml').write_text('\n'.join(f'{r} A: {z} E: {z} W: '+('x'+z[1:] if r==4 else z) for r in range(5)))"
python pin_screen.py fixture.xml
```

Expected: IMPOSSIBLE rows [4], a tab and fixture.xml. This artificial constraint contradiction is not a collision.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
