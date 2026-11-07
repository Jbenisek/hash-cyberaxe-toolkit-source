# carrygraph: bit-serial carry-graph solve of the 21-equation cycle (2026-10-09)

**Question:** can the E3-fixed cycle (split_e3: unknown g = C0.b1, check Y9 = C1.c1 + Y13, today a 2^32 scan at 43 ops = 2^37.43 ops) be solved with a bit-serial carry graph, as Sol solved his one-word cycles in D4 7.2? Break-even with 63.6027 needs under 2^16.4 ops per solve.

**Verdict: DOES NOT WORK.** No carry-graph order we could find, and none in the order families we searched exhaustively, does better than the 2^32 scan.
- Sol's recipe applied directly (one bit per addition per step, guessing the bits each rotation wraps) needs **2^75.75** live branches at its peak and about **2^79.9 transitions** per solve, against 2^32 for the scan.
- Every bit-serial order whose carry chains start at bit 0, at any relative speeds, peaks at **exactly 2^32** live branches at best. This is an exact search, and the best order is the scan itself. The scaled copies agree: the minimum is the word size at n = 8 (8) and at n = 16 (16), and it stays 8 at n = 8 when guessed carries are allowed. So no order prunes before the solver has carried as much uncertainty as the whole of g.
- **Why:** the cycle's 9 modular additions are joined by 20 rotation edges that form **11 independent rotation cycles**, and every one of them has a nonzero net rotation (12, 4, 24, 12, 12, 24, 4, 4, 8, 24, 8). Sol's equations have exactly one rotation on the path of the unknown, so one frame shift aligns every addition and a 16-state carry graph suffices. Here no frame assignment aligns them. The first equation already breaks it: Y12 = (g ^ R7(Y4)) - (R12(g) ^ X4) adds g to itself rotated by 12.
- The price stays at **84.61**. The cycle solve remains the blocker named in split_e3 section 5.

COMPUTED = run here. DERIVED = arithmetic on computed numbers. GUESS = not established.

## 1. Model (COMPUTED, cyc.py)
- The cycle is rewritten as 9 modular additions over XOR/rotation operands (`cyc.ADDS`): Y12, d1, a1, Dd1, w10, C1a1, C1c1, Y1, chk. chk = C1c1 + Y13 - Y9 must be 0. The words w2, Ka1, w3, X12, X1, Y0, C1d1, C1b1, Y13 fold into operands (for example C1a1 = (R24(d1) ^ R8(a1) ^ Dd1) + ~a1 + K5).
- This model equals the solve.cu transcription on 20,000 random (P, g): all 9 words agree (chk up to sign).
- All 16,491 GPU roots in split_e3/roots_2.txt (16,392 real instances) satisfy it (analyze.py replay, section 5).

## 2. Why the carry graph cannot align (COMPUTED, analyze.py)
Rotation edges, written as consumer <- word (rotation): Y12 <- g(0), g(12); d1 <- g(12); a1 <- Y12(8), d1(0), g(0); Dd1 <- d1(16), a1(0); w10 <- Dd1(16); C1a1 <- d1(24), a1(8), Dd1(0), a1(0); C1c1 <- C1a1(16); Y1 <- C1a1(0), C1c1(20), w10(0); chk <- C1c1(0), C1a1(8), Y1(24).

That is 10 nodes and 20 edges, so 11 independent cycles. With a spanning tree from g, the cycle closed by each non-tree edge has this net rotation:

| closing edge | net rotation (mod 32) |
|---|---|
| g -> Y12 (rot 12) | 12 |
| d1 -> a1 (0) | 4 |
| g -> a1 (0) | 24 |
| a1 -> Dd1 (0) | 12 |
| a1 -> C1a1 (8) | 12 |
| Dd1 -> C1a1 (0) | 24 |
| a1 -> C1a1 (0) | 4 |
| C1c1 -> Y1 (20) | 4 |
| w10 -> Y1 (0) | 8 |
| C1a1 -> chk (8) | 24 |
| Y1 -> chk (24) | 8 |

- A bit-serial solver processes each addition in one bit frame. A cycle whose net rotation is m forces misalignments along that cycle that add up to m (mod 32).
- At a misaligned edge, the consumer needs bits of its input before they are computed. The solver must guess them, and they stay live, unpruned, until the producing chain catches up.
- Sol's D4 FIRST/SECOND reduce to (P_A + R_r(Q_A ^ z)) ^ (P_B + R_r(Q_B ^ (z + delta))). That is one rotation and zero independent misaligned cycles, so 16 carry states x 32 bits x 2 = 1,024 transitions.

## 3. Sol's recipe generalised: time sweep (COMPUTED, sched.py, width.py; model checked in section 5)
- Each addition gets a frame. At step t it processes bit t - f. The solver guesses g bits at first use, guesses wrapped and early bits and verifies them when computed, and guesses one carry per chain that does not start at bit 0.
- Expected live branches = 2^(guesses - checks).
- Search over 32^9 frame vectors: coordinate descent, 300 restarts over 2 seeds, both converging. Best frames: Y12 8, d1 0, a1 0, Dd1 16, w10 0, C1a1 8, C1c1 20, Y1 0, chk 20.

| word size n | peak live bits | log2 transitions (predicted) | scan log2 |
|---|---|---|---|
| 8 | 22.00 | 26.77 (measured 26.93) | 8 |
| 16 | 40.00 | 45.38 | 16 |
| 24 | 57.17 | 62.70 | 24 |
| 32 | 75.75 | 79.92 | 32 |

- The n < 32 copies scale every rotation by n/32. All cycle rotations are multiples of 4, so the structure is exact.
- **Breakdown of the n = 32 peak** (event 209, step ~12): 32 g bits known minus 11 chk bits = 21, plus 48 bits guessed ahead, plus 6.75 open carry bits.
  - The 48 bits ahead: a1 16 (Dd1 = K - (R16(d1) ^ a1) and C1a1 read a1 at offsets 0/8 against d1 at 16/24), Dd1 8 (w10 = R16(Dd1) ...; C1a1 reads Dd1 at 0), C1a1 12 (C1c1 = R16(C1a1) + X9; chk reads R8(C1a1)), Y1 12 (chk reads R24(Y1)).
- The lookahead grows linearly with n (about 2.35 n), so the sweep is worse than the scan by about 2^44 at n = 32.

## 4. Any bit-serial order (COMPUTED, lattice.py, lattice2.py, exact_lb*.py)
**Model:** each addition advances its carry chain one bit at a time from a start bit, at ANY relative speed. Live level = g bits known + output bits needed before computed + open carry guesses - chk bits done. Guessed-ahead bits net out when they are verified.

**Exact threshold search** (BFS over progress vectors, every state with level <= T kept, no beam):

| n | chains from bit 0 | free starts (guessed carries allowed) |
|---|---|---|
| 8 | T=7 unreachable, T=8 reachable: **min = 8** | T=7.9 unreachable, T=8 reachable: **min = 8** |
| 16 | T=15 unreachable, T=16 reachable: **min = 16** | full search aborted (8.3M states at progress 4). With at most one guessed carry, all 136 start vectors are unreachable at T=15.9: **min = 16** in that subfamily |
| 32 | T=24, 28, 31 unreachable (T=31: 576k/484k/2.4k states at progress 16/32/48, dead at 55); beam reaches 32.00: **min = 32** | not run (state space) |

**Beam searches at n = 32:**
- Chains from 0 (beam 3,000): best 32.00. This is the "know all of g, then evaluate" order, the scan itself.
- Sweep starts with free speeds: 42.58. Free starts (beam 500): 55.58, myopic.

**Reading (DERIVED):** wherever the search is exact, the best carry-graph order carries n live bits, as many as g itself. So in this family the carry graph is at best the scan in disguise: at n = 32 the peak level alone is 2^32 live branches, and at about 17.6 ops per transition that is >= 2^36 ops. It never comes near 2^16.4.

**Memoisation (DERIVED, not run):** a DP that merges branches does not remove the guessed-ahead bits. They are unconstrained in every live branch and are part of any frontier, so merging cannot shrink the lookahead terms of section 3.

## 5. Validation
**n = 8 exact search vs exhaustive (COMPUTED, cg.c `dfs` vs `ex`).**
- 300 random instances with the real constant structure (mkinst.py rand): **300/300 identical root sets**, 315 roots (mean 1.05).
- Work per solve:

| | min | mean | max |
|---|---|---|---|
| transitions | 127,900,097 | 2^26.931 | 127,916,057 |
| ops | | 2^31.069 | 2^31.069 |

- That is 17.6 ops per transition in the op model of cg.c's header, against 2^8 candidates for the scan.

**n = 32 schedule on real instances (COMPUTED, analyze.py replay).**
- Inputs: all 16,392 real generator instances of split_e3/inst_2.txt. For each GPU root, the best 32-bit schedule was walked with every guess set to the true bit or carry.
- **16,491/16,491 roots pass every check.** 32,784 random non-roots are **all rejected**.
- Each root has exactly one path, because every guessed bit and carry is a function of g. So the 32-bit schedule returns exactly the GPU root set.
- The full 32-bit search was NOT run: it needs about 2^79.9 transitions, about 2^84 ops per solve (DERIVED from 17.6 ops per transition).

**Reference.**
- Reused the GPU exhaustive roots (split_e3/roots_2.txt, solve.cu).
- Independent CPU exhaustive (cg.c `ex` at n = 32, 672 s for 4 instances) on the first 4 real instances: the root sets {1836dc44, fe64bd69}, {3842d110, 4e4c99c8}, {b5915343, facb05ec}, {2829994b} are **identical to the GPU's** (COMPUTED, ex_real4.txt).

## 6. Price (DERIVED)
- score = 47.18 + log2(ops per solve), with the filter 2^12.95 and 2^42.98 trials unchanged.
- Sweep carry graph: about 47.18 + 84.1 = 131. The best order in the exact families is >= 47.18 + 36 = 83, no better than today's 84.61.
- **No change to the front line.** The 2^16.4 bar is about 20 bits below the floor these searches show.

## 7. Not done / limits
- No proof for orders outside the lattice model: several guessed carries per chain (chains split into pieces), non-bit-serial guessing, or algebraic or SAT solvers.
- With guessed carries, the exact bound covers all starts only at n = 8. At n = 16 it covers starts with at most one guessed carry. At n = 32 only the beam ran (best 42.58 found).
- **The 200-real-instance requirement was met by replay, not by a timed search.** The 32-bit schedule returns exactly the GPU root set on 16,392 real instances, but the full DFS cannot run (about 2^80 transitions). The timed exact search ran at n = 8 only (300 instances).
- Optimality of the sweep frames is by restarts, not proof (GUESS that 75.75 is optimal).
- The live-branch model assumes each check halves the branches. It matched the n = 8 measurement within 0.16 bits.
- Only 2 of the 14 cycle parameters (Y4, Y9) are fixed by E3. The other 12 depend on the free words (each word moves 2-7 params), so per-E3 precomputed tables do not apply to this cycle as built.

## Files
- cyc.py: model and check.
- width.py: sweep and treewidth heuristics, width_out.txt. The bit-graph treewidth lower bound by minor-min-width is 23.
- sched.py: schedules and frame optimiser, sched_n8/n32.txt; opt/ holds the n=32 optimiser runs.
- cg.c: DFS carry-graph solver and exhaustive reference.
- mkinst.py: instances inst_n8.txt, inst_real300.txt, inst_real4.txt.
- dfs_n8.txt, ex_n8.txt, ex_real4.txt.
- analyze.py with analyze_out.txt.
- lattice.py, lattice2.py, exact_lb.py, exact_lb_n.py, exact_lb_free.py, exact_lb_one.py, with exact_lb_log.txt, exact_lb_T31.txt, exact_lb_free_n16.txt, exact_lb_one_n16.txt.
