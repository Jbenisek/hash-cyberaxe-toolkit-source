# SCOUT_RECENT.md: what is new since 2023, and one new lever found by following it

Folder: research\newpaths\scout_recent. Written 2026-10-08. Research only: nothing submitted, posted or run on
Yukon; nothing outside this folder modified. Tags: COMPUTED = run here (file named); DERIVED = read from a cited
source or argued from stated facts; GUESS = judgement, not checked.

## 0. Bottom line

1. NEW LEVER (COMPUTED at word level, verified at 32 bits; value is a GUESS): **collide a NON-ROOT chunk, not the
   root.** A message of t full chunks plus a last chunk of 55 or 63 bytes is hashed as a tree; the last chunk's
   chaining value is one 2-round compression with counter v12 = t (any 32-bit value), v13 = 0, flags
   CHUNK_START|CHUNK_END = 3. If two such last chunks (same t, same prefix) have equal chaining values, the two
   full messages collide. The chunk index t is a free 32-bit word per trial (shared by A and B).
   In the team's own word-level model this tenth free word breaks the "no second prescribed word" proofs:
   - with the counter fixed at 0 (as in every earlier run): Y4 + E1.d1 and Y4 + E3.h1 have NO basis (re-proved here);
   - with the counter free: bases exist for Y4 + E1.d1, Y4 + E3.h1, Y4 + E3.g1, Y4 + E3.e2, Y4 + Y14, Y4 + Y6
     (pin H8; the w14-free set too). Y4 + E1.b1, E1.a2, Y9, Y1, w8 stay NO; three words (Y4, E1.d1, E3.h1) stay NO
     even with the high counter word free.
   - Best arrangement found: Y4 fixed per outer step, **E1.d1 is the inner loop word**, varied inside the
     heavy-beta cube of the team's T1 prize. Per trial only 3 equations reach the E1.b1 test, 5 reach E3.h1, 8 reach
     E3.e2 (present first test: 11). Varying E1.d1 changes only 17 of 100 words: E1, E3, C2's outputs, w0, w1,
     K0.a1 and T0; the whole round-0 state stays fixed. The counter absorbs w0.
   - Checked on real arithmetic: 2,000 random assignments per arrangement at 32 bits (all 100 internal words equal
     the real compression with counter T0 and flags 3, digest words 0, 2, 5, 7 of the 55/63 pair agree, T0 < 2^32);
     3,000 per arrangement at toy width 8; the tree claim on the organizer's own verifier/blake3.py (360 of 360).
   - Value (GUESS, from team figures I did not re-derive): HANDOFF 17:33/17:35 put T1 = "c1 in the heaviest beta's
     cube" at 905x (2^9.8). The team's own block study (research\h8\block\BLOCK_REPORT.md) could force T1 only at
     18,611 operations per forced trial against a break-even of about 11,700, and so dropped it. Here it is forced
     at no cost and the trial gets cheaper. If the 905x holds and the batch is recounted, that is worth roughly
     8 to 10 bits on the 55/63 path: 93.0 becomes roughly 83 to 88. Not counted on a real program yet.
2. LITERATURE since 2023 (DERIVED from the sources in section 2): no new cryptanalysis of the BLAKE3 hash setting.
   The only BLAKE3 paper is a boomerang on the keyed permutation (ePrint 2023/299). The relevant new tools are ARX
   meet-in-the-middle with carry rules (dual syncopation, EUROCRYPT 2026), the SHA-2 collision records of 2024-2026
   (SAT/SMT signed-difference search, memory-efficient condition MITM) and programmatic SAT. Generalized birthday
   work (CRYPTO 2026) does not help a 2-list collision. Section 2 gives the URL and the exact transfer for each.
3. BOARD (DERIVED from public PRs, 2026-10-08): two new entries at 93.0451 (GordoAR, PR #599) and 93.01972
   (winglock, PR #606). Both are the same 55/63 path with the H1 margin cut from 2.0 to 1.4
   (F = 185,350,144 x 5/7 = 132,392,960). Nothing on another path was visible in the PRs I read.

## 1. The chunk-counter lever in detail

### 1.1 Why it is legal (DERIVED from the target profile; COMPUTED on the organizer verifier)
- target-profiles\blake3-r2-prefix-v1.json: the message domain is any byte string below 2^64 bits; the tree is
  "standard binary tree over 1024-byte chunks with 64-bit zero-based chunk counters"; only the ROOT compression
  has counter 0. verifier\blake3.py `_compress`: `v = cv + IV[:4] + [counter & MASK, counter >> 32, len, flags]`.
- For N = t+1 >= 2 chunks the root is a PARENT node; the last chunk (index t) is an ordinary chunk with flags
  CHUNK_START|CHUNK_END = 3 when it is a single block. Its CV is the first 8 output words (v[i] ^ v[i+8]), the
  same formula as the digest. Equal CVs give identical trees, hence identical digests.
- tree_check.py: for t in {1,..,7,11,16}, lengths 55 and 63, 20 messages each: organizer digest of P||X equals
  tree_root(prefix CVs, CV_t(X)) in 360 of 360, and CV_t(X) = compress(IV, X, counter t, len, 3). COMPUTED
  (tree_check.txt).
- Cost: hashing the final pair costs about t compressions (t < 2^32), negligible. The message length is up to
  about 2^42 bytes; that is inside the domain, but how an AI judge reacts to a 4 TiB message is a GUESS (risk).
- The earlier dismissal (fringe\RESULTS.txt angle 10: "root counter is always 0") is correct for the root only.
  The root does not have to be the colliding compression. DERIVED.

### 1.2 Mechanism (DERIVED; COMPUTED in inner_check_B10.txt)
K0 = G(IV0, IV4, IV0, t; w0, w1): a1 = IV0 + IV4 + w0, d1 = ROR(t ^ a1, 16). With t fixed (= 0), w0's round-1
use (C2's y word) is tied to K0's round-0 state through d1 = ROR(a1, 16). With t free, t = ROL(d1, 16) ^ a1
absorbs any w0: the whole round-0 state stays fixed while w0 takes any value. In GD terms the equation
"K0.d1 <- K0.a1" gains an unknown, so the system has 10 free words instead of 9 (9 instead of 8 with w14 pinned).
The high counter word t >> 32 (v13, K1's d input) is limited to 19 bits by the 2^64-bit length bound: solving
for it succeeds with probability 2^-13, so it is a filter, not a free word.

### 1.3 Tests run (all COMPUTED; kissat via WSL, at most 2 processes)
Tools: basis_search_ctr.py / basis_sat_ctr.py = copies of research\night\main\basis_search.py / basis_sat.py with
one change: env COUNTER=1 puts an unknown T0 in K0's d input (COUNTER=2 also T1 in K1); COUNTER=0 is the original.

| Question (pin H8 = PIN_EXTRA=w14 unless noted) | COUNTER=0 | COUNTER=1 | file |
|---|---|---|---|
| basis with Y4 + E1.d1 | NO (proved) | YES | ctr_pairs_w14_main.txt |
| basis with Y4 + E3.h1 | NO (proved) | YES | ctr_pairs_w14_main.txt |
| Y4 + E3.g1 / E3.e2 / Y14 / Y6 | (team: NO) | YES each | ctr_pairs_c1_w14.txt |
| Y4 + E1.b1 / E1.a2 / Y9 / Y1 / w8 | (team: NO) | NO (proved) | ctr_pairs_c1_w14.txt |
| w14-free pinned set: Y4 + E1.d1, Y4 + E3.h1 | NO, NO | YES, YES | ctr_pairs_c1_pinB.txt |
| Y4 + E1.d1 + E3.h1 with T0 and T1 free | - | NO (proved, COUNTER=2) | cone3_triple_c2.txt |
| Y4, E1.d1 both fixed per outer step: fewest words recomputed per inner step before E3.h1 | - | 34 (none <= 32) | cone_E1d1_B*.txt, cone2_*.txt |
| Y4 fixed, inner word free to choose (solver picks E1.d1): words per trial before E1.b1 / E1.a2 / E3.h1 / E3.g1 / E3.e2 | - | 3 / 4 / 5 / 6 / 8 | cone4_E1b1_B10.txt, B20 |
| Y4 + E3.h1 fixed: per trial before E1.d1 | - | 37 | cone3_E3h1_B40.txt |

Real-arithmetic checks of the arrangements (order files order_Y4_E1d1.txt, order_Y4_E3h1.txt, cone4_E1b1_B10.txt):
- verify_ctr.py (32 bits, H8 pins copied from research\h8\design\h8_ref.py): 2,000 assignments each, internal-word
  mismatches 0 (100 words), half-collision 0/2/5/7 failures 0, counter out of range 0 (verify32_*.txt).
- verify_ctr_toy.py (w = 8, rotations 4/3/2/1, IV low bytes, random consistent toy pins): 3,000 assignments each,
  mismatches 0; one basis word over all 2^8 values gives 256 distinct (T0, message) pairs (toy8_*.txt).
  The toy pins do not have the H8 half-collision property, so the toy run checks the parametrisation only.
- inner_check.py (32 bits): outer words fixed, E1.d1 drawn inside the cube c1 & 0e09818b == 02008000 (the T1 cube
  named in HANDOFF 17:35): 300 of 300 trials have c1 in the cube, real-compression mismatches 0, half-collision
  failures 0; words that change with E1.d1: E1.a1 E1.a2 E1.b1 E1.c1 E1.d1 E3.e2 E3.f1 E3.g1 E3.h1 K0.a1 T0 Y10
  Y14 Y2 Y6 w0 w1; Y4, Y12, Y1, w12, Y9, w8, w5, C2.b1, C2.c1 stay fixed (inner_check_B10.txt).

### 1.4 What is NOT shown (be honest about it)
- The 905x value of T1 and the 2^6.5 of the h1 pattern are the team's figures (HANDOFF 17:33 and 17:35 bullets),
  not re-derived here. GUESS that they carry over unchanged. The counter changes no word that the residual event
  reads (E1, E3 inputs, pins), so the H1 rate model is the same model. DERIVED.
- No batch was built and no trial cost was counted. The "3 / 5 equations per trial" figure counts G-assignment
  equations in the word model only.
- No toy end-to-end collision with the counter was run: that needs a toy pin with the 55/63 half-collision
  property and the team's 8-bit rate machinery (r2_toy8y and similar), which I did not touch.
- Whether a stronger choice than "the heaviest beta cube" exists is open. E1.d1 is fully prescribed, so the inner
  loop can run over the best c1 values directly, and (Y4, c1) can be chosen jointly. GUESS: at least 905x.
- Judge risk: very long messages (up to ~2^42 bytes) and a non-root colliding compression. GUESS.
- Family / "fix half the digest, then birthday" ideas do NOT gain: a collision needs both members at the same t,
  so t is a family constant there, not a per-member unknown; the 4-check floor is untouched. DERIVED.

### 1.5 Suggested next steps for the main thread (not done here)
1. Have the owner of the h8 counter (Job A engine / Sol counter) confirm the T1 rate with E1.d1 held in a cube and
   Y4 fixed per outer step (same H1 model, so a re-read of the existing table should suffice).
2. Build the inner loop: per trial E1.a1 = ROL(d1,16) ^ Y12; Y6 = E1.a1 - Y1 - w12; E1.b1 test; then Y10, Y14
   from C2's second half, E3.h1 test. w0, w1, T0 only for survivors (order in cone4_E1b1_B10.txt, lines marked *).
3. A toy end-to-end at 8 or 10 bits with the counter (real collisions counted against the prediction), as the
   team's rule requires before a package.
4. Check flags 3 vs 11 does not change any pin (verify_ctr.py already uses flags 3 with the H8 pins: 0 failures).

## 2. Literature since 2023 (each with what could transfer)

| Item | What it does | What could transfer, exactly | Verdict |
|---|---|---|---|
| Hao, Wang, Jiao, Gong, "Approximate Modeling of Signed Difference and Digraph based Bit Condition Deduction: New Boomerang Attacks on BLAKE", ePrint 2023/299, https://eprint.iacr.org/2023/299 (local papers\2023_299.txt) | Boomerangs on the KEYED PERMUTATIONS: full 7-round BLAKE3 at 2^180, BLAKE2s +0.5 round, BLAKE-256 8 rounds 2^16 faster. Approximate signed-difference MILP model for ARX plus digraph-based automatic bit-condition deduction. DERIVED | Not an attack on the hash. The tool could search 1.5-round trails restricted to differences in E1/E3 inputs (LITERATURE.md 4.7) and deduce bit conditions automatically. The paper says its code "will be publicly available" when published; I found no URL. | needs more |
| Guo, Li, Liu, Wang, Zhang, "Dual-Syncopation Meet-in-the-Middle Attacks: New Results on SHA-2 and MD5", EUROCRYPT 2026, ePrint 2026/353, https://eprint.iacr.org/2026/353, code https://github.com/desert-oasis/dual-sync-MITM (local papers\2026_353.txt) | Rule language for forward/backward-independent bits through ARX: carry-preventing (x_i = y_i: lower bits do not reach higher carries), carry-preserving (y_i = c_i), constant-sum; MILP automation; first preimages on 46/47-step SHA-256, 51-step SHA-512; free-start collisions via Li-Isobe-Shibutani. Section 6: a t-bit partial-target preimage at 2^s gives a collision at 2^s * 2^((n-t)/2), useful only if s < t/2. DERIVED | Bit-level splitting of the residual: our word-level MITM split 0 bits; these rules buy bit-level independence for carry conditions. Their collisions are free-start, so no direct use. A test would be to apply the carry-preventing rule to E1/E3 with the outer words as "public". | needs more |
| Li, Zhang, Li, Liu, Qian, Zhu, "Pushing Collision Attacks on SHA-2 to 39 Steps", ePrint 2026/1120, https://eprint.iacr.org/2026/1120 (abstract only) | 38-step SHA-256 2^104.3, 38-step SHA-512 2^125.4, 36-step SHA-256 2^57; memory-efficient MITM to meet the uncontrolled conditions. DERIVED | Relies on SHA-2 message expansion and local collisions; BLAKE3 has only a word permutation. The condition-MITM idea is the one our residual MITM already tried (0 bits). | dead |
| Li, Liu, Wang, Shi, "Pushing the Limit of Memory-efficient Collision Attack Framework for SHA-2", CRYPTO 2026, ePrint 2026/1080, https://eprint.iacr.org/2026/1080 (local papers\2026_1080.txt) | First practical 35-step SHA-256 and SHA-512 collisions; SAT/SMT characteristic search over chosen message-difference sets. DERIVED | SAT/SMT signed-difference tool chain only. | dead |
| Li, Liu, Wang, Qian, Jia, Kong, "New Collision Attacks on Round-Reduced SHA-512", 2025, https://link.springer.com/chapter/10.1007/978-3-032-01901-1_7, slides https://iacr.org/submit/files/slides/2025/crypto/crypto2025/144/144_slides.pdf | 29-step practical SHA-512, 31 steps 2^97.3 -> 2^85.5; a model of 2-bit conditions in signed differences. DERIVED (search abstract) | 2-bit conditions are the analogue of our carry-coupled bit pairs; useful only inside a trail search. | dead for now |
| "Collision Attacks on SHA-256 up to 37 Steps with Improved Trail Search", https://link.springer.com/chapter/10.1007/978-3-032-25333-0_4 (CRYPTO 2026 per 2026/1120) | Abstract not readable (Springer login redirect). | - | not read |
| Li, Liu, Wang et al., "The First Practical Collision for 31-Step SHA-256", ASIACRYPT 2024, https://link.springer.com/chapter/10.1007/978-981-96-0941-3_8 | 1.2 h on 64 threads; memory-efficient framework. DERIVED (search abstract) | as above | dead |
| Alamgir, Nejati, Bright, "SHA-256 Collision Attack with Programmatic SAT", PAAR/SC-Square 2024, https://arxiv.org/abs/2406.20072 | CaDiCaL plus an IPASIR-UP propagator doing differential/algebraic reasoning: SFS collisions up to 38 steps; plain SAT only 28. DERIVED (abstract) | The fringe agent's bit-level SAT sampler (angle 7) failed with plain kissat/cadical at w = 6 to 8. A programmatic propagator that reasons on modular-addition carries is the published remedy. | needs more |
| Tang, Sun, Gong, "On the Regularity of the Generalized Birthday Problem", CRYPTO 2026, ePrint 2025/1351, https://eprint.iacr.org/2025/1351, code https://github.com/tl2cents/Generalized-Birthday-Problem | k-list vs single-list GBP, ISD-based framework, iSHAKE256 2^256 -> 2^189. DERIVED (abstract) | k = 2 (a collision) is plain birthday; no XOR split of our digest into independent lists exists (fringe angle 9). | dead |
| Zhang, Hou, Liu, "Probabilistic Linearization: Internal Differential Collisions in up to 6 Rounds of SHA-3", CRYPTO 2024, https://eprint.iacr.org/2024/1136; "Collision Attacks on Round-Reduced SHA-3 Using Conditional Internal Differentials", EUROCRYPT 2023, https://link.springer.com/chapter/10.1007/978-3-031-30634-1_8 | Two-block collisions: the first block prepares a chaining state that meets conditions for the second (connector). DERIVED (abstracts and search snippets; the CV-condition counts were not readable) | The idea "make the colliding compression's fixed inputs attacker-chosen through the mode" led to section 1: in BLAKE3's tree mode, the chunk counter is such an input, set legally by the message length. | alive (via section 1) |
| Wang, Liu, Hou, Hou, Lin, "Moving a Step of ChaCha in Syncopated Rhythm", ePrint 2025/2334, https://eprint.iacr.org/2025/2334; "A New Approach to Improved PNB-based Attacks on Reduced-round ChaCha and Salsa", ePrint 2025/1830, https://eprint.iacr.org/2025/1830 | PNB key recovery with syncopation and carry-preserving tricks (backward direction). DERIVED (abstracts) | Neutral bits for the half-fixed family were already 0 at w = 8 and 32 (fringe angle 6); these are key-recovery PNBs. | dead |
| Differential meet-in-the-middle papers: https://eprint.iacr.org/2025/1249 (AndRX/SIMON), https://eprint.iacr.org/2025/1911 (Feistel), "Improved Differential MITM Cryptanalysis" EUROCRYPT 2024 https://link.springer.com/chapter/10.1007/978-3-031-58716-0_10 | block-cipher key recovery. DERIVED (search snippets) | none for a fixed-IV hash | dead |
| "CryptanalysisBench: Can LLMs do Cryptanalysis?", arXiv 2607.18538, https://arxiv.org/abs/2607.18538 | LLM benchmark (July 2026). Abstract names no BLAKE target. DERIVED | none | - |

Searches that found nothing new (DERIVED): ePrint title search "BLAKE3" (https://eprint.iacr.org/search?q=BLAKE3:
8 hits, only 2023/299 is cryptanalysis); web searches for BLAKE2/BLAKE3 reduced-round attacks 2024-2026; for the
BLAKE counter as attacker freedom in a hash-mode attack. I found no publication that uses the BLAKE3 chunk
counter this way; novelty is a GUESS (search coverage limited).

## 3. HashSmash public material read (2026-10-08)
- https://github.com/Layr-Labs/hash-smash/pulls?q=is%3Apr+blake3-r2 (list of recent PRs; titles only for most).
- PR #606 (winglock, 93.01972) and #599 (GordoAR, 93.0451): margin 1.400 on F_H1 = 132,392,960; success floor
  0.39; 55/63 path; #606 notes "the thinnest margin in this lineage". PR #523 (leech1996, 94.24): BUDGET[0] change
  only. PR #383 (Th0rgal, 111.75, older). PR #602 is sha256-r32 (not ours). DERIVED.
- Launch press release (2026-10-05): https://www.prnewswire.com/news-releases/preparing-the-worlds-cryptography-for-the-ai-era-eigen-labs-and-zcash-organization-shielded-labs-launch-hashsmash-an-open-multiplayer-competition-to-test-how-far-ai-can-advance-attacks-on-widely-used-hash-functions-302897508.html

## 4. Limits
- eprint.iacr.org returns 403 to direct PDF fetches; 2026/353, 2023/299 and 2026/1080 came from web.archive.org
  copies (papers\). 2026/1120 had no archived PDF (abstract only). Springer chapter pages need a login.
- Only the PRs named above were read in full; the rest of the board was not surveyed.

## 5. Files (all in this folder)
basis_search_ctr.py, basis_sat_ctr.py (copies with the COUNTER option), ctr_pairs.sh, ctr_order.sh,
ctr_cone.sh, ctr_cone2.sh, ctr_cone3.sh, ctr_cone4.sh (runners); ctr_pairs_c1_w14.txt, ctr_pairs_c1_pinB.txt,
ctr_cone_run1..4.txt, cone*_*.txt, order_Y4_E1d1.txt, order_Y4_E3h1.txt (solver outputs and solving orders);
verify_ctr.py, verify_ctr_toy.py, inner_check.py, tree_check.py (checks) with outputs verify32_*.txt,
toy8_*.txt, inner_check_B10.txt, tree_check.txt; papers\ (2023_299, 2026_353, 2026_1080 PDF + text).
Baseline runs (COUNTER=0, both pinned sets) give NO basis for Y4 + E1.d1 and Y4 + E3.h1: ctr_pairs_w14_main.txt
(pin H8) and ctr_pairs_c1_pinB.txt (w14-free set). Re-run: `wsl -d Ubuntu -- bash <folder>/ctr_pairs.sh 0 w14 60
E1.d1 E3.h1` (COUNTER, PIN_EXTRA, time limit, targets).
