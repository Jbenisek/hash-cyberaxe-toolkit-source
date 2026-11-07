# pkg7 (DRAFT): state on 2026-10-06 after the step TEXT, how to build it, what is owed before filing

**NEWEST STATE: the section "Step FIX3" at the end (2026-10-07, the corrections of the Grok review and the text
review). The SHA-256 values just below, and those in "Step FIX", are superseded by the ones in "Step FIX3".**

Not part of the package. Nothing was staged, synced, filed or posted, no `yukon` command was run, the network and
the GPU were not used, `.key` was not read. pkg7 is a DRAFT: `SUBMISSION_STATE = "draft"` in `tools\pkg7_data.py`,
and `blake3-r2\claim.json` says "draft". The record of the filed package it started from is
`research\pkg6\FILE_STEPS.md` (frozen; not repeated here). Read with this file: `count\COUNT.md` (step COUNT) and
`PROGRAM_STEP.md` with `COST.txt` (step PROGRAM).

## What pkg7 is

The 55/63 path of the filed entry c66f230d (pkg6, 97.6) with the two-level program, a sub-class of the class, a
rule with eight conditions and a batch that keeps nine words in registers.

| | pkg6 (filed, c66f230d) | pkg7 (draft) |
| --- | --- | --- |
| construction | context of seven words, then the member (steps S1, T) | outer step, X2, member (steps O, M, Y, T), a table per outer step |
| values of Y4 | class 830303cf, 524,288 members | sub-class (e1 AND 07ef8303) == 030c0303, 131,072 members, 18,725 list words |
| count under the model | 162,266,763.66 | 185,377,197.55 (194382080300609/1048576) |
| rule A | five conditions | eight (h0=0, h1=1, h16=0, h17=0, h2^h10=1, h3^h11=1, h3^h12^h24=0, h6^h13^h25=0) |
| count that H1 is set against | 126,003,600 | 185,355,453 (exact with the rule: 185,358,111.47) |
| assumed factor, margin | 2^25, 3.75 | 49,400,000 = 2^25.558, 3.75 |
| trials | 2^102 | 1,424,469 * 2^81 = 2^101.442 (C0.d1 below 1,424,469; w5, X2 all values) |
| stage A, stage 2, share | 55 + 32, 115 + 48, 1/4 | 37 + 10, 105 + 30, 1/32 |
| other pieces | per X14 163 (charged 1,024) | middle step 134, table build 74 per list word, outer step 260 |
| charged per trial | 19.1 (budgeted 18.2521) | 7.7 (budgeted 7.3182) |
| time_log2 | 97.6 (bound 2^97.5186) | **95.7** (bound 2^95.6499, stated 2^95.65) |

Other readings of the same program (all in the proof and the note): every read of a memory word a load (`KEPT = 0`)
57 / 143, charged 9.2, 96.0; one more operation per list or table load 50 / 139, charged 8.1, 95.8; rule with six
conditions 41 / 135, share 1/8, charged 8.6, 95.9; factor 2^25 96.3; uniform rate 121.3.

Rendered files after the step TEXT (SHA-256):

    blake3-r2\proof.md                   84dc9d06589a03bee9a62bbabe3a8f4cda75b8a822bc753b304cc96e981db086  (2,159 lines)
    blake3-r2\claim.json                 e8a0d9430580d90b69066d59a6f89d4c8b2ad953973a193d56d9a88526a4b64e
    blake3-r2\experiments\manifest.json  3ba8bc765bcb2bbe3835ad78dac25f46f58875f90d647e7285c99d1edc5acff8
    blake3-r2\experiments\halfsearch.py  cde9b8279eaad69a148d570714fbbcceea8bd81faab8ef10773faa9fa38f5563  (unchanged since the step PROGRAM)
    blake3-r2\certificates\manifest.json a3c78779269ab224b0a36cc0cc075aaebdfb496a3a695bce1e743cf7bd45c4c8  (empty list)
    submission-note-r2.md                53a7d3b3673f9f455bc73d09e0896857d7aa74c9813f2a1ea3532db990a74e7c

Any build changes these; `python -B tools\fmt_pkg7.py` says whether the files on disk are what the templates give.

## Who did what

1. Step COUNT (helper agent): `count\`. Our counter with a sub-class option; every figure of GPT Sol 6.1 reproduced.
2. Step PROGRAM (helper agent): the experiment program, `tools\pkg7_data.py`, `COST.txt`, `work\` with its evidence.
3. Step TEXT (helper agent, the author of this file): the text. `src\` (templates), `tools\pkg7_text.py`,
   `tools\build_pkg7.py` (text build added; `--program` kept), `tools\proof_lines_pkg7.py`,
   `tools\lemma_a_text_pkg7.py`, `tools\fmt_pkg7.py`, `tools\text_scan_pkg7.py`, `tools\extract_parts.py`,
   `tools\validate_pkg7_text.sh`, `work\text\`. The program was NOT changed (its docstrings still call steps O and
   M "Step S1, first part / second part"; the proof says so in Section 4).
4. NOBODY HAS REVIEWED THE ASSEMBLED TEXT. The three reviews of the workflow come after this step.

## What the step TEXT did

Ported from the filed text (copied once by `tools\extract_parts.py` into `src\parts\`, with the word changes listed
in that tool; the build never reads pkg6): Sections 1 to 3 (hash, G, Lemmas L and H, Fact P), the class and
Lemma Q, 6.2, Lemma N, the packed word, the description of the count (steps 1 to 4). Carried over in substance:
Section 5, H2, the scope items, the field meanings, the memory of the selection.

New text:
- Section 4 in three levels from `research\pkg7_prep\text\01_new_order.md`, with the fixes of its verifier: three
  folded lines named, no "always changes" sentence, Lemma T2 restated on the displays (names in the place of line
  numbers; Table C with names; the wide Tables O and C are not in the proof, which is limited to 79 columns).
- 6.1: the sub-class and Lemma Q2. 6.3: rule A with eight conditions; Lemma A (a) to (d) in a new form WITH A
  PROOF (the step PROGRAM had it checked, not proved); the list V. The early test (Lemma E) is dropped.
- 6.4: ranges, loop form, Lemma T3, from fragment 02 with the verifier's fix: the text says that the program has
  no loops, no step 3 and no ranges, and the loop is defined so that the program's pieces are its body (entered
  behind the branch; the end cells hold 0, which is what the program's cells hold).
- 6.5: lists U and V, the 21 + 9 stored words, the table, Lemma T4, the batch of the recoded program, THE MACHINE
  CONVENTION (nine words kept in registers; stage 2 forms two values again and reloads four words), lane bounds
  for the recoded batch (9B), the tables from the program's own `TABLES`, the self-test.
- Section 7: H1 with its two parts named; H2 with a budget of 2^84; H3 stated on batches.
- Section 8: cost with every term (machine counts plus loop control bounded in words: 1 per X2, 8 per outer step,
  16 per value of C0.d1); the preprocessing item split into a bound and an estimate.
- Section 10: the count from `count\` with the other model's fractions beside it; the checks; what exists on real
  messages for this arrangement and what does not.
- Section 11 "Corrections to our entry c66f230d": 24 items (6 errors of statement, 8 figures, 7 statements
  stronger than their evidence or unstated conventions, 3 reported points that are not errors). Each was looked up
  in the filed text. `tools\fmt_pkg7.py` checks that all 27 quoted passages are in the filed proof, claim or note
  word for word. Verified by computation here: 45,271 / 32,768 = 1.3816; 67,065,401 * 16 / 2^30 = 0.99935;
  0.150015 in the evidence file; Poisson 0.917 against 0.944; 74,899 / 65,536 = 1.14287; the exact total from our
  count. NOT confirmed as errors and listed as such: the sampler mean 159,056,562 (the evidence file has that
  figure), "14 of them" (the program counts words in which some lane passes), "13,312 contexts" (the audit
  recomputed it from the raw files).
- Section 12 (same / new) and Section 13 (credit: GPT Sol 6.1, winglock, Th0rgal, 5kyguy, tekkac, Grok 4.7, the
  model reached through Venice as unverified, helper agents).
- `claim.json` (state draft, 95.7, the three heuristics), the experiment manifest (predicts 37, 10, 105, 30), the
  note (credit first, the readings table, the corrections, limits).

## Checks run in the step TEXT (all on the files with the hashes above)

| check | command | result |
| --- | --- | --- |
| displays of Section 4 and Table C as printed, parsed from the template | `python -B tools\proof_lines_pkg7.py 20000` | 96 lines (29, 21, 10, 12, 24), 88 cells of Table C, 20,000 tuples (2,000 extreme, 10,000 in the sub-class): names, program, words, half-collision, Y4, eta, read back: all right (`work\text\proof_lines.json`) |
| Lemma A (a) to (d) as stated, against the program | `python -B tools\lemma_a_text_pkg7.py 4` | 262,144 cases, wrong 0, the rule holds in 1,024; v of the text = `rule_word()` (`work\text\lemma_a_text.txt`) |
| program against the data module | `python -B tools\build_pkg7.py --program` | holds; Lemma A patterns 16 / 512 / 65,536 right |
| short self-test | `python -B -s blake3-r2\experiments\halfsearch.py --selftest 2000 1` | exit 0; 14,000 of 14,000 lanes; counts as `TABLES` (`work\text\selftest_2000_1.json`) |
| build | `python -B tools\build_pkg7.py` | written; no unknown name, no line over 79 |
| format and text | `python -B tools\fmt_pkg7.py` | nothing wrong (drift, ASCII, widths, JSON, field lengths 994 of 1024 and 2,806 of 4,096, the nine cited ranges, sections 1 to 13, lemmas, the scalar three ways, 27 quotations of Section 11) |
| public text scan | `python -B tools\text_scan_pkg7.py` | findings 0 (two lines excepted for a constant of the pin, as in pkg6) |
| organizer harness, own mirror `~/hashsmash/hash-smash-pkg7text` at 86f1102 | `wsl -d Ubuntu -- bash ".../research/pkg7/tools/validate_pkg7_text.sh" tests` | `mechanically_valid`; tests 23 + 84 + 176 OK (5 skipped); intake with the mirror copy marked ready: both experiments passed, 256 of 256, replay identical; tries mean 382.1; stage 2 entered on 9 of 256 (`work\text\validation_log.txt`) |

NOT run in this step: the long self-test (the one of the step PROGRAM is quoted; the program has the same
SHA-256), `work\tools\*` of the step PROGRAM, the counts, any GPU run, `research\public_text_scan.py` (the owner's
scan; it would report the line with the constant X3, as for pkg6).

## One place each

- Sub-class, rule, factor, machine, counts: `tools\pkg7_data.py` (PART A and B). A change of rule or factor
  changes the program and its SHA-256; then every file in `work\evidence` and `work\text` has to be made again.
- Every figure of the text: `tools\pkg7_text.py` (the names `{{...}}` of the templates). It stops when an evidence
  file does not name the SHA-256 of the program, when a rounded bound is below its value, or when the table of
  betas does not add up to the totals of the count.
- The budget of step 3 (2^84), the loop-control bounds (1, 8, 16) and the measured E1 rate (2^-31.41): the first
  lines of `tools\pkg7_text.py`.
- The text: `src\proof_head.md`, `proof_search.md`, `proof_cost.md`, `proof_evidence.md`, `claim.json`,
  `manifest.json`, `note.md`. Never edit the rendered files.

## Commands (PowerShell, from `research\pkg7`)

    python -B tools\proof_lines_pkg7.py 20000       (after any change of the displays or of Table C)
    python -B tools\lemma_a_text_pkg7.py 4          (after any change of Lemma A or of the program)
    python -B -s blake3-r2\experiments\halfsearch.py --selftest 2000 1 > work\text\selftest_2000_1.json
    python -B tools\build_pkg7.py
    wsl -d Ubuntu -- bash "./research/pkg7/tools/validate_pkg7_text.sh" tests
    python -B tools\build_pkg7.py                   (only the note changes: it quotes the validation log)
    python -B tools\fmt_pkg7.py
    python -B tools\text_scan_pkg7.py

The note quotes the harness only while `work\text\validation_log.txt` names the SHA-256 of the proof on disk;
after any change of the proof it says that the harness has not been run, until the validation is run again.

## Decisions for the owner

1. Factor and margin. 49,400,000 (margin 3.75, claim 95.7) is the reading of "margin about 3.75". Margin 2.4 would
   be 95.006 by the step PROGRAM's table, which prints 95.1.
2. The machine convention. 95.7 needs nine words kept in registers across batches; with a load for every read it
   is 96.0. The text states both. Other teams count lighter (32 or 64 registers).
3. H3 has room of 19 percent in the samples (0.0262 against 0.03125) and single contexts exceed the budget. A
   budget of 1/16 would cost about 0.11 in the scalar (estimate) and would need a change of the program.
4. Co-author field: the proof and the note credit winglock, Th0rgal, 5kyguy and tekkac by name;
   `research\others\CREDIT.md` proposes them as co-authors. The owner decides the field.
5. The name of the other model in the credits ("GPT Sol 6.1 (OpenAI)"), as for pkg6.
6. As for pkg6: the 2-round compression inside the program, and the owner's scan on the line with X3.

## Owed before filing (in order of weight)

Items 1 to 5 are DISCHARGED in Step FIX3 (2026-10-07); see that section at the end for detail. Item 6 stands.
CAUTION: the runs that discharge items 2 to 4 are NEW and are NOT yet cited in the package text. Section 10
("What does not exist") and the limitations still say there is no graphics-card run for the sub-class or for
rule A and no scaled-down run with a sub-class or a first-stage rule. Reconciling the package text with this new
evidence was out of scope for Step FIX3 (which applied only the listed review corrections) and is left for the
owner / a later step.

1. Review of the assembled text; Lemma T2 as restated, Lemma Q2 and Lemma A with its proof have been read by nobody
   but their author. -> DISCHARGED: `research\pkg7_evidence\textreview\REVIEW.md` and
   `research\grok\work\job23_pkg7_review\ANSWER.md` reviewed the assembled text (the exact part incl. Lemmas Q, Q2,
   L, A and parts of T2; the count; the cost; the whole text). Their findings are applied in Step FIX3.
2. A real-message run for THIS sub-class and THIS rule on the GPU (events of E1 and E3, the E1 pass rate, the rule
   with an E3 event). -> DISCHARGED: `research\pkg7_evidence\gpu-subclass\GPU_SUBCLASS.md` (24 outer tuples of
   2^40 real trials on sub-cube C15, mask 07ef8303 value 030c0303; the early test, E1 beta/tau/outcome and partial
   E3 events, and the rule on h1 recorded per run, plus a model run).
3. A scaled-down end-to-end run with a sub-class and a first-stage rule. -> DISCHARGED:
   `research\pkg7_evidence\small\SMALL.md` (sets 34 and 41; collisions among the trials that passed the rule
   against the exact prediction for exactly those trials; VOID TEST bad/bogus/lost 0).
4. A layout run in the ranges of the text (C0.d1 small and consecutive, w5 and X2 from 0). -> DISCHARGED:
   `research\pkg7_evidence\gpu-subclass\GPU_SUBCLASS.md` (the same runs enumerate X2 consecutively from a base
   with every member in list order, in the two-level layout).
5. The larger scaled-down job (task 5) and the returned server files were not evaluated for this text. ->
   DISCHARGED: `research\pkg7_evidence\servereval\SERVER_EVAL.md` (task 4 and task 5 recomputed from the raw
   files; every figure the text quotes reproduced).
6. The owner's decisions above; a person has read nothing.

## Not established (stated in the text as limits)

- H1, H2, H3. The model fails inside one context for rule A and inside one outer step for E1; only averages over
  outer steps agree with it.
- The loops, the ranges, step 3 and the loop control are defined in the text only; the cost of a pass (2^10) and
  the loop control are bounded in words.
- The list of 60 betas was not searched again; 16 outcomes with a product were counted by one function; Sol's
  sets are "best found", not proved best.
- The preprocessing bound covers two message words only; the selection has an estimate.
- No figure of `research\pkg7_prep\layout` is for the sub-class or for rule 8; they are quoted as what they are.

## Stale files in this folder (copies that came with pkg6; not used by the pkg7 build)

`evidence\` (the evidence of the filed program), `check_pkg6.py`, `ready_all.ps1`, `validate_pkg6.sh`, `review\`,
`ready_logs\`, and in `tools\`: `pkg6_data.py`, `build_pkg6.py`, `fmt_pkg6.py`, `text_scan_pkg6.py`,
`selftest_pkg6.py`, `proof_lines_check.py` and the count and rule tools of pkg6. The eight scripts that name
`research\pkg6` by its absolute path still carry the stop line of the step PROGRAM. The old templates of pkg6 in
`src\` were replaced; the rendered files of pkg6 as they stood before this step are kept in
`work\text\proof_before_text_step.md` and `claim_before_text_step.json`.

## Step FIX (23:50, after the three reviews): what changed, the final figures, how to stage and file

State: DRAFT (`SUBMISSION_STATE = "draft"`, `claim.json` "draft"). Nothing staged, synced, filed or posted; no
`yukon` command; no network; the GPU was not used; `.key` not read; pkg2 to pkg6 not touched. The program is
UNCHANGED (`cde9b827...5563`). The step TEXT's files are kept in `work\fix\before\` (templates, rendered files,
`pkg7_text.py`, this file, the TEXT step's validation log).

### Findings of the reviews: all applied at the source (`src\`, `tools\pkg7_text.py`)

Each was checked against the files first; none turned out wrong.
- count-cost 1 / judge 4: "3,243 integers per outcome" -> "on 1,081 outcomes (three per outcome)" (claim H1
  extrapolation, note).
- count-cost 2: the margin is nominally 3.75 as in c66f230d but tighter; sentence in Section 7 (there 4.29 and
  4.83 times 2^25 for the exact rule count and the whole count; here 3.75, 3.75, 3.75), pointer in Section 12.
  `FILED_RA = 302248762304709/2097152` added to `pkg7_text.py` (checked to round to 144,123,440.89).
- count-cost 3: "about 2^27.46" -> 2^27.47 (rounded to nearest); "= 2^97.386" -> "itself more than 2^97.386".
- construction 1: shared family corrected in 6.4 (X9, X14 the same in every trial of a run; 25 of 29 outer lines
  without C0.d1; Y8, Y12 from C0.c1, D3.d1, S9, w5, y alone: 1,424,469 * 2^32 = 2^52.44 trials share Y12 and w5;
  2^49 pairs), in the model paragraph and the limits of Section 10, and in claim H1 limitations. Verified by
  reading `outer()` and `member()` of the program.
- construction 2-4: 10.58 -> 10.5717; "from U, the seven words above and the word C0.d1 of the slow loop"
  (`table_build` loads `k("C0.d1")`); the P of 6.4 and of claim H3 renamed J (P was also Fact P and the cost of
  Section 8).
- judge 1: "our first entry 04638ed8" -> "our entry 04638ed8 (112.4)" (proof Section 13, note).
- judge 2: item 7 "three cells" -> "four cells" (proof, note).
- judge 3: summary and H1: the rates equal the other model's fractions; 185,355,453 is the participant's alone
  (also claim H1 extrapolation, note).
- judge 5: review status in Section 10 (exact part, limits), Section 13 intro, claim H1 limitations, note: three
  helper agents reviewed once; the corrections and the evidence added afterwards were NOT read again by them.
- judge 6-13: 0.3346 of r (1.8e-9, from `count\COUNT.md:221`); deepest event 0.91 with limits 0.785 and 1.046
  (`pkg7_prep\layout_verify\VERDICT.md:155`); Section 11 intro qualified for item 4 (and the note); item 19
  gained the unstated shares 1/2 and 1/8 (filed table rows recomputed by the audit, `AUDIT.md:175`; Grok
  `answer18_redteam6.md:86-91`); note gives 0.02617, 0.02622, 0.02622; same seed text of the first two
  processor runs, 512 contexts common (checked in `work\tools\entry_share.py`); winglock 18a7fc52 as first
  public count without sampling, "to the participant's knowledge" (from `research\others\CREDIT.md:123`; the
  second half of that proposal, whether our counter was written independently, is left OUT for the owner);
  item 23 "ambiguous and wrong in the referee's reading", heading "not errors of fact".
- judge notes: the four undescribed scaled-down runs are the self-check runs (3 against 6.8; from
  `task5_small_h8\ref\LOCAL_RESULTS.txt`); the reviewers' measurements in the ranges of step 2 are now cited
  (0.026171 in 8,192 contexts, 2^30 trials, 5 contexts above 1/32; 0.02619 on 2^22; 0.02620 in 640 contexts).
  The judge's one was RERUN here (`work\fix\rerun_entry_ranges.py 4 2`): output identical but for the time.
- count-cost note: "if the sub-class had only the class rate, 3.28 times the factor" added to the limits.
- count-cost note on the selection estimate: estimate (2) of Section 8 now covers the solver search and the
  counts only; the measurements of Section 10 are said to select nothing and to be outside it (the server runs
  below may be near 2^60 operations). The 2^60 term of T and its 2^90 sensitivity statement are unchanged.

NOT applied: the overnight layout queue (judge note; still running, not evaluated, said to be unused); the
judge's request to delete the stale pkg6 copies before staging (owner; `stage_pkg7.sh` copies only `blake3-r2`).

### Evidence added after the reviews (HANDOFF 23:20, 23:32, 23:36; each figure read from its file by me)

- Server task 5 (`astra-jobs\...\task5_small_h8\out\collect.txt`): two-level scaled-down, 8,448 runs, 8,108
  against 8,313.6 (-2.25 sd); 8 bits 6,276 / 6,489.6 (-2.65, 3.3% low), 10 bits 1,832 / 1,824.0 (+0.19); set 5
  series 0 has 38 / 40.0; bad 0, bogus 0. EXPECTED.txt (19:45) was written before the run (out 23:08). Section
  10, limits, claim H1 extrapolation, note.
- Server task 4 (`task4\out\collect.txt`): order of c66f230d, whole class, 24 x 2^45 real trials (2^49.58):
  692 / 690.78 listed E1 outcomes, beta+tau -0.07, beta -0.76, E3 partial -0.53, every run within 2.2 sd.
  Section 10 (new paragraph), claim H1 extrapolation, note.
- Cloud Sol (`astra-jobs\sol_cloud_answer_2.md:216, 235, 326-346`): same two fractions; sub-class the unique
  best 15-bit sub-cube; the eight conditions (another basis of the same affine set, checked by hand) a
  "certified global optimum". Section 10 and credit; stated as NOT checked by the participant.
NOT added: the filed-layout small-hash total "417 against 399.51" of HANDOFF (the text keeps the verifier's 345 /
335.76 and 93 / 93.97); Sol jobs O, P, S and Grok job 20 (cluster lever; not used by this package).

### Final figures (unchanged by the fixes)

`claim: state draft, time_log2 95.7 (bound 2^95.6499), factor 49,400,000, 2^101.442 trials, charge 7.7, count
for H1 185,355,453.45 (with rule A 185,358,111.47, all 185,377,197.55), sub-class 07ef8303/030c0303 (131,072
members), margin 3.75`. Stage A 37 + 10, stage 2 105 + 30, budgeted 7.3182. Other readings: every read a load
96.0; address additions 95.8; rule 6 95.9; factor 2^25 96.3; uniform 121.3.

### Checks run on the final files (all by me, this step)

| check | result |
| --- | --- |
| `python -B tools\proof_lines_pkg7.py 20000` | everything holds, 20,000 tuples (`work\fix\proof_lines_run.txt`) |
| `python -B tools\lemma_a_text_pkg7.py 4` | 262,144 cases, wrong 0 (`work\fix\lemma_a_run.txt`) |
| `halfsearch.py --selftest 2000 1` | exit 0; output byte-identical to `work\text\selftest_2000_1.json` (14,000 of 14,000) |
| `python -B tools\build_pkg7.py --program` | holds; rule 8: 37+10, 105+30, Lemma A 65,536 of 65,536 |
| harness, NEW own mirror `~/hashsmash/hash-smash-pkg7fix` at 86f1102 (`tools\validate_pkg7_fix.sh tests`) | `mechanically_valid`; tests 23 + 84 + 176 OK (5 skipped); intake with the mirror copy marked ready: both experiments passed, 256 of 256, replay identical, tries mean 382.1, stage 2 entered 9 of 256; `work\text\validation_log.txt` names the final proof and claim |
| `python -B tools\build_pkg7.py` (after validation) | all four files unchanged |
| `python -B tools\fmt_pkg7.py` | nothing wrong; 27 of 27 Section-11 quotations found; longest restriction 994/1024, longest heuristic field 3006/4096 |
| `python -B tools\text_scan_pkg7.py` | findings 0 (two pin-constant lines excepted, as before) |

Not run: the long self-test (quoted, program unchanged), the counts, any GPU run, `research\public_text_scan.py`.
The log header still says `validate_pkg7_text.sh` (hard-coded echo); its mirror line says pkg7fix.

### SHA-256 of the final files (also in `FROZEN_fix.sha256` and `FROZEN_fix_note.sha256`)

    blake3-r2\proof.md                   24d26f90f2ed282a47c94c256dccebad508a675457dedc06ec72d17c3f6a0d45  (2,251 lines)
    blake3-r2\claim.json                 ee1141341e58d8a3528226ea0c1ded8d725554563c1a0f523c82d33aaf1a1921
    blake3-r2\experiments\manifest.json  3ba8bc765bcb2bbe3835ad78dac25f46f58875f90d647e7285c99d1edc5acff8  (unchanged)
    blake3-r2\experiments\halfsearch.py  cde9b8279eaad69a148d570714fbbcceea8bd81faab8ef10773faa9fa38f5563  (unchanged)
    blake3-r2\certificates\manifest.json a3c78779269ab224b0a36cc0cc075aaebdfb496a3a695bce1e743cf7bd45c4c8  (unchanged)
    submission-note-r2.md                b6961c7aae4d6c5aed6a3bd39a3cb174e574201c7514bfe978a96dcc1575ee7a

### NOT established

- H1, H2, H3. No GPU or real-message run for the sub-class or rule 8; no joint count of rule 8 with an E3 event;
  the sub-class gain 1.142 rests on the model alone (without it 3.28 times the factor).
- The scaled-down two-level test is 3.3% low at 8 bits (-2.65 sd); cause unknown.
- H3: room 19% in the samples; single contexts exceed the budget (5 of 8,192 in the judge's in-range sample).
- Loops, ranges, step 3 and loop control exist in the text only.
- The changes of this step and the added evidence were NOT read by any reviewer (the lesson of item 17 applies).
- The cloud Sol's optimality statements are its own; not checked here.

### Owner's decisions

Factor and margin (95.7 at 3.75; the owner's 95.2 is not reached: about 95.1 at margin 2.4 by count-cost's
arithmetic, which needs a new factor and ranges, i.e. a program change); the register convention (96.0 with a
load for every read); co-authors (CREDIT.md proposes winglock, Th0rgal, 5kyguy, tekkac; the flag form below is
from CREDIT.md and is not confirmed); whether our counter was written independently of winglock's note; the name
"GPT Sol 6.1 (OpenAI)"; a re-read of this step's changes before filing. Contest end date: not in the organizer's
files (HANDOFF 20:46); not checked here (no network).

### Commands for the main session AFTER the owner's go (none was run here)

1. Check: `python -B tools\fmt_pkg7.py` (expect "RESULT: nothing wrong") and, in Git Bash from
   `research/pkg7/blake3-r2`, `sha256sum -c ../FROZEN_fix.sha256`. Any edit after this voids the hashes: then
   build, validate (`tools\validate_pkg7_fix.sh tests`), build again, fmt, scan, and remake the two FROZEN files.
2. Stage (sets "ready" in the staged copy only; keeps the filed c66f230d folder in
   `~/hashsmash/backup_candidates/`; written here, NOT run):
   `wsl -d Ubuntu -- bash "./research/pkg7/tools/stage_pkg7.sh"`
   expect "STAGED: all files identical to the frozen package" and `"status":"mechanically_valid"`.
3. File (PUBLIC AND PERMANENT; only with the owner's yes for this package), in WSL from
   `~/hashsmash/yukon/hashsmash`, as `research/r1/file_r1.sh` does it (put it in a script file; WSL quoting):
   `yukon submissions` (nothing in flight), then
   `yukon submit --track blake3-r2-exploratory --note-file "$HOME/hashsmash/notes/submission-note-r2-pkg7.md" --model "Claude Opus 5.5" --harness "Claude Code"`
   plus `--coauthors <names>` only if the owner says so.

## Step FIX3 (2026-10-07): the corrections of the Grok review and the text review, applied at the source

State: DRAFT (`SUBMISSION_STATE = "draft"`, `claim.json` "draft"). Nothing staged, synced, filed or posted; no
`yukon` command; no network; the GPU was not used by this step; `.key` not read; `tools\stage_pkg7.sh` was not
run. The program is UNCHANGED (`cde9b827...5563`). The scalar 95.7, the factor 49,400,000, the counts and the
program are unchanged by this step. The previous state (blake3-r2, the note, the two FROZEN files, `src\`,
`tools\pkg7_text.py`, this file, and the step-FIX validation log) is kept in `work\fix3\prev\`.

Sources: `research\grok\work\job23_pkg7_review\ANSWER.md` ("What to correct before filing" items 1 to 4) and
`research\pkg7_evidence\textreview\REVIEW.md` (STYLE findings F2, F3, F4). Each figure was checked against Grok
sections 2 and 3 before it was changed; none of Grok's figures was found wrong. All corrections were made at the
source (`src\` templates and `tools\pkg7_text.py`), never in the built files, which were then rebuilt.

### Changes (file -> rendered line -> old wording -> new wording)

Grok item 1 (the factor and the absence of clustering are assumptions):
- `src\claim.json`, H1 `extrapolation` (claim.json line 31), last sentence. OLD: "The extrapolation is from these
  to the rate of the event over the real trials of a run." NEW: "The factor and the absence of clustering are
  assumptions; the count is what the factor is set against, not a measurement of the trials, and none of these
  measurements reaches the joint event (R = 0 and rule A) over the real trials of a run that H1 asks about."
- `src\note.md`, "What is assumed" bullet (note line 138). OLD: "H1, H2 and H3 are assumptions. The factor
  {{factor}} is not measured by any experiment." NEW: "H1, H2 and H3 are assumptions. Both parts of H1, the factor
  {{factor}} and the absence of clustering of the good trials, are assumed; no experiment measures the factor, and
  the count it is set against is not a measurement of the trials."

Grok item 2 (four figures):
- 2.6 -> 2.67 per batch. `tools\pkg7_text.py` token `charge_room`: `dn(..., 1)` -> `dn(..., 2)`. Exact slack
  2.6728. proof.md line 1343: "...a reader may find uncounted, 2.67 per batch of seven trials."
- the 0.0270 share with its cost. `tools\pkg7_text.py`: new token `indep_share_6` = 0.027025 (the unrounded
  independent share); `src\proof_cost.md` main-loop sentence (proof.md ~line 1355). OLD: "a share of {{indep_share}}
  of the batches would run stage 2 and a trial would cost {{expected}} operations on average". NEW: "a share of
  {{indep_share_6}} of the batches, which rounds to {{indep_share}}, would run stage 2 and a trial would cost
  {{expected}} operations on average". Renders "a share of 0.027025 ..., which rounds to 0.0270, ... cost 7.2367";
  7.2367 is the cost at the unrounded share, as Grok section 3 states (at the rounded 0.0270 it is 7.2362).
- 2^70.04 -> 2^70.03. `tools\pkg7_text.py` token `pass_expected`: `up(..., 2)` -> `near(..., 2)`. lN - 31.41 =
  70.03199; nearest is 70.03 (Section 10 says counts with decimals are rounded to the nearest). proof.md line 1249;
  the gap "more than 2^13.9" is unchanged.
- clustering m 3.75 -> 3.74. `tools\pkg7_text.py` token `cluster_m`: computed from the unrounded expectation 1.876
  -> computed from the printed, rounded expectation `dn(expected_good, 2)` = 1.87, so m is consistent with the
  "1 - exp(-1.87 / m)" that the text prints. proof.md line 1301: "...the bound 0.39 would hold for m up to 3.74."
  (At m = 3.74, 1 - exp(-1.87/3.74) - 0.003 = 0.3905 >= 0.39; at 3.75 it is 0.3896.)

Grok item 3 (the register convention). `src\proof_search.md` (proof.md ~lines 1046-1052). OLD: "With that, the
batch uses all 16 registers; a register file of 15 does not run it." NEW: "With that, the batch uses all 16
registers, and 15 do not run it, under the program's convention that the result of an instruction may reuse a
register whose source value is used for the last time on that same instruction; if instead every source stays live
until its instruction finishes, the batch peaks at 17 registers, and the one extra word, spilled and loaded again
inside the batch, costs far less than the margin already left between the budget and the charge."

Grok item 4 (truncations and 1.1429):
- opening paragraph. `src\proof_head.md` (proof.md line 52). OLD: "it is {{r_sub_int}} times 2^-128 for Y4 in the
  sub-class ({{r_class_int}} for the whole class)." NEW: "it is {{r_sub}} times 2^-128 for Y4 in the sub-class
  ({{r_class}} for the whole class)." Renders 185,377,197.55 and 162,266,763.66 for the truncated 185,377,197 and
  162,266,763.
- 18725/16384 -> 1.1429. `tools\pkg7_text.py` token `trial_share`: `dn(..., 4)` -> `near(..., 4)`. 18725/16384 =
  1.142883; nearest is 1.1429. proof.md line 1261 and claim.json H3 scope: "a share of 1.1429 times 2^-8 of the
  trials." NOTE on Grok section 3: Grok says 1.1428 (rounded down) keeps a paraphrased sufficient condition
  ("share below 1.1428 x 2^-8") valid and that 1.1429 is the nearest four-decimal figure. The proof's actual
  wording is a DESCRIPTION of the exact batch budget E ("fewer than E trials ..., a share of 1.1429 x 2^-8"); E is
  exact, so the nearest value is accurate and does not weaken the condition. 1.1429 is therefore both what the task
  directs and correct here; Grok is not wrong, its caution is about a paraphrase, not the proof text.
- Section 11 item 12 (the same slip for the old ratio). `src\proof_evidence.md` (proof.md line 2077). OLD:
  "...is 74,899 / 65,536 = 1.14287 rounded down; 1.1428 is the figure to four decimals." NEW: "...is
  74,899 / 65,536 = 1.142868; to four decimals that rounds down to 1.1428, and the nearest four-decimal figure is
  1.1429." The quoted passage "1.142 times 2^-5" is unchanged; fmt still finds all 27 Section-11 quotations.

Text review F2/F3/F4:
- F2. `src\proof_head.md` Lemma T2 (a) (proof.md line 410). OLD: "and it reads only constants, the eight words and
  names of earlier lines." NEW: "and it reads only constants, the eight words (the eighth under the name Y4 in the
  lines of round 1) and names of earlier lines." (REVIEW gives the clause set off with "--"; the document uses no
  "--", so it is set in parentheses, the house style, with the reviewer's words unchanged.)
- F3. `src\proof_search.md` Lemma A (c) (proof.md line 700). OLD: "...the shifts being shifts of the whole packed
  word. Write y[i]..." NEW: "...the shifts being shifts of the whole packed word and each mask word holding the
  printed value in every lane (6.5). Write y[i]..."
- F4. `src\proof_head.md` "What Lemma T2 does not say" (proof.md line 508). OLD: "Eleven of the trial lines are
  among those on which E3.h1 depends (the lines for X0, D0.d1, D0.c1, X10, C2.a1, C2.d1, C2.c1, C2.b1, Y2, Y14 and
  E3.h1)." NEW: "Eleven of the trial lines are the line for E3.h1 and the ten it depends on (X0, D0.d1, D0.c1, X10,
  C2.a1, C2.d1, C2.c1, C2.b1, Y2, Y14)."

Task item 3 (credit sentence). `src\note.md` "Credit first" (note lines 8-9), one sentence added: "winglock,
Th0rgal, 5kyguy and tekkac are named in the co-author field of this submission, for the contributions this note
credits to them; no co-author is represented as having reviewed or endorsed the package."

### Nothing else was changed, and what was NOT applied
The scalar 95.7, the factor 49,400,000, the counts and the experiment program are untouched. `indep_share` (0.0270,
still used in Section 10 against the measured shares) and the integer tokens `r_sub_int`/`r_class_int` (used in
Section 7 and Section 12, where "times the factor" wants whole numbers) were left as they are. NOT applied, and why:
(a) Grok section-3/section-5 STYLE points that are NOT in its items 1-4 (the note's early "Only one batch in 32",
the "far inside the margin of 3.75" line, the opening-summary and claim-tension STYLE notes) and the SERVER_EVAL /
textreview style suggestions (F1-F4 of SERVER_EVAL) -- out of scope, the task lists only Grok items 1-4 and
textreview F2/F3/F4. (b) No change to Section 10's "What does not exist" or the limitations to reflect the new
sub-class/rule/in-range runs (gpu-subclass, small) -- out of scope and flagged in the owed list above for the
owner / a later step.

### Checks run (this step)

| check | result |
| --- | --- |
| `python -B tools\build_pkg7.py` (twice: build, then after validation) | written, then unchanged on re-run; time_log2 95.7, bound 2^95.6499 < 2^95.65 |
| harness, own mirror `hash-smash-pkg7fix` (`wsl ... tools\validate_pkg7_fix.sh tests`) | `mechanically_valid`; unit tests 23 + 84 + 176 OK (5 skipped); intake with the mirror copy marked ready: both experiments passed, 256 of 256 each, replay identical; tries mean 382.1, max 1721; stage 2 entered 9 of 256; stage A 37+10, stage 2 105+30; `work\text\validation_log.txt` names the new proof.md (177436...) |
| `python -B tools\fmt_pkg7.py` | RESULT: nothing wrong; longest restriction 994/1024, longest heuristic field 3006/4096 (H1 limitations); Section 11 27 of 27 quotations found; scalar 95.7 follows |
| `python -B tools\text_scan_pkg7.py` | findings 0 (two pin-constant lines excepted, as before) |

Not rerun (unchanged since Step FIX): the long self-test (program unchanged), the counts, any GPU run,
`research\public_text_scan.py`. The Section-4 displays and Table C are unchanged (the edits are in prose), so
`proof_lines_pkg7.py` and `lemma_a_text_pkg7.py` were not rerun; their `work\text\*.json` still match the program
and the displays, and the build accepted them.

### SHA-256 of the final files (also in FROZEN_fix.sha256 and FROZEN_fix_note.sha256, regenerated this step)

    blake3-r2\proof.md                   177436221877ec724ac733392561c1a77e1ff7bc004add67138c146b655c22d6  (2,257 lines)
    blake3-r2\claim.json                 bfbc61d8a80fe655a43d987fed2e91e25c28a97209a824c9cc231b82d55432cd
    blake3-r2\experiments\manifest.json  3ba8bc765bcb2bbe3835ad78dac25f46f58875f90d647e7285c99d1edc5acff8  (unchanged)
    blake3-r2\experiments\halfsearch.py  cde9b8279eaad69a148d570714fbbcceea8bd81faab8ef10773faa9fa38f5563  (unchanged)
    blake3-r2\certificates\manifest.json a3c78779269ab224b0a36cc0cc075aaebdfb496a3a695bce1e743cf7bd45c4c8  (unchanged)
    submission-note-r2.md                ef173f0e3ec28907f0d7070190c5103f690201469c621776959a4fa0c458e950
