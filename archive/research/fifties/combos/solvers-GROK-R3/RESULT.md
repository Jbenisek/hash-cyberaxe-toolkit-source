# R3 (Grok, medium confidence): word-level SMT on one split-point inversion (solvers-GROK-R3, 2026-10-09)

**Verdict: NO_GAIN.** z3 4.13.3 returns `timeout` at 900 s on the full instance (128 free guess bits) although the instance is known satisfiable. R3 can be added to BITS.md as closed for SMT (z3 QF_BV) too. MITM.md section 5 is not reopened.

Folder note: the brief named both `combos\r3_smt\` and `combos\solvers-GROK-R3\`. Everything is in `solvers-GROK-R3\` (the label and the final "save under" line). Nothing was written to `r3_smt\`.

## What was built (COMPUTED)
- `smt_inst.py` takes one real ctr_outer split point. It is generated as verify.py does: `random.Random(99)`, first `rels.point`. The script writes QF_BV SMT-LIB2.
  - The closure is the one from BITS.md section 1. Guess words C0.a1, C0.b1, C1.a1, D3.a1 are free 32-bit consts.
  - The 8 coordinates (Y12, K, w5, Y4, Y9, w8, C2.b1, C2.c1) are fixed to the point's values.
  - The other 74 words come from the triangular order of `core.prop_order` and are written as `define-fun` terms (bvadd/bvneg/bvxor/rotate_left). There are 78 relations in all, 74 triangular plus 4 checks. BITS.md's "75 other words" counts one differently, but the closure is the same.
  - The 4 asserted checks are exactly BITS.md's: `C1.a1-X1-X5-w3=0`, `Y1-C1.a1-C1.b1-w10=0`, `C2.c1-X10-C2.d1=0`, `w8-D0.a1+S0+S5=0` (smt_inst_out.txt).
- Python self-test of the emitted term structure at the true values:
  - all 74 derived words are reproduced;
  - the 4 checks hold;
  - the rebuilt basis round-trips through the real `halfsearch.ctr_outer`;
  - flipping bit 0 of C0.a1 breaks all 4 checks.
- The true guess for this point is C0.a1=ffe295f1, C0.b1=f3fe1e57, C1.a1=5307a8e8, D3.a1=44a91573 (point.json).

## Runs (COMPUTED; one z3 process at a time, z3's own -T limit)
| instance | free guess bits | limit | result | z3 time | model = true guess |
|---|---|---|---|---|---|
| ctl_pinned (control 1, guesses fixed to truth) | 0 | 300 s | sat | 0.00 s | yes |
| ctl_bad (control 2, truth with C0.a1 bit 0 flipped: the sttest.py/tocnf.py corruption) | 0 | 300 s | unsat | 0.01 s | - |
| part_b04 (low 4 bits of each guess word free) | 16 | 120 s | sat | 0.56 s (5,393 conflicts) | yes |
| part_b06 | 24 | 120 s | sat | 44.4 s (279,622 conflicts) | yes |
| part_b07 | 28 | 600 s | sat | 185.1 s (479,493 conflicts) | yes |
| part_b08 | 32 | 120 s | timeout | 120 s | - |
| **inst_true (the R3 instance)** | **128** | **900 s** | **timeout** | **900 s** (114 MB peak) | - |

Both controls behave as required, so the encoding is right and the timeout is the solver's, not the model's.

## Reading
- DERIVED: z3 time grows by 0.79 bit per free guess bit from 16 to 24 free bits (2^6.3 over 8 bits). From 24 to 28 it grows by 0.51 bit per free bit (2^2.06 over 4). Each figure comes from a single run on a single point, so solver luck is in it.
- GUESS: a straight log2 extrapolation from 28 to 128 free bits gives about 2^58 s at 0.51 bit per bit and about 2^86 s at 0.79, for ONE split point. Either way it is far from the 2^37-2^41 ops total that MITM.md section 5 would need. The sub-1 slope was measured only on the low bits, with the high bits pinned to truth. It does not show that the full instance costs less than 2^128.
- This agrees with BITS.md 2 and 6: word-level SMT bit-blasts to the same CDCL problem in which kissat and cms returned UNKNOWN, and the check bits depend on all 128 guess bits.

## Not tested
- Other split points. The decision rule asks for 5 more points only on a sat, so they were not run. BITS.md 3 says the cost is flat across points (structural).
- Other closures (only the easiest of the 6,609), other z3 tactics or options (default QF_BV only), bitwuzla, cvc5, boolector (not installed; no packages were installed), and runs longer than 900 s.
- A blocking-clause "corrupted" variant (free guesses, true guess excluded) was not run. The 0-free-bit flip control is the sttest.py analogue.
- Nothing was priced, and nothing touches the score.

Files: smt_inst.py, smt_inst_out.txt, point.json, *.smt2, *.out, run_ctl.sh, run_main.sh, run_extra.sh, run_main.log, summarize.py, summary.txt.
