# derive-sched-inverse-expansion-B (2026-10-12)

Cells: (3,19) (4,19) (4,20) (5,20) (5,21) -- schedule taps W_{j-16} / s0(W_{j-15}) from rows 3..5; and (10,17) -- +W10 into W17.
Evidence: check_cells.py -> check_cells.txt (exact, pure formula + enumeration; no traillab call needed, no sampling).
Consistent messages only: every pair follows chi37's W cells; nothing held fixed beyond the characteristic and the 32 l list.

## (3,19) (4,19) (4,20) (5,20) (5,21): label 0, 0 bits, PROVED
W_j = s1(W_{j-2}) + W_{j-7} + s0(W_{j-15}) + W_{j-16}. chi37 gives dW3 = dW4 = dW5 = 0 (rows 4,5 printed all "=", row 3 carries no difference).
So W_{j-16} and s0(W_{j-15}) enter dW19/dW20/dW21 as an identical zero on every consistent pair: no condition, no carry, event = cell with Pr 1. Example pair confirms dW3..5 = 0.

## (10,17): label 0, 0 bits, PROVED (exact over the 32 l)
dW17 = ds1(W15) + dW10 (dW1 = d s0(W2) = 0).
- dW10 (x-y) = fff80c00, fixed by W10's signed cells (n bit19, u bit12, n bit10) -> constant on every consistent pair.
- ds1(W15) = 0007f400 for each of the 32 l (enumerated; x member = l, has bit29 = 1, y = l ^ 20000000).
- Sum = 00000000 on 32/32 l. dW17 = 0 is certain given W15 in L*: nothing to win.
- Context (not a gain): with W15 free apart from the u at bit 29, Pr[dW17 = 0] = 8/64 = 1/8 exactly (signs of s1 bits 19,12,10); the L* restriction already pays this, so the cell and the exact event agree at Pr 1. Agrees with hot-H2-row17 (15,17).
- Example pair: dW17 = 0, W15 of x = 7dd43a81 in L*.

GOLD: none (no E cell; every cell's exact event equals the cell with Pr 1).

| cell | label | number | status |
|---|---|---|---|
| (3,19) | 0 | 0 bits (dW3=0) | PROVED |
| (4,19) | 0 | 0 bits (d s0(W4)=0) | PROVED |
| (4,20) | 0 | 0 bits (dW4=0) | PROVED |
| (5,20) | 0 | 0 bits (d s0(W5)=0) | PROVED |
| (5,21) | 0 | 0 bits (dW5=0) | PROVED |
| (10,17) | 0 | 0 bits; dW10=fff80c00 cancels ds1(W15)=0007f400 on 32/32 l | PROVED (exact enumeration) |
