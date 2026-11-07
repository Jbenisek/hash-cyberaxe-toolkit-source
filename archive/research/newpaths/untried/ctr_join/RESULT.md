# ctr x join (GAPS section 2, row 4): result

2026-10-10. Research only. Nothing filed or submitted, no yukon commands, no network.
Labels: COMPUTED = I ran it here; DERIVED = arithmetic from computed or cited numbers; GUESS.

## Verdict

**DEAD. 0 bits saved, on both ledgers (base and free).** DERIVED from the COMPUTED results below.

**Obstruction.** In every triangular (forward-computable) parametrization of the 55/63 two-round
system, the set of free words that reach the E1 key is exactly the set that reach the E3 key.
That holds at counter fixed, with t's low word free, and with all of t free, with w14 pinned or
free. It comes from an exhaustive z3 search over all triangular bases, checked against brute
force (COMPUTED). So no free word moves one side alone. An E1-side list that does not depend on
the outer step cannot exist, and neither can an E3-side list that leaves E1 alone.
Algebraically the two keys are independent (rank 7 of 7, COMPUTED on the linearized system), so
the decoupled directions do exist. They are reachable only through non-triangular solves.
Prescribing both keys needs 4 guessed 32-bit words at counter 1, about 2^128 by guess-and-check,
which is no better than the generic bound (section 4).

Bit level gives the same answer. coupling.py's two-sided split search, extended to t free in four
parametrizations, confirms **k = 0** split bits in each one (COMPUTED). The counter-fixed control
reproduces N17's 0 bits. Every screen-2 candidate bit is refuted by an observed cross move.

## 1. Definitions used

- Residual = key1 XOR key3 (coupling.py `World.diffs`), 128 bits. The pair collides iff key1 == key3.
- key1 depends only on T1 = (E1.a2, E1.b1, E1.d1). Moving the E1 inputs along the 2-word null
  direction (new E1.a1 and Y1; Y12, w5 and w12 compensate) changed key1 0 times in 20,000 moves
  (COMPUTED, `key_targets_check.py`).
- key3 depends on T3 = (E3.h1, E3.g1, E3.f1, E3.e2), a bijection of the E3 inputs (Y4, Y9, Y14,
  w8). Inverting it gave 0 mismatches in 20,000 (COMPUTED).
- t free. In model.py, T0 appears in one equation only (K0.d1). Freeing it just unlinks K0.a1
  from K0.d1, so w0 becomes free, and w0's only other use is C2's y input. T1 likewise frees w2
  (C0's x input; X0 in the filed solve order).
- Two-sided split: a triangular basis B = U + V + Fx in which
  - key1 depends on no V word, and key3 on no U word;
  - key1 depends on some U word, and key3 on some V word.

  Then for each Fx a list join over U x V tests |U|·|V| pairs for about |U| + |V| work.
- Cut with checks: up to c equations are left unsolved (c extra guessed words). Each check must
  hold no word that depends on both U and V, so that it can be joined on.
  - One-sided checks (cU, cV) filter a list; cross checks (cX) join two lists.
  - Gain = 32·min(|U|−cU, |V|−cV) − 32·cX − 1 bits (DERIVED). The search asked for gain > 0.

## 2. Structural search over all triangular bases (`struct_split.py`, z3): COMPUTED

The equation system is model.py's `system()`, imported unchanged (92 equations; 100 to 103 words).

**Encoding check.**
- On 247 random small systems × 3 modes, z3 matched brute force over every basis with 0
  mismatches. Brute-force positives were 125 / 159 / 161, so both outcomes were exercised.
- Positive controls: z3 accepts each filed basis (filed 8; +T0; +E1.d1; +E3.h1; +T0+T1).
  model.py's `propagate` agrees, and every word of these bases is classed "both".

| counter | w14 | split, no checks | some word moves E1 key only | some word moves E3 key only | split, ≤1 check, gain>0 | split, ≤2 checks, gain>0 |
|---|---|---|---|---|---|---|
| 0 (fixed) | pinned | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| 1 (T0 free) | pinned | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| 2 (T0,T1 free) | pinned | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| 0 | free | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| 1 | free | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| 2 | free | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |

Columns 4 and 5 together mean dep(key1) = dep(key3) in every triangular basis. Each query took
0.3 to 0.7 s without checks and 2 to 457 s with ≤2 checks. All results are proofs; none hit a
timeout.

**Sub-events (pairs).** I asked whether one E1-side word can be decoupled from one E3-side word
(9 × 8 pairs, no checks):

- **0 pairs of (E1 key word, E3 key word)** decouple, in all 6 configurations.
- Pairs that do decouple always involve an input-level word on at least one side, for example
  Y6|Y14, E1.d1|Y4 or Y12|E3.h1.
- t free opens more of these partial pairs: 10 → 36 → 41 pairs with w14 pinned (counter 0 → 1 → 2)
  and 18 → 43 → 44 with w14 free.
- None of them helps, because every residual bit needs the full key1 (all 3 words) and the full
  key3 (all 4).

## 3. Generic rank (`generic_rank.py`, linearized system, random coefficients mod 2^61−1): COMPUTED

| counter, w14 | dim of solution space | rank key1 | rank key3 | rank (key1,key3) | E3-fixed fibre dim / key1 rank on it | E1-fixed fibre dim / key3 rank on it |
|---|---|---|---|---|---|---|
| 0, pinned | 8 | 3 | 4 | 7 | 4 / 3 | 5 / 4 |
| 1, pinned | 9 | 3 | 4 | 7 | 5 / 3 | 6 / 4 |
| 2, pinned | 10 | 3 | 4 | 7 | 6 / 3 | 7 / 4 |
| 0, free | 9 | 3 | 4 | 7 | 5 / 3 | 6 / 4 |
| 1, free | 10 | 3 | 4 | 7 | 6 / 3 | 7 / 4 |
| 2, free | 11 | 3 | 4 | 7 | 7 / 3 | 8 / 4 |

So the decoupling exists algebraically: with E3 fixed, key1 can still move fully, and vice versa.
The obstruction is triangularity, not algebra. t free adds one fibre dimension per counter word,
but every new direction is again non-triangular (section 2).

## 4. Prescribe-both-keys route (`struct_split.py force`): COMPUTED

The algebraic decoupling suggests another route:

1. Pick key-word values with F1(k1) = F3(k3).
2. Solve the message system with all 7 key words prescribed.

Step 2 needs a basis that contains them. The table gives the minimal number of check equations
(guessed words) for that:

| counter, w14 | prescribe T3 (4 E3 key words) | prescribe T1 (3 E1 key words) | prescribe T1+T3 |
|---|---|---|---|
| 1, pinned | 2 | 1 | **4** (3 is UNSAT, proven in 198 s, not a timeout) |
| 2, free (most generous) | 1 | 1 | **3** (2 is UNSAT, proven in 23 s) |

Naive guess-and-check costs 2^(32·c) per message pair (DERIVED).
- At counter 1 (c = 4) that is 2^128, the same as the generic bound on the 128-bit residual.
- At counter 2 with w14 free (c = 3) it is 2^96. That configuration is not physical anyway:
  T1 < 2^22, and model.py treats w14 free only as a variant.

The front line is 62.9459 (cited from the project memory, not re-checked). So this route saves
nothing unless some solver for the 4-word non-triangular block beats guess-and-check by more than
65 bits (DERIVED: 128 − 62.95) just to tie the front line. No such solver was tried.

## 5. Bit level: coupling.py's split search with t free (`ctr_split_numeric.py`): COMPUTED

`build_t` is coupling.py's `World.build` with K0's and K1's d inputs set to T0 and T1. It was
checked against a full 2-round compression with counter t at W = 32: pins, all 9 E1/E3 inputs,
the half match, and residual == key1 XOR key3 each held in 200/200 random trials per mode, plus
40/40 per mode inside the run. The prescribed words were met in 200/200.

| mode (free words) | per-bit flip test: split candidates / 128 | screen 1 (1 base, 2 draws): partitions with k>0 | screen 2 (2 bases, 6 draws): partitions with k>0 | confirmed k (3 bases, 16 draws; top 24 candidates) | screen-2 candidate bits refuted by a cross move |
|---|---|---|---|---|---|
| C0: filed 8, t=0 (control; N17) | 0 | 5,920 of 6,561 | 7 | **0** | 7/7 |
| T0: filed 8 + T0 | 0 | 18,253 of 19,683 | 32 | **0** | 34/34 |
| T0T1: filed 8 + T0 + T1 | 0 | 55,788 of 59,049 | 85 | **0** | 85/85 |
| E1d1: filed 8 + E1.d1, T0 solved | 0 | 18,125 of 19,683 | 63 | **0** | 66/66 |
| E3h1: filed 8 + E3.h1, T0 solved | 0 | 18,218 of 19,683 | 49 | **0** | 49/49 |

**Reading the screens.**
- Screen 1 is mostly noise: with 2 draws a random bit fakes "never moved" often.
- Screen-2 survivors are biased, low-entropy difference bits.
- The last column replays the exact screen-2 candidates (same random stream), testing each bit
  with 8 bases × 32 draws per side. Every one of the 241 bits was moved by the wrong side at least
  once, so none of them is a split bit (`bit_kill_W32_replay.txt`).
- An independent screen-2 replicate (`bit_kill_W32.txt`) gave the same result: 205/205 refuted.

**W = 8 toy** (scaled rotations, as in coupling.py): confirmed k = 0 in all five modes, and
screen 2 was empty in all five (`numeric_W8_*.txt`).

**Word influence** (one word resampled, 24 draws each):
- Every free word moves key1 and key3 24/24, in every mode.
- T0 moves exactly Y6 (E1) and Y14 (E3), 24/24 each, and no other E1 or E3 input.
- T1 moves Y1 and Y6 (E1), and Y9, Y14 and w8 (E3).
- A prescribed E1.d1 or E3.h1 also moves only Y6 and Y14.

## 6. Why t does not help (DERIVED from 2 and 5)

The counter's only route into round 1 is one message word:
- T0 → w0 → C2's y input.
- T1 → w2 → C0's x input (and X0 → D0).

A word that enters a G call moves all four of its outputs, and each of C0, C1 and C2 outputs one
E1 input and one E3 input (Y12/Y4, Y1/Y9, Y6/Y14). So t alone always moves both sides. For
example, C2 with only w0 changing traces a single 32-bit curve in (Y6, Y14).

Re-solving t from a prescribed word (E1.d1 or E3.h1) does not help either. It just picks a
point on that curve.

Over all triangular bases, the dependency sets of the two keys stay equal (section 2). The extra
freedom shows up only as new non-triangular directions (section 3) and as input-level pair
decouplings that do not reach the keys.

## 7. Bits saved

| ledger | saving | basis |
|---|---|---|
| base | 0 bits | no triangular split exists; k = 0 at bit level; cuts of ≤2 checks give gain ≤ 0; the prescribe-both route costs 2^128 by guess-and-check at counter 1 |
| free (memory and precomputation free) | 0 bits | a table needs a key1 list that is independent of the outer step. Every outer word reaches key1, so the table index would be the whole outer step. |

All rows DERIVED.

## 8. What I could not test, or did not test

- **Other bases at bit level.** The bit-level split was searched numerically only in the five
  parametrizations above; the all-basis search is word level. A bit-level split inside some other
  triangular basis is not excluded. GUESS: unlikely, since in all five parametrizations every free
  word moves 116 to 128 of the 128 bits on each side.
- **Bigger cuts and smarter solves.** Cuts with 3 or more checks (with the gain condition) were not
  searched. Solves of non-triangular blocks that are cheaper than guess-and-check (a bitwise DFS of
  the e3solve kind, or a table) were not modelled. Each check is costed at a full 2^32.
- **T1's range.** The model treats T1 as a free 32-bit word. BLAKE3's input limit is 2^64 − 1 bytes
  and chunks are 1024 bytes, so t < 2^54 and T1 < 2^22 (DERIVED; I quoted the limit from memory and
  did not re-read the spec). Counter = 2 is therefore a generous model, and counter = 1 is the
  binding case.
- **The B event.** I did not read its definition; that was outside the brief. At word level no
  single E1 key word decouples from any single E3 key word, so any event built from key words is
  covered. An event on parts of words is covered only by the bit-level search in section 5.
- **Structural dependency.** The search uses the union rule. A structural non-dependency is exact;
  a structural dependency is generic and could cancel numerically. The numeric influence tables
  show no such cancellation for the five parametrizations.
- **Reading scope.** My first grep of GAPS.md printed all of its table lines. I used only
  section 2, row 4.
- **Write outside this folder.** Importing model.py made Python write
  `counter_next\knobs\__pycache__\model.cpython-314.pyc`, created 2026-10-09 23:57:53 by my first
  run. I deleted that file and the directory it created, so the knobs folder is back to its prior
  state. `job30_split\__pycache__` already existed (2026-10-08) and was not touched. To avoid this
  on reruns, set `PYTHONDONTWRITEBYTECODE=1`.
- **Refusals and limits.** No tool call was refused or stopped by the system. I stopped one of my
  own processes, PID 29784 (`struct_split.py checks`), at 00:17:28. It was on its last
  configuration (counter 2, w14 free, ≤2 checks), and stopping it kept every run under the
  20-minute cap. That configuration was rerun alone with an 18-minute z3 limit
  (`struct_split_checks_2_1.*`); the earlier lines are in `struct_split_checks_partial.txt`.
  The force query was run for counter 1 / w14 pinned and counter 2 / w14 free only, not for the
  other four configurations.

## 9. Files (all in this folder)

| file | what |
|---|---|
| `struct_split.py` | z3 search: split, one-sided, checks, pairs, force; brute-force validation |
| `generic_rank.py` | linearized ranks |
| `ctr_split_numeric.py` | coupling.py's per-bit split search with t free; full-compression verification |
| `bit_kill.py` | cross-move refutation of every screen-2 candidate bit |
| `key_targets_check.py` | checks that key1 = F(E1.a2, E1.b1, E1.d1) and that the E3 map is a bijection |
| `model_baseline_out.txt` | model.py's own output (unchanged run) |
| `struct_split_*.txt` / `.log` | structural outputs |
| `generic_rank.txt` | ranks |
| `numeric_W32_*.txt`, `numeric_W8_*.txt` | numeric split search outputs |
| `bit_kill_W32*.txt` | refutation outputs |
| `key_targets_check.txt` | target-set check |

Reproduce: run `python struct_split.py split|onesided|checks|pairs|validate`,
`python struct_split.py force 1,0`, `python generic_rank.py`, `python ctr_split_numeric.py 32`
(or `8`) and `python bit_kill.py 32 C0,T0,T0T1,E1d1,E3h1 replay`. Every run took under 15 minutes;
the longest was the 2-check search, 14.8 min before I stopped it (see section 8), and its rerun
took 8 min. At most 2 processes ran at a time.
