# Template filler: expand a selected row into an output file

Source: `research/launch/port/filltmpl.py`

Public SHA-256: `4622198f9a101ee7d2ab09f87cf61bb70a9bb4ba9b0df828e3c155314781ad79`

## Reviewed usage contract

Expand a selected values row into a template and write a new LF-normalized text file. It treats scalar values as replacement strings and a standalone B slot as a sequence of lines.

## Source inspection and available execution evidence

static-source-review; synthetic-roundtrips-repeated-slot-and-block-type-controls-passed.

One pass through template lines and their substitutions, plus output size. It does not price or evaluate the content it writes.

## Declared inputs

**CLI**: python filltmpl.py TEMPLATE VALUES_JSON ROW_KEY OUTPUT . VALUES_JSON must contain ROW_KEY; all referenced scalar slots must be strings, and B slots must be lists of strings.

**Substitution**: A line exactly {{B<number>}} is expanded with list.extend. Other lines substitute any {{word_characters}} key through a regular expression. Repeated scalar names are accepted; the companion extractor does not accept the same repeated named group.

## Outputs and interpretation

**OUTPUT**: Overwrites the chosen output file in UTF-8 with LF separators. It creates no missing parent directory and prints nothing on ordinary success.

## Imports

- Python standard library; no compiler, solver or proof verifier.

[Download the teaching kit](../../downloads/template-contracts.zip).

## Worked examples

### Replay filling and type-boundary behavior

Working directory: Extracted template-contracts-kit folder

```text
python -I -B replay.py
```

All writes are confined to disposable generated fixtures.

Expected: Ten documented interface cases pass, including the deliberately malformed B-slot example.

### Fill a synthetic row

Working directory: A scratch folder containing tools/ and templates made from synthetic notes

```text
python -B tools/filltmpl.py templates/note.txt.tmpl templates/note.txt.vals.json r39 rebuilt.txt
```

Validate the values schema first, then compare rebuilt.txt with the intended source using binary reads or hashes.

Expected: A normally silent successful exit and a rebuilt LF-normalized text file. Success alone does not establish byte identity.

## Example runs and tests

Ten disposable text-template interface controls. No actual research/submission package, verifier, server or solver was run. Text reconstruction is not scientific validity or a price proof. The runtime report identifies tested bytes, not every function or mode in the tool.

[Read the check report](../../verification/template-filltmpl-contract-report-bounded-runtime.json).

## Read alongside

- research/launch/port/README.md

## Failure modes

- No runtime schema check: B0='ab' produces two lines a and b instead of rejecting the string.
- Missing row or slot keys raise KeyError; non-string scalar values can fail during replacement.
- An existing output is overwritten. Use a new scratch destination, not a live proof or claim.
- Text reconstruction does not imply byte preservation, legal cryptographic inputs, correct dependencies or valid cost assumptions.
