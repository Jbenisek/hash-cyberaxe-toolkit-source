# SHA-256 saved-stage analyzer: parse counts and stage labels

Source: `research/retest/dig38_1029/analyze.py`

Public SHA-256: `457bdde652008dfbce2389eeb123b38d3b3cc11a8d2f5a43084234a5154ef843`

## Reviewed usage contract

The historical analyzer reads optional tests.txt and tests2.txt lists, then out/<name>.txt logs in the current directory. It prints one summary per listed test. It is a text parser, not a sampler or a verification of the recorded message pairs.

## Source inspection and available execution evidence

static-source-review; Copied saved-log parser, three parser edge controls and finite synthetic classifier checks; no cryptographic trials.

Linear text parsing of the supplied logs; each child in the finite publication check has a five-second timeout. The printed historical rates and UBgain=1+3/EX0 are not a runtime or attack-cost certificate.

## Declared inputs

**Exact edition and safe working directory**: Use the pinned source bytes. For the public worked example, download downloads/dig38-verdict-replay.zip and work inside its extracted dig38-verdict-kit folder. The kit checks source hashes and uses disposable copies; do not execute the historical record builder against a live research directory.

**Historical evidence boundary**: Saved labels and sums are not independent collision verification, an exhaustive necessity proof or a justified sampling law. The saved process resamples particles. A large sample count does not itself establish independent trials.

**Native file format**: Each nonempty non-comment test-list line is split once at | into a test name and description. Logs use VTAG class 0 and 1, prefix log2 P(rows 6..21), VSTAGE row and exit lines. Both VTAG classes are needed when a class table is present. No command-line options are parsed.

## Outputs and interpretation

**Analyzer labels**: N1=0 prints NO-VIOLATOR. Otherwise EX1=0 prints NECESSARY; a positive EX1 prints LEVER?. These are source-defined diagnostic labels, not publication proof verdicts.

**Counts and stages**: The b14R log parses to N0=201326592, EX0=8032, N1=0 and EX1=0, with six prefix estimates and earlier surviving row-16 violators. The parser reports the mean of the saved log2 prefix estimates, not a pooled success probability.

**Missing and repeated input behavior**: A missing log prints NOT DONE. A log containing only class 0 raises KeyError rather than NOT DONE. Repeated VTAG classes keep their last occurrence instead of summing them. All three behaviors were checked on disposable fixtures.

## Imports

- Python 3.9+ standard library for the portable kit. No network, compiler, solver or original workspace is needed.
- The source parser uses paths relative to the working directory. The public kit supplies a copied log and a disposable test-list fixture.

## Entry points

```json
[
  {
    "name": "load",
    "line": 5,
    "arguments": [
      "n"
    ],
    "doc": ""
  }
]
```

## Worked examples

### Replay the saved label transformation safely

Working directory: Extracted dig38-verdict-kit folder from downloads/dig38-verdict-replay.zip

```text
python -I -B replay.py
```

Expected: passed=true; analyzer NO-VIOLATOR; extracted builder NECESSARY for the earlier surviving row-16 class. Three synthetic analyzer branches pass. builder_top_level_executed=false. No research experiment is launched.

## Example runs and tests

Copied analyzer and four extracted classifier branches; saved-log sums and malformed/missing controls. No builder file-writing top level, sampling, collision verification, necessity proof or confidence-law certification. The runtime report identifies tested bytes, not every function or mode in the tool.

[Read the check report](../../verification/dig38-analyzer-bounded-runtime.json).

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- A repeated class tag overwrites the earlier count. Concatenating logs is not a supported pooling method.
- Malformed list lines or a partial class table can fail with an exception. NOT DONE does not cover all incomplete-input shapes.
- The N1=0 branch takes priority even if other fields are inconsistent. No semantic consistency validator or cryptographic verification is present.
- The last false-collision count and exit code are reported; the first E16 set size is used. These selections do not audit the entire experiment.
- Do not interpret an earlier nonzero VSTAGE count followed by zero final violators as an exhaustive impossibility proof.
