# PROGRAM8: the neighbour (cluster) path added to the pkg7 program and counted

Program agent of the job `pkg8` (cluster package). Research scratch in `research\pkg8\program`. Nothing is staged,
filed or submitted. No `yukon` command was run, `.key` was not read, the network and the graphics card were not
used. The only writes were to this folder and to the WSL scratch `~/hashsmash/pkg8`. All runs: CPU only, Windows
`python` 3.14 and WSL `python3` 3.14, one process at `nice 5`. Longest run 5 s. No tool call was refused or stopped.

Labels: **COUNTED** (by the program's own machine), **MEASURED** (with counts, taken from a named file),
**DERIVED** (arithmetic from stated inputs), **ESTIMATE**.

## 0. In short

- The file `halfsearch_cluster.py` is a copy of `research\pkg7\blake3-r2\experiments\halfsearch.py` with the
  neighbour path of design 2 added **below** the original code, so the original `--selftest` is byte-for-byte the
  pkg7 program's self-test. It still passes (exit 0; stage A 47, stage 2 135, 16 registers).
- The new path **executes and counts** every piece the task names: representative words, the gate test, opening a
  cluster (dispatch), neighbour words from stored member rows (the Y4-delta kernel and the mixed-X2 middle cache),
  their first stage and their stage 2. Every piece runs on the pkg7 counting machine (`Machine`), so every
  operation, load and store is charged in the pkg7/`COST.txt` convention.
- A new self-test `--cluster-selftest N` checks the whole neighbour path against the independent two-level
  reference `research\h8\twolevel\tl_ref.py` on **50,048 trials** (782 clusters): the staged h1, the gate (H4) and
  every K8 decision equal tl_ref; the 64-trial partition and the Y4-delta member formula hold; and **7,875 lanes**
  were put through the packed machine with genuinely mixed X2 values and matched `tl_ref` (stage A) and the full
  two-message reference (stage 2). All checks pass (exit 0).
- **Main new result (COUNTED).** The neighbour first stage is **47** and the neighbour stage 2 is **135**, the same
  as a representative, **even though a neighbour word mixes up to two X2 values across its lanes**. This is the one
  thing `research\pkg8_program\verify\VERDICT8.md` section 7 and `gpt_sol_answer_U.md` left as an assumption; it is
  now machine-counted and value-validated.
- **What is still not counted:** a single integrated routing schedule that threads all the pieces through one
  16-register lifetime account across a cluster (addressing of stored rows, metadata spills). Each piece is counted
  on its own machine; the combined register peak and the routing overhead `H` of `gpt_sol_answer_U.md` section 7
  remain UNKNOWN, as that file says.

## 1. The design that is implemented (from MEASURE.md design 2; constants checked in the program)

- Cube C15, `e1 = Y3 + Y4`, `(e1 AND 07ef8303) == 030c0303`, 131,072 members. Rule **F = K8** (eight parities of
  h1, `RULE_CONDITIONS = 8`, the existing rule that sends a lane to stage 2). Gate **G = H4** (four parities).
- Six flips: `e1` bits 14, 30, 31 and `X2` bits 14, 30, 31; corner 0. A **representative** has those six bits zero;
  its **63 neighbours** are all non-empty combinations of the six flips. (COUNTED that bits 14, 30, 31 are free in
  the class; the program asserts it.)
- The gate on z (DERIVED and COUNTED, matches `gpt_sol_answer_U.md` 4.3): because in C15 the member's e1 bits 0, 1
  are one and bits 16, 17 are zero, H4 on `h1 = ROR(ROR(z,8) XOR e1,16)` is a test on z alone:
  `((z XOR 0x01000000) AND 0x03000300) == 0x03000300`. The program derives `GATE_ALL = 03000300`,
  `GATE_V = 01000000` from the class and the H4 masks (`gate_constants()`), and the self-test confirms it equals H4
  on tl_ref's h1 in 782/782 clusters.

## 2. Machine counts of every new part (COUNTED by `halfsearch_cluster.py`; `cluster_counts()`)

All in the pkg7 convention (one operation, load or store each; 16-register machine; the two loop counters add 2 to
every register peak). "registers" is the standalone peak of that piece run on its own machine.

| new part | operations | loads | stores | total | registers | checked against |
|---|---|---|---|---|---|---|
| representative first stage (= pkg7 stage A, K8) | 37 | 10 | 0 | **47** | 16 | its own self-test + tl_ref |
| representative stage 2 (= pkg7 stage 2) | 105 | 30 | 0 | **135** | 16 | reference (two messages) |
| **neighbour first stage, mixed X2** | 37 | 10 | 0 | **47** | 16 | tl_ref, 7,875 lanes |
| **neighbour stage 2, mixed X2** | 105 | 30 | 0 | **135** | 16 | reference, 7,875 lanes |
| gate test on z (core predicate + branch) | 6 | 3 | 0 | **9** | 5 | H4 of tl_ref, 782 clusters |
| dispatch (seven-lane selector, U.md 4.4) | 21 | 8 | 0 | **29** | 5 | — (exact replay of U.md 4.4) |
| Y4-delta kernel `(U+D) AND M32` (U.md 3.1) | 2 | 3 | 0 | **5** | — | member = class_member, 49,266 |
| lane broadcast (U.md 3.1) | 6 | 1 | 0 | **7** | — | — |
| mixed-middle cache, per X2 group (U.md 4.2) | 126 | 90 | 42 | **258** | — | — |

Notes.
- **neighbour first stage = 47, stage 2 = 135 (COUNTED).** The X2-dependent words the batch reads (`X2+w7`, `-w2`,
  `w0`, `w12-S1-S6`, `w3`, `S5`, `S12`) are already loaded per word in the pkg7 batch, not kept resident; so when
  they are supplied as the correct per-lane packed words the macro is unchanged and the count is identical. The
  program proves this by running `partner_batch` (a line-for-line copy of `packed_batch` with the neighbour's own
  list word) on words with mixed X2 and checking every lane.
- **gate (COUNTED 9).** Core predicate `((z XOR V4) AND ALL4) + carry4`, OR with the resident not-bit-32, compare
  and branch: 6 operations, 3 loads (V4, ALL4, carry4). `gpt_sol_answer_U.md` 4.3 adds, for the live-register
  context, a one-word gate-flag spill and the reload of the one mask stage A evicts (1 store + 2 loads), giving
  **12** in all. The program counts the core; the +3 is the integrated-register overhead (section 4).
- **dispatch (COUNTED 29).** The unrolled seven-lane selector of `gpt_sol_answer_U.md` 4.4 (load zero once; per
  lane load its bit-32 mask, AND, compare, branch). A per-triggered-lane selector (MEASURE's d = 5/lane, ~9/word
  at the measured 1.81 triggered lanes/word) is cheaper but `U.md` 4.4 cautions it is not free; this is the main
  place the charge is sensitive (section 4).
- **mixed-middle cache = 258/group (COUNTED).** The six mixed-X2 neighbour words read seven middle fields each
  whose value is one of two homogeneous records lane by lane; `mixed = ((A XOR B) AND L) XOR B` is prepared once
  per canonical-X2 group (6 patterns x (1 mask load + 7 fields x (2 loads + 3 ops + 1 store)) = 258). Matches
  `U.md` 4.2 exactly.

Registers used: the two batch pieces peak at **16 of 16** (unchanged from pkg7). The gate and dispatch peak low on
their own machines; their true in-context pressure is the open item of section 4.

## 3. Self-test of the new path against tl_ref.py (COUNTED; `--cluster-selftest 50000`)

`evidence_cluster_selftest.json`; rerun with the command in section 5. A case is one checked trial; clusters are
drawn until at least N trials are checked.

| check | result |
|---|---|
| trials checked / clusters | 50,048 / 782 |
| staged h1 (from z) = tl_ref E3.h1 | 50,048 / 50,048 |
| K8 decision = K8 on tl_ref h1 | 50,048 / 50,048 |
| gate (H4 on z) = H4 on tl_ref h1 | 782 / 782 clusters |
| neighbour member = class_member and = representative + delta (U.md 3.1 (1)) | 49,266 / 49,266 |
| representative recovered by clearing the six flip bits (partition) | 49,266 / 49,266 |
| clusters with 64 distinct trials | 782 / 782 |
| packed machine, mixed X2: stage-A flag = scalar K8 | 7,875 / 7,875 lanes |
| packed machine, mixed X2: stage-2 word = reference (both real messages) | 7,875 / 7,875 lanes |
| new counts constant across cases | True |

The bridge to tl_ref is exact: both files use the same eight basis words
`C0.c1 C0.d1 D3.d1 S15 S9 w5 X2 Y4`, so a context + member maps straight into `tl_ref.flat`, whose `E3.h1` is the
reference h1. The existing `--selftest` still exits 0 (`evidence_base_selftest.json`: 2,000 cases, 14,000/14,000
lanes right, stage A 47, stage 2 135, 16 registers).

## 4. What is counted and what is not (honest boundary)

COUNTED here, with values validated: the representative and neighbour first/second stages (incl. the mixed-X2
neighbour case), the gate core, the dispatch selector, the Y4-delta kernel, the broadcast, the mixed-middle cache.

NOT counted (and why): a single **integrated routing schedule** that runs representative word -> gate -> dispatch
-> neighbour words -> stage A -> stage 2 with **one shared 16-register lifetime account** across the whole cluster.
Each piece above is counted on its own machine. The combined peak (parent packet index, saved gate flags, offset
cursor and the addressing `base + 8*member_index + pattern` all live at once) is the "complete routing
register-lifetime schedule" that `gpt_sol_answer_U.md` sections 4.4 and 10 and `VERDICT8.md` section 7 call UNKNOWN.
The only integrated-pressure item quantified is the gate's in-context eviction + flag spill (+3, giving the gate's
12 of `U.md` 4.3). The table-build in the new 8x layout (133,413 rows/outer tuple, `U.md` 4.1) is DERIVED there,
not re-counted here; its per-trial contribution is negligible but its memory is ~8x pkg7's.

## 5. Charge assembled from these counts (DERIVED; rates MEASURED elsewhere)

To place the counts on the score, use the accounting of `VERDICT8.md` section 4 with the rates **MEASURED** there
(`S' = 40.044`, `p_G = 0.062495`, `E_w = 2.1830`, `P_G7 = 0.24122`, `P_F7 = 0.026215`), the kept mass
185,358,111.47 and margin 3.75. The only change is to replace its assumed gate `g` and dispatch `d` by the values
**COUNTED** here. All per-trial-equivalent, s = 135:

    K = [ (a+g)/7 + P_F7*s/7 + P_G7*d + p_G*(9*a' + E_w*s) + 8*134/16384 ] / (1 + S'),  a = a' = 47.

| gate g, dispatch d | source | K | charged (pkg7: ceil(1.04 K, 0.1)) | time_log2 (3.75) |
|---|---|---|---|---|
| g = 4, d = 5 | VERDICT8 assumption | 1.3135 | 1.4 | 93.19 |
| g = 12, d = 9 | counted gate (U 4.3) + per-lane dispatch (~9/word) | 1.365 | 1.5 | 93.29 |
| g = 12, d = 29 | counted gate + counted seven-lane selector (U 4.4) | 1.482 | 1.6 | 93.38 |

So counting the gate and the dispatch raises the per-trial-equivalent charge from VERDICT8's assumed 1.31
(time_log2 93.19) to **1.37-1.48 (time_log2 93.29-93.38)**, the spread being the dispatch model. This is DERIVED:
the rates are measurements of other agents, and the integrated routing overhead `H` (section 4) is still omitted,
so it is a lower bound on the true charge, not a score to file. The nearest real filed program remains pkg7 at
time_log2 95.650.

## 6. Files and how to rerun

- `halfsearch_cluster.py` -- the pkg7 program with the neighbour path appended (original code unchanged above the
  `CLUSTER PATH` banner). New: `--cluster-selftest N [seed]`.
- `run_cluster.sh` -- runs both self-tests under WSL, writes JSON to `~/hashsmash/pkg8`.
- `evidence_base_selftest.json`, `evidence_cluster_selftest.json` -- the two self-test outputs quoted above.

```
# Windows:
python halfsearch_cluster.py --selftest 2000 1
python halfsearch_cluster.py --cluster-selftest 50000 pkg8
# WSL (as the job prescribes):
wsl -d Ubuntu -- bash "./research/pkg8/program/run_cluster.sh"
```

Key functions in the file: `gate_constants`, `partner_offsets`, `scalar_z`, `gate_flags`, `dispatch`,
`delta_uword`, `broadcast`, `mixed_middle_cache`, `partner_batch`, `partner_word_memory`, `cluster_reference`,
`cluster_counts`, `cluster_selftest`.
