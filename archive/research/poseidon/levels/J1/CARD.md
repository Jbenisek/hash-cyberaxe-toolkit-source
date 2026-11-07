# J1 card: R60, R61, R62 (toy exhaustive; learning only)
Script: j1.py (usage `python3 j1.py q seed r`); outputs out_q{257,769,1009}_s{1,2,3}_r{1,2}.txt (18 runs, each exhaustive over all q^2 (A,B) points; nice -n 10, 2 processes).
Validation (OBSERVED): generic scalar perm == poseidon_ref.hash_reduced (r=1,2,5, random inputs); toy (A,B) chain == scalar perm on 5 random inputs per run; control R1 = exactly 3 rank<=1 points, 1 per lane pair, in all 18 runs (reproduces U9/U2).

Per round, mean over 9 runs per r (q=257,769,1009 x seeds 1-3):
| r | round | zero locus of an S-box input / q | new double-zero pts | new single-zero (rows dependent) | new with no zero | rank<=1 total |
|---|---|---|---|---|---|---|
|1|R1|1.000 (exact q)|3.00|0|0|3.0|
|1|R2|1.005|3.56|3.00|0|9.6|
|1|R3|0.984|2.44|2.89|0|14.9|
|1|R4 (P)|0.997|0|1.67|0|16.6|
|1|R60|1.013|2.44|3.78|0|22.8|
|1|R61|0.993|2.00|2.78|0|27.6|
|1|R62|0.994|3.11|3.56|0|34.2|
|1|R63|0.994|2.56|2.33|0|39.1|
|2|R5 (P)|1.011|0|1.22|0|17.8|
|2|R60..R63|~1.0|2.1-3.0|3.0-3.2|0|23.1 / 28.9 / 35.0 / 41.0|
Triple zeros: 0 in every run/round. Nesting (set at round k contains set at k-1): held in every run (assert).

## The 5 most useful observations
1. OBSERVED (18 runs): the zero locus of each S-box input at R2..R62 has q (+-~sqrt q, mean ratio 0.98-1.01) points on the toy, same as the line at R1 (exactly q). Every zero locus looks like an absolutely irreducible-ish curve with ~q points whatever its degree (5^k); no extra components or point excess at R60-R62. Changes the map: the "dense" tail levels carry no visible point-count anomaly in the zero loci (empty square R60-R62 zero loci: filled, dull = random-curve rate). Real-field degree of these loci (Bezout 5^k) is DERIVED only, not measured here.
2. OBSERVED: two zero loci of different lanes meet in ~1 F_q point per pair per round (mean 0.67-1.26, Poisson-like), at every full round including R60-R62; triple meetings never (0 of ~120 pair-rounds x lanes). So each full round injects about 3 double-zero rank-1 points, independent of q and of the degree 5^k. DERIVED: this is the "random curves meet in O(1) points" rate, not a structural family; the 3 at R1 is the same rate, exact because lines.
3. OBSERVED + DERIVED: the rank<=1 census does NOT saturate in rounds; it grows by about 6 per full round (3 new double-zero + ~3 new single-zero-with-dependent-rows) and ~1.2-1.7 per partial round (single-zero only), independent of q (totals at R62: 29-39 at q=257, 32-36 at 769, 35-37 at 1009). U9's "saturates (does not grow with q)" is right in q, but across rounds it is linear: ~35 by R62, ~40 by R63. Partial rounds add no double zeros (PROVED: only lane 0 enters the S-box). New points with no zero: 0 in every run (PROVED: rank can only drop where some S-box derivative 5x^4 vanishes). Source split by round fills the U2/U9 table for R60-R62: R60 2.4 dbl/3.8 sgl, R61 2.0/2.8, R62 3.1/3.6 (r=1).
4. OBSERVED: r=1 and r=2 differ only by the extra R5 contribution (+1.2 single-zero points); R60..R63 per-round rates are identical (within noise). Inheritance is the whole story at R4/R5 (new = 0 double always). Level map: R5 is not a new source of structure beyond one single-zero family (J4 should not expect more).
5. OBSERVED, difference weights (exhaustive-restricted: 4e6 sampled pairs with equal lane 0 at R60 entry, per run): entry weight is always 2 or 3 (weight 1 never: PROVED by branch number 4 with lane-0-zero after M... consistent), weight-2 entry frequency ~2/q; S preserves weight in 100% of pairs (PROVED, lane-wise bijection); through R60..R63 M transitions are random-matrix rates: 3->3 ~1-3/q off, 3->2 ~3/q, 2->2 ~3/q^2.. 3->1 ~3/q^2 (q=257: 160/3.9e6 = 4.1e-5 vs 3/q^2=4.5e-5), 1->3 always (PROVED branch number). Collisions in the sample: 15585 vs random expectation 15564 (q=257); 3873 vs 3964 (q=1009); 5158 vs 5202 (r=2): trail pairs collide at exactly random rate (matches U11 s5). Control random pairs give the same transition rates: no weight-reduction channel from the trail. Level map: tail difference-weight lens = EMPTY/RANDOM; spend nothing more there at toy size.

## Caveats and empty squares (DERIVED/GUESS labelled)
- Pair columns for partial rounds in out_*.txt count lanes 1,2 values that are zero, not S-box zeros; ignore them for R4/R5 (S-box zero only lane 0).
- Not done: real-field R60 single-lane zero-locus degree and a real resultant (GUESS: Bezout degree 5^k per locus, 3125 at R60, 15625 at R61, 78125 at R62; resultants of pairs degree squared, infeasible by direct elimination as in U9). Toy q=4099 not run. Sampling of pairs for W: random a, then random b in its lane-0 group (slight 1/|group| bias, negligible).
- Genus/irreducibility of the loci not measured; point count ~q only says "not worse than a curve of genus O(1)*sqrt-scale"; the +-sqrt(q) spread is consistent with Weil but not tested for genus.
