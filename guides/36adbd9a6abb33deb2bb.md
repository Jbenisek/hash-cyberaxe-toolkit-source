# shapegraph

Source: `research/newpaths/shape_odd/shapegraph.py`

Public SHA-256: `e4d715b6ad77f89632b95ba101768b143cbddadaa4dbc6f8e750877527940d6d`

## Purpose recorded in the source

Exact shape facts (32-bit, no sampling).  Owner: shape_odd agent.
1. call-message graph: each message word links its round-0 call and its round-1 call -> cycle decomposition.
2. lattice symmetries: the 4x4 state is a torus Z4 x Z4 with rows = roles (a,b,c,d), columns and diagonals =
   G lines.  Find every map (r,c) -> (r, e*c + s*r + t) that sends columns to columns and diagonals to
   diagonals, its induced message-word map, whether it commutes with the message permutation, and whether
   it fixes the initial state.
3. Moebius / slide: the unique message M* whose round 0 returns the initial state (one round is a bijection,
   inverse formulas of ../../sol_answer_W_newpaths.md 3.3); then 2-round(M*) == 1-round(P M*).
4. Circle: per-word rotation-invariant sets and the birthday on rotation classes.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "math",
  "random",
  "sys",
  "toy"
]
```

## Entry points

```json
[
  {
    "name": "call_message_graph",
    "line": 21,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "lattice_symmetries",
    "line": 60,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "rol",
    "line": 88,
    "arguments": [
      "x",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "inverse_round0",
    "line": 92,
    "arguments": [
      "X"
    ],
    "doc": "Sol 3.3: the unique message m with round0(init, m) = X (32-bit)."
  },
  {
    "name": "moebius_fixed_point",
    "line": 126,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "circle",
    "line": 144,
    "arguments": [],
    "doc": ""
  }
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
