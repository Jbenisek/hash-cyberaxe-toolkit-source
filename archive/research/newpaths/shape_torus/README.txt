shape_torus - rings and the torus (research only; 2026-10-08)
Labels: COMPUTED = measured by a program here; DERIVED = follows by algebra/counting; GUESS = judgement.

FILES
  bitgd.py        bit-level guess-and-determine: each word is a ring Z/w of bits; rotations shift around it,
                  carries cut it at bit 0. Exact root enumerator roots() (2^s passes). Validated: valtest.py
  valtest.py      seeds vs brute force at w=16 (4 ring types: 0 mismatches) and w=32 reference roots
  ring_gd.py      GD orders with provenance; checks matched to cuts; Dulmage-Mendelsohn blocks per order
  dm.py           DM decomposition of the square system for an index set (the order-free ring structure)
  dm_*.txt        block-size profiles: fixed (msg / random / from GD orders), outhalf (msg / random)
  core_bits.py    bit-level seed minimisation of the core ring;  core_bits_fixed*.txt / .log
  ring_list.py    catalogue of the small rings (satellites) with bit seeds;  rings_fixed.txt, rings_outhalf.txt
  torus.c         toy 2-round BLAKE3 (w=8,12,16; rot floor(r*w/32); low w bits of IV), one-round inverse,
                  symmetric families (modes 0-4);  torus_fam_w8.txt, torus_fam8_w8/12/16.txt, torus_symiv_*.txt
  torus_gd.py     word-level solving orders of the torus families;  torus_gd_*.txt
  orbits.py       all row-preserving torus maps and the message orbits they force;  orbits.txt

=== PART 1. RINGS ===

1a. Product -> sum (DERIVED). In a guess-and-determine order the naive cost per member is 2^(32*checks). If the
    checks close rings one at a time (block-triangular order), early abort makes it SUM_b 2^(32 t_b), t_b = cuts
    of block b. The right object is the Dulmage-Mendelsohn (DM) decomposition of the square system left after
    fixing the F index words: its irreducible blocks are exactly the rings that must be solved together. It does
    not depend on the order chosen.

1b. Fixed variant (F = 4) (COMPUTED, dm_fixed_*.txt):
    - 495 message index sets, 30000 random index sets, 136231 index sets from GD orders: EVERY regular choice has
      ONE irreducible core block of 68..94 words (smallest 68, e.g. index m0,m4,m6,m7), plus 0-2 satellites.
    - Core tearing (word cuts) best found: 4 (3 not found by greedy tearing, not excluded - same open question as
      gd_sat's "2-3 undecided"). So the cut-and-run-around cost per member is 2^128, the same as the 4 checks of
      gd_order: the 4 checks form ONE 4-cut ring. No sampled index set splits them.
    - Core of index m0,m4,m6,m7 touches K1 (8 words), K2 (3), D0..D3 (31), C0..C3 (22), m2,m3,m10,m13.
1c. Outhalf variant (F = 12) (COMPUTED, dm_outhalf_*.txt): 1820 message index sets and 20000 random: one core of
    63..114 words, tearing 4 (best). Same 2^128 per member.
1d. Satellite rings (COMPUTED, rings_*.txt): fixed 38 distinct, outhalf 61 distinct, all 1-cut.
    - fixed: every satellite lies inside ONE G call (Sol's local pivots and longer ones). Bit seeds s:
      a,c pinned (q + ROR8(q^A) = T): 8;  b,d pinned: 9 (Sol bound 12);  a2 = a1 + ROR12(b^(c+ROR16(d^a1))) + y:
      5 (validated w=16: 3 seeds, 0 mismatches vs brute force);  up to 24-32 for 6-7 word rings.
    - outhalf adds TORUS rings through E0 and E2 joined by the output pairs (the shift-2 partners):
      e.g. {E0:b2, E2:d2, out2, out5}: ROR7(E0.b1 ^ T2 ^ a) ^ ROR8(E2.d1 ^ a) = T5 in a = E2.a2. This is
      GF(2)-linear with rotation difference 1, so it is literally "cut ONE bit and run around the 32-bit ring":
      s = 1 (COMPUTED w=16 and 32), 0 or 2 roots. Other E0/E2 rings: s = 7..20.
    - Satellites cost <= 2^32 bit passes once per member or are tabled (side words constants) - they never touch
      the core. They are useful tools, not a route.
1e. Bit-level cut-and-run-around of the core (COMPUTED, core_bits_fixed*.txt): starting from 6 tearing sets
    (4 and 5 words, 128/160 bits), greedy seed removal ends at 128 bits every time; no single bit of a 4-word cut
    can be dropped. The single-call rings show why bits help there (one or two rotations on the loop: s = r);
    the core loops pass many G calls and rotations (16,12,8,7 per half call), so s saturates at 32 per cut
    (DERIVED heuristic: a low bit window loses r bits at each ROR r). Lower bound on the core seeds: not proved.
1f. Cheapest procedure for a family (DERIVED from 1b-1e): guess 4 cut words of the core (2^128 per member),
    satellites by table/bit seeds; members needed 2^64 -> about 2^192 total. Generic is 2^128. DEAD.
    What would revive it: a core that splits into 1-cut rings (cost 2^32 per member -> ~2^96 total, and bit
    seeds could lower it). Not seen in ~170000 index sets (COMPUTED); GUESS that no index set splits it.
1g. The round-0 inverse "8-ring" K0-D2-K3-D1-K2-D0-K1-D3 is not a constraint ring: Sol's inverse is triangular
    (each diagonal gives its old b,c without messages). COMPUTED: torus mode 0, 2^16 random X at w=8,12,16, 0
    mismatches. The message permutation's two 8-cycles only link round-0 calls to round-1 calls; in the idea-1
    system they end up inside the core (m2,m3,m10,m13 for index m0,m4,m6,m7).

=== PART 2. TORUS SYMMETRY ===

2a. Which torus maps exist (COMPUTED, orbits.txt): among all 24^4 row-preserving position maps, exactly 4 keep
    columns->columns and diagonals->diagonals: the column shifts by 0,1,2,3. Exactly 4 swap columns<->diagonals
    (the "transposes" (r,c)->(r, k+r-c)); none of these keeps the feed-forward pairs (i, i+8), and they turn
    "columns then diagonals" into "diagonals then columns" (DERIVED), so they give no symmetric digest. DEAD.
2b. Message orbits for a symmetric 2-round trajectory (COMPUTED): shift 2 -> orbits {0,2,3,4,6,7},
    {1,5,8,...,15}: 2 free message words. Shift 1 or 3 -> one orbit: 1 free word. Symmetric state: 8 words
    (shift 2), 4 words (shift 1).
2c. What the IV breaks (DERIVED): v8..v11 = IV0..IV3 in EVERY block (also later blocks of a chain), and
    IV0 != IV2, IV1 != IV3, v12..v15 = (0,0,64,11): no block can start shift-symmetric.
    With a hypothetical symmetric IV (COMPUTED torus mode 3, w=8: 2^16, w=12: 2^24 two-orbit messages, every
    output symmetric; 2 full collisions found at w=12) the shift-2 family would give a 2^64 birthday on 128
    bits (~39% success with 2^64 members) and shift 1 a 2^32 one. The real IV is exactly what blocks this.
2d. Symmetric state after round 0 (X = sigma X), reached through Sol's one-round inverse (COMPUTED, torus mode 1,
    2^22 samples at w=8,12,16): U4=U6, U5=U7, U8=U10, U9=U11 hold always (diagonal pairs share outputs, so
    they share old b,c); each of the 8 round-1 message conditions holds at rate 2^-w (no hidden correlation).
    New structure found (DERIVED, COMPUTED): columns K0,K2 then share their final (b,c) and so their b1 = s;
    m0 and m4 depend on s only, so (m0,m4) lies on a curve; family sizes come in lumps of 2^w (Poisson count of
    curve hits, mean 1).
2e. THEOREM (DERIVED, exact; COMPUTED at w=8): any G call satisfies x + y = A_out - a_in - b_in - b1. Paired
    calls with equal (b,c) or equal outputs share b1, which gives linear relations; with all 8 round-1
    conditions they force   2*m13 = m1 + m5 + A0 - A2 + A3 - A1  (mod 2^w)   (Ai = a-output of Ki), so
    m1+m5+A0+A1+A2+A3 must be even; the column relations of K0/K2 and K1/K3 plus m2=m7, m6=m0, m3=m4 turn that
    sum mod 2 into   bit0(IV0 + IV1 + ... + IV7) = 0.
    For BLAKE3 the IV low bits sum to 5 (odd): the fully shift-2-symmetric 2-round family is EMPTY.
    COMPUTED (torus mode 4, w=8): 28 odd-parity toy IVs: 34 curve hits, 8704 stage-1 solutions, 0 members;
    37 even-parity IVs: 89 members (on 2 of 22 curve hits), all verified by the forward function.
    COMPUTED (w=12, torus_fam8_w12.txt): 18 odd-parity IVs: 26 curve hits, 106496 stage-1 solutions, 0 members;
    22 even-parity IVs: 118784 stage-1 solutions, 2 members (both on one curve hit), 0 forward failures.
    Even parity is necessary, not sufficient: members are far rarer and clumpier than 2^-(w-1) per stage-1
    solution (w=12: 2 seen vs 58 for a uniform guess) - more hidden structure; not pursued (family is dead anyway).
    COMPUTED (w=16, real IV low 16 bits, odd parity): 1 curve hit, 65536 stage-1 solutions, 0 members, 0 failures.
    (Offset-2 IV, even parity: 0 curve hits, so nothing to test.)
2f. Half-symmetric family fam6 (X symmetric + 6 conditions -> out0=out2, out5=out7) (COMPUTED w=8, 18 IV
    offsets): exists in lumps of 2^(2w) (2^16 per curve hit at w=8), every member verified (out0=out2,
    out5=out7, 0 failures); c7 and c8 each hold on exactly 1/2^w of members, never together. 2 free words,
    digest 64+128 = 192 bits -> needs 2^96 members > 2^64. DEAD.
2g. Y symmetric (after the round-1 columns) instead of X: Ysym (Y sym + 4 E-message pairs) has 4 free words and
    a 128-bit digest (DERIVED). Word GD (COMPUTED, 9000 runs): best 11 guesses = 7 checks -> 2^224 per member.
    DERIVED: Y symmetric forces the b,c rows of X symmetric (C0/C2 outputs equal -> old b,c equal).
    YsymA (E0/E2 half only, out0=out2, out5=out7): 10 free words, 3 checks, digest 192 bits -> 2^96 x 2^96.
    YsymA + idea 1 on half B: freedom -2 (empty generically).  Xsym: 0 free words, 5 checks.  All DEAD.
2h. Anti-symmetric (X[sigma i] = X[i] ^ delta): same counting as 2d-2g because X -> m is a bijection
    (DERIVED); it also loses the U-symmetry of 2d (the old-b,c formula is not linear). DEAD.

=== BOTTOM LINE ===
Rings: the idea-1 system (both variants) is one irreducible 4-cut ring (core 63-68+ words) plus small 1-cut
satellites; early abort gives nothing; bit-level cutting gives nothing on the core (heuristic); 2^192. DEAD.
Torus: the shift-2 symmetry is real and would give 2^64 with a symmetric IV, but BLAKE3's c-row IV and the
parity theorem kill the full family; every partial family is too small or too costly. DEAD.
Side products worth keeping: bitgd.py (exact bit-level ring solver, s = 1..24 for local rings, e.g. the
E0/E2 output ring with s = 1); the x + y = A - a - b - b1 identity (linear relations between paired G calls).
