# heur

Source: `research/newpaths/untried/b3-heur/heur.py`

Public SHA-256: `796da2c2fca37d19f836fed1faf9aeca5b554d78b2e1a9baac8f2e7f9bf1e1fb`

## Purpose recorded in the source

heur.py  (untried/b3-heur; research only; run inside WSL Ubuntu, one CPU process at a time)

Non-gradient heuristic for the class choice of E3 (layer r1d, free const, counter base): simulated annealing over
ONE member e1 = Y3 + Y4 (Y4 is an outer word on the counter path, so one member is enough), scored by the team's
exact counter tool pair_calc_sub (beta* = 18b0e098 alone, pin H8; the same call as counter_next/stack/run_cube.sh with
-cube ffffffff e1).  Per-member rates (normalisation of scan_y4.py, free = 0):
    total = sum_j L_j N_j / 2^64  over every row      (the objective of the stack's greedy scan; best known 76,161,024)
    S     = the same sum over the six front-line taus  (class value 67,633,152, the map's Section 2.6 figure)
Phase A: e1 inside the front-line class (e1 AND 03cf8303) = 030c0303, 19 free bits, eta = 830303cf.
Phase B: all 32 bits of e1 free; eta = ROR(e1 XOR (e1 + DY3), 16) is recomputed per point, so every point is a valid
         member of its own class (a different class choice whenever a class-fixed bit flips).
Energy = -score, score = log2(S) * 64 + log2(total) in phase A (lexicographic: S first, total breaks ties) and
score = log2(total) in phase B.  Geometric temperature, 1-3 bit flips, restart after a stall.
Usage: python3 heur.py SECONDS SEED [PHASE_A_SHARE]

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "math",
  "os",
  "random",
  "rates",
  "subprocess",
  "sys",
  "time"
]
```

## Entry points

```json
[
  {
    "name": "ror",
    "line": 32,
    "arguments": [
      "x",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "eta_of",
    "line": 36,
    "arguments": [
      "e1"
    ],
    "doc": ""
  },
  {
    "name": "score_A",
    "line": 80,
    "arguments": [
      "r"
    ],
    "doc": ""
  },
  {
    "name": "score_B",
    "line": 85,
    "arguments": [
      "r"
    ],
    "doc": ""
  },
  {
    "name": "anneal",
    "line": 89,
    "arguments": [
      "ev",
      "rng",
      "phase",
      "start",
      "bits",
      "score",
      "t_hi",
      "t_lo",
      "deadline",
      "trace"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 132,
    "arguments": [],
    "doc": ""
  }
]
```

## Read alongside

- research/newpaths/untried/b3-heur/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
