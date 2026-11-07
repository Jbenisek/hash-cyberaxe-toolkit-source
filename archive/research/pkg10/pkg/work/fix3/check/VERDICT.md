# pkg7 Step FIX3: verdict of the checking agent (2026-10-07)

**VERDICT: NOT READY.** Every change FIX3 made is one of the requested corrections, or a direct mechanical result of
one. The new figures are right, the organizer's check gives mechanically_valid on a copy marked ready, and every
hash agrees with the files that stage_pkg7.sh checks against. Two things still stand in the way of filing, and
neither comes from FIX3:

1. **Statements about evidence are out of date.** The package and the note still say that runs exist nowhere, but
   those runs are now on disk. `pkg7_evidence\gpu-subclass\GPU_SUBCLASS.md` (00:41) and `pkg7_evidence\small\SMALL.md`
   (00:31) were both written before the FIX3 build (01:05). The out-of-date places are:
   - proof.md lines 65-67: "No measurement exists for the sub-class with rule A beyond samples of at most 2^30 ...".
   - proof.md lines 1875-1883, under "What does not exist": no graphics-card run for the sub-class or rule A, no
     scaled-down run with a sub-class or a rule, and no measurement in the ranges.
   - claim.json line 33, the H1 limitations: "No run on a graphics card exists for the sub-class or for rule A ...;
     No scaled-down run has a sub-class or a first-stage rule".
   - claim.json line 51, the H3 limitations: "no run on a graphics card records it".
   - note line 152: "No run on a graphics card has the sub-class or the new rule. No scaled-down ...".

   The fixing agent flagged this, and it was outside the scope of FIX3. The owner has to decide between two fixes:
   cite the runs, or reword. Section 10 already uses a rewording for the layout runs: "... are not used in this
   text". Either fix changes the text, so it needs a rebuild, a new validation and a new freeze.
2. **The co-author sentence is a condition on how the package is filed.** The note now says "winglock, Th0rgal,
   5kyguy and tekkac are named in the co-author field of this submission". FILE_STEPS.md (lines 308-309 and 326)
   still says to add `--coauthors` only if the owner says so, and that the flag form is "not confirmed". The sentence
   is true only if the `yukon submit` command names exactly those four. If it does not, the sentence has to come out
   (and that means a refreeze).

## Every byte difference between work\fix3\prev and the present files

I compared the files by SHA-256, line by line, and word by word. The scripts are `cmp.py` and `words.py`, and their
output is in `cmp_summary.txt`, `cmp_diffs.txt` and `words_out.txt`. Unchanged: `experiments\halfsearch.py`, the
experiments manifest, the certificates manifest, `src\manifest.json` and all 8 files in `src\parts\`.

**blake3-r2\proof.md** (24d26f90 -> 17743622; 2,252 -> 2,257 lines). The word-level diff finds exactly 17 changes.
Every one is a requested correction:

| proof.md line | change | source |
| --- | --- | --- |
| 52 | 185,377,197 -> 185,377,197.55; 162,266,763 -> 162,266,763.66 | Grok 4 |
| 410 | "(the eighth under the name Y4 in the lines of round 1)" inserted | F2 (REVIEW's words; `--` changed to parentheses) |
| 507-510 | "are among those on which E3.h1 depends (the lines for ... Y14 and E3.h1)" -> "are the line for E3.h1 and the ten it depends on (... Y14)" | F4 (REVIEW's wording, exact) |
| 700 | "and each mask word holding the printed value in every lane (6.5)" inserted | F3 (REVIEW's wording, exact) |
| 1046-1052 | register convention, peak of 17 under the strict convention, spill sentence | Grok 3 |
| 1249 | 2^70.04 -> 2^70.03 | Grok 2 |
| 1261 | 1.1428 -> 1.1429 | Grok 4 |
| 1301 | m up to 3.75 -> 3.74 | Grok 2 |
| 1343 | 2.6 -> 2.67 | Grok 2 |
| 1355-1357 | 0.0270 -> "0.027025 ..., which rounds to 0.0270," (cost 7.2367 unchanged) | Grok 2 |
| 2077-2079 | "1.14287 rounded down; 1.1428 is the figure to four decimals" -> "1.142868; to four decimals that rounds down to 1.1428, and the nearest four-decimal figure is 1.1429" | Grok 4 |

The opening paragraph and Lemma T2 (a) were re-wrapped. The word diff shows nothing else changed in them. The line
counts shift by +1 at line 410, -1 at line 507 and +5 at lines 1046-1052.

**blake3-r2\claim.json** (ee114134 -> bfbc61d8). Field by field:
- H1 `extrapolation`: the last sentence was replaced (Grok 1).
- H2 `scope`: 2^70.04 -> 2^70.03 (Grok 2).
- H3 `scope`: 1.1428 -> 1.1429 (Grok 4).
- 7 `evidence_ids` entries moved with the new line numbers: 1215-1303 -> 1220-1308, 1454-1940 -> 1459-1945 (three
  times), 1240-1248 -> 1245-1253, 903-1213 -> 903-1218 and 1250-1264 -> 1255-1269. This follows mechanically from the
  added lines. For every range, the first line, the last line and the lines just outside it are identical before and
  after.
- Nothing else changed: `submission_state` is "draft", `time_log2` is 95.7, and no other field moved.

**submission-note-r2.md** (b6961c7a -> ef173f0e): the co-author sentence (task item 3) and the H1 "What is assumed"
bullet (Grok 1). Nothing else changed.

**Source files**, which match the rendered changes above:
- `src\claim.json`, `src\note.md`, `src\proof_cost.md`, `src\proof_evidence.md`, `src\proof_head.md`,
  `src\proof_search.md`.
- `tools\pkg7_text.py`, 5 lines: `charge_room` dn 1 -> 2; `pass_expected` up -> near; the new `indep_share_6`;
  `cluster_m` now computed from the printed 1.87; `trial_share` dn -> near.

**FROZEN_fix.sha256** (the claim and proof lines) and **FROZEN_fix_note.sha256** were regenerated. **FILE_STEPS.md**
is a record, not a package file: the header was changed, owed items 1-5 were marked discharged, and a "Step FIX3"
section was added.

No difference was found outside the requested corrections and their mechanical results.

## The arithmetic, recomputed from scratch

- (1,009,254.4 - 959,206.094073) / 18,725 = 2.672807, so 2.67 is right.
- 1 - (255/256)^7 = 0.02702539, so 0.027025 is right, and 0.0270 is right. The cost at that share is 7.236685, so
  7.2367 is right (at exactly 0.0270 the cost would be 7.236196).
- log2 N = 101.441993, and minus 31.41 that is 70.03199, so 70.03 is right. The gap is 13.968, so "more than 2^13.9"
  still holds, and the budget rate is -17.44199.
- 1.87 / -ln 0.607 = 3.74579, so 3.74 is right. At m = 3.74 the bound is 0.39047, and at 3.75 it is 0.38966. The
  expected count of good trials is 1.876068, printed as 1.87, "or more".
- 18725/16384 = 1.14288330, so 1.1429 (nearest) is right. 74899/65536 = 1.142868042, so 1.142868 is right.
- 194382080300609/1048576 = 185,377,197.5523, so .55 is right. 85074516985129/524288 = 162,266,763.6588, so .66 is
  right.

## Minor findings (none of them blocks filing by itself)

- **"costs far less than the margin" (proof.md lines 1050-1052) is overstated if the spill is a store plus a load.**
  I measured the batch with `regpeak.py` and `regspill.py`, without changing the program, over 40 batches. Under the
  strict convention the batch peaks at 17 registers, in stage A ("C2 to z", "rule A") and in stage 2 ("E1, A and B").
  In all 40 batches, 3 of the resident words are unused across all 17 stage-A peak steps. Dropping one of them and
  loading it again costs 1 load per batch, plus at most 1/32 for stage 2. That is about 39% of the 2.67 margin. A
  store-and-load spill, which is what "spilled and loaded again" describes, costs 2 of the 2.67. That is less than
  the margin, but not "far less". The scalar is not affected either way: 7.3182 + 2 x 18725/131072 = 7.604, below
  7.7. A tighter wording: "costs one load per batch, well under the 2.67 left".
- **1.1429 in "H3 holds whenever fewer than E trials ..., a share of 1.1429 times 2^-8"** (proof.md line 1261 and
  the claim's H3 scope). This is the nearest figure, which is the house convention. Read as a threshold on its own, it
  is 1.7e-5 above the exact 1.142883. Grok noted that 1.1428 is the safe form for a sufficient condition. The binding
  condition is E, which is exact, so this is acceptable.
- **Section 7, proof.md line 1287, still prints 185,377,197** (the floor of .55) among "the three figures". This is
  the same kind of truncation as Grok item 4, but Grok did not list it. It is unchanged.
- **The FIX3 record says `r_class_int` is used in Sections 7 and 12.** It is no longer used anywhere in `src\`. Only
  `r_sub_int` remains, in `proof_cost.md`. This is only a slip in the record.
- **Two files outside the package changed after FIX3:** `research\pkg7\MORNING.md` (01:26) and
  `work\failed_approaches_sources.md` (01:25). Neither is a package file, and there is no prev copy to compare them
  against.

## Validation

**My own rerun** used `check\validate_check.sh`, a copy of `tools\validate_pkg7_fix.sh` with its log in check\. It
ran on a fresh throwaway mirror at `/tmp/pkg7check3/hash-smash`, at 86f1102f, with nice 5, no network and no image
pull.
- Unit tests: 23, 84 and 176 OK (5 skipped).
- `local_tracks.py check` on the draft: mechanically_valid.
- On the mirror copy marked ready: mechanically_valid. The intake status is mechanically_valid, with package_sha256
  a48d06fc...
- Experiments passed:
  - half-collision: 256/256.
  - residual-search: 256/256, tries mean 382.1, max 1721.
  - Both replays identical.
  - Stage 2 entered: sum 9.
- Program sha256 cde9b8279eaad69a148d570714fbbcceea8bd81faab8ef10773faa9fa38f5563, unchanged from prev.
- Log: `check\validation_log_check.txt`. Report: `check\experiment-report-check.json`.

**Hashes.** All 5 package files and the note match `FROZEN_fix.sha256` and `FROZEN_fix_note.sha256`, which are the
files `tools\stage_pkg7.sh` checks against. There are 5 files on disk and 5 in FROZEN, and there is no `__pycache__`.

**Other checks:**
- `tools\fmt_pkg7.py`: "RESULT: nothing wrong", 27/27 quotations found, and the scalar 95.7 follows (2^95.64989).
- `tools\text_scan_pkg7.py`: findings 0.
- My scan (`scan.py`): 0 non-ASCII bytes, 0 CR, 0 links, 0 HTML comments and 0 words aimed at a reviewer, in all 6
  files.

## Not run

- `tools\build_pkg7.py`: it writes the package, which I am not allowed to do. The rebuild-is-unchanged result is
  therefore the fixing agent's, not mine.
- The long self-test, the counts, any GPU run, `proof_lines_pkg7.py` and `lemma_a_text_pkg7.py`.
- `research\public_text_scan.py`: it scans fixed paths, not pkg7. My `scan.py` applies the same patterns to pkg7.
- `tools\stage_pkg7.sh` and `yukon`: forbidden.
- The co-author handles: I could not check them without the network.

No tool call was refused or stopped.
