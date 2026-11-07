Total:

    T <= ([CHARGE] * N + 2^94 + 2^28 + 2^11 + 1) / 430 + 2 + 2^[P]
       <  [CHARGE] * N * (1 + 2^-7) / 430 + 2^[P1]
       <  2^[MAIN] + 2^[P1]
       <  2^[TIME].

Here N = 759,300 * 2^81 = 2^100.534311 and [CHARGE] * N / 430 = 2^(100.534311 +
[LOG2C] - 8.748192) = 2^[MAIN0]; the three logarithms are rounded so that the
result is not too small. The terms after the first add up to less than 2^94.01,
which is below [CHARGE] * N * 2^-7, itself more than 2^[SLACK], and
log2(1 + 2^-7) < 0.01123. The last term is the preprocessing of Section 9, the
bounded selection of the constants, the class, the sub-class and rule A
together with the recovery of W4 and W13, charged in full. The submitted bound
is time_log2 = [TIME], the total rounded up to two decimals. This is a
worst-case bound for the algorithm as stated, which halts within its budgets on
every run.
