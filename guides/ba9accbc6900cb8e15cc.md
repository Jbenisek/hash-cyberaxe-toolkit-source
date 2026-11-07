# SHA-3 ablation summary: failures, paired baselines and cumulative events

Source: `research/dig/incoming/sha3-r5-U01/work2/summ_drop.py`

Public SHA-256: `d08b8c36a1b694f03a3d8301a768f9fd7ed2e22eb715e37b7bffe603b703ca49`

## Reviewed usage contract

Read saved drop-group JSON lists, group records by the omitted constraint group, and report successful degrees of freedom, failure labels, cumulative event totals and paired DF changes. This is a descriptive summary, not a validating data parser or an exact attack probability calculator.

## Source inspection and available execution evidence

static-source-review; six-disposable-read-only-summary-fixtures-passed; no-connector-run.

Read-only linear aggregation over the matched records; the saved dataset has 252 records. No underlying research samples are regenerated and no discovery-cost inference follows from this inexpensive recount.

## Declared inputs

**Current directory file selection**: No arguments. Reads sorted glob matches drop_k[0-9]*.json from the current working directory, not the script directory. A backup such as drop_k1_backup.json also matches and is counted again.

**Record lists**: Each JSON file contains records with att, drop and status. For status=ok it expects DF, EM, npts and four ev_F_R0_R1_R2 integers. Other status labels are counted as failures without requiring successful-sample fields.

**Paired baseline**: Within each file, the last drop=none record for an attempt becomes that attempt's baseline. All records still contribute to totals, including repeated attempts. DF differences are reported only when both that record and its selected baseline have status=ok.

**Archived finite dataset**: The reviewed edition has seven files for seeds 1,2,5,6,8,9,11: six attempts times six group choices per file, 252 total records. These same numerical tables are in the SHA-3 local-objects kit's data directory.

## Outputs and interpretation

**Printed summary**: Prints matched filenames and, for each drop label, record count, ok count, min/max DF, counts of failed statuses, four summed events, total sampled points and min/max paired DF change. It writes no files.

**Event interpretation**: The columns are F, R0, R0-and-R1 and R0-and-R1-and-R2. The final three are cumulative events, not independent estimates to multiply. A saved zero final-event count is not a zero-probability theorem.

**Fixture evidence**: Six bounded cases check the archived totals, empty input, a synthetic paired difference, repeated attempts, a matching backup filename and an out-of-range event count. The source faithfully aggregates the valid archive but does not reject all malformed or duplicate data.

## Imports

- Python standard library only. No Keccak implementation, solver, NumPy, generator or network is imported by this summary.

[Download the teaching kit](../../downloads/encoder-summary-contracts.zip).

## Worked examples

### Check the summary contract before reusing it

Working directory: The extracted encoder-summary-kit folder

```text
python -I -B replay.py
```

Python 3.10 or later, standard library only. The kit supplies this source, all seven tables and its bounded checker, alongside the separate encoder checks. Do not use Python -O.

Expected: passed=true with six summary fixtures: the valid 252-record archive and synthetic cases for empty input, paired differences, duplicate records, backup filenames and invalid event totals. It does not certify a connector-conditioned success law.

### Recount the archived data without launching its generator

Working directory: research/dig/incoming/sha3-r5-U01/work2 inside the extracted encoder-summary-kit

```text
python -I -B summ_drop.py
```

This folder contains the script and seven numerical tables. Run from this directory, because its file glob is relative to the current working directory. Do not add backup copies matching drop_k[0-9]*.json.

Expected: Six groups, each runs=42. The unmodified group has 23 ok records, DF 35..53 and cumulative events [736,736,736,0] of 736. Dropping F has 28 ok records, DF 462..485 and [0,896,896,0] of 896. These remain historical finite observations.

## Example runs and tests

Six bounded read-only summary fixtures, not a connector rerun, independent sampling claim or zero-probability theorem. Original archived numerical data were separately recounted by the SHA-3 local-objects kit. The runtime report identifies tested bytes, not every function or mode in the tool.

[Read the check report](../../verification/sha3-ablation-summary-bounded-runtime.json).

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- An empty directory prints [] and succeeds; this is missing data, not proof that an experiment had zero outcomes.
- Backup copies and repeated records inflate counts. The summary does not deduplicate or certify independent trials.
- Duplicate baseline attempts select the last baseline while counting every row, changing paired differences.
- Counts larger than npts and violations of cumulative-event ordering are not rejected.
- The summary does not verify DF=1600-EM, seed identity, exact group completeness or the scientific meaning of a status label. The separate SHA-3 local-objects kit supplies a stricter manifest-bound recount for the archived dataset.
- Minimum and maximum observed DF values are not exhaustive bounds on every possible generated object.
