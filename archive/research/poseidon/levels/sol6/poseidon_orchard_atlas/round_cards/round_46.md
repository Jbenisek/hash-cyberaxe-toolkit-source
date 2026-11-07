# Round 46 — deployment round 47

**Zone:** partial. **S-box:** lane 0 only. **Fresh legal message choices here:** zero.

## Definition and local algebra
Let s be the input state. Add the three constants c[46]. Apply z -> z^5 to lane 0 only; then multiply by the pinned MDS. All arithmetic is in Fp, not XOR arithmetic.

Constants (canonical big-endian display, NOT serialized message order):
```
25e52be507c92760b87db1e2af3ea923646c49f9b46cbf19c5271c297852819e
1c492d64c157aaa471096d8b1b983c98a34c83a3485c6b2d5c380ab701b52ea9
0c5b801579992718f4e6c5e7a573f592d43487bc288df682a20c0b3da0da4ca3
```
The exact local paired rule is delta_out = M * d, where d[j] = (s[j]+c[j]+delta[j])^5 - (s[j]+c[j])^5 for active lanes, and d[j]=delta[j] for inactive lanes.

Whole-state inverse: apply M^-1, the inverse power d=5^-1 mod(p-1) on active lanes, then subtract the constants. The local state inverse is unique. A digest-lane inverse is a different problem.

## Interactions
All three previous state coordinates enter each post-MDS coordinate. This is immediate structural dependence, not a proof that every finite perturbation changes every coordinate. Earlier-round state is not an independently editable legal message input. Future-row interventions cannot alter the stored past, but future constraints can constrain earlier values.

For consecutive partial rounds, exact active-input equality leaves dimension 2 for one round, 1 for two, and 0 for three. This is the O=[e0;e0 M;e0 M^2] rank result, not a ban on other differential families.

## Recorded native diagnostic
2048 legal-message pairs with m0 -> m0+1 modp, m1 and capacity fixed. Output-lane change counts: 2048, 2048, 2048. Total XOR popcount across all samples and 3 words: 780998. No collision probability inferred. See all 512 limited feature tests in signature_screen.csv.

The row's full-state inverse was checked on 16 independent internal states. A singular-derivative finite-change counterexample was checked at this row. These internal samples do not assert legal-input reachability.

## Recorded exhaustive toy diagnostic
Different field p=257 and toy MDS/capacity: 66049 complete inputs, 66049 distinct full states, 257 digest values. Exact unordered projected collisions 8484585; noncollisions 2172717591; total 2181202176. This does not estimate native-field rates.

## Arithmetic ledger
9 additions + 12 multiplications = 21 field arithmetic operations for full-state evaluation. Cumulative through this row: 1011. Counts omit encoding,control,loads and representation costs and do not constitute a contest score.

Formal polynomial degree upper bound: 5^47. This is neither exact minimal degree nor a work bound.

## Open obligations
Global legal-input fibre counts, operationally useful conditional signature, interactions under an actual nonuniform proposal law, and costed exact end-to-end generator. This row is indexed and locally tested, not declared completely solved.

Sources: https://github.com/Annkkitaaa/hash-smash/blob/01f736268b7086d97f38837d343d63a81bf31649/verifier/poseidon.py ; https://github.com/zcash/halo2/blob/halo2_poseidon-0.2.0/halo2_poseidon/src/lib.rs. Evidence: data/round_cards.csv, data/round_pair_grid.csv, data/legal_message_sensitivity.csv, data/toy_full_input_counts.csv.
