# 95.7 package: ready for your decision

**Nothing has been submitted.** It waits for your approval.

## What it is

The improved entry for the same path as the filed 97.6: claim **time_log2 = 95.7**, margin 3.75. Your decisions of
2026-10-07 about 01:05: 95.7; state the 96.0 every-read-a-load alternative; co-authors winglock, Th0rgal, 5kyguy,
tekkac in the co-author field; file after Grok's review and your approval.

## Checks done

- Exact count: three independent sources agree to the last digit.
- Three helper reviews, all fixed; a fourth on the parts nobody had read: no error.
- Grok 4.7 hostile review with its own code: no error in the collision, the count, the cost or the 95.7. Its
  corrections are applied (pass FIX3).
- Real messages for this sub-class and rule (2^44.6 trials): the test passes at exactly 2^-8; the second-stage
  charge is on the safe side by 19 percent.
- Server: the sub-class on random outer steps, 275 deepest events against 288.1 predicted.
- Small hash with real collisions, sub-class and eight-condition rule: 121 found against 120.2 predicted.
- Organizer validation on the current files: mechanically valid; tests 23 + 84 + 176 OK; intake 256/256 twice,
  replay identical; the text format and word scans are clean.

## The one open point, for you to decide

The last text pass was meant to reconcile some wording. Its helpers were **stopped by a safety filter** before
doing anything, and nobody will work around that. So there are two finished versions, both valid:

- **Version FIX4 (current files).** Cites all the new runs and has the "approaches that failed" section. But an
  independent check found some sentences that say slightly more than their sources, and some older sentences that
  now contradict the new evidence section. The list is in `work\fix4\check\VERDICT.md`. None touches the program,
  the count or 95.7.
- **Version FIX3 (saved in `work\fix4\prev`).** Has Grok's corrections, but five sentences still say that some runs
  do not exist, which now do. That **understates** the evidence, which is the safer direction.

Your options:
1. File **FIX3**: safest wording, slightly out of date. (My recommendation if you want it out today.)
2. File **FIX4** as it is.
3. Fix the sentences listed in `work\fix4\check\VERDICT.md` yourself, then I rebuild, validate and file.
4. Hold.

## To file, after your approval (I run these)

1. Read-only look at our submissions (none in flight on this track).
2. Restore the chosen version if it is FIX3, then `tools\stage_pkg7.sh` (checks the frozen hashes first).
3. Compare hashes (must match).
4. `yukon submit --track blake3-r2-exploratory --note-file ... --model "Claude Opus 5.5" --harness "Claude Code"
   --coauthors @winglock @Th0rgal @5kyguy @tekkac`. If the platform rejects a handle, I stop and ask.

## Hashes, FIX4 (current)

proof.md 0bd9e181...81c7 (2,389 lines); claim.json b649a9b8...f5a1; note 3bfda493...fe63; halfsearch.py
cde9b827...5563 (unchanged in every pass). Full list: `FILE_STEPS.md`, Step FIX4.

## Not established (as the text itself says)

The three statistical assumptions; no person has read the text; the 8-bit small-hash test of the two-level order
is 3.3 percent low (10-bit level); the listed E1 outcome on the sub-class is unresolved at the local run's
precision (14 against 21.6), while the server's random arm on the same sub-class gave 275 against 288.1.
