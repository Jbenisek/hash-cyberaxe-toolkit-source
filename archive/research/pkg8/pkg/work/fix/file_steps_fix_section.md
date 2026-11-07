
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
