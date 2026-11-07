## 6. Ledger: worst-case operation count (primitive operations; `C(@@R@@) = @@C@@`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, and the statements of `main` outside the counters; `T_off` = the offline bound of section 6.2. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = @@K@@`, and `time_log2 = ceil_5(log2(N_max / @@C@@))`.

Every stage is charged by the rules of section 4.2 at the statement that executes it. The charges below are produced by the cost model of Appendix B (`costmodel.py`, `costmodel_e.py`): it ports the control flow of the shipped sources statement by statement and reads the leaf charges of the transform passes from `ntt_kern.h` and `ntt_a3.h`; section 6.1 validates it against the counters of the program at r = 3, 4, 5. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(@@AEXP@@-1)` elements (`ntt_init(@@AEXP@@)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | @@S_INIT@@ |
| setup | the line (`line_setup`) | @@S_LINE@@ |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 91, one allocation | @@S_A@@ |
| B (per trial) | `@@H@@` points, each with two evaluations of `F` (at `c + zeta^i` and `c - zeta^i`) at `C(@@R@@) = @@C@@` operations each, the loop work around them, the inverse transform of size `@@H@@`, the normalisation | @@S_B@@ |
| C (per trial) | `S^((p-1)/2) mod g`: Newton reciprocal, `@@STEPS@@` squaring steps, 45 multiplications by `S` (section 4.3) | @@S_C@@ |
| D (per trial) | half-gcd of `(g, R - 1)` (section 4.4) | @@S_D@@ |
| E (per trial, cap) | `Z = @@Z@@` rounds at degree `DMAX = @@DMAX@@` (below) | @@S_E@@ |
| F (per trial) | square root, back-map (below) | @@S_F@@ |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * @@C@@ + 32` | @@S_G@@ |
| main, per trial | the test `trials > MAXTR`, `trials++`, the stores of `t_centre`, `t_deg`, `t_gcd` and the arguments of the report line: at most 12 | @@S_X@@ |
| plan_invN misses | one per distinct plan size (@@NSET@@ sizes) | @@S_MISS@@ |
| H | canonical encoding of the output (6 conversions, 384 digits) | @@S_H@@ |
| I | report formatting (`400 * 8,192`), `REPORT_LOOPS`, entry, one `write`, one `exit_group` | @@S_I@@ |
| offline | section 6.2 | @@OFFLINE_BOUND@@ |
| **N_max** | `T_fixed + @@K@@ * T_trial + T_off` | **@@N_BOUND@@** |

`N_max = @@N_BOUND@@` operations `= @@UNITS@@` units, `log2(N_max / @@C@@) = @@TIME_LOG2_EXACT@@`, claimed as `@@TIME_LOG2@@` (rounded up at five decimals).

Stage B charges each of the `@@N2@@` evaluations of `F` as one reduced permutation, `C(@@R@@) = 216 + 21 * @@R@@ = @@C@@` operations, although a line evaluation is a strict subset of the work of a reference permutation; the loop work around the evaluations is charged on top (section 3).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping) and runs a round for each pass of the loop of `split_find_root_capped` until `deg G = 1` or `Z` rounds have been made. A round at current degree `d` costs `R(d)`: the coin draw 91 and one negation; the Taylor shift (`taylor_shift`: two allocations, three loops of `d + 1` steps with their loads, stores and loop control, the schoolbook product of two polynomials of `d + 1` coefficients, two inversions and one exponentiation by `d`); `Z^((p-1)/2) mod G` by schoolbook square-and-multiply (`pow_half`: 253 modular squarings, each `2d + 3 d (d-1)/2 + 2 d^2` field operations and an allocation and a free, and 45 multiplications by `Z`, each `2d` field operations; because `bound_mem_since` adds 9 operations per field operation, every field operation of `pow_half` is charged 10); two classical gcds (`gcd_cl`: at most `d` outer iterations, each with one inversion charged `@@INV@@` operations (the 330 field operations of `x^(p-2)` and the 2,310 control operations of its bit loop), at most `2d + 1` division steps, each charged at the largest row length); the copies, the tests and the frees. The cap charges every one of the `Z` rounds at `d = DMAX`, because `R(d)` is non-decreasing in `d`: `R(16) = @@R16@@`, of which `pow_half` is @@POWH16@@, the Taylor shift @@TAY16@@ and the two gcds @@GCD16@@ each. All allocations are charged at `L <= 16` live blocks (550 per allocation, 105 per free): in stage E the live blocks are the twiddle table, `G`, `S`, `S - 1`, `S + 1` and the two gcd arrays (at most 8), and at most four more inside the Taylor shift or the modular squaring. `E_cap = 1,000 + 3 + @@Z@@ * R(16) + 114 = @@S_E@@`.

Stage F. After the stage bookkeeping (1,000), `CTL(12000)` for the Tonelli-Shanks control and `CTL(2)`, the field operations of stage F are charged 10 each (`bound_mem_since`): `fp_pow` by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most @@F_ARITH@@ field operations, so `F = 13,002 + 10 * @@F_ARITH@@ = @@S_F@@`.

Every figure above is an upper bound that the program meets or exceeds when the Euclidean sequences of stage D are normal (declared in `H1-charging-rules`): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are those of the shipped source under the rules of section 4.2. No figure is measured on a run at r = @@R@@ (section 10.3).

### 6.1 Ledger recomputation and validation

The sum of section 6 is recomputed by the following script (standard library only); the stage rows come from the cost model of Appendix B, run on the files of Appendix A.

```python
from math import log2, ceil
K, C = @@K@@, @@C@@
fixed = [@@L_FIXED@@]   # init, setup, plan_invN misses, stage H, stage I
trial = [@@L_TRIAL@@]   # stages A, B, C, D, E (cap), F, G, main
offline = @@OFFLINE_BOUND_RAW@@
N = sum(fixed) + K * sum(trial) + offline
print('N =', format(N, ','))
print('units =', round(N / C, 1))
print('time_log2 =', '%.5f' % (ceil(log2(N / C) * 100000 - 1e-6) / 100000))
```

Validation of the cost model against the counters of the program (algorithmic totals; the executed runs at r = 3, 4, 5 had fixed centres and a different stage A, and their thread charges are excluded): the model is above the measured total in every row, and its heap peak equals the measured heap peak at r = 3 and r = 5 and is 64 bytes below it at r = 4 (the arena rule of section 7 adds 704 bytes for that).

| run | model total | measured total | model - measured | slack (bits) | model heap peak | measured heap peak |
|---|---:|---:|---:|---:|---:|---:|
@@VAL_ROWS@@

The last row is the shipped program itself (coin centre, single thread) at `RR = 3`, one trial with a centre that gave `deg G = 2`, stage E with 3 rounds at degree 2 (the model charges stage E for exactly that shape here, and stage F at its worst case); its counters are in section 10.1. For stage E at the cap, `test_e.c` (Appendix C) runs `split_find_root_capped` on 90 synthetic products of distinct linear factors (degrees 2 to 16, six per degree) and compares the counters with `3 + rounds * R(d) + 10 + 105 + 4`: no run exceeds it, and the largest ratio measured/model is @@E_RATIO@@. The coin draw measures 91 operations, as charged.

### 6.2 Offline derivation of the literals (preprocessing)

The program text contains literals that are derived from the organizer's constants and from `p` before the program is compiled: the 192 round constants and 9 MDS entries of `pallas_consts.h` in Montgomery form, `R^2 mod p`, `R mod p`, `2^65` and `5^q` in Montgomery form, the exponents `q`, `(q+1)/2`, `(p-1)/2`, `p - 2` and the integer `e = (4(p-1)+1)/5` (as 64-bit limbs; `E5INV` in `line.c`). There is no search and no choice: each literal is the value of one closed formula in the organizer's constants. The Montgomery form of a constant `x` is `x * 2^256 mod p`, one modular multiplication plus parsing 64 hexadecimal digits; `5^q` is a square-and-multiply of 221 squarings and at most 221 multiplications; the exponents are shifts and subtractions of `p`. Each literal costs at most 4,000 word operations, there are at most 250 literals: @@OFFLINE_BOUND@@ operations in all. This bound is inside `N_max` and is the declared `preprocessing_log2 = @@PREP_LOG2@@` (`2^@@PREP_LOG2@@ = 1,048,576 >= @@OFFLINE_BOUND@@`). The program reads no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the program re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

