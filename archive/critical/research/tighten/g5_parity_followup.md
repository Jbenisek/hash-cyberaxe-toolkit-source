# G5 route: can the parity-compatible K0 record be chosen? (2026-10-11, follow-up to g5_y_result.md)

Preregistration: `prereg_g5_parity.md` (written 21:59 to 22:00 MDT by `date`, addenda A, A2 and a deviation note before the results they concern).
Everything is in `research\tighten\g5par\` (programs `g5par.cu`, `g5tied.cu`, `g5tup.cu`, `b3cnf2.py`, `verify_stage.py`, logs, hit lists).
Nothing built as a package, nothing filed or submitted, no `.key` read. At most two processes at a time, only my own PIDs stopped.
Clock is the shell `date` (it can drift).

## Answer in six lines

1. **Not free.** The parity of (Pb_K0 xor dx_K0) is fixed by the other chain members, so there is no record to re-choose: it costs a share f of the link-(iv) hits.
   Measured f (hits that are parity-compatible): IV 0.81, hA 0.06, hB 0.61 (first 150 dm2 only); pooled 0.67 (0.50 to 0.77); one-hit-per-distinct-target weighting gives 0.62, 0.07, 0.38 (pooled 0.44).
2. **Priced as if the choice were free or counted** (price.py at the measured D3b rate 2^-8.56): free 57.27 (57.19 to 57.35); counted at IV 57.57 (57.16 at IV's own D3b rate 2^-8.14);
   counted pooled 57.84 to 58.45. Board window 57.4 to 57.7: break-even to slightly worse, never a clear win.
3. **That price does not survive tying the generator to real hits.** All 215,169 real link-(iv) hits have an EVEN dm0, and C2 almost never passes for those: with the K0/K2 values taken from
   real hits, **2 passes in 1.75e9 draws (4.42M D3b instances), y = 21.1 (95% 19.2 to 24.1), price about 2^67.5**, and IV (1.92M D3b) and hA (0.33M D3b) have no pass at all (y >= 19.3, >= 16.7).
   The parity bit (Pb ^ dx) & 1 is necessary, not sufficient.
4. **The priced trace itself is unsatisfiable.** It is route 0 of M=213, the same per-op trail as `retest\t6\route_M213.json`. SAT (kissat, confirmed by cadical on two cases) proves no collision exists on
   that trace for h = IV flags 11 (t6), IV flags 1, hA flags 0, hB flags 0, and for a free chaining value with flags 0 or 1. So no complete collision can be assembled on it, whatever the work.
5. **Partial assembly done:** 4 real IV tuples (links (iii) and (iv) exact, K-stage m0..m7) checked with the organizer's BLAKE3 round code: columns, D0, D2 and both links hold (25 of 94 route zero-difference ops).
   For all 4, no choice of m8..m15 satisfies D1 or D3 (SAT, 1 s). Digest not equal.
6. **Recommendation:** do not file or spend more on G5 as priced. The honest status of the route is "stage-level costs measured, joint infeasibility proven for the modelled trace".

## Task 1: can the route always choose a parity-compatible K0 record?

Which constants set Pb_K0 and dx_K0 (code: `k_bscan`, `mode_vchain3`): K0 = G(h0, h4, IV0, t_lo; m0, m1).
dx_K0 = dm0 is the chosen difference of word m0 (and dm7 = -dm0 is forced). Pb_K0 = ror7(b1 ^ b1') comes from the first half only: a1 = h0+h4+x, d1 = ror16(t_lo ^ a1), c1 = IV0+d1, b1 = ror12(h4 ^ c1)
for the root x = m0 and x + dm0. So Pb is a function of (h, t_lo, x, dm0); m1 does not change it, it only selects which b-out difference T in SS(Pb) is realised.

Why the choice is not free: link (iv) demands the K0 b-out modular difference T4 = -(dS3 + dm4), with dS3 from the K3 solution and dm4 from the K2 record, and the kernel requires compat(T4, Pb).
compat forces bit 0 of Pb to equal bit 0 of T4. So once (dm0, dS3, dm4) are fixed, the root's Pb parity is already fixed; re-choosing the root cannot change it.
The C2 parity rule becomes "dm0 + dS3 + dm4 even", a property of the tuple. Choosing parity-compatible therefore means choosing among tuples. In 215,169 hits the code found 0 cases where the Pb parity
disagreed with the target parity (`L4PAR parity inconsistencies 0`).

Fraction of contexts that offer a parity-compatible hit (Run A: `vchain3` link-(iv) scans, all K3-solvable dm0 per dm2, seed 20261012; hB restricted to its first 150 funnel dm2, see deviations):

| | dm2 with a hit | (dm2,dm0) pairs with a hit | of those, with a parity-ok hit | hits | parity-ok | f_hit (cluster bootstrap 95%) | log2(1/f_hit) | distinct (dm0,dS3,dm4) | ok | f_grp (95%) |
|---|---|---|---|---|---|---|---|---|---|---|
| iv (342 dm2) | 103, ok in 56 | 193 | 100 (52%) | 68,511 | 55,226 | **0.806** (0.620 to 0.906) | 0.31 | 1,443 | 895 | 0.620 (0.522 to 0.683) |
| hA (256) | 21, ok in 4 | 55 | 5 (9%) | 2,283 | 134 | **0.059** (0.001 to 0.220) | 4.09 | 169 | 11 | 0.065 (0.006 to 0.178) |
| hB (150 of 660) | 90, ok in 71 | 699 | 281 (40%) | 144,375 | 88,739 | **0.615** (0.318 to 0.758) | 0.70 | 3,207 | 1,217 | 0.380 (0.294 to 0.453) |
| pooled | 214 | | | 215,169 | 144,099 | **0.670** (0.500 to 0.772) | 0.58 (0.37 to 1.00) | 4,819 | 2,123 | 0.441 (0.370 to 0.501) |

The targets themselves are 49% to 50% parity-ok; hits are skewed toward ok because roots with Pb parity equal to dm0 parity are more numerous (hit-weighted). One hit is one K0 root, but D3b depends on Pb and not on the root;
by distinct (dm0, dm4, Pb) the shares are 0.62 (IV), 0.03 (hA), 0.33 (hB). The wide intervals are cluster effects (few dm2 carry most hits).
Link (iii) is not independent of the dm4 parity (Run C, rate per (dm4,target) pair, even / odd dm4): IV 2^-9.90 / 2^-10.27, hA 2^-13.97 / 2^-10.92, hB 2^-10.62 / 2^-11.68; weighting by the dm4 parity of the ok tuples this changes the
cost by +0.01 (IV), +0.61 (hA, 7 ok tuples), +0.19 bit (hB) in favour of the ok tuples. Not applied.

Price with the choice (price.py, D3b rate 2^-8.56; y_eff = y_ok + log2(1/f); y_ok = 10.795, Run B below; "46.01 + y" in the old table used the old D3b rate and is 56.80 for y_ok):

| case | y | price.py total |
|---|---|---|
| unconditional (g5_y_result headline) | 11.69 | 58.16 |
| choice free (Run B, y_ok) | 10.795 (10.715 to 10.881) | **57.27** (57.19 to 57.35) |
| choice counted, IV, hit-weighted f | 11.10 | 57.57 (57.16 at IV's own D3b rate 2^-8.14) |
| choice counted, IV, group-weighted f | 11.48 | 57.95 |
| choice counted, pooled, hit / group | 11.37 / 11.98 | 57.84 / 58.45 |
| choice counted, hA / hB, hit-weighted | 14.40 / 11.76 | 60.87 / 58.23 |

So "yes at counted cost" is the answer to the question as posed, but it prices at break-even or worse, not at the 56.80 of the secondary row.

## Task 2: new preregistration and runs

Parity rule fixed in advance: ((Pb_K0 ^ dx_K0) & 1) == 0. Fresh seeds 20261012 (pilots 9000001 to 9000005 discarded). Sample size for +-0.1 in y: 1/sqrt(k) scaling from the earlier 1,939 passes (+-0.09) gives 1,570 passes.

- **Run B** (record-level parity-aware, replication with fresh streams, 1.546e9 draws, 12 threads, about 12 min): 2,257 passing instances in 4,011,159 D3b instances, **y_ok = 10.795, 95% 10.715 to 10.881** (Clopper-Pearson 10.736 to 10.856; dm2-cluster bootstrap 10.715 to 10.881; half-width 0.083).
  Per chaining value: IV 10.788 (10.658 to 10.926), hA 10.311 (10.115 to 10.516), hB 11.053 (10.943 to 11.171). Real-G re-check bad 0, legacy disagreements 0. It reproduces the earlier 10.786.
- **Run D** (Addendum A, written after IV's f was read and before any D result): the same generator but the K0 record (dm0, Pb_K0) and dm4 are drawn from the real link-(iv) hits of that dm2 (hit-weighted), K2 root from the pattern records of that dm4,
  no parity filter (a parity-bad hit never passes; counter `c2_badpar` = 0 in all runs). 4,096,000 draws per dm2 that has a hit, tier 1 and tier 2 (fixed in advance: tier 2 only because the half-width was above 0.10), 1.753e9 draws in total.
  Control: the same code path on synthetic hits (random admissible records) gave y 11.77 (expected about 11.7), so the pipeline is sound.

| Run D (tiers 1+2) | draws | D3b | D3c inst | C2 passes | y_all (95%) | price.py at measured D3b rate |
|---|---|---|---|---|---|---|
| iv (206 dm2-rows) | 8.44e8 | 1,920,137 | 95,350 | **0** | >= 19.3 | |
| hA | 1.72e8 | 328,426 | 2,726 | **0** | >= 16.7 | |
| hB (first 150 dm2) | 7.37e8 | 2,173,747 | 15,531 | 2 (both on the same hit: dm2 599aa9aa, dm4 79669529, dm0 56a96956, Pb d576d756; different S9/S14) | 20.05 (18.2 to 23.1) | 2^66.4 |
| all | 1.75e9 | 4,422,310 | 113,607 | 2 | **21.08 (19.2 to 24.1)** | **2^67.6** (2^65.8 to 2^70.7) |

Why: every real hit has an even dm0 (iv 68,511 of 68,511, hA 2,283, hB 144,375). In the uniform-record Run B the logged passes have dm0 odd in 100% (IV, 5,108 of 5,108), 96% (hA) and 82% (hB). Three isolating runs on IV (seeds 9000003 to 9000005, discarded):
real (dm0, Pb) with random dm4 (4.2e7 draws, 120,644 D3b): 0 passes; real dm0 with a random admissible Pb of that dm0 (4.2e7 draws, 172,691 D3b): 0 passes; synthetic records (8.4e7 draws, 234,879 D3b): 67 passes. So the cause sits in the dm0 set that K3 + link (iv) allow, not in the dm4 tie or in Pb.
Passes need Pb popcount 17 to 25 (mean 21.1); hit Pb has mean 18.8, which also lowers the odds. Why K3-solvable dm0 are even was not derived.
Caveats: the K1 side, link (iii) and D1 are still not imposed on these instances; hB is the first 150 dm2 only; the 2 hB passes come from one hit (one dm2/dm4/dm0/Pb), so the pass count is 2 but the number of independent tuples behind it is 1.

## Trace check (note from `retest\t6\RESULT.md`)

The priced trace is route 0 of `route_dump_213.out` (M=213, m0,m2,m4,m6,m7); it is the same per-op trail as `route_M213.json` (K0 [1,1,1,1,0,1,0,1], D3 [1,1,1,0,1,1,0,0], ...). So the t6 UNSAT does apply to it.
t6 used h = IV, flags 11 (root block). I re-ran the identical CNF builder with other settings (`g5par\runsat.sh`, `satruns.log`):

| h, flags, counter 0 | kissat | conflicts |
|---|---|---|
| IV, 11 (t6 repeat) | UNSAT 16 s | 291,231 (same as t6) |
| IV, 1 (deployable first block) | UNSAT 14 s; cadical UNSAT 58 s | 256,646 |
| hA, 0 | UNSAT 14 s | 203,219 |
| hB, 0 | UNSAT 9 s (cadical not decided in 200 s) | 140,995 |
| free chaining value, 0 | UNSAT 23 s; cadical UNSAT 14 s | 261,750 |
| free chaining value, 1 | UNSAT 15 s | 191,844 |

Leave-one-call-out (16 runs, `satruns3.log`): all UNSAT. Greedy call-level core (`core.log`, rounds 2, no digest equality): D0, D2, C0, C1, C2, C3 alone (45 zero-difference ops) are UNSAT.
Round 0 only: K calls SAT; K+D0+D2+D3 (no D1) SAT in 50 s; K+D (with D1) undecided at 120 s; rounds 2 with K,D,C calls and no digest: UNSAT in 15 s.
Encoding check: the SAT pair for K+D0+D2+D3 (messages differ in words 0,2,4,6,7) satisfies all 27 route zero-difference ops in an independent Python trace that matches the organizer's `_compress`
(K 2/2 each, D0 8/8, D2 8/8, D3 3/3; D1 0/5): mA = 8aa9c950 5a54b0b0 237bdb9b 3892c00c bdd510c8 216ed197 f21ed590 1c16cd49 | 9417d9fe 00000000 97770000 400000e0 8d0cb91a 80000000 2e45c12d 294e2080,
mB = 033352c8 5a54b0b0 b7d2a231 3892c00c 463b7761 216ed197 00cf5a6c 3ef6676f | same m8..m15 (h = IV, flags 1, one round; `check_sat_pair.py r0_KD_noD1 1`).
Limit: this proves the word-level trace has no bit-level collision; it does not say no collision exists off this trace.

## Task 3: complete 2-round collision for the route

**Not assembled. The route as priced cannot be completed** (SAT above), and independently the stage costs are not reachable.
Largest stage reached, with real data and checked with the organizer's reduced BLAKE3 (`org_blake3.py` = `git show origin/main:verifier/blake3.py`, sha256 bf67aca2...0237; my G tracer is asserted equal to its `_compress` for every pair):
4 IV tuples from `vchain3` (L4 exact and L3 exact; `tup_iv_vchain3.txt`, `KSTAGE` lines), two distinct (dm0, dm2, dm4):
(a5554956, 356adaaa, 1d2b334e) and (5665a59a, a56a9556, a6d59967), each with 2 message variants. Example (flags 1, h = IV, counter 0):
mA[0..7] = 72c0a68d 662ca0ca 4cd3b8de 351599fd 8e12667c c8cab46a b82b4afa d5f87a91, B = A + dm at words 0,2,4,6,7 (dm0 a5554956, dm2 356adaaa, dm4 1d2b334e, dm6 ca952556, dm7 5aaab6aa), m8..m15 any common block.
Verified for all 4: state words equal after the round-0 columns 8/16 (as predicted), link (iii) dS1+dS6 = 0 and link (iv) dS3+dS4+dm4 = 0 on the real words, route zero-difference ops 25 of 94
(K0..K3 2/2, D0 8/8, D2 8/8, D1 1/5), 2-round digest equal words 0/8, organizer two-block messages not equal.

What is missing, with measured rates: D1 cancellations (0 of 208 D1 instances in the real chains, 2^-19.9 on synthetic ones; for these 4 tuples SAT proves no m8..m15 gives D1 or D3, 1 s each, `fixd.log`);
D3b (2^-8.6) then D3c (2^-4.3 on real hits) then C2 (2 in 4.4M D3b on real hits); the whole of round 1 (C0 to C3, E0 to E3, 0 of the 62 ops checked) and the digest.
hA: no exact-link tuple (0 of 256 dm2, `tup_hA.out`). hB: none (old run). The pair file is part of the logs, not a package.

## Deviations and limits

- hB Run A/C used the first 150 of 660 funnel dm2 (all 660 would take about 75 min at maxdm0 = 1000); iv and hA are complete. Run D hB therefore covers 90 hit-carrying dm2.
- The prereg named f_hit primary; distinct-target and distinct-Pb weightings are reported because hits that share a Pb give no new D3 instance (post-hoc argument, written before Run D).
- Run B and Run D still draw K1 and K2 values independently of links (iii) and D1; price.py's per-step operation counts and 2^10 D3 instances per tuple are untouched GUESSes.
- hA/hB are synthetic chaining values (reachable only by a prefix search); IV flags 1 is the only first block that needs no preimage.
- Bootstrap rows for Run D treat the two tiers as separate clusters; the reported interval is the wider Clopper-Pearson one.
- Clock drift possible (shell `date`).

Files: `g5par\{prereg refs, analysis_D_pooled.txt, parA_*_vchain3.txt, parA_*_hits.txt, parB_*.tsv, parD1_*.tsv, parD2_*.tsv, parC_*.out, satruns*.log, core.log, fixd.log, cad.log, tup_iv_vchain3.txt, verify_stage.py}`.
