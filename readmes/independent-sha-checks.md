# Independent SHA verifiers

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Recomputes message expansion, internal states and feed-forward outputs from numerical message/CV values.

## What this adds to the workflow

Before: Relying on a SAT marker, a decoder's label or an equality printout alone.

What we added: Checks the actual numerical predicate with an independent implementation, with mutation and nontriviality controls documented in the guides.

## Where to get it

- Starter/replay kit: `downloads/boardpair-teaching.zip`
- Starter/replay kit: `downloads/profile-contracts.zip`
- Starter/replay kit: `downloads/seed-prefix-contracts.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### Independently recompute decoded SHA-256 pairs without trusting a solver marker

- Original path: `research/game/climber/guided/kit/indep_verify.py`
- SHA-256: `dec3ad8f2be2ffaecc6e0e63801a12d75de19c3977685a8ff5133fde278b0513`
- Usage guide: `guide.html?id=20fff91402f11d9b672c`
- Source/download: `record.html?id=20fff91402f11d9b672c`
- Detailed README in the archive: `guides/20fff91402f11d9b672c.md`
- Finite test report: `verification/decoded-verifier-bounded-runtime.json`

### Independent SHA-256 reference: feedforward outputs and valid comparison domains

- Original path: `research/tools/indep_sha256_check.py`
- SHA-256: `94ff2424948cbd2b37f95d243d840800d973ef82ea050964fd081efb5891b486`
- Usage guide: `guide.html?id=7ffce43f689544c479ff`
- Source/download: `record.html?id=7ffce43f689544c479ff`
- Detailed README in the archive: `guides/7ffce43f689544c479ff.md`
- Finite test report: `verification/independent-reference-cli-report-bounded-runtime.json`

### A/E/W prefix checker: the exact verify_full contract

- Original path: `research/tools/kepler_tools/verify_full.py`
- SHA-256: `9ff45f77094f60f4def7a6b2e8a661abd4b3f852f7eb42331b45862bdd03e476`
- Usage guide: `guide.html?id=b183544959d14fc1996c`
- Source/download: `record.html?id=b183544959d14fc1996c`
- Detailed README in the archive: `guides/b183544959d14fc1996c.md`
- Finite test report: `verification/prefix-verify_full-bounded-runtime.json`

### Common-chain A/E diagnostic: the exact verify_cv contract

- Original path: `research/tools/kepler_tools/verify_cv.py`
- SHA-256: `14c13e6fd869b2bbe6a11ce1bca888961da413064f3bcbd726ac9405c4e9b14a`
- Usage guide: `guide.html?id=95602528ec6eda7415ab`
- Source/download: `record.html?id=95602528ec6eda7415ab`
- Detailed README in the archive: `guides/95602528ec6eda7415ab.md`
- Finite test report: `verification/prefix-verify_cv-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python standard library only (json, re, sys). No sha_cnf or char_pair_profile import occurs in this verifier.
- The complete teaching kit supplies this source, the two attributed seed JSONs and a wrapper with source-hash checks, input-dimension checks and bounded child timeouts.

### Use the source-checked finite replay

Working directory: The extracted boardpair-kit directory

```text
python -B replay.py
```

Expected: Two original pairs verify; their one-extra-step, one-bit-mutated-message and identical-message controls are rejected. The wrapper checks exact marker lines, not exit status alone. The 37-step pair is an external numerical control and the 38-step seed is project data.


### Check an existing decoded candidate

Working directory: The extracted kit root, with reviewed candidate.map and candidate.chk files supplied separately

```text
python -B kit/indep_verify.py candidate.map candidate.chk
```

Expected: A valid nontrivial pair prints an exact INDEP VERIFIED line. An invalid or identical-message pair prints INDEP NOT VERIFIED and may still exit zero. A printed chaining=sfs label alone does not prove that the input CVs were equal.

This documents the interface; the kit does not include arbitrary files with those names. Confirm n, 32-bit word ranges and both CVs before interpreting the result. Use a full-width shared-CV record for a semi-free-start claim.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
