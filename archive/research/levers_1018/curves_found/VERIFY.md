# VERIFY curves_found (2026-10-18, adversarial, research only; nothing filed, no participant code run)
Verdict: core claim CONFIRMED (no lever at a live row from this map; no carry beats generic at R+1). REDUCED on 6 details.
Scripts/logs in `verify/` (v1-v6, v5_sweep_*.json/log); hashes are OUR hashes_own.py / pos_ref.py only.

## Confirmed (recomputed here, COMPUTED)
- 29,028 distinct pairs / 16,435 ours; SHA3 r5 107 and BLAKE3 r1 1,279 distinct by organizer da==db (v1_counts.py).
- Poseidon: ladder chi2 30.5 on 28 cells; cross-round 19/27/33 hits vs 29.5 each on 5,070 pairs. New sweep of all 5,070 at every
  round 1..R+2: 0 hidden full collisions, full-digest weight 121-131 per group (random 128). Note: "0 of 1,290" has ~0 expected hits, so it only rules out a deterministic carry.
- SHA3 r5->r6: weight mean 71.0 (min 48), 36 always-zero bits, per-bit model 151.2; r7 weight 127.1 (random).
- SHA-256 P8: dW != 0 only at W7-11,15,16,23,25 below 38; dW22=dW31=dW36=0, so dW38 = s0(W23')-s0(W23) != 0 in all 8; r39 diff = dW38 in A and E (v3).
- BLAKE3: ALL 5,766 distinct 128/136-bit r2 pairs (not a sample) are full r1 collisions; r3 mask agreement 64.9/128 (v4). Bias gain 0.25 bit (127.75) (v6).
- Our rows: masked agreement at R-1/R+1 within 0.4 bit of chance in every SHA3 r6-r24, BLAKE3 r2-r7, SHA-256 r37-r64 group (v5 sweep).

## Reduced
1. SHA3 r6 cost with measured correlations (4 digest bits of one chi row taken jointly): 137.5 bits; per-byte joint 140.3; not 151.2 (v2).
   Still > 128 and excludes the cost of each r5 pair, so "not a lever" holds, margin 9.5 bits not 23. Both extrapolate 107 samples to a
   2^-137 event (DERIVED model). sha3-256-r6 is not in the local clone's pareto/target-profiles (Pareto SHA3 = r1-r4, r7-r24); r5->r7 is random.
2. The 8 SHA-256 r38 pairs are not collisions of any target: CV != IV in all 8 (COMPUTED); r38 and r39 profiles put "compression-only or
   free-start collisions" out of scope. The r39 wall is right but concerns no live row; the summary lists them as "full collisions".
3. "All 129 Poseidon collisions on 3 lines": 124 on 3 lines (62/32/30), 5 on own lines, 8 lines in all (poseidon_analysis.json). RESULT body correct, summary not.
4. Inventory misses hidden collisions (v5 sweep): +5,766 BLAKE3 r1 (the r2 128/136 pairs; total 7,045, 3,898 in our dossiers);
   2,158 SHA3 r1 (every r6-r24 22/18-bit pair that is a full r1 collision; 1,732 ours); SHA-256 r1-r13 trivial (late-word differences). Rows at floor: no lever.
5. Ownership: SHA3 r5 "9 ours": 17 of 107 appear in our dossiers, 2 only in ours; sha3_r6_carry.py prints 14 (last-seen dossier). Inconsistent label.
6. "r1 per-centre 104/259 = 0.402" and the first-hit fits: no script or saved output in the folder computes them. Label CLAIMED until saved.

## Places RESULT left untested (found here; places, not levers)
- SHA3 r5 collisions are 2-bit near-collisions at r3 and r4 (HW min 2, mean 3.1 / 5.0): compare with our SHA3 r3/r4 Pareto row scores (not read here).
- SHA-256 masked pairs carry BACKWARD: full-digest weight 118-121 at R-1..R-3 in every group (shift register); nothing at R+1.
- BLAKE3 r3/r4 pairs (ours) are r1 near-collisions (weight 58-63); r2 random. Open from RESULT: Luna S016 r17 models; 0xshikhar Poseidon pairs.
- Unused: 142,035 failed organizer trials (near misses never scanned).
