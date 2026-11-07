# Poseidon reference & replay tools

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Recomputes declared Poseidon profiles and saved pairs, with explicit numerical parameters and finite controls.

## What this adds to the workflow

Before: Trying to replay a result without its parameter file or a clearly identified profile.

What we added: Connects the reference arithmetic, exact parameters, pair values and verification output in a reproducible workflow.

## Where to get it

- Starter/replay kit: `downloads/poseidon-api-teaching.zip`
- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### Replay the Pallas Poseidon reference API with its complete numerical inputs

- Original path: `research/poseidon/orchard/exec_r2e/poseidon_ref.py`
- SHA-256: `344246fc03ae862cd42beabcade902edea45d23df6cb62751f741c3df636f171`
- Usage guide: `guide.html?id=0d6796439c0042f3a445`
- Source/download: `record.html?id=0d6796439c0042f3a445`
- Detailed README in the archive: `guides/0d6796439c0042f3a445.md`
- Finite test report: `verification/poseidon-api-bounded-runtime.json`

### Poseidon recorded-pair replay: three lower-round witnesses, not the selected higher-round target

- Original path: `research/poseidon/pkg_r7_paper/out_draft/experiments/replay_pairs.py`
- SHA-256: `497ce3f69860a10e518908f46163bb984cd9ed20ce7c184004fb236e3bd65b1c`
- Usage guide: `guide.html?id=509b777772c70fab6cee`
- Source/download: `record.html?id=509b777772c70fab6cee`
- Detailed README in the archive: `guides/509b777772c70fab6cee.md`
- Finite test report: `verification/poseidon-recorded-pairs-bounded-runtime.json`

### Poseidon toy root fractions: exact small tables, not a deployed-field success law

- Original path: `research/poseidon/pkg_r7_paper/out_draft/experiments/toy_root_fraction.py`
- SHA-256: `6f4b8b3a39f962c4452b9df5b7b90d860233b1f65051fb17a3be0b790ecbd280`
- Usage guide: `guide.html?id=5a93fcbde58389394b07`
- Source/download: `record.html?id=5a93fcbde58389394b07`
- Detailed README in the archive: `guides/5a93fcbde58389394b07.md`
- Finite test report: `verification/toy-root-bounded-runtime.json`

### Poseidon collision logs: require a verified record, not just exit zero

- Original path: `research/poseidon/orchard/exec_r2e/verify_collision.py`
- SHA-256: `c78a48a119c772c52450cd3fed27d30f11538289695baf44534ed1b2be9e62c2`
- Usage guide: `guide.html?id=7aa7512323dbb4c5c4d0`
- Source/download: `record.html?id=7aa7512323dbb4c5c4d0`
- Detailed README in the archive: `guides/7aa7512323dbb4c5c4d0.md`
- Finite test report: `verification/poseidon-log-contract-report-bounded-runtime.json`

### Check the small-field radix-3/radix-2 transform layout

- Original path: `research/poseidon/orchard/exec_r2c/src/pfa_check.py`
- SHA-256: `bfe828a480c84fe49e416cda4212ab9942c34d0651c6732aa868a624487a53c6`
- Usage guide: `guide.html?id=e943f7b9f7eda124ec2d`
- Source/download: `record.html?id=e943f7b9f7eda124ec2d`
- Detailed README in the archive: `guides/e943f7b9f7eda124ec2d.md`
- Finite test report: `verification/pfa-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python 3.10+ and its standard library; no pip packages, solver or network.
- Keep all eight v2 teaching-kit files together, including MANIFEST.json. Numerical inputs, API adapter and copied-source log harness are included. The organizer program and paper behind historical references remain excluded.

### Replay the complete finite API recipe

Working directory: The extracted poseidon-api-kit directory

```text
python -B replay.py
```

Expected: JSON with passed=true, 74 named API checks, 33 distinct_witnesses, five mutated_profiles, 20 rejected_invalid_inputs and twelve log-checker cases. These are existing r1-r5 records, not new collisions, organizer verification or a measured success probability.


### Inspect the exact numerical target without importing the API

Working directory: The extracted poseidon-api-kit directory

```text
python -B -c "import json; d=json.load(open('finite-witnesses.json')); p=d['parameters']['poseidon']; print(len(p['round_constants_hex']),len(p['mds_hex']))"
```

Expected: 64 3: the parameter set has 64 rows of round constants and three MDS rows. This shape observation alone does not certify their values; the replay verifies the pinned dataset hash and crosscopy controls.

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
