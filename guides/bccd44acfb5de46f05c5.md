# Poseidon r56 packed walk: inspect recovery and conditional costs

Source: `research/levers_1022/pos_r56_fix2/rho.py`

Public SHA-256: `b5bd922909b12d8871b381c7a1bc4255541241b45df0adb18fe5ad4c3f53773c`

## Reviewed usage contract

A historical full-round Orchard-style Poseidon design: two-round affine input parametrization, 807-operation equivalent walk map, packed distinguished-point table, bounded recovery, and integer parameter/charge derivation. Its actual fixed-map success claim depends on H1; reproducing the ledger does not prove that premise.

## Source inspection and available execution evidence

static-source-review; bounded-plan-packing-and-tiny-graph-checks-passed; no full-field search or tuning.

The bounded kit uses only fixed-size fixtures and graph domains at most four. The historical attempt has about 2^127 trail steps and must not be used as a smoke test. Python elapsed time and RSS are not the abstract-machine operation and memory ledger.

## Declared inputs

**Finite CLI modes**: python rho.py --plan computes the historical ledger; no argument also means plan. --listing prints the step program. --selftest includes 24 reduced-bit sampled walks and word-machine checks; --tune runs parameter descent. Unknown flags, including --help, silently return without a useful result. Import constructs the line, step program and constant recipes.

**Field and round domain**: The declared target uses the hardcoded prime, three-lane state [m0,m1,2^65], eight full plus 56 partial rounds, and state[0] output without feedforward. Inputs are canonical field elements. This r56 label means 56 partial rounds, 64 total rounds.

**Step and message APIs**: message(W) maps a field parameter injectively to two field inputs. make_F(kappa) interprets its argument as a nonzero multiplicative factor in this BCD variant, despite older additive-rho wording in some docstrings. Its mutable register array must not be shared concurrently. attempt(coin) masks two integers to 254 bits and maps zero kappa to one.

**Search preconditions**: search takes a deterministic map, distinguished-point predicate, start, block-multiple step budget, table capacity and recovery caps. The step budget must be a nonnegative multiple of UNROLL=18; it is documented but not enforced. Stored distinguished values must fit 142 bits; index gaps fit 119. _put ORs into zeroed storage, not overwriting an existing field.

## Outputs and interpretation

**Finite plan**: Returns an exact integer numerator and declared memory calculation, plus floating display logs and fixed-point model-success arithmetic. Replayed numerator 137215184878174913969505127226939604471902, reference price 1392 and nominal memory 1048568 bytes. These are reproduced model outputs, not a complete implementation-price proof or physical RAM measurement.

**Search result**: Returns (pair or None, status, evaluations, operation counters). Status distinguishes found, exhausted steps, table overflow, gap width, recovery gap and start-on-cycle. A first repeat from a pure cycle is not a pair of distinct predecessors.

**Bounded publication evidence**: 17066 exhaustive graph/start/DP-subset cases on domains 1..4: 4408 valid tiny-map pairs, 6329 start-on-cycle and 6329 exhausted steps. Also 1536 packed-field boundary checks, five line points and nine equivalent-step/reference comparisons. The 4408 pairs are not Poseidon collisions and give no full-field rate.

## Imports

- Python 3.9+ standard library. The offline lesson includes the exact recovered source, checker, wrapper, README and identity manifest.
- The historical submission note is currently unavailable in the publication audit; source-level fixtures do not recover its full machine-listing and lifetime proofs.
- No solver, network, external PDF or original repository is required by the bounded kit.

## Entry points

```json
[
  {
    "name": "_round",
    "line": 102,
    "arguments": [
      "st",
      "i"
    ],
    "doc": "Round i of the reference permutation on the state st (list of 3 field elements)."
  },
  {
    "name": "digest",
    "line": 111,
    "arguments": [
      "m0",
      "m1"
    ],
    "doc": "Digest of the Orchard hash of the two canonical field elements (m0, m1): initial state [m0, m1, 2^65], all rounds, output state[0]."
  },
  {
    "name": "enc",
    "line": 119,
    "arguments": [
      "x"
    ],
    "doc": "Canonical 32-byte little-endian encoding (x < P)."
  },
  {
    "name": "inv",
    "line": 129,
    "arguments": [
      "a"
    ],
    "doc": ""
  },
  {
    "name": "root5",
    "line": 133,
    "arguments": [
      "a"
    ],
    "doc": ""
  },
  {
    "name": "line",
    "line": 137,
    "arguments": [],
    "doc": "The input line on which rounds 0 and 1 are affine.  Round 0 maps (m0, m1) to U = (m0 + c00)^5, V = (m1 + c01)^5 (a bijection) and a constant\nthird lane; the round-1 S-box input is then affine in (U, V).  On (U, V) = (U0 + a tau, V0 + b tau) its lane 0 is constant (M00 a + M01 b = 0)\nand its lanes 1, 2 are d_i tau, so the S-box gives d_i^5 tau^5: with W = tau^5 the state after round 1 is A + W B.\nm"
  },
  {
    "name": "message",
    "line": 154,
    "arguments": [
      "W"
    ],
    "doc": "The two message elements of the line point W."
  },
  {
    "name": "after_round1",
    "line": 160,
    "arguments": [
      "m0",
      "m1"
    ],
    "doc": ""
  },
  {
    "name": "build_step",
    "line": 221,
    "arguments": [],
    "doc": "The step program: from x (register x) to F(x) = digest(message(x + rho0)) / OUTSCALE (register x), as a straight-line list of\nfield operations (op, dest, src1, src2) with op ADD or MUL.  Register names: x (walk value), e0..e2 (attempt registers e_i = E0_i + rho0),\nk<n> (constants, values in the returned dict), y*, z*, h*, u, x5, t1, t2 (working).  Equivalent form of rounds 2..63:\nevery lane is hel"
  },
  {
    "name": "kappa_consts",
    "line": 405,
    "arguments": [
      "kappa"
    ],
    "doc": "The attempt's register values for the coin kappa (D): every step constant K_j(1) kappa^(e_j), e_1, e_2, and OUTSCALE_kappa."
  },
  {
    "name": "make_F",
    "line": 414,
    "arguments": [
      "rho0"
    ],
    "doc": "F(x) = digest(message(x + rho0)) / OUTSCALE, computed by executing the step program (every operation of STEP once).\nWith D, rho0 is the multiplicative coin kappa and F(x) = digest(message(kappa x - E0_0)) / OUTSCALE_kappa."
  },
  {
    "name": "table_words",
    "line": 459,
    "arguments": [
      "m"
    ],
    "doc": "Words of a table of m packed entries, plus one pad word: every field read loads the word holding its first bit and the next one."
  },
  {
    "name": "_get",
    "line": 464,
    "arguments": [
      "tw",
      "off",
      "width"
    ],
    "doc": "The field of `width` bits at bit offset off (it spans at most two words: off mod 256 + width <= 255 + 142 < 512)."
  },
  {
    "name": "_put",
    "line": 470,
    "arguments": [
      "tw",
      "off",
      "v"
    ],
    "doc": "OR the field value v (v < 2^142) into the zeroed bits at bit offset off: two read-modify-writes."
  },
  {
    "name": "search",
    "line": 477,
    "arguments": [
      "F",
      "is_dp",
      "x0",
      "steps",
      "mcap",
      "gmax",
      "gpos"
    ],
    "doc": "Single-trail collision search on the map F: x_0 = x0, x_i = F(x_{i-1}), UNROLL steps per block.  Every x_i (i >= 1) with is_dp(x_i) is\nstored as one packed entry (x, i - previous stored index); the start x_0 (index 0) is kept in its own word.  Halts (failure) after `steps`\nevaluations (a multiple of UNROLL), when the table already holds `mcap` points at a new one, when an index gap reaches 2^119, "
  },
  {
    "name": "words",
    "line": 682,
    "arguments": [
      "n"
    ],
    "doc": ""
  },
  {
    "name": "number",
    "line": 686,
    "arguments": [
      "w"
    ],
    "doc": ""
  },
  {
    "name": "dp_count",
    "line": 690,
    "arguments": [
      "T"
    ],
    "doc": "Exact count over the field: p = 2^254 + c with c = p mod 2^128 >= T, so exactly (2^126 + 1) * T of the p field elements are distinguished."
  },
  {
    "name": "other_fixed",
    "line": 695,
    "arguments": [
      "m"
    ],
    "doc": "Table scans, insertions, the two index passes, constant loads, the message roots, table zeroing (4 per word) and MISC, for m entries."
  },
  {
    "name": "ledger_ops",
    "line": 700,
    "arguments": [
      "ops",
      "nstep"
    ],
    "doc": "Word and field operations of a run, from its counters (nstep = |STEP|)."
  },
  {
    "name": "ledger",
    "line": 705,
    "arguments": [
      "S",
      "gmax",
      "m",
      "d"
    ],
    "doc": "The worst-case total (word operations) of the attempt without the preprocessing term: every halt charged at its limit\n(recovery: positioning walk at most gmax + d - 1 evaluations, lockstep at most 2 gmax)."
  },
  {
    "name": "code_instr",
    "line": 711,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "fixed_bytes",
    "line": 715,
    "arguments": [],
    "doc": "Bytes of the peak that do not depend on the table size: start word, code, constants, register file, kappa setup."
  },
  {
    "name": "memory",
    "line": 720,
    "arguments": [
      "m"
    ],
    "doc": "Bytes at the peak (the search; setup holds a subset, the offline derivation runs before the attempt): every item is a 32-byte word unless stated."
  },
  {
    "name": "exp_neg_ub",
    "line": 728,
    "arguments": [
      "xn",
      "xd"
    ],
    "doc": "Upper bound, in units of 2^-FB, on e^-(xn/xd) for xn/xd >= 0: 1/s with s the floored sum of the first KEXP + 1 terms of the series of e^x,\na lower bound on e^x (all terms are positive).  Counts: 2 KEXP mul, KEXP + 1 div, KEXP + 2 add."
  },
  {
    "name": "exp_consts",
    "line": 744,
    "arguments": [
      "KD",
      "H",
      "TAB"
    ],
    "doc": "(e^-KD, e^-H + e^-(H + KD - 10^-6), e^-TAB) as upper bounds (Lemma 2 (d): lockstep gap and positioning window)."
  },
  {
    "name": "gap_width_ub",
    "line": 755,
    "arguments": [
      "T"
    ],
    "doc": "Upper bound (units 2^-FB) on P(some stored index gap >= 2^GBITS): such a gap holds 2^119 - 1 consecutive indices below t with no DP, hence a\nwhole aligned block [j 2^118, (j + 1) 2^118) below t with no DP; at most 2^10 blocks lie below SMAX = 2^128, each empty with probability at\nmost (1 - theta_lo)^(2^118) <= e^-(theta_lo 2^118) by Lemma 1 (iii)."
  },
  {
    "name": "success_fp",
    "line": 766,
    "arguments": [
      "n",
      "d",
      "T",
      "ek",
      "c"
    ],
    "doc": "Lower bound (units 2^-FB) on P_F(success) for budget n and detection window d (proof.md Section 5, Lemma 2):\n1 - e^(-c n (n + 1) / 2N) - n / N - eps, eps = e^-KD + n d / N + e^-H + e^-(H + KD - 10^-6) + e^-TAB + E_W, N = p;\nE_W = 2^10 e^-(theta_lo 2^118) bounds an index gap of 2^119 or more (Lemma 2 (e)).\nc = 1 is the random function; other c is the deviation model of Section 8: a uniformly random"
  },
  {
    "name": "least_k",
    "line": 785,
    "arguments": [
      "q",
      "d",
      "T",
      "ek"
    ],
    "doc": "The least k (n = k 2^100) whose success bound reaches q, by bisection on [2^26, 2^28] (n between 2^126 and 2^128; the bound is below q at the\nlower end and at least q at the upper end, both asserted; the claim needs only that the bound at the returned k reaches q).  At most 30 evaluations."
  },
  {
    "name": "table_exp",
    "line": 803,
    "arguments": [
      "S",
      "T",
      "m"
    ],
    "doc": "Upper bound (units 2^-FB) on ln P(more than m of the stored DPs), by the Chernoff bound of Section 5(c):\nf(mu) = -mu + a (1 + ln(mu / a)), a = m + 1, mu = ceil(S theta_hi) < a, increasing in mu below a; ln(mu / a) <= -(u + u^2/2 + ... + u^KLN / KLN),\nu = 1 - ceil(mu / a) rounded down, since the dropped terms are positive.  Returns (f, mu); f is None if mu >= a."
  },
  {
    "name": "derive",
    "line": 826,
    "arguments": [
      "T",
      "m",
      "KD",
      "H",
      "TAB",
      "q",
      "ek"
    ],
    "doc": "The offline derivation of the trail length S = n + d and the gap cap gmax from T_DP = T and the table size m (integers only)."
  },
  {
    "name": "plan",
    "line": 851,
    "arguments": [],
    "doc": "Offline: re-derives and asserts the literals (STEPS, GMAXC, T_DP < 2^16, the table bound, the memory), then prints the ledger.  Everything\nthat fixes a literal or a charge is exact integer arithmetic above; the floats below only format the report (log2 of integers, decimal\nprinting) and no literal of the program is computed from them."
  },
  {
    "name": "tune",
    "line": 903,
    "arguments": [],
    "doc": "Offline: the finite parameter search that fixes the literals T_DP, MCAP, KD, H, TAB and UNROLL.  A cell (U, KD, KG, TAB) takes the largest\ntable MCAP with memory <= 2^20 (bisection) and the largest T in [40000, 65535] whose derivation passes the table bound (bisection, 16 probes);\nits value is the exact ledger total.  Descent from (18, 19/2, 77/8, 13): at steps 1/8, 1/64, 1/512, 1/4096, try the 8 "
  },
  {
    "name": "attempt",
    "line": 982,
    "arguments": [
      "coin"
    ],
    "doc": "The claimed attempt (one run, not repeated). It executes only the step program, the table logic and the recovery: STEPS and GMAXC are integer literals (printed with the parameters in section 5), not computed online; `plan` is the offline derivation and check of those literals and of the ledger. coin = two uniformly random 256-bit words; rho0 and x0 are their low 254 bits (every\n254-bit word is bel"
  },
  {
    "name": "run_rho",
    "line": 1001,
    "arguments": [
      "seed"
    ],
    "doc": "The search of `attempt` on the reduced map v -> low NB bits of F(v), rho and the start taken from the seed; the pair is checked on the\nreference digest: distinct messages whose digests agree in the low bits that the reduced map keeps (after the division by OUTSCALE)."
  },
  {
    "name": "offline_nodes",
    "line": 1033,
    "arguments": [],
    "doc": "Operator, call and subscript nodes of the offline source: every top-level definition and statement of this file except the attempt (`make_F`, `search`,\n`attempt`, `_get`, `_put`), the word machine and the self-checks.  Proof.md Section 7 bounds the compiled offline code by 8 instructions per node."
  },
  {
    "name": "selftest",
    "line": 1042,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "listing",
    "line": 1098,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "main",
    "line": 1102,
    "arguments": [],
    "doc": ""
  }
]
```

[Download the teaching kit](../../downloads/poseidon-rho-contracts.zip).

## Worked examples

### Replay the finite recovery and layout checks

Working directory: The extracted rho-contract-kit

```text
python -I -B replay.py
```

Expected: passed=true, exhaustive_graph_cases=17066, found_valid_graph_pairs=4408, packed_field_cases=1536 and step_reference_comparisons=9. No full-field attempt or parameter tuning.

### Inspect the historical conditional plan

Working directory: A new directory containing the pinned rho.py

```text
python -B rho.py --plan
```

Expected: 807 field operations per step; total_ops=137215184878174913969505127226939604471902; memory.total=1048568; success_lower_bound_decimal=0.39000000061813340752. The real-map success remains conditional on H1.

## Example runs and tests

Exact finite graph enumeration and named arithmetic/packing fixtures. Plan output remains conditional on H1 for the actual field map; no success-rate proof, full instruction listing audit, CPU timing claim or complete memory-price certification. The runtime report identifies tested bytes, not every function or mode in the tool.

[Read the check report](../../verification/rho-contract-kit-report-bounded-runtime.json).

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Do not treat model success as a proved law for a fixed Poseidon map.
- Changing output scale preserves collision implications but generally changes trajectories and success events.
- The search silently overshoots an invalid one-step budget to eighteen steps. The filed literal is a valid block multiple.
- make_F requires nonzero kappa for its scaled-map interpretation. Avoid sharing its mutable closure across threads.
- _put requires unused zeroed fields and bounded values; it is not a general assignment operation.
- A reduced-bit self-test match is not a full digest collision or evidence of the full-field success rate.
- Assertions disappear under Python -O; the publication wrapper rejects that mode.
- Plan reproduction does not certify the stated per-AST-node compilation charge, instruction listings, all spill traffic or complete peak allocation proof.
- Live historical snapshot path is missing. Exact original bytes are retained under an explicit source hash.
