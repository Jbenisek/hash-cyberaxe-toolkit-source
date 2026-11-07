## 7. Premise H1 and its evidence

H1 (claim.json `H1-random-function-model`), the only premise of the claim.
- Statement: for the attempt's coins rho0 and x_0 (uniform 254-bit words), the search of Section 2 on the real map F(x) = digest(x, rho0) succeeds with probability at least P_F, the success probability of the same search on a uniformly random function, which Lemma 2 bounds by P_F >= 0.390000002. This is an assumption; no proof is known.
- Role: score-critical. It is the only step from Lemma 2 to the claimed success probability; the recovery (Section 3), the ledger (Section 5) and the memory (Section 6) are proved.
- Scope: target poseidon-orchard-r23-prefix-v1, inputs (x, rho0), one trail with the parameters of Section 2 (S = 1.70e38 evaluations). Not claimed for other round counts or budgets.
- Limitations: the evidence below is measured on outputs truncated to 16 to 40 bits, on trails of at most {{MAXEV}} steps; the 254-bit map over 2^127 steps cannot be observed, so the transfer to full width is the premise itself.

Evidence: measurements of the real map at r = 23. Our own code (Appendix C, with our C field library; `rho.py`'s `digest` equals the organizer's `verifier/poseidon.py` digest on 24 of 24 inputs at r = 23, and the organizer digest confirms all {{PAIRS_OK}} of the {{PAIRS}} pairs the runs returned: distinct messages (A, rho), (B, rho) whose digests agree in the low w bits). Each measurement was run twice, run A and run B, on disjoint functions and starts ({{MINUTES}} minutes in all). The measurements are evidence for H1 only: no parameter of the attempt is taken from them.
- Map at width w: F_w(v) = low w bits of digest(v, rho), v in [0, 2^w). Each trial draws its own rho (the function index) and start, as the attempt draws rho0 and x_0. The walk runs until its first repeat, with every value kept, giving the exact t (first repeat), mu and lambda of Section 3.
- Collision rate: for a random function on N = 2^w points, P(t > n) = prod_{i<=n} (1 - i/N), so t^2 / 2N is exponential with mean 1. The hazard multiplier c = K / sum(t^2 / 2N) estimates the factor on the collision rate (c = 1 for a random function; 95% interval from the Gamma law of the sum).
- Distinguished points at density theta = 2^10 / 2^(w/2) (low w/2 bits below 2^10; 1/16 at w = 16, 20): theta times the mean gap between consecutive DPs (1 for a random function) and theta times the mean detection delay a' - mu over walks with lambda > 20 / theta (1 - theta for a random function).
- The full search (`search` of Section 2, with Lemma 2 parameters computed by the same formula for N = 2^w, D = 2^(w/2+10), SMAX = 2^(w/2+3), at widths 24 to 40): the fraction of runs that return a verified pair, against the Lemma 2 bound for that width.
- Control: the same program on a keyed pseudo-random function (splitmix64), five times as many trials per width.

{{TABLE}}

Regime and result: in 13 of the 14 run-and-width cells the 95% interval of the hazard multiplier contains 1; the exception (run B, w = 28: {{B28}}) lies above 1, on the side of more collisions, and one exclusion in 14 is what 95% intervals give by chance. Pooled over {{KALL}} walks it is {{CPOOL}}, 95% interval [{{CLO}}, {{CHI}}]. The weighted slope of log c against width is {{SLOPE}} per bit (standard error {{SLOPE_SE}}): no trend is detected. The search succeeded in {{SUCC_ALL}} of its runs at widths 24 to 40, against a mean Lemma 2 bound of {{SUCC_LB}}. DP gaps follow the geometric law the lemma uses (theta x mean gap {{GAPRANGE}} at widths 24 to 40), and no gap of these Orchard runs reached gmax.
Extrapolation: from widths 16 to 40, where c is measured, to width 254, by H1. The measurements show the rate law that Lemma 2 uses on the real round function at the claimed round count. They do not bound c at full width.
Sensitivity: if the true collision rate is c / N per earlier value with c = 1 - e, the same success needs n larger by c^(-1/2), that is 0.5 log2(1/c) bit of time: 0.0072 bit for e = 0.01, 0.0370 for e = 0.05, 0.076 for e = 0.10. At the lower end of the measured interval (c = {{CLO}}) the price is {{DT_LO}} bit.
Why the attempt draws rho0: on one fixed map the success over starts alone depends on that map's longest cycle. For the rho = 0 map we measured {{FIX24}}, {{FIX28}} and {{FIX32}} at widths 24, 28 and 32. For 80 fixed pseudo-random maps at width 24 (40 per run, 200 starts each) the per-map fractions ranged from {{CF_MIN}} to {{CF_MAX}} (standard deviation {{CF_SD}} and {{CF_SD_B}} in the two runs). Drawing rho0 as a coin makes the attempt's probability an average over maps, which is what Lemma 2 bounds.

## 8. Experiments

None are declared. The organizer runner's Python path calls `digest_fn(b"")` to size the digest (`experiments/runner.py`), and the Orchard digest rejects any input other than two 32-byte encodings, so a declared Poseidon experiment fails before its program runs. The measurements of Section 7 were run with our own code (Appendix C), and their data are in Appendix D.

