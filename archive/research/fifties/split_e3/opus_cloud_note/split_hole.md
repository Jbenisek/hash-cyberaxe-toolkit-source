# Where the hole is: the E1/E3 split (2026-10-10)

Labels: **COMPUTED** (exact, by the scripts named), **DERIVED**, **OPEN**.

## 1. The residual is two independent lotteries, and the search pays their product

COMPUTED from `results/pairs_453_weights.txt` (C15 weights), by `notes/split_costs.py`:

| quantity | value |
|---|---|
| E3 (side 3) alone, summed over the support | 2^-54.59 |
| E1 (side 1) alone, summed over the support | 2^-40.15 |
| joint, Pr[Z] = sum P1(t,s)·P3(t,s) | 2^-100.53 |

In the last step, E1 = G(Y1, Y6, Y11, Y12, w12, w5) and E3 = G(Y3, Y4, Y9, Y14, w15 = 0, w8) share no inputs. The coupling is only that every free word feeds both. The 63.6 score is an amortised search of the 2^100.5 product. It is not a birthday wall: the residual's real entropy is 100.5 bits, not 128.

DERIVED: what decoupling would buy, in trials.

| design | trials | score at 30 / 74 / 524 ops per trial |
|---|---|---|
| coupled (today) | 2^100.5 | (amortised to 63.6) |
| one-sided: fix E3, search E1 | 2^54.6 E3 configs + 2^47.8 E1 trials | 50.8 / 52.1 / 54.9 |
| product meet-in-the-middle on (t,s) | 2 × 2^50.3; memory is only the on-support hits | 47.4 / 48.7 / 51.6 |
| construct E3 instead of searching for it | one prescription + about 2^44–2^48 E1 trials | 40s to low 50s, depending on prescription cost |

The "28 bits forced to zero" that a meet-in-the-middle needs are already in hand: the class concentration is 2^27.5. What is missing is the decoupling, not concentration.

## 2. Why constructing E3 is affordable

DIRECT §1 already priced prescribing E3's inputs. Q = Y9 and E = w8 are E3's c and y inputs, and Y4 is its b input. The price is one cyclic 32-bit equation per step, with about one root per target. That cost was weighed against the 2^-9.8 filter, about 10 bits, and rejected. Weighed against E3's own 2^-54.6 it is cheap. The col3 free half-collision already works by prescription (six pinned constants). This is the same move, one G call later.

## 3. The exact test (OPEN; needs the 77-equation word model)

Run the peeling tool (mink.py) with these prescribed as inputs:
- E3's inputs {Y3, Y4, Y9, Y14, w8};
- the col3 pins.

Report two numbers:
1. k, the minimal number of cyclic equations.
2. The free words left downstream that move E1's inputs {Y1, Y6, Y12, w12, w5} without touching the prescribed set.

Two free sinks help here:
- **E0 and E2 inputs are don't-care**, because those calls carry no difference.
- **The counter is the only input not reused in round 1**, so it can absorb round-0 changes.

Degrees of freedom: about 491 free bits (13.75 message words plus the 51-bit counter), against 64 + 160 prescribed. That leaves about 267 bits, so the family exists algebraically. Only the cost of traversing it is open.

Decision rule: if k ≤ 2 and at least 2 free words move E1, the 50s or lower are in reach. Even when every E1 trial needs its own 2^16-operation solve, the one-sided split stays around 56.

## 4. Idea 1 (counter + flag differences cancelling in round 1) is dead as stated

COMPUTED on real 2-round BLAKE3 by `notes/structural_footprint.py` (self-test against the 7-round empty-input vector).

Every structural difference needs both message words of its round-0 column. Flags cancelled with m6 alone left the round-0 state identical in 0 of 2000 trials. Round-1 footprints after the round-0 cancellation:

| structural difference | round-1 injections | words differing after round-1 columns |
|---|---|---|
| length 55/63 (current) | col3.x (m4), E1.y (m5) | 4 (2 of them pinned to zero) |
| flags, root chunk 11 vs root parent 12 | col0.y (m6), col2.x (m7) | 8 |
| parent vs chunk (counter t, flags 7) | col0.y, col2.x, col2.y, E0.x | 8 |
| counter-high + flags (idea 1) | col0.x (m2), col0.y (m6), col1.x (m3), col2.x (m7) | 12 |

There are two further problems with idea 1:
- **A counter difference only exists between a parent node (counter 0) and a chunk at the same tree position.** That forces the flag difference too, and it makes one side's message two chaining values rather than free words.
- **A counter-high difference needs a chunk index of at least 2^32.**

Of the legitimate differences, the current length difference has the smallest footprint.
