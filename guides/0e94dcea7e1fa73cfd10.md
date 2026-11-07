# fmt pkg6

Source: `research/pkg9/pkg/tools/fmt_pkg6.py`

Public SHA-256: `a501af19f2c864c21ac5c7da619df2a54eb13a10e4455a1b513f1a0262ff5d7a`

## Purpose recorded in the source

Format checks for the pkg6 files, the line ranges that claim.json cites, and the arithmetic of the claim.

    python -B tools/fmt_pkg6.py [--write-ranges] [--fix-eol]

--write-ranges  first renders the package from src/ and tools/pkg6_data.py (tools/build_pkg6.py); the evidence
                ranges of claim.json are part of that rendering, because claim.json is a rendered file.
--fix-eol       rewrites CRLF as LF in the checked files.
Without options nothing is written: the files on disk are checked as they are, and the tool says whether they
still are what the templates give (a rendered file that was edited by hand shows up as DRIFT).
Exit status 0 only if nothing is wrong. Research helper, not submitted.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "build_pkg6",
  "json",
  "math",
  "pathlib",
  "pkg6_data",
  "re",
  "subprocess",
  "sys"
]
```

## Read alongside

- research/pkg9/pkg/tools/proof_lines_check.py
- research/pkg9/pkg/tools/proof_lines_pkg7.py

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
