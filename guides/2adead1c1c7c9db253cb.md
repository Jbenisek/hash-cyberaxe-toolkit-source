# W11 representative sampler: inspect class selection and stopping

Source: `research/game/climber/guided/n39steer/classvals3.py`

Public SHA-256: `1426268bf71aa102111997cf52647467e245e3db73ddf1d2a040feb0a14defb7`

## Reviewed usage contract

Sample one X word for each requested modular small-sigma class under the historical signed W11 row, preserving a hardcoded original witness word for its class. This is a historical data producer with a reproduced subset-stopping defect, not a general complete representative solver.

## Source inspection and available execution evidence

static-source-review; hardcoded-seed-and-three-subset-boundary-controls-passed-in-temporary-copies.

At most two million scalar draws, but completion is not guaranteed and the stopping comparison is incorrect when the seed class is absent from the requested set. A sampling cap or successful process exit is not an exhaustive no-root proof or a cost guarantee for producing complete messages.

## Declared inputs

**Current-directory files**: Reads base39.xml row 11 and class_set_W11.tsv. Nonempty non-comment table rows supply class from field one and status from field three. Duplicate class labels overwrite earlier statuses. The class labels are exact strings.

**Fixed row and original seed**: Interprets u,n,- as in the class enumerator. Inserts X=01003fbb into got even when its class is not requested, then asserts that its class is 2000bea0. This assertion checks the class, not general compliance of the seed with a replacement signed row.

**Sampling**: Uses random.seed(39), then x=(getrandbits(32) AND free_mask) OR fixed_n_bits. At most 2,000,000 draws. Newly sampled classes are retained only when present in the requested table.

## Outputs and interpretation

**CLASSVALS3.tsv**: Overwrites one row per requested class in input insertion order: class, hexadecimal X, and copied status. An unresolved class receives dash and MISSING. A missing class does not force a nonzero exit.

**Printed totals**: Prints requested class count, len(got), and sample count. len(got) includes the hardcoded seed even if it was not requested, so found is not necessarily the number of requested classes resolved.

## Imports

- Python standard library. Do not use -O: the original's hardcoded-class assertion would be disabled.
- The linked rank-and-table kit checks the already archived representatives; it does not claim to reconstruct this sampler's random selection.

[Download the teaching kit](../../downloads/w11-class-recount.zip).

## Worked examples

### Check the complete archived data safely

Working directory: The extracted w11-class-kit folder

```text
python -B replay.py
```

Checks the signed row, modular class and all 1,152 stored values with a separate rank certificate. This is data verification, not execution of the sampler.

Expected: passed=true and representatives_checked=1152. The local class proof does not certify a whole-message success law.

### Inspect a new request before regenerating

Working directory: A disposable directory containing the original source and validated copies of base39.xml and class_set_W11.tsv

```text
python -B classvals3.py
```

The unmodified source is suitable only for investigating its historical behavior. For arbitrary subsets, repair and separately test the stop condition to check requested-set coverage, validate the seed's domain, and explicitly fail on unresolved rows. Never overwrite the research's original tables while experimenting.

Expected: CLASSVALS3.tsv may include MISSING even for reachable classes. Validate every requested row; exit status and printed found are insufficient.

## Example runs and tests

Six synthetic producer-interface cases. Tiny enumerator covers four values only; the separate rank proof and finite dataset replay certify the archived full domain. Representative subset failure does not invalidate the independently checked full historical table. The runtime report identifies tested bytes, not every function or mode in the tool.

[Read the check report](../../verification/w11-representative-contract-report-bounded-runtime.json).

## Read alongside

- research/game/climber/MAP_README.md
- research/game/climber/README.md

## Failure modes

- The loop compares len(got) to len(want), not the size of their intersection. For one reachable requested class other than 2000bea0, it performs zero draws and writes MISSING. For two such classes it can stop after finding only one. Both behaviors were reproduced.
- With an empty request it prints classes 0 found 1 samples 0. Do not use the found total as a completeness check.
- The archived 128-class request includes the seed class and its full saved table passes independent verification. The subset defect does not invalidate those saved representatives.
- A replacement row may violate the hardcoded seed's bit constraints even if its class assertion passes. Validate signed-row membership for every output word separately.
- Case-sensitive class strings, parser assumptions and the finite draw cap can leave MISSING entries. These are not evidence that the requested class is unreachable.
- A valid representative is a local word value only; it does not establish schedule consistency or a SHA-256 collision.
