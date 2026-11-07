# ---------------------------------------------------------------- optimized (still exact) evaluation

Source: `research/poseidon/impl/poseidon_own.py`

Public SHA-256: `78f360797c10a26c36327fe0773df91285733f1e76cfd6a54d91b0e5a2a198d0`

## Purpose recorded in the source

Our own Orchard PoseidonHash<ConstantLength<2>> (P128Pow5T3, Pallas base field) with a round-prefix parameter.

t=3, rate 2, capacity 1, S-box x^5, R_F=8 (rounds 0-3, 60-63), R_P=56 (rounds 4-59), 64 rounds.
Round i: state += RC[i]; S-box (all 3 lanes if full, lane 0 if partial); state = MDS * state.
Hash: init [m0, m1, 2^65], one permutation, digest = state[0]. No feed-forward.
Constants come from constants_own.py, generated from the PUBLIC halo2_poseidon-0.2.0 fp.rs (gen_constants.py).
Written independently; the PR 923 program was used only as DATA for cross-checking (see check_pr_constants.py).

Op counting (cost rule: one modular add or mult incl. squaring = 1 primitive):
  sbox  = 2 squarings (x^2, x^4) + 1 mult (x^5)        -> 3 mults (2 of them squarings)
  ARK   = 1 add per lane
  MDS   = 3 mults + 2 adds per output lane
Counter keeps add, sqr, mul separately (mul = non-squaring mults); mults_total = sqr + mul.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "constants_own"
]
```

## Entry points

```json
[
  {
    "name": "is_full_round",
    "line": 40,
    "arguments": [
      "i"
    ],
    "doc": ""
  },
  {
    "name": "_add",
    "line": 44,
    "arguments": [
      "a",
      "b",
      "c"
    ],
    "doc": ""
  },
  {
    "name": "_mul",
    "line": 48,
    "arguments": [
      "a",
      "b",
      "c"
    ],
    "doc": ""
  },
  {
    "name": "_sbox",
    "line": 52,
    "arguments": [
      "x",
      "c"
    ],
    "doc": ""
  },
  {
    "name": "mds_mul",
    "line": 59,
    "arguments": [
      "s",
      "c",
      "rows"
    ],
    "doc": ""
  },
  {
    "name": "round_fn",
    "line": 72,
    "arguments": [
      "s",
      "i",
      "c",
      "rows"
    ],
    "doc": "One deployed round i (0-based). `rows` limits which MDS output lanes are computed (None for the rest)."
  },
  {
    "name": "perm",
    "line": 83,
    "arguments": [
      "state",
      "rounds",
      "counter",
      "digest_only"
    ],
    "doc": "First `rounds` rounds of the deployed permutation (rounds in 0..64; 0 = identity).\ndigest_only=True computes only MDS row 0 in the LAST executed round (other lanes returned as None)."
  },
  {
    "name": "hash_prefix",
    "line": 95,
    "arguments": [
      "m0",
      "m1",
      "r",
      "counter",
      "digest_only"
    ],
    "doc": "Digest (field element) of the Orchard ConstantLength<2> hash truncated to the first r rounds."
  },
  {
    "name": "hash_prefix_bytes",
    "line": 101,
    "arguments": [
      "data",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "hash_prefix_opt",
    "line": 109,
    "arguments": [
      "m0",
      "m1",
      "r",
      "counter",
      "pre"
    ],
    "doc": "Same digest, fewer executed primitives, for fixed programs that hard-code derived constants:\n  (a) lane 2 of round 0 is the constant K=2^65+RC[0][2]: its S-box and MDS column are precomputed constants,\n      and the per-row constant M[i][2]*K^5 is folded into the next round's constants (or, for r==1, added once);\n  (b) the last executed round computes only MDS row 0.\n`pre` (Counter) receives the o"
  },
  {
    "name": "expected_counts",
    "line": 142,
    "arguments": [
      "r",
      "digest_only"
    ],
    "doc": "Analytic counts for perm(.., r) from the structure (adds, sqr, mul)."
  }
]
```

## Read alongside

- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
