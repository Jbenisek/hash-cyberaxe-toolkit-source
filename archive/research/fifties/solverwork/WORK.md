# Executed solver work vs the cap C_G(T) (G7 + G15, CG layout): 2026-10-09, local, nothing submitted

**Question.** The front-line credit charges each solver call at its worst-case cap. Under the CG layout (Sol CD 11.3) the cap is C_G(T) = 1024 + 2304 F + 3328 n_s + 5216 n_l, with a maximum of 17,504. The credit is 1.06 x (16/27) x cbar_old (CD 11.4). How much work does a call actually execute?

## Answer

| | value | label |
|---|---:|---|
| Solver calls measured (2 walks x 2^32 outer steps) | 1,063,703 + 1,065,105 | MEASURED |
| Mean executed per call / mean C_G per call (same calls) | 5,242.8 / 8,664.6 = **0.6051** (SE of the mean 0.92 units) | MEASURED |
| Executed per outer step, reweighted to the model T cells | 1.29967 units | MEASURED |
| Model mean of C_G per outer step | 2.14801 | DERIVED (ledger.txt cells) |
| Credit basis (16/27) x cbar_old per outer step | 2.45131 | DERIVED (CD 11.4) |
| **r = executed / credit basis** | **0.5302** (+/- 0.00001) | MEASURED / DERIVED |
| r with the program-only extras added (walks 20, g25 9, g29 4, e29 1: +124 units per call) | 0.5427 | MEASURED |
| **Bit gain** if the credit row (21% of the total) is charged at 1.06 x the executed mean | **0.150 bit** (0.146 with the extras) | DERIVED |
| The same with CREDIT_G's real share of N_G (16.37%) | 0.115 bit | DERIVED |
| Part of that gain that needs only a T-only premise (C_G model mean in place of (16/27) cbar_old, r = 0.8763) | 0.038 bit at 21% | DERIVED |

**Distribution of executed / cap per call (MEASURED, walk P; walk R is identical to 4 decimals).**
Quantiles: 1% 0.447, 10% 0.518, 25% 0.554, 50% 0.569, 75% 0.712, 90% 0.715, 99% 0.768, max 0.928. The largest executed call was 11,740 units on walk P and 12,704 on walk R, against a largest cap of 17,504. **No call exceeded its own cap (0 of 2,128,808).** The distribution is multimodal by T cell, because the fixed part dominates:

| T (rows) | calls (P) | mean executed | C_G | ratio | old G7 tree executed / C_old |
|---|---:|---:|---:|---:|---:|
| 01 (175) | 71,318 | 4,806.0 | 6,656 | 0.722 | 7,794.8 / 12,416 |
| 02 (185) | 367,606 | 4,756.3 | 6,656 | 0.715 | 7,712.9 / 12,416 |
| 04 (275) | 71,004 | 4,790.6 | 8,544 | 0.561 | 7,778.1 / 17,120 |
| 08 (285) | 20,661 | 4,992.0 | 8,544 | 0.584 | 8,153.7 / 17,120 |
| 10 (385) | 217,311 | 4,773.4 | 8,544 | 0.559 | 7,744.8 / 17,120 |
| 12 (185,385) | 219,930 | 6,196.3 | 11,872 | 0.522 | 9,046.0 / 23,136 |
| 18 (285,385) | 18,277 | 6,289.9 | 13,760 | 0.457 | 9,230.3 / 27,840 |
| 40 (685) | 41,222 | 4,820.1 | 6,656 | 0.724 | 7,817.4 / 12,416 |
| 42 (185,685) | 22,694 | 8,498.0 | 12,288 | 0.692 | 11,345.2 / 20,736 |
| 52 (185,385,685) | 13,680 | 9,924.1 | 17,504 | 0.567 | 12,658.2 / 31,456 |

The cell shares match the model to within sampling error. P(T != 0) was 2.4766e-4 on walk P and 2.4799e-4 on walk R, against 2.4786e-4 in the model.

**Where the gap is (MEASURED).** Per call, the fixed part 1024 + 2304 F + 1408 |T| averages 5,197 units, which is 99.1% of the executed work. The trees execute 46.5 units per call against a tree cap of 3,469 per call, or 1.34% of it. The reason is that 76% of rows (1,027,472 of 1,351,964) are dropped in row_setup by guards (a)-(g) and (G7) before any tree node is visited. Surviving rows prune early, and G15 cuts the tree further. Mean tree units per row: 175 70.0, 185 17.7, 275 54.6, 285 190.4, 385 36.7, 685 62.6, against row tree caps of 1,920 (small) and 3,808 (large). For comparison, the old G7-only tree gives executed / C_old = 0.4905.

## Does executed work depend on anything a premise would have to cover? YES, but only through 0.9% of it (DERIVED from the code)

- The fixed part (99.1%) is a function of T alone, the same quantity that H5' (V = C(T)) covers. Its model mean of 1.28814 per step is exact.
- The tree part (0.9%) depends on words other than T:
  - row_setup guards (a)-(g) and (G7): bits of Q = Y9, y = Y4, E = omega, E' = E + DY3, kappa, e1 bits 2/21/22/23, and C2.c1, C2.b1 bits 22-23.
  - Every tree arc: the descriptors of Q, y, E, E' and kappa at each position.
  - G15: e1 >> 22, C2.c1 >> 22, C2.b1 >> 22, (Y1 + w12) bits 16-24 and Y12 bits 16-24.
  - Leaf tests: J1-J3.
- So a credit at the executed mean needs a NEW premise on the real-walk joint law of (Y9, Y4, omega, C2.c1, C2.b1, Y1 + w12, Y12) given T. H5' does not cover this, and there is no exact model mean for the tree part.
- Because that part is about 1% of the charge, a crude bound would do. Charging the tree at 10x its measured mean gives r = (5,197 + 465) / 9,890 = 0.5725, a gain of 0.136 bit at 21% (DERIVED arithmetic on a hypothetical charge).
- A T-only premise on C_G itself (r = 0.8763) is worth 0.038 bit. prereg7's 2^39 histogram records T, so E[C_G(T)] on that sample can be computed from its run_out.json without a new run (not done here).

## Method (MEASURED unless marked)

- **Steps.** I used prereg7's validated generator: Philox4x32-10 words with the prereg7 MAIN seeds, indices 0 to 2^29-1 in each of the 8 streams. That is a subset of prereg7's main sample, run through pkg12b ctr_outer, the 14-outcome automata and formula (V). T = H_Q & H_E & 0x5f & VMASK[v].
  - `passgpu.cu` is the prereg7 kernel `v7gpu.cu`, byte for byte, plus one filter kernel (gen_pass.py; the diff is only the added lines). It lists the indices with T != 0 in 2.4 s.
  - Every listed step was recomputed in Python with the unchanged `run_prereg.eight_words` + `ref_fields`. GPU/Python T or v mismatches: 0 of 2,128,808.
  - False-negative check: a Python scan of the first 524,288 indices of stream 0 gave exactly the GPU list (131 on P, 127 on R).
  - The package's own filter (pkgBA16 build_tables/look) gives the same T on every call, and nu_of = v on every call.
- **Two walks.** prereg7's ctr_outer uses CTR_FLAGS = 3. The front-line pkgBA16 step CO (root instance) uses FLAGS = 11 in K3.d1, so every derived name differs between the two.
  - Walk P is prereg7 as validated.
  - Walk R is the same kernel with the flags-11 constant. Its names were checked name by name against pkgBA16 `scalar_outer` (0 mismatches).
  - The two walks agree on every statistic within the SE. **Side finding for the caller:** prereg7's H5' sample ran on the flags-3 walk, not the root instance's flags-11 walk. On 2^32 flags-11 steps the T law still matches the model (P(T != 0) z about +0.5; cell shares as above).
- **Solver.** I used the pkgBA16 halfsearch.py functions unchanged, loaded as a module: row_setup (guards (a)-(g), (G7), walks of bits 0..6), FORCED/DUAL/SELECTED, fixed_arc, g15/g15_words, is_joint_root.
  - halfsearch.py has the full G7 tree (`traverse`) and the slot16 one-path G15 mode (`path16`, cap 8,936, the source of the "largest step 8,558" figure). It has no full tree with G15 as the CG layout specifies.
  - `trav()` in solver_measure.py is BA.traverse with one switch. With g15=True, free position 15 is deleted and h15 is prescribed by G15, exactly as in BA.path16 (CF 7.1/7.2).
  - With g15=False, trav() matched BA.traverse (roots and every node count) on all 649,242 rows that survived setup.
  - Every G15 root was also a G7 root. G15 removed 42 of the 45 G7 joint roots; it is a necessary condition only for full successes (CF 7.1).
  - Rows with two different depth-7 states: 0, so no tree ran twice.
- **Units.** I used the cap ledger with the actual counts: 1024 + 2304 F + 1408 rows + 20 forced + 48 free + 4 sel20 + 64 g15 + 80 leaf + 120 root.
  - A static all-arcs run reproduces the CF 7.2 full-tree counts exactly: small rows 42/3/2/2/4 give 1,920; large rows 80/7/4/4/8 give 3,808. The G7 trees reproduce ledger.txt: 72/7/4/8 gives 4,736 and 140/15/8/16 gives 9,440.

## Limits

- The fixed allowances (1024, 2304 per family, 1408 per row) are charged flat, as in the ledger and the program. Their true instruction counts, for example for a row dropped at guard (a), were not measured, so "executed" is an upper bound there.
- Node costs are the ledger's per-node upper costs, not instruction counts.
- The CG full tree with G15 is my construction from CF 7.1/7.2 and BA.path16. No package code implements it.
- The certificate was not run; it is charged at 120 per root (3 G15 roots in total).
- The words come from Philox, a pseudorandom generator. The sample is 2^32 steps per walk.

## Files (all here)

- Code: gen_pass.py, passgpu.cu, passgpu11.cu (and binaries), solver_measure.py, analyse.py, build_and_list.sh, full_run.sh, run_py.sh, env.sh, debug_names.py.
- Results: static_check.json, measure_{P,R}_1000000.json, summary.json (all figures above). measure_{P,R}_250.json are the timing runs.
- Data: pass_list_{P,R}.txt, the GPU lists. They can be regenerated in 2 s with build_and_list.sh.
