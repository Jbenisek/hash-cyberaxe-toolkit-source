# derive-sched-inverse-expansion-A (2026-10-12)

Cells: (0,16) (1,16) (1,17) (2,17) (2,18) (3,18) -- schedule taps W_{j-16} (rows 0,1,2 into 16,17,18) and s0(W_{j-15}) (rows 1,2,3 into 16,17,18).

## Result: label 0 (proved constant), gain 0 bits, PROVED

Argument (formula): W_j = s1(W_{j-2}) + W_{j-7} + s0(W_{j-15}) + W_{j-16}.
chi37 fixes the message difference: dW_i = 0 (every bit "=") for i = 0..5; the W rows with a difference are only 6,7,8,9,10,14,15,22,24 (atlas header, parsed from chi/chi37.txt; rows 4,5 printed all "=", rows 0..3 carry no difference).
Every consistent pair following chi37 therefore has W_i = W'_i for i = 0..5, so W_{j-16} - W'_{j-16} = 0 and s0(W_{j-15}) - s0(W'_{j-15}) = 0 identically (XOR and modular), for j = 16,17,18.
The term enters dW16/dW17/dW18 as an exact zero; no condition, no carry, no probability -- nothing to win or lose. No sampling needed (the event equals the cell on every pair: both are certain).

Numeric confirmation on the chi37 example pair (mx/my in chi/chi37.txt): check_dW.txt -- W0..W5 dXOR = dMOD = 0.

Note on (0,16): the value tie of W0 to W16 is the inverse-expansion construction already recorded as I at (16,0) (W0 solved from chosen W16). That is a value dependency, not a difference contribution; this cell stays 0. Same for (1,17)/(2,18) vs I cells (17,1)/(18,2).

GOLD: none (no E cell).

| cell | label | number | status |
|---|---|---|---|
| (0,16) | 0 | 0 bits (dW0=0) | PROVED |
| (1,16) | 0 | 0 bits (d s0(W1)=0) | PROVED |
| (1,17) | 0 | 0 bits (dW1=0) | PROVED |
| (2,17) | 0 | 0 bits (d s0(W2)=0) | PROVED |
| (2,18) | 0 | 0 bits (dW2=0) | PROVED |
| (3,18) | 0 | 0 bits (d s0(W3)=0) | PROVED |
