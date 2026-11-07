# The chunk-counter method: a mode parameter used as a solving variable

Folder: research\newpaths\counter_method. Written 2026-10-08. This is research only: no yukon, nothing filed, posted or
cancelled, trace untouched, pkg11 untouched. Nothing was written outside this folder. The organizer verifier was
imported read-only, with bytecode writing off.

Tags: COMPUTED means run here (method_check.py, output in method_check.txt) or in a named folder. DERIVED means it
follows from a cited source or from an argument given here. GUESS means judgement that has not been checked.

Sources:
- our own work: counter\adjudicate\VERDICT.md, counter\structure\STRUCTURE.md, counter\value\VALUE.md,
  counter\toy\TOY_RESULT.txt, scout_recent\SCOUT_RECENT.md, research\sol_lemmas_Z3.md, and
  catalogue\CONCERNS_FOR_ORGANIZERS_from_Jbenisek_100826.md (the file named CONCERNS_FOR_ORGANIZERS.md does not exist);
- the target profile blake3-r2-prefix-v1.json;
- the specifications listed in section 7, with local text copies in refs\.

counter_next\ contained only knobs\model.py, and stack\ was empty. This note does not map knobs or stack refinements.

## 0. Summary

1. **The method.** Some hash modes place a per-position parameter (a counter, offset or tweak) into the compression
   state. In a tree mode, a leaf's first compression starts from a constant chaining value. There, the parameter can
   be left unknown and solved inside each trial, at no cost. It is one extra word in the solving system, and both
   messages share it. It gains something only when it lets a solving basis prescribe one more internal word, which
   turns a probability-q condition into a certainty. As a constant it gains nothing. (DERIVED; toy control COMPUTED)
2. **Exactness.** The full-hash collision follows from a short tree lemma (section 1.1). Organizer code confirms
   it: our earlier folders, plus part E here, which plants a collision in the first block of any chunk (40/40). The
   per-trial gain is an exact conditional probability, P(E | success)/q, by Sol's rejection-equivalence lemma.
   For 2-round BLAKE3 that is 2^11 x 0.365 = 2^9.55. Counted with the cost change and minus the clusters it gives
   up, the net is +7.6 bits (92.53 -> 84.96). (DERIVED / COMPUTED in counter\value)
3. **BLAKE3 is the clean case.** Every chunk starts from the key words, and its counter sits in v12. So the counter
   gives a neutral direction of round 0: (w0 + d, w1 - d, t XOR a1 XOR (a1 + d)) leaves the whole round-0 state
   unchanged. This held in 3000/3000 trials, and in 0/3000 when t is held fixed. (COMPUTED, part A)
   - BLAKE2 tree mode has the same freedom through its node offset (COMPUTED for BLAKE2s, part D).
   - Skein tree mode and MD6 have it too (DERIVED).
   - Sequential BLAKE/BLAKE2/Skein do not: there a new counter value means a new prefix and a new chaining value.
   - ParallelHash and KangarooTwelve have no per-leaf parameter at all.
4. **Costs.**
   - t is an output of the solve, close to uniform below 2^32. A typical pair is 2 TiB and the largest 4 TiB.
   - The shortest pair (1079/1087 bytes) costs 2^32 times more trials.
   - Hashing a typical pair costs 2^36 compressions. That is negligible in the cost model, but it takes about 16
     days in the organizer's Python verifier.
   - The harness can see neither the construction's exact half-collision nor a found pair. (COMPUTED / DERIVED)
5. **Novelty.**
   - A chosen counter, salt or tweak is standard freedom in free-start and compression-function attacks.
   - A counter has also been exploited at the mode level, as in Streebog and dithered MD.
   - We found no prior use of a tree mode's leaf position as cost-free, fixed-IV freedom, used per trial as a solving
     variable. Search coverage is limited. (DERIVED from section 5's sources; novelty is a GUESS)

## 1. The technique, stated generally

### 1.1 When a node collision is a full-hash collision (tree lemma)

**Lemma T (BLAKE3; DERIVED, checked on organizer code).**
- Setting: t >= 1. P is any string of 1024t bytes. X and X' are distinct, each of 1 to 1024 bytes. CV_t(X) is the
  chaining value of X compressed as chunk number t: its blocks chained from the IV/key with counter t,
  CHUNK_START on the first block, CHUNK_END on the last, and no ROOT.
- Statement: if CV_t(X) = CV_t(X'), then BLAKE3(P||X) = BLAKE3(P||X').

Proof.
- Both messages have t + 1 chunks, and the tree shape depends only on the chunk count.
- Chunks 0..t-1 are the same bytes with the same counters, so they have the same CVs.
- Chunk t has equal CVs by hypothesis.
- Every parent is a function of its two child CVs alone (IV, counter 0, length 64, flags PARENT).
- Since t + 1 >= 2, ROOT is applied to a parent and never to chunk t. So every parent input agrees, including the
  root's.

The converse fails only if some parent collides on its own.

Checks:
- counter\structure: t = 1..1025 and t = 2^32 + 5, with 150/150 messages and 75/75 planted pairs.
- part E here: a planted collision of the FIRST block of chunk i (counter i, flags CHUNK_START, 64 bytes), with
  more chunks after it, gives equal digests 40/40. Unpatched, the digests differ 40/40.

So the colliding compression can be the single-block last chunk (the 55/63 case, flags 3) or the first block of
any chunk.

What it does NOT give:
- Near or partial collisions do not lift. The parent scrambles them: the two real t = 1 pairs agree on 0 of the 4
  half-mask digest words (COMPUTED, counter\adjudicate).
- t = 0 is a different function: the chunk is then the root, with flags 11 and counter 0.

**General form (DERIVED).** Take a tree mode in which:
- nodes pass only their output upward,
- the tree shape depends only on the length, and
- one node's output collides at a fixed position while all other node inputs are equal.

Then the hash collides. Tree-soundness theory gives the converse: a sound mode turns any outer collision into an inner
one [BDPV14].

### 1.2 Conditions for a free per-trial parameter

Let tau be the mode parameter at the colliding node. The method needs all four of these:

- **(M1) Fresh start.** The colliding compression is the first compression of its node. Its chaining input is a
  constant, or depends only on tau in a known way. If earlier compressions of the same node also carry tau, changing
  tau changes the chaining input, and the trial is a new instance rather than a solve. In BLAKE3 every block of
  chunk t carries t, so only a first block qualifies.
- **(M2) Lifting.** Lemma T, or its analogue for the mode.
- **(M3) Legality.** Every value the solve can output must be realisable in the message domain.
  - BLAKE3: t != 0, and t < 2^51 under the 2^64-bit bound, so v13 < 2^19.
  - Skein: Position = len mod N_l (section 2).
  - Any value outside the realisable range acts as a filter on trials.
- **(M4) Shared, never a difference.** Both messages sit at the same position, so tau is one common unknown. A
  difference in tau would need two different tree positions, for example a parent against a chunk, which is a
  separate 2^128 problem (DERIVED, scout_recent).

### 1.3 When it helps (and why a constant does nothing)

**Setup.** The attack solves a system S over the colliding compression's internal words. Each trial fixes a basis
B, a set of free words that determines the rest triangularly. Making tau an unknown adds one variable and one
equation's worth of slack, so the basis grows by one word.

**Proposition H (DERIVED, within a basis-solving attack).** The parameter helps if and only if there is an internal
word W that meets two requirements:
- W carries a condition E, of probability q, that success needs, or that holds a large share of the success mass;
- (prescribed set) + W extends to a basis with tau unknown, but not with tau constant.

Then W is enumerated over E's solutions, and tau is computed last.

**Gain.** Suppose that, for fixed outer words, the map W <-> tau is a bijection. Then the prescribed sampler is exactly
the baseline (tau uniform) conditioned on E: P_prescribed(F) = P_base(F and E)/q for every trace event F. This is
Sol Z3, lemma 2C, proved for the real BLAKE3 sampler (COMPUTED/PROVED, research\sol_lemmas_Z3.md). The per-trial
factor is therefore P(E | success)/q, with no new independence premise. The cost factor per trial must then be
counted separately.

For 2-round BLAKE3:
- E is "c1 in the beta* cube", with q = 2^-11.
- P(E | success) = 67,698,688/185,377,197.55 = 0.365.
- The factor is 747.9 = 2^9.547.
- Our machine charges 6.5 ops per trial against 7.7 (+0.244 bit).
- Without clusters: -2.222 bits.
- Net +7.57: 92.53 -> 84.96, or 84.45 at the board's margin (COMPUTED in counter\value, rechecked in
  counter\adjudicate).

The one OPEN piece: the success mass removed by excluding t = 0 is not priced (Sol Z3, section 3). It affects at most
one cube member per outer step.

**Control N: a constant parameter does nothing (COMPUTED and DERIVED).** A constant tau re-instances the same system:
for each constant, round 0 is a bijection. The trial family is only relabelled.
- Toy W = 8: counter arrangement with E1.d1 not forced, 54 found against 47.8 predicted at the filed rate
  (1.13 +- 0.15). Forced, 251 against 255.0, with 10.9 times fewer trials per collision than the filed arrangement (counter\toy).
- scout_cross measured constant counters only, and found no gain. Both scouts were right.

**Mechanism as a neutral direction (COMPUTED, part A).**
- In BLAKE3's first G call: a1 = IV0 + IV4 + w0, and d1 = ROR16(t XOR a1).
- Holding d1 fixed and moving (w0, w1, t) to (w0 + d, w1 - d, t XOR a1 XOR (a1 + d)) keeps all 16 round-0 output
  words: 3000/3000. With t held fixed: 0/3000.
- Along this direction w0 + w1 = K0.a2 - K0.b1 - IV0 - IV4 is constant.

So round 0, a bijection between message and state for any fixed counter [AGKMM10], becomes 2^32-to-1 once the counter
is free. The free word first acts at round 1, as the y word of column 2 (w0) and the x word of diagonal 0 (w1).

## 2. Why BLAKE3, and the other modes

| Mode | Where the position parameter enters | Free per trial? Cost | Verdict |
|---|---|---|---|
| BLAKE3 [B3, sections 2.4 and 7.5] | Chunk index t in v12 (low 32 bits) and v13, in every block of chunk t. Each chunk's first block starts from the key words. | Yes, at zero cost: 32 bits in v12. v13 < 2^19, so as a solved word it is only a 2^-13 filter. | Applies. COMPUTED (part A, part E, counter\structure). The spec calls the chunk counter "not strictly necessary for security" (section 7.5). |
| BLAKE2 sequential [RFC 7693, section 3.2; B2, sections 2.3-2.4], and BLAKE [AHMP08] | Byte counter in v12 and v13, XOR IV4 and IV5. It counts all bytes so far. | No. A new counter value means a different prefix length, hence a different chaining value h. Every trial is a new instance, costing at least 1 compression, not a solve. The only local choice is the final block's own length (at most 64 or 128 values, which also moves the padding): a source of a difference, like BLAKE3's v14, not a word. | Does not apply. DERIVED |
| BLAKE2 tree [B2, sections 2.8 and 2.10] | Node offset in parameter bytes 8..13, XORed into the IV: h2 plus 16 bits of h3 for BLAKE2s; h1 (64-bit) for BLAKE2b, read from the reference parameter layout and not run. Each leaf is a fresh instance. | Yes, at zero cost, for the last leaf of a tree with unlimited or large fanout. The offset must equal the number of preceding leaves, so the message size is offset x leaf length. Node depth is fixed by the tree level. | Applies. COMPUTED for BLAKE2s: the layout matches hashlib 200/200, and the offset absorbs m4 (a1 = v2 + v6 + m4) with the round-0 state unchanged, 2000/2000 (control 0/2000). The offset also enters the feed-forward, which cancels between the two messages. BLAKE2sp/bp (fanout 8/4, interleaved blocks) give only 3 or 2 bits, set by the length: not a word. |
| Skein tree [SK13, sections 3.5.6 and 3.3.2] | Leaf i = UBI(G, M_0,i, i·N_l + 2^112 + T_msg·2^120). The Position field starts at i·N_l, and G is shared. Tweak words t0, t1 and t2 = t0 XOR t1 are added into subkey words Nw-3 and Nw-2 at every injection, every 4 rounds. | Yes, at zero cost. The low log2(N_l) >= 6 bits of Position are fixed by the block length. Solved whole, Position is a 2^-log2(N_l) filter, so only the high bits are free. It re-enters at every subkey injection, so it is neutral only up to the next injection. | Applies in principle. DERIVED; usefulness is a GUESS. Sequential Skein behaves like BLAKE2. |
| MD6 tree [MD6, compression input] | U = level and a 7-byte node index: one of the 89 input words. Leaves are independent. | Yes, at zero cost: a 56-bit index. | Applies in principle. DERIVED; usefulness is a GUESS (one word out of 89). Sequential MD6 (L = 0) chains. |
| ParallelHash [SP 800-185, section 6.3] | Leaves are cSHAKE(X_i, 256, "", ""), with no index. n and B appear only in the final call. | Nothing to solve for. | Does not apply. A leaf collision is position-independent. DERIVED |
| KangarooTwelve [RFC 9861, section 3] | Leaves are TurboSHAKE128(S_i, 0x0B, 32), with no index. S_0 and n-1 appear only in the final node. | Nothing to solve for. | Does not apply. DERIVED |
| MD strengthening (SHA-2) | The length sits in the final block's message words and must match the prefix. | No: it is sequential. | Does not apply. DERIVED |

The common thread (DERIVED): the method needs a mode that both (i) restarts the chaining value per node and (ii) puts
the node's position into that node's own compression input. BLAKE3, BLAKE2-tree, Skein-tree and MD6 do both.
Sakura-style modes (ParallelHash, K12) do (i) but not (ii). Sequential HAIFA modes do (ii) but not (i).

## 3. Where else it could apply

- **BLAKE3 at 3 or more rounds.**
  - DERIVED: the neutral direction is a round-0 property, so it exists at every round count. It enters round 1 at
    col2.y and diag0.x (COMPUTED, part B).
  - DERIVED: after the round-1 diagonal step it touches all 16 state words, because column 2's outputs feed every
    diagonal. So it is one extra free word for message modification in rounds 0-1, and nothing later.
  - GUESS: it helps only an attack whose solving phase over rounds 0-1 is short of exactly one prescribed word, as
    ours was at 2 rounds (8 free words after the pins; 9 with t). The specific T1 lever has no known 3-round analogue,
    because the 55/63 free half reaches only 2 rounds (CONCERNS item 3). At 4 or more rounds, the probabilistic rounds
    dominate, and one word of outer freedom is negligible.
- **Near-collisions and partial targets.** These do not lift through the tree (section 1.1). The method is for full
  collisions only. DERIVED; the t = 1 check is COMPUTED.
- **Preimage.** The digest is a root parent with counter 0, so it gives no freedom. A target for the last chunk's CV
  has to come from the prefix stack, and the prefix stack depends on t. Choosing t changes the target, which breaks
  M1. DERIVED.
- **Second preimage of a long message.** Each chunk i is a target with its own counter i. A solved t lands on one
  target per trial, so the many targets give no speedup. This is the protection HAIFA intended [BD07]. DERIVED.
- **Multicollisions.**
  - A k-collision of the last chunk at one t lifts to a k-multicollision.
  - Collisions of first blocks at distinct chunk indices compose (part E), giving 2^k messages from k collisions. But
    the 55/63 construction needs a final block, so it can be used once per message. DERIVED.
- **Other members of the free-half family.**
  - Other length pairs with a cancellable v14 difference: the counter is independent of the pair, so the same
    freedom applies. DERIVED.
  - Keyed and derive_key modes (CV = key words) are the same, but outside the profile. DERIVED.
  - Any root-colliding 2-round construction can be moved to a non-root last chunk. Its pins must be re-solved for
    flags 3 instead of 11; structure did this for H8 (K3.a1 = ROL(K3.d1, 16) XOR 3). DERIVED / COMPUTED there.
- **Other ARX tree modes.** BLAKE2-tree's offset is absorbed exactly like BLAKE3's counter (COMPUTED, part D). For
  Skein-tree the effect is neutral only up to the next subkey injection (DERIVED). Whether either buys a prescribed
  word depends on an attack that does not exist yet (GUESS).

## 4. Cost accounting, counted as written

- **Message size.** COMPUTED in counter\structure; DERIVED here.
  - t is an output of the solve, not a choice. Over outer steps it is roughly uniform below 2^32 (mean log2 30.5).
    Within one outer step it is not uniform.
  - A typical pair has 2^31 chunks: 2^41 bytes, or 2 TiB, per message. The largest is 4 TiB.
  - Forcing t <= T costs a factor 2^32/T in trials:
    - t = 1 (1079/1087 bytes): 2^32;
    - t <= 3 (fits the harness default of 4096 bytes): 2^30.4;
    - t <= 63 (fits its maximum of 65,536 bytes): 2^26.0;
    - t <= 2^20 (1 GiB): 2^12.
  - The prefix content is free (all-zero chunks will do). Only its length is forced.
- **Verifying a found pair.**
  - About 2 x 17 x 2^31 = 2^36.1 compressions, including parents. In the contest's units that is 2^-49 of the
    attack.
  - Wall clock:
    - our C tree hash (4 threads x 8 lanes) ran 2^36 chunk compressions in 85 s (counter\structure);
    - the organizer's Python blake3 at 2 rounds takes 0.33 ms per chunk, so a typical pair takes about 16.5 days on
      one core and the largest about 33 days (COMPUTED, part C).
  - Each message also has to be stored and moved (2-4 TiB), unless it is described as (t, chunk pattern, X, X') and
    expanded as a stream.
- **Contest cost model.** DERIVED from the profile.
  - Time is counted in compression equivalents, memory is free, and output size is not scored.
  - The pair is two distinct complete messages below 2^64 bits, under the standard mode and IV. The out-of-scope list
    (free-start, compression-only, mode changes) does not cover it.
  - Counted literally, the score is 84.96 at our conventions and 84.45 at the board's margin.
  - Disclose four things: the non-root colliding compression with Lemma T, the typical size, the verification
    cost, and the unpriced t = 0 exclusion.
- **What an evaluation harness can and cannot see.** DERIVED from hash-smash docs and runner.py, via counter\adjudicate.
  - Cannot see:
    - The exact half-collision of the last chunk's CV, because the root parent scrambles it. Even at t = 1 the two
      digests agree on no half-mask word.
    - The full collision, at 2^-91 per trial.
    - A found pair, which is over the message cap.
    - Pair verification in practice, which takes about 16 days in the reference verifier.
  - Can see:
    - the tree lemma, but only through the verifier's internal functions;
    - a reduced-width end-to-end run: the W = 8 toy produced 305 real full-hash collisions of complete messages
      (counter\toy);
    - premise proxies on real 32-bit trials, if internal events are allowed.
  - So the method is LESS evaluable than the root version on its exact part, though it needs fewer premises (no
    H4-H6).
  - Concrete harness fixes:
    - an internal-event check on _chunk_output / _compress;
    - support for toy widths;
    - a compact-pair verifier with a native hasher.
  - Restricting t to the cap (2^26 or more extra trials) is not a fix.

## 5. What is new against the literature

- **Known: parameter freedom in free-start and compression-function settings.** The counter, salt or tweak is
  attacker freedom in the free-start and compression-function settings.
  - [GKNWW14] defines BLAKE2's compression-function framework as attacker control of the CV and of v12 and v13.
  - The BLAKE3 specification separates the hash setting from the compression-function setting in its trail table [B3].
  - SHAvite-3 has chosen-counter, chosen-salt pseudo-collisions and preimages [Pey09; GLMNPRS10]. Its hash-setting
    attacks work "for a given salt and counter value" [BDLF10].
  - Skein has near-collisions with chosen tweaks [YCJW11].
- **Known: counters as a lever in generic mode attacks.**
  - Streebog's poor use of the HAIFA counter enables a second-preimage attack [GJLPW14].
  - Dither sequences have been exploited [ABFHKSZ08].
  - HAIFA's counter is the defence [BD07].
- **Known: tree soundness.** Inner and outer collisions correspond, with the counter inside the inner function's
  input [BDPV14]. In the ideal model, therefore, the counter buys nothing. This method needs a structured, reduced
  compression.
- **Not found: the method itself.** We found no prior work that does the following:
  1. points out that a tree mode's leaf position supplies, inside the fixed-IV hash setting and at zero cost per
     trial, an input that otherwise only the semi-free-start setting grants, and that the lift to a full collision is
     exact;
  2. uses that input as a per-trial solved variable that buys exactly one prescribed internal word, with an exact
     rejection-equivalence factor P(E | success)/q;
  3. observes, with a measured control, that the same input as a constant buys nothing.

  Earlier searches agree: LITERATURE.md, SCOUT_RECENT.md, and today's searches for BLAKE3, BLAKE2 node offset, tree
  leaf index and Skein tree. Novelty is a GUESS: eprint returned 403s, Springer needs a login, and 2025-2026 coverage
  is thin.
- **A remark for designers.** BLAKE3 added the chunk counter to defeat non-constant-time shortcuts, and calls it not
  strictly necessary for security [B3, section 7.5]. At reduced rounds it is attacker freedom. K12 and ParallelHash
  avoid it by keeping position out of the leaves. GUESS: at 7 rounds it does not matter.

## 6. Open items

- The t = 0 exclusion is unpriced (Sol Z3, section 3).
- Whether the physical sampler realises the joint law at 2^-91 is OPEN. It shares premise H1' with the filed path.
- The independent 32-bit recheck (Grok job 32) had not reported as of VERDICT.md.
- Skein-tree and MD6 are DERIVED from their specifications only, with no toy run.
- No 3-round use of the neutral direction has been tried.

## 7. Files and references

Files in this folder:
- METHOD_NOTE.md: this note.
- method_check.py and method_check.txt: parts A-E, 0.7 s; run as `python -B method_check.py > method_check.txt`.
- refs\: text copies of Skein 1.3, BLAKE2, SP 800-185, RFC 9861, RFC 7693 and [BDLF10].

References:
- [B3] O'Connor, Aumasson, Neves, Wilcox-O'Hearn, BLAKE3 specification, sections 2.4-2.6 and 7.5, https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/blake3.pdf
- [B2] Aumasson, Neves, Wilcox-O'Hearn, Winnerlein, BLAKE2 specification, sections 2.3, 2.4, 2.8 and 2.10, https://www.blake2.net/blake2.pdf
- [RFC 7693] BLAKE2, https://www.rfc-editor.org/rfc/rfc7693
- [SK13] Ferguson et al., The Skein Hash Function Family v1.3, sections 3.3.2 and 3.5.6, https://www.schneier.com/wp-content/uploads/2015/01/skein.pdf
- [MD6] Rivest et al., The MD6 hash function (2008), https://people.csail.mit.edu/rivest/pubs/RABCx08.pdf
- [SP 800-185] NIST, cSHAKE, KMAC, TupleHash and ParallelHash, section 6, https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-185.pdf
- [RFC 9861] KangarooTwelve and TurboSHAKE, section 3, https://www.rfc-editor.org/rfc/rfc9861
- [BDPV14] Bertoni, Daemen, Peeters, Van Assche, Sufficient conditions for sound tree and sequential hashing modes, https://keccak.team/files/TreeHashing.pdf
- [BD07] Biham, Dunkelman, A framework for iterative hash functions: HAIFA, ePrint 2007/278, https://eprint.iacr.org/2007/278
- [GJLPW14] Guo, Jean, Leurent, Peyrin, Wang, The usage of counter revisited: second-preimage attack on new Russian standardized hash function, SAC 2014, https://eprint.iacr.org/2014/675
- [ABFHKSZ08] Andreeva et al., Second preimage attacks on dithered hash functions, EUROCRYPT 2008, https://www.di.ens.fr/~fouque/pub/euro08b.pdf
- [GKNWW14] Guo, Karpman, Nikolic, Wang, Wu, Analysis of BLAKE2, CT-RSA 2014, section 2, https://eprint.iacr.org/2013/467
- [BDLF10] Bouillaguet, Dunkelman, Leurent, Fouque, Attacks on hash functions based on generalized Feistel (SHAvite-3-512), SAC 2010, https://www.di.ens.fr/~fouque/pub/sac10b.pdf
- [GLMNPRS10] Gauravaram et al., Cryptanalysis of the 10-round hash and full compression function of SHAvite-3-512, https://orbit.dtu.dk/en/publications/cryptanalysis-of-the-10-round-hash-and-full-compression-function-/
- [Pey09] Peyrin, Chosen-salt, chosen-counter, pseudo-collision on SHAvite-3 compression function (2009), cited in [BDLF10]
- [YCJW11] Yu, Chen, Jia, Wang, Near-collision attack on the step-reduced compression function of Skein-256, https://eprint.iacr.org/2011/148
- [AGKMM10] Aumasson et al., Differential and invertibility properties of BLAKE, FSE 2010, https://eprint.iacr.org/2010/043
- [AHMP08] Aumasson, Henzen, Meier, Phan, SHA-3 proposal BLAKE (HAIFA counter in v12-v15). This is a GUESS citation; it was not fetched here.
