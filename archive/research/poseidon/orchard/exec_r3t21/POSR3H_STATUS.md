# POSR3H status (named-fix refile of POSR3G / 4086e210) - 2026-10-15

Built and staged, NOT submitted. No new counted run (cache data/cache/df73de6b3e04d72b/); numbers identical: N = 317,054,280,703, time_log2 30.08182, memory 250,386,180 B (2^27.900), collision centre 1.

## Changes (text only)
- build_package.py: new plan_size() mirrors plan3_for_len (ntt.c); POWN/POWNP computed from 2m-1 and m+1 and asserted equal to the stage-C buffers (2*2^AEXP, 2^AEXP). claim.json H1 scope now: "m = 976562; powering transforms (stages C and D, chosen by plan3_for_len) N = 2097152 (2^21) and N' = 1048576 (2^20) at the top; line interpolation (stage B): 3145728 evaluations of the line (2H) and one inverse transform of size H = 1572864 (3 * 2^19)". All from PAR/plan variables, nothing hard-coded.
- proof_template_exec.md: new Section 1 bullet "One finite regime" (powering N, N' vs line H, 2H; ledger N is a count); Section 3 and the stage B row name the line sizes and point to the powering sizes; Section 4.3 sentence computed from the plan (no hard-coded r=3 numbers) and names the line sizes separately.
- F2-historical-time-memory-scalar: proof L10 now says the normalized scalar is log2(time) = 30.08182, memory stated separately, 37.98182 = time + memory penalty (bookkeeping, not normalized cost). Note "Numbers" paragraph likewise. (Proof L180 itself already said only "memory penalty 7.900"; no 37.98182 there.)
- EXP-001: replay line of the proof pins: gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0 (read from the .comment section of the counted executable), Linux 6.18.40.1-microsoft-standard-WSL2, Ubuntu 26.04 LTS under WSL2, AMD Ryzen 9 7900X. Source: logs/env_pin.txt. Limit: the run logs did not record the environment; kernel and CPU were queried on the same machine after the run (said so in the text). The compiler is certain (binary .comment).
- Note: "Response to 4086e210 findings" paragraph names F1-h1-dimension-scope-conflict, F1-h1-dimension-mismatch, F2-no-organizer-execution, F1-self-reported-execution-artifacts, EXP-001, F2-inert-reviewer-directions, F2-historical-time-memory-scalar. Note is 15,481 B (>= 5 KiB), ASCII.
- Left alone on purpose: the AMAX comment in the shipped source (proof appendix, "3 * 2^20 = 3145728 >= 1953123") is a source comment on the chooser's upper bound, not a regime claim; editing it would make the proof's source differ from the counted run.

## Checks
- claim.json scope numbers 2097152, 1048576, 3145728, 1572864 all appear in proof.md (3, 3, 5, 4 times). Old vs new proof differ in 11 diff lines, all prose.
- prefile: ALL PASS. rulecheck: mem-gate PASS (13 stage peaks <= 2^27.9), mem-includes-prep PASS; 3 EXPOSED (R03/R05/R12) are the same wording hits as POSR3G/POSR3F (read before, unchanged text in the source/ledger).
- pareto_candidate.py rc=0, state ready, package_sha256 c35725d6...46215.

## Staging
- New slot /root/hashsmash/yukon/pos_posr3h (base pos_posr3g copied, not modified), staged by slotstage_pareto.sh POSR3H poseidon 3 pkg_stage_exec_fix submission-note_exec.md pos_posr3g. STAGED.sha256 head 11b527572966a4b4. dependencies.json (POSR3F 3b99dfad) copied into pareto/, sha256 dd6f3227...a27f9a (unchanged).
- research/launch/submit_pareto_posr3h.sh written from submit_pareto_posr3g.sh (staged-files guard, deps guard, --dependencies-file). NOT RUN. Needs the owner's go. Also generated: research/launch/slotstage/out/submit_POSR3H.sh (no deps flag; do not use).

## Open point: do POSR4M/POSR5M use a rows==2 plan?  NO
exec_r4mt and exec_r5mt ntt.c plan3_for_len (L510) only returns make_plan(3, a), i.e. 3*2^a; no rows==2 plan exists there. Every product length (powering 2m-1, m+1, Newton l2+l-1, hgcd nres/Lmax, split 2n-1) goes through that chooser. Their claim scopes (r4: N = 12582912, N' = 6291456, 12582912 evaluations; r5: 50331648, 25165824, 50331648) equal both the line sizes (2H, H) and the powering sizes (smallest 3*2^a >= 2m-1: 3*2^22 and 3*2^24; >= m+1: 3*2^21 and 3*2^23), and the proof text says "N = 3 * 2^a >= 2m - 1, N' = 3 * 2^b >= m + 1". So no F1-type conflict. Residual wording risk only: their scope labels H as "N' in its transforms" although it is the line size; it coincides with the powering N' here.
