Yes. The best use of multiple models here is **not** asking all of them “find better attack.” They’ll converge on the same obvious ideas. The better setup is to give each agent a different wrong-looking lens and force it to produce a falsifiable test.

Current grounded facts to anchor this:

The best established route still only forces **four digest words** and has not proved a fifth/sixth pin or a new score below the `2^63.6` benchmark. SOLCLOUD_14_REPORT The current hole is not “lack of concentration”; the split notes say the E3 side is about `2^-54.59`, E1 about `2^-40.15`, joint about `2^-100.53`, and what is missing is **decoupling**, not raw concentration. SOLCLOUD_14_INPUT_SPLIT_HOLE The prior exact work also warns that local weights and pretty trails are not attack exponents. cloud_40s_characteristic_answer

So the weird ideas should be aimed at **decoupling, legality, or a new coordinate system**, not just another filter.

## Agent swarm I would run

### 1. “Sacrifice one pin” agent

**Daydream:** What if the four forced digest words are a trap? Give one back.

The current path protects words `0,2,5,7` and fights the other four. A model should test routes where one of the “free” constructed equalities is deliberately allowed to move, if that creates an independent product family or cheaper E1/E3 split.

**Why it might matter:** Losing one digest pin costs up to 32 bits, but a real product/birthday split can save much more than that. If sacrificing one pin lets E1 and E3 be generated independently, the trade could still win.

**Test:** For each subset of forced pins of size 3 instead of 4, rebuild the dependency/peeling graph and ask:

```text
Does E1 get at least one free word that does not move E3?
Does E3 get at least one free word that does not move E1?
Is the remaining key interface smaller than 128 bits?
```

**Kill condition:** If every three-pin relaxation still has all useful free words coupled, drop it.

**Potential payoff:** High. This is the first non-normie thing I’d try.

---

### 2. “Coset spiral” agent

**Daydream:** The pure period-4/8 spiral failed because it demanded the whole difference be periodic. Maybe the useful object is:

```text
nonperiodic carrier + periodic correction
```

The last test killed exact period-4/8 as the whole route. It did not kill a periodic **component** inside a larger affine family.

**Test:** Take real surviving states from the current construction. Compute the local Boolean Jacobian:

```text
free message bits → solved checks
free message bits → remaining residual checks
```

Search for vectors:

```text
u in kernel(solved checks)
u has period-4/8 projection
u moves residual checks predictably
```

Then test whether second-order carry repair preserves it.

**Kill condition:** No nonzero periodic/coset component survives inside the solved-check kernel across many real states.

**Potential payoff:** Medium to high. This is the correct follow-up to the spiral failure.

---

### 3. “Digest fold, not state merge” agent

**Daydream:** Stop merging internal state. Target only the final `v[i] XOR v[i+8]`.

A lot of routes try to make G outputs or column states equal. That may be too strong. BLAKE3’s digest fold only requires XOR equality pairs, not full state equality.

**Test:** Build a solver that removes all internal merge requirements and encodes only:

```text
folded digest word i equal
```

plus legal message constraints.

Ask it for any route with five or six digest folds equal, even if no intermediate call fully merges.

**Why this matters:** The D4 report itself warns that constructed boundary conditions do not automatically imply actual digest pins, and it leaves global digest-pin improvement open. SOLCLOUD_14_REPORT

**Kill condition:** If digest-only solving still collapses to the same four pins under exact arithmetic.

**Potential payoff:** Very high if it works. This is one of the few ways to skip the current wall.

---

### 4. “Length-pair heretic” agent

**Daydream:** 55/63 may be locally best but globally wrong.

The carry-aware report says 55/63 uniquely gets a one-bit local first-G saving, but other near-63 length choices preserve more common message bits; whether those common bits compensate later is explicitly open. cloud_40s_characteristic_answer

**Test:** Rebuild the entire route for:

```text
47/63
31/63
maybe 59/63, 61/63, 56/64, 60/64
```

Do not rank by first-G local score. Rank by whole-route score:

```text
pins preserved
residual entropy
available zero-padding/common bytes
number of independent movers
cost to construct legal messages
```

**Kill condition:** If every alternative loses more later than it gains in preserved common bits.

**Potential payoff:** Medium. Very plausible 1–5 bits, less likely a 20-bit jump.

---

### 5. “Legal tree abuse” agent

**Daydream:** Parent nodes look illegal because their words are child CVs, not raw message words. But reduced-round BLAKE3 may make child CVs cheap enough to shape.

The reports correctly warn not to treat parent words as freely chosen raw bytes. Parent words must be realized as actual child chaining values, with cost charged. SOLCLOUD_14_REPORT

But maybe the child-CV image is large enough to give useful structured parent words cheaply.

**Test:** For parent-root or root/parent mixed forms, generate child CV populations and measure whether they hit the required word patterns faster than random. Do not assume arbitrary parent words.

Search for:

```text
child CV image ∩ useful parent-pattern family
```

**Kill condition:** If child CV acquisition costs more than the bits saved.

**Potential payoff:** High but risky. This is a “maybe new construction,” not an optimization.

---

### 6. “Carry trail first” agent

**Daydream:** Choose the carry pattern first, then solve message words around it.

Most search starts from words, then sees what carries happen. Flip it:

```text
desired carry skeleton
→ compatible additions
→ message constraints
→ legal words
```

For ARX hashes, carries are the real hidden state. Periodic XOR patterns may fail, but signed/carry patterns can still work.

**Test:** Use signed differences `{−1,0,+1}` and exact carry DP. Search for small carry skeletons that make the residual equations collapse. Reject anything that cannot be completed to legal message words.

**Why:** Prior work already says unrestricted signed characteristics and 32-bit full-collision search remain open, even after many local exclusions. cloud_40s_characteristic_answer

**Kill condition:** If every low-cost carry skeleton either fails legality or reintroduces the same four residual words.

**Potential payoff:** High. This is one of the most serious “different lens” agents.

---

### 7. “Invariant hunter” agent

**Daydream:** There may be a conserved quantity through a G call that isn’t obvious in normal variables.

The Job 14 report already gives a complete G invariant for one interface: `(B,C,T,K)` determines the output. SOLCLOUD_14_REPORT

Have an agent search for more invariants across **two G calls plus message reuse**, not one call.

**Test:** Use algebraic normal forms or SAT-based equivalence to search for low-degree invariants:

```text
linear XOR invariants
addition-XOR cube invariants
modular sum invariants
rotated parity invariants
```

Focus on invariants that connect E1 and E3 or reduce the residual interface.

**Kill condition:** Only trivial known invariants appear.

**Potential payoff:** Medium to high. This is “apple on head” territory.

---

### 8. “Class as error-correcting code” agent

**Daydream:** The Y4 class is not just a filter; it may be a codebook.

The current class gives strong concentration, but the open problem is whether that structure can be used constructively rather than just filtered. The split note says the 27.5-bit concentration is already present; missing piece is decoupling. SOLCLOUD_14_INPUT_SPLIT_HOLE

**Test:** Enumerate all `2^19` class members and compute residual signatures. Run Walsh/Hadamard or rank/correlation tests:

```text
Y4 class bits → tau
Y4 class bits → eps
Y4 class bits → beta support
Y4 class bits → residual words
```

Look for affine subspaces or cosets with unusually concentrated residual keys.

**Kill condition:** No exploitable subspace bigger than the current class filter.

**Potential payoff:** Medium. Could shave bits directly off 63.6.

---

### 9. “Interface minimizer” agent

**Daydream:** Don’t search for collisions; search for the smallest interface that must be shared between two independent lists.

Current work says the independent-list interface is too big or not constructed. But the exact minimum separator may not have been found.

**Test:** Build a bit-level dependency hypergraph from source words to:

```text
E1 inputs
E3 inputs
class constraints
legal padding
current pins
```

Then compute minimum separators under three models:

```text
word-level
bit-level ignoring carries
bit-level with carry-state nodes
```

Ask: “What is the smallest thing both sides must agree on?”

**Kill condition:** Separator remains ≥4 full words under all exact models.

**Potential payoff:** Very high if it finds a 1–2 word separator.

---

### 10. “Opposite direction” agent

**Daydream:** Start from a desired digest equality and invert backwards, instead of forward-building a path.

Because one full BLAKE3 round as a message-to-state map is invertible in the prior report, backward construction is not crazy. SOLCLOUD_JOB_14

**Test:** Pick five or six target digest equalities, choose free folded state variables satisfying them, invert round 1, then check whether the resulting round-0 messages obey legality/padding/reuse constraints.

This flips the current workflow:

```text
forward path → hope residual vanishes
```

into:

```text
desired fold → invert → test legal message reuse
```

**Kill condition:** Inverted messages violate padding/reuse with full-rank 128-bit obstruction.

**Potential payoff:** Very high, but likely hard.

---

## My top five to actually send out

1. **Sacrifice one pin to buy independence.**
2. **Digest-fold-only solver, no internal merge assumptions.**
3. **Carry-trail-first signed characteristic search.**
4. **Backward fold inversion.**
5. **Class-as-code Walsh/correlation search.**

Those are the most different from the “normal” path and most likely to find a surprise.

## Copy/paste prompt for external agents

```text
You are one specialized cryptanalysis research agent. Do not try to solve every route.

Target: complete-message BLAKE3 reduced to 2 rounds. Legal inputs only. Single-block root must have counter 0, fixed legal flags, valid padding. Nonroot/tree/parent routes must include legal child/root realization cost. Score is total work in 2-round-compression units; success probability ≥0.39.

Known state:
- Current front line around 2^63.6.
- Existing route forces digest words 0,2,5,7 and leaves words 1,3,4,6.
- E1/E3 residual split exists, but decoupling is missing.
- Word-level split and pure period-4/8 route failed.
- Local weights are not attack exponents; prove or measure real conditioned rate.

Your assigned lens:
[INSERT ONE LENS ONLY]

Deliver:
1. One concrete construction idea or impossibility result.
2. Exact variables and words involved.
3. What must be true for it to beat 63.6.
4. A minimal test that runs on reduced width first.
5. A 32-bit real-arithmetic check plan.
6. Cost accounting: setup, failed trials, successful trial verification.
7. Label every claim PROVED / DERIVED / GUESS / OPEN.
8. Do not claim a new score unless the success rate and charged cost are both established.
```

## Short version

The current agents should stop asking **“how do we make the existing residual cheaper?”**

Ask:

> “What assumption created this residual in the first place?”

The highest-upside weird moves are:

```text
give back one current pin
target digest fold directly
choose carries before words
invert backward from the fold
treat the class as a codebook
```

Those are meaningfully different from the normal search path.

## Tests of daydream.md ideas

Three of the ideas above were tested. All three are dead. Each paragraph gives the verdict, the finding, the bits, and the next step. Files are under `./research/fifties/daydream_file/<key>\` (each has a RESULT.md).

**1. Sacrifice one pin (`sacrifice_pin`): DEAD.** The literal move does not exist. Digest words 0, 2, 5 and 7 each come from one E0 output XOR one E2 output, and in the 55/63 Lemma L family a difference reaches E0 only through Y15 and E2 only through Y7, so the words cannot be given back one at a time (COMPUTED map, DERIVED proof). A G call with a difference in one state word never leaves 3 or 4 of its outputs equal (proved; exhaustive check at 4 and 5 bits). A one-sided difference makes the collision probability exactly 0. A two-sided difference creates a second 128-bit E0/E2 XOR cross key, and 2^16 real 32-bit trials per case kept 0 of the four words equal. Freeing the C3 pin constants while keeping Fact P (the generous reading) raises the least k from 2 (counter 1) and 1 (counter 2) to 4-6, with 0 check-free movers in all 21 relaxations. The reason: freeing r pins changes DOF by r - 2, but each side gains 2 interface words, and the coupling sits in C1 and D0, which C3 does not touch. Bits: independence saves 0; the net is above 63.6 (the brief's own model gives 95.6), and the E3-held design gets worse (k from 1 to at least 4, against split_e3's 84.6). Next step: drop this line, since daydream.md's kill condition is met. It reopens only with an attack outside the w4/w5 Lemma L family where message differences reach E0 or E2 separately (for example via w1, w9 or w11); that is untested and would break the round-0 cancellation.

**2. Class as a codebook (`class_codebook`): DEAD.** Under model M, the model that prices 63.6, the per-member E3 mass over all 2^19 members is exactly flat for the six front-line rows and for S as a whole (max/mean = 1, every Walsh coefficient 0), so no member subset has a different rate (COMPUTED, exact). The only codebook structure is in the ...60a0 rows, which the front line excludes. They sit on the cosets e1[21] = e1[26] (2x) and, with e1[2] = 0, 4x. The best class over all 14 outcomes gains 2^0.087, and taking those rows in would raise the filter pass share by about 5x the per-pass cost. The real member loop outside M (17,767 contexts x 2^19 members = 2^33.12 outer steps) measured E 2^-4.192 and P 2^-9.968. The large low-order |z| values (up to 120) are within-context clustering and flip sign between train and test. The one effect that replicates is the coset e1[26] != e1[27], which passes about 0.45% more often. Bits: 0.000 under M; at most +0.006 in the real loop; train-chosen coordinate cosets re-measured on test give +0.004 / -0.003 / -0.003 for codim 1 / 2 / 3. Next step: close the line. Only the deep part is untested: run the joint solver on about 10^7 real passes split by e1[26]^e1[27] and e1[2], e1[21], e1[22], e1[23], looking for root-count or solver-cost skew. M predicts none, and the cost share caps any gain near 0.2 bit.

**3. Length-pair heretic (`length_pairs`): DEAD.** No other length pair beats 55/63 or decouples E1 from E3. The cancellation is unique for every pair (w4' = ((K+w4) XOR x) - K, w5' = w5 + w4 - w4'); the lemma held in 800,000 tests with 0 failures, and all 2,080 pairs are enumerated and agree with the census on the 2,016 common pairs. Every pair pins on C3 with equal b and d outputs, so digest words 0, 2, 5, 7 are always forced and the residual is always E1 XOR E3. Freed padding words do not help: in four message formats (F55, F60, F61, F48) the exact least k is identical, and w14 never appears among the loop-word designs. Ranking by the counter-route numerator (GUESS where it carries other levers over): H8 at 55/63 and 56/64 scores 63.60, L16a at 48/64 about 65.5, L6c at 57/63 or 62/64 about 65.9, B at 60/62 about 67.0. Bits: every alternative pair costs +1.9 bits or more, and the front line stays 63.60. Next step: if more board lines are wanted, check whether the front line's pin-specific parts (best betas, cluster gate, filter automata, outcome set) carry over to L16a at 48/64 and L6c at 57/63 or 62/64 (the C figures rest on single best betas and could re-rank), and compare L6c with the filed delta-2 pin before any 62/64 refile. Stop spending effort on freed padding words.
