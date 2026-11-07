Total:

    T <= (1.65 * N + 2^94 + 2^28 + 2^11 + 1) / 430 + 2 + 2^80
       <  1.65 * N * (1 + 2^-7) / 430 + 2^81
       <  2^92.5198 + 2^81
       <  2^92.53.

Here N = 759,300 * 2^81 = 2^100.534311 and 1.65 * N / 430 = 2^(100.534311 +
0.722466 - 8.748192) = 2^92.508584; the three logarithms are rounded so that the
result is not too small. The terms after the first add up to less than 2^94.01,
which is below 1.65 * N * 2^-7, itself more than 2^94.256, and
log2(1 + 2^-7) < 0.01123. The last term is the preprocessing of Section 9, the
bounded selection of the constants, the class, the sub-class and rule A
together with the recovery of W4 and W13, charged in full. The submitted bound
is time_log2 = 92.53, the total rounded up to two decimals. This is a
worst-case bound for the algorithm as stated, which halts within its budgets on
every run.
