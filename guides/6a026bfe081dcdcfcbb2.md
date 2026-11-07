# Profile a concrete SHA-256 pair: values, signed rows and raw condition counts

Source: `research/game/climber/guided/kit/char_pair_profile.py`

Public SHA-256: `1b9e8011a2104447f9941cc19134a13abd56191c2bd834985f9ef7dc85ee8611`

## Reviewed usage contract

A Python reference evaluator and characteristic profiler. It expands two messages, evaluates full 32-bit reduced-step SHA-256 from one chosen chaining value, records internal A/E words and derives signed difference rows. Its C1 total is a deterministic metric of that trajectory, not an independently calibrated attack probability or complete work price.

## Source inspection and available execution evidence

static-source-review; bounded-finite-controls-passed; other modes not runtime-certified.

profile performs two N-step state evaluations plus two schedule expansions and row/count formatting. That is 2N SHA-256 step iterations, not a complete machine-operation count. For n>=16, each expansion adds n-16 schedule words. No SAT solver, Monte Carlo sampling or unbounded loop is part of this module's documented computation.

## Declared inputs

**profile(cv, m1, m2, n, t0=16, koff=0)**: cv has eight integer words, each message sixteen integer words, and n is the compression-step count. Use canonical unsigned 32-bit words and 1<=n<=64 with 0<=koff and n+koff<=64. The API does not validate all these boundaries. koff selects a different constant window, which changes the experiment.

**Command-line words**: --cv requires eight hexadecimal words, --m1 and --m2 sixteen each. Spaces or commas separate words. parse_words masks parsed integers to 32 bits rather than rejecting overwide or negative values; use exactly eight hex digits per word for an unambiguous public record. --n and --t0 are integers; --koff shifts the constants.

**Preset precedence**: --preset pin39b selects the source's published external numerical control and overrides supplied CV/message arguments. With a preset, n is a.n or the preset's n, so --n 0 falls back to the preset rather than validating zero. The teaching-kit guide instead uses the two separately attributed JSON seeds.

**Representation**: Rows print bit 31 on the left. u means side 1 bit 1 / side 2 bit 0; n means 0 / 1; a dash means equal with value unspecified; 0/1 mean equal with that value. Initial A rows -1,-2,-3,-4 are a,b,c,d; E rows are e,f,g,h. Schedule W indices start at zero.

**Optional files**: --xml-char writes signed rows; --xml-pinned writes a positive-control shape; --json writes the summary/count/row subset. Existing output files are overwritten. A parent directory must already exist. --values changes printed equal-bit representation, not the internal compression model.

## Outputs and interpretation

**API profile**: Returns n,t0,w, per-step counts, total, signed rows, value rows, A1/A2/E1/E2 trajectories, W1/W2 schedules and collision. State dictionaries include negative chaining indices; schedule lists retain all sixteen input words even for a shorter target.

**collision**: Tests equality of the eight final working-state words and inequality of expanded W[:n]. With a common CV, working-state equality also yields equal feed-forward output. The function does not return a padded standard-IV hash. For n<16 its distinctness test examines only the first n message words, so it can reject pairs differing solely in unused input words.

**C1 total**: For t>=t0, sum differing A bits, differing E bits, Maj-condition bits and Ch-condition bits. Maj counts exactly one differing input; Ch counts some differing input except both f and g differing. W differences are reported but are not an extra term in that sum. Correlated/implied conditions and arithmetic feasibility prevent reading this count as an automatic -log2 probability theorem.

**XML exports**: The signed export preserves the pair's A/E/W path. The pinned export fixes initial CV bits and W0..15 values/signs, keeps expanded W signed, frees intermediate A/E rows and marks the last four A/E rows equal. That export only describes an intended positive control if the concrete seed really collides; export does not refuse a noncollision.

**Exit behavior**: A well-formed noncolliding pair still prints collision=False and exits zero. argparse usage failures generally exit 2; several explicit sys.exit(string) validation failures exit 1 despite the opening docstring's broad exit-2 description. Check the actual collision field, not exit zero alone.

## Imports

- Python standard library only. The profile module has a main guard; importing it defines functions/constants without launching a search or writing output files.
- The teaching ZIP includes the module, two seed JSON files and a wrapper that checks hashes before importing it. No solver or third-party Python package is needed.

## Entry points

```json
[
  {
    "name": "R",
    "line": 52,
    "arguments": [
      "x",
      "k"
    ],
    "doc": ""
  },
  {
    "name": "s0",
    "line": 53,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "s1",
    "line": 54,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "expand",
    "line": 57,
    "arguments": [
      "W",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "states",
    "line": 63,
    "arguments": [
      "chain",
      "W",
      "n",
      "koff"
    ],
    "doc": "A[t], E[t] for t = -4..n-1 as dicts (t -> 32-bit value); chaining rows per the sha_cnf convention."
  },
  {
    "name": "popcount",
    "line": 75,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "maj_cond_mask",
    "line": 78,
    "arguments": [
      "da",
      "db",
      "dc"
    ],
    "doc": "bit mask of Maj positions with exactly one differing input (rule C1)."
  },
  {
    "name": "ch_cond_mask",
    "line": 83,
    "arguments": [
      "de",
      "df",
      "dg"
    ],
    "doc": "bit mask of Ch positions with some differing input and not both f and g differing (rule C1)."
  },
  {
    "name": "signed_row",
    "line": 88,
    "arguments": [
      "x",
      "y",
      "values",
      "w"
    ],
    "doc": "row of w characters, bit w-1 first: '-' (or the value when values=True) where equal, 'u'/'n' where the copies differ."
  },
  {
    "name": "profile_from_values",
    "line": 98,
    "arguments": [
      "A1",
      "A2",
      "E1",
      "E2",
      "W1",
      "W2",
      "n",
      "t0",
      "w"
    ],
    "doc": "the C1 price of a pair given its state words A/E (dicts t=-4..n-1) and schedule words W (lists, length >= n).\nReturns dict: 'steps' (per-step dicts for t=-4..n-1), 'total' for t >= t0, signed 'rows' and value 'vrows', collision flag."
  },
  {
    "name": "profile",
    "line": 125,
    "arguments": [
      "cv",
      "m1",
      "m2",
      "n",
      "t0",
      "koff"
    ],
    "doc": "expand both messages, run both computations from the chaining value cv, and price the pair (rule C1)."
  },
  {
    "name": "xml_text",
    "line": 132,
    "arguments": [
      "n",
      "rowsA",
      "rowsE",
      "rowsW",
      "comment",
      "w"
    ],
    "doc": ""
  },
  {
    "name": "pinned_xml",
    "line": 141,
    "arguments": [
      "pr"
    ],
    "doc": "positive-control instance: cv rows as 0/1, W0..15 as 0/1/u/n, W16.. as signed rows, states free, last 4 rows equal."
  },
  {
    "name": "char_xml",
    "line": 151,
    "arguments": [
      "pr"
    ],
    "doc": "stage-1 characteristic: signed differences only ('-'/u/n) on every state and W row."
  },
  {
    "name": "print_profile",
    "line": 156,
    "arguments": [
      "pr",
      "values"
    ],
    "doc": ""
  },
  {
    "name": "parse_words",
    "line": 167,
    "arguments": [
      "s",
      "k",
      "name"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 174,
    "arguments": [
      "argv"
    ],
    "doc": ""
  }
]
```

[Download the teaching kit](../../downloads/boardpair-teaching.zip).

## Worked examples

### Inspect the 38-step project seed through the API

Working directory: The extracted boardpair-kit directory

```text
python -B -c "import sys,json; sys.path.insert(0,'kit'); import char_pair_profile as c; s=json.load(open('boardpairs/wit/r38_s102.json')); p=c.profile(*[[int(x,16) for x in s[k]] for k in ('cv','M1','M2')],38); print(p['collision'],p['total']['cond'])"
```

Expected: True 84. This is the raw C1 total for this concrete seed, not 2^-84 as a proved search-success probability.

### Use the protected complete-kit replay

Working directory: The extracted boardpair-kit directory

```text
python -B replay.py
```

Expected: Both finite seeds and the abc control pass; all six negative controls are rejected. The wrapper validates source hashes and uses a separate compression checker for the witness controls. It reports the two raw C1 totals 61 and 84 without treating them as probabilities.

## Example runs and tests

API profile for both seeds and full abc control; the exact documented r38 API example prints True 84. Raw C1 counts are not probabilities. The runtime report identifies tested bytes, not every function or mode in the tool.

[Read the check report](../../verification/pair-profiler-bounded-runtime.json).

## Read alongside

- research/game/climber/MAP_README.md
- research/game/climber/README.md

## Failure modes

- Do not infer collision validity or a probability law from a zero exit status or the field name price.
- Malformed API vectors can raise indexing errors; CLI masking can silently change an overwide or negative input.
- Nonzero koff changes the constant window and is not ordinary prefix-round SHA-256.
- For two different CVs, internal-state equality alone is not equal feed-forward output; this API's profile takes one shared CV.
- Do not use the positive-control XML export on a noncolliding seed without checking its predicate.
- The unused pin39b preset is external published numerical data, not a new project discovery or a paper redistribution license.
- The source's discussion of raw condition counts is not an independent theorem establishing unbiased, independent or feasible trials.
