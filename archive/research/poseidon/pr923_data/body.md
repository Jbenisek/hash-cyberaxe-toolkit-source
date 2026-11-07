Following up on [discussion #380](https://github.com/Layr-Labs/hash-smash/discussions/380), where I proposed two Poseidon target definitions, the organizers picked Target B, the instance deployed in Zcash Orchard, and asked for a PR. This fills in the deferred `poseidon` family: target definitions, a reference implementation with the official vectors, instrumented costs, draft starter packages and regression coverage. It adds no baselines, no scores and no Yukon registration.

## The target

Zcash Orchard `PoseidonHash`, parameter set `P128Pow5T3`, pinned to halo2_poseidon 0.2.0 at tag halo2_poseidon-0.2.0, the version the orchard crate depends on. The constants themselves are unchanged since May 2022; the crate is a later repackaging of the same values. It matches the Zcash Protocol Specification section 5.4.1.10.

| Item | Value |
| --- | --- |
| Field | Pallas base field, `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001` |
| Width | `t = 3`, rate 2, capacity 1 |
| S-box | `x^5` |
| Rounds | `R_F = 8` full (four leading, four trailing), `R_P = 56` partial, so 64 deployed rounds |
| Round body | Add round constants to all three elements, apply the S-box (all three in a full round, element 0 only in a partial round), then multiply by the MDS matrix |
| Mode | `ConstantLength<2>`, initial state `[m0, m1, 2^65]`, capacity element `L * 2^64` with `L = 2`, one permutation |
| Message | Exactly 64 bytes: two 32-byte little-endian field elements, each strictly less than `p` |
| Digest | State element 0 as 32 little-endian bytes |
| Nominal reference | 127 |

Canonical encoding is enforced: an element encoded as `x + p` is rejected, because it is the same field element as `x` and accepting both encodings would hand out a collision for free. Wrong lengths are rejected too, and certificate verification reports either as a failed certificate.

The output space is `p`, about `2^254`, not `2^256`, so the generic collision exponent is about 127. The registry records `nominal_security_bits: 127` while `digest_bits` stays 256 for the 32-byte encoding.

## Choices made

**Round pair 1 and 2, as prefix rounds.** In #380 the organizers suggested starting there ("We can always start with round pair 1, 2") and asked for a PR. The pair is explicitly provisional. Both targets run the first `r` rounds of the deployed schedule and stop, the prefix convention every other target uses, so rounds 1 and 2 are the first one and two full rounds. The implementation accepts any prefix from `r = 1` to `r = 64`, so moving the pair later needs no code change. Collisions at rounds 1 and 2 are expected to be easy. The nominal 127 is the generic reference, as for the other exploratory targets, not an estimate of difficulty at these rounds.

**Deployed constants, truncated to the first `r` rows**, with the MDS matrix unchanged. This is the only consistent choice under prefix reduction, since the reference generator is seeded with `R_F` and `R_P` and cannot be reseeded for one or two rounds.

**Exploratory lanes only**, matching SHA-256 37/38. The two unused rigorous Poseidon slots are dropped, so planned lanes move from 26 to 24, while runnable lanes move from 26 to 28.

**Reference operation cost `C = 27` and `C = 54`**, counted in field operations since this is a prime-field target.

## What I verified

Full record in [`docs/FRONTIER_VALIDATION.md`](docs/FRONTIER_VALIDATION.md).

- `bash .yukon/setup.sh`: 348 tests, 343 passed, 5 skipped, against 311 and 306 on `main`, so the 37 added tests are the whole difference.
- 22/22 official vectors reproduce (11/11 permutation, 11/11 hash), and all 192 round constants plus the 3x3 MDS matrix equal the pinned `fp.rs`.
- Domain gates: `x + p`, an element equal to `p`, and any length other than 64 bytes are rejected, including through certificate verification. Negative controls for a changed constant, a wrong capacity element and a wrong round count break the vectors.
- `python3 scripts/reference_operation_costs.py`: 27 and 54, cross-checked at 64 rounds as 816 multiplications (240 S-box, 576 MDS) and 576 additions.
- All 26 existing lane configuration hashes recorded before and after in [`docs/validation/poseidon-orchard-fingerprints.json`](docs/validation/poseidon-orchard-fingerprints.json).

Separately, outside this PR, I regenerated all 192 constants and the MDS matrix with my own port of the Poseidon v1.1 reference generator (Grain LFSR, seeded for R_F = 8, R_P = 56), and they matched. Those scripts are at https://github.com/Annkkitaaa/hashsmash-poseidon-verification. Within the PR, the constants are checked against the pinned fp.rs and the official vectors.

## This PR needs the `yukon-unsafe` label

All 26 existing lane configuration hashes change, each confined to `cost_model`, `qualification_policy` and `reference_checker_sha256`, with selected operation weights unchanged. `qualification_policy` moves for every lane because its hash covers a fixed, lane-independent set of 24 review-contract files, and exactly one changed: `schemas/claim-frontier-v3.schema.json`, which needs the two new profile IDs in its `target_profile` enum or neither package can validate.

I cannot apply labels myself, so please add it. Poseidon adds no registration, so this queues no new baseline workflow.

## Out of scope

Organizer baselines and live judge qualification. Both packages are incomplete drafts with nominal template values, not attacks, baselines or scores. The tracks are defined and locally runnable but deliberately not registered in Yukon, as Keccak[800] already is, since registration also needs an admissible baseline per lane.

## Open items for the organizers

1. **Field cost rule.** The cost model says a field-specific model is required before Poseidon activation, and a 255-bit modular multiplication is not one of its listed primitives. I did not change that policy text. These values count one addition and one multiplication modulo the target prime as one primitive each, giving 27 and 54. Multiplications only would give 18 and 36, and a higher price per modular multiplication scales both. Happy to use whatever you decide.
2. **Nominal 127 against the cost model's "128" sentence.** `nominal_reference` still reads "128 for selected 256-bit modern targets". Poseidon is 127 because its output space is the field order. I left that shared sentence alone rather than edit it unilaterally.
3. **Registration and baselines** are yours, as is whether the pair moves off 1, 2.
4. **`--require-complete` now passes.** Filling the last deferred slot takes `pending_tracks` from 4 to 0, so the gate now reports only that every slot has a definition, not that any lane has a baseline.

## Possible follow-up

My proposal argued for holding `R_F = 8` fixed and stepping `R_P` only, since a prefix cut removes the trailing full rounds that HADES uses against statistical attacks. I am happy to add that later as a separate variant family, for example `poseidon-rf8-rp{n}`, rather than replacing this one.

