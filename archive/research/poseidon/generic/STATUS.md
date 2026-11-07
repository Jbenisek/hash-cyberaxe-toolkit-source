# Poseidon generic birthday entry at the maximum round count (10-15)

Admission (allbench.sh, 10-15 17:08Z): hashsmash-pareto/poseidon status open, rounds 3..56 (56 = every partial round). The track's "round" r is the number of PARTIAL rounds (profile text: "plus eight fixed full rounds"); r = 56 is the complete Orchard hash (rounds 0-3, partial 4-59, 60-63). C(56) = 216 + 21*56 = 1392 (contract reference_operation_costs). Nominal reference in the contract: 127.0 (not a baseline). Ranking: most rounds first, then normalized time-memory.

## Q1 Contract
Input two canonical field elements (32-byte LE each, < p); initial state [nk, rho, 2^65]; digest = state[0], whole element compared. One reference permutation call = 1 unit, other word op = 1/1392; memory term = max(0, log2 bytes - 20).

## Q2 Generic collision entry (BUILT)
Walk F(x) = digest(x, 0) on field elements: the output is itself a canonical input, so no injective map or conversion is needed. One trail, DP density 27554/2^128 (2^-113.25), table 2^14 DPs x 48 B (786,528 B; total 815,104 B < 1 MiB), merge point recovered from stored points (single trail needs no extra factor: expected work stays ~ sqrt(pi N/2), the budget for success 0.39 is 0.994 sqrt(N)). Lemma 2 proved for a random function by exact lazy sampling: P(no repeat in n steps) = prod(1-(i+1)/N); explicit eps terms (detection e^-8 + n d/N, gaps, table) = 1.12e-3; bound 0.3900000006. Budget: n = 1.6948e38 (2^126.9944) + d 9.9e34 + recovery 3*gmax 6.7e35 + 7 other ops/step. T = 1.711e38 units: **time_log2 = 127.0082, claimed 127.009**, memory 2^20 (floor), score about 127.009. 0.009 above the nominal 127; the overhead is the 7 loop ops per step (0.007 bit) plus tails (0.002 bit).
Not tested / limits: no collision exists to show (2^127); H1 (real F behaves like a random function) is declared, not provable. Recovery was simplified to 3*gmax evaluations (first stored DP before the merge, no binary search); correctness is proved in proof.md Section 3 and exercised by experiments (pairs verified against the organizer digest at r=56).

## Q3 Package (BUILT, STAGED, NOT SUBMITTED)
- Package: research/poseidon/generic/pkg (claim.json, proof.md 10.4 KB, experiments/rho.py 22.4 KB + manifest, empty certificate manifest). Sources of the parts: build_rho.py (joins constants_own.py + core_rho.py -> rho.py), make_manifests.py (claim + manifests), note.md (submission note), chk_exp.py (emulates the organizer runner: runs both experiments with 256 trials and checks every pair with the organizer's verifier digest).
- Checks run: rho.py digest == verifier/poseidon.py digest at r=56 (4 inputs) and == our own implementation at 64 rounds; experiments through chk_exp.py: rho-n14 232/256 pairs, proj-w254 222/256 pairs, all pairs distinct and verified by the organizer digest; run time 0.6 s and 2.4 s (limit 20 s each). Organizer's pareto_candidate.py --family poseidon --rounds 56: state ready, rc 0.
- Staged slot: WSL ~/hashsmash/yukon/pos_posgen (base pos_posr5m). Submit script written, NOT run: research/launch/submit_pareto_posgen.sh (copy of slotstage/out/submit_POSGEN.sh; refuses if staged files changed; appends one FILINGS.md line). Needs the owner's go; re-read `yukon benchmark show` admission first.
- Not run: the real organizer sandbox (Docker) for the experiments, export_review_packet critique, prefile_check of our own. Judge risks: (1) "1 unit per reference call + 7 ops" machine convention (H2), (2) H1 premise, (3) a rival with a smaller loop overhead.

## Levers / next
1. Lower the per-step overhead: expand the permutation instead of the unit call and use the constant second input (round 0 on one lane, last round row 0 only: -30 of 1392 ops = -0.031 bit) but then loads/code must be charged with immediates, a convention the judges have not ruled on (Poseidon rulings charged loads) - not in this package.
2. Table up to ~21k entries (still < 1 MiB) lowers d and gmax terms (~0.003 bit).
3. At lower rounds an algebraic entry is cheaper but ranks below (rounds first): this entry sits alone at the top of the rounds order until someone files r56 lower.

## 10-15 update: 98b1c2c4 fix
Rejected at intake because the organizer runner calls digest(b"") for python experiments (Poseidon refuses it). pkg2 declares no experiments, program printed in proof Appendix B; staged slot pos_posgen2, submit_pareto_posgen2.sh written, NOT run. See FIX_98b1c2c4.md.
