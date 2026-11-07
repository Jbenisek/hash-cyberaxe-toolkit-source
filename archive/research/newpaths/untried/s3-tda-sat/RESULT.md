# s3-tda-sat: SHA3-256 r6, cells msg x tda and msg x sat (scout, 2026-10-10)

Our own team's research. Nothing filed or submitted. No yukon commands, no network.
Labels: COMPUTED (ran it here), DERIVED (arithmetic on computed or cited numbers), GUESS. CITED = taken from
`research\SHA3R6_MAP.md` (section given) and not recomputed here.
Model: standard Markov assumption (chi values independent across rounds), the same one every trail estimate uses.
Note: the relayed user request was "how close is the next blake3 submission". This scout does not answer that; it is the
SHA3 r6 grid task the workflow computed.

## Bottom line
- **msg x tda: dead.** The Dinur-Dunkelman-Shamir family (6-bit double-kernel trails, the trails the TDA was built for)
  was enumerated exactly and pushed through 6 rounds. Its best placement uses a 2-round connector with the double kernel at
  theta3/theta4. On the identity-transition trails, the digest-collision probability is 0 for 2 of the 8 classes, and
  the best class needs at least 2^140.6 pairs (rigorous). With every kernel-keeping middle choice summed, the floor is 2^134.6
  (GUESS-assisted). In contest units that is at least 127.6 even at the most generous per-pair price, so it misses
  124.04565 by at least 3.5 bits and our 123.1-123.5 by at least 4.1 bits (DERIVED).
- **msg x sat: open (weeks-scale), negative prior.** A trail route with 2^T pair trials costs about
  2^(T - 1.02 - k) units, where k = 3.1 to 6 (GUESS) is the bit-sliced, early-abort per-pair discount. So the bar is
  **T <= 128.2-131.1** to beat 124.04565 and **T <= 127.2-130.5** to beat 123.1-123.5 (DERIVED). The best known tail
  floors near 2^132 (CITED section 3.3), which is 0.9-3.8 bits short of the board. The GLST trail with a 2-round connector
  needs 2^197-2^206 (CITED section 3.3), and the DDS family needs at least 2^134.6.
- **Obstruction (both cells):** at c = 512 the connector covers at most 2 rounds, so four chi layers are paid:
  chi3, chi4, chi5 and the digest chi6. A double kernel covers only two thetas, and no third one exists (COMPUTED). One
  theta spread therefore always lands before the digest round. After it, theta6 puts lone difference bits into
  plane-0 chi6 rows at x <= 3, and such a row can never collide. Only 9 of the 31 nonzero row differences are
  allowed, and every one of them contains x = 4 (COMPUTED). Every chi4 output of the lightest DDS classes leaves
  10-34 such forced rows (COMPUTED).

## 1. What a trail has to reach in the contest cost model (DERIVED, k is GUESS)
- Pairs needed for success 0.39: N = -ln(0.61)/p = 0.494 * 2^T, so log2 N = T - 1.017 (DERIVED).
- Cost per pair in units: 2^-k. Lower end k = 3.115: one message through 6 bit-sliced rounds = 187.57/1626 units
  (CITED section 1, DERIVED). Upper end k ~ 6 (GUESS): early abort after the chi3 conditions needs only the message M
  (the conditions are on M's values), rounds 1-2 plus a few chi3 bits, and Gray sharing of round 1.
- Bar: T < 125.063 + k gives 128.2..131.1 to beat 124.04565. T < 124.12 + k and T < 124.52 + k give
  127.2..130.1 and 127.6..130.5 to beat 123.1 and 123.5. The connector re-solve cost (~2^11 units per linear system,
  GUESS) is amortized only when the system leaves >= ~16 DF.
- So the trail route is closer than 124 vs 132 suggests. Cutting 1-4 bits from the best known tail would put it level
  with the board. Nobody has found such a tail.

## 2. Exact facts at rate 1088 / capacity 512 (facts.txt, conn.txt; COMPUTED unless marked)
- Message space: 1,080 free bits; 520 bits have zero difference (512 capacity + 8 pad). CP kernel inside it: dim 760.
- chi restriction weights: 2 (1 bit), 3 (2 bits), 3-4 (3 bits), 4 (4-5 bits).
- **Full linearization**: the largest affine subspace on which chi is affine has dim 2 (320 such cosets). So one row costs 3
  conditions, and all of chi1 costs **960 of 1,080 DF, leaving 120** (DERIVED). A one-block SHAKE128 has 1,336 free bits and
  would keep 376 (DERIVED). That 256-bit rate gap is why the GLS-style connector does not transfer.
- **TDA difference phase**: for every output difference b, the largest affine set of compatible input differences has
  dim 2. A generic target therefore needs >= 260 active chi1 rows to zero the 520 fixed bits linearly (DERIVED). Counting
  bound: sum_a DDT(a,b)/32 = 1 per row, so a generic target costs >= 520 chi1 value conditions, leaving <= 560 DF (DERIVED).
- **2-round connector fan-in**: one chi2 input bit = 11 chi1 output bits in 10 chi1 rows. Linearizing one isolated chi2
  condition bit therefore costs <= 10 conditions.
- **Digest round**: allowed nonzero plane-0 chi6 row differences (x0..x4) are 00001 (2 cond.), 00101, 10101, 00011,
  01011 (3), 00111, 10111, 01111, 11111 (4). A lone bit at x = 0..3 makes a collision impossible. Plane-0 chi6 inputs come
  from the theta6 output lanes (x,x), rho 0/44/43/21/14.

## 3. Idea 1: DDS target difference algorithm + 3/4-round trail (dds.py, dds2.py, dds4.py, dds5-8.py, conn.py)
- Family: 6-bit sets S with S and rho-pi(S) both in the CP kernel. COMPUTED: 0 four-bit sets; 8 classes up to
  z-translation; 120 patterns lie inside the 1,080 free bits (matches the map's 120). No compatible chi input of S has a
  kernel pre-image, so there is no backward third kernel round. No chi4 output of any kernel-keeping middle choice is in
  the kernel, so there is no forward third kernel round either. This is exact for the 342 middle choices with <= 12
  variables (min chi5 weight 105). For the other 170, the DP gives min|theta(b4)| >= 103 bits, which is more than any b4
  of <= 54 bits could have (COMPUTED).
- Placements on 6 rounds:
  - Kernel at theta1/theta2 (S is the message difference) or theta2/theta3: two or three spreads come before chi6. The first
    spread alone has a path weight of 105-129 (COMPUTED). After that the difference is dense, and the digest probability
    approaches the generic 2^-256 (GUESS).
  - Kernel at theta4/theta5 or theta5/theta6: the chi output just before the kernel has to be a dense exact value (no
    kernel pre-image exists, COMPUTED). For the identity choice that value has 209-320 active rows (conn.txt), so chi2 or
    chi3 carries >= 418-640 conditions (DERIVED: >= 2 per active row). That is more than a 2-round connector can absorb:
    960 for chi1 linearization plus >= 418 is more than 1,080.
  - **Middle (theta3/theta4) is the only placement with a single spread before the digest round:**
    - Path weight w(chi3)+w(chi4)+w(chi5) has an exact minimum of 128 (class 5: 12 + 11 + 105); per class 128-153
      (dds4.txt, COMPUTED).
    - The zero-or-x4 relaxation of the digest is inconsistent for every chi4 output in classes 4 and 5 (COMPUTED).
    - Clustered cost C = -log2 P(digest collision | chi5 input), taken over all chi5 outputs (dds8). On identity-transition
      trails it is 0 probability for classes 0 and 4 (rigorous). For the others the minimum C is 128.6 (class 6) to 154.6
      (rigorous lower bound from rows with independent forms, COMPUTED). The estimate over all touched rows is 234-253
      (GUESS-grade: it treats the rows as independent).
    - Trail total T >= 12 + C: **>= 140.6 pairs (class 6, rigorous)**. With the 63 heavier kernel-keeping mids assumed to
      contribute no more than the identity, the floor is 134.6 (GUESS-assisted).
    - Using a 1-round TDA instead pays chi2 as well: +11-12 (COMPUTED).
- Connector for the middle placement (conn.txt):
  - b1 = L^-1(a2) has 538-850 bits and covers 209-320 active chi1 rows. The chi1 value floor is 479-753 conditions
    (COMPUTED). That leaves <= 327-560 DF, then chi2 takes 12 plus <= 120 for linearization (DERIVED).
  - Class 6 (209 rows) has <= 418 linear difference dimensions, fewer than the 520 needed. DDS's linear TDA fails there and
    a non-linear difference phase is needed.
  - DF is tight but not what blocks this family; the digest round is.
- Contest units: 140.6 - 1.02 - 6 = 133.6, or 127.6 from the 134.6 floor (DERIVED). Both are above 124.05 by >= 3.5 bits
  and above 123.1-123.5 by >= 4.1 bits.

## 4. Idea 2: SAT search for a short tail after a 2-round connector
- Bounded estimate: cost >= 2^(T_min - 1.02 - k), where T_min is the lightest 4-layer tail (chi3, chi4, chi5, digest chi6)
  that a 2-round connector at c = 512 can reach.
  - Known T: best published 4-round trail, floor ~132 (CITED 3.3), gives 125.0-127.9 units, short by 0.9-3.8 bits
    (board) or 1.5-4.8 bits (ours). It is unknown whether a 2-round connector at c = 512 can reach that trail.
  - GLST trail: 197-206 (CITED 3.3), gives 190-202 units.
  - DDS family: >= 134.6-140.6 (section 3).
  - A 3-round connector would remove chi3 (the GLST SHAKE128 shape, 2^123.5), but it is >= 33 DF short at c = 512 and
    re-rolling costs >= 2^156 (CITED 3.3).
- Literature prior: GLST built exactly this SAT tool and published only quantum 6-round SHA3-256 attacks. No classical
  attack below 2^128 is published (CITED section 5).
- Real test (beyond this budget): a GLST-style SAT search over 4-round trail cores, counting the digest round with the
  clustered method of dds8.py. It needs T <= ~129-131 and a chi2 output whose 2-round connector keeps >= ~16 DF after chi1
  (chi1 costs >= 520). Weeks-scale (map section 4).
- Cheap first step: take the published 141-weight trail (its source is in shake.md / the literature, which I was not
  allowed to read here) and run dds8.py's digest bound and conn.py's ledger on it. That would show whether "floor ~132"
  survives an exact digest count and a connector at c = 512.

## 5. Limits and stopped runs
- Not bounded: the 63 heavier kernel-keeping middle choices per class (chi4 weight >= 14); trails that leave the kernel
  at chi3; and any non-DDS trail.
- k (per-pair price) is a GUESS; it moves the bar by about 3 bits.
- Stopped runs (my own processes; nothing was refused):
  - The first dds.py run passed the 10-minute run limit. I stopped it after its enumeration had printed (8 classes,
    120 legal patterns) and replaced the loop with dds2/dds4.
  - dds6.py (DFS feasibility search) passed the limit too; I stopped it and replaced it with dds7/dds8.
- Every run was single-process; the longest finished run took 245 s.

## Files
kk.py (Keccak bit helpers, self-tested against verifier/keccak.py incl. sha3_256 r6), facts.py/.txt, dds.py (stopped;
enumeration only), dds2.py (library + DP), dds4.py/.txt/_mids.txt/_best_class*.txt, dds5.py/dds5_c45.txt,
dds6.py (stopped), dds7.py/dds7_c45.txt, dds8.py/dds8_c*.txt, conn.py/conn.txt.
Commands: `python kk.py`, `python facts.py`, `python dds4.py 0 8 12`, `python dds5.py 4 6 13`, `python dds7.py 4 6 13`,
`python dds8.py 0 8 13` (run as 0-4, 4-6, 6-8), `python conn.py`.
