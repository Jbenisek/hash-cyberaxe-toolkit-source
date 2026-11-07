# Alternative characteristics, 37-step SHA-256: bit 31, then a short look at the low-bit gate (job 119 retest)

Taken over from Grok job 119, whose runner ran out of credits. The inputs are `research/grok/in/job119_alt_chars2/` and `research/grok/work/job117_alt_chars/`. All of that is our own code, read here as data. Labels used: **PROVED**, **COMPUTED**, **GUESS**. 1 CE = 2644 word-ops, and for SAT runs 1 word-op = 1 propagation, the job112 meter. Nothing was submitted, and only this job's own processes were stopped.

## Verdict

- **No bit-31 pair was found, so no bit-31 characteristic exists yet.** The published dense part cannot be carried over to bit 31 (PROVED below). A new dense part (rows 6..15) would have to be found. The sign-free and the tail-guided SAT runs at bit 31 found nothing in 30 min each. The bit-29 control run, with the same tail-only guidance, also found nothing, so these runs say nothing either way about bit 31.
- **If a bit-31 characteristic is found, its late part is lighter.** The exact late event is **75/2^19 = 2^-12.771**, against the published **1275/2^24 = 2^-13.684**, a gain of **+0.913 bit**. The tail cell rank would be **73**, against 74, if the rotated rows 16..21 still hold at bit 31. The `-0.78 bit` W22 penalty in the brief is wrong: job117 measured two bit-31 `dW22` values whose state window costs 23. The four bit-31 values whose window costs 22 have exactly the published mode.
- **Low bits: the message gate is about 1.3 bits from bit 29, not 5.5.** Bit 10 is the best low bit. When both sides of the gate are counted exactly, it costs 2^-23.68, against 2^-22.40 at bit 29. Bit 10's W22 cell rank is 8, against 10. This is a GUESS-level lead (net about +0.7 bit). The other pieces at bit 10 were not measured.

## 1. The bit-31 late event

**COMPUTED** (`scan_w22.sh`, output in `scan_w22.txt`). This is a full 2^32 scan of `σ1(x+D)−σ1(x)`.

| D | maximum count | number of T at the maximum |
|---|---:|---:|
| 017f8000 (published) | 9830400 = 75·2^17 | 8 |
| 05fe0000 (bit 31) | 9830400 | 8 |
| 06020000 (bit 31) | 9830400 | 8 |

- No collided bucket goes above that count, so 9830400 is the true maximum (COMPUTED).
- `fa020000` and `f9fe0000` are the negatives of these two. They have the same mode (PROVED, by the map x → x−D).
- `exact31.py` checks that all 8 mode values T can be reached as `−dσ0(W9)` for the bit-31 W9 mask `14044aa8`.
- At bit 31, `dW24 + (−dW8) = 2^31 − 2^31 = 0`. So T = `−dσ0(W9)`.
- At bit 31, `dW22 = dσ0(W7)`, because `dW6 + dW15 = 2^31 + 2^31 ≡ 0` whatever the signs. At bit 29 that cancellation is a sign condition.

**PROVED**, `dW26` at bit 31:
- `x + 2^31 = x ⊕ 2^31` and σ1 is a GF(2) bijection (rank 32, COMPUTED).
- So `σ1(x+2^31) − σ1(x)` takes each of the 8 signings of `00205000` with probability exactly **1/8**. A 2·10^5-sample check agrees.
- The published value at bit 29 is 17/256.

The total keeps the same E22 blocker coin (1/2) as the published one: q_event(bit 31) = (75/2^15)·(1/8)·(1/2) = **75/2^19 = 2^-12.7712**, against **1275/2^24 = 2^-13.6837**. Gain: **0.9125 bit**.

## 2. Tail GF(2) rank

**COMPUTED** (`tail_rank31.py`):
- Published `chi37.txt`: 76 equations, rank **74**. This reproduces job117.
- Without the W22 and W24 cells: 62 equations, rank 60. The same holds for that set rotated by 2 bits.
- W22 cell:
  - Published: rank 10.
  - Bit 31, all four state-22 `dW22` values, every form of weight ≤ 4, best target: **rank 10**.
- W24 cell:
  - Published: rank 4.
  - Bit 31: **rank 3**. Only the three σ1 output-sign forms remain, because the sign of bit 31 is not a condition.
  - If bit 31 is pinned as well, the rank goes back to 4.
- No other tail equation uses the W22 and W24 variables, so the ranks add: bit-31 tail rank = 60 + 10 + 3 = **73**.

**GUESS:** this assumes the rotated rows 16..21 are a valid bit-31 window. job117's `state_min` supports it: at bit 31 it finds the same pattern, cost 22, rotated. It is not confirmed by a pair.

## 3. Why the published dense part does not transfer (PROVED + COMPUTED)

- **PROVED.** At bit 31 the state is shared through row 5, so `δE6 = δA6 = δW6 = 2^31`. Since `x + 2^31 = x ⊕ 2^31`, E6 and A6 can differ **only in bit 31**.
- The published bit-29 rows use carry spreads: E6 is `uuu` on bits 31..29 and A6 is `nu`. That shapes Σ1(E6) into a 9-bit difference that the later rows depend on.
- Shifted up by two bits, those spreads would need bits 33..31, which do not exist. So rows 7.. of the published characteristic have no bit-31 counterpart.
- **COMPUTED with kissat.** Rotating the A/E cells by +2 gives UNSAT:
  - rows 0..24: UNSAT in 4.5 s
  - without the x2 conditions: also UNSAT
  - rows 6..8 alone: UNSAT
  - full wrap: UNSAT in 0.85 s

## 4. Pair search (all metered)

`chi31_sat.py` is job112's `dense_sat.py` with two additions: B is read from the environment, and there is a `rot` mode that rotates the chi37 cells in. Its `rotcheck` passes the published pair (B=29, ROT=0). With every register, it gives the same 373,211 clauses as job112's `chi` mode.

| run | result | propagations |
|---|---|---:|
| kissat, rotated AE cells, rows 0..24 | UNSAT, 4.5 s | 2,847,256 |
| kissat, same without x2 | UNSAT, 4.5 s | 2,780,261 |
| kissat, full wrap | UNSAT, 0.85 s | 20,617 |
| cadical, rotated AE cells (stopped by me once kissat had proved UNSAT) | — | 47,973,506 |
| kissat seed 2 walk, B=31, rotated tail rows 16..24 only (`r31_tail.cnf`) | UNKNOWN, 1800 s | 1,139,736,242 |
| cadical seed 1, same file | UNKNOWN, 1800 s | 1,930,549,991 |
| kissat seed 1, B=31, sign-free window (`r31_full.cnf`) | UNKNOWN, 1800 s | 1,247,193,323 |
| kissat seed 2 walk, **B=29 control**, tail rows only | UNKNOWN, 1800 s | 1,177,509,119 |
| **total** | | **5,548,610,315 = 2^21.00 CE** |

The row-range probes in `probe/` were run with `-q` (60 s cap each), so they are wall-time only and are not in the total. No model was found, so `verify31.py` (its own 37-step compression) was only run on job112's pair A as a self-test: `COLLISION_37`, digest `3c7353c7…03b5b458`, the same as job112. `pairA_pattern.txt` is that pair's signed pattern in chi37 row format. No chi37-format candidate file was written, because no bit-31 pair exists.

## 5. Low-bit families: the message gate counted on both sides

The gate, from `dW16 = dW21 = dW25 = dW26 = 0`, is σ0(W10+D10)−σ0(W10) = σ1(W14+D14)−σ1(W14) = T = −dW9, where:
- D10 is an algebraic `−dσ1(W24)`
- D14 is an algebraic `−dσ0(W6)`

Carries are allowed in W9, W10 and W14, which means a different signing or XOR pattern from the family masks. The screen (`gate_pair.py`, 2^22 samples, GUESS level) picked the targets. Exact 2^32 counts (`gate_exact.sh`, output in `gate_exact.txt`, 134 s) are COMPUTED:

| bit | W22 cell rank | D10 / D14 / T | σ0 side | σ1 side | joint |
|---:|---:|---|---:|---:|---:|
| 29 | 10 | fff7f400 / fc3ff800 / fd00ee66 | 2^-10.746 | 2^-11.657 | **2^-22.403** |
| 10 | 8 | fd800001 / feffff88 / fe54bf60 | 2^-10.289 | 2^-13.393 | **2^-23.681** |
| 11 | 8 | 04fffffe / fe0000f0 / ff9a80c0 | 2^-16.608 | 2^-9.313 | 2^-25.920 |
| 12 | 8 | 0a000004 / fc0001e0 / ff2d0180 | 2^-16.913 | 2^-9.453 | 2^-26.366 |
| 4 | 7 | 000a0000 / 20040002 / 8008ab02 | 2^-23 | 2^-9.667 | 2^-32.667 |

- Bits 3, 5 and 6 come out at about 2^-31 in the screen.
- job117 counted only the σ0 side against carry-free `−dW9` targets, which gave 16.30 bits at bit 10. Allowing carries lets the σ0 side reach 2^-10.29.
- **GUESS.** Bit 10 is 1.28 bits worse on the gate and 2 cell ranks lighter, so net about +0.7 bit. Still unmeasured at bit 10: the exact W22 mode, the exact `dW26` (only bounds exist), the state window and the dense part. The maximum over T is taken from sampled candidates, not from a full join.

## Not established

- A bit-31 dense part or conforming pair. The SAT result is UNKNOWN, and the bit-29 control shows that tail-only guidance is too weak at 30 min.
- That the tail rank 73 holds for a real bit-31 characteristic.
- The full joint maximum of the low-bit gate, and every other low-bit tail piece.

## Next step (GUESS)

Search for a bit-31 dense characteristic with signed-difference propagation, the paper's kind of tool. Then run the job112 `chi` mode on it. The other option is longer and more parallel SAT runs at B=31, calibrated first on B=29 with the same guidance.
