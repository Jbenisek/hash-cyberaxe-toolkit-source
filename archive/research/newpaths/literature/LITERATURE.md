# LITERATURE.md: what is published, and what it means for 2-round BLAKE3 collisions

Folder: research\newpaths\literature. Written 2026-10-08. Research only; nothing was submitted or run on Yukon.

Tags. DERIVED = read from the source text (local copy in papers\ unless marked "abstract only")
or worked out from it. COMPUTED = arithmetic done here (commands in section 6). GUESS = from
memory or not checked against a source.

Our setting, for comparison: 2 rounds (column step, diagonal step, column step, diagonal step).
One block, fixed IV, v12 = v13 = 0, v14 = block length, v15 = flags. Output word i = v[i] ^ v[i+8].
Cost: 1 unit per compression, 1/430 unit per word operation, memory free.

## 0. Bottom line

1. DERIVED. I found no published collision attack on 2-round BLAKE, BLAKE2 or BLAKE3 with the
   fixed IV that costs less than the birthday bound. The fixed-IV collision results stop at
   1.5 rounds: Li-Xu 2009, 2^96 for BLAKE-32. At 2 and 2.5 rounds the published collisions
   are free-start, meaning the attacker chooses the IV (2^112). The board's 92 to 94 is
   already past anything in print.
2. DERIVED. IDEA 1 already has a published form. Li and Xu (2009) fix 2 output words
   through message modification and then run a birthday search on the other 6 words. That is
   IDEA 1 one half-round earlier, with 2 output words fixed instead of 4. In
   meet-in-the-middle (MITM) papers the same move is called "t-cell partial-target preimage
   to collision": Li-Isobe-Shibutani at FSE 2012, and Dong et al. at CRYPTO 2021, section 6.
   Dong et al. give a cost formula (section 2.2).
3. DERIVED. Our gd_sat.py is in substance the SAT model of Autoguess (Hadipour-Eichlseder,
   ACNS 2022): symmetric relations, step-indexed knowledge propagation, and a
   sequential-counter limit on the number of guesses. Autoguess is public and also has CP,
   MILP and Groebner back ends. It can serve as an independent cross-check (not run here).
   An older precedent is Aumasson et al. (FSE 2010). Their exhaustive search found that
   inverting 1.5 rounds of BLAKE with explicit G equations needs at least 4 guessed words.
4. DERIVED. The BLAKE3 designers' own trail search (spec Table 5) gives 2^-185 as the best
   2-round trail for the hash. That figure is for a full-state trail with message-only
   differences. It does not bound attacks that need only half of the output, or that use a
   length difference in v14. The leading entries use both.
5. COMPUTED (cost per list entry is a GUESS). Under the contest cost model, a two-list join
   for IDEA 1 costs about 2^62.5 to 2^64.5 with 2 checks, 2^78 to 2^80 with 3 checks and
   2^94 to 2^96 with 4 checks. With 5 or more checks it costs more than 2^110. So up to 3
   checks clearly beats the board, and 4 checks only matches it (section 4).

## 1. Published results on the BLAKE family

"IV" column: fixed = the standard IV and a real hash. chosen = the attacker sets the
chaining value, salt or counter (free-start or semi-free-start). perm = the internal
permutation only.

| Ref | Target, attack | Rounds | IV | Cost | Use to us |
|---|---|---|---|---|---|
| [LX09] | BLAKE-32 collision | 1.5 | fixed | 2^96 | Template for IDEA 1: 2 output words controlled, then a birthday search on the other 192 bits. DERIVED |
| [LX09] | BLAKE-32 free-start collision | 2, 2.5 | chosen (h0, h2 changed and fixed up through m0, m2) | 2^112 | Needs IV freedom, so no direct use. DERIVED |
| [LX09] | BLAKE-32 preimage | 1.5 / 2.5 | fixed (no salt) | 2^192 / 2^241 | No direct use. DERIVED |
| [AGKMM10] | BLAKE-32: one round is a bijection on the message space; one round inverted explicitly | 1 | fixed | trivial | m -> state after round 0 is a bijection for a fixed IV. This is the basis for building inside-out. DERIVED |
| [AGKMM10] | BLAKE-32 preimage by guess-and-determine: guess m8, m10, m11 and one mid word | 1.5 | fixed | 2^128 | "At least four words are necessary" (exhaustive search). The same kind of question as gd_sat. DERIVED |
| [AGKMM10] | near-collision 232/256, linearised model | 4 (rounds 3 to 6) | chosen | 2^56 | No. DERIVED |
| [TU10] | BLAKE-32 near-collision 184/256, hill climbing | 2 | chosen (semi-free-start) | 2^26 | No: needs the IV, and is only near. DERIVED (eHash listing and abstract) |
| [GM09], [SWWD10] | near-collisions | 4 | chosen | 2^56; 2^21 | No. DERIVED (eHash listing, Su et al. abstract) |
| [DK11] | iterative differential plus rebound; colliding pairs for the compression function | 3 | GUESS: chosen | 2^60 | Rebound on BLAKE is known, but not with the fixed IV. DERIVED (abstract only); the IV setting is a GUESS |
| [KLN11] | rebound plus local collision; distinguisher | 10 (permutation) | perm | - | The inbound phase solves for G values in the middle of the permutation. DERIVED (slides) |
| [BNR11], [Hao14] | boomerang distinguishers | 7 to 8.5 | perm or chosen | 2^184 and up | No. Leurent showed that some of the [BNR11] trails are invalid. DERIVED |
| [GKNWW14] | BLAKE2 2.5-round collision (from [LX09]) | 2.5 | chosen | 2^112 (2s), 2^241 (2b) | No. Wikipedia's security summary lists this as a BLAKE2s "collision" without saying the IV is chosen. DERIVED |
| [GKNWW14] | BLAKE2b fixed points, rotational and squeeze attacks; 208-bit partial collisions | 12 | chosen (a symmetric IV is needed) | 2^64 | No: the BLAKE2/BLAKE3 IV is not symmetric. DERIVED |
| [EFK15] | higher-order differential MITM preimage on BLAKE-512 / BLAKE2b | 2.75 | fixed | 2^510.3 / 2^511 | MITM has been used on BLAKE, but only for preimages and barely below generic. DERIVED |
| [EFK15] | pseudo-preimage, BLAKE2s compression function | 6.75 | chosen | 2^253.8 | No. DERIVED |
| [B3spec] | best trail probabilities, BLAKE3 hash setting | 1, 1.5, 2 | fixed | 2^-1, 2^-29, 2^-185 | Rules out a classical single-trail differential at 2 rounds. Says nothing about partial-output attacks. DERIVED |
| [AFKMR08] | Rumba (four Salsa20 outputs XORed): collision via a high-probability differential | 3 | fixed-function | 2^79 vs 2^256 | Nearest ARX/ChaCha-family collision precedent; source of probabilistic neutral bits. DERIVED (abstract only) |
| [Aum19] | survey "Too much crypto", updated 2026-07-06 | - | - | - | Best real-hash preimage reaches 2.75 rounds; no BLAKE3-specific cryptanalysis cited. DERIVED |

Searches found no BLAKE3-specific reduced-round cryptanalysis paper (Crossref, web, C2SP page,
BLAKE3 spec). Blog claims that "2.5 rounds of BLAKE3 are broken" go back to [LX09] (free-start).
DERIVED. Coverage is limited (section 7).

## 2. Techniques and whether they apply

### 2.1 Message modification, inversion and inside-out construction
- DERIVED [LX09]. In 1.5-round BLAKE, the words h0 and h4 depend only on G0 of the last
  column step. Its four inputs are set by m9, m11, m13 and m15 in the preceding diagonal
  step. That gives 64 bits of output held constant at O(1) cost per message, for a family of
  2^384 messages.
- DERIVED. At 2 rounds the last half-round is a diagonal step, so each output word pairs two
  G calls. Our structural fact (out0, 2, 5, 7 depend only on E0 and E2) is the 2-round
  version of the same observation. The price is that E0's and E2's 8 input state words sit
  behind a full round of mixing, not half a round. That is why the "fixed" family is left
  with only 4 free words.
- DERIVED [AGKMM10]. For a fixed initial state, one round is a bijection between message and
  state, with explicit equations (their (1) to (10)). Inside-out parametrisation (choose round-0
  output or intermediate G values, then solve for m) is therefore standard. It is also what
  the leading entries' construction does.
- DERIVED [KLN11], [DK11], [MRST09]. Rebound / start-from-the-middle: solve the middle G
  calls for values, then extend outward with message modification and probability. On BLAKE
  it has been used only on the permutation or the free compression function.

### 2.2 Partial-output (half-digest) to collision
- DERIVED [Dong21, section 6]: if an algorithm produces messages whose digest lies in a fixed
  subspace covering t of h cells, running it (2^w)^((h-t)/2) times gives a collision. The
  MITM version costs about
  (2^w)^( h/2 - min{ DoF+ - t/2, DoF- - t/2, m - t/2, t/2 } )   (their eq. 9),
  where DoF+ and DoF- are the forward and backward neutral words and m is the matching filter.
  Credited to Li-Isobe-Shibutani (FSE 2012) for converting a pseudo-preimage into a collision.
- DERIVED. For us, w = 32, h = 8, t = 4 (out0, 2, 5, 7). The best gain is t/2 = 2 words, so
  2^64. The formula reaches that only if DoF+ >= 4, DoF- >= 4 and m >= 4 words. Their
  framework is cell-wise MILP for AES-like designs. The mapping to our "core + side A + side
  B + checks" is close but not one-to-one: in the "fixed" variant the 4 target words are
  constant by construction, not matched.
- DERIVED [LX09]. Same idea, no MITM: 2 words fixed by modification, then a memoryless
  birthday search on the remaining 6 words.

### 2.3 Automated guess-and-determine
- DERIVED [HE22] Autoguess (github.com/hadipourh/autoguess). It searches for a minimal "guess
  basis". Relations are symmetric relations: each variable is determined by the others, as
  in modular addition, XOR, or a bijection with XOR. The SAT/SMT model has state variables
  per propagation step, a step bound (--maxsteps) and a sequential-counter limit on the
  number of guesses. It also offers CP, MILP and Groebner back ends, and an "elimination
  rule" that merges relations. This is the same model as gd_sat.py.
- DERIVED [BDF11] (via [HE22]). The Bouillaguet-Derbez-Fouque tool goes further. It searches
  guess-and-determine and MITM attacks together and solves linear systems, not only one
  unknown per equation. Our --tables option (2^32 tables for small cycles) is the ARX
  analogue of that extra power.
- GUESS. A limitation shared by both tools and gd_sat: one-unknown-per-equation propagation
  cannot solve a 2-equation, 2-unknown ARX system. Some such systems are bit-serially
  solvable (Paul-Preneel FSE 2004; S-functions [MVDP10]). Rotations break the bit order,
  though, so check each case.

### 2.4 Meet-in-the-middle on ARX hashes
- DERIVED [EFK15] (building on Knellwolf-Khovratovich, CRYPTO 2012). Differential and
  higher-order-differential MITM gave 2.75-round preimages of BLAKE-512 and BLAKE2b. These
  are preimages, not collisions, and at the generic level.
- DERIVED [AGKMM10, 5.3]. In BLAKE every message word is used in every round, so there are no
  independent message chunks. Their conjecture: MITM preimages cannot exceed about 5 rounds.
  For our 2 rounds that means any "side A / side B" independence must come from guessed
  internal words (gd style), not from message chunks.

### 2.5 ARX differential tools and validity checks
- DERIVED. These are the exact-probability tools: Lipmaa-Moriai (FSE 2001, xdp+) and
  S-functions [MVDP10], which give exact probabilities and counts through carry graphs. The
  leaders' "carry automata" count is this method.
- DERIVED [Leu12]. Multi-bit constraints showed that the published BLAKE-256 boomerang trails
  of [BNR11] (7- and 8-round permutation; 6.5- and 7-round compression function) cannot be
  satisfied. Corrected trails cost more.
- DERIVED [LIM20]. Checking difference and value transitions together exposed incompatible
  published Gimli trails, including one in the specification. The general lesson: assuming
  independence across steps is the usual failure mode in ARX and AND-RX differential claims.
- DERIVED [LLW24]. The SAT/SMT characteristic search for SHA-2 (practical semi-free-start
  collision on 39-step SHA-256) is the current state of the art in SAT-driven ARX-like
  collision search (abstract only).
- GUESS. Other trail-search tools: Mouha-Preneel (SAT, Salsa20, 2013), Biryukov-Velichkov
  threshold search (2014), CASCADA (Ranea-Rechberger 2022).

### 2.6 Generic tools for the final birthday step and list joins
- GUESS (standard references, not fetched). Parallel collision search, van Oorschot-Wiener
  (JoC 1999): memoryless and GPU-friendly. Wagner, generalized birthday (CRYPTO 2002).
- DERIVED [DDKS12] (abstract only). Dissection of bicomposite problems, for better time-memory
  trade-offs.
- DERIVED. If the "fixed" family is indexed by exactly its 128 free bits, the birthday step
  can be a rho walk p -> out1,3,4,6(member(p)), which needs no stored lists. Memory is free
  in the contest anyway, so this matters only for practicality.

## 3. Published techniques used by the leading entries (rivals\, local copies)

All current leaders (93.59 Subflatus3 ef81f589, 93.73 GordoAR 6a600434, 93.7358 winglock
c19feef4, and the 94.x line) derive from Jbenisek c66f230d (ours, with tekkac). Mapping to
the literature (DERIVED from the notes and from research\pkg10\pkg\src\proof_head.md):

| Their piece | Published technique |
|---|---|
| 8 free words, given as internal values (round-0 output X2, intermediate G values of C0 and D3, S-words, w5), mapped explicitly to a 55-byte and a 63-byte message | Inside-out / start-from-the-middle construction; round inversion [AGKMM10]; message modification [LX09] |
| 55/63-byte lengths: v14 differs by XOR 8, and the difference is cancelled in K2 with six solver-found constants; digest words 0, 2, 5, 7 then agree with probability 1 | Local cancellation of an input-word change through a word of the same G ([LX09] Observation 2, there with an IV word). Constants found by SAT search, as in characteristic search |
| Remaining 128 bits: Y4 is held in a class where an E3 value has the fixed XOR difference eta = 830303cf (h1' = h1 XOR eta), and the E1 and E3 differences must cancel in the folding (their "Lemma D": D1, D3, D4, D6 = 0) | Truncated differential / partial collision on the folded output |
| Rate F * 2^-128 with F about 2^26.5, counted exactly ("carry automata", 185,350,144) under the independent-word model M | S-function / xdp+ exact counting [MVDP10]; independence assumption (H1) |
| Rule A, beta filter, staged A/B/C batches with halting budgets | Early-abort sufficient conditions (Wang-style); budgets bounded by Chernoff tails |
| Sub-class S8, outer step / X2 table / member levels | Structured trial sets (in the spirit of neutral bits, Biham-Chen 2004; PNB [AFKMR08]): GUESS for the analogy |
| 7 lanes of 36 bits in a 256-bit word, masked rotations | Bitslicing / SWAR implementation, no cryptanalytic content |

COMPUTED. 2^100.5 trials x 3.485 operations / 430 = 2^93.55, consistent with their 93.589.
DERIVED. Since c66f230d the gains are mostly engineering: batch order, stage costs, budget
margins. The S8 sub-class and the beta filter also changed the counted rate (S8 is worth a
factor of 1.29 of the margin). GordoAR also raised F from 1/2 to 5/7 of the model count (the
margin went from 2.0 to 1.4).
None of them uses MITM, list joins or guess-and-determine families.
DERIVED [Leu12, LIM20]. Their main premise, H1 (i) (model M at 2^-100.5, never tested at
that depth), is exactly the kind of independence assumption that the ARX-validity papers
found failing.

## 4. What this means for us

1. DERIVED. Nothing published blocks IDEA 1, and nothing published already does it at 2
   rounds. Reaching a 2-round fixed-IV collision at about 2^64 to 2^80 would be a new result,
   and 12 to 28 bits below the board. The lineage to cite is [LX09] (1.5-round template),
   [Dong21] / Li-Isobe-Shibutani (partial-target to collision), [AGKMM10] (inside-out) and
   [HE22] (guess-basis tool).
2. COMPUTED (cost per list entry e = 50 to 200 word operations is a GUESS). With c checks
   and a two-list join yielding 2^64 members, lists of 2^(32+16c) are needed. Total cost:
   c <= 2: 2^62.5 to 2^64.5. c = 3: 2^77.9 to 2^79.9. c = 4: 2^93.9 to 2^95.9, about the
   board. c = 5: 2^109.9 or more. Target: <= 3 checks after the core, or 4 checks with a
   join that does better than a plain two-list join (Wagner / dissection, if the checks
   split further: GUESS).
3. DERIVED. The [AGKMM10] floor (at least 4 guesses for a 1.5-round full-state inversion)
   is consistent with our k=4 and k=5 UNSAT results for the "fixed" family at 2 rounds. So
   one-unknown-per-equation propagation probably has a hard floor. The gains must come from
   the extras: --tables (BDF-style system solving), splitting into independent sides
   (MITM / Dong DoF accounting), or bit-serial solving of small ARX systems.
4. Suggested cheap checks (not run here):
   (a) Run Autoguess (CP or SAT back end) on the same relation set. It independently checks
       k=4 and k=5 UNSAT and may finish k=6.
   (b) Phrase the side split as Dong et al.'s DoF+ / DoF- / m accounting. The objective
       min{DoF+ - t/2, DoF- - t/2, m - t/2, t/2} tells directly whether a split reaches 2^64.
5. DERIVED. Results to discard: BLAKE2 fixed-point, rotational and squeeze attacks (they need
   a symmetric IV); the 2.5-round 2^112 "BLAKE2s collision" (chosen IV); all
   boomerang/impossible-differential work (permutation only).
6. DERIVED. Validity risk to manage. If a path rests on an independence model (as the
   leaders' H1 does), the literature says to check value-dependent compatibility
   ([Leu12], [LIM20]). Toy-width exhaustive checks, using job28.py's toy rotations, are the
   cheap version.
7. GUESS. A literature-flavoured second path: a 1.5-round trail (the spec says the best is
   2^-29 in the hash setting) whose round-1 difference avoids E0's and E2's inputs, plus
   folded-output cancellation in E1/E3. The leaders' route is a special case of this. A
   SAT/MILP trail search with the "difference only in the E1/E3 inputs" constraint and
   possibly a v14 length difference has not been published and may find other members of
   that class.

## 5. References (URLs; local copies in papers\)

- [LX09] Li Ji, Xu Liangyu, Attacks on Round-Reduced BLAKE, ePrint 2009/238. https://eprint.iacr.org/2009/238 (li_xu_2009_238.*)
- [AGKMM10] Aumasson, Guo, Knellwolf, Matusiewicz, Meier, Differential and invertibility properties of BLAKE, FSE 2010. https://eprint.iacr.org/2010/043 (2010_043.*)
- [SWWD10] Su, Wu, Wu, Dong, Near-collisions on the reduced-round compression functions of Skein and BLAKE, CANS 2010. https://eprint.iacr.org/2010/355 (2010_355.*)
- [TU10] Turan, Uyan, Practical near-collisions for reduced round Blake, Fugue, Hamsi and JH, 2nd SHA-3 conf. 2010. http://csrc.nist.gov/groups/ST/hash/sha-3/Round2/Aug2010/documents/papers/TURAN_Paper_Erdener.pdf (via eHash: ehash_blake.txt)
- [GM09] Guo, Matusiewicz, Round-reduced near-collisions of BLAKE-32, WEWoRC 2009. http://www.jguo.org/docs/blake-col.pdf (via eHash)
- eHash BLAKE page (archived): https://web.archive.org/web/2020/https://ehash.iaik.tugraz.at/wiki/BLAKE (ehash_blake.*)
- [DK11] Dunkelman, Khovratovich, Iterative differentials, symmetries, and message modification in BLAKE-256, ECRYPT2 Hash Workshop 2011. https://cris.haifa.ac.il/en/publications/iterative-differentials-symmetries-and-message-modification-in-bl/ (abstract only)
- [KLN11] Khovratovich, Leurent, Naya-Plasencia, Observations on Blake (slides), 2011. https://www.microsoft.com/en-us/research/wp-content/uploads/2011/03/blake-slides.pdf (kln11_*)
- [BNR11] Biryukov, Nikolic, Roy, Boomerang attacks on BLAKE-32, FSE 2011. https://link.springer.com/chapter/10.1007/978-3-642-21702-9_13
- [Leu12] Leurent, Analysis of differential attacks in ARX constructions, ASIACRYPT 2012. https://www.iacr.org/archive/asiacrypt2012/76580221/76580221.pdf (leurent_ac12.*)
- [GKNWW14] Guo, Karpman, Nikolic, Wang, Wu, Analysis of BLAKE2, CT-RSA 2014. https://eprint.iacr.org/2013/467 (2013_467.*)
- [Hao14] Hao, The boomerang attacks on BLAKE and BLAKE2, Inscrypt 2014. https://eprint.iacr.org/2014/1012 (2014_1012.*)
- [EFK15] Espitau, Fouque, Karpman, Higher-order differential meet-in-the-middle preimage attacks on SHA-1 and BLAKE, CRYPTO 2015. https://espitau.github.io/bin/HOD.pdf (efk15_hod.*)
- [B3spec] O'Connor, Aumasson, Neves, Wilcox-O'Hearn, BLAKE3 specification, sections 4.4 and 7.3, Tables 4 and 5. https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/blake3.pdf (blake3_spec.*)
- [Aum19] Aumasson, Too much crypto, ePrint 2019/1492 (rev. 2026-07-06). https://eprint.iacr.org/2019/1492 (2019_1492.*)
- [AFKMR08] Aumasson, Fischer, Khazaei, Meier, Rechberger, New features of Latin dances: analysis of Salsa, ChaCha, and Rumba, FSE 2008. https://eprint.iacr.org/2007/472 (abstract only)
- [MRST09] Mendel, Rechberger, Schlaeffer, Thomsen, The rebound attack, FSE 2009 (GUESS: not fetched)
- [MVDP10] Mouha, Velichkov, De Canniere, Preneel, The differential analysis of S-functions, SAC 2010. https://www.doi.org/10.1007/978-3-642-19574-7_3 (abstract via search)
- [BDF11] Bouillaguet, Derbez, Fouque, Automatic search of attacks on round-reduced AES and applications, CRYPTO 2011, pp. 169-187 (cited in [HE22])
- [DDKS12] Dinur, Dunkelman, Keller, Shamir, Efficient dissection of bicomposite problems, CRYPTO 2012. https://eprint.iacr.org/2012/217 (abstract only)
- Li, Isobe, Shibutani, Converting meet-in-the-middle preimage attack into pseudo collision attack: application to SHA-2, FSE 2012 (cited in [Dong21])
- [LIM20] Liu, Isobe, Meier, Automatic verification of differential characteristics: application to reduced Gimli, CRYPTO 2020. https://eprint.iacr.org/2020/591 (abstract only)
- [Dong21] Dong, Hua, Sun, Li, Wang, Hu, Meet-in-the-middle attacks revisited: key-recovery, collision, and preimage attacks, CRYPTO 2021. https://eprint.iacr.org/2021/427 (2021_427.*; section 6, eq. 9)
- [HE22] Hadipour, Eichlseder, Autoguess: a tool for finding guess-and-determine attacks and key bridges, ACNS 2022. https://eprint.iacr.org/2021/1529, https://github.com/hadipourh/autoguess (2021_1529.*)
- [LLW24] Li, Liu, Wang, New records in collision attacks on SHA-2, EUROCRYPT 2024. https://eprint.iacr.org/2024/349 (abstract via search)
- Qiao, Song, Liu, Guo, New collision attacks on round-reduced Keccak (connectors), EUROCRYPT 2017. https://eprint.iacr.org/2017/128 (abstract only; structural analogue: a 1 to 2 round solving layer followed by probabilistic or birthday rounds)
- Guo, Liu, Song, Linear structures: applications to cryptanalysis of round-reduced Keccak, ASIACRYPT 2016. https://eprint.iacr.org/2016/878 (search result only)
- Wikipedia, Hash function security summary (where the 2.5-round "BLAKE2s collision" entry comes from). https://en.wikipedia.org/wiki/Hash_function_security_summary

## 6. How the numbers in section 4 were computed

Windows python, on 2026-10-08:
`for c in 0..5: L = 2^(32+16c); units = log2(2*L*e/430 + 2^64*e/430)`, e = 50 and 200.
Result (c: e=50, e=200): 2: 62.48, 64.48; 3: 77.9, 79.9; 4: 93.9, 95.9; 5: 109.9, 111.9.
Leaders: log2(2^100.5 * 3.485 / 430) = 93.553.

## 7. Limits of this search

- DBLP returned a bot-check page and was not used. The Semantic Scholar API was
  rate-limited. eprint.iacr.org refused direct PDF downloads (403 and 429), so the PDFs were
  taken from web.archive.org copies.
- Not read in full: [DK11] (abstract only, so its IV setting is a GUESS), [BNR11], [GM09],
  [TU10], [AFKMR08], [MRST09], Wagner 2002, van Oorschot-Wiener 1999.
- Possible gaps: recent Chinese-venue or 2025-2026 ePrint work on BLAKE2/BLAKE3 that my
  searches did not surface. A future check could search ePrint by title for "BLAKE3".
