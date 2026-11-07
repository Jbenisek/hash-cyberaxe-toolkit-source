# VERDICT: the chunk-counter lever on the 55/63 path

Folder: research\newpaths\counter\adjudicate. Written 2026-10-08, about 15:10. Research only. No yukon, nothing filed,
posted or cancelled, trace untouched. Nothing was written outside this folder. The organizer verifier was imported
read-only, with bytecode writing off; its __pycache__ is unchanged since 2026-10-05.
Tags: COMPUTED = run here or in a named file. DERIVED = follows from a named source or a stated argument. GUESS = judgement.
My own checks: adj_check.py, output in adj_check.txt.

## Short answer

1. The lever is real. The counter by itself buys nothing. What gains is the per-trial counter: it lets E1.d1 be
   prescribed next to Y4, so trial condition T1 (c1 in the beta* cube) holds by construction. (COMPUTED by four
   agents and by me; details in section 1.)
2. Net value, same conventions as our filed entry (our counting machine, margin 2.0, success 0.39, no clusters):
   time_log2 84.96, against the filed 92.53. That is a gain of 7.6 bits, +-0.5 bit (1 sd, GUESS on how the parts
   combine). Against the same arrangement without clusters the gain is 9.8 bits. At the field's margin 1.4 the
   figure is 84.45. (DERIVED; ledger recomputed in adj_check.txt.)
3. The toy run (W = 8) confirms the mechanism end to end: 305 real full-hash collisions of complete messages, and
   the predicted gain realised at 0.94 +- 0.13 (-0.09 +- 0.20 bit). It cannot confirm the 32-bit size of the gain.
   (COMPUTED in toy\.)
4. New risk that no agent raised. Under the current organizer harness, no organizer-run experiment can show the
   counter half-collision. The 4 equal words sit in the last chunk's CV, and the final digest scrambles them. The
   filed package had exactly that organizer check, and the evaluability lane listed it as the tested scope beside
   H1. So a counter package is LESS
   evaluable on its exact part, while it is MORE evaluable on premises (it needs no H4-H6). (COMPUTED and DERIVED;
   section 3.)
5. Do not file. The path is set aside by CyberAxe, the organizers' evidence question is still open, and Grok
   job 32 (an independent 32-bit recheck) has not reported. Section 4 lists what a package would need.

## 1. Is the lever real? Yes

- Tree mode (COMPUTED). Take P = t full chunks. The organizer digest of P||X is a function of one value: the last
  chunk's CV, a compression with cv = IV, counter t (v12 = t mod 2^32, v13 = t >> 32), block length 55 or 63 and
  flags 3. Checks on the organizer verifier:
  - structure: 150/150 messages and 75/75 planted CV collisions for t = 1..1025, plus 4/4 at t = 2^32 + 5;
  - scout_recent: 360/360;
  - scout_cross: t = 1, 2, 3, 5.

  This is the standard mode; the profile puts out of scope only free-start or compression-only collisions and
  changes of the mode. The pair is two complete messages in the domain, so it is an ordinary collision. (DERIVED from
  target-profiles\blake3-r2-prefix-v1.json.)
- Freedom (COMPUTED by scout_recent with SAT, and by structure with its own exact peeling test, validated against
  brute force).
  - With t solved per trial (t = ROL(K0.d1,16) XOR K0.a1, "t absorbs w0"), Y4 + E1.d1 has a solving basis.
    With the counter fixed it does not.
  - The counter buys exactly one extra prescribed word: Y4 + E1.d1 + E3.h1 has no basis.
- Real 32-bit arithmetic (COMPUTED). In every trial, CV words 0, 2, 5 and 7 are equal, c1 is in the cube and
  beta = 18b0e098:
  - structure: 5,400 trials, plus 6 complete messages hashed by the organizer's blake3();
  - value: 3,000 trials against the real non-root compression (0 word mismatches), and 2^45.6 GPU trials;
  - adjudicator: the two t = 1 pairs of structure\e2e_t1.txt (1079 / 1087 bytes), recomputed on
    verifier/blake3.py. CV words 0, 2, 5 and 7 are equal with counter 1 and flags 3. The same blocks as root blocks
    (counter 0, flags 11) agree on 0 of 4 words, so the counter is essential to the pair.
- Toy end to end (COMPUTED, toy\TOY_RESULT.txt). At W = 8, all 372 collisions were rebuilt as complete messages and
  confirmed by two independent tree hashes: 305 counter, 67 filed.

  | arrangement | found | predicted | trials per collision |
  |---|---|---|---|
  | filed | 67 | 64.0 | 8.8e8 |
  | counter, d1 forced into the heaviest beta | 251 | 255.0 | 8.1e7 |
  | control: counter, d1 not forced | 54 | 47.8 | same rate as filed |

- The two scouts do not conflict (DERIVED; the toy control settles it). scout_cross measured a CONSTANT counter,
  which only relabels trials: no gain, and t = 0 is best for the filed cluster design. scout_recent's lever SOLVES
  t per trial. In that arrangement X2 and Y4 are outer-step words and t_hi = 0, so the X2 co-pass and x30/x31
  effects do not enter.

## 2. Net value

### What each report said, and how I reconcile it

| item | structure | value | toy | adjudicated |
|---|---|---|---|---|
| rate factor of a trial | 748x (DERIVED) | 747.92 = 2^9.547 (DERIVED) | 905x quoted, not re-derived | 747.92 = 2^9.547. Sol answer Y re-sums the 7 exact rows to 67,698,688 and PROVES that conditioning on the cube does not bias E3 under model M. "905x" is the whole-class figure (904.92); the sub-class one is the one usable with rule A. (DERIVED) |
| cost per trial | 3.4 ops, a GUESS inferred from the board | 6.5 vs 7.7 on our filed machine, lane-checked 2100/2100 (COMPUTED) | 45x in lines, does not transfer | x0.844 = -0.244 bit on our machine. I checked that count_ctr.py's parts add to stage A 41 and stage 2 72. (COMPUTED) |
| baseline | board 93.0 (margin 1.4, no clusters, lighter machine) | our filed 92.53 (margin 2.0, clusters 2.22 bits) | toy filed arrangement | both shown below |
| net gain | +9.3 +- 1.5 | +7.57 +- 0.4 | +8 +- 3 | **+7.6 +- 0.5 vs our 92.53; +9.8 vs the same arrangement without clusters** |

The three reports differ only in baseline and cost convention, not in substance. My recomputation uses one formula,
T = log2(0.5) + 128 - log2(C/margin) + log2(ops/430) + 0.02 (adj_check.txt, COMPUTED):

| case | time_log2 |
|---|---|
| filed 92.53 (clusters, margin 2.0) | 92.53 |
| filed arrangement, no clusters, 7.7 ops | 94.75 |
| **counter, our machine 6.5 ops, margin 2.0** | **84.96** |
| counter, our machine, margin 1.4 (field's margin) | 84.45 |
| counter, no cost gain at all (7.7 ops), margin 2.0 | 85.20 |
| board leaders (93.02 / 93.05) imply 3.36 / 3.42 ops per trial at margin 1.4 | 93.02-93.05 |
| counter on the board's lighter machine (scaled by our 6.5/7.7 ratio), margin 1.4 | 83.25 |

### Uncertainty

- Rate factor: exact under model M, and model M is shared with the filed figure. The part that is not shared is
  whether the new sampler realises the conditional law (Sol: OPEN). The proxies say it does:
  - E1 outcome real vs exact: -0.8% +- 0.8% (GPU 2^45.6);
  - E1 outcome AND rule A: 55 vs 59.6;
  - toy realised fraction: -0.09 +- 0.20 bit.

  GUESS: +-0.3 bit for the joint event no experiment reaches (2^-91).
- Cost: +-0.1 bit. Even with no cost gain the result is 85.20.
- Clustering inside an outer step: Sol PROVES Var/E <= 1 + 2^-13 under a fresh-inner extension; the physical
  sampler is OPEN. Value DERIVED a clump size of about 1. Effect on the success bound: negligible (GUESS).
- Total for the gain: +-0.5 bit (1 sd, GUESS on how the parts combine). Model M itself is not included; it is the
  same risk the filed 92.53 already carries.
- Upside not counted: clusters rebuilt on the new inner loop. Value measures rule A carried at 0.81-0.95 per flipped
  c1 bit and GUESSES 2-3 bits, but clusters bring back H4-H6-type premises. Not recommended now. A better beta does
  not exist: Sol DERIVES that beta* is first among all 53 betas and that no union of two betas beats it.

## 3. Risks

### 3a. Message size (DERIVED; GUESS on the judge)

- t comes out of the solve and is about uniform below 2^32 (structure, tdist.py). A found pair has about 2^31
  chunks: about 2 TiB on average, at most about 4 TiB (2^42 bytes).
- That is inside the domain (below 2^64 bits; the verifier accepts below 2^61 bytes).
- Verifying the pair costs about 2^36 compressions: negligible in the cost model, but no judge or harness can run it.
- Small t cannot be bought: t = 1 occurs at about 2^-32 per trial.
- v13 = 0 throughout. Trials with t = 0 (probability 2^-32) must be skipped, because they would be root
  compressions with flags 11.

### 3b. Judge reaction (GUESS)

- An AI judge may read "one non-root compression collides" as a compression-only collision, which is out of scope.
  The defence is the tree lemma, which is short and exact, plus the organizer's own code lines. Risk: low to
  moderate.
- A 2-TiB message may draw a "practicality" remark. The profile allows it.
- A jump from about 93 to about 85 will draw closer scrutiny.

### 3c. The organizers' evaluability problem. Which premises would remain internal-state rates?

1. **NEW, and missed by the value report.** The exact half-collision becomes internal. The organizer harness checks
   only digest events: full-collision or digest-xor-mask
   (hash-smash\docs\HEURISTIC_EXPERIMENTS.md; experiments\runner.py).
   - Its message cap is 4096 bytes by default, and an organizer may raise it to 65,536 at most
     (runner.py line 55 and line 65). So t <= 3 by default, t <= 63 at most.
   - Even at t = 1 the final digests of a counter pair do NOT agree on the half mask. COMPUTED on the two real pairs
     in adj_check.txt: "equal on the half mask: False". DERIVED: the root is a parent compression over
     (CV_P, CV_t), and 2 rounds scramble it.
   - So no organizer-run experiment can show the counter half-collision. In 64c075ac the evaluability lane's
     tested scope for H1 reads: "The organizer verified the exact 128-bit half-collision and a toy extra-byte
     residual event, not H1" (dossiers\64c075ac\judge-dossier.json). A counter package loses that support. It would rest on a proof plus a participant self-test,
     which is untrusted.
   - GUESS: a material evaluability finding is likely (about 50%); whether it blocks is unknown. Options: keep
     pkg10's root-arrangement experiment as evidence for the shared G-level construction (a different instance:
     counter 0, flags 11, Y4 innermost), and put the counter construction's code and derivation in proof.md, cited
     by line. That is the route the organizers endorsed.
2. **H1'** (score-critical): R = 0 and rule A at least half of 2^11 x 67,698,688 x 2^-128 per trial, with no extra
   clustering. The event itself is a full collision. Its conditioning (c1 forced into the cube) and every
   measurable proxy are internal. It is the same kind as the filed H1, which all four lanes rated plausible.
3. **H2'** (E1 test passes below budget) and **H3'** (stage-2 entries within 1/32): internal-word rates of the
   same kind as the filed H2 and H3, which were rated plausible with no organizer experiment.
4. **No H4-H6.** These were the only blockers of 64c075ac (aggregate.json reasons). That is the counter package's
   gain in evaluability.

Net (GUESS): the premise list is shorter and of a kind already rated plausible. But the exact part loses its only
organizer-run check. The organizers said (HANDOFF 2026-10-08) that the harness has no mechanism for internal-state
conditions and that a human is looking at an extension. A counter package depends on that answer at least as much
as pkg10 does.

### 3d. Other risks

- Model M and the completeness of the old beta enumeration are shared premises. Sol reconciled the records; it did
  not recount them from scratch (DERIVED from sol_answer_Y_counter.md section 6).
- This is the 55/63 path again, not a new path. It counts once under the "many paths" goal (GUESS on how the owner
  weighs it).

## 4. What a package would need before filing (none of it to be filed without the owner's explicit go)

1. The owner reopens the 55/63 path, which is set aside pending the organizers. Ask the organizers, once, how an
   exact CV-level half-collision of a non-root chunk can be evidenced, since a digest event cannot see it. Ask too
   whether a pair of about 2^41 bytes is acceptable as an ordinary collision.
2. Wait for Grok job 32, the independent 32-bit recheck (work\job32_counter, not finished at 14:57). Sol Y is in:
   it confirms 67,698,688, the factor 747.92 and beta* optimal, and leaves two items OPEN: the physical-sampler
   transfer and the per-outer-step second moment.
3. A program (copy halfsearch.py, change in small steps):
   - the order of value\cone4_E1b1_B10.txt (5 equations per trial);
   - the run-wide RT table of ROL(d1,16) over the 2^21 cube members;
   - stage A at 41 and stage 2 at 72 on the filed machine;
   - budgets and halting rules, the t != 0 check, v13 = 0;
   - a self-test that rebuilds complete messages for small t and checks them against the organizer's tree.

   Experiment sources must stay within 64 KiB in total.
4. proof.md:
   - the tree lemma, with the verifier lines;
   - the construction (proof.md section 4 with K0.a1 left to the trial, K3 flags 3, K1 v13);
   - the 7-row ledger and Sol's conditioning theorem;
   - the marginal-law argument (outer offsets uniform, so each trial has the conditional M law);
   - the clumping bound;
   - the cost table;
   - the GPU proxy table;
   - the toy end-to-end result.

   Put the counting programs, or tight pseudocode, in proof.md and cite them by line (F-EVAL-02 was raised on every
   entry so far).
5. claim.json:
   - new restrictions, each at most 1,024 characters: lengths 1024t + 55 and 1024t + 63, 1 <= t < 2^32, a non-root
     last chunk with flags 3;
   - memory_log2_bytes at least 42 to cover the output (free in the score);
   - heuristics H1'-H3' only;
   - a margin chosen by CyberAxe: 2.0 gives 84.96, the field's 1.4 gives 84.45 (count as written; disclose).
6. Before any submit: a backup with a label, HANDOFF and MASTER_PLAN entries, and the owner's yes for that specific
   submit, with the stated confidence and the unrun checks (the joint event at 32 bits; organizer evidence of the
   half-collision).

## 5. Files (this folder)

- adj_check.py: the organizer-verifier recheck of two t = 1 pairs, and the one-formula ledger.
- adj_check.txt: its output.
- VERDICT.md: this file.

Sources read: counter\structure\STRUCTURE.md, counter\value\VALUE.md (with analyze_gpu.txt, count_ctr.py,
value_calc_out.txt), counter\toy\TOY_RESULT.txt (with summary.txt, verify_hits.txt), scout_recent\SCOUT_RECENT.md,
scout_cross\SCOUT_CROSS.md, research\sol_answer_Y_counter.md, dossiers\64c075ac, pkg10 manifest and claim,
hash-smash docs, runner.py and the target profile, and the HANDOFF newest bullets.
