# b3-heur: simulated annealing over the E3 class choice, scored by the exact counter tool

Folder `research\newpaths\untried\b3-heur`. Written 2026-10-10 (clock read at 00:06 and 00:26 MDT). This is our own
team's research.
- Nothing was filed, submitted or posted. No yukon command was run, no network was used, and `.key` was not opened.
- One CPU process ran at a time, and every run took under 10 minutes.
- I stopped no process. Each one I started ended on its own.

Grid cells: free ctr/const/cv x heur, layer r1d x heur. Labels: COMPUTED (run here), DERIVED (arithmetic from computed
or cited numbers), GUESS.

## Answer

**Dead for the class choice, closed with numbers.** I ran a simulated annealer: no gradient, random 1-3 bit moves, a
temperature schedule and restarts. It was scored by the team's exact counter `pair_calc_sub` and evaluated 5,794
distinct points in 540 s (COMPUTED). It found nothing better than the best known value under the same evaluator:

Values in the table are COMPUTED; the gain column is DERIVED.

| objective (rate per member of an E3 class, same evaluator) | best known | best found here | gain |
|---|---:|---:|---:|
| S: the six front-line outcomes of beta* (the rate behind H1') | 67,633,152 | 67,633,152 | 0.000 bit |
| total over every beta* row (the objective of the stack's greedy scan) | 76,161,024 | 76,161,024 | 0 |
| any other class (eta not 830303cf) | none known | eta 830503cf: S 15,073,280, total 21,196,800 | -2.17 bits on S |

The obstruction is stronger than GAPS item 7's "no gradient": on the front-line objective there is no variance at all.
- **S takes one value, 67,633,152, everywhere it was measured** (COMPUTED). That covers the 2,499 class members the
  annealer visited (0.48% of 2^19) and all 498 prior cubes of the stack scan (19 down to 0 free bits). Each of the six
  S rows is also constant on its own across the 498 cubes. Max equals mean, so a heuristic over members or sub-cubes
  has nothing to gain.
- **What does vary is worth nothing.** The total depends only on e1 bits 2, 21 and 26 on all 2,499 members, which is
  the greedy's structure. 1,300 members reach 76,161,024 and none goes higher (COMPUTED). The varying part is the
  seven tau x5060a0 rows. Per passing outer step they carry at least 34.7x (5.12 bits) less mass than S (DERIVED,
  Section 3), so the front line drops them.
- **Other classes are much worse.** The annealer visited 1,029 other classes (eta values, 8 to 23 fixed bits).
  1,027 had an exact beta* rate of 0 at every member visited. The other two are far below (COMPUTED):
  - 830503cf: S 15,073,280, total up to 21,196,800;
  - 830303d7: S 1,572,864 at 2 of 40 members.
  The front-line class is 4.49x (2.17 bits) ahead on S.

This cell does not move the front line (62.9459 filed, 62.7934 next; both cited from the brief).

## 1. The evaluator (COMPUTED reproduction)

- **Tool.** The team's counting binary `pair_calc_sub` (WSL Ubuntu, `~/hashsmash/pkg7_count/bin`, run read-only),
  with exactly the arguments of `counter_next\stack\run_cube.sh`:
  - pin H8: DY3 fdb77cfd, DY11 0a08818b, delta fffffff8, Y3 8127c181, Y11 7af77f38;
  - eta 830303cf, beta* 18b0e098 with k = 11;
  - filed rule A (S8) printed beside, and `-mode both`.
  My copy of the beta list and every output stay in this folder.
- **Reproduction.** On the class (cube 03cf8303/030c0303) all 30 OUTR lines match the stack's
  `cube_03cf8303_030c0303.out` (`diff`). That run took 1.76 s. One member (cube ffffffff/070c0307) takes 0.23 s.
- **Rates.** The rate of a member is the sum over rows j of L_j N_j / 2^64 (the normalisation of `scan_y4.py`, with
  0 free bits).
  - A cube's rate is the average of its members' rates (DERIVED: a cube's N_j is the sum over its members, divided by
    2^free). So no sub-cube beats the best member, and searching members covers every sub-cube.
  - S is the rows with tau 285020a0, 685020a0, 185020a0, 385020a0, 275020a0 and 175020a0 (eps 6e21be55). They were
    identified by their sum: on the class they total exactly 67,633,152, the map's Section 2.6 figure (DERIVED).
  - Adding 675020a0 (65,536) gives 67,698,688, the stack's "sub-class" rate.
- **Other classes.** For any e1, eta = ROR(e1 XOR (e1 + DY3), 16) is computed and passed, so e1 is a valid member of
  its own class. Off the front class the binary often reports `n3pos 0`, an exact zero. An example is kept in
  `member_b71d43bf_830303c9.out`: taus 95, passing 76, n3pos 0.

## 2. The heuristic and what it saw (COMPUTED)

Command: `heur.py 540 1 0.45`. Logs: `evals_s1.tsv`, `trace_s1.txt`, `analyze_out.txt`.

- **Phase A (243 s, 1,212 evaluations).** The search stayed inside the class: 19 free bits of e1 = Y3 + Y4. Y4 is an
  outer word on the counter path, so one member is enough.
  - Score: 64 log2 S + log2 total, so S comes first.
  - Temperature fell from 0.1 to 0.003.
  - After 150 evaluations without a new best it restarted, either at a random member or back at the best (8 restarts).
  - It found a 76,161,024 member (2f1c33e7) within its first 50 evaluations and never improved on it.
- **Phase B (297 s, 4,581 evaluations).** All 32 bits of e1 were free, so a flip of a class-fixed bit moves to
  another class.
  - Score: log2 total. Temperature fell from 1.0 to 0.01. There were 31 restarts, and a random restart lands in a
    random class.
  - It visited 1,029 classes other than 830303cf (3,295 points). 1,027 of them were exactly 0 at every member
    visited.
  - 830503cf: S was flat at 15,073,280 over the 52 members visited, and the total was 15,073,280 to 21,196,800.
  - 830303d7: 38 of 40 members were 0 and 2 had 1,572,864.
  - Nothing beat the front class.
- **The front class over both phases (2,499 members):**
  - S was 67,633,152 at all 2,499 and r7 was 67,698,688 at all 2,499.
  - The total was 67,698,688 when bit 21 = bit 26 (617 members), else 75,235,328 when bit 2 = 0 (582), else 76,161,024
    (1,300).
  - Every one of the 5,794 calls returned code 0. The binary ran for 536.8 s in total.

## 3. Why there is nothing to find (DERIVED from the numbers above and cited exact pass rates)

1. **Max = mean on S.** S has 1 distinct value over 2,499 + 498 points, and the average over any cube or member set
   is that value. So every class sub-choice gains 0.000 bit on the rate behind H1'.
2. **The varying rows are a loss under the filter.** Pass rates, all exact:
   - the seven beta* x5020a0 rows pass 2^-9.8132 of outer steps (STACK.md Section 1, computed there);
   - the 14 rows of cube 07ef8307/070c0307 pass 2^-7.53 (same source);
   - the six S rows pass 2^-9.9782 (map 2.7, Lemma F).

   Two comparisons follow.
   - **The x5060a0 rows alone.** At least 2^-7.53 - 2^-9.8132 = 0.004299 of outer steps can hold only an x5060a0
     success. Those steps hold at most those rows' mass at the best member, 76,161,024 - 67,698,688 = 8,462,336. That
     is at most 1.97e9 per passing step, against S's 67,633,152 x 2^9.9782 = 6.82e10: 34.7x, or 5.12 bits, less.
   - **All 14 rows at the best member.** 76,161,024 x 2^7.53 = 1.41e10 per passing step, 4.85x (2.28 bits) below S.
     This agrees with STACK.md 2.2 (V4q 72.59 against V4 70.99).

   Most of the front line's charge comes after the filter: opened clusters 53%, solver 19% and fills 18% (map 2.7). So
   mass per passing step is the right yardstick (GUESS that the pre-filter rows do not change this).
3. **The class is close to pinned by beta*'s rows.** Of 1,029 other classes, 1,027 were exactly 0 at every member
   visited, and the best is 2.17 bits below on S (values COMPUTED, gap DERIVED).
   - Likely reason (GUESS, not computed): STACK.md Section 1's condition (1) needs the addition differential
     0, eta -> G(tau) to be possible, and (3) needs G, ROR(eta XOR eps, 8) -> tau.
   - Both tie eta to beta*'s tau and eps. Flipping a class-fixed bit of e1 changes eta's carry pattern and breaks them.

**GUESS on why S is flat in the front class.** Y4 enters E3 only through f1 = ROR(y XOR g1, 12), because E = e1 + w8
is uniform. Under (1), g1 is fixed only on G's carry chain. So a flip of y can be offset by a flip of g1 that keeps f1,
(1) and (2), and for the six S taus apparently (3) as well. The flatness is a property of this class, not a law: in
830303d7, S is 0 at 38 members and 1,572,864 at 2 (COMPUTED). An exact closure for all 2^19 members would be a short
pure-math job (Sol) if wanted.

## 4. The other cells in this group (not run; reasons)

- **const x heur over the pinned constants (pins): OPEN.** One evaluation needs a pin that satisfies Fact P (a pin
  solver) and a per-beta E1 file. GAPS item 1 says 10 scored pins lack that file. That is not a seconds-per-point
  evaluator, so it does not fit this budget. GAPS item 1's exact ranking (max over beta of R_beta x 2^k) is the better
  tool there.
- **ctr x heur: not run.** The counter t is solved per trial (t = ROL(K0.d1,16) XOR K0.a1, map 2.5), so no free choice
  is left for a heuristic. The counter's only design choices are which word it prescribes (X9, GAPS Section 3) and the
  cube Q* (an E1-side class), and neither is a landscape search. DERIVED from the construction.
- **cv x heur: not run.** The rate does not depend on the instance (A11 over 8 instances, R18; cited from GAPS item 8),
  so a heuristic over chaining values or prefixes has a flat objective.
- **layer r1d x heur:** this run. E3's class is a round-1 diagonal object.

## 5. Files (this folder) and commands

- `one_cube.sh MASK VALUE`: the stack's call with outputs here (`base_*.out`), used for the reproduction.
- `one_member.sh E1 ETA`: one member of any class, full output kept.
- `rates.py`: the parser (S, r7 and total per cube). It also summarises the stack's prior cube outputs (read-only) into
  `prior_cubes.tsv` and `prior_cubes_summary.txt`.
- `rows_check.py` -> `rows_check_out.txt`: per-row values over the 498 prior cubes. Each S row has 1 value; the
  x5060a0 rows have 2-3 values.
- `heur.py SECONDS SEED SHARE`, run inside WSL as `wsl -d Ubuntu --exec python3 <path>/heur.py 540 1 0.45`. It writes
  `evals_s1.tsv` (every evaluation), `trace_s1.txt` and `run_s1.stdout` (empty). A 20 s smoke run (seed 99) was
  deleted after the check.
- `analyze.py evals_s1.tsv` -> `analyze_out.txt`.

## 6. Limits

- **Coverage of the class.** S's flatness is shown on 2,499 + 498 points, not on all 2^19 members. Sampling cannot
  exclude a rare member with a higher S. I GUESS that none exists, since every half-class and every sampled member has
  the same S.
- **Coverage of classes.** Phase B drew classes in proportion to their size, so only 9 small classes (21-23 fixed
  bits) were visited. In a class whose S varies by member (830303d7), a class marked 0 may still hold nonzero
  members that were not visited. A complete list of classes with a nonzero beta* rate would need an exact enumeration over
  the carry paths of e1 + DY3, which was not run.
- **The binary.** Rows were taken as the binary prints them. Its source
  (`research\pkg10\pkg\count\pair_calc_sub.c`) was not read.
- **Files read beyond those the brief names.** I needed them to find "the existing counter tools":
  - `counter_next\knobs\model.py` (named in GAPS item 4; it is a basis test, not a rate model);
  - `counter_next\stack\STACK.md` Sections 0-2.3 and 5-6;
  - `run_cube.sh`, `scan_y4.py`, `beta_star.lst` and the class cube output;
  - greps of `scan_y4.txt`, `scan_y4_q01b2.txt` and `cube_runs.log`.

  The 498 cube outputs were parsed by script, read-only. The reference `blake3.py` was not needed, because the
  evaluator is the counting binary, and it was not opened.

## Blocked

Nothing was refused or stopped. Every process I started ended on its own.
