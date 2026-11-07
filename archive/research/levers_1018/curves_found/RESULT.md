# curves_found: a map of every real collision we hold, and whether round R predicts R+1 (2026-10-18, research only)
Labels: COMPUTED = run here on the named file; DERIVED = arithmetic/argument on computed numbers; CLAIMED = someone's text, not checked.
Nothing filed, staged or submitted. No participant code run: hashes are OUR implementations (pos_ref.py loads our exp_line.py; hashes_own.py),
checked against organizer-recorded digests (20/20 per family x round, 24 rows, plus full-round hashlib) before use. Rival pairs are organizer output read as data.

## 1. What exists (COMPUTED; `collisions_found.jsonl.gz`, 29,028 distinct pairs, 16,435 ours; counts in `collisions_found_counts.tsv`, fig0)
| family | full collisions (distinct pairs) | partial / near pairs (organizer-checked) |
|---|---|---|
| Poseidon (ours, our runs) | r0 1, r1 106, r2 15, r3 5, r4 1, r5 1 = 129, all re-verified at their round with our reference | r7-r15 4,418 ours (line ladder 6-12 bit, birthday 14 bit); r21 652 (bradcush) |
| SHA-256 | r38: 8 ours (SFS compression pairs, Kissat S018/S019/S022/S023 models); r31 2,066 + r32 1 (rivals) | r40-r64 1,700 ours (16-18 bit); r32-r38 2,272 rivals |
| SHA3-256 | r5: 107 distinct (9 in our dossiers) | r5-r24 6,857 (ours 3,837) |
| BLAKE3 | r1: 1,279 (766 ours) | r2 6,714 (2,875 ours), r3-r7 2,693 ours |
Not in the set: rival Poseidon collisions (their proofs in our tree carry only the printf template); Luna S016 r17 models (not decoded here); the 142,035 failed organizer trials (kept in `dossier_trials.jsonl`, unused).

## 2. Poseidon: the shape is one family of lines, and it does not move with the round (COMPUTED, `analyze_poseidon.py`, fig1/fig2/fig5c)
- All 129 full collisions lie on 3 lines of the plane U=(nk+c0)^5, V=(rho+c1)^5: line j=0 holds 62 (every r0, r3, r4, r5 pair, 14/15 r2, 40 r1),
  the other two hold 32 and 30 (r1 lean builds, one two-family r2); 5 two-family pairs sit on lines of their own. 55 of the 56 j=0 pairs
  with a recorded centre have W1+W2 = 2c (anti-diagonal in fig1; the odd one is exec_r2_line2, another parametrisation).
  This is the attack's own construction (the line does not depend on r), not a discovery.
- R does not predict R+1: the same 129 pairs re-hashed at every other round 0..10: 0 of 1,290 collide; leading-bit agreement mean 1.03 bits (random 1.0).
  Organizer Poseidon pairs (r7-r21, 5,070 distinct, ladder + birthday) re-hashed at R-1/R+1/R+2 on the same mask: 19/27/33 hits vs 29.5 expected each.
- Rates follow the random-root model at every round: ladder success over r8..r21 x w6..12: chi2 30.5 on 28 cells; first-hit s means on the truncated
  geometric; extra agreeing bits beyond the mask mean 0.87-1.20 (random 1.0). Per-centre success at r1: 104/259 = 0.402 vs 1-e^-1/2 = 0.393 (z 0.3);
  r2 8/16. Root positions s on j=0: KS D 0.182, n 62, p ~0.03 (DERIVED; one test of ~20 here, not significant).
- Reading: each round's collisions are the square roots of a fresh polynomial g_r; the map has the line and nothing else. This matches
  `research/beyond_bday/poseidon/RESULT.md` (counting statistics random from r3, algebra not). No lever from the map.

## 3. Other families: three real "carry" curves, none below generic (COMPUTED, `analyze_bits.py`, `forward_dig.py`, fig3-fig5)
- SHA3-256 r5 collisions -> r6 (fig5b): the 107 pairs have r6 digest-difference weight mean 71.0 (min 48, median 69; random 128 +- 8),
  and 36 bit positions are zero in all 107; at r7 weight 127.1 (random), r8 127.7. The carry lasts exactly one round.
  Lever test (DERIVED, per-bit independence assumed): zeroing the remaining bits from fresh r5 pairs costs ~151 bits per r6 collision > 128 birthday. Not a lever.
- Our SHA-256 r38 SFS pairs -> r39 (fig5a): difference 0 at steps 25..38, then at step 39 exactly dW38 (mod 2^32) in words A and E, all 8 pairs.
  dW38 = sigma0(W23') - sigma0(W23) and sigma0 has GF(2) rank 32 (COMPUTED), so dW38 != 0 for every P8 pair: the 38-step wall is exact for P8;
  39 needs another characteristic. Steps 40/41: weight 48-69 / 83-100.
- BLAKE3 r2 -> r1: every 128/136-bit r2 near-collision in the dossiers (7 experiments, 6+ owners, up to 300 sampled each) is a FULL r1 collision.
  r2 -> r3 random (mask-bit agreement 0.50). The 4,487 128-bit r2 pairs carry 15 biased outside-mask bits (|z| 6-24, same across owners;
  e.g. word3 bit19 agrees 0.678, word1 bit0 0.373). Net information sum(-log2 q) = 127.75 of 128 bits: 0.25 bit (DERIVED). Not a lever.
- Everything else is flat: 85 masked groups, outside-mask agreement |z|>3 in 2 only (blake3 r2 residual-search, rival sha3 r5 round2-mask); Holm over 19,319 per-bit tests: 136 hits,
  all in blake3 r2 (55) and the rival sha3 r5 "round2-mask" set (81, a near-full-agreement set). One-round-on mask agreement 0.47-0.54 in 115 of
  139 groups; the rest are the SHA3 r5 pairs, and 2 SHA-256 groups (0.72-0.75; total weight drops only 128 -> 123-125, the state shift register).
  Our rows r40-r64 (SHA-256), r8-r24 (SHA3), r3-r7 (BLAKE3): no extra bit, no carry.

## 4. Answer
- Counts per family/round: section 1. Structure: lines (Poseidon, by construction), one-round carries (SHA3 r5->r6, SHA-256 shift,
  BLAKE3 r1->r2 by design), 15 biased BLAKE3 r2 bits. Chance baselines given with each.
- Does the set at R predict R+1? Poseidon no (0/1,290; 79 hits vs 88.5 expected). Hash families: only for one round, and every carry
  costs more than the generic bound at the next round (SHA3 r6 ~151 > 128; SHA-256 P8 at r39 impossible; BLAKE3 0.25 bit).
- No lever at a live row from the empirical map. The 2-D shapes are the attack constructions we already use.
- Not tested (open, each <= 20 min): decode Luna S016 r17 models into pairs; r6 SHA3 cost with measured pairwise bit correlations instead of
  independence; fetch rival Poseidon pairs (0xshikhar r1-r5) from GitHub raw and add them to the line map.

## Files (all in this folder)
collect_dossiers.py -> dossier_trials.jsonl (196,096 organizer trials), dossier_experiments.tsv; id_owner.json (board ids -> owner);
build_poseidon.py + pos_filelist.txt -> poseidon_full_collisions.jsonl; analyze_poseidon.py -> poseidon_analysis.json, fig1, fig2;
hashes_own.py; analyze_bits.py -> bits_analysis.json, fig3, fig4; forward_dig.py -> forward_dig.json; sha3_r6_carry.py; sha256_r38_sfs.py;
build_dataset.py -> collisions_found.jsonl.gz, collisions_found_counts.tsv; plot_summary.py -> fig0, fig5; centre_summary_files.txt.
Plots need Python 3.11 (user-home/AppData/Local/Programs/Python/Python311/python.exe has matplotlib; the default python does not).
