# NATURE.md - shortcuts from biology and nature, turned into algorithms and measured

Folder `research\newpaths\nature`, 2026-10-08. Research only: no yukon, no submission, no trace.
Tags: COMPUTED = measured here (commands in section 5); DERIVED = follows from a measurement or a stated fact by a
short argument; GUESS = not checked.

Toy used everywhere (identical to Grok job28; COMPUTED 15/15 test vectors at w = 8, 16, 32 agree with
`job28.compress`): word size w, rotations floor(r*w/32) of (16,12,8,7) - w=8: (4,3,2,1), w=12: (6,4,3,2),
w=16: (8,6,4,3) - IV = low w bits, v12 = v13 = 0, v14 = 2w, v15 = 11, BLAKE3 schedule.
"Half A" = out0,2,5,7 (depends on E0, E2 only); "strong fiber" = messages with E0's and E2's inputs fixed (idea 1);
"half B" = out1,3,4,6.

## 0. Bottom line

- Every analogy was turned into a concrete algorithm and measured on the toy against a plain baseline. **None beats
  random search or the known 4-check guess-and-determine core.** Projected costs at 32 bits are 2^128 or worse,
  except the "catalyst" (free tables), which is the known idea-1 join at about 2^94 and is blocked by the missing
  join (separable: join key 0). Details and numbers in sections 2 and 3.
- The reason is measured, not assumed: after two rounds the toy has **no neutrality, no smooth landscape and no
  steerable degeneracy** in value space (section 1). Those three properties are what every biological shortcut uses.
- **One real structure came out of the DNA-mirror test ("tandem repeats"):** BLAKE3's rotations 16, 12 and 8 are
  multiples of 4, so a difference word that repeats every 4 bits passes three of the four rotations unchanged, and
  any rotation keeps the period-4 subspace. A G call with an input difference only in d, of the form u = 0x88888888,
  returns the "palindromic" output difference (u, 0, u, 0) with probability **2^-20.98 measured at 32 bits** (2^-21
  predicted); palindromes cancel in the output fold. Pushed to a full characteristic: the best carry-free colliding
  characteristic inside the period-k subspace has round-1 weight **713 (k=1, = job29's all-ones trail), 586 (k=2),
  314 (k=4, all 2^32 checked)**; period 8 not settled (SAT timed out). All are far above 128: dead as an attack
  at k <= 4; a clean new data point for the differential line (idea 3).

## 1. The one fact every analogy runs into

Nature's shortcuts lean on one of three properties of the genotype-to-phenotype map:

1. **Neutrality** - many mutations leave the phenotype unchanged, so populations drift cheaply over huge neutral
   networks (RNA folding: a sizeable fraction of point mutations is neutral - GUESS from memory, not checked).
2. **Smoothness** - a small change makes a small phenotypic change, so selection, annealing and affinity
   maturation can climb.
3. **Modularity or degeneracy that can be reached for free** - parts that recombine (recombination, V(D)J), or
   many-to-one maps whose degenerate region costs nothing to enter (codon wobble, enzyme pockets).

Two-round BLAKE3 has none of the three in value space (COMPUTED, section 3):
- every message bit position changes on average 15.993-16.006 of the 32 half-A bits at w=8 (2^27 flips; ideal 16),
  31.7-32.4 of 64 at w=16 and 63.5-64.7 of 128 at w=32 (ideal 64); the distribution of changed bits is the
  binomial one (1 flip in 2^27 changed only 1 bit, binomial predicts 1.0);
- 0 neutral single-bit (2^27) and single-word (2^24) mutations at w=8; compensatory 2- and 3-word mutations
  restore half A exactly at the random-function rate;
- the fitness autocorrelation under one bit flip is 0.001 +- 0.001 at w=8 and w=32;
- pivot degeneracy is real (up to 256 roots, mean 169 siblings for A* = 0 at 32 bits) but lives in round 1 while
  every message word is also read in round 0, so a degenerate "synonym" never survives as a message (0 of 60,100
  siblings at w=8, 0 of 10,550 at w=16).

The single place where nature-like degeneracy exists in this problem is **difference space**: the leaders' class of
Y4 (2^19 members recognised by one E1 test) is exactly a cross-reactive receptor, and the period-4 "tandem repeat"
subspace found here is another such pocket. Both are differential structures.

## 2. Results table

| # | nature | algorithm here | toy measurement vs baseline | cost at 32 bits | status | verdict |
|---|---|---|---|---|---|---|
| 1 | neutral networks (Schuster, Reidys) | random walk on the half-A / strong fiber with mutation + repair | neutral fraction 0 / 2^27 bit flips, 0 / 2^24 word changes (random 0.031, 0.004); pair repair 0 / 7.1e7 (random 0.016); triple repair 2 / 9.4e9 (random 2.19); threshold lambda* = 0.5 (bits), 0.0215 (bytes) | each neutral step ~2^128 evaluations (= a fresh preimage); 2^64 members -> 2^192 | COMPUTED + DERIVED | dead |
| 2 | evolution of robustness (van Nimwegen) | hill-climb messages towards few-bit phenotype change (PNB-like) | best R: hill-climb 4 = best of 3000 random 4 (w=8); 7 = 7 (w=32) | no robust region exists to exploit | COMPUTED | dead |
| 3 | codon degeneracy | choose targets so pivots q+ROR(q^A)=T have many roots; count surviving message variants | E_T[roots] = 1 exactly; size-biased siblings 7.6 (random A), 169 (A=0) at w=32; survivors in the real system 0 / 60,100 (w=8), 0 / 10,550 (w=16) | buys 0 members | COMPUTED + DERIVED | dead |
| 4 | enzymes / catalysts | free tables (pivot root tables, whole-G tables, list joins) | covered by fringe angle 11 (still 4 checks) | kinetics not thermodynamics: c=4 join ~2^93.9-95.9 if a join existed (none: separable key 0) | DERIVED | dead |
| 5 | immune clonal selection (CLONALG) | affinity maturation of message pairs on half A at w=8 | without table: 0 / 8 runs of 2^26 evals (random pair search 2^32); with table: 236,598 evals mean vs birthday 82,137 (83,275 measured); output concentration 1.002 | >= 2^128 | COMPUTED | dead |
| 6 | protein folding / annealing | Metropolis annealing on message bits towards a half-A target | 16-bit target: SA 72,832 evals vs random 56,511 (theory 65,536); autocorrelation 0.001 +- 0.001 | >= 2^128 per 128-bit target | COMPUTED | dead |
| 7 | gene regulatory networks (Kauffman attractors) | iterated map x -> half digest(embed(x)) at w=8, exhaustive functional graph | 6 embeddings at 2 rounds: occupancy and pair count within 1.2 sd of a random map; the same test at 1 round sees 5.7 x the random collision probability | rho = birthday: 2^128 | COMPUTED | dead |
| 8 | slime mould / ant colony | path search over solving orders in the G dependency graph | exact optimum already known (4 checks, word and bit level) | no gain possible | DERIVED | dead |
| 9 | DNA double strand (mirror fold) | "palindromic" G differences dA=dC, dB=dD that cancel in out[i]^out[i+8] | random ports: 0.4-2.6 x random; d-port: 103 x random at w=12; d-palindrome 2^-20.98 at w=32 | full characteristic in the period-k subspace: W1 >= 314 (k <= 4) | COMPUTED | dead for k <= 4; k >= 8 see 3.9 |
| 10 | ribosome slippage / frameshift (own) | slide: the unique m* with round0(v_init, m*) = v_init | exists and verified; 2-round(m*) = 1-round(PERM m*) | one message, no family | COMPUTED | dead |
| 11 | kinetic proofreading (own) | staged filters | already in the leaders' path (stage A/B, rule A) | <= 0.77 bit (END_OF_LINE 3.1) | DERIVED | known |
| 12 | cross-reactivity / partial recognition (own) | hold fewer E0/E2 inputs, accept a k-bit half-A entropy | fringe: every half-A variant needs 4 checks, including outhalfA | 2^(64+k/2) members x 2^128 each | DERIVED | dead |

## 3. Each analogy in detail

### 3.1 Neutral networks and repair (DNA proofreading)

Mapping. Genotype = message; phenotype = half A (weak fiber) or the 12 E0/E2 input words (strong fiber). A neutral
mutation keeps the phenotype; "repair" = re-choose k other words to restore it (compensatory mutation).

Measured (w=8, COMPUTED, `nature neutral`, `pairs`, `triples`):
- single-bit flips: 0 neutral in 2^27 (random-map expectation 0.031); single-word changes: 0 in 2^24 (0.0039);
  strong fiber 0 in both;
- every 2-word repair (all 120 word pairs x all 65,535 alternative values, 9 bases, 7.1e7 messages): 0 restore
  half A (random 0.016), 0 restore the strong fiber;
- every 3-word repair (all 560 triples x 2^24 values, one base, 9.4e9 messages): 2 restore half A (triples
  {3,5,11} and {6,8,13}; random expectation 2.19), 0 restore the strong fiber (random 5e-10).

So the neutral network is the random-map one. Reidys-Stadler-Schuster: a neutral network percolates only when the
neutral fraction lambda exceeds lambda* = 1 - a^(-1/(a-1)) (a = alphabet size): 0.5 for bit mutations, 0.0215 for
byte mutations, 5.2e-9 for 32-bit word mutations. Ours is about 2^-32 (w=8, half A) and 2^-128 (w=32): far below,
so the network is a dust of isolated points (DERIVED). A step needs a repair set of at least 4 words and about
2^(4w) trials - the cost of a fresh preimage - so a walk costs 2^128 per member and 2^192 for 2^64 members (DERIVED).
The strong fiber's size is 2^(4w) on average (dimension count; consistent with fringe's gdnum, 18 members found
against 16 expected at w=6), but it is not connected under any cheap move.

Population dynamics (van Nimwegen-Crutchfield-Huynen): populations concentrate on the most connected genotypes.
Hill-climbing for robustness R(m) = number of single-bit mutants that change at most 8 of 32 half-A bits (w=8) or 48
of 128 (w=32): random messages mean R 0.439 and 1.528 (binomial predictions 0.45 and about 1.5); 3000-step
hill-climb reaches 4 and 7, equal to the best of 3000 random messages. No heritable robustness (COMPUTED).

### 3.2 Codon degeneracy

Mapping. Sol's pivots: fixing a column's outputs (A, C) leaves q + ROR8(q ^ A) = T (T = C - c); fixing (B, D) leaves
ROR12(b ^ r) ^ (r + D) = ROL7(B). Many roots = synonymous codons: several message pairs for one internal value.

Exact facts. For every A, sum_T n_A(T) = 2^w, so the mean number of roots over T is exactly 1 (DERIVED; COMPUTED
0.989 +- 0.02 at w=32). Degeneracy moves mass; it never adds it.

Measured (COMPUTED, `pivot_ac`, `pivot_bd`):

| w | (a,c) max roots | P(no root) | size-biased siblings (random A) | A = 0 | (b,d) max roots |
|---|---|---|---|---|---|
| 8 | 4 (bound 2^2) | 0.33 | 1.80 | 2.98 | 4 (bound 2^3) |
| 16 | 16 (bound 2^4) | 0.51 | 2.87 | 11.0 | 7 (sampled; bound 2^6) |
| 32 | 256 (Sol's A=0, T=ffffffff) | 0.75 | 7.6 | 169 (also A = ffffffff, 80000000) | not sampled |

"Size-biased" = the number of roots of the T that a random member actually has, i.e. its synonyms. At A* = 0 the map
q -> q + ROR8(q) is close to a circulant with a kernel of alternating bytes (u, -u, u, -u), so its image has only
about 2^24.6 values (DERIVED from 169; Sol's 256-root example is the extreme).

The decisive test (COMPUTED, `variants`): take a real message, solve each round-1 column's pivot for all alternative
message pairs, substitute them into the message and recompute. With X held fixed the siblings reproduce the column
outputs (353/353 at w=8, 552/552 at w=16). In the real function: **0 survivors** in the strong fiber out of 60,100
siblings (w=8, 20,000 bases, about 3 per base) and 10,550 siblings (w=16, 2,000 bases; up to 13 siblings at one column). Reason
(DERIVED): every message word is read in round 0 as well, and round 0 is a bijection message -> X, so any sibling
changes X and all column inputs. Choosing degenerate targets at several columns at once multiplies relaxed siblings
(at most 2^8 x 2^12 x 2^8 x 2^12 = 2^40 per X at 32 bits) and still buys nothing in the real system.

The one exact synonym in this problem is fringe's sum absorption G(a+t, b, c, d, x-t, y) = G(a, ..., y): it enlarges
the family (plusA, 6 free words) but keeps 4 checks (fringe angle 1).

### 3.3 Enzymes and catalysts (free tables)

Mapping. A catalyst lowers the barrier of one step without changing the equilibrium. Here: a table turns a solving
step into a lookup (pivot root tables: 2^64 entries, 2^72 operations of preprocessing, negligible; whole-G tables:
fringe angle 11; list joins: literature section 4). DERIVED: tables change the cost per trial (kinetics), not the
number of trials or the 4 residual checks (thermodynamics). For idea 1 with c = 4 checks a two-list join would cost
2^93.9-95.9 (`derive.py`, literature formula), and no join exists (separable: key 0). An asymmetric join with one list
paid as 2^85 preprocessing needs the other at 2^107: worse. For the leaders' path cost per trial is 1.65-1.71 against
a floor of 1: at most 0.77 bit. Verdict: dead as a new path; already used where it helps.

### 3.4 Immune system: clonal selection and affinity maturation

Algorithm (`clonalg`, w=8, CLONALG of de Castro-Von Zuben): population of 50 message pairs, affinity = number of equal
half-A bits, the 10 best cloned in proportion to rank, hypermutation 1 + 12 exp(-3 aff/32) bit flips, 5 random new
pairs per generation (receptor editing). Target: a half-A collision (32 bits).
- Pure affinity maturation: 0 of 8 runs found the collision in 2^26 evaluations each (best affinity 29/32); a
  random pair search needs 2^32 per success.
- With the free-memory table (every evaluated half A stored): 20/20 found, mean 236,598 evaluations against the
  birthday 82,137 (uniform reference measured 83,275 over 100 runs). It is a birthday on its distinct messages
  (about two thirds of its evaluations repeat a message).
- Concentration of its outputs: half-A repeats among distinct messages 60,734 against 60,595 uniform (ratio 1.002).
Verdict (COMPUTED): worse than the birthday, no output concentration. Affinity maturation needs a correlated
landscape (3.5), which is absent.

Cross-reactivity (own, DERIVED): recognise a class instead of a value - hold fewer E0/E2 inputs and accept k bits of
half-A entropy. The birthday then needs 2^(64+k/2) members, and fringe's greedy GD shows every half-A variant
(including outhalfA, which holds only the 4 output words) still needs 4 checks, so each member costs the same.
Dead. (The leaders' Y4 class is the working form of cross-reactivity, in difference space.)

### 3.5 Protein folding: energy landscape and annealing

Landscape (Weinberger's autocorrelation; `autocorr`): energy f(m) = Hamming distance of half A to a random target.
corr(f(m), f(m with d random bit flips)): w=8: 0.0011 (d=1), 0.0084 (d=2), -0.0012 (d=4), 0.0013 (d=16); w=32:
0.0009 (d=1), 0.0015 (d=2); standard error 0.001. The d=2 excess is the 1/128 (w=8) and 1/512 (w=32) chance that
the two random flips hit the same bit and cancel (0.0078, 0.0020); corrected, all values are 0 within error. An
uncorrelated landscape means annealing is a random search (No Free Lunch, Wolpert-Macready).
Annealing (`anneal`, 100 runs, Metropolis, 4000-step sweeps with restarts, 1-2 bit moves): 16-bit target in
72,832 evaluations on average, random sampling 56,511 (theory 65,536). Verdict: dead (COMPUTED). The ARX "carry
landscape" version (fix the carries, solve linearly, check) is the XOR-linear trail search: see 3.9 and job29.

### 3.6 Slime mould and ant colonies

Mapping. Physarum / ant-colony optimisation are heuristics for shortest paths in a graph; here the graph is the
dependency graph of the 16 G calls and the "path" is a solving order. That optimisation has been solved exactly:
word level 8 guesses = 4 checks for the fixed family (gd_order / gd_sat, Sol X, fringe EXACT), bit level 256 guessed
bits = 128 check bits (main session's `bit_gd.py`, `bit_prune_fixed.txt`). A heuristic cannot beat a proved optimum.
Dropped without a run (DERIVED).

### 3.7 Gene regulatory networks: attractors of an iterated map

Algorithm (`funcgraph`, w=8): f(x) = half digest of the message with x (32 bits) placed in 4 words, the rest fixed;
f maps 32 bits to 32 bits; all 2^32 points evaluated; image fraction and pair count sum n(n-1)/N compared with a
random-map control (Flajolet-Odlyzko: 1 - 1/e = 0.6321206, pair count 1). Rho walks from 100-300 random starts as the
attractor statistic. A cheaper collision of any iterated map needs a lower collision entropy of H restricted to the
embedding (DERIVED); the image fraction measures it to about 1e-5.

COMPUTED (`fg8.c`; the first rows also with the slower generic `nature funcgraph`). Domain 2^32: a self-map,
image fraction against 0.6321206 (sd about 4.8e-6) and pair ratio against 1 (sd about 3e-5). Domain 2^30: occupied
bins of 2^32 against the exact random expectation (sd about 1.0e-5 relative) and pair ratio (sd 8.6e-5).

| embedding of x (rest of message) | half | rounds | domain | occupancy vs random | pairs / expected |
|---|---|---|---|---|---|
| random-map control (splitmix) | - | - | 2^32 | 0.6321176 (-0.6 sd) | 1.000025 |
| random-map control (splitmix) | - | - | 2^30 | 0.9999887 (-1.1 sd) | 1.000096 |
| m0..m3 (rest zero) | A | 2 | 2^32 | 0.6321147 (-1.2 sd) | 1.000029 |
| m5, m8, m12, m15 = E1/E3-only words (rest random) | A | 2 | 2^32 | 0.6321179 (-0.6 sd) | 0.999989 |
| top 2 bits of all 16 words (rest random) | A | 2 | 2^30 | 1.0000095 (+1.0 sd) | 0.999900 |
| m12..m15 (rest random) | B | 2 | 2^30 | 0.9999927 (-0.7 sd) | 1.000043 |
| m1, m9, m11, m14 = E0/E2 message words (rest zero) | A | 2 | 2^30 | 1.0000009 (+0.1 sd) | 0.999994 |
| **sensitivity check: m0..m3, one round only** | A | **1** | 2^30 | **0.6305527 (-37,000 sd)** | **5.717522** |

The test is sharp: after one round it sees a collision probability 5.7 times the random one (a birthday on that
1-round half would be 2.4 times cheaper). After two rounds every embedding is a random map to within 1.2 sd: no
attractor structure, no degeneracy, the iterated map costs the birthday bound (DERIVED: 2^64 for one 128-bit half,
2^128 for the digest).

Rho lengths from random starts are dominated by the giant component of one map (the control gives mean cycle 30,156
and tail 91,026 against the across-maps averages 41,069 each), so they are reported but carry little weight; the
image fraction and pair count are the precise tests.

### 3.8 Kinetic proofreading, slippage and the mirror

- Kinetic proofreading (Hopfield 1974): staged discrimination multiplies specificity per stage. That is the leaders'
  stage A / stage 2 with rule A. Cost factor only, at most 0.77 bit left (END_OF_LINE 3.1). DERIVED.
- Ribosome slippage / frameshift (own): a message read "one round late". Round 0 is a bijection, so exactly one m*
  satisfies round0(v_init, m*) = v_init; then 2-round(m*) = 1-round(PERM(m*)). COMPUTED (`slide.py`, `slide.out`):
  for block length 64, m* = f18e6f3b 03b36a40 5b13ce48 79ac165c 1f434a9b ff044d48 804339e9 6023e684 464c6cba 06277727
  6ae5892a a0d9a941 ff10325c 1bdae340 d96a2b5b a03a31f6; both identities verified (also for lengths 55 and 0, where
  m* is not a valid short-message encoding). One message per length, not a family; dead.

### 3.9 DNA double strand: the fold as a mirror, and the tandem-repeat subspace

Mapping. out[i] = v[i] ^ v[i+8] pairs row a with row c and row b with row d, like base pairing. Half A cancels when
E2's output difference is E0's with a<->c and b<->d swapped; the simplest case is a "palindrome" dA = dC, dB = dD in
both calls with the same values.

Measured (`palin`, 2^28 random G inputs per row, rate against the random 2^-2w):

| difference in | w=8 | w=12 |
|---|---|---|
| x | 0.83 | 1.13 |
| y | 2.00 | 2.63 |
| x, y | 0.94 | 0.81 |
| a | 0.81 | 0.75 |
| b | 0.88 | 1.38 |
| c | 0.38 | 0 |
| d | 1.14 | **103** |
| all six | 0.98 | 1.19 |

The y row is the derived factor 2 (dA must be all-ones and r in {0, 2^(w-1)}). The d row at w=12 has a mechanism
(DERIVED, then COMPUTED): with a difference only in d, carry-free propagation gives the output (u, 0, u, 0) where
u = ROR_R0(delta), provided ROR_R1(u) = u, i.e. u repeats with period gcd(R1, w). For w = 32, R1 = 12, so period 4:
u = 0x88888888 (7 non-MSB bits) costs three carry-free additions, 2^-21. Measured (`dpal`): **2^-20.98 at w=32**
(130 in 2^28), 2^-24.68 for u = 0x11111111 (10 hits; predicted 2^-24), 2^-6.00 at w=12 (u = 0x888, predicted 2^-6),
2^-21.0 at w=16 (u = 0xaaaa, period 2). With u = 0x8888 at w=16 (wrong period) 0 hits, as predicted.

Why it matters: rotations 16, 12, 8 are multiples of 4 (only 7 is not), and every rotation maps a period-k word to a
period-k word for k | 32. So the XOR-linearised compression maps period-k message differences into period-k states:
a small invariant "tandem repeat" subspace (k=4: 4 coordinates per word). In it the four final diagonals can all be
palindromic: a state difference with only row d = (u,u,u,u) after the round-1 columns, and no difference in the
eight E message words, collides with probability 2^-84 from the final step alone (DERIVED from the measured 2^-21 per
call). The question is the cost of the whole characteristic.

Exhaustive answer for k <= 4 (`period4.py` + `p4enum.c`, every nonzero carry-free colliding characteristic in the
subspace, Lipmaa-Moriai weight of all 96 additions, COMPUTED):

| period k | kernel dim | characteristics | best total W | best round-1 W1 |
|---|---|---|---|---|
| 1 | 8 | 255 | 1333 (= job29's all-ones on m3, m10, m14) | 713 |
| 2 | 16 | 65,535 | 1051 | 586 |
| 4 | 32 | 4,294,967,295 | 742 | 314 |
| 8 | 64 | 2^64 (too many to list) | not settled | not settled (SAT timed out, below) |

Period 8 by SAT (`pksat.py`, cryptominisat5 with native XOR clauses, a sequential counter on the active round-1
OR-bits): the encoding was validated on period 4, where the bound-42 instance returned exactly the enumerated optimum
(W1 = 314, same message pattern, decoded and re-scored). Period 8 timed out at 80 active bits (240 s) and at 32
active bits (900 s, i.e. "W1 <= about 128?"). So the period-8 minimum is not established (COMPUTED: timeouts only).

Best period-4 message pattern (W1 = 314): nibble patterns 8 0 1 1 9 9 9 9 9 0 0 0 9 0 0 1 on m0..m15. Even with
round 0 entirely free by message modification, W1 = 314 > 128: dead as an attack for k <= 4. The weight falls as the
period grows (713, 586, 314), and the full space (k = 32) is the general trail search of idea 3 / job29, where no
colliding characteristic below 128 is known. This ladder is offered to that line as a structured family to search.

## 4. What is not established

- Period-8 and period-16 minima (section 3.9) are not settled (SAT timed out at 240 s and 900 s); the general
  trail question (k = 32) is not answered here. A MILP solver or a longer SAT run is the next step for whoever owns
  the differential line.
- The strong fiber's exact size at w=8 was not enumerated (dimension count and fringe's w=6 counts only).
- CLONALG and annealing were tuned by hand once; other settings were not swept. The landscape autocorrelation (zero)
  is the reason to expect no setting helps, not a proof.
- Belief / survey propagation on the bit-level fiber (statistical physics of SAT) was not run; fringe's CDCL runs
  (angle 7) found no member at w=6-8 in 300-399 s, and BP is usually weaker than CDCL on such structured instances
  (GUESS).
- The functional-graph test covers 6 two-round embeddings (plus a control and a one-round check); other embeddings
  were not tried.
- All toy results use the floor-scaled rotations; the period-k results are at the real w = 32 rotations.

## 5. Files and commands

All in this folder. Build and run in WSL (scripts cd here):
- `nature.c` - toy and all experiments (`selftest neutral pairs triples pivot_ac pivot_bd variants funcgraph clonalg
  birthday autocorr anneal palin robust dpal`); `build.sh` + `check_selftest.py` (cross-check with job28).
- `quick1.sh`, `quick2.sh`, `quick3.sh`, `quick4.sh`, `run_tri.sh`, `run_fg1.sh`, `run_fg2.sh` - the exact runs;
  outputs `quick1.out` ... `quick4.out`, `tri.out`, `fg1.out`, `fg2.out`.
- `fg8.c` + `run_fg8.sh` - fast functional-graph test (hugepage counter array, optional 2^30 domain); outputs
  `fg8_a.out`, `fg8_b.out` (2^32 runs), `fg8_c1.out` to `fg8_c3.out` (2^30 runs); `fg1.out` holds the first control.
  The generic `run_fg1.sh` / `run_fg2.sh` runs were too slow (killed by their 30-minute limit) and were replaced.
- `period4.py K` (Windows python + numpy) writes `pK_basis.txt`; `p4enum.c` enumerates (`quick4.out`); `pksat.py` +
  `pksolve.sh` SAT minimisation for larger K (cryptominisat5 XOR clauses), results `pksolve.out`, the decoded
  period-4 check in `pksat_decoded.txt` (instances deleted; regenerate with `python pksat.py K bound 1 file.cnf`).
- `slide.py` (frameshift fixed point), `derive.py` (thresholds, join costs, random-mapping constants).
- `pids.txt` - start/stop times of every background job (all mine, all finished).

## 6. Sources

- Reidys, Stadler, Schuster, Generic properties of combinatory maps: neutral networks of RNA secondary structures,
  Bull. Math. Biol. 59 (1997) 339-397. https://link.springer.com/doi/10.1007/BF02462007 ; threshold formula as
  restated in https://www.tbi.univie.ac.at/newpapers/Abstracts/95-07-058abs.html and https://arxiv.org/pdf/1508.03815
- van Nimwegen, Crutchfield, Huynen, Neutral evolution of mutational robustness, PNAS 96 (1999) 9716-9720.
  https://arxiv.org/abs/adap-org/9903006
- de Castro, Von Zuben, Learning and optimization using the clonal selection principle, IEEE TEC 6(3) (2002) 239-251.
  https://www.dca.fee.unicamp.br/~vonzuben/research/lnunes_dout/artigos/ieee_tec01.pdf
- Weinberger, Correlated and uncorrelated fitness landscapes and how to tell the difference, Biol. Cybern. 63 (1990).
  https://link.springer.com/doi/10.1007/BF00202749
- Wolpert, Macready, No free lunch theorems for optimization, IEEE TEC 1(1) (1997) 67-82.
  https://ieeexplore.ieee.org/document/585893
- Flajolet, Odlyzko, Random mapping statistics, EUROCRYPT '89, LNCS 434 (1990) 329-354.
  https://link.springer.com/doi/10.1007/3-540-46885-4_34
- Kauffman, Metabolic stability and epigenesis in randomly constructed genetic nets, J. Theor. Biol. 22 (1969)
  437-467. https://wikidp.org/Q28256189
- Hopfield, Kinetic proofreading, PNAS 71 (1974) 4135-4139. https://pmc.ncbi.nlm.nih.gov/articles/PMC434344
- Nakagaki, Yamada, Toth, Maze-solving by an amoeboid organism, Nature 407 (2000).
  https://ideas.repec.org/a/nat/nature/v407y2000i6803d10.1038_35035159.html ; Tero et al., Science 2010 (via the
  same search).
- Evolutionary search in cryptanalysis (works only on reduced primitives, e.g. one-round TEA, DES internals):
  https://arxiv.org/pdf/1006.5745 ; https://e-archivo.uc3m.es/entities/publication/e7b0aaaa-4505-4fe0-b49f-87fef8e41f55
- Lipmaa-Moriai addition weight, PNB (Aumasson et al. 2008) and the BLAKE literature: see
  `..\literature\LITERATURE.md`. Prior project results used: Grok job28, job29, job30; fringe `RESULTS.txt`;
  Sol W and X; `..\bit_prune_fixed.txt`.
