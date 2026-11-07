# pkg7, step PROGRAM: the two-level program with the sub-class and the rule with eight conditions (2026-10-06)

State of the package: **DRAFT**. Written by the helper agent of the step PROGRAM. Nothing was staged, synced, filed
or posted; no `yukon` command was run; nothing was pulled from the network; the GPU was not used; `.key` was not
read; `research\pkg2`, `pkg4`, `pkg5`, `pkg5L`, `pkg6`, `pkg7_program`, `pkg7_prep`, `h8` and `grok` were only read.
Files were written in `research\pkg7` and, in WSL, in `~/hashsmash/pkg7run` (scratch) and
`~/hashsmash/hash-smash-pkg7run` (an own clone of the local organizer checkout, 86f1102).

**Only the experiment program is new.** `blake3-r2\proof.md`, `claim.json`, `experiments\manifest.json`,
`certificates\manifest.json` and `submission-note-r2.md` are still the text of the filed `research\pkg6` (old
arrangement, rule with five conditions, 524,288 members, 97.6), except that `claim.json` now says
`"submission_state": "draft"`. The folder as it stands must not be staged.

Program: `research\pkg7\blake3-r2\experiments\halfsearch.py`, 63,738 bytes (the organizer allows 65,536), SHA-256
`cde9b8279eaad69a148d570714fbbcceea8bd81faab8ef10773faa9fa38f5563`, `RULE_CONDITIONS = 8`, `REGISTERS = 16`,
`KEPT = 9`, `FACTOR = 49400000`. Every evidence file names the SHA-256 of the program it is for; a file is evidence
only while the program still has that SHA-256. All paths below are under `research\pkg7\`; "evidence" is
`work\evidence`.

## 1. What the program is

Base: `research\pkg7_prep\opt\strict\halfsearch.py` (SHA-256 85be4400...1245), the recoded two-level batch that
`research\pkg7_prep\opt_verify\VERDICT.md` confirmed (counts on an independent tracer, 2,174,158 lanes on real
digests, bounds, harness). It was preferred to the batch of `research\grok\work\job15_batch` because its stage A is
smaller (rule with five conditions: 29 + 8 = 37 against 30 + 11 = 41; stage 2 101 + 27 = 128 against 100 + 27 =
127, and stage 2 weighs one part in 32 here) and because it has a checker's verdict. Nothing was taken from the
other batch. Against that base, 58 functions and methods have the same text (among them `outer`, `middle`,
`member`, `table_row`, `trial`, `messages`, `residual_word1`, `compress2`, `reference`, `batch_check`, `lane_flags`,
the class `Machine`, `outer_step`, `table_build`, `middle_step`); seven are changed (`class_pattern`, `list_words`,
`rule_a_constants`, `rule_a_flags`, `packed_batch`, `rule_a_right`, `selftest`) and `rule_word` is new, besides the
constants and `TABLES`. The changes:

1. **Sub-class.** New line `CUBE = (0x04200000, 0x00000000)`: `class_pattern()` adds these bits of e1 = Y3 + Y4 to
   the bits that eta fixes. The class is (e1 AND 07ef8303) == 030c0303, **131,072 members**, 18,725 list words (the
   last has four members and three spare lanes). `class_member(k)` fills the 17 free bits in increasing order.
   `evidence\ref_compare.txt`: the members are exactly the 131,072 members of the class of the design reference
   (`research\h8\twolevel\h8_ref.py`, 524,288 members) whose e1 has bits 21 and 26 zero, in the same order.
2. **Rule.** `RULES` has four, six and eight conditions, each containing the one before it (COUNT.md names p4,
   old6, S8): h0 = 0, h1 = 1, h16 = 0, h17 = 0; then h2 XOR h10 = 1, h3 XOR h11 = 1; then h3 XOR h12 XOR h24 = 0,
   h6 XOR h13 XOR h25 = 0. `RULE_CONDITIONS = 8`. The rule with five conditions of the filed package is gone.
3. **Lemma A in a new form** (`A_PLANS`, `rule_a_constants()`, `rule_word()`, `rule_a_flags()`). The old form
   needed every bit of e1 that the rule reads to be fixed by the class and every condition to be one bit or two
   bits of z. The new rule reads the free bits 27, 28, 29 of e1 and has two conditions on three bits. Now:
   - bit i of h1 is bit (i + 24) mod 32 of z XOR bit (i + 16) mod 32 of e1; so the rule reads the 13 bits
     2, 3, 4, 5, 8, 9, 16, 17, 24, 25, 26, 27, 30 of z;
   - the test word y is made from z by **8 operations with 2 masks**: s = (z << 12) AND 0003c000; y = z XOR s;
     s = s << 12; y = y XOR s; s = (y << 13) AND 40010000; y = y XOR s. Then y8 = z8, y9 = z9, y24 = z24,
     y25 = z25, y26 = z26 ^ z2, y27 = z27 ^ z3, y16 = z16 ^ z4 ^ z3, y30 = z30 ^ z17 ^ z5 (y16 is the XOR of two
     conditions of the rule, h3 ^ h11 and h3 ^ h12 ^ h24; the eight positions are independent combinations of the
     eight conditions);
   - the wanted bits at these eight positions depend on the member: y8 = e0, y9 = e1, y24 = e16, y25 = 1 ^ e17,
     y26 = 1 ^ e18 ^ e26, y27 = 1 ^ e19 ^ e27, y16 = 1 ^ e8 ^ e27 ^ e28, y30 = e9 ^ e22 ^ e29. A **second static
     list V** (one word per list word, the same for the whole search, `list_words(j)[2]`) holds, per lane, a 1
     where the wanted bit is 0. Stage A loads V[j] (one load, in the place of the constant ADD of the base) and
     tests ((y XOR V[j]) AND ALL) == ALL with ALL = 4f010300, by the carry of the base: bit 32 of
     ((y XOR v) AND ALL) + (2^32 - ALL);
   - `rule_a_constants()` does not trust the plan: it follows the steps on five lanes of bit names and stops
     unless every read position holds only bits 0 to 31 of its own lane and is a combination of the conditions,
     and the positions are as many as the conditions and independent.
   The rule with six conditions has one step ((z << 24) AND 0c000000), the rule with four none.
4. **Registers.** Nine words stay in registers during a class loop as in the base, now A16, B16, A12, B12, the two
   masks of the steps, ALL, 2^32 - ALL and "not bit 32". X2 + w7 and w0 are loaded where stage A reads them. The
   first step of rule A takes the register of z (five registers for the values of stage A, 16 of 16 in use), so
   **stage 2 forms z again** (`Z_AGAIN`: 4 operations + 3 loads, in the part "C2, rest"), as the base already
   forms the third value of C2 again.
5. **Budget constant.** `TRIALS_LOG2 = 102` is replaced by `FACTOR = 49400000` (= 2^25.5580; the exact kept count
   divided by 3.7522): a run has 2^127 / FACTOR = 2^101.442 trials, `RUN_PAIRS` = ceil(2^127 / (FACTOR * 131072))
   pairs (outer step, value of X2), and `STAGE_2_BUDGET` = 18,725 * RUN_PAIRS >> 5. No count depends on the value.
6. `rule_a_right()` is now a complete enumeration (section 3); the JSON line of the self-test has `rule_a_on_z`
   (steps, ALL, wanted bits, free bits of e1 read) and `class` (eta, mask, value, members).

A cheaper test was looked for and not found. With the 13 bits masked first (one AND, one mask), no sequence of up
to four steps y = y XOR (y shifted) reads the rule, and no sequence of three steps v = (an earlier word) XOR (an
earlier word shifted) either (complete searches over all shift distances, `work\tools\search\xorshift.py 4 out.txt` and
`general3.py out.txt`, 0 solutions each; 24 s and 63 s on the host). Three masked shifts cost 12 (9 operations, 3 masks);
the test above costs 10. It is not proved to be the cheapest, and no other rule was tried.

## 2. Counts per stage (operations + loads [+ stores]; the program's own machine)

| piece | count | file |
| --- | --- | --- |
| **stage A per batch, rule with 8 conditions** | **37 + 10 = 47** (loop 3+1, X0 to X10 3+4, C2 to z 17+4, rule A 14+1) | `evidence\counts.txt` (1,500 cases per rule, 10,500 of 10,500 lanes right each), `evidence\tracer_counts.txt`, the long self-test |
| **stage 2 per batch** | **105 + 30 = 135** (entry count 3+1, C2 rest 17+7, C1 to Y1 31+8, E1 A and B 41+6, E1 test 13+4, restore 0+4) | same |
| stage A, rules with 4 / 6 conditions | 29 + 8 = 37 / 32 + 9 = 41; stage 2 101 + 27 = 128 / 105 + 30 = 135 | same |
| middle step per value of X2 | 85 + 40 + 9 = 134 (its 9 loads of the class loop entry included) | `evidence\counts.txt` |
| outer step | 148 + 91 + 21 = 260 | `evidence\counts.txt` |
| table build per list word (seven members) | 43 + 26 + 5 = 74; per outer step 74 * 18,725 = 1,385,650 (2^20.40) | `evidence\counts.txt`, `evidence\class_loop.txt` |
| registers in use | batch 16, outer step 11, table build 7, middle step 13, of 16; per part of the batch: loop 12, X0 to X10 13, C2 to z 16, rule A 16, entry count 11, C2 rest 15, C1 to Y1 15, E1 A and B 16, E1 test 11, restore 11 | `evidence\counts.txt`, `evidence\register_peaks.txt` |
| lane bound for all inputs | batch 9 * 2^32 - 9, 36 bits of 36 (largest seen in the long self-test 8.349 * 2^32); stored words and flag words below 2^32; the word added to the carry word of stage A at most ALL; shifted words misused 0 | `evidence\lane_bound.txt` (2,000 random cases per rule within the bounds) |
| every read of a memory word a load (`KEPT = 0` set in memory) | stage A 37 + 20 = 57, stage 2 100 + 43 = 143, middle step 146, 10 registers (rules 4 / 6: 47 / 51) | `evidence\every_use.txt` (600 cases per rule, all lanes right) |

Independent tracer (`work\tools\tracer_counts.py`, the counting machine of `research\pkg7_prep\opt_verify`, which
shares no code with the program's `Machine`): from its instruction list stage A 37+10, stage 2 105+30, outer step
148+91+21, table build 43+26+5, middle step 85+40+9 for the rule with eight conditions (and 29+8 / 101+27, 32+9 /
105+30 for four and six); the smallest register FILE THAT REFUSES and still runs the batch is 16, 15 is refused;
300 cases per rule, same instruction list in every case, results equal to those on the program's machine, no fault.

## 3. Tests run (all for the SHA-256 above)

- **Long self-test** (`work\selftest_big.sh 61 8:1000000`, WSL, Python 3.14.4, `nice -n 5`):
  `evidence\selftest_1000000_rule8_61.json`: exit 0 after 1,000,000 cases (1,499 s; 250,000 the last batch, 200,000
  with extreme words), **7,000,000 of 7,000,000 lanes right** against the complete digests of their two real
  messages, stored words right in 1,000,000 of 1,000,000 cases, counts the same in every case and equal to
  `TABLES` (stage A 37+10, stage 2 105+30), every sum below the bound of its part, registers 16 / 11 / 7 / 13
  (batch, outer step, table build, middle step), largest lane of a sum seen 8.349 * 2^32, flags right on 128 of
  128 patterns, rule A on 65,536 of 65,536 words, the list holds 131,072 members in 18,725 words. 27,068 lanes
  satisfy the rule and 23,368 of the 1,000,000 batches enter stage 2 (every fourth case is the short last batch,
  whose spare lanes repeat a member); no stage-2 test word was zero.
- Self-tests of the two other rules, 250,000 cases each, seed 61 (`evidence\selftest_250000_rule{4,6}_61.json`):
  both exit 0 (398 s and 404 s), 1,750,000 of 1,750,000 lanes right each, stored words right in 250,000 cases,
  counts the same in every case and equal to `TABLES` (29+8 and 101+27; 32+9 and 105+30), sums below their
  bounds, 16 registers, rule A patterns 16 of 16 and 512 of 512; 109,228 and 27,297 lanes satisfy the rule,
  53,713 and 22,005 batches enter stage 2 (every fourth case is the short last batch); no zero stage-2 word.
- A second seed text on the host, 40,000 cases (`evidence\selftest_40000_rule8_pkg7-second.json`): exit 0, 280,000
  of 280,000 lanes right, 37+10 and 105+30, 16 registers; 1,048 lanes satisfy the rule, 895 batches enter stage 2.
- Short self-test (`evidence\selftest_small.txt`, 9 lines ok, 0 failed): 2,000 cases, 14,000 of 14,000 lanes right
  against the complete digests, stored words right in 2,000, counts as `TABLES` in every case, sums below their
  bounds, flags right on 128 of 128 patterns, rule A on 65,536 of 65,536 words, same bytes when repeated, second
  seed text exit 0, wrong arguments rejected.
- **Lemma A by complete enumeration, three ways.** (a) The program's `rule_a_right()`, part of every self-test: all
  2^13 patterns of the bits of z that the rule reads times all 8 patterns of the free bits 27, 28, 29 of e1, each
  once in every one of the seven lanes of 65,536 packed words, other bits random, lane bits 32 and 33 filled, on
  the program's machine with the word of the list V: 65,536 of 65,536 words right (512 of 512 and 16 of 16 for
  six and four conditions); in 1,792 words a lane satisfies the rule (7 * 256: the share is exactly 2^-8).
  (b) `evidence\lemma_a_enum.txt` (`work\tools\lemma_a_enum.py`): rule and test typed a second time by hand, scalar;
  the support is found by flipping every bit of z (36) and e1 (32): exactly the 13 bits of z and the bits 27, 28,
  29 of e1; 65,536 patterns * 64 fills = 4,194,304 inputs, TEST = RULE in all, the rule holds in 16,384 (2^-8); a
  lane inside a word of seven lanes with random neighbours gives the same eight bits as alone, 140,000 of
  140,000; the constants typed there are those of the program. (c) `tools\build_pkg7.py --program`. And the
  other way round (`evidence\plan_negative.txt`): seven wrong plans (a wrong mask, a wrong distance, a read
  position more or less, a shift that brings a bit above 31 or a bit of the next lane to a read position, a
  condition not read) all end in the error of `rule_a_constants()`.
- **Decisions identical with the program before any recoding** (`evidence\equiv_e1_0of2.txt`, `_1of2.txt`;
  `work\equiv_run.sh 200000 e1 2`): 200,000 batches (50,000 the last list word, 40,000 with extreme words). The
  two-level program of `research\pkg7_program` (cde390bf...6638: every word fetched, nothing kept, nothing formed
  again) runs its own outer step, table build, middle step and batch on the same sub-class; its stage-A word is
  made from ITS z by the rule as written on h1 (typed in the tool). Same seven members, same five table words,
  same stage-A flags and branch, same stage-2 words, flags and branch in 200,000 of 200,000; 5,493 of 1,400,000
  lanes satisfy the rule, 4,721 batches enter stage 2, no zero stage-2 word.
- **Reference, 50,000 trials** (`evidence\ref_compare.txt`): `outer()`, `middle()`, `member()`, `trial()`, the
  sixteen words, the two messages and the table row against `research\h8\twolevel\tl_ref.py`, by name, 50,000 of
  50,000 (2,000 contexts, every fifth with extreme words); the batch against `tl_batch.py` on the program's
  members, 400 of 400 batches per rule (table words, stage-2 words, flags, branch; for four conditions also the
  stage-A flags); `compress2` against the organizer's `verifier\blake3.py` with 2 rounds, 2,000 of 2,000.
- **One complete outer step** (`evidence\class_loop.txt`): the whole table, 18,725 words, all equal to
  `table_row()` of their members, 131,072 different members; the list V, 18,725 of 18,725 words; ALL 18,725
  batches of one value of X2: **131,075 of 131,075 lanes right** against the complete digests, stage counts (37,
  10, 105, 30) in every batch, 16 registers; three more values of X2 from three more middle steps on the same
  memory with the SAME table, 3,000 batches each: 21,000 of 21,000 lanes right each. Batches entering stage 2:
  574 of 18,725 (0.0307), then 0.0313, 0.0243, 0.0303 (the budget is 0.03125; see section 6, item 5).
- Forward compression written a second time (`evidence\check_program.txt`): 20,000 trials and both experiments
  through stdin/stdout, 46 check lines, all ok (lengths, zero tail, pin, S and X of the context, Y4 in the
  sub-class, digest words 0, 2, 5, 7, Lemma N, the rule on h1 against the program's test on z with the member's
  word of V, the round trip of the seven words, loop structure, the organizer's reference digests). 77 of 20,000
  trials satisfy the rule (2^-8 is 78.1).
- **Organizer harness, own mirror** `~/hashsmash/hash-smash-pkg7run` at 86f1102 (`evidence\validation_log.txt`,
  `work\validate_pkg7.sh tests`; candidate = `blake3-r2` of this folder, i.e. the new program with the text of
  pkg6; image present locally, not pulled): the repository's unit tests 23 + 84 + 176 OK (5 skipped);
  `local_tracks.py check`: `"status": "mechanically_valid"`; intake with the mirror copy marked ready: experiment
  status passed; **half-collision 256 of 256, replay identical; residual-search 256 of 256, replay identical**,
  tries mean 382.1, max 1721; observations in all 256 rows: stage A 37 + 10, stage 2 105 + 30, 7 lanes right; 9
  of 256 counted batches enter stage 2.
- Text scan of the program: findings 0, one line excepted for a constant of the pin, as in pkg6
  (`evidence\text_scan.txt`). Time: half-collision 0.1 s, residual-search 2.7 s for 256 seeds on the host, limit
  20 s (`evidence\time_experiments.txt`).

## 4. Cost table (`COST.txt`, `python -B work\tools\cost.py`; arithmetic in `tools\pkg7_data.py`)

time_log2 = 123.339 - log2(f) + log2(charged / 34) + 0.012; f = kept count / margin; charged = budgeted * 1.04
rounded up to 0.1; budgeted: a share 2^-(n-3) of the batches enters stage 2 (the program's `STAGE_2_BUDGET`; NOT a
measured share); expected: the share 1 - (1 - 2^-n)^7. Per trial: (18,725 * batch + middle step + (18,725 * 74 +
260) / 2^32) / 131,072; the middle step adds 0.00102, the table build and the outer step 2.5e-9. Kept counts:
`count\a15_totals.txt` (step COUNT).

| rule | kept count, exact (conservative) | stage A, stage 2 | expected | budgeted | charged | time_log2 at margin 3.75 | at margin 2.4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **8 (S8), the program** | 185,358,111.47 (185,355,453.45) | 47, 135 | 7.2367 | 7.3182 | **7.7** | **95.650** | **95.006** |
| 6 (old6) | 185,358,125.47 (185,355,465.45) | 41, 135 | 7.8714 | 8.2691 | 8.6 | 95.809 | 95.165 |
| 4 (p4) | 185,358,154.95 (185,355,465.45) | 37, 128 | 11.9339 | 14.4299 | 15.1 | 96.621 | 95.977 |
| 8, every read a load (`KEPT = 0`) | as above | 57, 143 | 8.6963 | 8.7826 | 9.2 | 95.906 | 95.262 |
| 6, every read a load | | 51, 143 | 9.4194 | 9.8406 | 10.3 | 96.069 | 95.425 |

- f at margin 3.75 is 49,428,830 = 2^25.5588; at margin 2.4 it is 77,232,546 = 2^26.2027. With the program's
  `FACTOR` 49,400,000 (margin 3.7522): 95.650. With the conservative count no figure of the table moves (the two
  counts differ by 2,658 of 185 million).
- At one decimal, rounded up as pkg6 prints: **95.7** (margin 3.75) and 95.1 (margin 2.4; 95.006 is 0.006 above
  95.0: margin 2.3906 or less prints 95.0). The filed pkg6 is 97.519 (charged 19.1, f = 2^25): 1.87 lower here.
- The charged 7.7 has room for 0.6 operations per batch in stage A (budgeted * 1.04 = 7.611). One operation or
  load less in stage A would give 7.5 (95.612); one more 7.8 (95.668); two more 8.0 (95.705).
- The estimate of the task (95.5 to 95.9) holds. The figure "95.449" of the step COUNT assumed stage A 41 for
  eight conditions; the machine counts 47.

## 5. Measurement of the stage-2 entry (NOT used in any budget)

`work\tools\entry_share.py` (numpy on the CPU, real trials in the member order of the program, h1 anchored against
the program's complete compression of message A: 65,536 of 65,536 anchors equal in each run):

| run | trials | rule 8: share of the trials | batches entering stage 2 | single contexts | per outer step |
| --- | --- | --- | --- | --- | --- |
| 8,192 independent contexts (`evidence\entry_share_8192x1_1.txt`) | 2^30 | 2^-8.0019 | 0.026170 | 0.0071 to 0.0421 | same |
| 512 outer steps * 16 values of X2 (`evidence\entry_share_512x16_1.txt`) | 2^30 | 2^-7.9992 | 0.026224 | 0.0120 to 0.0421 | 0.0239 to 0.0289 |
| 8,192 independent contexts, second seed text (`evidence\entry_share_8192x1_2.txt`) | 2^30 | 2^-8.0000 | 0.026222 | 0.0122 to 0.0406 | same |

Budget of the program: 1/32 = 0.03125; independence formula 0.02704; 7 * 2^-8 = 0.02734. For the rule with six
conditions: 2^-6.00, 0.0979 and 0.0981 (budget 0.125; single contexts 0.026 to 0.163); four: 2^-4.00, 0.2405.

## 6. What is NOT established

1. **No text.** Proof, claim, manifest and note are those of pkg6. Nothing of sections 1 to 5 is in them, the
   manifest still describes the old search (524,288 members, 55 + 32 and 115 + 48), and the errata of the filed
   text (`research\grok\answer18_redteam6.md`, `research\proveout\audit\AUDIT.md`, Sol's referee report) are not
   applied. `tools\pkg6_data.py` (177 KB, tokens and paragraphs of the old arrangement) is NOT ported: it is set to
   `TEXT_PORTED = False`, `SUBMISSION_STATE = "draft"`, so `tools\build_pkg6.py` renders nothing (do not run it
   with `TEXT_PORTED = True` on this folder: it would look for a line `TRIALS_LOG2` in the program and stop, and
   its Lemma A is the old one). The new figures are in `tools\pkg7_data.py`; `tools\build_pkg7.py --program`
   compares the program with them. The docstring of the program still cites sections of proof.md by the numbers
   of pkg6; changing it changes the SHA-256, and the program has 1,798 bytes of room. Eight scripts that came with
   the copy still name `research\pkg6` by its absolute path and would write into the filed package if run from
   here (`ready_all.ps1`, `validate_pkg6.sh`, `tools\selftest_big.sh`, `tools\selftest_big_launch.sh`,
   `tools\rule_a_sat_all.sh`, `tools\rule_a_sat2_all.sh`, `tools\rule_a_sat2_one.sh`, `tools\rule_drat_all.sh`): each
   got a first statement that stops it (`work\tools\_guard_copies.py`); whoever ports them removes it.
2. **Lemma A in its new form is checked, not proved.** Complete enumeration three ways and every real lane
   (section 3), but no written proof and no reader. The text needs: the plan, why each read position holds what
   it holds, why bits 32 and above and neighbour bits never reach a read position, the list V, and the carry test.
3. **The machine convention.** 47 and 135 need nine words kept in registers for a class loop and two values
   formed again in stage 2. That is inside "16 registers, every executed load and store charged" (the register
   file that refuses confirms 16), but it is not the sentence of the filed text ("fetched from memory each time it
   is used"). Under that sentence the row is 57 and 143, charged 9.2, 95.906. The text has to say which machine it
   is. 16 of 16 registers are in use, no slack. No address addition is charged for the list loads (three in
   stage A: XA, X6, V; four in stage 2), as in pkg6: with one each, 50 and 139, charged 8.1, 95.723 (arithmetic).
4. **The list V** is a second static list (18,725 words, 0.57 MiB; with the table of an outer step and the list U
   4.00 MiB in all). Its making (131,072 members, a few operations each) is preprocessing and is not counted.
5. **The stage-2 budget is exceeded in single contexts.** Measured over 2^30 real trials the share of the batches
   that enter stage 2 is 0.0262 in three runs, 16 percent below the budget 2^-5, but single contexts reach 0.042,
   and the complete value of X2 of section 3 has 0.0307 (3,000 batches of the next value: 0.0313). For the filed
   pkg6 the largest single context reported was below its budget (0.1684 against 0.25, its FILE_STEPS.md). So here
   the budget holds only as an average over the contexts of a run (the largest of 512 outer steps of 16 values
   each was 0.0289); that it holds over a run is a heuristic and is not proved, and the dependence of the pass
   rate on the context is not analysed. The same is true of the rule with six conditions (single contexts up to
   0.163 against 0.125).
6. **Ranges, end tests, trial space.** As in `research\pkg7_program`: the ranges of the six words of the outer
   step and the end tests of the two loops are not defined in the program (the cells the end tests compare with
   are placeholders; the outer step steps w5 by one). A run of 2^101.442 trials is 2^52.442 outer steps of 2^32
   values of X2 with 131,072 members each; whether the ranges of `research\pkg7_prep\text\02_loops_and_trial_space.md`
   give that many, and that no two trials of a run are the same pair, is not shown here. The amortised table build
   assumes that every outer step serves all 2^32 values of X2; for N values it adds 10.57 / N per trial.
7. **No real-message evidence for this sub-class and rule beyond the processor.** No run on the graphics card, no
   count of the E1 event, of H1 or of H2 in the sub-class, no scaled-down end-to-end run with real collisions in
   this enumeration. The layout runs of `research\pkg7_prep\layout` are for the whole class and other rules.
8. **The kept counts** are those of the step COUNT (`count\COUNT.md`, with its own list of what is not established:
   60 betas, 16 outcomes counted by one function, exact against conservative). Nothing was recounted here.
9. **FACTOR.** 49,400,000 is this helper's reading of "margin about 3.75". The owner decides factor and margin; a
   change is one line of the program and of `tools\pkg7_data.py`, a new SHA-256, and the tests again (the counts do
   not depend on it). The charge (1.04, one decimal) and the tail 0.012 are taken as given; the work per passing
   trial on a machine with kept words (the registers are loaded again: 9 loads) is not written out.
10. The rules with four and six conditions have 250,000 cases, not 1,000,000, and no measurement beyond section 5.
11. The middle step still computes two lines and stores one word that no batch needs (S0, w1), and does not set
    the list position back (one operation per value of X2, 8e-6 per trial).
12. Not run: `scripts\prepare_experiment_image.py` (it pulls an image; the pinned image was already in the local
    Docker). As in pkg6: the owner has not confirmed that the organizer's rules allow a 2-round compression inside
    the experiment program (`compress2`, called only to check the counted batch), and the owner's own word scan
    would report the line that prints the constant X3.
13. The helper edited no file of the handoff or the master plan.

## 7. Files and commands

| file | what it is |
| --- | --- |
| `blake3-r2\experiments\halfsearch.py` | the program |
| `tools\pkg7_data.py` | ONE place for the new figures: sub-class, rules, factor, counts, cost arithmetic, reader of `count\a15_totals.txt` |
| `tools\build_pkg7.py` | `--program`: the program against `pkg7_data.py` (nine lines, class, rules, budget, counts of the three rules, Lemma A) |
| `tools\pkg6_data.py`, `tools\build_pkg6.py`, `src\`, the other `tools\` | still those of pkg6; switched off (`TEXT_PORTED = False`), state draft |
| `COST.txt` | the cost tables (three tables, counts, evidence quoted) |
| `work\tools\` | `common.py`, `counts.py`, `every_use.py`, `register_peaks.py`, `lane_bound.py`, `ref_compare.py`, `check_program.py`, `class_loop.py`, `selftest_small.py`, `selftest_big.py`, `entry_share.py`, `text_scan.py`, `time_experiments.py` (those of `research\pkg7_prep\opt`, changed for the sub-class, the list V and the new rules; `_edit1.py`, `_edit2.py` are the edits), and new: `equiv.py`, `lemma_a_enum.py`, `plan_negative.py`, `tracer_counts.py`, `cost.py` |
| `work\selftest_big.sh`, `work\equiv_run.sh`, `work\validate_pkg7.sh`, `work\wsl_status.sh` | the WSL scripts |
| `work\evidence\` | what the tools wrote |
| `count\` | the step COUNT, untouched |

Commands (PowerShell, from `research\pkg7`, unless WSL is named; every WSL process is started with `nice -n 5`):

    python -B -s blake3-r2\experiments\halfsearch.py --selftest 2000 1
    python -B tools\build_pkg7.py --program
    python -B work\tools\selftest_small.py
    python -B work\tools\counts.py 1500
    python -B work\tools\every_use.py 600
    python -B work\tools\register_peaks.py 200
    python -B work\tools\tracer_counts.py 300
    python -B work\tools\lane_bound.py 2000
    python -B work\tools\lemma_a_enum.py 64
    python -B work\tools\plan_negative.py
    python -B work\tools\ref_compare.py 2000 25 400
    python -B work\tools\check_program.py 20000 256
    python -B work\tools\class_loop.py 3 3000
    python -B work\tools\entry_share.py 8192 1 1
    python -B work\tools\entry_share.py 512 16 1
    python -B work\tools\entry_share.py 8192 1 2
    python -B work\tools\text_scan.py
    python -B work\tools\time_experiments.py
    wsl -d Ubuntu -- bash "./research/pkg7/work/equiv_run.sh" 200000 e1 2
    wsl -d Ubuntu -- bash "./research/pkg7/work/selftest_big.sh" 61 8:1000000
    wsl -d Ubuntu -- bash "./research/pkg7/work/selftest_big.sh" 61 4:250000 6:250000
    wsl -d Ubuntu -- bash "./research/pkg7/work/validate_pkg7.sh" tests
    python -B work\tools\cost.py                       (reads the evidence; run it last)

## 8. Credit, as the handoff has it

GPT Sol 6.1 (the rule with eight conditions and the exact figures of the sub-class, reproduced by the step COUNT);
winglock (the idea of a sub-class, first used on our first entry); Th0rgal (the coding items 2.2 to 2.4 of his
note, carried over by `research\pkg7_prep\opt`, and words kept in registers); 5kyguy (masks kept in registers);
Grok 4.7 (`job15_batch`: an independent tightened batch with the same idea, read and compared, not used).
