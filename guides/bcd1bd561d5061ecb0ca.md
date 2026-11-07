# gen cuda

Source: `research/newpaths/untried/b3-thi-walk/real/gen_cuda.py`

Public SHA-256: `34178e08e67394569aa535f399842c0d85e25ba60c28c3348f16d1a05519c592`

## Purpose recorded in the source

gen_cuda.py - generate CUDA sources for the real 32-bit walk measurement from the SHIPPED program (research only).

co_lines.inc : the 77 lines of step CO of experiments/frontline.py (LINES), with the single walk change
               K1.a1 = ROL(K1.d1,16) XOR thi, as C statements over uint32 (inputs: the seven outer words, Y4, fl, thi)
tables.inc   : the flat byte automata F1 (test (1) on Y9) and F2 (test (2) on omega) of frontline.py, restricted to S
consts.inc   : constants (Y3, Y11, DY11, X15, IV, BETA, EPS, TAUS, Q* and class masks)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "os",
  "sys",
  "walk_model"
]
```

## Entry points

```json
[
  {
    "name": "nm",
    "line": 18,
    "arguments": [
      "s"
    ],
    "doc": ""
  },
  {
    "name": "src",
    "line": 22,
    "arguments": [
      "e"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 47,
    "arguments": [],
    "doc": ""
  }
]
```

## Read alongside

- research/newpaths/untried/b3-thi-walk/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
