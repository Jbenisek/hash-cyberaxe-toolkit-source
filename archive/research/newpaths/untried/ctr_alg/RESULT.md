# ctr x alg: an off-the-shelf SAT solver for the per-step E3 systems (GAPS.md section 2, row 3)

Research only. Nothing was filed or submitted. Run 2026-10-10, WSL Ubuntu, Ryzen 9 7900X. Labels: COMPUTED
(measured or counted in a run here), DERIVED (computed from COMPUTED numbers by a stated formula), GUESS.

## Verdict: DEAD. No bits saved on X2.

No off-the-shelf solver does the per-passing-step E3 solve with less measured work than the DFS.

- **Best realistic set-up:** CryptoMiniSat in-process through its C API, with one incremental template and each step as
  assumptions. It costs **2^18.97 cycles per passing step**, against the simple DFS's **2^18.68 ops** on the same 270
  record steps (both DERIVED). On the X2 ledger that is **T 71.232, i.e. -0.24 bit vs 70.990** (DERIVED).
- **Command-line use:** 1.8 to 4.5 bits worse.
- **Lower bound only:** the counter lower bound (formula literals + propagations, 1 op each) would give +0.93 bit. No
  measured cost comes within 2^5.5 of it.

Why:
1. **The systems are tiny.** One 32-bit unknown, about 456 variables and 2,133 clauses (COMPUTED, rec11_s000_t4). The DFS's 2^18.5 ops
   per step is already about what one solver call costs to set up and preprocess.
2. **The solvers' work is not in their counters.** kissat refutes all 270 real steps with 0 conflicts (COMPUTED). The
   refutation happens in preprocessing: SAT sweeping in its kitten sub-solver, congruence closure, backbone and
   substitution (ablate_out.txt). Plain CDCL needs 52.6 conflicts per system (COMPUTED, 23 systems). So the counters
   badly understate the cost, and measured CPU sits 2^5.5 to 2^11 above the lower bound.
3. **The ceiling is low anyway.** On X2 the solve term is about 415 of 850 units. Even SOLVE = 0 gives T 70.024, only
   +0.966 bit (DERIVED).

## Key numbers (per passing step; X2 ledger = stack_calc V4, T = 69.987 + log2((435 + 2^-9.8132 SOLVE)/430) + 0.02)

| measure | rec7 (150 steps) | pooled rec7+rec11 (270) | T on X2 (pooled) | vs 70.990 | label |
|---|---|---|---|---|---|
| DFS simple (e3solve.py weights 6/12/40/1024) | 2^18.51 (record reproduced, T 70.988) | 2^18.68 | 71.075 | -0.085 | DERIVED |
| DFS joint (e3solve2.py weights) | 2^19.16 | 2^19.21 (rec11: 2^19.26, nodes 2^15.91 = record) | 71.372 | -0.382 | DERIVED |
| SAT lower bound, best config (cms) | 2^12.81 | 2^12.82 | 70.050 | +0.940 | DERIVED |
| CLI process CPU minus start-up, best (cadical) | 2^23.31 | 2^23.37 | 74.864 | -3.873 | DERIVED |
| CLI solve phase only (F - F_bot), best (cadical) | 2^21.17 | 2^21.13 | 72.800 | -1.810 | DERIVED |
| CLI solve phase: kissat / cms / kissat-nc | | 2^22.61 / 2^22.58 / 2^23.61 | 74.14 / 74.11 / 75.10 | -3.15 / -3.12 / -4.11 | DERIVED |
| cms in-process, fresh solver per system | 2^22.25 | 2^22.18 | 73.744 | -2.753 | DERIVED |
| **cms in-process, incremental template** | **2^18.77 (T 71.124)** | **2^18.97** | **71.232** | **-0.242** | DERIVED |
| oracle per-system min(DFS simple, cms incremental) | 2^18.08 | 2^18.23 | 70.862 | +0.128 | DERIVED (oracle; a real chooser gets less: GUESS) |
| SOLVE = 0 (ceiling of any solver) | | | 70.024 | +0.966 | DERIVED |

Full table: ledger_out.txt. On rec7, the record's own steps, incremental CMS against the record DFS is -0.134 bit.

- **Packed-outer variant (stack_calc V4p, c = 81 + ...):** V4s (68.135) GUESSED a solver at 2^15 per passing step. No
  off-the-shelf solver comes near that. The measured best (2^18.97) gives T 70.606 (DERIVED), not 68.13; V4p with
  the DFS is 70.213.
- **Joint DFS tail:** the joint DFS has a heavy tail, with median 2^16.80 against mean 2^19.21 (DERIVED). The solver's
  cost is nearly flat across steps: incremental median 2^18.63, mean 2^18.97.

## Conversions (stated)

- **DFS:** counts (COMPUTED) times the stack code's own op weights (DERIVED).
- **SAT lower bound (most favourable to SAT):** each literal of every formula read counts 1 op, and each propagation
  counts 1 op. Decisions, conflict analysis, learning, congruence closure, sweeping, Gauss-Jordan and the sub-solver
  are all charged 0.
- **SAT measured:** child CPU seconds (getrusage, COMPUTED) times 4.7e9 cycles/s (/proc/cpuinfo 4699.9 MHz),
  counted as 1 word op per cycle. In-process timings use perf_counter_ns around the single C call. GUESS: IPC >= 1 on
  this cache-resident formula, so cycles understate the solver's instruction count, which favours SAT.
- The two sides are in different units: DERIVED ops for the DFS, measured cycles for the solvers. The DFS was not
  timed in C.

## Method (e3sat.py, e3sat_time.py, cms_inproc.py, ledger.py)

**Systems.** The stack code was imported read-only (no bytecode written there). There are three sets:
- **rec11:** the exact 120 passing steps of e3solve2.py's record run, seed 11. COMPUTED: 120 of 127,617 tried, as in
  e3solve2_rerun.txt.
- **rec7:** the exact 150 steps of e3solve_out.txt, seed 7 after replaying the 300 plants' draws. COMPUTED: 150 of
  148,371 tried.
- **Main sample:** the first 20 steps of rec11, which have 23 viable outcomes, so 23 systems. These get per-instance
  lines, 5 to 9 timing repetitions, and their CNF/XNF files are kept in cnf/.

The full sets were added because the DFS mean is tail-driven. 20 steps cannot estimate it, and solver runs cost
milliseconds.

**Planted systems (12).** These check that a "no solution" answer is trustworthy:
- **5 rplant:** random real pairs, each with its own differences as the target, as in e3solve.py (a).
- **7 bplant:** one per beta* tau, on the real targets. kissat finds a full E3 solution with y (class member), q, w8
  and h1 all free, with 24/16/8 random q/w8 bits fixed for diversity. Each plant is re-checked forward, passes the exact
  outer filter, and is then solved as an ordinary per-step system.
- **Why not algebraic plants:** they were too slow. For a fixed g1, condition (2) needs K = DY3 + f1' - f1 to satisfy
  15 linear bit conditions: K_0 = eps_0, plus one condition at each of eps's 14 zero bits in positions 0..30. Only
  the bits of y at G's one-positions move K. The class fixes 15 bits of y + Y3, and 9 of those sit at G's 14
  one-positions (tau#0), so very few y qualify (diag_plant.py: 0 of 300 sampled; test_bplant.py: closed form exact on
  3,000 K, no plant in 40 s per tau; console output, not saved).
- All 7 beta* outcomes are reachable in E3 (test_gen_out.txt, COMPUTED).

**Encoding.** h1 is the 32-bit unknown, and E3 runs on both messages (h1' = h1 ^ eta). The constraints are dg1 = G,
de2 = eps, dg2 = tau. There are two encodings:
- **CNF** (Tseitin, constants folded) for kissat and CaDiCaL.
- **XNF** for CryptoMiniSat: the same circuit, with every XOR gate as an XOR clause.

Every solver enumerates all solutions, using a blocking clause on h1 and re-running until UNSAT.

**Solver configs.**
- kissat 4.0.3 with `--check=0`. The Ubuntu build checks every derived clause by default, which only adds time.
- kissat-nc: the same, plus `--congruence=false`.
- CaDiCaL 2.1.3, default.
- CryptoMiniSat 5.11.21, default, with XOR clauses.
- Every run uses `kissat --time=300` / `-t 300` / `--maxtime 300`. At most one solver ran at a time, besides the
  driver.

**Timing split (e3sat_time.py).** Each formula F is timed against F_bot, which is F with the units (v), (-v) appended
at the end. The solver reads all of F, then stops at once. solve = cpu(F) - cpu(F_bot), with medians of interleaved
runs and no output printed.

**In-process (cms_inproc.py).** libcryptominisat5.so is driven through ctypes; nothing was installed or compiled. There
are two modes:
- **Fresh:** a new solver per system.
- **Incremental:** one parametric template (1,072 variables, 1,737 clauses, 541 XOR clauses) for all 337 + 12
  systems. Each system is one solve under 192 assumption literals, and learned clauses carry over.

## Correctness (COMPUTED)

- **Agreement:** on 349 of 349 systems, the solution sets agree across simple DFS, joint DFS and all four solver
  configs, and both in-process modes agree too.
- **Soundness:** 0 unsound models (every model was re-checked with e3solve.e3).
- **Plants:** 12 of 12 planted h1 found by both DFS's and every solver.
- **Real systems:** 0 of 337 have an E3 solution, consistent with e3solve_out.txt's 0 in 150.

## Per-instance verdicts (verdicts_out.txt)

Each line compares the cheapest measured solver cost (CLI solve phase, in-process fresh, in-process incremental)
against the cheaper of the two DFS's on that instance. Costs are log2 per system. Incremental figures for the first
lines include the template's cold start. rec11_s008_t1 had one CLI split below timing noise, which was dropped.

| system | sols | DFS simple / joint | SAT LB | best measured SAT | verdict |
|---|---|---|---|---|---|
| rec11_s000_t4 | 0 | 18.0 / 13.9 | 11.9 | 20.2 | SAT dearer by 2^6.3 |
| rec11_s001_t0 | 0 | 15.2 / 14.8 | 12.5 | 18.7 | dearer 2^3.9 |
| rec11_s002_t4 | 0 | 19.2 / 13.6 | 12.0 | 18.6 | dearer 2^5.0 |
| rec11_s003_t1 | 0 | 18.3 / 19.8 | 12.3 | 18.5 | dearer 2^0.3 |
| rec11_s004_t4 | 0 | 17.6 / 12.7 | 12.0 | 18.2 | dearer 2^5.5 |
| rec11_s005_t1 | 0 | 12.8 / 12.8 | 11.8 | 17.9 | dearer 2^5.1 |
| rec11_s005_t4 | 0 | 14.0 / 12.7 | 11.9 | 16.9 | dearer 2^4.1 |
| rec11_s006_t0 | 0 | 17.1 / 17.5 | 12.8 | 18.4 | dearer 2^1.3 |
| rec11_s007_t1 | 0 | 18.4 / 21.1 | 12.2 | 17.9 | SAT cheaper by 2^0.4 |
| rec11_s007_t4 | 0 | 19.9 / 21.1 | 12.2 | 17.6 | cheaper 2^2.3 |
| rec11_s008_t1 | 0 | 19.3 / 20.8 | 12.6 | 18.4 | cheaper 2^0.9 |
| rec11_s009_t1 | 0 | 19.3 / 16.1 | 12.7 | 17.9 | dearer 2^1.8 |
| rec11_s009_t4 | 0 | 20.0 / 16.1 | 12.7 | 17.8 | dearer 2^1.6 |
| rec11_s010_t1 | 0 | 18.3 / 18.6 | 11.9 | 17.8 | cheaper 2^0.4 |
| rec11_s011_t6 | 0 | 17.9 / 19.4 | 12.8 | 19.9 | dearer 2^2.0 |
| rec11_s012_t4 | 0 | 19.8 / 16.7 | 12.8 | 19.8 | dearer 2^3.1 |
| rec11_s013_t4 | 0 | 18.0 / 14.6 | 12.6 | 18.9 | dearer 2^4.3 |
| rec11_s014_t1 | 0 | 19.3 / 15.5 | 12.6 | 18.6 | dearer 2^3.1 |
| rec11_s015_t1 | 0 | 19.3 / 18.2 | 12.2 | 18.5 | dearer 2^0.3 |
| rec11_s016_t6 | 0 | 17.8 / 17.1 | 12.1 | 18.6 | dearer 2^1.4 |
| rec11_s017_t1 | 0 | 18.3 / 15.6 | 12.4 | 19.6 | dearer 2^4.1 |
| rec11_s018_t5 | 0 | 16.0 / 16.5 | 12.8 | 18.7 | dearer 2^2.7 |
| rec11_s019_t0 | 0 | 19.1 / 20.2 | 12.6 | 18.9 | cheaper 2^0.3 |
| rplant_s000 | 1, planted found by all | 18.0 / 19.8 | 13.9 | 21.1 | dearer 2^3.1 |
| rplant_s001 | 1, planted found by all | 21.3 / 19.6 | 13.9 | 21.2 | dearer 2^1.6 |
| rplant_s002 | 2, planted found by all | 20.2 / 18.4 | 14.5 | 21.5 | dearer 2^3.1 |
| rplant_s003 | 2, planted found by all | 16.8 / 16.6 | 14.4 | 21.2 | dearer 2^4.6 |
| rplant_s004 | 1, planted found by all | 15.8 / 14.5 | 13.9 | 20.8 | dearer 2^6.3 |
| bplant tau#0 | 1, planted found by all | 18.3 / 21.0 | 13.9 | 20.7 | dearer 2^2.4 |
| bplant tau#1 | 1, planted found by all | 19.3 / 19.6 | 13.8 | 21.0 | dearer 2^1.7 |
| bplant tau#2 | 1, planted found by all | 18.3 / 23.8 | 13.8 | 20.8 | dearer 2^2.5 |
| bplant tau#3 | 1, planted found by all | 21.1 / 22.9 | 13.9 | 20.6 | cheaper 2^0.5 |
| bplant tau#4 | 1, planted found by all | 17.5 / 20.4 | 13.9 | 20.3 | dearer 2^2.8 |
| bplant tau#5 | 1, planted found by all | 17.3 / 19.9 | 13.8 | 20.4 | dearer 2^3.0 |
| bplant tau#6 | 1, planted found by all | 19.1 / 21.3 | 13.9 | 20.4 | dearer 2^1.3 |

Tally (COMPUTED): the solver is dearer on 18 of 23 real systems and on 11 of 12 plants. Where it is cheaper, it wins by
at most 2^2.3, and only where the cheaper DFS costs 2^18.3 or more.

## Leads (GUESS, not tested)

- **Portfolio:** an oracle choice of DFS or solver per system is worth at most +0.13 bit on X2. A real chooser, for
  example one that predicts DFS cost from the (2)-automaton count, gets less. This is not worth building for X2.
- **kissat's sweeping:** it kills every real system without main-solver conflicts. A hand-written sweep or probe on the
  E3 circuit might prune condition (3) earlier than the DFS, which checks (3) only at the leaves because of the
  rotation by 8. Its cost is unknown, and the X2 ceiling is still +0.966 bit.

## Could not test (stated plainly)

- **Instruction counts:** valgrind and perf are not installed in WSL. Cycles from CPU time are used instead, and IPC
  is unknown.
- **kissat and CaDiCaL in-process:** no library or headers are installed; only libcryptominisat5.so exists. A custom
  lean CDCL was not built.
- **DFS timing:** the DFS was not implemented in C and timed. Its cost is the stack code's DERIVED op weights.
- **GPU:** not used. CDCL solvers are CPU-only.
- **Timing noise:** per-instance CLI splits carry noise of about 0.3 ms. The means over 270 steps are unclipped, so
  the noise averages out.

## Tool problems

- No call was refused or stopped. No process was killed.
- Measurement bug (mine): CMS 5.11.21 rejects `--printsol 0`, so the first CMS timing split was invalid (status
  mismatch on every run). It was re-run with `--verb 0` (e3sat_time_cms_out.txt).
- Cosmetic: that file's last-but-one line reads "exit True" because of a shell-quoting slip. The run itself completed.

## Files

| file | what it is |
|---|---|
| e3sat.py, e3sat_out.txt | main driver: systems, encodings, all solvers, DFS, correctness, counters, first ledger |
| e3sat_time.py, e3sat_time_out.txt, e3sat_time_cms_out.txt, time_split*.json | parse vs solve CPU split |
| cms_inproc.py, cms_inproc_out.txt, cms_inproc.json | in-process CMS, fresh and incremental |
| ledger.py, ledger_out.txt | every measure on the X2 ledger, plus the V4p/V4s check |
| verdicts.py, verdicts_out.txt | per-instance lines |
| ablate.py, ablate_out.txt | which kissat technique refutes |
| e3solve2_rerun.txt | record joint DFS reproduced, 2^15.91 nodes and 2^19.26 ops |
| test_gen.py, test_gen_out.txt | SAT plant generator check |
| diag.py, diag_out.txt, diag_plant.py, test_bplant.py | xdp+ weights per tau, kissat counters, algebraic plant diagnosis |
| systems.json, cnf/ | all systems and counters; CNF/XNF of the 23 + 12 main systems |
| probe_*.sh | environment probes |
