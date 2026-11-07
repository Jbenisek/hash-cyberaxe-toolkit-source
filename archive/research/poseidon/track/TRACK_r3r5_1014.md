# Official Poseidon (Orchard) pareto track text, rounds 3-5 (owner paste 10-14)
- Distinct canonical input pairs (nk, rho), each 32-byte LE < p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001; state [nk, rho, 2^65].
- x^5; 8 full rounds at indices 0-3 and 60-63; the first r partial rounds starting at index 4 (r in {3,4,5}); pinned constants + MDS.
- Collision = entire final first field element, canonical 32-byte LE. Aliases, chosen capacity, full nullifier construction out of scope.
- Classical, success probability >= 0.39; justify total computation across all processors incl. preprocessing, randomness, failed trials, sorting, lookups, memory ops, recovery, amplification; memory in bytes.
- Score = timeLog2 + max(0, memoryLog2Bytes - 20); T in target-compression units, per-round normalization in the clone's cost model; memory < 1 MiB = one unit, fractional MiB above.
- Objectives: maximize rounds, minimize normalized cost. AI screening then human review; plausible_not_refuted is not acceptance.
- Self-contained proof.md + consistent claim.json; declared certificates/experiments; submission_state draft vs ready; judge does not fetch citations; each heuristic: evidence, tested scope, extrapolation, limitations.
- "Do not execute participant Python on the host"; keep previous submissions as evidence, never rewrite their candidates; edit only candidates/poseidon; run setup/checks before changes.
