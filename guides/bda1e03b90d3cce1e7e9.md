# Exact ledger of the entry, integers only (standard library). Run: python3 -B ledger.py

Source: `research/dig/incoming2/blake3-r2-G02-U04/work/ledger_new.py`

Public SHA-256: `e8e8a7785a97d0ea0aa201b59e232ea5df57f36c404623ae0547bf5e423815d1`

## Purpose recorded in the source

Exact ledger of the entry, integers only (standard library). Run: python3 -B ledger.py
BASE reproduces the ledger of 7c2264a8 (57.3737); NEW is this entry (changes 1 to 10 are those of c994a61f, 11 to 13 new). Each row is machine units (430 make one unit of time).
exact kept counts of the 16 member classes (type t, e1[2], e1[26], e1[27]); the classes have 32,768 members each
Parameters. pass_count: words per 2^32 passed by test (1); u_*: machine units; mu_millionths: MU in millionths of a unit per outer step;
pre: call-only lane units debited with the screen; words: boundary words per live block (old: k words, new: ceil((E + b L)/7));
partial: partial words per live block; setup/piece/wrap/ranges/pieces: live-block units and counts; final_per_chunk: units to write
both messages for one chunk; u_word: the word row with its test (u_wt); u_pf: the prefilter of every word (kept words 1/8 + s).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "math"
]
```

## Entry points

```json
[
  {
    "name": "cdiv",
    "line": 4,
    "arguments": [
      "a",
      "b"
    ],
    "doc": ""
  },
  {
    "name": "ledger",
    "line": 32,
    "arguments": [
      "c"
    ],
    "doc": ""
  },
  {
    "name": "certificate",
    "line": 64,
    "arguments": [
      "n"
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
