# Round 00 — deployment round 1

**Zone:** leading_full. **S-box:** all three lanes. **Fresh legal message choices here:** zero.

## Definition and local algebra
Let s be the input state. Add the three constants c[0]. Apply z -> z^5 to all three lanes; then multiply by the pinned MDS. All arithmetic is in Fp, not XOR arithmetic.

Constants (canonical big-endian display, NOT serialized message order):
```
360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303
2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b
150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8
```
The exact local paired rule is delta_out = M * d, where d[j] = (s[j]+c[j]+delta[j])^5 - (s[j]+c[j])^5 for active lanes, and d[j]=delta[j] for inactive lanes.

Whole-state inverse: apply M^-1, the inverse power d=5^-1 mod(p-1) on active lanes, then subtract the constants. The local state inverse is unique. A digest-lane inverse is a different problem.

## Interactions
All three previous state coordinates enter each post-MDS coordinate. This is immediate structural dependence, not a proof that every finite perturbation changes every coordinate. Earlier-round state is not an independently editable legal message input. Future-row interventions cannot alter the stored past, but future constraints can constrain earlier values.

This full round has no nonzero S-box-avoiding difference on all three active lanes. That does not exclude output-only cancellations.

## Recorded native diagnostic
2048 legal-message pairs with m0 -> m0+1 modp, m1 and capacity fixed. Output-lane change counts: 2048, 2048, 2048. Total XOR popcount across all samples and 3 words: 781939. No collision probability inferred. See all 512 limited feature tests in signature_screen.csv.

The row's full-state inverse was checked on 16 independent internal states. A singular-derivative finite-change counterexample was checked at this row. These internal samples do not assert legal-input reachability.

## Recorded exhaustive toy diagnostic
Different field p=257 and toy MDS/capacity: 66049 complete inputs, 66049 distinct full states, 257 digest values. Exact unordered projected collisions 8454272; noncollisions 2172747904; total 2181202176. This does not estimate native-field rates.

## Arithmetic ledger
9 additions + 18 multiplications = 27 field arithmetic operations for full-state evaluation. Cumulative through this row: 27. Counts omit encoding,control,loads and representation costs and do not constitute a contest score.

Formal polynomial degree upper bound: 5^1. This is neither exact minimal degree nor a work bound.

## Open obligations
Global legal-input fibre counts, operationally useful conditional signature, interactions under an actual nonuniform proposal law, and costed exact end-to-end generator. This row is indexed and locally tested, not declared completely solved.

Sources: https://github.com/Annkkitaaa/hash-smash/blob/01f736268b7086d97f38837d343d63a81bf31649/verifier/poseidon.py ; https://github.com/zcash/halo2/blob/halo2_poseidon-0.2.0/halo2_poseidon/src/lib.rs. Evidence: data/round_cards.csv, data/round_pair_grid.csv, data/legal_message_sensitivity.csv, data/toy_full_input_counts.csv.
