# Lever keccak_slack: LS1 Keccak round polarity slack (2026-10-15)

## Result

| row | step (straight line) | BSTEP | time_log2 filed | time_log2 new | delta |
|---|---|---|---|---|---|
| LS1R7 (r7) | 35,517 -> **34,771** (-746, -2.10%) | 35,537 -> 34,791 | 124.28591 | **124.25619** | **-0.02972** |
| LS1R8b (r8) | 42,482 -> **41,569** (-913, -2.15%) | 42,502 -> 41,589 | 124.34902 | **124.31855** | **-0.03047** |

Memory term stays 0 on both rows (r7 max 1,041,770 B; r8 max 1,029,407 B, margin 19,169 B).

Arithmetic: N = Tb*BSTEP + replay + rare + PRE, with Tb, replay and rare unchanged (they do not depend on the step).
r7: main share 0.97128, so N_new/N_old = 1 - 0.97128*746/35,537 = 0.97961, log2 = -0.02972. r8: the same with 913/42,502.
The exact values come from the filed ledger programs with only the counts changed: `cert7_new.py` and `cert8b_new.py`, run twice each, outputs identical (`c7_run1/2.txt`, `c8_run1/2.txt`):
- r7: XOR 25,200 + AND 4,098 + OR 4,158 + NOT 1,315 = 34,771; certificate `time_log2 = 124.25619`
- r8: XOR 30,174 + AND 4,913 + OR 4,943 + NOT 1,539 = 41,569; certificate `time_log2 = 124.31855`

## Where the "254 extra ops" came from (per-round counts from gen.c)

I added a tag to every node in the generator (`genp.c`) and counted the live ops after DCE for each round. Trial 192 reproduces the filed prog.bin (sha256 ed4af487...).

| r7 round | C | D | apply | chi AND/OR | extra XOR (two-op terms) | chi out XOR | NOT | total |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 0 | 41 | 0 | 41 |
| 1 | 371 | 268 | 645 | 1,600 | 320 | 1,600 | 220 | 5,024 |
| 2 | 1,280 | 320 | 1,600 | 1,600 | 320 | 1,600 | 217 | 6,937 |
| 3 | 1,280 | 320 | 1,600 | 1,600 | 320 | 1,600 | 228 | 6,948 |
| 4 | 1,280 | 320 | 1,600 | 1,600 | 320 | 1,600 | 227 | 6,947 |
| 5 | 1,280 | 320 | 1,600 | 1,600 | 320 | 1,600 | 246 | 6,966 |
| 6 (pruned) | 1,280 | 320 | 320 | 256 | 54 | 256 | 40 | 2,526 |

(r8 is the same plus a round of 6,965.) A full round is 6,720 + its NOT count. The floor of 1 extra op per chi row (odd 5-cycle) is the 320 two-op terms. The slack is **all row-complement NOTs, 217 to 246 per full round**, not DCE or bookkeeping. The 6,974 in EDGE_AUDIT was r7 minus r6, which includes the change in the pruned round. The NOT count matches the random-polarity expectation: a row costs 1, 2 or 3 extras with probability 10/32, 20/32 and 2/32, a mean of 1.75 (observed 1.68).

Why: each plane's polarity (physical = logical XOR p) is forced. With AND/OR/XOR only, every node outputs 0 on an all-zero physical input, so p equals the u=0 Keccak value unless a NOT is placed somewhere. The generator picked each row's complements greedily from whatever polarity came in.

## What changed (generator only; same ISA, same ops, same registers)

1. **Theta NOTs (polarity plan).** A NOT on a column parity C[x][z] costs 1 and flips 10 chi inputs. A NOT on D[x][z] costs 1 and flips 5 inputs, one in each of 5 rows. Per round, simulated annealing chooses the set that minimises the sum over rows of min_s(|s| + mismatched terms) plus the theta NOTs. The predicted row cost matched the built count exactly in every round (e.g. 1,987 predicted = 1,987 built).
2. **Free output polarity of the two-op term.** The term a AND NOT b with mixed operand polarity can be built as A XOR (A AND B), polarity 0, or as (NOT A) OR B, polarity 1, both 2 ops. Every row has at least one such term, so about 320 planes per round get a polarity choice at no cost. Each one flips 11 chi inputs of the next round through theta. The annealing of round r+1 sets these bits together with its theta NOTs. This needs a multi-pass build: pass k fixes round k's decisions and the bits of round k-1, then the next pass rebuilds.
3. **Round 1** (linear inputs, where forms are deduplicated): a greedy search over C/D complements, keeping each one only if it lowers the real built op count of rounds 0..1 (-57 ops).
4. Constant selection: rerunning the 512-trial search with the plan gives at most 2 ops (best trial 468: 34,975 against 34,977 for trial 192 at 400k iterations). So trial 192 is kept and the filed constants do not change.

Effect per round (r7 final): rounds 2-5 are 6,793 / 6,802 / 6,811 / 6,810 (NOTs about 45 plus theta NOTs about 100, against 217-246). Round 1 is 4,945 (was 5,024). The pruned round is 2,441 (was 2,526).

Progression on r7 (annealing iterations per round): theta NOTs only 35,207 (400k) / 35,186 (4M). With free polarity: 34,977 (400k), 34,909 (2M), 34,854 (6M). Adding round-1 greedy at 20M gives **34,771** (the shipped setting).

## Minutes-scale checks (every run done twice; all deterministic)

- Original gen.c with `gen 1 192` reproduces the filed r7 prog.bin (sha256 ed4af487...) and 35,517.
- Final r7 (`genr2.c`, 20M, optmode 3): runs 1 and 2 are identical, prog.bin sha256 834b367c...acfaa, 34,771. selftest (`selftest7.c`: 4 batches x 256 trails x 4 chained steps against the lane-wise Keccak reference) gives 0 mismatches for both seeds (default and 0x1234567).
- Final r8: runs 1 and 2 are identical, sha256 3df61825...ff8d, 41,569. selftest8 gives 0 mismatches for both seeds.
- Slim shipping candidate `genS.c` (no instrumentation, phi/mixed flags bit-packed, OPTIT 20M default) writes byte-identical prog.bin for r7 and r8. size(1): r7 text 27,250 + data 8 + bss 692,960 = 720,218 (MAXN 37,888); r8 text 27,058 + data 8 + bss 761,728 = 788,794 (MAXN 45,312). VmHWM 589,824 B (r7) and 638,976 B (r8). Generator wall time 22-43 s.
- Registers: 2,181 used, max live 1,925, unchanged (limit 2,192 declared).
- Ledger programs: run twice each, outputs identical.

## Premises and sensitivity

- No new premise on the search side: the op counts are counted by the generator and checked by selftest. Tb, replay, rare ops and the success bound are unchanged.
- Preprocessing: one generator run. Bound: at most 1 + 3*640 + (NROUNDS-1) builds at 2^32 each (the filed per-build bound), plus 5-6 annealing runs of 20M iterations at 2^8 ops or fewer each. That is under 2^43, entered as PRE = 2^43 (declared 33 for r7, 32 for r8). Share of N about 1e-28, so the score effect is 0.
- Memory: the r8 preprocessing term is the binding one (image + 32 KiB stack + 5*LINE = 1,029,407, margin 19,169 B). Any further growth of the generator's static arrays on r8 must stay within that margin. The non-bit-packed version (975,862 B image) would have exceeded 2^20.
- Sensitivity of the gain: each 100 ops per step is 0.0040 bit (r7) or 0.0033 bit (r8). The remaining gap to the structural floor is about 73-91 ops per full round plus round 1 and the pruned round, under 0.016 bit on r7 if all of it were removed. Longer annealing gave diminishing returns: 2M to 6M gained 55 ops, 6M to 20M plus round-1 greedy gained 83.
- Transfer: the same generator family is used by LS1C2 (r6, 3 full rounds); about -0.025 to -0.03 bit expected there. Not built.

## What a package rebuild needs (per row; nothing filed or staged was touched)

1. Replace `gen.c` with `genS.c` (sha256 956fc2b1...adcaca, 26,458 B), with `#define NR` / MAXN set per track (r7: NR 7, MAXN 37888; r8: NR 8, MAXN 45312). Run it as `gen 1 192 3` (trial 192, polarity plan on), not `gen 512`. Code sizes in the note come from this shipped source and size(1).
2. New outputs: `out_r7/` and `out_r8/` (prog.bin, meta.txt, ledger.txt). **PD changes** (r7 pd 7fffff7d7fff7f7e 0000000200000000 0000008200000000 0, r8 pd 7fffffffffff7ff6 0 0 0), so data.bin must be rebuilt from meta.txt (`other8.py` data_image). other.bin should be unchanged, but check that it does not embed the straight-line length (the r8 note gives "42,497 instructions" for prog.bin + pf.bin; new values 34,786 / 41,584).
3. Ledger: the new counts above. GEN_IMAGE = 720,218 / 788,794. GEN_PEAK needs a 5-run VmHWM bound (only 1-2 runs done; not binding, because image + stack dominates). PRE = 2^43 with the build-count derivation. Memory-table text: 34,786 / 41,584 instructions x 5 B.
4. Proof section 3.2 (row complements) gets a short paragraph on items 1-3 above: polarity forced by NOT placement, theta NOTs, (NOT A) OR B as the polarity-1 form of the two-op term, multi-pass annealing, round-1 greedy. Correctness is by the selftest.
5. Re-run on the new prog.bin: kat/check_ref (reference side; unchanged), selftest (done), and hrand_test / proj_test (F changes by the new PD constant; these were not re-run here). Also the 16 KiB stack-limit run of the generator, which was not run.
6. Intake: the source grows by about 8 KB (26.5 KB against about 18 KB); check the 64 KiB experiment-source total per package.

Files: `genS.c` (candidate), `genr2.c` (instrumented, same output), `genp.c` (per-round census of the filed generator), `cert7_new.py`, `cert8b_new.py`, `c7_run*.txt`, `c8_run*.txt`, `final_r7/r8_stdout.txt`, `trials_a.txt`, `out_r7/`, `out_r8/`.
