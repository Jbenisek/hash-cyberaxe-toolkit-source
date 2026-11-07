# BLAKE3 original five-round compact edition: check both capacity limits

Source: `research/blake3_r5/compact/pkg/blake3/experiments/bsrho.py`

Public SHA-256: `e75d5ad818fb012736b4b5761608f1147ba430f15095535cd8f58214fda251ed`

## Reviewed usage contract

The original five-round compact package and its pre copy contain identical source bytes. Their 31,606-operation binary circuit is independently checked on this source, not inferred from the four-round version. The compact representation declares 207,120 code bytes and a larger endpoint table than the uniform 36-byte B5 layout. Fresh inspection also finds separate trail-field and long-immediate gaps. Historical predecessor attributions remain in the source.

## Source inspection and available execution evidence

static-source-review; Own-pin finite digest/allocation, generated-code inspection, field packing, synthetic recovery and supplied-budget ledger. No default optimization or original search..

One fixed circuit construction/allocation, tested with a ten-second subprocess limit. No default numerical model, optimization or original collision campaign.

## Declared inputs

**Target used by this implementation**: Five-round BLAKE3 with unit 1054: a full block of 32 zero bytes followed by little-endian x, standard IV, counter 0, length 64 and flags 11. Some header prose still says seven rounds; executable ROUNDS=5 and UNIT=1054 drive this implementation.

**Masked walk and compiler**: The walk is f XOR q. A batch has 256 bit-sliced lanes, 31,606 binary instructions and 771 allocated registers in 16 compiler chunks. Packed recovery uses seven 36-bit lanes and 1,072 primitive operations.

**Ten-byte fields**: Use unsigned 64-bit keys and unsigned 16-bit trail IDs. The finite test accepts trail 65,535 and rejects 65,536. Negative -1 aliases the all-ones fields, so validate nonnegative integers before packing.

**Bounded entry point**: The example constructs and allocates the circuit only. Do not launch historical --selftest, --stats, a default plan, embedded-C builds or collision searches to reproduce it. Use a disposable directory containing the exact downloaded source.

## Outputs and interpretation

**Fresh finite equivalence**: Independent digest comparisons cover 256 fixed lanes and two known answers. Allocation/chunk equivalence, two rejected mutations, a two-step masked chain and packed recovery controls pass. They do not establish a universal hash-generator or attack-success proof.

**Trail-field capacity and budget envelope**: The declared capacity is 79,940 records. The permitted start-count envelope is 256+79,940+1=80,197, exceeding the 65,536-value trail field. The plan construction accepts that envelope, while packing rejects 65,536. This is a concrete interface/accounting gap, not evidence that an actual target trajectory reaches the overflowing value.

**Large recovery immediates cross the byte limit**: Generated recovery contains eight large q-mask immediates. Under the source five/36-byte encoding, charging these as short instructions omits at least 8×31=248 bytes. The declared 1,048,504-byte search phase becomes at least 1,048,752, or 176 over 1 MiB. This lower bound is not a complete repaired layout or a new adjudication.

**Operation ledger and scoring model**: The source constants are step=31,606, handler=34, body=31,643, code=207,120 and table=79,940. Setup/search phases are 311,904/1,048,504 declared bytes. At supplied Tp=22 and B=100000000000000000000000000000000000, the integer ledger gives N=10302496048561015212815230542948125809248. This fixture is not the optimized default price; the capacity boundaries remain attached.

**Synthetic control flow**: Six artificial one-batch cases cover a returned pair, a miss and budget exits. Four common-endpoint recovery graphs take 5, 7, 4 and 2 oracle calls. Four packing roundtrips and two overflow rejections pass. These are interface controls, not real-hash collision witnesses.

## Imports

- Python 3 standard library for the finite example.
- The two source routes have identical SHA-256 bytes; surrounding package manifests are not declared identical.

## Entry points

```json
[
  {
    "name": "_ror",
    "line": 32,
    "arguments": [
      "v",
      "k"
    ],
    "doc": ""
  },
  {
    "name": "digest_words",
    "line": 36,
    "arguments": [
      "m",
      "rounds",
      "flags",
      "blen",
      "counter"
    ],
    "doc": "Compression of the single block m (16 words) with chaining value IV, counter 0, length 64, flags 11 (CHUNK_START|CHUNK_END|ROOT):\n8 digest words v[i] XOR v[i+8], `rounds` rounds (5 for the target)."
  },
  {
    "name": "f_scalar",
    "line": 56,
    "arguments": [
      "x",
      "n",
      "key"
    ],
    "doc": "f(x): the low n bits of the digest of the message key(32 bytes) || x.  key = 0 is the target."
  },
  {
    "name": "message",
    "line": 63,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "build_packed",
    "line": 131,
    "arguments": [
      "qw"
    ],
    "doc": "The recovery circuit for the walk g = f XOR q: the plain 5-round compression of the block 0^32 || x followed by one XOR of each of the 8\noutput words with the 32-bit word of q (a word that is 0 costs no operation).  qw = the 8 words of q."
  },
  {
    "name": "packed_circuit",
    "line": 166,
    "arguments": [
      "qw"
    ],
    "doc": ""
  },
  {
    "name": "packed_f",
    "line": 173,
    "arguments": [
      "xs",
      "n",
      "qw"
    ],
    "doc": "g on up to 7 values at once with the packed recovery circuit (g = f XOR q, low n bits; qw = the 8 words of q)."
  },
  {
    "name": "_ror_planes",
    "line": 290,
    "arguments": [
      "A",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "_constw",
    "line": 294,
    "arguments": [
      "v"
    ],
    "doc": ""
  },
  {
    "name": "trace",
    "line": 298,
    "arguments": [
      "n"
    ],
    "doc": "The network of the 5-round digest of the block 0^32 || x (chaining value IV, flags 11), x = low n bits of the input planes (planes >= n are 0).\nInput planes are upright; output plane j is the signal (node, neg): the plane the circuit stores is the node, so the stored value is the digest\nplane XOR neg."
  },
  {
    "name": "allocate",
    "line": 444,
    "arguments": [
      "st"
    ],
    "doc": "Register assignment of the straight line: input plane j and output plane j both live in register j (the chain feed is\nrenaming, no moves); temporaries take the lowest free register above n.  Returns (instructions as (op, dst, a, b) with\nregister numbers, number of registers used).  Raises if output j would have to be written while input j is still needed."
  },
  {
    "name": "run_allocated",
    "line": 474,
    "arguments": [
      "st",
      "code",
      "planes"
    ],
    "doc": "Execute the allocated code on a register file; returns the first n registers (the next input planes)."
  },
  {
    "name": "_tmasks",
    "line": 487,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "transpose",
    "line": 502,
    "arguments": [
      "rows"
    ],
    "doc": "Transpose a 256 x 256 bit matrix given as 256 integers of 256 bits (bit c of rows[i] = element (i, c))."
  },
  {
    "name": "pack_lanes",
    "line": 517,
    "arguments": [
      "xs",
      "n",
      "pin"
    ],
    "doc": "Stored input planes (low n) for up to 256 lane values."
  },
  {
    "name": "lanes_of",
    "line": 523,
    "arguments": [
      "planes",
      "n",
      "pin"
    ],
    "doc": "All 256 lane values (n bits) from n stored planes."
  },
  {
    "name": "lane_value",
    "line": 529,
    "arguments": [
      "planes",
      "l",
      "pin",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "set_lane",
    "line": 536,
    "arguments": [
      "planes",
      "l",
      "x",
      "pin",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "stage1_ops",
    "line": 579,
    "arguments": [
      "pin",
      "s1"
    ],
    "doc": "Operations of the stage-1 test (mask of lanes whose s1 low digest bits are zero): OR over the positive planes, AND over\nthe inverted planes, one complement if both kinds occur, one combine, one final complement; plus compare and branch."
  },
  {
    "name": "stage1",
    "line": 590,
    "arguments": [
      "planes",
      "s1",
      "pin"
    ],
    "doc": "Mask of lanes whose s1 low digest bits are all zero."
  },
  {
    "name": "_plan",
    "line": 611,
    "arguments": [
      "n",
      "Tp",
      "kappa",
      "tmax",
      "Sb"
    ],
    "doc": ""
  },
  {
    "name": "tail_log2",
    "line": 630,
    "arguments": [
      "mean",
      "k"
    ],
    "doc": "log2 of the Chernoff bound exp(-mean) (e mean / k)^k on P(count >= k), k > mean."
  },
  {
    "name": "step256",
    "line": 638,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "other_code",
    "line": 644,
    "arguments": [
      "st"
    ],
    "doc": "Instructions besides the main body: handlers 1,000, recovery (the packed circuit with the 8 XORs of q, plus 47), setup, cut and slice 160."
  },
  {
    "name": "machine_constants",
    "line": 650,
    "arguments": [
      "st",
      "R"
    ],
    "doc": "(PH, FILT, BODY, code bytes, tmax) of the n = 256 program with R registers (spill loads and stores added to the body)."
  },
  {
    "name": "gen_scratch",
    "line": 661,
    "arguments": [
      "nodes"
    ],
    "doc": "Scratch bytes of the runtime generator (the C port GEN_C, two passes, no node table): 8-bit use counts (a node is used up to 15 times at 7 rounds), one byte per node, for the nodes of the n = 256 network\n(constant, 256 inputs, one per gate), the signal state, the shadow stack and the result record.  Returns (total, use counts, nodes)."
  },
  {
    "name": "gen_idle",
    "line": 670,
    "arguments": [
      "tmax"
    ],
    "doc": "Bytes of the region that holds the table, the register file, and the counters and plane copy once the search runs; while the generator\nruns the search has not started and the same region holds the generator's code image and its scratch."
  },
  {
    "name": "phase_bytes",
    "line": 676,
    "arguments": [
      "code",
      "tmax"
    ],
    "doc": "(setup phase, search phase) resident bytes.  Setup: main code (as large as the final code, written as the generator emits it), advice,\nthe counters and plane copy, the generator's code image (GEN_CODE instructions) and its peak scratch.  Search: main code, advice, table,\nregister file, counters.  The generator is never called after setup; its image and scratch are overwritten by the table and the "
  },
  {
    "name": "plan",
    "line": 683,
    "arguments": [
      "n",
      "kappa",
      "Tp",
      "R"
    ],
    "doc": ""
  },
  {
    "name": "ledger",
    "line": 705,
    "arguments": [
      "p",
      "st",
      "R"
    ],
    "doc": "Operation budget in word operations (exact Fractions); units are operations / 1054 (C of blake3-r5)."
  },
  {
    "name": "_lossq",
    "line": 721,
    "arguments": [
      "Tp",
      "q",
      "tmax",
      "kappa",
      "Sb",
      "rate",
      "fine",
      "coarse"
    ],
    "doc": "Lemma 2 of proof Section 4 for q = Q / L trails; `rate` scales the collision hazard (H1 (d) sensitivity)."
  },
  {
    "name": "_b256",
    "line": 757,
    "arguments": [
      "Tp",
      "tmax",
      "kappa",
      "Sb"
    ],
    "doc": "The least B (multiple of GRAIN) with P_lower >= P_MIN."
  },
  {
    "name": "loss",
    "line": 772,
    "arguments": [
      "p",
      "rate"
    ],
    "doc": "The probability losses of proof Section 4 (floats): the terms, their sum and the lower bound on the success probability."
  },
  {
    "name": "is_dp",
    "line": 816,
    "arguments": [
      "x",
      "p"
    ],
    "doc": "Mixed distinguished point: low s1 bits zero and the window above them below Tp."
  },
  {
    "name": "dp_key",
    "line": 821,
    "arguments": [
      "x",
      "p"
    ],
    "doc": "The kb bits above the window, then the fb low bits of the window value (which determine it)."
  },
  {
    "name": "pack_entry",
    "line": 826,
    "arguments": [
      "key",
      "t"
    ],
    "doc": ""
  },
  {
    "name": "unpack_entry",
    "line": 831,
    "arguments": [
      "e"
    ],
    "doc": ""
  },
  {
    "name": "trail_lengths",
    "line": 835,
    "arguments": [
      "p",
      "r",
      "ts",
      "f2"
    ],
    "doc": "Pass 1 of the recovery: both trails (numbers ts) walk together from their starts, one packed batch per step, until each has\nreached a distinguished point; returns the two lengths.  More than capr steps is a halt."
  },
  {
    "name": "recover",
    "line": 851,
    "arguments": [
      "p",
      "r",
      "t0",
      "t1",
      "f2"
    ],
    "doc": "t0, t1 = the numbers of two finished trails with the same end.  Returns (x, y), x != y, f(x) = f(y), or None.  Pass 1 recomputes\nthe two lengths; pass 2: the longer trail moves alone for l1 - l2 steps, then both move together (two lanes of the packed circuit)."
  },
  {
    "name": "search",
    "line": 874,
    "arguments": [
      "eng",
      "p",
      "r",
      "cnt"
    ],
    "doc": "One attempt with the fresh random word r: the pair (x, y) or None.  Raises Halt at a budget.  Budgets: B batches,\ne2max stage-1 hits, tmax table keys, cmax cut trails, a recovery of at most capr batches."
  },
  {
    "name": "derive",
    "line": 927,
    "arguments": [
      "seed",
      "tag",
      "bits"
    ],
    "doc": ""
  },
  {
    "name": "attempt",
    "line": 931,
    "arguments": [
      "eng",
      "p",
      "seed",
      "tag"
    ],
    "doc": ""
  },
  {
    "name": "t1_run",
    "line": 948,
    "arguments": [
      "seed",
      "n"
    ],
    "doc": "Family law, fresh random key K: steps until the first repeat of x -> low n bits of digest(K || x)."
  },
  {
    "name": "e1_trial",
    "line": 957,
    "arguments": [
      "seed",
      "eng",
      "ideal_cls"
    ],
    "doc": "T3 (target, organizer-checked pair) and the ideal control, one attempt each; T1 as an observation."
  },
  {
    "name": "t2_columns",
    "line": 975,
    "arguments": [
      "digs"
    ],
    "doc": "The seven projections (T2_NAMES) of each 256-bit digest, as seven lists of B_T2-bit values:\nword 0, word 3, word 7, xor of the 8 words, sum of the 8 words, and two 22-bit concatenations of 11-bit pieces."
  },
  {
    "name": "e2_trial",
    "line": 988,
    "arguments": [
      "seed",
      "tr",
      "st256"
    ],
    "doc": "T2: M_T2 points of the target function (the block 0^32 || x, K = 0) at width 256 (source by trial index: uniform inputs, counter r + i, or iterates of g\nfrom 256 random starts), the 256-bit digests f(x) = (stored planes) XOR q, equal pairs in seven 21-bit projections.  w0 is the checked event."
  },
  {
    "name": "serve",
    "line": 1029,
    "arguments": [
      "req"
    ],
    "doc": ""
  },
  {
    "name": "selftest",
    "line": 1049,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "print_ledger",
    "line": 1113,
    "arguments": [
      "lg"
    ],
    "doc": ""
  },
  {
    "name": "stats",
    "line": 1123,
    "arguments": [
      "trials"
    ],
    "doc": "Run the two experiments locally on pseudo-random seeds and print the counts (descriptive only, no inference is drawn from them)."
  }
]
```

## Worked examples

### Compile without starting a search

Working directory: A disposable directory with the hash-checked original five-round compact bsrho.py

```text
python -I -B -c "import runpy; m=runpy.run_path('bsrho.py',run_name='bounded_copy'); s=m['step256'](); c,r=m['allocate'](s); print(s.ops,r)"
```

Expected: 31606 771

## Example runs and tests

Exact-copy identities, fresh finite kernel/allocation, field-capacity boundary, generated-immediate inspection and supplied-budget ledger. No default optimization, actual overflowing target trajectory, new adjudication, retained generator or success/price certificate. Also fresh own-pin field packing, artificial one-batch search/two-pass recovery and compiler-only example. Synthetic graphs are not collision witnesses. The runtime report identifies tested bytes, not every function or mode in the tool.

[Read the check report](../../verification/compact-r5-bounded-runtime.json).

## Read alongside

- research/blake3_r5/compact/pkg/blake3/experiments/manifest.json
- research/blake3_r5/compact/pkg/blake3/proof.md

## Failure modes

- This source uses 64/16-bit fields; do not silently transfer another edition’s 63/17-bit fix or plan guard.
- Do not count every instruction as five bytes when recovery embeds 256-bit masks.
- A permitted budget envelope exceeding a field is not proof of a reached real-hash overflow.
- Some source prose is stale; read executable ROUNDS=5 and UNIT=1054.
- Synthetic returned pairs are not real BLAKE3 witnesses.
- No earlier select-gate verdict or retained generator result is transferred to this binary source.
