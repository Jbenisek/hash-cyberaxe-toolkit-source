# LEVELS - what we now know about the levels of the reduced Orchard Poseidon (merge of the 12 learner cards)

Written 2026-10-12. Folder `./research/poseidon/levels`. Merge only: the 12 learner cards `U1..U12\CARD.md`, the skeleton `atlas\ATLAS_POSEIDON.md`, and the old research files (QUESTIONS.md, CLOSED_DOORS.md, LEVERS.md, dig\UNIVERSE_GAPS.md section 1 and section 8) were read; nothing was re-run except a 10-line spot check (section 9). **No attack scores anywhere in this file: this is a map of a new target, points come later.**

Labels (as in the cards): OBSERVED (measured, a command is named in the cited card), PROVED (short argument or exact computation), DERIVED (follows, not fully written out), GUESS (nothing run). A card reference like `U9 s6` = card U9, section 6. "AB" = coordinates (A,B) = ((nk+c00)^5, (rho+c01)^5); "nk-degree" = degree in (nk,rho). Toys = same structure over F_q with gcd(5,q-1)=1, random Cauchy or random-MDS matrix and random constants.

Contents: 1 the plain picture and the level map - 2 coverage matrix (where we have dug and where not) - 3 the old questions translated - 4 per-level knowledge and open questions - 5 objects that span levels - 6 steps and lanes - 7 handle register - 8 errata and shaky spots - 9 spot check done in this merge - 10 least understood levels - 11 proposed next learning round.

---

## 1. The plain picture and the level map

**The target in one paragraph (DERIVED from the cards).** Three lanes, init [nk, rho, 2^65]. The map has three blocks glued by narrow interfaces. The *front block* R0..R3 is four full rounds: R0 only relabels the two inputs (bijection (nk,rho) -> (A,B)) and puts the state on an affine plane P0; R1 is the only round that is exactly solvable by hand (affine S-box inputs, zero loci are lines); R2 and R3 are dense (full triangles of monomials, nothing dropped). The *partial block* (R4, plus R5 when r=2) is nearly linear: one scalar `w = (s0+c)^5`, everything else affine; pairs whose lane 0 agree pass through it linearly; this transparency dies at three partial rounds. The *tail* R60..R63 is four full rounds that are a bijection of the 3-lane state, ending in a read of lane 0 that is one linear form of three fifth powers (rows 1,2 of the last M are dead). Every round is a bijection of F^3, so a collision exists only through the truncation to lane 0: it is **one equation on a two-dimensional domain** (a curve in the (A,B) plane), never a full-state coincidence.

**Rosetta table (levels, original round index, r = 1 and r = 2).** Trap recorded by the cards: the same round has a different level number for r=1 and r=2 after the partial block, and degrees differ by a factor 5 between nk-coordinates and AB-coordinates.

| original round | kind | level r=1 | level r=2 | S-boxes | AB-degree of a lane after the round (r=1 / r=2) | nk-degree |
|---|---|---|---|---|---|---|
| init | - | L0 | L0 | - | - | 1 |
| R0 | full | L1 | L1 | 3 (lane 2 acts on constant K) | 1 | 5 |
| R1 | full | L2 | L2 | 3 | 5 | 25 |
| R2 | full | L3 | L3 | 3 | 25 | 125 |
| R3 | full | L4 | L4 | 3 | 125 | 625 |
| R4 | partial | L5 | L5 | 1 | 625 | 3125 |
| R5 | partial | not run | L6 | 1 | - / 3125 | 15625 (r=2) |
| R60 | full | L6 | L7 | 3 | 3125 / 15625 | 15625 / 78125 |
| R61 | full | L7 | L8 | 3 | 15625 / 78125 | 78125 / 390625 |
| R62 | full | L8 | L9 | 3 | 78125 / 390625 | 390625 / 1953125 |
| R63 | full | L9 | L10 | 3, then row 0 of M only | 390625 / 1953125 | 1953125 / 9765625 |

(degrees: OBSERVED exactly by finite differences on an AB-line for the output, 5^8 (r=1) and 5^9 (r=2), U12 s9; nk-degrees by the exact leading-form tracker on 300 lines per r with 0 cancellations, U9 s1.)

---

## 2. Coverage matrix - where we have dug (archaeology record; empty squares kept on purpose)

Read from the cards (DERIVED: my reading of which probe each card actually ran on that level). Symbols: **RT** = measured on the real field and on toys; **R** = real field only; **T** = toy only; **p** = partial (a single instance, or derived only, or a related quantity); **-** = not looked at.

Probes: (a) degree and polynomial support; (b) zero loci of S-box inputs and critical (rank-1) points; (c) pair / difference behaviour; (d) backward walk (fifth roots, inverse); (e) special values, aimed hits, symmetry; (f) toy exhaustive counts.

| level | (a) degree/support | (b) zero loci / critical | (c) pairs / differences | (d) backward | (e) special / symmetry | (f) toy exhaustive |
|---|---|---|---|---|---|---|
| init (domain) | RT (lines a=0, b=0) | RT (axes, (0,0), 25 grid) | RT (weight 1 or 2) | RT (X2 roots) | RT (capacity scan, cap*) | T |
| R0 | RT | RT (3 two-zero points seen at R1.C) | RT (line of equal lane 0) | RT | RT (i-symmetry, drop dirs) | T |
| R1 | RT (301 / 21) | RT (lines; 3 points exact) | p (generic; free boundary) | p (3 roots counted) | R (aimed zeros) | T |
| R2 | RT (7751 / 351) | RT (2 rank-1 pts real; curves) | p (free boundary only) | p | R (aimed zeros) | T (implicit degree saturates) |
| R3 | RT (195001 / 8001) | R (6 pts) T | RT (the interface pair set) | p | R (aimed zeros) | T |
| R4 | RT (196251 AB; toy nk) | p (only lane 0 can vanish; not counted on real) | RT (transparent, trail) | p (1 root) | p | T |
| R5 (r=2) | RT (4,887,501 AB) | **-** | RT (trail, balance) | p | **-** | T (r=2) |
| R60 | RT (4,887,501 AB, r=1) | T only (real double zeros infeasible so far) | p (toy weights; real degrees; free boundary) | R | R (125 linear states pulled back) | T |
| R61 | R (exact lines, low/top layers) | **-** | p | p | **-** | T (agreement counts only) |
| R62 | R (same) | **-** | p | p | **-** | T (agreement counts only) |
| R63 | RT (X7, line degrees) | RT (t_j zero loci) | RT (M0 . dT = 0) | RT | RT (special t_j, dead rows) | T (all q^3 tail states) |
| output | RT (top byte) | n/a | RT | RT | RT | T |

Reading the matrix: the middle of the tail (R61, R62), the second partial round R5 and the real-field critical set beyond R3 are the thinnest squares; the front block and the object cards (MDS, field, S-box, constants) are the thickest. Section 10 turns this into a ranking.

---

## 3. The old research questions, translated into Poseidon learning questions, mapped to levels

Source files: QUESTIONS.md (the owner's question grid, stages 1-5), CLOSED_DOORS.md (headings and a few rows per family; 85 doors on BLAKE3 / SHA3 / SHA-256 / Keccak plus the "wins that were errors" table and the "near-doors"), LEVERS.md (the families only), dig\UNIVERSE_GAPS.md section 1 (ranked gaps G01..G09) plus its section 8 (Poseidon). "Status" says whether a card already answered it (card ref) or it is open; open ones have an ID used in section 4 (format `OQ-<level>-<n>`).

### 3.1 From QUESTIONS.md

| # | old question (stage) | Poseidon learning question | level(s) | status |
|---|---|---|---|---|
| T01 | New PATH or re-pricing? (1) | For each observation: is it a new fact about a level, or a restatement of a known one (X1..X12)? Tag every card statement new / known. | all | done in section 4 and 8 (every fact has a level and a source) |
| T02 | What would a home run look like? (1) | Where does each observable stop being structured and start looking like a random function? (the level at which structure ends) | R0..R3, R4, tail | partly: pair-count ratio is exact only at R0 (q/(q+1)), 0.9995 at R1, 0.99994 at R2, 1.000 after (U3 s3, U11 s2). Open: structured *subsets* (see OQ-B-1, OQ-Y-1) |
| T03 | What parts of the sphere are we missing (lenses)? (1) | Which lens x level cells are empty? Lenses here: algebraic (degree, support), geometric (planes, curves, zero loci), differential (pairs, trails), arithmetic of F_p (characters, subgroups), symmetry, inverse/backward, statistical. | all | section 2 matrix; empty squares are R5/R61/R62 zero loci, characters along a trace, symmetry beyond R0 |
| T04 | Has anything learned on another hash been tested here? (1) | Transfer checks: (i) boring-details recount (found atlas errata), (ii) birthday / meeting lens: forward half from (A,B) meets backward half from y with (T0,T1) free, (iii) "free bits die on the expansion" (SHA-256) -> "free (s1,s2) balance on the real surface", (iv) differential cores (SHA3) -> trail subspace dims. | R3/R4, R60, partial block | (i) done; (ii) OQ-B-3; (iii) OQ-B-2; (iv) done (dims 2,1,0, U3, U12) |
| T05 | Did I dismiss this by argument at today's speeds? (1) | List every statement that rests on argument only (GUESS/DERIVED) and test it where cheap. | R2, R3, interface | open list: implicit degrees 625 / 15625 (OQ-A2-1), irreducibility of the R3-equal level curve (OQ-B-1), "R3 lane-0 root-free is luck" (OQ-A3-2) |
| T06 | Dense area: what boring details does everyone copy without recounting? (1) | Recount every printed number: constants (all 192 re-derived from Grain, U6), MDS (Grain, no rejection), group orders (atlas "unfactored" was wrong), capacity 2^65, output top byte, test vectors, the organizer's profile JSON. | init, constants, field | mostly done (U6, U8); organizer's profile JSON itself not yet recounted: OQ-I-1 |
| T07 | Does every PRINTED condition hold on the published witness? (1) | Check each fact printed in the organizer's profile and TASK.md against our implementation (11/11 public vectors already match). | init | OQ-I-1 |
| T08 | Is it in the mill tailings? (1) | Which null results were instrument-limited and should be re-run with a better instrument? | constants, toys | yes: single wide LLL is blind from k>=97 (U6); fibre-count statistics are blind to every structure tried (U10). Re-do list in section 11 |
| T09 | What does the trash say (near misses)? (1) | Near misses in toys: pairs agreeing in 2 of 3 lanes; weight-1 differences reappearing; accidental zero coefficients. | out, tail | done at random-rate level (U10 s2 Q6, U11 s5, U9 s2): all Poisson-like, nothing systematic |
| T10 | Is it in the pre-contest research / archive? (1) | The archive's Poseidon claims (Luna 3: "no third-round skip via rational curves", PR 923 routes) are CLAIMED-UNTESTED here. Learning translation: are the zero-locus curves of R2 / R3 S-box inputs rational? what is their genus? | R2, R3 | OQ-A2-2 (never computed: only point counts ~q and Bezout degrees) |
| T11 | Is any 2^-k filter really a MATCH (birthday lens)? (1) | Is there a level boundary where the target splits into f(A) = g(B) with A and B independent? Candidate: front half (R0..R4) and backward half (from y, with T0,T1 free) meet at R60 entry; the only joining condition is the plane condition (M^-1 s)_2 = K (U12 s6). | R3/R4 and R60 | OQ-B-3 |
| T12 | Boring edges (rules, rounding, success, memory, padding, final step) (1) | canonical < p, 32-byte little-endian output, top byte, capacity encoding, dead output rows, which r are admitted. | init, out | done: U4 s1.5 (top byte 64 values, top two bits 00 except probability 1.6e-39), U6 s5, U11 s1 |
| T13 | Measured or copied? (2) | Upgrade every atlas "OBSERVED on a few inputs" to exhaustive toy or many real inputs. | all | done by U12 s7 (audit table); X4 found FALSE as an every-point statement |
| T14 | Preregistered with fresh seeds and a control? (2) | Every null must have a control that can fail: gcd(5,q-1)=5 toys, shuffled-output null, planted relation, changed-constant control. | all | in use: U1 s1, U6 s2, U10 s2; missing control for the factor-pattern statements (U2 s2 used 60 random matrices) |
| T15 | Is the unit right? (2) | Normalise units: nk-degree vs AB-degree (factor 5), multiplications vs S-boxes vs fifth roots, forward vs backward cost ratios (U1 says 97, U7 103, U12 ~120 by timing: three different units). | all | recorded in section 8 |
| T16 | Could the GPU do this? (2) | Exhaustive toys at q = 12289 (1.5e8 inputs) and counting passes. | toys | open: OQ-Y-2 (not attempted; U1 sampled 12289) |
| T17 | Did we COUNT EVERY CASE? (2) | Exhaustive q^2 enumeration is done to q = 1009 (some 4099); exact monomial counts on the real field to R5 / R60 (AB) and R3 (nk); exact line polynomials to the output. | all | what remains uncounted: real-field critical points beyond R3 (OQ-T-2), toys above q=4099 |
| T18 | Is the same quantity written the same way everywhere? (2) | Rosetta table (section 1); level numbers differ between r=1 and r=2; AB vs nk degrees. | all | done in section 1 |
| T19 | Which conventions does the structure rest on? (2) | original (not regenerated) constants for the reduced r; add-constants-before-S; lane-0 output; canonical input domain. | init, constants | U6 s1 PROVED consequence: constants are a slice of the R_P=56 table; rest by definition |
| T20 | Which other levers touch the same rows (joint or product)? (2) | Which structural sets share objects? M is shared by all 9-10 rounds; one determinant (0xebe164..a8ba) controls both the trail dimension and the balance of the partial block (U12 s4); the plane normal n and the trail vector u (U3, U5). Intersection grid of all special sets. | all | partly; the grid is OQ-X-1 (never run) |
| T21 | Does a smaller-looking count make the paid route cheaper? (2) | (score question) translated to: which structural facts reduce the arithmetic needed to evaluate a level (sparse partial round saves 4 multiplications, U3 s5; R0 lane 2 constant; R63 dead rows)? Recorded as arithmetic facts only. | R0, R4, R5, R63 | done (U3, U4, U9 s8) |
| T22 | Exact count or best provable case? (3) | Prefer exact counts (done: 195001 monomials etc.). | R3.. | done |
| T23 | Does it pass the checker? (3) | Every deep result gets a value check against poseidon_ref at a random point. | all | in use (U9 "MATCH" lines); one flaky exception recorded (section 8) |
| T24 | HOW did it die, and what does that say about its neighbours? (5) | For each impossibility, record the mechanism and test the neighbours: triple lane-0 equality R3&R4&R5 impossible (mechanism: det[e0;e0M;e0M^2] != 0) -> neighbours: R4&R5 without R3, det = 0 matrices (q=23 seed 1 keeps a trail for all r), r=3. | R3-R5 | partly: U3 s4, U11 s3, U12 s3; OQ-P5-2 for R4&R5 without R3 |
| T25 | Why did it fail / who shaved us? (5) | (filing questions) not applicable to a learning pass. | - | n/a |
| T26 | Update the registers (handoff, LEVERS, LENSES, QUESTIONS) (5) | This file + section 7 handle register are the Poseidon entries. | - | done here |

### 3.2 From CLOSED_DOORS.md (door types -> Poseidon doors)

| # | old door type | Poseidon translation | level(s) | status |
|---|---|---|---|---|
| T30 | "A law of 4 conditions: round 0 bijective" (BLAKE3 door 1) | All rounds bijective: no full-state collision; collision = 1 equation on a 2-dim domain, so the solution set is a curve. | all | PROVED (X1); toy exhaustive q <= 257 and U12 to 103 |
| T31 | Idea 1 / fix words, constant half, birthday | Meeting in the middle at a level boundary; the dimension of both halves at the boundary (front: 2-dim surface at R3 / R4; backward: 2 free parameters T0,T1 with one plane condition). | R3/R4, R60 | OQ-B-3 |
| T32 | Alternative parametrisations / hosts (parent-node door) | Alternative parametrisations of the domain: (A,B) coordinates (done), lines, conics, curves through special points. | init, R0 | (A,B) done (X2); curves of higher degree OQ-D-2 |
| T33 | Exchange symmetry "swapped rows" | Symmetries of the map: i-symmetry S(ix) = iS(x), mu4 scaling with zero constants, Frobenius twist of M. | R0, R1, all | i-symmetry dies after exactly one level (U7 s3); zero-constant scaling broken by constants and capacity (U10 s5); Frobenius twist untested (OQ-M-3) |
| T34 | Message-only route UNSAT / "SAT forcing per trial" | Forcing S-box inputs to chosen values by elimination / root-finding. | R1..R61 | aimed hits (S-box input = 0, 1, i) found by one univariate root-find at R1, R2, R3 (U7 s7); equal lane 0 at a level found at R1..R4, R60, R61 (U11 s6); simultaneous two-condition forcing: R1 exact, R2/R3 pair points counted (U2 s2.Q4, U9 s7) |
| T35 | SHA3 chi difference table | S-box difference spectrum of x^5 (closed form, uniformity 4). | S-box | DONE: U7 s2 (365 toy primes, 0 misses) |
| T36 | Zero-digest core / kernel classes, active-row weights | Difference weight patterns and minimal active S-boxes per round ending in a lane-0 zero (branch number 4). | R60..R63 | the branch-number tabulation is cheap and not done: OQ-T-1 (U11 s8) |
| T37 | Digest bit forced across a family (weight-79 core) | Output top byte / which output bits are forced. | out | done: top two bits 00, byte 0x40 unreachable (U4 s1.5) |
| T38 | SHA-256 "free message-word bits died on the expansion (held-fixed-words artifact)" | The balance of the partial block holds for *free* (s1,s2) but on the real hash (s1,s2) lie on the 2-dim R3 surface: does balance survive on the surface? | R4, R5 | OQ-B-2 (the exact analog of an old artifact; U12 flagged it) |
| T39 | Birthday lens closed (no independent inputs) | Same as T11. | R3/R4 | OQ-B-3 |
| T40 | "Drop row-16 relations" (which conditions are necessary) | Which of the 24-25 S-box evaluations are live: R0 lane 2 is a constant, partial rounds touch only lane 0, R63 rows 1,2 are dead. | R0, R4, R5, R63 | done: U4 s1.7-8, U3 s8 (only 2 constant values and 2 dead values in the pipeline) |
| T41 | Wins that were errors (units bug, small sample, rate error, ...) | Our own errors so far: tracker drops cancelled lane, sampling duplicates inflate pair counts, wrong X6 check, binning bug, mislabelled determinant, flaky product. | all | section 8 |
| T42 | Near-doors that are NOT closed | Open items with no verdict: section 4 open lists and section 10. | all | - |

### 3.3 From LEVERS.md (families) -> handle families

The lever register's rule (owner 10-11): record every gain however small, test transfer and composition. Poseidon translation: record every *structural handle* with level, label and a composition test. Families: coordinate relabelling (X2, X5, X11), exact linear sub-structure (partial block, tail linear points), degree handles (drop directions, top-form perfect power), zero-locus and critical-set handles, F_p-arithmetic handles (characters, 2-adicity), symmetry handles, backward-walk handles, evaluation-cost handles, interface-pair handles. The register is section 7. OQ-X-1 [T20, G08] = the composition grid: for every pair of structural sets (S-box zero loci, critical set, trail pairs, drop-direction lines, centre axes, i-related pairs, the 125 linear states) the observed intersection count against the expected one, on exhaustive toys (job J8).

### 3.4 From UNIVERSE_GAPS.md section 1 (ranked gaps) -> Poseidon

| gap | old meaning | Poseidon learning meaning | status |
|---|---|---|---|
| G01 | Poseidon is the live target with 0 cells | Build the row dig on the live profile: this whole file; cell groups IN / ROUND / OUT / TECH of its section 8 correspond to sections 4.1 / 4.2-4.12 / 4.13 / (TECH is score work, skipped on purpose) | started: 12 cards |
| G02 | memory axis | What must be held to cross each level boundary: dimension and description of the boundary object (front surface 2-dim at R3 / R4; backward family 2 parameters + 1 plane condition). Sizes in the learning sense only. | OQ-B-3 |
| G03 | characteristic family (support, bit position, signs) | Which difference supports exist per level: weight-1/2/3 patterns, trail subspaces (dims 2,1,0), 9 weight-2-stays-weight-2 directions of M | partly (U11 s3, U12 s3); full table OQ-T-1 |
| G04 | CV / first block / padding | Domain and capacity: all (nk,rho) < p admitted, capacity enters only through K = (cap+c02)^5 | done (U1) |
| G05 | BLAKE3 init, output fold, mode choices | Pinned init vector, output = lane 0 = row 0 of M after R63, which r are admitted (r=1,2; r=3 contrast probes only). Alternative output lane: GUESS that the structure is identical by symmetry of the MDS rows (all entries nonzero); not run. | partly; PR 923 variant (R0 only for r1, R0-R1 for r2) lives entirely inside levels L1-L2 of this map |
| G06 | sub-round (row/slice) cells | Step cells C / S / M per round and lane cells (section 6) | skeleton in atlas; cards add facts |
| G07 | statistical premises and ledgers | Premises our learning stands on: BPSW (not a proof) for the large primes, sampled "no structure", LLL blindness, flint product limit | section 8 |
| G08 | clustering, triple interactions, composition | Intersection grid of special sets; 0 of 30 pair points lie on a third zero-locus curve (U2 s2.Q4) | OQ-X-1 |
| G09 | neighbouring tracks and round counts | r = 0..5 contrasts (U3, U10), r=3 loses the trail and the balance (U12 s4), gcd(5,q-1)=5 control (U1, U10, U11, U12), Vesta constants untested | partly |

---

## 4. Per-level knowledge and open questions

Format per level: **Know** (label, card) / **Boring details** / **Open** (`OQ-` ids; origin = old translated T## or card-raised U#).

### 4.1 init (the domain)

**Know.**
- Domain is all (nk, rho) in [0,p)^2, no S-box input excluded; state [nk, rho, 2^65]; 2^65 is a 66-bit integer, far below p (U1 s9). The init set is a plane {s2 = 2^65}.
- Capacity and c02 enter only as cap + c02 (PROVED; toy 18/18, U1 s2). The hash depends on the capacity only through K = (cap+c02)^5, and cap <-> K is a bijection (U10 Q4). K-scan over all of F_257 and 16 values at q=769: no fibre-level structure, special K (0, +-1, +-i) not outliers (OBSERVED, U1 T3; U10 Q4 all 257 / 769 capacities).
- The 5x5 grid {0,+-1,+-i}^2 of (a,b) inputs: dull in value (no lane small, no repeat, 25 distinct outputs), special only in Jacobian rank: 0 at (0,0), 1 at the other 8 with a=0 or b=0, 2 at the other 16 (OBSERVED, U1 s7).
- The lines a = 0 and b = 0 (nk = -c00, rho = -c01): the Jacobian of the whole map wrt (nk,rho) has rank <= 1 at every level (PROVED, U9 s7, U12 s7); the map there is a function of a^5; line polynomials along the centre axis have exactly 80.00% zero coefficients at every round (OBSERVED, U9 s6). At (a,b)=(0,0) the output gradient is exactly zero (OBSERVED, U1 s7).
- With zero constants and cap = 0 the map has an exact scaling symmetry (y(lam x) = lam^(5^8) y(x) for r=0; mu4 only when partial rounds are present); the real constants and cap = 2^65 break it (real field 0/40 holds) (OBSERVED + PROVED, U10 s5).
- Difference weights at init: 2 (both inputs differ) or 1; weight 3 from R0.M on, always (OBSERVED 300 pairs r=1,2, U11 s3).

**Boring details.** i = `0x36bdcc7b...b6db`; X = 2^65 + c02 = `0x150c93fe...5dc8` is divisible by 2, 3 and 5 as an integer and has 3 trailing zero bits (OBSERVED, re-checked in section 9; GUESS: coincidence, ~1/120; irrelevant as a field element); X is a quadratic residue, not a cube, not a 4th power (U6 s5). Special capacity cap* (254-bit) puts all three R1.S inputs at zero on the plane; for the real capacity n.(-c1) - K != 0 so this never happens (U1 s2).

**Open.**
- OQ-I-1 [T06, T07] Recount every fact printed in the organizer's profile JSON and TASK.md (round list, constants hash, canonical rule, output encoding, admitted r, capacity encoding) against our implementation; list implicit conditions. Real, read-only, one agent.
- OQ-I-2 [U1 Q-c] At cap* (all three R1.S inputs zero on the plane; the three R1 lines concurrent) is anything structural different (rank at that point, fibre through it) in a toy where K can be steered to that value? Toy exhaustive.
- OQ-I-3 [U6 s9] Other capacity encodings (L*2^64 for other lengths): any effect? (GUESS: no.)

### 4.2 R0 (full round; the relabelling round)

**Know.**
- State after R0.M = M (A, B, K)^T with A=(nk+c00)^5, B=(rho+c01)^5, K=(2^65+c02)^5; hash(nk,rho) = H(A,B) for 1144 real inputs x r in {1,2} (2288 checks, 0 failures) and for every input of exhaustive toys q = 257, 769, 1009, 4099 (0 mismatches); sampled to q = 1,000,003 (OBSERVED, U1 s1; U12 s7 adds q = 23, 29, 103). (A,B) range over all of F^2: PROVED, because x -> x^5 is a bijection (gcd(5,p-1) = 1).
- c00 and c01 only relabel the inputs: complete fibre-size arrays identical in 18/18 toy runs with controls (c02, c1,0) that do change the arrays (OBSERVED, U1 s3).
- P0 = affine plane {n.s = K}, n = row 2 of M^-1 (full hex in U1 s2). Its direction space is span(M column 0, M column 1). The planes for different K are parallel translates along M column 2 (PROVED).
- Every lane-0 fibre after R0.M has exactly q points; pair ratio q/(q+1) exactly (0.9961 / 0.9987 / 0.9990 at q = 257 / 769 / 1009) (OBSERVED + PROVED, U3 s3, U11 s2). R0 is the only level whose pair statistic is exactly non-random.
- Degree-drop directions after R0.M: exactly one direction per lane, never shared, u/v = (-M_i1/M_i0)^(1/5); the lane loses its top degree (5 -> 4) and the drop is gone after one MDS (OBSERVED 35 toy configurations x all q+1 directions, plus real field; PROVED by bijectivity, U1 s5, U12 s7). With gcd(5,q-1) = 5 the count is 0 or 5.
- The exponent condition is the whole reason R0 is a bijection: with gcd(5,q-1) = 5 the image after R0 is exactly ((q-1)/5+1)^2 states (25-fold compression) and later rounds add only ~1% loss each (OBSERVED + PROVED, U10 s2.Q7, U1 s1; full-state collisions then exist, U11 s1).
- i-symmetry: pairs with nk' = i(nk+c00)-c00, rho' = i(rho+c01)-c01 are i-related through R0.C, R0.S; after R0.M the defect is the constant vector (1-i) K M[:,2]; R1.S destroys it (defect input-dependent from there on); no output relation in exhaustive toys q = 257, 769, 1009 (OBSERVED, U7 s3). The symmetry covers exactly one level.
- Inverse S-box: d = 5^-1 mod (p-1) is 254 bits, Hamming weight 125; its top 126 bits are the nibble pattern 0x33..3 = (2^128-1)/5 (PROVED: 5d = 1 mod 2^32...). Costs: plain 253 squarings + 124 mults = 377; best generic window ~306-310; a pattern-doubling chain 291 (OBSERVED by running the chain, U1 s6, U7 s6).
- R0 lane 2 acts on a constant: only 24 (r=1) / 25 (r=2) of the 25 / 26 S-box evaluations are live (U4 s1.7, U7 s0).

**Boring details.** Three F_p points where two R1.C lanes vanish simultaneously (one per lane pair, one linear solve each); in (nk,rho) each is the F_p-rational one of 25 geometric intersections of two quintic curves (PROVED, U1 s8); they sit at persistent rank 1 (see R1).

**Open.**
- OQ-A0-1 [U1 Q-d, U7, U12 Q5] Shorter addition chain for d (below 291); none searched. Arithmetic only.
- OQ-A0-2 [U1 Q-b] Local structure of the fibre through (0,0) (order of vanishing 5 in a and b): count the points of that fibre on toys vs q.
- OQ-A0-3 [U1 Q-f] Ratio test of M_i1/M_i0 against small-difference ratios (not done).

### 4.3 R1 (full; the exactly solvable round)

**Know.**
- S-box inputs are affine in (A,B): l_i = M_i0 A + M_i1 B + M_i2 K + c1_i (PROVED). Lane degree 5 in AB, 21 monomials (full triangle), 301 of 351 in nk (OBSERVED, U2 s1).
- Zero locus of each S-box input = a line in (A,B), exactly q points on the toy (PROVED + OBSERVED, 30 seeds at q=257, U2 s2.Q4). Any two lines meet in exactly one point (all 2x2 minors nonzero). The three lines are concurrent iff (M^-1 c1)_2 = -K; not equal on the real field (OBSERVED). So there are exactly 3 points with two zero S-box inputs, all F_p-rational; in toys exactly 3 in all runs (U1 s8, U9 s7).
- Those 3 points are *persistent critical points*: the state Jacobian wrt (A,B) has rank 1 from R1 on and never regains rank 2 (PROVED: rank J_k <= rank J_{k-1}); on the real field rank 1 holds at every later round to the output, r=1 and r=2 (OBSERVED, U1 s8, U9 s7).
- Top form of the AB lane polynomial is a degree-5 binary form with 6/6 nonzero coefficients; factor patterns: lane 0 {1,4}, lane 1 {1,4}, lane 2 irreducible quintic (OBSERVED, U2 s2). The directions that are F_p-roots of a lane form (R1 lanes 0,1) drop exactly one lane by one degree in that round only (OBSERVED, U2 s2.Q5).
- Implicit equation of the image surface (after M): least degree 25, unique (nullity 1) on the toy q=257; two quintic cross-sections with 25 common points, none at infinity (DERIVED); small q reduces degree (9, 9, 13, 16, 17, 19 for q = 17..53) (OBSERVED, U2 s2.Q3). Affine span of the point set jumps from dimension 2 (planes) to 3 at R1.S (OBSERVED, U2 s2.Q6).
- R1 is the only round with exactly solvable zero loci, hence the only one with closed-form two-lane-zero points (U2 s3).
- Aimed hits: one linear solve puts the R1 S-box input of lane 0, 1, 2 exactly at 0 (3/3 on the real field, U7 s7). Lane 0 equal to a target at R1.M by one root-finding of degree 5 (U11 s6).

**Open.**
- OQ-A1-1 [U1 Q-e] Local type (fold / cusp) of the image surface at the three persistent critical points: needs the local expansion in (A,B) at a point with two zero lanes. Real field, exact arithmetic, cheap.
- OQ-A1-2 [U7 Q6] Number of (A,B) giving identical R1.S outputs in two lanes (uses the quartic structure of x^5 differences); not measured.
- OQ-A1-3 [U2 Q5] Do other sparse curves exist besides the lines through a=b=0 (the a=0 line with b free was dense)?

### 4.4 R2 (full)

**Know.**
- AB-degree 25, 351 AB monomials (full triangle), 7751 of 8001 nk monomials; structural zeros inside the nk degree triangle: 250 = 50*5^(k-1) (OBSERVED, exact expansion, U2 s1).
- Zero locus of each S-box input: a quintic curve in (A,B), ~q points on a toy (217..296, mean ~255 at q=257); pair intersections have Bezout degree exactly (resultant degrees 5, 25, 125 hit the bound), 0..3 F_p points per pair on the real field (31 points over 33 pairs solved), each re-verified; 0 of 30 points lies on a third curve (OBSERVED, U2 s2.Q4). R2 real rank-1 points: 2 (pairs (0,2), (1,2); pair (0,1) none), persistent to the output (OBSERVED, U9 s7).
- Top-form factor patterns: lane 0 {1,5,19}; lane 1 {2 linear, 2 quadratic, 1 quartic, 1 quintic, 1 of degree 10}; lane 2 {1,2,5,17}; all squarefree, all coefficients nonzero; an irreducible degree-5 factor in every lane looks structural but the statistic says coincidence (0.27 vs 0.19 for random polynomials, 60 matrices) (OBSERVED, U2 s2).
- Relations among lane sets: no affine relation between R1.M and R2.M (affine dimension 6 of 6); polynomial relations of degree <= 4 none; exactly 3 independent of degree 5, the known M^-1 R2.M = (R1.M + c)^5 (OBSERVED toy, U2 s2.Q6).
- Toy implicit equation: the R2 surface sits at the counting bound for q = 17..43 (no low-degree equation at toy scale); the derived degree 625 cannot be seen at q=257 (U2 s2.Q3).
- Aimed hits at R2 lane 0 and lane 2 (S-box input = 0, 1) by a univariate degree-5 root-find in B for fixed A; root counts over 40 random A: mean 1.275 (OBSERVED, U7 s7). A single vanishing S-box derivative does not degrade the Jacobian (rank stays 2 after every round) (OBSERVED, U7 s7).

**Open.**
- OQ-A2-1 [T05, U2 Q1] Is the implicit degree of the R2 surface really 625 (R3: 15625)? Needs q ~ 1000+ and points-on-curve or line-interpolation methods rather than dense linear algebra. Toy, new method.
- OQ-A2-2 [T10] Genus / rationality of the R2 and R3 S-box-input zero-locus curves (point counts ~q only; Hasse-Weil deviations never examined). Toy exhaustive point counts vs q give a genus proxy.
- OQ-A2-3 [U2 Q4] Do any of the 31 real two-zero points (pairs of S-box-input zero loci, R1..R3) show structure after the partial block? (No point lies on a third curve: 0 of 30.)

### 4.5 R3 (full; last round of the front block)

**Know.**
- AB-degree 125, 8001 AB monomials; nk lane has **195001** monomials = the support-law prediction {ceil(i/5)+ceil(j/5) <= N}, count 1 + 10N + 25N(N-1)/2; 1250 structural zeros inside the nk triangle; no monomial outside the law and no law monomial missing, on all three lanes (OBSERVED, 54 s, U2 s1 and U9 s5). The boundary layer of the law is provably nonzero (a one-term sum), the interior is observed (U9 s5).
- Top form (degree 125, 126/126 coefficients nonzero): F_p-roots per lane 0, 0, 1; lane 0 factors 4 + 9 + 112, no linear factor (OBSERVED, U2 s2, U9 s4). Hence no F_p direction drops lane 0 or lane 1 at R3 - the lane that feeds the R4 S-box is never reduced (DERIVED hand-off, U2 s2.Q5).
- Real-field rank-1 points at R3: 6 (2 per lane pair), persistent to the output (OBSERVED, U9 s7). Pair resultants of degree 1, 25, 625.
- Lane 0 after R3 is the interface to the partial block: the level curve {f = f(P)} has nk-degree 625 (AB-degree 125), the pair set {(P,Q): f(P)=f(Q)} is a hypersurface of dimension 3 in the 4-dim pair space with ~p^3/2 pairs; toy pair counts are within 0.1% of the random-function value (OBSERVED toy q=257 / 769 / 1009, U3 s3, U11 s4). Irreducibility / smoothness of the level curve: GUESS, never tested.
- Free boundary: for a fixed first input and free A', lane 0 after R3 is a degree-125 polynomial in B'; one root-finding gives a partner with equal lane 0 (0.18 s per trial, mean roots 0.8 over 10 trials), all verified (OBSERVED, U11 s6).
- Aimed S-box zero at R3 lane 1 by a degree-25 univariate root-find in B: found, mean 0.92 roots over 12 random A (OBSERVED, U7 s7).

**Open.**
- OQ-A3-1 [U2 Q2] Full factor pattern of the R3 forms (degree 125); only the root counts are known (minutes per lane with flint).
- OQ-A3-2 [U2 Q6] Is the missing F_p root of R3 lanes 0 and 1 luck of this M? (random: ~37% each; toy count over random Cauchy matrices would answer; the toy distribution of root counts is Poisson-like, U9 s4).
- OQ-A3-3 [U2 Q3] Closed form of 1250 = 50*5^(k-1) structural zeros and whether the same closed form extends to the partial rounds (U9 gives the law; the zero count at R4 in nk-coordinates is 10N = 6250 by the same formula, DERIVED).

### 4.6 The R3 -> R4 interface (the pair set with equal lane 0 after R3)

This is the interface between the dense block and the partial block; no card owns it, and it is where the partial block's transparency becomes useful or not.

**Know.**
- Pairs with equal lane 0 after R3.M are a dimension-3 set (DERIVED); the conditional rate of agreement at every later level is 1/q, no memory: joint counts with later levels are independent (OBSERVED, U11 s4 s5).
- Within that set, those with difference on the trail direction u = (0, M02, -M01) (after R3.M) are exactly the pairs that also agree after R4.M: 33025 = 33025 at q=257 seed 1 (and 33124 = 33124 in U11), 4 other (q, seed) cells likewise; direction (d2/d1) of R3-equal pairs is uniform over the 258 directions (OBSERVED, U3 s4, U11 s3). None of those keeps lane 0 equal after R5 (0 in every row).
- Weights of differences: after R3 every R3-equal pair has weight 1 or 2 (lane 0 zero); after R4 every pair has weight >= 2 (branch number); weight 1 reappears after R60 at ~3/q^2 rate: random (OBSERVED, U11 s5).
- Free boundary at R4: lane 0 after R4 is a degree-625 polynomial in B'; one root-find 1.13 s per trial, roots found (OBSERVED, U11 s6).

**Open.**
- OQ-B-1 [T05, U3 Q2, U12 Q2] Structure of the R3-equal pair set: curve of pairs through a fixed P: irreducible? smooth? Toy: count points of the fibre curve per P (distribution vs Poisson, number of components via Frobenius statistics); real: distinct-degree factorisation patterns of the degree-625 level polynomial over many (P, A'). Also the sub-set on the trail direction (dimension 2): degree and irreducibility.
- OQ-B-2 [T38, U12 Q1] Balance of lane 0 after R4 and R5 *restricted to the R3 surface*: exhaustive toy (restrict the q^2 inputs to those with equal lane 0 after R3, then test uniformity of lane 0 after R4, R5 at fixed s0); the exact analog of the SHA-256 "held-fixed artifact".
- OQ-B-3 [T11, T31, U4 Q] The meeting structure: front surface at R4 / R60 entry (2-dim) versus backward family from y (2 parameters, one plane condition). What can be said exactly about the intersection (a curve of collisions, dimension count) and about the probe "is this R60-entry state on the front surface" (cost: ~25 fifth roots, one equation)? Toy: size and overlap statistics of front images for r=1 vs r=2 (also U4 Q4).
- OQ-B-4 [U11 Q] Joint solve of "equal after R3" and "equal after R4" (two curves in the pair space intersect in finitely many points per start): count on toys; real by resultant.

### 4.7 R4 (first partial round)

**Know.**
- X5 exact: state after R4 = M (w, s1+c41, s2+c42)^T with w = (s0+c40)^5; 0 mismatches in 1000 real states (also with carried constants, and through the whole hash for r=1,2) (OBSERVED, U3 s1; U10 s2.Q1 20000/20000 at q=1000003).
- A pair with equal S-box input (equal lane 0 after C) passes linearly: output difference = M (0, d1, d2), independent of the base state; 200/200 hand-built real pairs; negative controls 0/200 (OBSERVED, U3 s2). If the S-box inputs differ, the difference depends on the base state.
- Lane degrees along difference lines: generic d: 5,25,125,625,3125 after R4,R60..R63; d0=0: 1,5,25,125,625; d0=0 on the trail: R4 lane 0 degree 0 (OBSERVED real, U11 s5). A real R3-equal pair (found by root-finding) follows the d0=0 row exactly.
- Degree: lane degree 3125 (nk) after R4, 625 (AB); AB support: 196251 monomials per lane = full triangle, verified at a random point (OBSERVED, U9 s2).
- The first partial round makes the top forms of all three lanes scalar multiples of ONE polynomial and they stay so to the output: output top form = c * Phi3^(5^5) (r=1) / ^(5^6) (r=2), Phi3 = top form of lane 0 after R3 (degree 125, factor degrees 4, 9, 112, no F_p root). Consequence: every F_p line has exactly the generic output degree, per-variable degree equals total degree for every fixed other variable (PROVED + OBSERVED against the exact degree-1,953,125 line polynomial on two lines, U9 s4). At R4 the lanes are proportional down to degree 126; the difference of lanes is exactly the full degree-125 triangle (8001 monomials) (OBSERVED, U9 s9).
- Zero coefficients inside the triangle after a partial round are shared by all three lanes at toy size (same monomial; Poisson(N/q) accidents): the lanes' zero sets coincide where only w^5 contributes (U9 s2).
- Sparse equivalent form: M = diag(1,Mhat)*[[m00, v],[Mhat^-1 w, I]] exists (the 2x2 minor Mhat is invertible), verified on 300 states for r = 1..4 and on the whole hash; the front factor is absorbed into R3's dense M; saves 4 multiplications per partial round (12 -> 8). Entries generic (not 0, 1, equal). Lanes 1,2 cost 1 multiplication and 1 addition each beyond the lane-0 row (DERIVED) (OBSERVED, U3 s5; GUESS that 5 is minimal for generic M).
- Effective carried constants (r=1): R60 constants become c60 + M(0,c41,c42) = (0x2b6546a2..6811, 0xa57eba6..968f9, 0x965901..0161); none is 0, +-1 (OBSERVED, U3 s6, U6 s4).
- Backward: 1 fifth root (319 mults vs 939 for a full round) (DERIVED, U7 s6).
- Constants of partial-round lanes 1,2 are absorbed into the next round's constants (X5/X11); the lane-0 constant stays at the S-box.

**Open.**
- OQ-P4-1 [U9 Q1] What exactly happens to the zero-locus/critical structure in a partial round (only lane 0 can vanish)? Real-field count of F_p points where the R4 S-box input vanishes and the Jacobian has rank 1 (U9 s7: "not done on the real field").
- OQ-P4-2 [U3 Q] Non-identity lower block in the sparse form for fewer than 5 mults per round (arithmetic only).
- OQ-P4-3 [U3 Q] Pushing lanes-1,2 constants through sparse matrices to the end of the block was DERIVED, not run on the real field.

### 4.8 R5 (second partial round; r=2 only)

**Know.**
- R0..R4 and R60..R63 are identical functions in r=1 and r=2 (300 random inputs, 0 failures); G2 = Psi o R5 o Psi^-1 o G1 on full 3-lane states (600 checks), Psi = R60..R63 (OBSERVED, U12 s1).
- The collision sets of r=1 and r=2 are statistically independent: overlap of lane-0 colliding pairs at q=103, 3 seeds: 5319 / 5381 / 5145 vs 5322 / 5293 / 5315 expected (OBSERVED, U12 s1). R5 re-randomises which pairs collide.
- Trail: a difference survives k partial rounds unseen iff (M^j d)_0 = 0 for j<k; surviving direction dimension 2, 1, 0 for k = 1, 2, 3 (PROVED; real det[e0; e0M; e0M^2] = `0xebe164ab9dff92f6f90c296e3b831a7221b9f7429d21e01d7dc2ebf46e8a8ba`, nonzero). Largest r with a trail is 2. Trail vector u = (0, M02, -M01); (Mu)_0 = 0, (M^2 u)_0 = `0x3141e9b5...5747` != 0; 200 real pairs along t*u pass R4 and R5 with the proven formulas (OBSERVED, U3 s2-s4, U12 s3).
- Exhaustive toys q = 17, 23, 37: pairs of distinct states with equal lane-0 S-box input in all r partial rounds = n(q^(3-r)-1)/2 exactly (r = 1..4); equal lane 0 after R3, R4, R5 together: exactly 0 (random would give 128 / 384 / 504 at q = 257 / 769 / 1009), while R3&R4 only is at the random rate (OBSERVED, U3 s4, U11 s3, U12 s3). A valid MDS matrix can keep a 1-dim trail for every r (q=23 seed 1: det = 0): the real M passes only because the determinant is nonzero (OBSERVED, U3 s4).
- **Balance of the partial block (new, not in the atlas):** with the entry lane 0 fixed and (s1,s2) free, lane 0 after one partial round and after two takes every value exactly q times (all 36 toy cases q = 23, 29, 37, 103, 3 seeds, entry lane 0 in {0,1,5}); after three it is not balanced. The same determinant controls it: the 2x2 minor of the coefficient matrix of (y0, L) equals det[e0;e0M;e0M^2] (OBSERVED + PROVED, U12 s4; decomposition checked on 200 real states).
- AB support at R5 (r=2): 4,887,501 monomials per lane = full triangle on all three lanes, verified at a random point (340 s) (OBSERVED, U9 s2). Degree 15625 (nk), 3125 (AB) (U3 s3, U12 s2).
- Effective constants for r=2: R5 lane-0 constant becomes c50 + M01 c41 + M02 c42 = `0x39dce27c...37ee`; R60 constants (0x316d25f0..4d0e, 0x2c284cc1..4c83, 0x36c5e753..6831) (OBSERVED, U3 s6, U6 s4).
- Backward: 26 fifth roots in total for r=2 (23 to the state after R0.M); the extra root is exactly the extra partial S-box (OBSERVED, U12 s6).

**Open.**
- OQ-P5-1 [T24, U12 Q3] Algebraic degree and structure of Psi o R5 o Psi^-1 as a map on F^3 (the conjugation view); does r partial rounds = r conjugates give a usable recursion?
- OQ-P5-2 [T24, U11 Q] Pairs that agree at R4.M and R5.M but not at R3.M (codimension-2 condition at R4 entry): exact parametrisation and count.
- OQ-P5-3 [U12 Q1] R5 has had no zero-locus or Jacobian census of its own (probe (b) empty); lane 0 is the only S-box.
- OQ-P5-4 [U4 Q] Do the front images (R0..R4) and (R0..R5) overlap inside R60-entry space (toy, exhaustive)?

### 4.9 The partial block -> tail interface

**Know.** After r=1: the entry difference at R60 is M(0,d1,d2) (a 2-dim subspace); after r=2 along the trail: spanned by M^2 u = (0x3141e9..5747, 0x1978ec47..120e, 0x167d4c4f..389f) (OBSERVED, U12 s3). A difference with d0 = 0 entering a *full* round is not transparent: lane degrees after R60.M are [5,5,5] not [1,1,1] (OBSERVED real, U11 s3). Zero-pattern of a difference is preserved by C and S (S bijective lane-wise); only M changes it, with branch number 4 (wt(d)+wt(Md) >= 4) (PROVED from nonzero entries and minors, U11 s3).

**Open.**
- OQ-W-1 [U12 s3, U3 Q] What the tail does with the fixed-direction trail difference M^2 u t (unknown scale t): not followed on the real field; toys showed only the random collision rate.
- OQ-W-2 [U11 Q] Activity table: minimal number of active S-boxes per tail round for differences that end in M0 . dT = 0 (see OQ-T-1).

### 4.10 R60, R61, R62 (the tail's first three rounds)

**Know.**
- The tail is a bijection of F^3 with Tail degree exactly 625 as a function of any R60-entry state (OBSERVED on two random lines, 640 points, U4 s1.3); R60..R63 are identical in r=1 and r=2; the hash degree is 5^4 x (front degree) (U4 s3).
- R60 (r=1): AB support 4,887,501 monomials per lane = full triangle on all three lanes, verified at a random point (808 s) - the first full round after the partial block, all three S-boxes act on degree-625 lanes (OBSERVED, U9 s2). Degrees per round on exact line polynomials: 15625 (R60), 78125 (R61), 390625 (R62), 1953125 (R63), zero coefficients strictly inside the degree range: 0 on every lane at every round; r=2 to 9,765,625 with 0 interior zeros (899 s, 6.8 GB) (OBSERVED with a value check at each round, U9 s6).
- Lowest layers: every one of the 7381 monomials of AB-degree <= 120 is present in every lane at every round from R3 on, to the output; top layers: the top 9 (r=1) / 6 (r=2) homogeneous layers of the output are dense with 0 zero coefficients (OBSERVED, U9 s2).
- Backward: 3 fifth roots per full round (939 mults each); 12 for the whole tail; 25 (r=1) / 26 (r=2) to the R0 input (OBSERVED, U4 s1.2, U12 s6).
- Free boundary: equal lane 0 after R60 (degree 3125 in B'): 13.6 s per trial; after R61 (degree 15625): 64.4 s; roots found and verified; R62 started and not finished (OBSERVED, U11 s6, addendum).
- Degree-drop in the tail: the leading coefficient of Tail(u) along direction u in R60-entry space is G(u)_0, G = four rounds of (S then M) with constants deleted (homogeneous of degree 625, OBSERVED); building u by running the constant-free map backward from (0,a,b) gives G(u)_0 = 0 and degree 624 on that line (OBSERVED). A curve of directions (one equation on P^2) drops the degree by at least 1; how far it can drop is unknown (U4 s1.3). For lines through the *front* surface (nk,rho)-lines, no F_p direction drops the degree (PROVED via Phi3, U9 s1): the tail's drop directions are not reachable by lines of inputs.
- 125 points of the R60-entry space where R63 is purely linear: all t_j = (state after R62.M + c63)_j in {0,+-1,+-i} (125/125 OBSERVED; each pulled back through R62, R61, R60 with 9 roots and forward-checked), same for r=1,2 (U4 s1.4).
- State Jacobian rank 1 at later rounds for the real-field rank-1 points inherited from R1..R3 (11 points total, U9 s7).

**Open.**
- OQ-T-1 [T36, U11 Q] Minimal-active-S-box / weight table for the four tail rounds (cheap, exact, branch-number arithmetic, verify on toys).
- OQ-T-2 [U9 Q1] Real-field double-zero (rank-1) points at R60..R62 and single-zero-with-dependent-rows points (R2 on): resultant degrees (5^k)^2 are infeasible by direct elimination; is the count the number of F_p-points of a fixed variety? Toy census gives 30-50 points that saturate (do not grow with q).
- OQ-T-3 [U4 Q] How low can the Tail degree go on special curves of directions (624 reached; 623?). Finite-difference probe takes 640 evaluations and works at every level boundary.
- OQ-T-4 [U4 Q] Where do the 125 linear R60-entry states and the lines t_j = t_k = 0 pulled back to R60 entry sit relative to the front surface? Membership test is cheap (OQ-B-3).
- OQ-T-5 [U9 Q4] Depth at which lanes are proportional at R60..R63 after full rounds re-mix them (layer-wise differences of exact polynomials; the truncated top-layer ring could do it).
- OQ-T-6 [U11 Q] Free-boundary depth: R62, R63 and r=2 (R5, R60) not reached; time against degree: 625 -> 1.13 s, 3125 -> 13.6 s, 15625 -> 64.4 s.
- OQ-T-7 [U4 Q] Does the 2-dim backward family (T0,T1 free) at R60 entry have a nice description (curves of what degree)?

### 4.11 R63 (last round) and the read

**Know.**
- y = sum_j M0j T_j with T = S(state after R62.M + c63); 0 mismatches in 1000 inputs for r=1 and 1000 for r=2, and 20000/20000 at q = 1,000,003 (OBSERVED, U4 s1.1, U10 s2.Q1). Rows 1,2 of the last M are dead: changing R63.M lanes 1 or 2 by +1 never changes y (both r); the adjoint is zero there in 100/100 points; R63.M lanes 1,2 are the only dead values and R0.C / R0.S lane 2 the only constant values in the whole pipeline (OBSERVED, U4 s1.7-8).
- Gradient wrt the lanes after R62.M = M0j * 5 * t_j^4: zero only at t_j = 0 (PROVED).
- If two of the three t_j are 0, y = M0j t_j^5 (one fifth power); if any t_j is 0, y depends on two fifth powers (count 3q^2-3q+1 states in the toy, exact match q = 103, 257); if every t_j in {0,1,-1,i,-i}, y = M0 . t linear (OBSERVED, U4 s1.4).
- A collision means M00 dT_0 + M01 dT_1 + M02 dT_2 = 0 with dT != 0 (PROVED): at least two of the three S-boxes of R63 are active. For a lane-0 collision the weight before R63.S must be >= 2.
- Toy tail (q = 103 and 257, all q^3 states): tail on states is a bijection; every y has exactly q^2 preimage states at R60 entry (X7 consequence) (OBSERVED, U4 s4).
- Backward from y: choose (T0,T1) freely, T2 = (y - M00 T0 - M01 T1)/M02, then 3 roots per full round; a random (T0,T1) violates the plane condition (OBSERVED residual nonzero); the preimage set of y is the curve where the residual vanishes (PROVED, U12 s6).

**Open.** Covered by OQ-T-1..7 above (the R63 card has no separate open item beyond them).

### 4.12 output

**Know.** Output = 32 bytes little endian of lane 0. Top byte takes exactly the 64 values 0..63, uniform (chi-square 61.2 on 63 df, 10^5 inputs, r=1; 80.9 for r=2, 3x10^4 inputs); the top two bits are 00 except with probability 1.6e-39 (PROVED); 0x40 is unreachable by sampling (OBSERVED + PROVED, U4 s1.5; the chi-square in `u4_facts_output.txt` is mis-binned, use `u4_q5_fix_output.txt`).

**Open.** None specific.

---

## 5. Objects that span levels

### 5.1 The MDS matrix M (same in all 9-10 rounds; card U5, U3, U8)

**Know.**
- Cauchy M_ij = 1/(x_i + y_j) with x_i, y_j from the Grain stream (below), 251-254 bit differences, no small ratio, no integer relation with |c| <= 4 (OBSERVED null, U5 s4). det M non-residue; Legendre pattern of M: rows (-,-,+), (-,+,+), (+,-,+).
- The characteristic polynomial is irreducible; eigenvalue alpha is a **primitive element of F_{p^3}**: ord M = p^3 - 1 exactly (about 2^765); M is a Singer cycle of GL_3(F_p), M^k is scalar iff (p^2+p+1) | k, order mod scalars p^2+p+1 (OBSERVED by checking alpha^(n/q) != 1 for the 11 primes q | n, with BPSW-only primality, U5 s2, U8 s5; three learners got the same factors). M^k and M^-k have all entries nonzero for k = 1..200000, fully MDS (entries and minors) for k = 1..1000; bad k are 9 lines + 9 conics of P^2(F_p), first bad k near 2^250 (DERIVED from toy exhaustion at q = 257, 769, 1009 with 18/q bad fraction) (U5 s3).
- The three planes {(Mv)_i = 0} meet pairwise in the columns of M^-1; the trail line (0,M02,-M01) lies in the plane {(Mv)_0 = 0} and misses the other two; the three lines {v_0 = 0} meet P_i in slopes that are Moebius images of the Cauchy x_i (PROVED, U5 s5). None of those lines lies in the direction plane of P0 (U5 s5).
- In the Krylov basis M is multiplication by alpha; each lane is a trace form Tr(beta_i z); none of the beta is special (OBSERVED, U5 s7). Kummer model F_{p^3} = F_p[theta]/(theta^3 - 2), Frobenius = diag(1, omega, omega^2) (U8 s5).
- M^-1 is not Cauchy but has displacement rank 1 (OBSERVED, U5 s1). The 2x2 minor Mhat = M[1:,1:] is invertible (U3 s5).
- Nothing about the real M lies outside the ordinary range of random Cauchy matrices on the statistics tried (1000 matrices; irreducible + primitive is a ~1-in-9 coincidence) (OBSERVED, U5 s8); Cauchy vs random-MDS is invisible to fibre and pair statistics and to the plane / carry / end-form / trail identities (U10 s2).

**Boring details.** M12 is a 256th power (2-depth 8), M11 an 8th power, x2-x1 a 32nd power (OBSERVED; M12 d2 = 8 and M11 d2 = 3 re-checked in section 9; GUESS chance, ~3.5% that one of 9 entries is that deep). y1-y0 and y2-y0 have identical characters but different values (U8 s4).

**Open.**
- OQ-M-1 [U5 Q] Does the whole hash have a useful description in F_{p^3} coordinates between S-boxes (alpha^k phi(state)) on the partial block? 
- OQ-M-2 [U5 Q] Why do the nine conics of M^k (minors) give no simple relation with the Cauchy parameters (second look with a CAS).
- OQ-M-3 [T33, U5 Q] The Frobenius twist: is the hash symmetric under a field-automorphism-like action? untested.
- OQ-M-4 [U8 Q] Discrete log in F_{p^3}^* now conceivable for the smooth parts; any use for the 63+1 repeated applications is unexplored (GUESS: none).
- OQ-M-5 [U3 Q] Does the organizer's M family guarantee det[e0;e0M;e0M^2] != 0 or is it luck for this matrix? (toy: 1 of 6 random MDS had 0)
- OQ-M-6 [U8 Q] Why is M12 a 256th power; does it matter for any 2-adic filter?

### 5.2 The constants table (card U6; also U3 s6, U8 s4)

**Know.**
- All 192/192 constants reproduce exactly from the halo2 Grain generator: field=1, sbox=0, n=255, t=3, R_F=8, R_P=56, 160-bit warm-up, taps 0,13,23,38,51,62, 255 bits read big-endian, rejected if >= p (212 rejected draws). The six Cauchy parameters follow in the same stream drawn *without rejection*, reduced mod p (3 of 6 were >= p); then the MDS matches 9/9. Regenerating with R_P=1, 2, 55, 57 gives entirely different numbers: the reduced target uses the R_P=56 table slice (OBSERVED, U6 s1; PROVED consequence).
- Every relation search is null and calibrated: no c_s = M^k c_r for k in -8..8 over all 64*63 ordered pairs (0 of 68,544); no collinear pair (0 of 68,544), no c_s in the plane of (c_r, M c_r) etc. (0 of 12,096), no coplanar triple (0 of 41,664); calibration on toy q = 257, 12289, 65537, 1000003, 7340033 shows the same detectors fire at the predicted accidental rate (OBSERVED, U6 s6).
- Lattice nulls: the 10 used rounds, MDS entries, effective (carried) sets for r=1, 2, per-round and per-lane columns are generic; block-covering (all 3- and 4-block unions of 12-value blocks plus the number 1: 560 + 1820 LLL runs) excludes any integer relation of norm < ~30 among at most 4 constants; **a single wide LLL is blind**: a planted 3-term relation is recovered up to k = 65 values and missed from 97 (OBSERVED, U6 s2).
- Statistics uniform: top byte chi-square p 0.19; bit lengths p 0.11; 90/192 QR; Hamming weight mean 127.23; 2-adic order spectrum matches the halving law; x^5-c has pattern (1,4) for all 192 (OBSERVED, U6 s3, s5; U8 s3-4).
- The constants of lane 0 and 1 in R0 relabel the inputs; those of lanes 1,2 in partial rounds are carried into the next round; only X = 2^65 + c02 matters through K (X2, X5, X11; U6 s0).

**Open.**
- OQ-K-1 [U6 Q] Relations not yet searched: products (c_a c_b = c_c c_d), powers (c_a^5 vs others), the Cauchy parameters x_i, y_j (only M_ij entered the lattice), partial relations on 2 of 3 lanes. Use block-covering (never a single wide LLL).
- OQ-K-2 [U10 Q3] Residual mu4 relations c_s = lam c_r (lam in {1,-1,i,-i}) between rounds, not searched (only M^k relations).
- OQ-K-3 [U6 Q] Is the 2-adic order spectrum of effective constants (2^32 | 102 of 192) relevant to the 2-adic structure of x -> x^5 on the dense block?
- OQ-K-4 [U6 Q] Other Poseidon instances (Vesta constants) as comparison data (not looked at).

### 5.3 The S-box x -> x^5 (card U7; U8 s2)

**Know.**
- Bijection (gcd(5,p-1)=1; Phi5 irreducible over F_p so x^5 = 1 only at x = 1); fixed points 0, 1, -1, i, -i (5 = 1 mod 4 and p = 1 mod 8); derivative 5x^4 vanishes only at 0; differential uniformity 4.
- Differential spectrum has a closed form: (x+a)^5 - x^5 = b has N = (1 + chi(u-1)) + (1 + chi(-u-1)) solutions with u^2 = (b + 8h^5)/(10h^5), h = a/2. For Pallas (p = 1 mod 8) per fixed a: 0 solutions for 5(p-1)/8 values of b, 2 for (p+3)/4, 4 for (p-9)/8, exactly one b with 3. Fitted on 365 toy primes with 0 misses (the other residue classes of q mod 8 are in U7 s2) (OBSERVED + PROVED for the reduction; the four counts are DERIVED fits).
- Quadratic character, quartic character and 2-depth of every value are preserved by x -> x^5; the octic exponent goes e -> 5e mod 8; the two cubic classes swap (PROVED from 5 odd, 5 = 1 mod 4; real 2000/2000). C and M do not preserve them, so characters survive the S layers and are scrambled by C and M (U8 s2).
- x^5 - c = (x - r)(irreducible quartic) for every c != 0 (300 random c, all 192 constants, toys) (U8 s3).
- Cycles of x -> x^5 on F_p^*: 15,683,600 cycles, 235 distinct lengths; short ones only in the 2^32*3*463 subgroup (1: 4 elements, 2: 20, 4..256: 6 cycles each, 462: 24, 512, 924); longest 2^235 holds 49.9% of the elements; 5 is a primitive root modulo both big primes of p-1 (U7 s1, U8 s2). Atlas slip corrected: the order of 5 mod 3 is 2 and mod 463 is 462 (section 8).
- The 125 triples in {0,+-1,+-i}^3 are fixed by the S layer; M sends 124 of 124 nonzero triples out of the set; a state can stay special only as the zero vector (OBSERVED, U7 s4).
- S(lam x) = lam^5 S(x): symmetry for lam in mu4 (see init and R0).
- Polynomial normal form (U7 s5): without constants the k-round map lives in the lattice 5Z^3 (3, 21, 351 monomials for k = 1,2,3); with constants F,F has 2076 monomials per lane = #{(a0,a1,a2): sum ceil(a_j/5) <= 5}; P (R4) has 8 monomials with constants, 3 without; P,P 196 / 24; P,P,F 14,976 / 956.
- Probability of a random S-box input hitting 0 or a fixed point is 5/p per input; toys match 1-(1-s/q)^n; aimed hits are found by one root-find (U7 s7).
- Cost: x^5 = 3 multiplications; x^d about 103x (U7), 97x (U1, multiplication count 291/3), ~120x (U12, Python timing 110 us vs a forward S-box): three different units (section 8).

**Open.**
- OQ-S-1 [U7 Q1] Branching of the 2-to-4 pair structure in a backward walk (about 1/8 of b have 4 preimages of the difference): chains across 3 rounds, branching factor.
- OQ-S-2 [U7 Q2] Coordinate change making the constants vanish on a sublattice (gap between 351 and the dense counts).
- OQ-S-3 [U7 Q3] Any "symmetry with a constant defect" when the pair is chosen at R1.C or deeper (defects in the kernel of (M^-1 .)_2).
- OQ-S-4 [U7 Q4] Simultaneously steering two or more S-box inputs (two equations in (A,B)): how many solutions at levels R2 / R3 (the 31 real two-zero points answer this for pairs; triples: 0 of 30).
- OQ-S-5 [U7 Q5] Cycles of the round map on a sub-plane (toy q=257, r=1, exhaustive) vs the bare S-box prediction.
- OQ-S-6 [U8 Q1, Q5] A coset or subset surviving C + S + M for a step (e.g. {+-1,+-i}^3); characters of S-box inputs along an actual trace vs the output.

### 5.4 The field F_p and its subgroups (card U8; also U5, U7)

**Know.**
- p = 1 + 2^32 t (t odd, 223 bit). p-1 = 2^32 * 3 * 463 * 539204044132271846773 (69 bit) * 8999194758858563409123804352480028797519453 (143 bit). p+1 = 2 * 43 * 257 * 25457 * 798828148463 (40 bit) * a 186-bit prime. p^2+1 = 2 * 5 * 13 * 132437 * a 484-bit prime. p^2+p+1 = 3 * 73 * 5839 * 12221196943 * 5187662682403 * 487887715480415483992657 (79 bit) * a 334-bit prime. All four group orders are now completely factored (the atlas "unfactored C, C'" were only a rho limit) (OBSERVED with ECM; BPSW probable primes, not certified; products re-multiplied; three learners independently) (U5 s2, U7 s1, U8 s1; products and the p-1, p^2+p+1 splits re-checked in section 9).
- 2-Sylow subgroup H cyclic of order 2^32; S acts on H as multiplication by 5 on Z/2^32; smallest quadratic non-residue 5, smallest non-cube 2; sqrt(2) exists; elements of order 2^k are listed in `U8\tower.json`. 2-depth histogram of F_p^* is exactly (p-1)/2^(d+1) at depth d (OBSERVED exhaustively on every toy).
- The 5th roots of unity live only in F_{p^4} (in the p^2+1 part); x^5 is a bijection because 5 divides none of p-1, p+1, p^2+p+1. Phi5's Frobenius is the 4-cycle zeta -> zeta^2 (DERIVED).
- Constants: 90 of 192 are residues, 72 cubes (expected 64), 45 fourth powers (48), one 463rd power; octic counts (22, 28, 15, 27, 23, 30, 30, 17) chi-square 9.5 on 7 df: random.

**Open.** OQ-F-1 [U8 Q1] a 2-adic coordinate useful across a level (S is linear in log coordinates of H; C and M are not); OQ-F-2 [U8 Q6] effects that only appear at 2-adicity ~32 (no toy of that size can be enumerated: nearest exhaustive 2-adicity is 12 at q = 12289 sampled only); OQ-F-3 certify the large primes (BPSW only so far).

### 5.5 Degrees and polynomial shape (card U9; U2, U12)

**Know.** See levels above. Summary: degrees x5 per round (full or partial) in AB (5^(rounds-1)) and nk (5^rounds); the (nk,rho) support is exactly {ceil(i/5)+ceil(j/5) <= N} (count 1 + 10N + 25N(N-1)/2) with the boundary provably present, interior observed to R3 on the real field and to R4 on a toy; AB supports are full triangles to R5 and R60; the output top form is a perfect power; the only forced zero coefficients are on the two centre axes (80.00%); rank never recovers; line polynomials are dense off-centre; real polynomials have no accidental zeros while toys show Poisson(N/q) accidents (U9 s10). The output nk-polynomial has ~1.9e12 monomials for r=1 against 144 multiplications for the circuit (U9 s8).

**Open.** OQ-D-1 [U9 Q5] layer patterns between the top 9 and bottom 121 layers of the output; OQ-D-2 [T32, U9 Q3] images of conics / higher-degree curves (can composition lower the top form?); OQ-D-3 [U9 Q6] the one flaky run (section 8).

### 5.6 Toy copies as an instrument (card U10; also U1, U3, U12)

**Know.**
- Exhaustive toys: q = 17, 23, 29, 37, 103, 257, 769, 1009, 4099 (some runs), sampled to 12289, 65537, 786433, 1000003; gcd(5, q-1)=1 holds for all (1000003: q-1 = 2*3*166667); controls q = 11, 31, 41, 61, 71, 101, 131, 151, 181, 191, 211, 251, 1051 with gcd 5; 2-adicities 1, 4, 8, 12, 16, 18 present.
- Fibre and pair statistics are blind to everything tried: Cauchy vs non-Cauchy, 2-adicity 1..16, all 257 / 769 capacities, r = 0..3, fibre differences (no preferred difference vs shuffled null), K = 0. They show structure only when constants and capacity are zero (exact scaling) or the exponent condition fails (U10 s3).
- What sees structure: exact identities (X2, X5, X7), exact counts of structured subsets (trail pairs; stacked equal-lane-0 = exactly 0; balance), symmetries, and the exact injectivity fingerprint q^2/(q^2+q+1) = 0.9961 at q = 257 for (lane 0, lane 1) pair counts, which matched 0.9956 (U10 s3).
- Sampling with replacement inflates pair counts by duplicate inputs: subtract them (U10 s5).

**Open.** OQ-Y-1 [U10 Q1] An instrument other than fibre counts that sees the front/partial/tail structure: the agreement lattice (pairs equal in lane i at levels in S, all subsets S) is one candidate (section 11). OQ-Y-2 [T16] exhaustive q = 12289 on GPU; OQ-Y-3 [U10 Q7] effect of a non-MDS matrix (a zero entry or zero minor) on any statistic; OQ-Y-4 [U10 Q6] number k of projective zeros of the full-rounds-only zero-constant form (k = 0, 0, 2, 3 at q = 257, 769, 1009, 4099): is it predictable and what is it at p?

### 5.7 What a collision is (card U11; U12 s1)

**Know.** A collision is a pair of distinct canonical inputs with equal lane-0 outputs; the 3-lane map is a bijection so the final states differ in lane 1 and/or lane 2 (exhaustively: pairs equal in lanes 0 and 1 happen at the random rate, 32814 at q=257 vs 33024 expected; pairs equal in all three lanes never); lanes 1,2 of the final state are produced by dead rows; the live statement is M0 . dT = 0 with dT != 0. Zero pattern of a difference is preserved by C and S; the branch number of M is 4. Pairs equal in lane 0 at a given level follow a 1/q rule at later levels (no memory) except the exact R3&R4 trail relation. Equal lane 0 at one level is cheap to force through R1..R4, R60, R61 by one univariate root-find (degree 5^L in B', mean roots ~1). The level of the first impossibility is three consecutive partial equalities (PROVED for the real M).

### 5.8 r = 1 versus r = 2 (card U12)

**Know.** r=2 = r=1 with R5 inserted, conjugated by the tail; same prefix and suffix; degree x5; trail dimension 2 -> 1; collision sets independent; one more fifth root backward (26 vs 25); the same determinant controls the trail dimension and the balance; exact AB-line output degrees 5^8 and 5^9 (166 s and 885 s finite differences); three narrow interfaces: front -> partial (a 2-dim surface in F^3), partial -> tail (w, s1, s2) -> M(w, s1+c, s2+c), tail -> output (one linear form of three fifth powers).

---

## 6. Steps and lanes (the "doors" inside a round)

| step | what it does to a difference / a structure | known behaviour |
|---|---|---|
| C (add constants) | translation: difference unchanged, zero pattern unchanged | constants: R0 lanes 0,1 relabel input; partial-round lanes 1,2 carry into the next round; lane 2 of R0 combined with capacity into K; the rest are plain translations. No relation among constants (U6). |
| S (x^5) | bijection per lane; zero pattern of d preserved; derivative 5x^4; 5 fixed points; characters mostly preserved | acts on 3 lanes (full) or lane 0 (partial); R0 lane 2 acts on a constant; difference spectrum uniformity 4; special values {0,+-1,+-i}. |
| M (MDS) | the only step that changes the zero pattern; branch number 4; Singer cycle; Cauchy | nothing special statistically; columns of M^-1 = intersections of the coordinate-zero planes; P0 direction space = span(col 0, col 1); trail vector from row 0. |

| lane | role |
|---|---|
| lane 0 | the only S-box in partial rounds; the output lane; carries the trail condition (M d)_0 = 0; "equal lane 0 at a level" is the object of every pair statistic |
| lane 1 | input rho; untouched in partial rounds (linear); dead after the last M |
| lane 2 | constant 2^65 until R0.S (acts on a constant, gives K); untouched in partial rounds; dead after the last M |

---

## 7. Handle register (every structural handle, even small; labels as in the cards; composition tests are open)

Rule (LEVERS.md): record every handle, test transfer and composition. No scores. "Composes?" is the open grid OQ-X-1.

| id | handle | levels | label | composes? |
|---|---|---|---|---|
| H1 | (A,B) coordinates: hash(nk,rho) = H(A,B), (A,B) free in F^2 | init, R0 | PROVED + OBSERVED exhaustive toys | untested with H6 (R1 lines) in nk space |
| H2 | carried constants (X5/X11): lanes 1,2 constants of partial rounds move into the next round | R4, R5, R60 | PROVED + 1000 real states | with H5 (sparse form) DERIVED only |
| H3 | end form y = sum_j M0j T_j; rows 1,2 dead | R63, out | PROVED + 1000 inputs | with H10, H11 |
| H4 | trail transparency: d0 = 0 passes a partial round linearly; dims 2,1,0 for k = 1,2,3 | R4, R5 | PROVED + OBSERVED real + toy | with H16 (same determinant) |
| H5 | sparse equivalent partial block (saves 4 mults per partial round, r=1..4 verified) | R4, R5 | OBSERVED | with H2 |
| H6 | R1 S-box zero loci are lines: exactly 3 two-zero points | R1 | PROVED + toy exhaustive | feeds H12 |
| H7 | forcing by one univariate root-find: aimed S-box zero (R1-R3), equal lane 0 at a level (R1-R4, R60, R61) | R1..R61 | OBSERVED real | open: two forcings at once (OQ-S-4, OQ-B-4) |
| H8 | degree-drop directions: R0 one per lane (transient); R1/R2/R3 F_p-root directions drop one lane by one; tail curve of directions drops to 624 | R0..R3, tail | OBSERVED | relation to the trail vector never computed (U3 Q) |
| H9 | output top form = c * Phi3^(5^5) (r=1) / ^(5^6) (r=2); Phi3 has no F_p root | R4..out | PROVED + exact check | closes H8 for input lines |
| H10 | 125 linear states at R63.S (all t_j in {0,+-1,+-i}), pulled back to R60 entry | tail | OBSERVED | relation to the front surface open (OQ-T-4) |
| H11 | two t_j = 0: y depends on one fifth power (1-dim set per pair) | R63 | PROVED + OBSERVED | pulled-back curves open (U4 Q) |
| H12 | persistent critical points (rank-1 points never regain rank): lines a=0, b=0; 3 points at R1, 2 at R2, 6 at R3 (11 real); toys saturate at ~30-50 | R1..out | PROVED (never recovers) + OBSERVED counts | counts for R4..R62 open |
| H13 | centre-axis sparsity: on a=0 or b=0 the map is a function of a^5 (80.00% zero coefficients) | all | PROVED + OBSERVED | the only forced-zero structure found |
| H14 | i-symmetry (one level) | R0 | PROVED + OBSERVED | dies at R1.S |
| H15 | mu4 / scaling symmetry with zero constants and cap 0 | all (toy-only) | OBSERVED, broken in the real hash | residual relations OQ-K-2 |
| H16 | balance of the partial block for free (s1,s2) at r <= 2, controlled by the same determinant as H4 | R4, R5 | PROVED + toy exhaustive | on the real surface open (OQ-B-2) |
| H17 | Singer-cycle structure / F_{p^3} coordinates of M | all | OBSERVED (BPSW caveat) | OQ-M-1 |
| H18 | character invariants of the S layer (quadratic, quartic, 2-depth preserved) | S steps | PROVED | OQ-S-6 |
| H19 | backward walk: 3 roots per full round, 1 per partial; (T0,T1) free; plane-condition residual | all | OBSERVED | meeting structure OQ-B-3 |
| H20 | exact injectivity fingerprint (X1) and the R0 exact flatness q/(q+1) | all | PROVED + toys | n/a |
| H21 | exactly zero: stacked lane-0 equality after R3,R4,R5 | R3..R5 | PROVED + toys | n/a |

---

## 8. Errata, corrections and shaky spots

**Corrections to the atlas (found by the learners):**
1. Order of 5: mod 3 it is 2 and mod 463 it is 462 (atlas G1 said 3 and 463) (U7 s1, U8 s2; re-checked in section 9).
2. "Unfactored C (212 bit) and C' (225 bit)" were only a Pollard-rho limit: p-1 and p+1 factor at once; p^2+p+1 needed a longer ECM run; p^2+1 also factored (U5, U7, U8).
3. X4 "Jacobian rank 2 at every point" is false as an every-point statement: rank < 2 at exactly 2q-1 points after R0 (a = 0 or b = 0) on a toy and 205 at q=103, growing to 246 / 256 after R63; on the real field rank <= 1 on the lines nk = -c00, rho = -c01 at every level (U12 s7, U1 s7, U9 s7).
4. The atlas OBSERVED-on-few-inputs statements were upgraded in U12 s7; X6 "r >= 3 no trail" now has a proof and a second role for the determinant.
5. The atlas gauge for the Cauchy parameters (x0 = 0) differs from the raw Grain draws; same matrix (U6 s1, U5 s4, not an error).

**Errors in our own outputs (kept so nobody reads them as results):**
- U4 `u4_facts_output.txt` Q5 chi-square line is mis-binned; use `u4_q5_fix_output.txt`.
- U8 `exp1_output.txt` prints "Cauchy det formula ... False" because of a bad print line; `exp2_output.txt` has True. `exp2_output.txt` toy cubic lines print a wrong 'omega' label; `exp2b_output.txt` is the corrected run. `fact1_output.txt` ends with the 412-bit item and 5187662682403 listed as UNFACTORED only because the work list was not re-checked after the time cap.
- U10 `e2_mds.py` final section "X6 trail check" tested the wrong thing (superseded by `e9_trail.py`); `e1_output.txt` last line (lane-0 birthday) is a dict-overwrite artifact (superseded by `e10_output.txt`).
- U12 script label slip: `u12_real.py` prints "observability det[e0; e0M; e0M^2]" but its rows are e0M, e0M^2, e0M^3 (`0x1875f9a2...8bb5`, nonzero); the atlas value `0xebe164ab...a8ba` is confirmed (U12 s7, and re-computed in section 9).
- U11 `toy_u11.py` prints -1 in the chain column after the fifth level (int64 guard), not a result; R62 root-finding was not finished.
- U9 one concurrent run of the centre-axis script printed 0 zero coefficients at R63 only (forced to be 80%); two later runs with a value check gave 80.00% with MATCH: possibly a flaky large `fmpz_mod_poly` product in python-flint 0.9.0, unexplained. python-flint 0.9.0 `fmpz_mod_poly` multiplication segfaults for products above ~4-8 million 255-bit coefficients; the library now splits products into 2^20-coefficient blocks and every deep result carries a value check.
- U12: the exact-degree tracker silently turns a cancelled lane into zero and loses its lower terms: do not read post-cancellation lane degrees as true. First attempts at the finite-difference formula used 5^(8+r) for an AB-line (one power too high); corrected.
- Sampling with replacement inflates pair counts by duplicate inputs (U10 s5).

**Shaky spots (premises):**
- Primality of the large factors (79-, 143-, 186-, 334-, 484-bit) is BPSW only. The primitivity of M and every "p^3-1 fully factored" statement rest on it (U5 caveat).
- "Nothing found" statements: single wide LLL blind from 97 values; fibre statistics blind; toy exhaustion only to q ~ 1009-4099; a null at toy size says little about structures that need 2-adicity near 32.
- Implicit degrees 625 / 15625 for R2 / R3 and the irreducibility of the R3 level curve are DERIVED/GUESS only.
- Unit traps: nk vs AB degree (factor 5); inverse cost ratios 97 / 103 / 120 (multiplication count vs Python timing); "level" numbering for r = 1 vs 2.

---

## 9. Spot check done during this merge (OBSERVED, inline Python on `orchard\impl\poseidon_ref.py` and the pinned constants, nothing saved)

- p-1 = 2^32 * 3 * 463 * 539204044132271846773 * 8999194758858563409123804352480028797519453: True. The seven factors of p^2+p+1 listed by U5 / U8 multiply to p^2+p+1: True.
- 5^2 = 1 mod 3 and ord(5) mod 463 = 462: True.
- 2-depth of M12 = 8 and M11 = 3: True. X = 2^65 + c02 is divisible by 2, 3 and 5 and by 8: True.
- det[e0; e0M; e0M^2] = the 2x2 minor of rows (e0M, e0M^2) = `0xebe164ab9dff92f6f90c296e3b831a7221b9f7429d21e01d7dc2ebf46e8a8ba` (as claimed by U3, U12); (M u)_0 = 0 for u = (0, M02, -M01): True.
Not re-run: everything else (the cards' scripts and outputs are the evidence). Where two learners overlapped (factorisation: U5, U7, U8; trail: U3, U11, U12; supports: U2, U9; toy facts: U1, U10, U12) their numbers agree; the only conflicts found are the unit differences listed in section 8.

---

## 10. Which levels look least understood (ranked; evidence = empty squares in the section 2 matrix and the open lists)

1. **R61 and R62 (the middle of the tail).** Only degrees, exact line polynomials, lowest/top layers and one free-boundary run (R61). No zero-locus or critical-point census, no pair behaviour beyond toy agreement counts, no special-value study, no card of their own. Real double-zero counts here are infeasible by direct elimination so a method question sits on top of the missing data (OQ-T-2, OQ-T-1, OQ-T-6).
2. **The R3 -> R4 interface (the pair set with equal lane 0 after R3).** It is the hinge between the dense block and the partial block, and everything about it beyond "dimension 3, random-rate pair count, 1/q conditional rate" is DERIVED or GUESS: irreducibility and smoothness of the level curve, balance of the partial block on the actual surface (the exact analog of a past artifact), and the meeting-point structure (OQ-B-1..4).
3. **R5 (second partial round, r=2) as an object.** Everything on it is inherited from R4 by analogy plus the trail/balance facts; no zero-locus or Jacobian census, no special values, the R4&R5-without-R3 pairs unparametrised, the conjugation view G2 = Psi R5 Psi^-1 G1 only stated (OQ-P5-1..4).
4. **The real-field critical set beyond R3.** 11 rational rank-1 points through R3 are exact; R4..R62 counts are missing on the real field, single-zero-with-dependent-rows points are not counted, local type (fold/cusp) of the three R1 points is unknown (OQ-A1-1, OQ-P4-1, OQ-T-2).
5. **R2 and R3 as geometric objects.** Support and degrees are exact; the implicit-equation degrees, genus/rationality of the zero-locus curves, the full factor patterns of the R3 forms and whether the missing F_p root is luck are open (OQ-A2-1..3, OQ-A3-1..2).
6. **Tail <-> front geometry.** Where the 125 linear states, the "two t_j = 0" curves and the degree-drop curve (624) sit relative to the front surface; and what the tail does with the fixed-direction r=2 trail difference (OQ-T-4, OQ-W-1).
7. **Instruments, not levels:** we have no statistic other than exact identities and exact subset counts that sees structure in toys (fibre statistics are blind). Building and validating that instrument is a learning goal of its own (OQ-Y-1).

Best understood: init and R0 (relabelling, plane, K, drop directions, symmetry, controls), the object cards (M as a Singer cycle, constants from Grain, field factorisations, S-box differential spectrum), degrees and supports of the front block and R4/R5/R60, the end form at R63 and the output.

---

## 11. Proposed next learning round (round 2; no scores; toy or real stated; one question per agent)

General rules for the briefs (from the cards' lessons): one question per agent; named files and sections only; every result labelled OBSERVED with the command; **controls** that can fail (gcd(5,q-1)=5 toy; a toy with det[e0;e0M;e0M^2] = 0 such as q=23 seed 1; planted structure); value check against `poseidon_ref.py` for every deep real-field result; never a single wide LLL (use block covering); subtract duplicates when sampling; max 1 heavy process per agent with its own time limit; stop only your own PIDs; cheap models; GPU only where the job is a counting pass at q >= 12289 and a CUDA path already exists in the project (unverified here).

| job | level | question (learning) | toy / real | instrument and control | origin |
|---|---|---|---|---|---|
| J1 | R60, R61, R62 | Fill the same card U2 filled for R1..R3: read/write, zero locus of each S-box input (point counts ~q? Bezout degree), rank-1 point census by source (two zeros / one zero with dependent rows / inherited), difference weight transitions through the round | toy exhaustive q = 257, 769, 1009 (4099 if time); real: R60 single-lane zero-locus degree and one resultant if feasible | exhaustive counts; control: same census at R1..R3 reproduces U2/U9 numbers (3, 2, 6 real; 3 per toy) | OQ-T-2, probe (b), (c) empty squares |
| J2 | R3 -> R4 interface | Structure of the pair set {f(P) = f(Q)}: points of the level curve per P (distribution vs Poisson, components via Frobenius statistics), restricted to the trail direction; balance of lane 0 after R4, R5 on the R3 surface | toy exhaustive q = 257, 769, 1009 (restrict to R3-equal pairs); real: distinct-degree factorisation patterns of the degree-625 level polynomial over many (P, A') | control: balance for free (s1,s2) must reproduce U12 (exactly q); control: det=0 matrix toy | OQ-B-1, OQ-B-2, OQ-B-4 |
| J3 | agreement lattice (all levels) | For every subset S of levels {R0.M, R1..R4(, R5), R60..R63} count unordered input pairs with equal lane i (i = 0,1,2) at all levels in S; compare with the product-of-probabilities prediction; list every cell that is not random | toy exhaustive q = 257 and 769 (all subsets of 9-10 levels = 512-1024 subsets x 3 lanes) | control: known cells R3&R4 (trail relation), R3&R4&R5 (exactly 0), R0.M (q/(q+1)); this is the "grid dig" of the pair statistic | OQ-Y-1, T02, T09 |
| J4 | R5 | Card for R5 and the conjugation view: lane-0 zero locus and rank-1 census with r=2, algebraic degree/structure of Psi R5 Psi^-1, pairs equal at R4.M and R5.M without R3.M, overlap of the r=1 and r=2 front images in R60-entry space | toy exhaustive q = 103, 257 (and 23, 29, 37) | control: r=1 numbers from J1/J3 | OQ-P5-1..4 |
| J5 | tail <-> front geometry | Membership test for "is this R60-entry state on the front surface" (invert 1 + 3x3 roots and check the plane condition); test the 125 linear states, the pulled-back "two t_j = 0" curves and the degree-drop curve against the front surface; toy: count intersections exactly | real (cheap, ~25 roots per test) and toy exhaustive | control: states generated by the forward front must test positive | OQ-B-3, OQ-T-4, OQ-T-3 |
| J6 | tail activity table | Exact table of minimal active S-boxes / weight patterns for the four tail rounds for differences ending in M0 . dT = 0 (branch number 4); then verify cells against toys | pure arithmetic + toy q = 103/257 exhaustive | control: reproduce weight-1/2/3 counts of U11 s5 | OQ-T-1, T36 |
| J7 | critical set | Local type (fold/cusp) at the 3 R1 persistent points (series in (A,B)); count points of the fibre through (0,0) vs q; full critical-point catalogue per level on toys q = 257..1009 with the source of each point | real (local expansion) + toy exhaustive | control: U9's 32-50 / 36-44 / 36-43 toy counts | OQ-A1-1, OQ-A0-2, OQ-T-2 |
| J8 | interaction grid | All pairwise intersections of the structural sets: 9 S-box zero loci (R1..R3 or the toy's extra levels), critical set, trail pairs, drop-direction lines, centre axes, i-related pairs, 125 linear states; observed vs expected intersection counts | toy exhaustive q = 257, 769 | control: 0 of 30 pair points on a third curve (U2) and 3 two-zero points at R1 | OQ-X-1, T20, G08 |
| J9 | dense block geometry | Genus proxy (point counts vs q) of the R2 / R3 zero-locus curves; implicit degree of the R2 surface at q >= 1000 by the points-on-curve method; R3 factor patterns (distinct-degree factorisation, minutes per lane) | toy + real | control: R1 line (genus 0) and the q=257 degree-25 R1 equation | OQ-A2-1, OQ-A2-2, OQ-A3-1, OQ-A3-2 |
| J10 | free-boundary depth | Measure equal-lane-0 forcing by one root-find at R62, R63 and for r=2 (R5, R60): time against degree (625 -> 1.13 s, 3125 -> 13.6 s, 15625 -> 64.4 s so far), root-count distribution over 100 trials at R1, R2 (Poisson?) | real, one process, per-trial limit 20 minutes | control: R1..R4 reproduce U11 numbers; value check each root | OQ-T-6, U11 Q |
| J11 | arithmetic of F_p along a trace | Quadratic / quartic / octic characters and 2-depth of the S-box inputs along a trace vs later quantities; the subset {+-1,+-i}^3 under C+S+M; mu4 relations among constants | toy exhaustive q = 257, 769, 1009 (2-adicity 8, 8, 4) + real constants | control: gcd=5 toy; planted mu4 relation in a constants table | OQ-S-6, OQ-K-2, OQ-F-1 |
| J12 | recount the printed facts | Recount every fact in the organizer's profile JSON and TASK.md against our implementation | real, read-only | list of mismatches | OQ-I-1, T06, T07 |
| J13 | small arithmetic leftovers (low priority) | Shorter addition chain for d (below 291); certify the large primes with a proof-grade test if a tool is available; relations among Cauchy parameters, products and powers of constants by block-covering | real | control: planted relations | OQ-A0-1, OQ-F-3, OQ-K-1 |

**Suggested order.** Start J1, J2, J3 together (three levels the matrix shows thinnest; all exhaustive toys, each 1 heavy process); J12 and J6 in parallel as short cheap jobs; then J5 and J7 (use J1-J3 outputs); J4, J8, J9 next; J10 as a long single background process; J11 and J13 as filler. Do **not** spend the next round on more fibre-count statistics, more single wide LLL runs, or more r = 0..3 toy fibre scans: the cards show those instruments are blind or already random-rate.

**What each answer would change on the map (so the round is judged by learning, not by a number):** J1 / J4 / J7 fill the empty squares of section 2; J2 / J5 turn the interface hinge from GUESS to measured; J3 gives the first instrument other than identities that sees structure at level pairs; J8 tests whether any two handles of section 7 compose; J9 / J10 / J11 sharpen what is dense, what is cheap to force, and what the arithmetic of F_p keeps from level to level.

---

## 12. Round 2 (2026-10-12; learning, no scores) - results of J1, J2, J3, J6, J12

Source cards: J1/CARD.md, J2/CARD.md, J3/CARD.md, J6/CARD.md, J12/CARD.md (each in its own folder under levels\). Labels as in the cards. Jobs J4, J5, J7, J8, J9, J10, J11, J13 were not run in this round (their squares stay as in sections 2 and 11).

### 12.1 Per job: what was learned

**J1 (R60..R62 census; toy exhaustive q = 257, 769, 1009, seeds 1-3, r = 1, 2; 18 runs).** Validated: scalar permutation == `poseidon_ref.hash_reduced` (r = 1, 2, 5); control R1 = exactly 3 rank-1 points (one per lane pair) in all 18 runs. No real-field zero-locus degree or resultant was done (real degree 5^k stays DERIVED only).
- OBSERVED: each S-box-input zero locus at R2..R63 has about q points (ratio 0.98-1.01); no anomaly at R60-R62. Dull = random-curve rate.
- OBSERVED: two different-lane zero loci meet in about 1 point per pair per round (0.67-1.26); triple meetings never. About 3 new double-zero rank-1 points per full round, independent of q and degree.
- OBSERVED, CORRECTION to U9 "saturates": the rank-1 census is independent of q but grows linearly with rounds: about +3 double-zero and +3 single-zero-with-dependent-rows per full round, +1.2..1.7 single-zero per partial round. Totals for r = 1: 14.9 (R3), 22.8 (R60), 34.2 (R62), 39.1 (R63); r = 2: 23.1 / 28.9 / 35.0 / 41.0 at R60..R63.
- PROVED: no new rank-1 point without an S-box zero; partial rounds add no double zeros.
- OBSERVED: r = 1 vs r = 2 differ only by one R5 single-zero family (+1.2); R60..R63 per-round rates equal. R5 adds no further structure.
- OBSERVED: difference weight at R60 entry (4M pairs per run, equal lane 0) always 2 or 3, never 1; S preserves weight in 100% of pairs (PROVED); M transitions at random-matrix rates (3->1 about 3/q^2); trail pairs collide at the random rate (15585 vs 15564 expected at q = 257). Control random pairs give the same rates: no weight-reduction channel.

**J2 (R3 -> R4 interface; toy q = 257, 769, 1009 x 2 seeds; real field with python-flint; det = 0 control toys).** Real runs value-checked against `poseidon_ref.round_full` at 3 points.
- OBSERVED (real), the one surprise of the round: the degree-624 level polynomial (L3(x,rho0) - L3(P))/(x - nk0) is not random-looking. 3-16 irreducible factors (random controls 5, 6, 10, one big factor 494-569), about 2.4 degree-4 factors per polynomial (random about 0.25), recurring degrees 12, 20, 28, 60, largest factor 188-600 (mean about 350). Roots 0-3 (random-like). Reproduced at a second rho0. Cause not found; GUESS: small monodromy group (imprimitive, tied to the 5^4 composition). Only 2-3 random controls were completed and one rho0 pair: treat the strength as moderate.
- OBSERVED (toy): level-curve sizes mean q, var/q 0.94-1.07, no empty class; R3-equal pairs 1.000 x random. Count statistics are blind to the structure in the previous item. Do not spend more rounds on toy fibre counts.
- OBSERVED (toy): trail pairs inside the level curve are Poisson(1) and isolated (0.997-1.004 x random); R3&R4&R5 and R3..R6 exactly 0 in all 6 cases (random would be 128/384/504); R4&R5 without R3 at 0.989-1.000 of random (q = 257 slightly low, -1.6/-2.1 sigma, not at q >= 769).
- OBSERVED (toy): the free-(s1,s2) balance control reproduces exactly q for L4, L5; restricted to each level curve the number of distinct L4/L5/L6 values equals a random-function control (|z| <= 2.3 over 18 tests). The partial-block balance neither survives nor breaks on the R3 surface: no artifact, no gain (OQ-B-2 answered for the toy).
- OBSERVED (control that can fail): det[e0;e0M;e0M^2] = 0 toys (q = 23 seeds 3, 5; 29 seeds 18, 29; 37 seeds 8, 36) have R3&R4&R5 = R3&R4 exactly; det != 0 gives 0.

**J3 (agreement lattice; toy exhaustive q = 257 seeds 1, 2 and q = 769; r = 2; 10 levels x 3 lanes x 1023 subsets; control toys q = 23, 29, 37).**
- OBSERVED, reproduced in all three runs: lane-0 cells {R3,R4,R5} and {R2,R3,R4} are empty (expected 128.5 at q = 257, 384.5 at q = 769; z -11 / -20). The only reproducible non-random multi-level cells besides R0&R1.
- DERIVED (hand argument, not a formal proof): the R3&R4 trail fixes the R3 output difference direction (0, M02, -M01); equality at R2 then needs it to be an eigenvector of M[1:,1:], i.e. det[e0;e0M;e0M^2] = 0. Control passed in all 4 det = 0 toys (counts of {R3,R4}, {R2,R3,R4}, {R3,R4,R5}, {R2,R3,R4,R5} identical) and gave 0 as predicted in the 3 det != 0 toys: a sharp switch. J2 independently confirms the R3&R4&R5 half.
- OBSERVED: single-level equal-pair rate times q = 0.996 at R0 (q/(q+1)) and 1.000 elsewhere, all lanes, including R5 and R60..R63.
- OBSERVED: R0&R1 is the other non-random pair cell (ratio 0.90-1.16 at q = 257, 0.97-1.00 at q = 769; lane and sign change with the constants; shrinks with q). GUESS: R1 restricted to an R0 line is a degree-5 polynomial.
- OBSERVED, dull: the tail R60..R63 and R5-R60 pair cells show nothing; about 500 cells with E >= 1 per run gave a handful of |z| > 4 flags at q = 257 (for example R4&R5&R60 at +5.4), none reproduced in the other seed or at q = 769 (noise at the 500-cell trial level).
- Instrument status: the first non-identity instrument that sees structure in toys (it sees the determinant condition); it has power only for pairs, triples and a few quads (all 4+-level sets have E < 1).

**J6 (tail activity table; arithmetic + toy exhaustive q = 23, 29; q = 103/257 not run, pairs are q^6).**
- PROVED/DERIVED: support chain (s0..s3) possible exactly when |s_k| + |s_{k+1}| >= 4 across each M and |s3| >= 2. 337 of 2401 chains, 25 weight patterns. Fills OQ-T-1 / T36 and the G03 tail row with an exact table.
- DERIVED, matches toy: minimum 8 active S-boxes over the four tail rounds, reached only by weight patterns (2,2,2,2) [81 chains], (1,3,2,2) [27], (1,3,1,3) [9]. Chains by total active: 8:117, 9:144, 10:63, 11:12, 12:1. Cell dimension = 3 + |s0| - forced zero lanes - 1.
- OBSERVED: collisions in every cell at the random rate q^dim (ratio 0.98-1.04 on cells with > 10^4 hits; generic (3,3,3,3) 1.0000; totals 6,424,176 at q = 23 vs q^5 = 6,436,343; 20,486,760 at q = 29 vs 20,511,149). The tail adds no collision bias beyond support combinatorics.
- OBSERVED: chains ending in weight 1 occur but never collide (0 of about 1.9M). 336/337 feasible chains collide at q = 29 (and at q = 23, a different chain missing); the chain with zero hits at q = 23 had 18 at q = 29 (thin curve, GUESS: no structural exclusion).
- Not done: real-field table is counting only (DERIVED); no front-to-tail compatibility (which s0 the front can produce; belongs to J5/J1).

**J12 (recount of printed facts; real, read-only, one process; no yukon).**
- OBSERVED: organizer verifier digest == our `hash_reduced` on 342/342 random inputs (r = 0..56) plus edge inputs; rejects x = p, 63/65-byte messages, bytearray; r = 1 schedule [0,1,2,3,4,60..63] identical; 11/11 public vectors pass.
- OBSERVED: 0 functional mismatches. One cosmetic printed error: every one of the 57 profiles says `"full_rounds": 56` (the real full-round count is 8; 56 is the partial count), ignored by the verifier. `digest_bits` says 256 while the output is one element below p (255 bits); the 127 exponent is correct (log2(p)/2 = 127.0).
- DERIVED: cost normaliser exact: 27 per full round, 21 per partial, C(r) = 216 + 21r, C(1) = 237; dense MDS and 3 multiplications per x^5 charged, so no discount to exploit. Cost model v1 and v2 differ only by id/version and the added algebraic-estimates block (omega 2.8, no default coefficient, base-2 logs).
- OBSERVED: the 57 profiles differ only in id, rounds, round_selection; text matches rounds in all 57; modulus equals p; implicit conditions: 2^65 = 2 * 2^64 < p, gcd(5, p-1) = 1, p mod 5 = 2, 2-adicity of p-1 is 32, MDS determinant nonzero.
- Empty: live benchmark admission list (the copy we hold has an empty list), judge prompts. Another participant's PR data (pr923_data) uses a different definition of "rounds" (total prefix, 64 full); do not mix with the organizer target.

### 12.2 Coverage squares now filled (update to section 2)

| level | probe | was | now |
|---|---|---|---|
| R60, R61, R62 | (b) zero loci / critical | T only (R60), - (R61, R62) | T filled by J1: point counts about q, pair meetings about 1, census by source (dull, random-curve rate). Real still empty. |
| R60..R63 | (c) pairs / differences | p | T filled by J1 (weights 2-3, random transitions) and J6 (exact support table, activity floor 8, collisions at q^dim). Real: table is DERIVED. |
| R5 | (b) zero loci / critical | - | T filled by J1: one single-zero family, +1.2 points, no double zeros (PROVED). (e) special/symmetry still empty. |
| R5 | (c) pairs | RT | J2/J3: R4&R5 without R3 at random rate (q >= 769); R3&R4&R5 empty = det effect. |
| R3 -> R4 interface | all | DERIVED/GUESS | T: Poisson(1) trail pairs, random balance on the surface, det switch. R: level polynomial factors not random (first real measurement). |
| all levels | agreement lattice | not existing | T: filled for subsets of 10 levels at q = 257, 769 (lane-matched); mixed-lane cells empty. |
| all levels | (f) toy census by source | partial | T: rank-1 census by source per round (J1). |
| organizer facts | recount | - | J12: filled. |

Still empty (carried): real-field critical set beyond R3 (R4..R62 counts), real zero-locus degrees at R60+, local type of the 3 R1 points (J7), R61/R62 special values (probe e) and real pair behaviour, mixed-lane agreement cells, q > 1009 toys, J5 front-surface membership, J8 composition grid, J9 genus/implicit degree, J10 depth timing, J11 arithmetic characters.

### 12.3 New open questions

- OQ-R2-1 (J2): why does the real degree-624 level polynomial have many small factors (about 2.4 of degree 4, repeated 12, 20, 28, 60)? Next: is the pattern a function of rho0 only or also of nk0; more random controls (only 2-3 completed); are the degree-4 factors conics or cusps (roots in F_p^4); a toy analog at q about 13 with a full Galois-group computation. First real structural lead of the round.
- OQ-R2-2 (J3): the R0&R1 pair-cell deviation (0.90-1.16) and the triple R0&R1&R2 ratios (0.85-1.29, z up to 3-4 at q = 257) are unexplained; run at q = 1009 and 4099 to see the shrinkage and settle the GUESS.
- OQ-R2-3 (J3 -> J2): is det[e0;e0M;e0M^2] = 0 the only way to get R3&R4&R5 pairs? On the real field det != 0, so they are absent: formalise the proof (currently a hand argument).
- OQ-R2-4 (J1): the rank-1 census is linear in rounds (about 6 per full round); is the real-field rate the same? Real R4 and R60 counts remain infeasible by direct elimination (OQ-T-2 stays).
- OQ-R2-5 (J6): front-to-tail compatibility (which support s0 the front image can produce in the R60 entry space), and J6 at q = 103 by sampling instead of exhaustion.
- OQ-R2-6 (J12): cosmetic profile error `full_rounds: 56` goes in the batch of organizer notes (not a scoring fact).

### 12.4 Re-ranked: least-understood levels (replaces the section 10 order for planning)

1. **The R3 -> R4 interface (up from 2).** It holds the only real-field anomaly of the round (non-random factorisation of the level polynomial) that no toy statistic sees. Understand the monodromy structure (OQ-R2-1); L4 (degree 3125) is out of reach, so first the toy Galois analog.
2. **Real-field critical set beyond R3 (up from 4).** J1 shows the toy census grows linearly (about 40 by R63) but real counts at R4..R62 are still missing; local type of the R1 points (J7) untouched.
3. **R61 and R62 (down from 1).** Toy squares are now filled and dull (zero loci, pair meetings, weights, activity floor 8, collisions at random rate). Still no real-field data and no special-value probe, so not closed, but the toy lens is spent at q <= 1009.
4. **R2 and R3 as geometric objects.** Unchanged (J9 not run). The J2 factor pattern at R3 makes the J9 R3 factor patterns (distinct-degree factorisation per lane) a natural companion job.
5. **Tail <-> front geometry (J5).** Unchanged; J6 gives the tail-side table, the front side (which s0) is still missing.
6. **R5 (down from 3).** J1/J2/J3 show R5 adds one single-zero family, a random-rate pair set and the det-explained empty cell. Remaining: probe (e) special values and the conjugation view; J4 is now a short job.
7. **Instruments:** J3 is the first instrument beyond identities that sees structure (the determinant switch); its power stops at triples/quads at q <= 769. A real-field or larger-q version (counting pass at q >= 12289, GPU only if a CUDA path exists) is a learning goal of its own.

Best understood now (adds to section 10): organizer facts and cost normaliser (J12), tail support combinatorics (J6), the toy census by source per round (J1).

### 12.5 Suggested next order

J2 follow-up (OQ-R2-1: more rho0, nk0, random controls, toy Galois analog) first; J7 and J5 next (J1 gives the toy catalogue to compare); J9 with R3 factor patterns; J4 short; J10 as a long single process; J11/J13 filler. Not worth repeating: toy fibre counts, toy tail weights, toy R60-R62 zero loci at q <= 1009.
