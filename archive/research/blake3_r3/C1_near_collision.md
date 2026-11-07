# B3R3-C1: near-collision of first-block CVs + free final block, 3 rounds, target < 2^125

Labels: PROVED / COMPUTED / GUESS. Files: C1_act5.cpp (activity, sparse version of act4.cpp with CV-word start), C1_climb.c, C1_climb_r*_k*.txt.

## Setting (as given)
Block 2 = compress(CV, m, counter 0, len 64, flags CHUNK_END|ROOT), 3 rounds, digest = v[i]^v[i+8], i<8. CV, CV' differ in k of 8 words; blocks m, m' same or different.

## (a) Can 3 rounds cancel a k-word CV difference?
1. PROVED (algebra, same block m=m'): each G is a bijection of (a,b,c,d) for fixed message, so any CV difference stays active in the column/diagonal it enters. After round 0 it occupies one column, after round 1 all 4 diagonals (CV words 0,4,8,12 map to 4 different diagonals), so all 16 words are active entering round 2. Cancellation then needs 8 digest-word equalities by chance. No cheap cancellation with m=m'.
2. PROVED (algebra, different blocks): a difference d in an a-slot CV word (words 0..3) is cancelled in the very first G half-step by m_x' = m_x - d (a = a+b+m_x is then equal; every other word of that G is equal). But that message word is reused in rounds 1 and 2 (PERM), so the cancelled difference reappears as a message difference there. A b-slot word (4..7) cannot be cancelled this way (b is used again in b=(b^c)>>>12). So differing blocks convert a CV difference into a message difference; they do not remove it.
3. COMPUTED, word-level activity model (C1_act5, same generous rules as act4: a G call with k active message words may silence up to BUD*k of its 4 outputs; check = digest word with an active side; initial activity = k CV words, v8..v15 equal; message-difference set D free):
   - 3 rounds, BUD=1, |D|<=5, k=1 and k=2: min checks = 6 (hist: 6:1680 / 5880 sets, none lower). |D|<=3: 7.
   - 3 rounds, BUD=2, |D|<=3: min 6 for k=1,2. (For reference 1 round: 4 checks at BUD=1, 0 at BUD=2; 2 rounds: 7 / 4.)
   - 3 rounds, BUD=2, |D|<=5, k=1: min 0 at D={7,10,12,14} (CV word 3 or 7). This is a model artifact: the same D gives 0 with NO CV difference in the earlier one-block run (act_r3_D5.txt), because BUD=2 lets one message word silence two outputs, which a G call cannot do. Not trusted. (k=2 at |D|<=5, BUD=2 timed out; not run.)
   So the model's honest-leaning minimum is 6 active digest words = 6 x 32 = 192 bit conditions.
4. COMPUTED, exact 32-bit experiment (C1_climb.c, real BLAKE3 round function, random CV pair with k=1 (word 0) and k=2 (words 0,4), hill-climb over (m,m') on Hamming distance of the 256-bit digests, 3e8 evaluations per row, same seed per k):
   - 1 round: best distance 28 bits (clear local structure, as the model says).
   - 2 rounds: best 83 (k=1) and 83 (k=2).
   - 3 rounds: best 79 (k=1) and 79 (k=2).
   Random baseline for the best of ~1e8 to 3e8 independent draws is about 80-82, so for 2 and 3 rounds the climb is at the random level: no locally reachable cancellation. This is a search-failure result (GUESS that nothing is hidden for a smarter search), not a proof of absence.

## (b) Cost against 2^125
- Near-collision (8-k words equal) by birthday: k=1: 2^(16*7)=2^112; k=2: 2^96 compressions (COMPUTED, standard formula; memory-less version costs the usual factor, ignored).
- Cancellation: allowed budget is < 2^125, i.e. at most 3 unsilenced digest words (96 bits) at k=1. Model minimum is 6 words = 2^192 (GUESS: 2^32 per active word; the model gives only the number of words, not the probability). Total k=1: 2^112 + 2^192 ~ 2^192; k=2: 2^96 + 2^192 ~ 2^192. Needing more near-collision pairs to retry does not help (pairs cost ~2^112 * sqrt(P)).
- Break-even requirement: <= 3 active digest words (k=1) or <= 3 (k=2, 2^125 - 2^96 slack still ~3 words). Best model value 6; hill-climb finds none.

## (c) Verdict
KILLED for any cost below 2^125 under our tools: the number that closes it is 6 active digest words (192 bit conditions, ~2^192) in the word-level model at 3 rounds for k=1,2, with the exact hill-climb at random level (79 vs ~80). LIMITS (say plainly): the model is a lower bound on activity not a proof; the 2^32-per-word price is a GUESS; the BUD=2, |D|=4 or 5 zero-check entries are unexplained by exact tests (the 0-check D={7,10,12,14} was not tried exactly here); no SAT/algebraic solve of 1024 free message bits was attempted. If anything is ever re-opened: exact test = take D={7,10,12,14} (0x5480) with CV word 3 and try to build the real 3-round trail by solving G half-steps (message modification), counting real surviving digest words.
