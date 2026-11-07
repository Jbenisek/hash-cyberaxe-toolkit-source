# parent up

Source: `research/newpaths/counter_swing/around/parent_up.py`

Public SHA-256: `6bb2f3d6fb3292ff8d5ff45ba08adcba518b4f35cca59bcab46bb840254eb054`

## Purpose recorded in the source

parent_up.py - collisions placed at a parent node (item 3): two different child-CV pairs, same parent output.
A parent has cv = IV, counter 0, length 64, flags 4 on both sides, so the only difference is in its message.
Cases: (a) the right child half-collides (its CV words 0,2,5,7 equal, 1,3,4,6 differ: the 55/63 output moved up
one level): parent message words 9, 11, 12, 14 differ; (b) one random right-child word differs (m8);
(c) two words of the left child differ (m2, m3, the pair a column could absorb if there were a d difference).
Prints at w = 32 and w = 8: fraction with the round-0 state equal, mean number of state words that differ after
round 0, and the digest-half equality counts.  Lemma G2 (a G call with equal input state is injective in
(x, y)) predicts round 0 never cancels.
Run: python -B parent_up.py

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "numpy",
  "tb3"
]
```

## Entry points

```json
[
  {
    "name": "run",
    "line": 20,
    "arguments": [
      "w",
      "n",
      "batches",
      "rng"
    ],
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
