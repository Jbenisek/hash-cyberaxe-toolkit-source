# pkg7 Step FIX4: verdict of the checking agent (2026-10-07)

**VERDICT: NOT READY.** Every byte that FIX4 changed belongs to one of the four requested changes, or follows
mechanically from one. The organizer's check gives mechanically_valid on a copy marked ready, the program is
unchanged, and every hash agrees with the files that `tools\stage_pkg7.sh` checks against. Most new figures match
their source files. But the package text is still not right:

- Four statements written in FIX4 are stronger than their evidence, or are attached to the wrong rule (A to D below).
- Seven older statements that FIX4 did not touch now contradict the new Section 10 (E below). This is the same
  kind of defect that made FIX3 NOT READY.

Every fix is a text change at the source, then a rebuild, a new validation and a new freeze. None of them touches
the program, the count, the factor or the scalar.

## Blocking findings

**A. FIX4 turned a correct "does not exist" into a wrong "exists"** (proof.md lines 1957-1962, the third bullet
of "What does not exist").
- The new bullet ends: "for an event of E1 or E3 in those full ranges there are only the review's processor
  measurements".
- The review's processor measurements in the ranges of step 2 count rule A and the entry to stage 2 only
  (`review\judge7_entry_ranges.txt`; proof.md lines 1765-1772). No E1 or E3 event is counted in them.
- The old bullet was right: "No measurement in the ranges of step 2 ... of an event of E1 or E3; for rule A only
  the measurements of the review".
- Fix: "for an event of E1 or E3 in those ranges there is no measurement; for rule A there are only the review's
  processor measurements".

**B. "The deepest marker" is the wrong label, and it reports only the favourable result.** It appears in proof.md
line 67 (the opening summary), line 1948 (the first bullet of "What does not exist"), the H1 limitations in
claim.json, and note line 153.
- All four say that the deepest marker the run reaches is the partial E3 event at 2^-32.2, about 1.18 times richer
  in the sub-class.
- The same run reaches a deeper event, the listed E1 outcome at 2^-40.15. There it saw 14 against 21.59. The
  sub-class rate is 5.3e-13 against 7.6e-13 for the whole class. `GPU_SUBCLASS.md` section 8 and the new Section 10
  text (lines 1890-1891) both say so.
- Fix: write "the listed partial E3 event at 2^-32.2", not "the deepest marker". In the summary, H1 and the note,
  add that the listed E1 outcome at 2^-40.15 came in at 14 against 21.59, a shortfall the run does not resolve.

**C. The scaled-down run is described as fixed in advance, but only the first 6 of its 30 runs were** (proof.md
lines 1918-1919).
- The text says "The plan and the reading rule were written and hash-stamped before the counted runs."
- `SMALL.md` section 4: the 3 runs per set declared in advance gave 29 against 24.045 (z +1.01). The other 24 runs
  were declared in writing after that result was seen and before they ran. The result 121 against 120.23 covers
  all 30.
- The package discloses the same kind of follow-up for the 436-run job ("the later ones were made because of
  that"). Disclose it here too.

**D. Failed approach 4 gives figures for the wrong rule** (proof.md lines 2048-2053).
- The text says flipping a single free bit "changes the first-stage outcome with probability between 0.035 and
  0.063".
- Those figures come from the stage-A five-condition rule of entry c66f230d, measured on the class with 19 free
  bits (`h8\bitlevel\skip_report.txt`, GRID_REPORT section 1).
- This package's first stage is the eight-condition rule A. A rule that passes with probability 2^-8 changes its
  outcome with probability at most 2 x 2^-8 = 0.0078. So the figures cannot apply to this package's rule.
- Fix: name the rule ("for the five-condition rule of entry c66f230d").

**E. Seven older statements now contradict the new Section 10.** FIX4 did not change any of them.

| place | text today | what the new evidence says |
| --- | --- | --- |
| proof.md 1255 (H2) | "it was not measured in the sub-class" | the graphics-card run counts 9,537 E1-test passes ("E1 requires the eta that Y4 gives", `gpu-subclass\out\EVAL.txt`) in 2^44.585 trials, that is 2^-31.37 (whole-class layout runs: 9,520 of 2^44.58, 2^-31.37) |
| claim.json H2 limitations | "The rate was not measured for the sub-class." | same as above |
| proof.md 1773-1774 | "These and the three runs above are the only measurements that have the sub-class and the rule of this package." | the graphics-card runs and the scaled-down run at lines 1878-1927 have them too |
| proof.md 1979-1982 (Limits) | "The scaled-down runs reach whole collisions ... without the sub-class and the rule" | line 1907 describes a scaled-down run with both |
| proof.md 2001-2004 (Limits) | "The pass rate of the E1 test is measured for the whole class only. The share of the batches ... is measured on 2^30 trials three times, and by the review" | both are now measured on the graphics card for the sub-class (2^-31.37; 0.026178) |
| proof.md 2328-2331 (Section 12) | "It lacks what the filed entry had: runs on a graphics card for its own class of values of Y4 and its own rule" | it now has them (Section 10) |
| note 146-147 | "For the sub-class with the new rule there are only processor samples of at most 2^30 real trials" | contradicted by the very next bullet (line 152) |

There is also a smaller one. proof.md lines 2020-2024 list the evidence that was added after the review, and the
list does not include the FIX4 additions. "The reviewers have not read these changes" is still true.

## Minor findings (none blocks filing by itself)

- **The opening of "Approaches tried" overstates the bullets** (line 2027). It says "each says what would be needed
  to revisit it". Only items 1, 7 and 9 say that.
- **Item 9 gives the wrong bottom of the range.** It says "estimated at 102 to 107". In `paths\ATLAS.md` Table 1
  the best other family is 101.34 (62/64, delta 6, two-level; 101.48 for 57/63). The range is about 101 to 107.
- **Item 8 drops a name.** It reads "A participant server search". The source credits GPT-6 Luna, the owner's
  agent on the server ("GPT-6 Luna ran it"). The rest of the package names other models.
- **The "Chosen and random outer words" paragraph mixes figures from two sets of runs.**
  - The arm counts 421/421.2, 235/226.1, 275/288.1 and +5.04 sd come from `task7_layout_gpu\out\collect.txt`.
  - "measured at 1.087 and 0.914" comes from `h8\layout_rule\out\RULE_stats_C15_base16384.txt` (the m15 arms,
    256 tuples each, 2^42 trials).
  - collect.txt's own arms measure W = 1.0980 and 0.9115.
  - The model's +-8.48% (`pred.txt`) is printed as "about 8.4"; to the nearest digit it is 8.5.
- **"On the same members and geometry"** (line 1891) should read "on the same pin and geometry". The comparison is
  between the sub-class and the whole class.
- **Item 5, "the estimated scalar is about 96.9", does not say which arrangement it is.** It is the scalar of the
  earlier five-condition arrangement (ML_REPORT, 96.86), not of this package's 95.7.

## Every difference between work\fix4\prev and the present files

I compared the files by SHA-256 (`cmp.sh`, `cmp_out.txt`), with unified diffs (`d_*.diff`), and claim.json field by
field (`d_claim_fields.txt`). Nothing changed in:
- `experiments\halfsearch.py` (cde9b827...5563)
- `experiments\manifest.json`
- `certificates\manifest.json`
- `src\manifest.json`, all 8 files of `src\parts\`, `src\proof_cost.md` and `src\proof_search.md`
- `tools\pkg7_text.py`

No file was added to blake3-r2 or src.

| file | old -> new | what changed | which requested change |
| --- | --- | --- | --- |
| blake3-r2\proof.md | 17743622 -> 0bd9e181; 2,257 -> 2,389 lines | lines 65-72: opening summary rewritten (+5 lines) | Change 1 |
| | | lines 1878-1943: three new Section 10 subsections | Change 2 |
| | | lines 1947-1962: bullets 1-3 of "What does not exist" replaced (bullets 4-5 unchanged) | Change 1 |
| | | lines 2026-2077: "Approaches tried that did not improve this path", 10 bullets | Change 3 |
| blake3-r2\claim.json | bfbc61d8 -> b649a9b8 | H1 limitations (3,006 -> 3,249 chars) | Change 1 |
| | | H3 limitations (1,164 -> 1,309 chars) | Change 1 |
| | | 15 `evidence_ids` ranges moved: +5 after line 65; s10 end 1945 -> 2077 | mechanical result of Changes 1-3 |
| | | nothing else: `submission_state` "draft", `time_log2` 95.7, claim block, restrictions, statements, scopes, extrapolations and H2 unchanged | |
| submission-note-r2.md | ef173f0e -> 3bfda493 | one bullet, lines 152-157 | Change 1 |
| src\proof_head.md, src\proof_evidence.md, src\claim.json, src\note.md | | the templates of the rows above; `build_pkg7.py --check` gives "unchanged" for all four outputs (no drift) | Changes 1-3 |
| FROZEN_fix.sha256, FROZEN_fix_note.sha256 | | regenerated (claim, proof and note lines) | freeze |
| FILE_STEPS.md | | NEWEST-STATE header, the owed-caution, the owner-decisions line, the file command with `--coauthors @winglock @Th0rgal @5kyguy @tekkac` and "STOP if a handle is rejected", and the Step FIX4 section | Change 4, plus the record. The decision matches HANDOFF "UPDATE 01:05", verbatim "1 95.7, 2 yes, 3 yes, 4 wait" |
| work\fix4\freeze.sh, work\text\validation_log.txt | | the fixing agent's freeze script and its validation log | not package files |

`prev\validation_log_before.txt` exists only in prev. It is the saved copy of the earlier log and is not a
difference in any present file. No file under research\pkg7 changed after 01:30 apart from the files listed above.

I checked every evidence range. Each one starts at its heading or paragraph and ends just before a blank line:
245-545 is Section 4, 549-621 is 6.1-6.2, 640-777 is 6.3, 779-906 is 6.4, 908-1223 is 6.5, 1225-1313 is Section 7,
1250-1258 is H2, 1260-1274 is H3, and 1464-2077 is Section 10 up to "Scope and limitations" (it now includes the
Approaches section).

## The new figures, each read in its source file

- **Graphics-card sub-class run** (`pkg7_evidence\gpu-subclass\GPU_SUBCLASS.md`, `out\EVAL.txt`). All of these
  agree with the source:
  - 24 tuples, 2^23 values of X2, 131,072 members; 24 x 2^40 = 2^44.585; bad 0, contradictions 0.
  - 2^21 words, 0 disagreements.
  - 103,079,088,429 passes, which is 2^-8.000002 (I recomputed it).
  - 24 x 2^40 / (3 x 2^30) = 8,192.
  - 98,688,658,735 / 3,769,840,435,200 = 0.026178; 0.027025; 0.8377 -> 0.838.
  - 6,314 against 5,353.63; 14 against 21.59 at 2^-40.15.
  - 1.1833 at 8.9 sd; 1.148 +- 0.051; 0.998.
  - 268 / 6,314 / 2^-8 = 10.87.
  - 185,358,111.47 of 185,377,197.55 not measured.

  The wording problems are in B above.
- **Scaled-down run** (`pkg7_evidence\small\SMALL.md`). These agree:
  - 30 runs; 30 x 2^34 = 515,396,075,520 trials; 2,013,236,457 passes.
  - 121 against 120.23, sd 10.96, z +0.07; bad, bogus and lost all 0.
  - First stage 2,013,265,920 expected, z -0.66; 9 per cent (10.96 / 120.23 = 0.091).
  - Kept 0.071 and 0.085, written as "7 to 9 per cent"; the real rule keeps 0.999897.

  The one problem is the "hash-stamped before the counted runs" wording (C above).
- **Chosen and random arms** (`task7_layout_gpu\out\collect.txt`): 421 / 421.2 / 345.7, 235 / 226.1 / 288.1,
  275 / 288.1 and +5.04 sd all agree. 1.087 / 0.914 and 3.7-4.0% (0.0366 and 0.0396 between tuples) are in
  `h8\layout_rule\out\RULE_stats_C15*.txt`, and +-8.48% is in `pred.txt`. See the minor finding about mixing the
  two sets of runs.
- **Failed approaches** (`work\failed_approaches_sources.md` and the files it names):
  - Item 1: 222,513, all at e = 2, none split (`redlift\main\out\st_side1_r2.txt`).
  - Item 2: 0.6 s to 6.0 s; levels 3 and 4 UNKNOWN at 900 s (`satlift\out\runs.txt`).
  - Item 3: 30 of 30 UNSAT; blocks 35, 20 and 49; 18,900 against 11,673; 0.7 bit (`block\VERIFY.md`).
  - Item 4: 0.035 to 0.063, but for the five-condition rule (D above).
  - Item 5: 11, 25, 26 and 6, 18, 19; 96.86 (`multilevel\ML_VERIFY.md`, `ML_REPORT.md`).
  - Item 6: 4,432 pins; 177.69, a relative 1.1e-6 (`realize\REALIZE_REPORT.md`).
  - Item 7: 253 = 100 + 153; proved lower bounds 78, 71, 71 and 75, so unsatisfiable up to 70 to 77
    (`fouractive\FOUR_REPORT.md`). Grok 4.7 is the model's name in `ai_credits.md`.
  - Item 8: bounds 100 to 103 UNKNOWN at 3,600 s each; bound 104 gives 107,785 and 30,487
    (`astra-jobs\task6-results\out\totals.txt`, `trail5_server.log`).
  - Item 9: 102 to 107 (see the minor finding: the bottom is 101.3).
  - Item 10: 2,000 of 2,000 real trials (HANDOFF line 818).
  - The fixing agent was right to drop the 0.048%/0.049% figure.
- **Arithmetic and rounding:** H1 limitations 3,249 of 4,096 characters; 0 non-ASCII bytes, 0 CR and 0 tabs in the
  proof, the claim and the note.

## Claim fields, program and validation

- **claim.json:**
  - `submission_state` is "draft" and `time_log2` is 95.7.
  - The claim block, restrictions, statements, scopes and extrapolations are unchanged. Only the H1 and H3
    limitations and the evidence ranges moved.
  - `build_pkg7.py --check` (read-only): no drift; state draft; time_log2 95.7 (bound 2^95.6499); factor
    49,400,000; 2^101.442 trials; charge 7.7.
- **Program:** halfsearch.py is cde9b8279eaad69a148d570714fbbcceea8bd81faab8ef10773faa9fa38f5563, the same byte for
  byte as prev. `build_pkg7.py --program` gives:
  - rule 8 stage A 37+10, stage 2 105+30; Lemma A patterns 65,536 of 65,536.
  - The program has the pin, the sub-class, the three rules, the factor and the budget.
- **Organizer's mechanical check:** I ran `check\validate_check.sh tests`, a copy of `tools\validate_pkg7_fix.sh`.
  It used a fresh throwaway mirror at `/tmp/pkg7check4/hash-smash` (at 86f1102f), nice 5, no network and no image
  pull. The log is in `check\validation_log_check.txt` and the report in `check\experiment-report-check.json`.
  - Unit tests: 23, 84 and 176 OK (5 skipped).
  - `local_tracks.py check` on the draft: mechanically_valid.
  - On the mirror copy marked ready: mechanically_valid. The intake status is mechanically_valid, with
    package_sha256 5d04ded0154d920757bd3aae1b869b6579d4b1f539e0959e3cbe7cd51c48c53b, the same as the fixing agent's
    log.
  - Experiments passed. half-collision: 256/256. residual-search: 256/256, tries mean 382.1, max 1721. Both
    replays identical.
  - Stage 2 entered: sum 9. Stage A 37+10, stage 2 105+30.
- **Hashes:**
  - `sha256sum -c FROZEN_fix.sha256`, run from blake3-r2 as `stage_pkg7.sh` runs it: 5 of 5 OK.
  - The note's hash equals the first 64 characters of FROZEN_fix_note.sha256 (3bfda493...).
  - There are 5 files in the package and 5 in FROZEN; no `__pycache__`.
- **Other checks:**
  - `fmt_pkg7.py`: "RESULT: nothing wrong". Longest restriction 994 of 1024; longest heuristic field 3,249 of
    4,096; 27 of 27 Section 11 quotations; the scalar 95.7 follows (2^95.64989); 9 cited ranges.
  - `text_scan_pkg7.py`: findings 0 (the two pin-constant lines are excepted, as before).

## Not run

- `build_pkg7.py` in write mode. I am not allowed to write the package; I ran `--check` and `--program`, which are
  read-only.
- The long self-test, the counts, any GPU run, `proof_lines_pkg7.py`, `lemma_a_text_pkg7.py`, and
  `research\public_text_scan.py`. The last one scans fixed paths; `text_scan_pkg7.py` was run instead.
- `tools\stage_pkg7.sh` and `yukon`, which are forbidden; no `.key`; no network. The co-author handles were not
  checked, because that needs the network.

No tool call was refused or stopped. Files written: only in `work\fix4\check\`, plus the throwaway WSL mirror
`/tmp/pkg7check4`.
