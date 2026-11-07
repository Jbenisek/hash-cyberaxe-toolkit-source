# Four-pattern contradiction (rows 18/19): close37/job2 "only 2 of 4 live" vs the +1.93..1.98 lever

Date 2026-10-12. Verdict: the lever stands; close37/job2's "P00/P10 dead" is a held-fixed artifact of its own window setup (answer (a), second option). No package, LEVERS.md or HANDOFF.md edited.

## Why job2 saw P00/P10 dead
job2 runs `window --rows 19 21 --prefix-relax Pxx` on chi37_job2.txt. The pattern relaxation only acts on the prefix (rows < 19). E19 is drawn inside the window, where the BASE cell row 19 E[29]=1 is forced (carrier "union", forced 6 bits at stage 19). The lever's parity E18[10]^E19[29]=0 (and E18[29]=E18[10]) needs E19[29]=0 when E18[10]=0. With E19[29] held at 1 and E18[29]=E18[10]=0 the Ch term at step 21 no longer cancels at bit 29, so the row-21 stage is unsatisfiable: exactly the E18[10]=0 patterns (P00, P10) die, E18[10]=1 (P01, P11) live. That is the observed split. It is a property of the held printed E19[29] cell, not of the characteristic: the lever replaces the 8 value conditions by 6 parities that include E19[29].

## Independent evidence that all four patterns are live on the full path
1. Verified full 37-step collisions exist for three non-printed patterns (research/tighten/r37_unforced_files, recomputed here with verify_alts.py, 37-step digests equal): alt_G1 = (E18[1],E18[10]) = (1,0) = P10; alt_G2 = (0,1) = P01; alt_G12 and i_all52 = (0,0) = P00. All other printed cells hold in them.
2. tests/known_answers.sh K4 command re-run (hist_out.txt; 512 SMC prefixes, rows 18..21, R1v): patterns passing rows 18..21 = 266 / 253 / 246 / 259 (P10, P00, P11 printed, P01); 1024 total, equal to R1. Row 21 passes for all four.
3. r37_unforced.md exact enumeration (199 prefixes x 2^32 W18): pattern shares 0.237/0.256/0.263/0.244; W20/W21 counts identical for prefixes of all four patterns.

## Decisive bounded check (this folder)
chi37_job2_e19z.txt = chi37_job2.txt with ONLY the row-19 E cell bit 29 changed 1 -> 0 (copy also placed at tools/traillab/chi/chi37_job2_e19z.txt; its `check` reports FAILED only because the published pair violates that edited cell). Same command as job2 (window rows 19 21, event out, np 2048, mt 4096, seeds 1,2,3, threads 2). Window stages 19/20/21 all pass; every exact event is re-hashed through all 37 steps (replay mismatches 0). Outputs: fix_out.txt.

| pattern | E19[29] cell | exact events / 25,165,824 | exact rate log2 | prefix log2 P(4..18), 3 seeds |
|---|---|---|---|---|
| P11 printed (job2) | 1 | 1945 | -13.65 | -44.95 |
| P01 (job2) | 1 | 1917 | -13.68 | -45.06 |
| P10 (this run) | 0 | 1853 | -13.72 | -45.05 |
| P00 (this run) | 0 | 1834 | -13.74 | -44.99 |

All four are equal within error (Poisson sd about 2.3 percent = 0.03 bit). P00/P10 are not dead; they revive with the right E19[29].

## Answers
(a) Both measurements are right but measure different things: job2 holds E19[29]=1 fixed in a pattern where the lever requires E19[29]=E18[10]. The lever's own full-path q3 (K4 / r37_unforced 1.93, CI 1.78-2.09) uses the relaxed E19[29] and counts all four patterns, each about 1/4 of the total.
(b) The filed gain stands: relaxed vs printed-only is about 4x = 2 bits structurally, measured 1.93 (1.98 in the traillab q3 run). No evidence for the "1 bit" revision. close37/job2 row (S37-JOB2-PAT, gain 1.0) should be marked as an artifact, not applied.
Not tested here: rows 22+ per pattern separately (event "out" includes them in each exact event; r37_unforced shows steps 20..23 pattern-independent); a fresh joint q3 of the whole path was not re-run.
