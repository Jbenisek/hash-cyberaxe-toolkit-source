# judge common lines

Source: `research/pkg10/pkg/review/judge_common_lines.py`

Public SHA-256: `1e6cb6c41f663e7c8c5547024a8c475a51d55241111404eeaab05a671f12ea7d`

## Purpose recorded in the source

Review helper (lens: judge). Sentences of pkg6's public files that are word for word in pkg5's as well and that
carry a figure, a name of a lemma or a file: these are the places where something false could be left over.
Writes review/judge_common_proof.txt and review/judge_common_note.txt. Reads only.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "pathlib",
  "re",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "sentences",
    "line": 15,
    "arguments": [
      "text"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/pkg10/pkg/review/judge_common_proof.txt

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
