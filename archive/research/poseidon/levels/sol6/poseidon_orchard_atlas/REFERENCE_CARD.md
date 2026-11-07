# Reference card — Orchard Poseidon, pinned research atlas

Date: 2026-10-12. Target proposal: HashSmash PR923, head 01f736268b7086d97f38837d343d63a81bf31649. The retrieved PR is open/unmerged and does not register Yukon tracks. A live UI change must be checked against its actual deployed profile before filing.

## Exact identity
- Pallas **base** prime: `0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`.
- State 3, rate 2, capacity 1; S-box exponent 5.
- Deployment RF8/RP56: full round indices 0..3 and 60..63; partial 4..59.
- Proposed tracks prefix 1/prefix 2; both are full-round prefixes.
- Add constants -> S-box -> MDS. No fresh message injection between rounds.
- Input exactly 64 bytes: m0,m1 each 32-byte **little-endian canonical** integer less thanp.
- Initial state `[m0,m1,36893488147419103232]` = `[m0,m1,2^65]`.
- Output state lane 0,32-byte little-endian canonical field encoding.
- Reject x+p encodings and wrong lengths. No extra padding block at ConstantLength<2>.
- Constants are always generated for RF8/RP56, never for the truncated round count.
- Difference convention throughout: delta = second value minus first modulo p, not XOR.
- Matrix multiplies a column vector from the left.

## Validated here
11 hash vectors +3 permutation vectors;1024 round inversions;1024 independent formula replays;19 nonzero MDS minors;432 partial chart identities;2048 low-round chart identities. Scope and counts are in data/results.json and reports/RESEARCH_REPORT.md.

## Never transfer these assumptions
SHA parity ranks, SHA/BLAKE operation-unit prices, free intermediate inputs, independent per-round probabilities, an alleged complete-state merger, or native rates inferred from p257 experiments.

## Evidence labels
PROVED = shown algebraically with stated domain. COMPUTED_EXACT = exact finite calculation in the named field or finite set. SAMPLED = finite diagnostic only. EXACT_TOY = exhaustive different small field. SOURCE = source claim not newly reproduced. OPEN = no result. Neither local proof nor an indexed grid cell means global attack optimality.

Sources: https://github.com/Layr-Labs/hash-smash/pull/923 ; https://github.com/Annkkitaaa/hash-smash/blob/01f736268b7086d97f38837d343d63a81bf31649/verifier/poseidon.py ; https://github.com/zcash/halo2/blob/halo2_poseidon-0.2.0/halo2_poseidon/src/lib.rs.
