# RECOUNT: the pkg8 cluster program re-counted with an independent tracer

RECOUNT agent. Folder `research\pkg8\review\recount`. Research only. Nothing was staged, filed or submitted;
no `yukon` command was run; `.key` was not read; the network was not used; `research\pkg8\pkg` and `research\pkg7`
were read only. Writes: this folder and `~/hashsmash/pkg8_review` inside WSL. Two interpreters, Windows `python`
and WSL `python3`, one process at `nice 5`, longest run under one minute. **No tool call was refused or stopped.**

Labels: **COUNTED** (by my own counter), **MEASURED** (with counts), **DERIVED** (arithmetic from stated inputs),
**ESTIMATE**.

## 0. What I did

I wrote my own counter (`mytrace.py`, class `Tr`) straight from the charging scheme I was given -- load, store,
add, subtract, AND, OR, XOR, NOT, shift 1 each; a rotation of every lane 5; a comparison and its branch 2; a word
already in a register is not a load; 16 registers. It does **not** use `halfsearch_cluster.Machine`. The arithmetic
of every piece is re-transcribed line by line from the program's text. `halfsearch_cluster` is imported for VALUES
only (memory builders, the reference, the class constants), never for its counter.

The tracer also carries the real 256-bit packed values, so it checks three things the program's own self-test does
not check together: the count, every lane against the independent reference, and the 36-bit lane occupancy (the
largest lane of every sum, against the bound the program's part table declares).

Files: `mytrace.py` (my counter), `run_recount.py` (one cluster, every piece, the split), `run_many.py` (many
clusters), `myledger.py` (my charge ledger), `wsl_check.sh` (the program's self-tests + my tracer under WSL),
`out1.json`, `many.json`.

## 1. My counts beside the package's (COUNTED)

| piece | my count | package | agree |
|---|---:|---:|---|
| representative word, first stage | **47** (37 operations + 10 loads) | 47 | yes |
| representative word, second stage | **135** (105 + 30) | 135 | yes |
| neighbour word, first stage -- each of the nine forms | **47** | 47 | yes |
| neighbour word, second stage -- each of the nine forms | **135** | 135 | yes |
| register peak of any of those words | **16** (14 values + 2 loop counters) | 16 | yes |
| gate test on z, core predicate + branch | **9** (6 + 3) | 9 core, 12 charged | core yes |
| dispatch, unrolled seven-lane selector | **29** (21 + 8) | 29 | yes |
| Y4-delta kernel `(U+D) AND M32` | **5** (2 + 3) | 5 | yes |
| lane broadcast | **7** (6 + 1) | 7 | yes |
| mixed-middle cache, per canonical-X2 group | **258** (126 ops + 90 loads + 42 stores) | 258 | yes |
| member table: table build per list word | **74** (43 + 26 + 5) | 74 | yes |
| middle step per value of X2 | **134** (85 + 40 + 9) | 134 | yes |
| outer step | not re-transcribed | 260 | -- |

Volume: **1,800 words** through my tracer (1,200 under Windows `python`, 600 under WSL `python3`), **12,600 lanes**
checked against `halfsearch_cluster.reference` on each lane's own X2 and member: **12,600 right, 0 wrong**. The
triple (stage A, stage 2, registers) was `(47, 135, 16)` for **every one** of the 1,800 words. No lane-sum bound of
the part table was reached.

Two places where the charging scheme I was given could have been read differently, and neither changes a number:

- *Rotation masks.* "A rotation of every lane 5" could mean 5 including its two mask words. In the batch it makes
  no difference: the masks of the rotations by 16 and 12 are resident, those by 8 and 7 are fetched once each into
  a register (4 loads in "C2, rest") and then used, and the one-bit rotation in "E1 test" is written as
  shift/AND/shift/OR, four units, not five. My tracer counted **0** rotations that had to load a mask at the point
  of use. (COUNTED)
- *Compare and branch.* I charge 2, as the scheme says and as the program does.

## 2. Does a neighbour word cost the same as a representative word when its lanes carry different X2? (COUNTED)

**Yes.** This was the one thing the ledgers assumed; I confirm it four ways, independently of the program's counter.

1. **Structural (COUNTED).** The batch reads seven X2-dependent memory words: `X2+w7` (twice), `w0` (twice),
   `-w2`, `w12-S1-S6`, `w3`, `S5`, `S12` (once each) -- nine reads of seven names, which my tracer counts directly.
   **None of the seven is among the nine resident words** (those are `A16 B16 A12 B12`, the two masks of rule A,
   `A all`, `A carry`, `not bit 32`), so each is a fresh load wherever it is read. Supplying a blended packed word
   in place of a homogeneous one changes the value that the load brings in, not the instruction. There is no
   per-lane work anywhere in the word.
2. **Counts (COUNTED).** All nine neighbour word forms -- three pure in X2 (offsets t = 1..7, 8..14, 57..63) and
   six mixed, which I derived myself from `partner_offsets` -- gave 47 and 135 with a register peak of 16, on every
   one of the 1,080 mixed-X2 words I ran.
3. **Values (COUNTED).** 7,560 lanes inside mixed-X2 words were right against the reference run on that lane's own
   X2 and member, and the stage-A flag of each equalled the scalar rule.
4. **Lane occupancy (COUNTED + DERIVED).** The largest lane of any sum, per part, over all 1,800 words:
   `X0 to X10` 2.9856 (bound 3), `C2 to z` 3.8558 (4), `rule A` 1.0 (2), `C2, rest` 4.6643 (5), `C1 to Y1` 4.6480
   (5), `E1, A and B` 7.5017 (9), `E1 test` 2.0000 (2, and strictly below by construction). No bound broken.
   DERIVED: a mixed word cannot break a bound that homogeneous words respect, because the bound is taken lane by
   lane and each lane of a mixed word is exactly the lane that some homogeneous word of that X2 would have.

What a mixed word does cost extra is the *preparation* of its blended middle words, and that is charged
separately and correctly: 258 per canonical-X2 group for the six blended records, plus 8 middle steps (8 x 134)
for the eight homogeneous records of the group. Both are right to amortise over the group's 16,384
representatives (0.0811 per representative, COUNTED/DERIVED), because the blend masks are the fixed lane patterns
of the nine partner words and the two field values depend only on the group's eight X2 values -- not on the
representative. Nothing has to be redone per cluster.

Also COUNTED by me: 63 neighbours are exactly nine words of seven lanes, with no spare lane.

## 3. The split of the second stage, re-derived from the program text (COUNTED/DERIVED)

My own part totals for the second stage: entry count 4, "C2, rest" 24, "C1 to Y1" 39, "E1, A and B" 47,
"E1 test" 17, restore 4 -- **135**.

The four lines of "E1, A and B" that reach `c1` and `c1'` are `a1` (2 operations, 1 load), `d1` (1 XOR + a
5-unit rotation, 1 load), `c1` (1, 1) and `c1b` (1, 1): **14 units**. So

- **prefix = 4 + 24 + 39 + 14 = 81** (COUNTED)
- **tail = (47 - 14) + 17 + 4 = 54** (COUNTED), to which both ledgers add **3** for restoring the values the
  branch leaves live (an addition to the part table, not a count: ESTIMATE) -- **57**
- **test = 12** -- taken as given from `research\others\tests\RESULTS.md`; it was counted on a machine whose
  second stage was 143 or 147, and I did **not** recount it on this 135-unit schedule (ESTIMATE).

**P(a lane passes the cheap test) = 105/16384 = 0.0064086914** (MEASURED/counted elsewhere, O4; not re-derived by
me). **P(a word of seven lanes passes) = 1 - (1 - 105/16384)^7 = 0.0440074957** (DERIVED by me, exact rational
13946532073518583478505973785 / 316912650057057350374175801344).

Per entered word: **81 + 12 + 57 x 0.0440075 = 95.5084** (DERIVED). This is `count_split.py`'s figure exactly.

## 4. The charge and time_log2 from my own counts (DERIVED; rates MEASURED elsewhere)

Rates used as premises, all measured by other agents: S' = 40.02 (so 41.02 trial-equivalents per representative),
2341/16384 representative words per representative, P_F7 = 0.02622, P_G7 = 0.2416, gate rate 1/16 (structural),
9/16 neighbour stage-A words per representative, 0.1364 neighbour stage-2 words per representative. Formula as the
package's: `t = 123.339 - log2(kept/margin) + log2(charge/34) + 0.012`.

| my ledger | per representative | charge per trial-equivalent | x1.04 | t at 3.75 | t at 2.4 |
|---|---:|---:|---:|---:|---:|
| whole second stage, expected rates, gate 9 | 54.89 | 1.3382 | 1.392 | 93.18 | 92.54 |
| whole second stage, expected rates, gate 12 | 55.32 | 1.3486 | 1.403 | 93.19 | 92.55 |
| **whole second stage, Section 8's 1.2x budget, gate 12** | **64.68** | **1.5768** | **1.640** | **93.42** | **92.77** |
| second stage split at the cheap test, expected | 49.79 | 1.2137 | 1.262 | 93.04 | 92.40 |
| second stage split, 1.2x budget | 58.04 | 1.4149 | 1.471 | 93.26 | 92.62 |
| **the package: 67.225 per representative, charged 1.71** | 67.225 | 1.6389 | 1.71 | **93.479** | **92.835** |

**Does 93.5 follow? Yes, with room.** My strictest counted reading -- the 1.2x budget of Section 8 on the gate rate
and the neighbour stage-2 share, the gate at U's 12, the dearer seven-lane dispatch, and the package's own 1.04
uplift -- gives a charge of 1.640 and **93.42**. The package charges 1.71 and claims the bound 2^93.4791, which I
reproduce to 93.4787. The package is therefore **4.3 per cent above my own strictest counted ledger** and 22 per
cent above my expected-rate ledger. At margin 2.4 the same counts give **92.77** (package 92.835), so a claim of
92.9 would follow there.

The claim does not fail on the counts. What it rests on is not the counting: the measured rates are premises, the
yield 40.02 is a mean, and the routing items below are not counted at all.

## 5. Where I differ from the package, and why

**D1. The headline budgeted charge, 67.225 units per representative (1.6389), is not itemised anywhere.** The
string "67.225" occurs in exactly two files in the whole workspace, `proof.md` and `submission-note-r2.md`, and in
no ledger. Running the same items with Section 8's own stated 1.2x budget I get **64.68**, not 67.225. The gap,
about 2.55 per representative, is the size of the one item Grok's audit names as the largest open swing (loading a
table base into a register instead of using it as an immediate addend, +2.68 per representative): 64.68 + 2.68 =
67.36, within 0.2 per cent of 67.225. So the figure is **reachable and conservative, but a reader cannot
reconstruct it from the package.** It should be itemised before filing. (I note the alternative reading that
1.6389 = 1.5768 x 1.04 already includes one uplift, in which case 1.71 applies the 1.04 twice -- harmless, but it
would mean the printed "4.3 per cent margin" is really 8.4.)

**D2. Section 8's cost table is the pkg7 table.** Its rows (stage A 6.714439, stage 2 0.602692, middle step
0.001022, ...) still sum to **7.318 per trial**, while the "budgeted" cell of the same column says **1.6389** and
the "charged" cell 1.71 (= 1.71 x 131,072 in the neighbouring column). The formula `P = W*47 + W*135/32 + 134 + 1
+ ...` printed just above it is likewise the pkg7 formula, with no cluster term. The cluster ledger -- gate,
dispatch, addressing, neighbour words, the blend cache, the eight middle steps -- appears nowhere in Section 8.
This is the most serious thing I found: the number is defensible but the section that is supposed to derive it
does not.

**D3. The rounding granularity changed.** pkg7 charged `ceil(1.04 K)` to one decimal (7.611 -> 7.7). Here
1.04 x 1.6389 = 1.70446 is rounded to **two** decimals, 1.71. With pkg7's own granularity the charge would be 1.8
and the claim **93.56 -> 93.6**. The claim 93.5 depends on the finer rounding; it is not wrong, but the convention
changed between the two entries and the text does not say so.

**D4. Heuristic H4 is mis-stated by a factor of 16.** It says "the number of trials found to satisfy rule A **per
representative whose gate opens**, divided by the probability that a trial satisfies rule A, is at least 40.02".
The measured quantity (`MEASURE.md` line 165) is `E[partners found passing F per REPRESENTATIVE] / p_F`. Per
representative whose gate opens the same measurements give 2.5028 / 2^-8 = 640.7, not 40.02. The charge divides by
41.02 = 1 + 40.02 and uses the right quantity, so **no number moves**; the statement of the heuristic is wrong as
written and a reviewer checking H4 literally will not reproduce 40.02.

**D5. Step 2(c) of 6.4 does not describe the implemented loop.** It says: "for each of the 2^32 values of X2 ...
run the batches for the **2,048** representatives of the sub-class". With the six flips as implemented (e1 bits
14, 30, 31 and X2 bits 14, 30, 31) a canonical-X2 group has **16,384** representatives and X2 runs over the 2^29
canonical values. The product is the same either way -- 2^43 representatives per outer tuple, which is what every
ledger amortises over -- but as written the loop contradicts Lemma C (clusters partition only when X2 is
restricted to its canonical values, otherwise a trial is reached both as a neighbour and as a representative), and
the packing fraction would be 293/2048 = 0.14307 rather than the 2341/16384 = 0.142883 the ledgers use.

**D6. `count_split.py` presents two figures as agreeing when they differ by one unit.** It prints "per entered
word: 95.5084 (Grok's hand figure 96.5084)". Grok's figure is `1 + 81 + 12 + 57P`; the tool derives `81 + 12 +
57P`. My recount gives 95.5084, i.e. the tool's arithmetic is right and the parenthesis is misleading; the extra
unit is Grok's and is unexplained in its answer.

**D7. The gate's 12 is 9 counted plus 3 not counted.** My core count is 9, as PROGRAM8 says. The charged 12 adds a
flag spill and the reload of the mask stage A evicts, which is an integrated-register argument, not a machine
count; Grok's trace argues for +1 (10) instead. The spread is 0.43 per representative, 0.010 per trial-equivalent,
about 0.011 bits. Charging 12 is the conservative choice.

**D8. No conflict with PROGRAM8's own figures.** Its section 5 gives 93.19 to 93.38 from the same pieces and says
plainly that this is a lower bound, not a score, because the routing overhead is omitted. The package files 93.5,
above that range, which is the right direction.

## 6. What I could not count

- **The integrated routing schedule.** One 16-register lifetime account threading representative word -> gate ->
  dispatch -> neighbour words -> both stages, with the parent packet index, the saved gate flags, the offset
  cursor and the address `base + 8*member + pattern` live at once. Every piece is counted on its own machine; the
  combined peak and the overhead are UNKNOWN, exactly as PROGRAM8 section 4 and VERDICT8 section 7 say. The items
  that stand in for it in the ledgers are ESTIMATEs I could not verify: cluster addressing 5 per opened cluster,
  metadata spill 4 per gate word, group setup 16, last-word spare-lane suppression 4. Together they are 0.55 per
  representative at expected rates, 0.013 per trial-equivalent, about 0.014 bits; the strict "load every address
  base" reading is a further 2.68 per representative, about 0.067 bits.
- **The cheap test's 12 units**, which were counted on a different machine with a different second stage.
- **The outer step's 260**, taken from the program's part table, not re-transcribed.
- **The eight-fold table layout's 133,413 rows per outer tuple.** It is DERIVED in `gpt_sol_answer_U.md` 4.1 and I
  did not recount it; arithmetically 133,413 = 131,072 + 2,341, which is consistent with one row per member plus
  one per representative word. Its contribution is 1.1e-6 per representative and cannot move the claim.
- **The measured rates themselves** (S' = 40.02, P_G7, P_F7, the 0.1364 neighbour stage-2 share, the cheap test's
  105/16384). They are premises of my ledger, not counts of mine.

## 7. The program's own self-tests, as they print (COUNTED, both interpreters, exit 0)

`--selftest 2000 1`: 14,000 of 14,000 lanes right, 2,000 of 2,000 cases stored right, 54 lanes passing rule A, 46
batches entering stage 2, 0 zero test words, stage A 37 operations + 10 loads, stage 2 105 + 30, 16 registers.
Exit 0.

`--cluster-selftest 50000 pkg8`: 50,048 trials in 782 clusters; staged h1 = tl_ref 50,048/50,048; K8 = tl_ref
50,048/50,048; gate = H4 of tl_ref 782/782 clusters; `gate_all 03000300`, `gate_v 01000000`; partition recovers the
representative 49,266/49,266; 782/782 clusters with 64 distinct trials; neighbour members match `class_member`
49,266/49,266; packed sample 1,125 words, 7,875 lanes, stage-A flag = scalar 7,875/7,875, stage-2 word = reference
7,875/7,875; `new_counts_constant` true; new counts: representative stage A 37+10 regs 16, representative stage 2
105+30, neighbour stage A 37+10 regs 16, neighbour stage 2 105+30, gate core 6+3 regs 5, dispatch 21+8 regs 5,
delta kernel 2+3, broadcast 6+1, mixed-middle cache 126 ops + 90 loads + 42 stores. Exit 0.

`count_split.py`: stage A 47, stage 2 135; prefix 81 + test 12 + tail 57 = 150 if the tail always ran;
P(word) = 0.0440074957; per entered word 95.5084; and its ledger rows 93.331 / 92.688 (whole) and 93.199 / 92.556
(split) at margins 3.75 and 2.4.

`charge\cost8.py`: variant 1 expected K = 1.3486 charged 1.5 t = 93.290; budgeted K = 1.4395; variant 2 expected
K = 1.2286 t = 93.083. (These are the package's own scratch ledgers; none of them produces 1.6389 or 67.225.)

## 8. One-line verdict

Every machine count in the package is right -- I reproduce 47, 135, 9, 29, 5, 7, 258, 74 and 134 with a counter of
my own, and the mixed-X2 neighbour word really does cost exactly what a representative word costs, in count, in
values and in lane occupancy. **93.5 follows from my counts and is conservative by about 0.06 bits against my
strictest reading and 0.29 against my expected-rate reading.** What is not right is the *text*: Section 8 still
derives pkg7's number, the 67.225 that the claim rests on is itemised nowhere, H4 is mis-stated by a factor of 16,
the loop of 6.4 says 2,048 representatives at 2^32 values of X2 where the design has 16,384 at 2^29, and the
rounding granularity changed from 0.1 to 0.01 without a word. None of these moves the score; all four are things a
hostile reviewer will find.
