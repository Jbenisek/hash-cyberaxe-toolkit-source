# SHA-256 r39 joint walk: inspect the kernel and reconstruction filters

Source: `research/pkg_r39_combined/work/dk/experiments/r39joint.py`

Public SHA-256: `538b062d52fecc6cc97ba200175657e13c17483083da6b9e06537ed5b3b0c781`

## Reviewed usage contract

The archived program generates a Boolean walk kernel specialized to a chaining value, gathers distinguished-point matches, reconstructs claws and filters W9, W8 and W17 before checking both 39-step compression outputs. The embedded common-chosen-CV pair is an existing specimen, not a newly found standard-IV collision. The full attack mode also tries to derive a chaining value from a shared first block.

## Source inspection and available execution evidence

static-source-review; Copied pinned-source finite arithmetic, 1024 kernel/scalar comparisons, six graph fixtures, stubbed edge paths and empty CLI controls; no attack or walk window.

Finite CLI controls have a ten-second child timeout in the publication checker. Nonzero windows and --attack are not bounded examples. Historical operation allowances, observed success rates and large stopping budgets are not certified by these source-contract checks.

## Declared inputs

**Exact edition**: Use the pinned distributed file from this record. The two reviewed archive paths contain identical bytes. Current workspace files differ only in line endings, but the runtime report binds the distributed SHA-256, not a guessed newer edition.

**Finite source export**: --gen-c prints the embedded freestanding C generator and exits. It does not compile or execute it. The zero-window interface --windows 0 --out zero.json writes an empty JSON array to the selected path; it is not an experiment or benchmark.

**JSON interface**: Without --gen-c, --windows or --attack, the program reads stdin JSON with experiment_id and trials. IDs are r39-transplant-claw and r39-window-small. Each trial supplies trial and a hexadecimal seed string; only its first 16 characters are converted. Empty trial lists return an empty schema-version-1 response.

**Real work and optional backend**: --windows N runs real windows; the default window size is 2^26 lane steps, not a small website example. --attack has very large historical window/work limits. R39_WASM selects an external Wasmtime module if available; otherwise generator work uses the declared 575000 fallback charge. The publication checks disabled that environment override.

## Outputs and interpretation

**Finite checks actually performed**: 32 fixed-seed scalar identity fixtures verify W1=u and the W16 walk-residual relation. Four generated Python kernels, across two chaining values and both register-bank directions, agree with the source scalar fstep on 1024 word comparisons, including the low-seven-bit distinguished-point aggregate.

**Existing specimen**: The embedded pair matches the full numerical identity of p_li39tab23s1_luna in the earlier independently replayed collection. Its two outputs agree at 39 steps and a one-bit mutation fails. This source-contract check is internal consistency plus identity linking, not another independent digest implementation or a new discovery.

**Counted model versus elapsed time**: The Mach model charges basic operations 1, branches 2 and loads/stores 3; generated bitwise instructions are counted separately. Two tested kernels have 734 instruction records and modeled register counts 131 and 133. These are finite cases, not universal bounds or CPU measurements. A window diagnostic prints modeled ops, component counts, elapsed seconds and observed matches.

**Component grouping**: count_groups builds a bipartite graph of the two word values. Six tiny fixtures show it ignores the first tuple component (the CV identity). Use it only within one CV or group externally before combining windows.

## Imports

- Python 3 standard library for the finite source export and copied checks; no compiler, network, solver or full research workspace.
- Optional wasmtime and a compatible R39_WASM module alter generator accounting. The finite publication check does not certify the C or WebAssembly backend.
- The full search is self-contained but computationally substantial. Do not run --attack or nonzero --windows as a routine replay check.

## Entry points

```json
[
  {
    "name": "ror",
    "line": 6,
    "arguments": [
      "x",
      "k"
    ],
    "doc": ""
  },
  {
    "name": "S0",
    "line": 7,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "S1",
    "line": 8,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "s0",
    "line": 9,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "s1",
    "line": 10,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "CH",
    "line": 11,
    "arguments": [
      "e",
      "f",
      "g"
    ],
    "doc": ""
  },
  {
    "name": "MAJ",
    "line": 12,
    "arguments": [
      "a",
      "b",
      "c"
    ],
    "doc": ""
  },
  {
    "name": "expand",
    "line": 18,
    "arguments": [
      "w",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "traj",
    "line": 22,
    "arguments": [
      "cv",
      "w16",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "compress",
    "line": 32,
    "arguments": [
      "cv",
      "w16",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "inF",
    "line": 44,
    "arguments": [
      "w",
      "D",
      "T"
    ],
    "doc": ""
  },
  {
    "name": "consts",
    "line": 45,
    "arguments": [
      "cv"
    ],
    "doc": ""
  },
  {
    "name": "fstep",
    "line": 52,
    "arguments": [
      "x",
      "c"
    ],
    "doc": ""
  },
  {
    "name": "recover_a1",
    "line": 57,
    "arguments": [
      "cv",
      "a0",
      "u"
    ],
    "doc": ""
  },
  {
    "name": "build",
    "line": 61,
    "arguments": [
      "cv",
      "a0",
      "a1"
    ],
    "doc": ""
  },
  {
    "name": "second",
    "line": 81,
    "arguments": [
      "W"
    ],
    "doc": ""
  },
  {
    "name": "claw_pair",
    "line": 86,
    "arguments": [
      "cv",
      "a0",
      "u"
    ],
    "doc": ""
  },
  {
    "name": "_build_by_bit",
    "line": 93,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "solve_row_exact",
    "line": 112,
    "arguments": [
      "A0",
      "E0",
      "W0",
      "A1",
      "E1",
      "W1",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "invert_downward",
    "line": 143,
    "arguments": [
      "A_top",
      "E_top",
      "W"
    ],
    "doc": ""
  },
  {
    "name": "verify_advice_construction",
    "line": 149,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "count_groups",
    "line": 176,
    "arguments": [
      "dset"
    ],
    "doc": ""
  },
  {
    "name": "allocate",
    "line": 236,
    "arguments": [
      "g",
      "out",
      "acc",
      "dst_bank",
      "dpreg",
      "nfixed"
    ],
    "doc": ""
  },
  {
    "name": "to_source",
    "line": 263,
    "arguments": [
      "recs",
      "name",
      "dpreg"
    ],
    "doc": ""
  },
  {
    "name": "build_folded",
    "line": 277,
    "arguments": [
      "consts5",
      "src_bank",
      "dst_bank",
      "dpb"
    ],
    "doc": ""
  },
  {
    "name": "consts5",
    "line": 326,
    "arguments": [
      "c"
    ],
    "doc": ""
  },
  {
    "name": "make_kernels_folded",
    "line": 329,
    "arguments": [
      "c",
      "dpb"
    ],
    "doc": ""
  },
  {
    "name": "mS0",
    "line": 519,
    "arguments": [
      "m",
      "v"
    ],
    "doc": ""
  },
  {
    "name": "mS1",
    "line": 521,
    "arguments": [
      "m",
      "v"
    ],
    "doc": ""
  },
  {
    "name": "ms0",
    "line": 523,
    "arguments": [
      "m",
      "v"
    ],
    "doc": ""
  },
  {
    "name": "mMAJ",
    "line": 525,
    "arguments": [
      "m",
      "a",
      "b",
      "c"
    ],
    "doc": ""
  },
  {
    "name": "mCH",
    "line": 526,
    "arguments": [
      "m",
      "e",
      "f",
      "g"
    ],
    "doc": ""
  },
  {
    "name": "a32",
    "line": 527,
    "arguments": [
      "m",
      "a",
      "b"
    ],
    "doc": ""
  },
  {
    "name": "s32",
    "line": 528,
    "arguments": [
      "m",
      "a",
      "b"
    ],
    "doc": ""
  },
  {
    "name": "table_words",
    "line": 544,
    "arguments": [
      "wdig"
    ],
    "doc": ""
  },
  {
    "name": "_e1",
    "line": 937,
    "arguments": [
      "i",
      "sd"
    ],
    "doc": "r39-transplant-claw (proof Section 10)"
  },
  {
    "name": "_e2",
    "line": 972,
    "arguments": [
      "i",
      "sd"
    ],
    "doc": "r39-window-small (proof Section 10)"
  },
  {
    "name": "_t4",
    "line": 998,
    "arguments": [
      "sd"
    ],
    "doc": ""
  },
  {
    "name": "serve",
    "line": 1012,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "main",
    "line": 1033,
    "arguments": [],
    "doc": ""
  }
]
```

## Worked examples

### Inspect the in-program C generator without running it

Working directory: Disposable folder containing the downloaded pinned r39joint.py

```text
python -I -B r39joint.py --gen-c
```

Expected: The embedded C source is printed. No compiler, kernel walk or output file is invoked.

### Check the empty diagnostic interface

Working directory: Disposable folder containing the downloaded pinned r39joint.py

```text
python -I -B r39joint.py --windows 0 --out zero.json
```

Expected: Exit 0, no stdout, and zero.json contains []. This checks serialization only; no research window is run.

## Example runs and tests

Copied pinned source only: existing specimen identity, 32 scalar identities, 1024 generated-kernel comparisons, six component fixtures and finite CLI controls. No attack, walk windows, probability sample, C/WASM compilation or full price certification. The runtime report identifies tested bytes, not every function or mode in the tool.

[Read the check report](../../verification/r39joint-bounded-runtime.json).

## Read alongside

- research/pkg_r39_combined/work/dk/experiments/manifest.json
- research/pkg_r39_combined/work/dk/proof.md

## Failure modes

- No dedicated --help parser exists: unrecognized arguments fall through to the stdin JSON interface.
- Missing trials raises KeyError; unknown experiment IDs exit nonzero. The interface does not provide a comprehensive request validator.
- The internal run_window(iters=0) uses the default window because zero is false in its conditional. This is different from the safe CLI --windows 0. Stubbed control-flow fixtures verified the distinction without a real walk.
- If all eight kernel setup attempts reject, --windows can dereference ks=None while formatting its summary. A mocked failure path reproduces TypeError; no real rejection frequency was measured.
- A nonzero r39-window-small request runs substantial work. Trial indices above 4 yield rows without observations, rather than a completed experiment.
- Both JSON message fields remain null even for observations about an embedded pair. Observation labels are not message-pair certificates.
- Source assertions disappear under python -O. Do not use optimized mode for evidence checks.
- A recorded component count is not a distinct-independent-trial count. Kernel caps, generator fallback charges, sampling laws and the complete attack price require separate justification.
- The archived credits name prior contributors. The publication adds a bounded usage review, not a blanket novelty or reuse-license claim.
