# cycle_solver / reorder: is there a better design with a cheap exact cycle solver? (2026-10-09)

**Question.** Inside the k = 1 census (T1 = v13 free; designs from split_e3/designs.pkl), is there a design whose cyclic component is shorter, or friendlier to rotations, so that an exact solver well below 2^16.4 ops exists?

**Verdict: NO.** Reordering cannot reach the bar.
- All the shortest designs are the same 22-equation cycle, cut at different places. They cost the same 43 ops per candidate g and read the same 14 parameter words.
- No design has a narrower rotation spread than offsets {0,4,...,28}.
- The one exact saving found prices at **83.83** (from 84.61): stop each candidate as soon as K1.a1 is known, because the T1 filter fixes 13 bits of K1.a1.
- The bar is 2^29.37 ops per usable E1 trial. Exhaustive work is 2^44.95 candidates per usable trial, so even 1 op per candidate misses the bar by 15.6 bits.

Labels: COMPUTED = run here; DERIVED = arithmetic on computed numbers; GUESS = not established.

## 1. Census of the 3,234 designs (offsets.py, params.py, opscount.py)
- **Coverage (COMPUTED).** 3,227 designs map onto the exact relation model (split_e3/ev.py, 78 relations, T1 in K1.a1). The other 7 use the trial word Y2 and were skipped.
- **Loop length and op count (COMPUTED).** The shortest loops are 21 equations (408 designs) and 22 equations (42), at 43 and 46 ops per candidate. Everything else is 32 to 60 equations and at least 63 ops.
- **The 408 shortest designs are one cycle (COMPUTED).**
  - Same 14 parameters: K1.b1, S1, S11, S12, S6, X0, X13, X4, X5, X8, X9, Y4, Y9, w6.
  - Same 22 core words, through C0 (all of it), D1 (a1, d1, c1, X1, X12), K1 (a1; w2, w3) and C1 (all of it).
  - Only 9 core words can serve as the single loop word: C0.b1, Y8, C0.c1, C0.d1, C1.a1, C1.d1, C1.c1, C1.b1, Y13. Each gives 21 equations and 43 ops (t1abort_out.txt).
  - From the other 13 core words, propagation stalls: each sits between two equations that each have a second unknown core word.
  - The front design (g = C0.b1) is already optimal in this census.
- **Rotation offsets (COMPUTED).**
  - For each loop word W, O(W) is the set of r such that bit i of W reads bit i - r of g.
  - Arc width of the check's offset set: 28 in 450 designs, 29 in 105, 30 in 1,252 and 31 in 1,420. **No design is below 28 of 32.**
  - The best 450 have exactly {0,4,...,28}. Only rotations by 16, 12 and 8 act on loop words; the 7/25 rotations act on constants only. Every other design also has odd offsets (22 to 32 offsets).
  - The first merge of two different offsets is G's own second-half d update.
    - Cut at C1.a1: `Y1 = ROL8(Y13 ^ ROL24(C1.d1))` merges offsets 16 and 8 (Y13 = ror8(C1.d1 ^ Y1)).
    - Cut at C0.b1: `Y12 = C0.c1 - Y8` merges offsets 0 and 12.
    - The d1 and a2 of the same G call both depend on the loop word. That is structural, not a choice of cut.
- **Parameters (COMPUTED).**
  - Every design reads at least 8 B-dependent parameter words, entering at different loop steps (histogram: 8 to 18).
  - The longest prefix of the loop free of B is 4 steps.
  - So a one-time 2^32 table h(g) = p, which would need B to enter at a single point, does not exist in any design.

## 2. The T1 filter, and the one exact saving (t1abort.py)
- **What the filter fixes (COMPUTED).** T1 = K1.a1 ^ rol16(K1.d1), and K1.d1 does not depend on the loop word. So 1 <= T1 < 2^19 fixes exactly the top 13 bits of K1.a1, by XOR with no carry.
- **Why the scan cannot be limited to 2^19 values (COMPUTED).** That would need K1.a1 (or w2, C0.a1, w3) as the loop word, and none of them can be one.
  - K1.a1's equations are `w2 = K1.a1 + 566d1711`, `w3 = S1 - K1.a1 - K1.b1` and T1.
  - The next steps are `X12 ^ rol16(C0.d1) ^ C0.a1 = 0` and `C1.a1 = X1 + X5 + w3`. Each has two unknown core words.
- **Early abort (COMPUTED op counts, DERIVED price).**
  - Cut at C0.b1: K1.a1 is known after 24 of the 43 ops, so the candidate can stop there with a 13-bit test.
  - Per usable trial: 2^12.95 × 2^32 × (24 + 1 + 19 × 2^-13) = 2^49.59 ops.
  - Total: 2^92.57 ops, a score of **83.83**, against 84.61 for the plain scan.
  - Not built or validated separately (a gain of 0.78 bits).

## 3. Why no cheap exact solver exists for this cycle (sepbound.py; DERIVED for the named orders, GUESS for all solvers)
- **Position order (Sol's D4 §7.2 carry graph).** It works when every loop word has one offset. Here a check bit at position i reads g at i, i-4, ..., i-28, so the state must hold the g bits of an arc of width 28, plus 19 to 20 carry bits from the 13 additions that read loop words. That is at least 2^28 states per position, already above a 2^32 scan at 43 ops.
- **Slice order (positions mod 4, allowed because every offset is a multiple of 4).** Without carries, the cycle would split into four independent 8-bit problems. With carries, the state must hold the carries crossing the nibble boundaries: at least 7 × 19 = 133 bits.
- **Earlier results agree.** split_e3/cone.py: every check bit reads all 32 g bits. split_e3/loopw.py: no loop word. mitm2.py: no split.
- **Blocking structure.** The equation that blocks this is G's second-half d update in C1 and in C0 (ROR8 of d1 XOR a2). With it come the 16- and 12-bit first-half rotations on the same loop path, which spread the offsets over all 8 nibbles.
- **Not proved.** That no solver of any kind can reach 2^16.4 (GUESS). SAT was not timed on this 32-bit cycle.

## 4. Best design and its measured solve cost, validated
- **Solver.** The best design is the 21-equation cycle at 43 ops per candidate, here cut at **C1.a1** (gen_cpu.py → cpu_scan.c). It uses the front design's free words, so the split_e3/inst_2.txt parameter lines feed it unchanged.
- **Method.** It scans all 2^32 values of C1.a1. On each root it reports the C0.b1 value from the same pass, so the full solution can be compared with the GPU reference cut at C0.b1 (split_e3/roots_2.txt, solve.cu).
- **Instances.** 200 real instances from the generator: 25 per E3 target × 8 targets, including the 8 generating points.
- **Result (COMPUTED, compare.py, compare_out.txt).**
  - **200 of 200 root sets are identical** to the GPU reference, with 0 mismatches and no roots missed.
  - All 204 roots were rebuilt through all 78 relations and hold.
  - The generating C0.b1 was found in 8 of 8 generator instances.
  - Root-count histogram: 0:68, 1:79, 2:40, 3:8, 4:4, 5:1.
- **Ops per solve (COMPUTED).** 43 × 2^32 = 2^37.43, mean = max, because the scan does not stop early. One table-free pass, no lookups. The parameter setup is the 46 pre-equations per proposal, negligible next to the scan.
- **Time (COMPUTED).** 4.4 s per solve for one process on the CPU, vectorised (gcc -O3 -march=native). It was about 10 s each with 3 processes in parallel.

## 5. Not done
- The census is the randomised greedy sample of split_e3 (881 minimal sets). An exhaustive enumeration of all k = 1 bases was not run.
- T1-fixed k = 2 designs: kseq.py already shows no one-word order (a coupled 64-bit system). Their cycles were not offset-analysed here.
- No SAT/CDCL timing of the 32-bit cycle, and no treewidth computation for other variable orders (networkx is not installed).
- The early-abort solver of §2 was priced but not built.
