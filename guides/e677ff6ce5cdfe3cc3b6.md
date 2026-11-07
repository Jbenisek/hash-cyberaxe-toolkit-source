# pdftext

Source: `research/newpaths/scout_cross/pdftext.py`

Public SHA-256: `ea384f7a366431359024ce218a368aebda818a10f87c92d18aec3296e07110df`

## Purpose recorded in the source

Crude PDF text extraction (zlib streams + Tj/TJ operators). Windows python, stdlib only.
Usage: python pdftext.py in.pdf out.txt

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "re",
  "sys",
  "zlib"
]
```

## Entry points

```json
[
  {
    "name": "strings_from_stream",
    "line": 5,
    "arguments": [
      "s"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 28,
    "arguments": [
      "inp",
      "outp"
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
