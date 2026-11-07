# CR_UNITS - per-round unit C(r) check of Pareto filings (10-15)

Method: C(r) = `reference_operation_cost` printed by `pareto_candidate.py --family F --rounds R --show-contract` (run in WSL slot pos_b3r7b; word_operation weight = 1/C confirmed in each contract). Cost model collision-frontier-v5 (poseidon: orchard-field-ram-v2); scoring policy hashsmash-scalar-tm-v1 / hashsmash-orchard-tm-v1: normalizedTimeMemoryLog2 = timeLog2 + log2(max(1, memBytes/2^20)) = time_log2 + max(0, memory_log2_bytes - 20). Recomputed = log2(N / C_contract), N = the proof's total primitive-operation count. Read-only, no submissions.

Contract C(r): blake3 r3 638, r4 846, r5 1054, r6 1262, r7 1470 (=14+208r); sha3-256 r7 1897, r8 2168, r24 6504; sha256 r39 2812, r40 2896, r64 4912; poseidon r3 279, r4 300, r5 321, r56 1392 (=216+21r). All 15 match the unit the proofs state.

| id | family | r | C(r) contract | C(r) used | N | time_log2 claimed | recomputed | delta | mem_log2 claimed | official score | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 62cfd777 B3R3PV | blake3 | 3 | 638 | 638 | 2.3827e40 | 124.8123 | 124.812298 | +2e-6 | 20 | 124.8123 | OK |
| 75d5e1f9 B3R4 | blake3 | 4 | 846 | 846 | 4.5975e40 | 125.35348 | 125.353470 | +1e-5 | 20 | 125.35348 | OK |
| 41b32afc B3R4b | blake3 | 4 | 846 | 846 | 3.6582e40 | 125.02375 | 125.023744 | +6e-6 | 20 | 125.02375 | OK |
| staged B3R4c (pos_b3r4c) | blake3 | 4 | 846 | 846 | 3.6582e40 | 125.02375 | 125.023744 | +6e-6 | 20 | 125.02375 | OK (same as B3R4b) |
| a6ee439c B3R4d | blake3 | 4 | 846 | 846 | 3.7513e40 | 125.06 | 125.059993 | +7e-6 | 20 | 125.06 | OK |
| 86329045 B3R5 | blake3 | 5 | 1054 | 1054 | 4.5099e40 | 125.00855 | 125.008545 | +5e-6 | 20.37855 | 125.38710 | OK |
| 4e7607f1 B3R6 | blake3 | 6 | 1262 | 1262 | 5.5112e40 | 125.03801 | 125.038004 | +6e-6 | 20.64109 | 125.67910 | OK |
| 1cd0dd3b B3R7 | blake3 | 7 | 1470 | 1470 | 6.4910e40 | 125.05397 | 125.053968 | +2e-6 | 20.86686 | 125.92083 | OK |
| 8fbecd8a B3R7b | blake3 | 7 | 1470 | 1470 | 7.6457e40 | 125.29018 | 125.290175 | +5e-6 | 20 | 125.29018 | OK |
| f4f7b40e LS1R7 (slots ls1r7t/v, same claim) | sha3-256 | 7 | 1897 | 1897 | 4.9187e40 | 124.28591 | 124.285909 | +1e-6 | 20 | 124.28591 | OK |
| 3183c941 SHA3R7P | sha3-256 | 7 | 1897 | 1897 | 6.7125e40 | 124.73447 | 124.734467 | +3e-6 | 20 | 124.73447 | OK |
| staged SHA3R8 (pos_sha3r8) | sha3-256 | 8 | 2168 | 2168 | 7.9726e40 | 124.79004 | 124.790032 | +8e-6 | 20 | 124.79004 | OK |
| 606bcba0 SHA3R24 | sha3-256 | 24 | 6504 | 6504 | 2.7666e41 | 125.00008 | 125.000078 | +2e-6 | 20 | 125.00008 | OK |
| 01e31be9 S256R39 | sha256 | 39 | 2812 | 2812 | 1.1837e41 | 124.98494 | 124.984932 | +8e-6 | 20 | 124.98494 | OK |
| 368d1718 S256R39B | sha256 | 39 | 2812 | 2812 | 1.0766e41 | 124.84811 | 124.848105 | +5e-6 | 20 | 124.84811 | OK |
| staged S256R40 (pos_s256r40) | sha256 | 40 | 2896 | 2896 | 1.1202e41 | 124.863 | 124.862997 | +3e-6 | 20 | 124.86300 | OK |
| 5790b7ac S256R64 | sha256 | 64 | 4912 | 4912 | 2.0771e41 | 124.9915 | 124.991500 | 0 | 20 | 124.99150 | OK |
| 98b1c2c4 POSGEN | poseidon | 56 | 1392 | 1392 | budget form (units 1.711053e38) | 127.009 | 127.008152 | +8.5e-4 | 20 | 127.00900 | unit OK; claim rounded UP to 3 decimals (documented "rounded up"), delta > 1e-4 but in the safe direction |
| 83c8a1b1 POSGEN2 | poseidon | 56 | 1392 | 1392 | same as POSGEN | 127.009 | 127.008152 | +8.5e-4 | 20 | 127.00900 | same as POSGEN |
| 9f396ede POSR3E | poseidon | 3 | 279 | 279 | 4.5822e11 | 30.61314 | 30.613134 | +6e-6 | 28.062 | 38.67514 | OK |
| 3b99dfad POSR3F | poseidon | 3 | 279 | 279 | 4.6214e11 | 30.62543 | 30.625430 | 0 | 28.114 | 38.73943 | OK |
| 4086e210 POSR3G | poseidon | 3 | 279 | 279 | 3.1705e11 | 30.08182 | 30.081818 | +2e-6 | 27.9 | 37.98182 | OK |
| c4ee5996 POSR3H | poseidon | 3 | 279 | 279 | 3.1705e11 | 30.08182 | 30.081818 | +2e-6 | 27.9 | 37.98182 | OK (same N as POSR3G) |
| 39cb620f POSR4M | poseidon | 4 | 300 | 300 | 3.9924e12 | 33.63159 | 33.631582 | +8e-6 | 30.198 | 43.82959 | OK |
| cf167c24 POSR5M | poseidon | 5 | 321 | 321 | 9.2087e12 | 34.7397 | 34.739699 | +1e-6 | 32.577 | 47.31670 | OK |

Not covered: poseidon r56 has no staged non-generic slot besides POSGEN/POSGEN2; sha256-r39..r64 and sha3 slots filed before 10-14 (other tracks) were not in scope.

## Findings
- No unit mismatch: every proof uses the contract C(r); every claimed time_log2 equals log2(N/C) rounded up at the 5th decimal (delta 0 to +1.0e-5, claim never below the recomputation).
- Only delta > 1e-4: POSGEN/POSGEN2 (+8.5e-4), a deliberate round-up of 127.00815 to 127.009; safe direction, costs 0.00085 bit.
- Memory term: official board score = time_log2 + max(0, mem_log2 - 20). Entries claiming mem = 20 (all blake3 r3/r4/r7b, sha3, sha256, POSGEN) have zero memory term (a few sit at 2^19.9999 bytes, claimed as 20). B3R5/B3R6/B3R7 carry +0.37855/+0.64109/+0.86686, matching what FILINGS.md told the owner (125.38710, 125.67910, 125.92083). Poseidon r3/r4/r5 entries carry memory 2^27.9-2^32.6 bytes, so the official scores are ~38.0 / 43.8 / 47.3 (FILINGS.md shows these as "time+mem" only); the memory term (7.9 to 12.6 bits) is larger than the time number, so the owner should be told these Pareto scores are not ~30-35.
- Poseidon contract uses a different cost model id (orchard-field-ram-v2, policy hashsmash-orchard-tm-v1, same formula and 2^20 B unit); its C(r) = 216+21r (r3 279 ... r56 1392) is what the proofs use.
