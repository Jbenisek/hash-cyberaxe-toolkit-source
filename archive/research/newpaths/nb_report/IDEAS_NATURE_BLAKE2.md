# Ideas from BLAKE2 and from nature: what was tried and what is left

For the owner. Written 2026-10-08 by the report agent (folder `research\newpaths\nb_report`).
Research only: no yukon, nothing submitted or posted, trace untouched, no credential file opened.

Labels: COMPUTED = a program measured it. DERIVED = follows by algebra or counting from stated facts.
GUESS = judgement, not checked. Each line names the folder that holds the proof.

Sources summarised here (all under `research\newpaths\`):
- `blake2\BLAKE2.md`: the BLAKE2 agent.
- `nature\NATURE.md`: the nature agent.
- `sidepaths\SIDEPATHS.md`: the side-path agent.
- `nb_verify_nature_0`, `nb_verify_nature_1`, `nb_verify_sidepaths_0`, `nb_verify_sidepaths_1`: two skeptics per
  claim that had a cost number.
- `scout_recent\SCOUT_RECENT.md` and `scout_cross\SCOUT_CROSS.md`: two scouts. They are not mine, but they hold the
  one live lead, and it came from a BLAKE2 idea.

How to read the cost column: log2 of the total work in contest units (1 unit = one 2-round compression). Lower is
better. 128 is plain birthday search. The board is at about 93.0. Our filed entry claims 92.53. "-" means no
attack
comes out of it at all.

## 1. The short answer to your two questions

**BLAKE2.**
- Nothing published on BLAKE2, BLAKE, BLAKE3 or ChaCha gives a 2-round collision with the real starting
  values. Every published collision-style result needs a chosen starting state, or it is only a
  distinguisher, a key recovery or a preimage. (DERIVED, about 21 papers, URLs in `blake2\BLAKE2.md` section 5.)
- The one trick that does carry over is Li and Xu (2009): cancel a difference in the starting state with message
  words in round 0. That trick is our 55/63 path, using the block-length word. (DERIVED)
- One BLAKE2 feature did turn into something new: the **block counter**, which BLAKE2 also keeps in state words 12
  and 13. Through BLAKE3's chunk tree we can set that counter to a different value on every trial, at no cost. That
  gives the search one extra free 32-bit word. It is the only lead from today that could be worth more than a
  fraction of a bit. The main session is still checking it (section 3, item 1).

**Biology.**
- About 25 tricks from cells and nature were turned into real algorithms and measured. Examples: DNA repair,
  neutral evolution, codon synonyms, enzymes, immune selection, protein folding, gene networks, slime moulds,
  base pairing and tandem repeats.
- None of them beats plain search. (COMPUTED)
- The reason was measured, not assumed. Nature's shortcuts need one of three things:
  - slack: many small changes do nothing;
  - a smooth landscape: a small change makes a small difference;
  - free synonyms: many inputs give the same result.
- After 2 rounds, BLAKE3 has none of the three. One flipped message bit changes about half of the output bits.
  0 of 2^27 single-bit changes kept the target half the same. The landscape correlation is 0.001 +- 0.001.
  (COMPUTED, toy at 8 and 32 bits)
- The tricks nature uses that DO work here are already inside our path:
  - The length cancellation is like allostery: a far-away site switches the active site.
  - The class of Y4 is like a receptor that recognises a whole family of shapes.
  - Rule A followed by the E1 test is kinetic proofreading: a cheap check first, an expensive one second.
  - Seven trials packed in one 256-bit word is pooled testing.
- The live lead is "epigenetics": a mark that sits outside the DNA and changes how a gene is read without
  changing the gene. Here the mark is the chunk counter. It sits outside the message block, yet it changes how the
  block is processed. (DERIVED, analogy only)

## 2. One line per idea

Tag = status of the measurement. Verdict: dead / small (under 0.2 bit) / known (already in the path) / open.

### 2a. From BLAKE2 and the BLAKE literature

| # | Idea | Where it came from | What it means here | What the test showed | Verdict | Cost | Tag |
|---|---|---|---|---|---|---|---|
| B1 | Carry-free (linear) difference trails, round 0 solved for free | Su et al. 2010, Rumba 2008, Guo et al. 2014 (BLAKE2 analysis) | Find a message difference that survives 2 rounds | Best trail at 32 bits costs 2^-821 even with round 0 free. The generic cost is 2^-128. The trails look like random codes. | dead | 527 or worse | COMPUTED (`blake2`) |
| B2 | Sparse "all-ones" differences (the 88888888 family) | Guo-Matusiewicz 2009, Dunkelman-Khovratovich 2011 | Complement m3, m10 and m14 | Best structured trail found: 2^-527. Still 2^-155 even if every round-1 column were free. | dead | 527 | COMPUTED (`blake2`) |
| B3 | Probability-one paths (MSB local collisions, the Salsa20 core invariant) | Aumasson et al. 2010, Hernandez-Castro et al. 2008 | A difference that passes for sure | None exist, for a full collision or for either half, at 8, 12, 16 or 32 bits | dead | - | COMPUTED (`blake2`) |
| B4 | Starting-state difference cancelled in round 0 | Li-Xu 2009 | This IS our 55/63 path. Its skeleton is forced; only the length pair and the pins are choices. | Proved by inverting G: half B can never be free, and half A is free only with the pinned C3 pattern | known | 92.53 (filed) | DERIVED (`blake2`, `sidepaths` S10) |
| B5 | Flags difference: a 1-block message against a 2-chunk root (flags 11 vs 12) | Li-Xu applied to BLAKE3's tree | A second free-half path | Round 0 collides, but round 1 sends differences into both halves in 100% of samples | dead | above 128 (GUESS) | COMPUTED on toys (`blake2`) |
| B6 | Counter or chaining-value DIFFERENCE between the two messages | BLAKE2 counter/flags, free-start attacks | Two messages at different tree positions | Needs a generic 2^128 step | dead | 128 | DERIVED (`blake2`, `sidepaths` S5) |
| B7 | Rotational, rotational-XOR, "squeeze", fixed points | Guo et al. 2014, Ashur-Liu 2016 | Symmetric pairs of states | All need a symmetric or chosen starting state. BLAKE3's is neither. | dead | - | DERIVED (`blake2`, `fringe`, `shape_odd`) |
| B8 | Boomerang, impossible differential, differential-linear, neutral bits (PNB) | Biryukov et al. 2011, Hao 2014, Beierle et al. 2020 | - | These are distinguishers or key recovery. A collision needs all 256 bits, not one biased bit. | dead | - | DERIVED (`blake2`) |
| B9 | Higher-order meet-in-the-middle; near-collisions by hill climbing | Espitau et al. 2015, Turan-Uyan 2010 | - | The first is a preimage method and needs a split that does not exist. The second needs a chosen IV and only gives near-collisions. | dead | - | DERIVED (`blake2`) |
| B10 | Salt, personalisation or key words as freedom | BLAKE2 parameter block | Extra input words | BLAKE3 has no salt. Keyed mode is out of scope for this track. | dead | - | DERIVED (`sidepaths` S4) |
| B11 | Signed-difference search with automatic bit conditions | Hao-Wang-Jiao-Gong 2023 (ePrint 2023/299) | A better E1/E3 cancellation on our path | Not run; it needs a solver build | open | refines 92.5 only | GUESS |
| B12 | **The block counter as a free knob, set per trial** | BLAKE2 counter t in v12/v13, plus BLAKE3's chunk tree (`scout_recent`) | Collide the LAST chunk of a long message instead of the root. Its counter t is the chunk index, and we may solve for it on every trial. | Checked at 32 bits (2000 cases each, 0 mismatches) and on the organizer's verifier (360/360). It adds a 9th free word. Then a second residual-side word (E1.d1 or E3.h1) can be prescribed next to Y4; at counter 0 that is proved impossible. | **open, the lead** | scout's GUESS 83-88 | COMPUTED (mechanism) + GUESS (value) |

### 2b. From biology and nature

| # | Idea | Where it came from | What it means here | What the test showed | Verdict | Cost | Tag |
|---|---|---|---|---|---|---|---|
| N1 | Neutral networks and DNA repair | Reidys-Stadler-Schuster 1997 | Walk between messages that keep half the digest fixed | 0 of 2^27 bit flips and 0 of 2^24 word changes are neutral. Repairs work only at the random rate. | dead | 192 | COMPUTED (`nature`) |
| N2 | Evolution of robustness | van Nimwegen et al. 1999 | Breed messages whose output barely moves | Hill climbing did no better than the best of 3000 random messages | dead | - | COMPUTED (`nature`) |
| N3 | Codon synonyms (many codes, one amino acid) | genetic code | Pick targets where one inner value fits many messages | Synonyms exist (up to 256), but 0 of 70,650 survive in the real function: every message word is also read in round 0 | dead | - | COMPUTED (`nature`) |
| N4 | Enzymes and catalysts (free precomputed tables) | chemistry | Memory is free, so use big tables | Tables lower the cost per trial, never the number of trials. The one useful join (idea 1) does not exist. | dead | 93.9 even if the join existed | DERIVED (`nature`) |
| N5 | Immune clonal selection | de Castro-Von Zuben 2002 | Breed message pairs towards a half collision | Worse than birthday: 236,598 against 82,137 evaluations | dead | 128 | COMPUTED (`nature`) |
| N6 | Protein folding and annealing | Weinberger 1990 | Slide downhill to a target | No downhill exists (correlation 0.001). Annealing is no better than random. | dead | 128 | COMPUTED (`nature`) |
| N7 | Gene networks and attractors | Kauffman 1969, Flajolet-Odlyzko 1990 | Iterate the hash and look for short cycles | A random map within 1.2 sd at 2 rounds. The same test sees 5.7x more collisions at 1 round, so it works. | dead | 128 | COMPUTED (`nature`) |
| N8 | Slime mould and ant colonies | Nakagaki et al. 2000 | Find the best solving order | The best order is already proved exactly (4 checks) | dead | - | DERIVED (`nature`) |
| N9 | DNA double strand: palindromes that cancel in the output fold | base pairing | Equal differences on mirrored words cancel | A real effect: 2^-21 per G call at 32 bits. The full trail still costs 2^-314 or worse. | dead | 314 or worse | COMPUTED (`nature`) |
| N10 | Tandem repeats: differences that repeat every 8 bits | follow-up of N9 | Rotations 16, 12, 8 keep such patterns | Trail weight falls as the period grows (713, 586, 314 for periods 1, 2, 4). Period 8 is unsettled: the solver timed out. | open, long shot | unknown | COMPUTED + GUESS |
| N11 | Ribosome slip (read the message one round late) | frameshift | A message that round 0 leaves unchanged | It exists, but there is only one per length: no family | dead | - | COMPUTED (`nature`) |
| N12 | Kinetic proofreading (cheap check, then expensive check) | Hopfield 1974 | Early-abort stages | Already in the path. Both skeptics refuted the claimed 90.8: it needs discount 1 and a charge of 1.00 per trial, and staging alone cannot get below 1.094. The one step left is to split stage 2 at the c1 test (END_OF_LINE item 2). | small | 92.38 (gain 0.15) | COMPUTED (skeptics) |
| N13 | Immune cross-reactivity (recognise a class) | own | Hold fewer words, accept a fuzzy target | Still 4 checks per member | dead | 192 | DERIVED (`nature`) |
| S1 | Retrosynthesis (build back from the product) | chemistry | Make a second residual word free next to Y4 | Impossible with the counter at 0 (exhaustive search, 0 bases). B12 shows it IS possible with the counter free. | dead at counter 0, see B12 | - | COMPUTED (`sidepaths`, `scout_recent`) |
| S2 | Alternative splicing (one gene, several readings) | virology | One pinned C3 serving 3 block lengths | 160 of 160 triples UNSAT in z3. A pin exists for a length pair exactly when the XOR of the lengths is even. | dead | - | COMPUTED (`sidepaths`) |
| S2b | Two length pairs on one base | variant of S2 | 2 pairs per trial | 14 of 14 UNSAT | dead | - | COMPUTED (`sidepaths`) |
| S3 | Antibody affinity maturation | immunology | Hill climb on the 128-bit leftover | One bit flip changes 63.5 of 128 leftover bits on average. There is no gradient. | dead | - | COMPUTED (`sidepaths`) |
| S6, S7 | Sparse pins; equal-length pairs that touch only E1/E3 | G algebra | - | Impossible by algebra | dead | - | DERIVED (`sidepaths`) |
| S8 | Gene duplication: a 2-block message with a chosen chaining value | free-start analogy | Pick a good CV with 2^85 preprocessing | Both skeptics: the rate does not depend on the CV (300 pairs over 12 CVs, then 2^24 members per CV). Gain 0, not 0.12. | dead | 92.53 (92.54 if the 2^85 is spent) | COMPUTED (skeptics) |
| S9 | Pooled testing: bitslice 256 trials per 256-bit word | many ribosomes on one mRNA | Cheaper stage A | Both skeptics built it and checked every lane (0 errors). The gain is real but small, 0.02-0.15 bit. The upper end needs code specialised to each context, or computed jumps, and gathered stage-2 lanes. The "0.46-0.69 bit redesign" was refuted. halfsearch.py is already 63,712 of 65,536 bytes. | small | 92.37-92.50 | COMPUTED (skeptics) |
| S10 | Is our structure the only free half in one block? | proof by inversion | - | Yes, for differences in one block | closing fact | - | DERIVED + z3 (`sidepaths`) |
| S11 | Crossing over between two members | genetics | Swap w8..w11 | Y4 leaves its class (2^-13) | dead | - | DERIVED (`sidepaths`) |
| S12 | Ant trails: spend more trials in rich contexts | stigmergy | Prefer good outer steps | SIDEPATHS says at most 0.12 bit and dead. One skeptic argues a bounded outer-step filter could take the full +8.4%, about 0.116 bit. That is untested. | open, small | about 92.41 (GUESS) | DERIVED + GUESS |

### 2c. New lines added by this report (not tested beyond what is stated)

| # | Idea | What it means here | Result | Verdict | Cost | Tag |
|---|---|---|---|---|---|---|
| R1 | Which "marks outside the DNA" can be set for free on each trial? | All state words that are not message | Counter low word t_lo: free, 32 bits. Counter high word t_hi: only 19 bits, because messages must stay under 2^64 bits; scout: a 2^-13 filter, not a free word. Block length: already used. Flags: fixed by message shape. Chaining value: costs one compression per value, far too dear per trial. | t_lo is the only free one | - | DERIVED |
| R2 | Idea 1 (hold half the digest constant, birthday on the rest) plus the free counter | Does one more free word rescue idea 1? | One extra unknown with no new equation can remove at most one check (short argument). So there are 3 or more checks, and direct cost is 64 + 32x3 = 160 or more. A split would be needed, and none exists. | dead unless a split appears | 160 or more | DERIVED (sketch) |
| R3 | The prefix chunks P ("junk DNA", horizontal gene transfer) | Use the content of the earlier chunks as freedom | Every chunk starts from the fixed key words, not from the previous chunk. P only sets the counter t. | dead | - | DERIVED |
| R4 | Selective breeding: pick the parents, don't screen the children | With E1.d1 prescribed, enumerate only the richest c1 values instead of testing random ones | The c1 cheap test already shows the mass is concentrated. 105/16384 of E1's c1 values pass: a skeptic re-counted that exactly over 2^32 (`nb_verify_nature_0`). Per the proof's exact count, those values keep 99.997% of the counted rate; that count was not rerun. E1.d1 fixes c1 because Y11 is pinned. With c1 chosen directly, trials outside that set are never made. Value not counted. | open, part of B12 | not counted | COMPUTED (the c1 fact) + GUESS (gain) |
| R5 | A practical risk of B12 | The colliding messages are t chunks long | t must take all 2^32 values to be a free word, so a typical collision has about 2^31 chunks: about 2 TiB. If t is limited to small values, it becomes a filter, not a free word. Hashing the final pair costs about 2^31 compressions: nothing next to 2^85, but heavy for a Python verifier. | risk to check | - | DERIVED |

## 3. The live ones: next concrete test and who runs it

Only item 1 can move more than about 0.2 bit. Everything else is fine-tuning of the existing path.

1. **Chunk counter as a free word (B12, R4, R5).** The scout's value guess is 83-88. From the block study's own
   figures, a 905x class forced for free on the old non-cluster design gives 96.95 - 9.82 = 87.1. (DERIVED from
   `research\h8\block\BLOCK_REPORT.md`. Whether it stacks with clusters is not known.)
   - Main session: finish the check that is already running (HANDOFF 13:40). Build one counted trial on the
     counter arrangement, with Y4 per outer step and E1.d1 as the inner word, and count it on the program's own
     machine.
     Two things to settle there:
     - A random 32-bit counter lowers the X2 co-pass from 0.2585 to about 0.244 in the filed trial model
       (`scout_cross` 1c, COMPUTED). That costs cluster yield, which must be counted.
     - Decide on the 2 TiB message risk (R5) against the judge and the intake limits.
   - GPT Sol (pure maths): the exact rate under model M with c1 (equivalently E1.d1) prescribed. Give the
     enrichment of the best c1 value and of the best sets of 2^k values. Say whether that gain multiplies with the
     Y4 class, sub-class C15 and rule A, or overlaps them. This is the number the whole lead rests on.
   - The 3090: a toy end-to-end run at 12 or 16 bits, using a toy pin that has the half-collision property.
     Compare collisions per trial with c1 prescribed against random c1. Only this run checks that the gain is
     real and not an artefact of model M.
   - Grok on CPU: rerun the exhaustive minimum-guess search (`variants\gdx`) for idea 1 with the counter as an
     extra unknown. It confirms or breaks R2. It should be a short run (GUESS).
2. **Split stage 2 at the c1 test (N12).** +0.15 bit, 92.38. Main session. It needs the 12-unit test replayed on
   the program's counting machine (END_OF_LINE item 2). (COMPUTED by both skeptics)
3. **Outer-step filter for the +8.4% effect (S12).** About +0.116 bit, about 92.41. Main session or Grok: check
   that the cluster yield H4, the gate rates and rule A hold on the selected outer steps. Note the judge's earlier
   fatal finding on unbounded selection (F2-unbounded-nonuniform-selection). The filter must be a bounded,
   counted algorithm. (DERIVED + GUESS, `nb_verify_sidepaths_1\SKEPTIC_S8.md`)
4. **Bitsliced stage A (S9).** 0.02-0.15 bit (92.37-92.50). Low priority. The program file has only about 1.8 KB of room under
   the 64 KiB intake limit. (COMPUTED by both skeptics)
5. **Period-8 tandem repeats (N10).** Grok on CPU: a longer cryptominisat run (hours, one process) or a MILP
   model, using `nature\pksat.py`. It matters only if the round-1 weight drops below about 90 AND round 0 can be
   solved. Low chance. (GUESS)
6. **Signed-difference search (B11).** Grok on CPU, aimed at the counter arrangement. It is a refinement, not a
   new path. (GUESS)

## 4. Corrections between agents (read before citing them)

- **"Counter paths are dead"** (`blake2` B6, `sidepaths` S5): true for a counter DIFFERENCE between the two
  messages. It is not true for a counter value SHARED by both and solved per trial: that is B12. (DERIVED)
  `scout_cross` 1b/1c found a fixed counter constant neutral or slightly harmful. That is also consistent: a
  constant only relabels messages; the gain comes from solving for t per trial. (DERIVED)
- **S1 "no second free residual word"** holds at counter 0 only. With the counter free, bases exist
  (`scout_recent` 1.3). (COMPUTED by the scout)
- **N12 "90.8"** is wrong. It needs discount 1, which END_OF_LINE says not to take. The realistic figure is
  92.38. "At most 0.77 bit" uses the old charge 1.71; at the filed 1.65 it is 0.72, and the true staging floor is
  1.094 per trial-equivalent, worth at most 0.59 bit. (COMPUTED, skeptics)
- **S8 "up to 0.12 bit"** is 0. The +8.4% is an outer-word effect, not a chaining-value effect. (COMPUTED,
  skeptics)
- **S9 "0.46-0.69 bit with a redesign"** is refuted. Neighbour lanes differ in X2 and come from scattered
  clusters, so bitslicing them costs more than the present packed lanes. (DERIVED, skeptics)
- `research\grok\work\job16_entry\h8_ref.py` does not run: its `arrangement.txt` holds 82 bytes. Use
  `sidepaths\fam55.py` (self-tested 200/200 against the organizer verifier) instead. (COMPUTED, `sidepaths`)

## 5. Blocked, incidents and not verified

Blocked:
- `blake2` agent: a foreground wait (Start-Sleep 100) was refused by the harness. They waited with background
  loops instead and did not retry the sleep.
- The claude.ai Gmail, Google Calendar, Google Drive and Wix connectors need authorization in your claude.ai
  connector settings. None of this work needed them.
- This report: nothing was blocked.

One incident: the skeptic in `nb_verify_sidepaths_1` imported `halfsearch` and so created
`research\pkg10\pkg\blake3-r2\experiments\__pycache__`, outside its folder. It removed that within minutes and
reports that halfsearch.py and manifest.json are unchanged. I did not re-check those hashes. (reported, not
verified by me)

Not verified anywhere yet:
- The value of the counter lead (B12): the 905x figure, how it stacks with clusters, and a counted trial. All are
  GUESS until items 1a-1c of section 3 are done.
- The 12-unit c1 test has never been replayed on the program's counting machine.
- Period-8 and period-16 trail minima: the solver timed out.
- The linear trail weights were never checked against real carry arithmetic, because nothing was cheap enough to
  sample. The 32-bit ISD search did not converge, so its numbers are upper bounds.
- The organizers judged our 92.53 entry (64c075ac) not_evaluable because H4 to H6 have no organizer
  experiment. Any number above that builds on H1 to H6 shares that problem. (read from HANDOFF)
- I re-ran no experiments for this report. Every number above is copied from the named folder. Section 2c and the
  87.1 in section 3 are my own arithmetic on those numbers.
