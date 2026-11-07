# B3R4d (blake3 round 4, pareto) - STAGED, not submitted
Base: B3R4c (b4c, staged slot pos_b3r4c, untouched) = B3R4b 41b32afc (rejected, not_evaluable, finding F1-adaptive-finished-trail-conditioning / judge H4). b4b, b4c and their slots untouched. Run 10-15, all code under WSL nice -n 10.

## Result
P_success bound (program's own `bsrho.py --loss`, appA.py agrees): P_lower = 0.39000000000095 (margin 9.5e-13; B is the least multiple of 10^24 that reaches 0.39). It did NOT stay at the old batch count: the old batch count (B = 1.4323e36, Tp 68) gives only 0.3702 under the new bound (0.3793 with c = 13 L), so batches were added.
time_log2 = 125.06000 (raw 125.0599933561, certificate 2^12505999 * 846^100000 <= N^100000 < 2^12506000 * 846^100000) vs 125.02375 for B3R4b/c: +0.03625 bit.
Plan: Tp 67 (was 68), B = 1,457,780,783,501,000,000,000,000,000,000,000,000 (was 1.4323e36), c = 13 L (was 11 L), at most 1 cut trail (was 2), table 5,245 entries (was 5,251), N = 37512812019573143153979006568004192172275.
Memory: 1,048,506 B (<= 2^20), search phase leaves 70 B (was 10; item 4 done, no cost at 5 decimals), setup phase 1,042,104 B.

## Where the fix is
- Lemma text: `pkg/blake3/proof.md` Section 4 (lines 88-141): H2 (cut count only), Lemma 1 (unchanged), Lemma 2 with Steps 1-6 (lazy sampling with a DP lottery; usable collisions Y_t; Claim 1 usable collision is output; Claim 2 injectivity; Step 3 disturbance; Step 4 supermartingale M_t = exp(S_t/N' - (w-1)H_t) w^R 1[no usable collision]; Step 5 counting S from below + Chernoff; Step 6 sum). Source template `proof_t.md` (draft of Section 4: `sec4_new.md`).
- H1 clause (d) (adaptive hazard) with sensitivity: proof Section 5, claim.json heuristic H1 (statement/extrapolation/limitations), Section 8 premise list updated (H1 a-d, H2 cut count, H3). The old H2 (a)(c)(d) are gone (now proved for F).
- Note: `pkg/submission-note.md` (12.4 KB), section "Response to 41b32afc findings" names F1-adaptive-finished-trail-conditioning and H4 and all 9 material ids (rulecheck R21 passes).
- Code: `pkg/blake3/experiments/bsrho.py` (`_zq`, `_lossq`, `_b256`, `plan`, `loss`), `appA.py` (Appendix A copy); build `build_all.py`.

## What differs from the sketch in ANALYSIS.md (read this)
1. The sketched supermartingale (new point vs points of FINISHED trails) is what I first built, but its accounting loses ~22% of the pair count (open points plus the final window) and needed +0.18 bit (Tp 60, B +13%). The filed lemma uses a better predictable set: the usable set Y_t includes points of trails still open (their finish is known from the DP lottery, which is conditioned on, F values stay uniform inside their class), with the time and cut conditions in the definition, a bound on later disturbance (3.3e-3) and a penalty exponent w for unusable collisions. Cost vs old plan: +0.036 bit.
2. The old Lemma 2 (and B3R4/B3R3PV/0a9640ed text) ignored that a collision in the last batches cannot finish its trail before the halt (a point colliding with a long-tail trail needs that tail). The new count charges it (about 11% of the pairs). Monte Carlo of the bare process (my own C sim, /tmp, not in the package; L=64 and L=256, 40k/20k runs, old parameters) gives success 0.4228 / 0.4123, above 0.39, so the old claim was true but not proved; the new bound is a rigorous lower bound that is ~0.03 below that.
3. Also re-optimised (levers, all in the program): age cap c = 13 L (best of the kappa sweep), 1 cut allowed (-0.004 bit), Chernoff tail budgets 1e-3 each (-0.0025 bit).

## Checks
- bsrho.py --selftest: True. --ledger and appA.py agree (same N). --sweep run.
- Organizer intake (stage_run.sh, pareto_pipeline intake): {"intake":"passed"}, status mechanically_valid; organizer experiment outputs identical to b4c (checked trials equal), so stats/organizer summary unchanged.
- rulecheck (memgate): mem-gate PASS (30 stage peaks <= 2^20); 15 PASS, 4 N/A, 3 EXPOSED (R05 extrapolation, R07 iid-from-selected, R19 evidence-package: the same three as b4c; I removed the R12 and R21 hits my first draft had).
- prefile_check: all PASS except "experiment programs known-good" bsrho.py (same as b4c; intake passed).
- Experiment sources: bsrho.py 61,819 B + manifest 3,400 B = 65,219 B of 65,536 (limit 64 KiB): 317 B spare, no further additions possible.

## Not tested / limits
- The new Lemma 2 was written and checked by me only (every inequality direction re-derived once; no independent reviewer, no formal check, no brute-force of the lemma's steps at small scale). The Monte Carlo above checks only that the true success is above the bound, not the lemma. An independent read of Section 4 Steps 2-5 is the one thing worth doing before filing.
- Chernoff quantile for the trail sums uses numerical integration of the exponential model (relative error ~1e-7, declared as 1/L approximations).
- The judges' reading of H1 (d) and of the new Section 4 is untested; a second finding on it is possible.
- K (cut count) law stays an H2 premise.

## Slot / submit
Slot: WSL ~/hashsmash/yukon/pos_b3r4d/pareto (STAGED.sha256 22ba6d3f78a07eef4e65..., dependencies.json sha256 8cc8ddfef39f88fe2a691198634395a6a096ba78208e21b0cf1f815cddce1644; dependencies: 41b32afc first, then 75d5e1f9, 62cfd777, 0a9640ed, 3356413f, 6ae36351).
Submit script (NOT run): research/launch/submit_pareto_b3r4d.sh
