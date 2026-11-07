# b3-mode-edge: the {m2,m3,m4,m6} internal-block local collision, stage by stage

Scout result, 2026-10-10. Clock read 01:49 at the start; the last run ended at 03:16. This is our team's
research only: nothing was filed or submitted. I ran no yukon commands, used no network, and never opened
`.key`. One process ran at a time. The RTX 3090 (WSL) ran every 2^32 scan, and the host CPU ran the small DFS
and DP solvers.

No tool call was refused or stopped by the system. I stopped two of my own runs by PID: the first `d3ab` run
(an unbounded sampling loop, rerun with a cap) and the full structured-K3 run (it would have passed 20 minutes,
rerun on every 11th pattern).

Files read:
- `b3-mode/RESULT.md`, `k3_scan.c`, `k3_general.c`, `k3_rescan_*.out`, `k3_general_*.out`
- `BLAKE3_2ROUND_MAP.md` (header and sections 1, 3, 5, 6)
- `hash-smash/verifier/blake3.py`
- `target-profiles/blake3-r2-prefix-v1.json`
- `sol_answer_D4_local.md`

Labels: COMPUTED (I ran it; exact unless a sample size is given), DERIVED (arithmetic on computed numbers),
GUESS.

## Verdict: dead at h = IV

1. **K2 is solvable for exactly 1,270 of the 2^32 differences dw4 at h = IV.** The enumeration covered every x4
   and every dw4 at once (COMPUTED). All 1,270 are period-4 signed-digit shapes, for example `88877788` and
   `ef1110ef`. The set is closed under negation. At two random chaining values it has 922 and 1,108 elements, so
   the mode lever does not enlarge it (COMPUTED).
2. **The C3 link dw4 = -dS3 therefore needs K3's a-difference to land in a set of density 2^-21.69.**
   - K3 itself is easy: 3,048 solvable dx6 in 6 minutes, with 25,167 distinct dS3.
   - None of the 25,167 lands in -S2.
   - At the larger joint-pass level, 0 of 816,790,917 joint-pass dA values land in -S2, where 241.5 were expected
     if the hit rate were uniform. That bounds the rate below 2^-28.0 (95%), at least 6.3 bits under uniform
     (COMPUTED).
   - K3 has no joint pass at all for period-4 dx6: 0 in 1,004 x 2^32 pairs (COMPUTED).
3. **P(K2) x P(K1) is far below the build gate of 2^-6.** It is about 2^-21.69 x 2^-2.09 = 2^-23.8 (DERIVED), so
   no pair was built at h = IV.
4. **Forcing K2 to hold does not save the downstream stages.** In synthetic chains (a real K2 root, with dS3 set
   to -dw4):
   - K1: 212/900.
   - D3: 1 of 212 K1-solved chains.
   - D1: conditions (i) and (ii) held in 4 of 74 chains.
   - C0: 0 of 3,110,352 candidates.
   - Complete chains: 0 of 900.
5. **Cost.** Even granting C0 = 1 and a uniform C3 hit rate, the price is at least 2^63.5 units, above 62.7934
   (DERIVED, section 5). If the measured joint-level C3 bound applies to solutions too, it is at least 2^69.9.

**Root cause.** The rotations 16, 12 and 8 preserve residues mod 4, and K2's two equalities hold only on
period-4 difference shapes.

K3 lives off them:
- Its joint test never passed on a period-4 dx6.
- On the dx6 where it does pass (screened with dx6 = 2 mod 4, as wave 1 observed), no dA was period-4.

Five places join the two worlds, and each is a carry-compatibility test between a period-4 XOR pattern and an
unstructured modular difference. The measured rates are:

| junction | measured rate |
|---|---|
| C3 link | < 2^-28 per joint pass |
| K1 coupling | 2^-2.1 |
| D3 | 2^-7.7 |
| D1 | 2^-4.2 |
| C0 | 0 of 3.1M |

## 1. The route (re-derived; it matches wave 1)

At a chunk block the state is v0..7 = h, v8..11 = IV0..3, v12 = t_lo, v13 = t_hi, v14 = 64 and v15 = flags.
Side B minus side A is written d (mod 2^32).

| call | inputs | message difference | wanted |
|---|---|---|---|
| K1 = G(h1,h5,IV1,t_hi; m2,m3) | equal | dm2 = -dm6 (from C0), dm3 = dw3 | S5, S13 equal |
| K2 = G(h2,h6,IV2,64; m4,m5) | equal | dm4 = -dS3 (from C3) | S2, S10 equal |
| K3 = G(h3,h7,IV3,fl; m6,m7) | equal | dm6 = dx (free) | S7, S15 equal |
| D0, D2 | no difference | none | automatic |
| D1 = G(S1,S6,S11,S12; m10,m11) | a, b, c differ | none | X6, X11 equal (S12, m10, m11 free) |
| D3 = G(S3,S4,S9,S14; m14,m15) | a, c, d differ | none | X4, X9, X14 equal (a1 and a2 free) |
| C0 = G(X0,X4,X8,X12; m2,m6) | d differs | dm2 + dm6 = 0 | compat(dm2, dX12-xor), X0 via m9 |
| C1 = G(X1,X5,X9,X13; m3,m10) | a differs | dm3 | dS1 + dS6 + dw3 = 0 (coupling ii) |
| C3 = G(X3,X7,X11,X15; m4,m13) | a differs | dm4 | dm4 = -dS3 |
| C2, E0..E3 | no difference | none | automatic |

Exact stage forms (each re-run on the real G):

- **K2.** Condition 1 is H(a1) = H(a1 + dw4), with H(u) = u + ror12(h6 ^ (IV2 + ror16(64 ^ u))). Condition 2 is
  compat(d1 - d1', ror8(d1 ^ d1')), and y5 is then any point of a carry cube. So the solvable dw4 are the
  differences of H-collision pairs that pass condition 2. A bucketed sort of all 2^32 H values gives every root.
- **K1.** The b2 test compat(dc, B) depends on x2 alone. The d2 condition fixes dS1 = (z ^ D) - z through z = a2,
  and coupling (ii) turns into 2·dS1 = dA - dS6. dS6 ranges over the values reachable in K2's y-cube, up to 1,024
  sampled per root.
- **D3.** Its d1 difference is Dd1 = ror8(A) ^ ror16(B), where A is K2's XOR pattern and B is any pattern of adding
  dS3. The stage needs compat(dS3, Dd1) (condition A, through m15) and compat(-dS9, Dd1) (condition B). It also
  needs S14 to stay inside K2's d2-cube while keeping the matched dS6 (a carry DP). The scan is exact over all
  2^32 a1.
- **D1.**
  - Condition (i): (S11 + d1) ^ (S11' + (d1 ^ Dd1)) = S6 ^ S6', checked over all 2^32 a1 with a 4-state DP, d1
    free through S12.
  - Condition (ii): ror8(d1' ^ (a2 + δ)) - ror8(d1 ^ a2) = c1 - c1', with a carry DFS that guesses the carry at
    bit 8.
  - C0: compat(-dx6, d2 ^ d2').

Self-tests (COMPUTED, selftest.out): 200,000 planted solutions each for the d1, a2, condition-A and condition-A∧B
solvers, with 0 misses and 0 wrong answers. The condition-A and A∧B DPs matched a GPU brute force over all 2^32
values in 40/40 and 40/40 cases.

## 2. Per-stage table (h = IV, flags 1 for K3)

| stage | measurement | number | label |
|---|---|---|---|
| K3 screen | joint pass per random (dx6, x6), ctz(dx6) = 1 | 14,188 in 2^40 = 2^-26.21 | COMPUTED |
| K3 rescan | screened dx6 with a verified solution | 3,048 / 6,000 | COMPUTED |
| K3 | distinct dS3 per solvable dx6 | 25,321 / 3,048 = 8.31 | COMPUTED |
| K3, period-4 dx6 | joint passes, 1,004 patterns in 4 classes (6-8 digits; every 11th pattern) | 0 in 2^41.97 pairs (about 55,000 expected at the random rate); a stopped run added 500 class-0 patterns, also 0 | COMPUTED |
| K2 | solvable dw4 (exhaustive) | 1,270 of 2^32 = 2^-21.69 | COMPUTED |
| K2 | roots: total; per solvable dw4 | 570,922,486; from 4 to 65,975,348 | COMPUTED |
| K2, other h | solvable dw4 at two random (h2, h6) | 922; 1,108 | COMPUTED |
| C3 link, solutions | K3 solution dS3 with -dS3 in S2 | 0 / 25,167 (0.0074 expected if uniform) | COMPUTED |
| C3 link, joint passes | joint-pass dA with -dA in S2 (5,000 rescans) | 0 / 816,790,917 (241.5 expected if uniform); rate < 2^-28.0 | COMPUTED |
| K2 roots for D3 | (dw4, A) patterns with D3 condition A possible | 64,572 / 891,196; 390 of 1,270 dw4 | COMPUTED |
| D3 A∧B | per (feasible pattern, K1 dS9) | 2,966 / 100,000 = 2^-5.08 | COMPUTED |
| K1 | coupled K1 solvable per (dx6, K2 root) | 212 / 900 = 2^-2.09 | COMPUTED |
| D3 | exact over 2^32 a1, up to 64 K1 solutions per chain | 1 / 212 K1-solved chains = 2^-7.73 | COMPUTED |
| D1 (i) | exact over 2^32 a1 (first K1 solution) | 17 / 74 | COMPUTED |
| D1 (ii) | given (i), capped enumeration | 4 / 17 | COMPUTED |
| C0 | given D1 | 0 / 3,110,352 candidates (4 chains) | COMPUTED |
| complete chain | K1, D3, D1 and C0 together | 0 / 900 | COMPUTED |

The scan counts asked for (about 2^7 per stage) were exceeded:
- K2 was run for all 2^32 differences at once.
- K1 ran 900 full 2^32 scans.
- D3 ran 7,978 exact 2^32 scans.
- D1 (i) ran 74 exact 2^32 scans.

## 3. What K2's solvable set looks like

The largest root counts are on the dw4 values below (`s2check_iv.out`; 4,000/4,000 random entries re-verified on
the real G):

| dw4 | negation | roots |
|---|---|---|
| ef1110ef | 10eeef11 | 65,975,348 |
| 88888878 | 77777788 | 43,237,974 |
| e221de22 | 1dde21de | 40,977,024 |
| 88877788 | 77788878 | 19,654,648 |

Each is a signed-digit sum on one residue class of bit positions mod 4 (plus carries). This happens because
condition 1 needs the b1 difference (ror12 of ror16 of the a1 difference) to cancel the a1 difference, and
condition 2 needs ror8 of the d1 pattern to match the d1 difference. Both hold only on (near) period-4 patterns.
P(K2) is therefore not the 2^-14 a random compat would suggest: it is 0 off this set and large on it.

## 4. The C3 link, measured at the joint-pass level

`k3hit_f1.out` screened 2^40 random (dx6, x6) pairs at h = IV (a new seed). It then rescanned 5,000 dx6 and
tested every joint-pass x for -dA in S2 on the GPU:

- **Joint passes:** 816,790,917.
- **Hits:** 0, where 241.5 were expected if dA were uniform. A Poisson(241.5) gives 0 with probability about
  e^-241.
- **Upper bound (COMPUTED):** P(-dA in S2 | joint pass) < 3/816.8M = 2^-28.02 at 95%, at least 6.3 bits below
  uniform.

So the K3 dA values avoid the period-4 set rather than meeting it at random.

The exclusion is not a simple congruence (`residues.py`, COMPUTED):
- Every K3 dS3 is odd, and 672 of the 1,270 values in -S2 are odd.
- Modulo 2^12, 4.9% of the K3 mass sits on residues that -S2 also uses.

I have no proof of the exclusion; it is a measurement. The 2^-21.69 used in section 5 is the optimistic value.

## 5. Cost (DERIVED)

**K3, per distinct dS3:**
- Screening costs 2^26.21 trials x about 40 word operations = 2^22.78 units per candidate dx6.
- A full rescan costs 2^32 x about 30 operations = 2^28.16 units.
- Dividing by the solvable fraction 0.508 and by 8.31 distinct dS3 gives 2^26.11 units per distinct dS3.

**Per complete chain (optimistic):** 2^26.11 x 2^21.69 (C3, uniform GUESS) x 2^1.70 (a D3-A feasible root
exists) x 2^2.09 (K1) x 2^7.73 (D3) x 2^4.21 (D1) = **2^63.53 units, with C0 = 1 assumed**. That is above
62.7934.

| assumption changed | cost |
|---|---|
| measured joint-level C3 bound (2^-28.02) in place of uniform | at least 2^69.9 |
| a carry-DP K3 solver that removes the rescan (not built; it would leave 2^22.78 / 0.508 per combo) | 2^58.1 x 1/P(C0) |

C0 held for 0 of 3.1 million D1 candidates, and the C3 link is below uniform, so neither lever closes the gap.

## 6. Is {m2,m3,m4,m6} the D4 pattern?

It lies inside D4's no-metadata one-pin arm, but it is not the D4 sampler that was measured.

1. In `sol_answer_D4_local.md` (sections 7, 10, 11), that arm keeps J = {1,5,8,9,11,12,14,15} and m0 common and
   lets {m2,m3,m4,m6,m7,m10,m13} differ. {m2,m3,m4,m6} is the corner with m7, m10 and m13 also common
   (d10 = d13 = 0).
2. D4's own automatic-residual lemma (section 10) then makes three of its four round-1 residuals automatic:
   - D4's D1 has m10 common and S7 equal (from K3).
   - D4's D2 has m0 common and S4 equal (K0).
   - D4's D3 has m13 common and S5 equal (from K1).
3. Only D4's D0 remains, and that is our C0, because its y-word m6 differs.
4. The price of that corner is the column-output equalities in K1, K2 and K3. They make round-0 diagonals T0 and T2
   difference-free, so only T1 (our D1) and T3 (our D3) need cycles.
5. D4's identity collapse (section 10) needs m0, m4 and m6 common, so it does not apply here; every candidate is
   distinct because dm6 ≠ 0.
6. D4's measured rates (2^-15.9 per diagonal, 0 joint in 8M) came from its random section-7 sampler with all four
   diagonals active. They do not transfer, and this report replaces them for this corner.

## 7. Limits (not tested)

- K3 was run with flags 1 only, not 11 or 3. K2, K1, D1 and D3 do not depend on the flags.
- Not every root of a forced dw4 was tried for K1, D3 and D1, and not every K1 solution was tried for D1. D1 was
  tested on the first K1 solution per chain, with caps of 2^20 a1 x 64 d1 x 64 a2. This freedom could add a few
  bits per link. It cannot touch the C3 link.
- No carry-DP solver for K3 was written; the rescan is brute force on the GPU.
- No pair was built: the gate failed. No free-start validation pair could be built either, because no synthetic
  chain passed C0.
- {m0,m2,m4,m6,m7} (the other 3-condition route in wave 1) was not examined.

## 8. Next test (for whoever continues)

Apply the same exhaustive "solvable-difference set" enumeration to each forced stage of {m0,m2,m4,m6,m7} before
any chain work: one s2enum-style run per forced G, about 10 s each. A route is worth chaining only if the forced
stages' solvable sets share one rotation class. Here they do not: K2 is period-4 and K3 is not.

## Files

Code:
- `kpipe.cu`: GPU scanners and the exact solvers. Modes: k3find, s2enum, s2check, s2pat, k2scan, chain, d3ab,
  k3hit, k3struct, selftest, k3t, freestart.
- `build.sh`, `run.sh`, `run_k3big.sh`, `run_k3hit.sh`, `run_k3struct.sh`, `run_s2h.sh`, `env_check.sh`,
  `ps_mine.sh`, `stop_pid.sh`
- `verify_pair.py`: reference check for a built pair (unused, since no pair was built).
- `residues.py`: low-bit residue comparison of K3 dS3 against -S2.

Data:
- `s2_iv.bin`: (dw4, roots, first x4) for all 1,270 dw4.
- `s2pat_iv.bin`: (dw4, A, roots, x4) for all 891,196 patterns.
- `s2_hA.bin`, `s2_hB.bin`
- `k3sol_f1.txt`: 25,321 K3 representatives.
- `k3hit_f1.txt`: joint-pass hits (empty).

Outputs: `s2enum_*.out`, `s2check_iv.out`, `s2pat_iv.out`, `k3big_f1.out`, `k3hit_f1.out`, `k3struct_*.out`,
`d3ab_iv.out`, `chain_*.out` / `chain_*.log`, `selftest*.out`, `k2scan_test.out`, `k3find_test.out`.
