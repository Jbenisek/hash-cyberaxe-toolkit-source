# Preregistration: random-mapping premise for the blake3-r3 chain (written 2026-10-12 15:45 MDT, before any counted run)

Frozen files (sha256): premise.cpp 04fc5adcdb658589472896aea7cef117b42c67192f280aec17fed7fb1aee0aa6,
as_test.py 9e16ddfe7dc20f71db67a746be93cc7b705b550b5c4f1dce90ad2a7713ee1ba0, rho_frozen.py (the shipped program, run as rho.py)
505dcce6c3af87702dfe426be8be1deabd3fb1abfa966edde75d789a0e83f611. Seeds are inside the files. No run is repeated, no parameter is
changed after a result; every output is reported, passing or not.

Smoke runs before this note (not counted, disclosed): rho n=16..36, 300-400 runs with K=0, and with fresh K per run at n=20,24,28,32
(400 runs each). They showed that fixed-K first-repeat times are not independent samples (all starts share one functional graph:
ratios 0.70 to 1.65 across n), and that fresh-K runs agree with the random mapping (ratios 0.994 to 1.004). That is why test T1 uses fresh K
and tests T2 and T3 measure the fixed target directly.

Function: f(x) = digest(K || x), 3 rounds, flags 11, length 64, counter 0; K = 0^32 bytes for the target (m0..m7 = 0).

T1 (family law, fresh K per run). premise rho n runs 1: n = 32 with 2000 runs, n = 40 with 300 runs. Statistic: T = distinct points before
the first repeat. Predictions for a random mapping: E T = sqrt(pi N/2), E T^2 = 2N, T^2/(2N) ~ Exp(1). Pass: |z_mean| <= 4, |z_T2| <= 4,
KS sqrt(R) D <= 1.949 (0.1 percent critical value). Reported: ratio = mean T / sqrt(pi N/2).

T2 (full-width uniformity of the fixed target). premise proj <source> <k> for source in {chain, counter, random}, k = 0..13: 2^26 points of the
256-bit f with K = 0 (chain: x_{i+1} = digest(x_i); counter: x = r + i; random: uniform x), the k-th projection (32-bit words W0..W7, XOR
of the 8 words, sum of the 8 words, four 40-bit pairs W(2j) + low 8 bits of W(2j+1)), observed equal pairs against C(2^26, 2)/2^bits.
Pass: |z| <= 4.5 for each of the 42 statistics (Poisson z). Reported: observed/expected.

T3 (algorithmic success of the shipped search on the fixed target). as_test.py <dir> n cond first count with the shipped rho.py (plan(n), one
attempt = one call of search with a fresh r): n = 32: attempts 0..3999 for cond target (K = 0 chain) and 0..3999 for cond ideal (blake2b
keyed PRF of the same width, fresh key per attempt); n = 40: attempts 0..479 for each. Pass: every returned pair re-checks (bad_pairs = 0) and
the two-proportion z of target against ideal has |z| <= 3.5 at each n. Reported: both success frequencies and the plan's pure-birthday value
1 - exp(-Q^2/2N).

Not tested and said so: the full 256-bit functional graph (no test can see it), any structure that appears only for iterations of length
above 2^40, and the dependence of results on the choice K = 0.
