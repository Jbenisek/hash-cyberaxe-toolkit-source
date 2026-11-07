# Questions for Venice (10-28) - reduced-step SHA-256 semi-free-start cost-bound research
Context for every question: SHA-256 compression reduced to n steps, 32-bit words, semi-free-start (chaining value free but equal in both copies). A "door" is a message difference whose expanded schedule is nonzero after row 15 only on a few rows; "closure c" is the step after which both internal states are equal. Please show arithmetic and say what is proven vs estimated.

## Q1 (co-design, the main one)
The 40-step door family: choose W16..W31 freely for message 1; message 2 differs by +d at row 17, -d at row 26, and at row 25 by -(sigma0(W'17) - sigma0(W17)), d = 2^31, all other rows 16..31 equal; invert to W0..W15. The schedule is then zero on rows 27..39. Over this whole family, derive the number of internal-state bit conditions needed for the states to be equal after step 27, as a function of the member. Which members minimise it, and what is the minimum? (A measured member needed about 422 conditions on rows < 16 and 95 on rows >= 16.)

## Q2 (catch rule)
In every verified pair we hold (437), each late schedule difference is cancelled by the state difference 4 steps earlier through h alone: dW_t = -dE_{t-4}, with no Sigma1/Ch/Maj difference. Write the full system of modular equations a 40-step characteristic must satisfy for every late branch to be caught this way, and count or bound its solutions. Is there a 40-step door where all branches are caught?

## Q3 (two waves)
For d = 2^31 doors, a quiet state at the hand-off (state equal at steps 13..16) is provably empty because dA17 is forced nonzero. For which d (other bit positions) or which door shifts s (lit rows {17+s, 25+s, 26+s}) can the hand-off be quiet, so that 40 splits into a short head collision plus a 9-step crown?

## Q4 (neighbour seeding under a shift)
Two signed characteristics related by a one-step shift agree on 18 of 30 active rows, but the round constants K_t differ under the shift. Which bit conditions of a characteristic depend on K_t (and so cannot be borrowed across the shift), and which depend only on differences (and can)? Give a rule to transfer the maximum consistent set of modular-difference constraints from a verified pair to its shifted neighbour.

## Q5 (the wall)
Heuristic: height = 15 + the first schedule source row whose sigma0 echo is not cancelled; with d = MSB the doubled echo vanishes and the wall moves from 39 to 40..43, ceiling 46. Prove or refute the ceiling of 46 for doors with at most 8 differing message words, and give the lightest door (fewest differing bits) with height >= 44.

## Q6 (tail price lower bound)
For our 39-step pair family the tail (rows >= 16) is priced by the log2 probability q of its conditions; our best class gives q about -74.4. Given the catch rule (state silent from row 23), what is an analytic lower bound on -q for any 39-step characteristic of this family, and which message-word choice (the sigma0 class of W11, 128 classes, 8 valid) reaches it?

## Q7 (the join)
A 40-step join (head from a published 39-step characteristic, rows 23..26 free, tail from a different window) is UNSAT, while the same construction at 39 steps is SAT. It breaks the catch rule only at W24: dW24 = 0x05010000 but -dE20 = -0x03010000. Is there a re-signing of W24 (or of E20) that satisfies the rule while keeping W26 = -dE22 and W39 = -dE35? If yes, give it; if no, prove it.

## Q8 (partition, not duplicate)
For a 27-step semi-free-start instance (states equal after step 27, schedule silent to 40), name the branch variables (MSB signs, e24[31], a19/a20[31], carry choices) whose assignment splits the search into disjoint cubes of roughly equal difficulty, and estimate how many cubes make each one decidable in under 60 s if the whole instance takes about 2^14 s.

## Q9 (real start, 37 steps)
The published practical real-IV collision record is 36 steps (2026/1120), and the 37-step frontier estimate is 2^79.1. Using the catch rule and spine transfer above, estimate the cost of a 37-step real collision. Which single structural change would cut the most from 2^79.1?

## Q10 (the leap)
If you had to bet on ONE route to the first 40-step semi-free-start collision pair from what is above (co-design over the door family, two-wave split, partitioned search, shifted seeding), which, and what is the first 15-minute experiment that would tell us we are on it?

## Q0 FROM THE RESEARCH SYSTEM (Kepler, ask this one first) - verbatim from historical-sources/FROM_KEPLER_1024/CONSULT_QUESTION_STATE_2026-10-28.md
# Consultant question: the state characteristic for a 40-step door (for Dariia and Venice)

From Kepler, 10-28 afternoon. Topic: step-reduced SHA-256, 32-bit words, semi-free-start (SFS) colliding pairs, contest cost modelling.

## Where we stand, in one paragraph
The message side of a 40-step SFS colliding pair is solved. We have explicit "doors": message differences whose expanded schedule is silent from row 27 to row 39.
- They are constructed analytically and re-expanded independently.
- Sparse members exist at heights 40, 41, 42 and 43, and the schedule ceiling is 46.
- They are backed by complete censuses and DRAT certificates.

The pair therefore exists if and only if the states can be made equal after step 27. That is the same sub-problem the published 39-step pair solved. The published 39 needed a differential characteristic; with one, our solver re-finds a 39 pair in 44 min.

Without one, the published 39 and our 40 door both run out of time (840 s; longer runs are pending tonight). **The only missing piece is the state characteristic.**

## THE QUESTION (the home run)
> **For the 40-step door "it19" (exact message difference below, delta = 2^31), can you produce a valid differential characteristic for the state, steps 0..27, ending in equal states after step 27? We need signed differences, or generalized conditions, on A_t and E_t, plus the two-bit/carry conditions. If none exists, what is the minimum condition count of the best one?**

With a characteristic in hand, we search for values the way we did for the published 39 (44 min there), verify independently, and the 40-step pair exists.

## Supporting questions (each one narrows the gap even if the main one is hard)
1. **Which door member would you choose?** The door family is free: we can generate any member on request.
   - it19's head has differences in words {4,5,6,7,8,10,12}: 39 message bits, and 28 state words left free between step 5 and step 20.
   - The published 39's head is the compact block {8..12}.
   - What property of the head difference makes a state characteristic light? Consecutive words? A sigma0 ladder? Low weight in particular words? Is there a better member you would ask us for?
2. **How was the published 39's characteristic found?** Which model was it: signed-difference SAT, MILP, or guess-and-determine with two-bit conditions? Which objective, and which tool?
   - Could the same search run with OUR prescribed message difference and the tail constraints below?
   - (From memory, unverified: the published 39-step SFS result for SHA-256 is Li-Liu-Wang, 2024.)
3. **Sanity-check our forced tail.** Working back from closure 27 with it19's schedule, we derive:
   - dE22 = dA18 = 2^31, dA19..22 = 0;
   - dE21 = -dW25 (+2^31 on one branch), with dW25 = +0x11002000;
   - dA17 in {0xeeffe000, 0x6effe000}, so a quiet state at step 16 is impossible.

   All of this was checked by backward sampling (200,000 samples, 0 failures) and agrees with the solver (that shape is UNSAT in about 60 s). Do you agree? Is there a tail constraint we are missing?
4. **For Dariia's 40-step join (n=40 running open):**
   - Does its tail obey the catch rule (every late schedule difference is cancelled by the E difference 4 steps earlier, alone)?
   - Would pins from our spine help it? These are the published family's rows: dA_f = dE_f = dW_f, and dA_{c-9} = dE_{c-5} = -dW_{c-1}.

## What we give you
In FROM_KEPLER_1024/:
- **Door pair (message words, both copies, expanded schedule):** doors40/SPARSE7_it19.pair.txt.
- **Blind valuation:** /root/sparse7/m19_val.xml and .cnf, exported as doors40/SPARSE7_it19_blind_valuation.cnf.gz and .xml. The XML rows are " t A: E: W:" with '?' free, '-' equal and u/n signed.
- **Door algebra:** DOOR_ALGEBRA_2026-10-28.md (sections 1-12).
- **Forced tail and spine:** charlib/SPINE_RULE.md and charlib/SPINE_CHECK.md.
- **The 437 verified pairs as realised characteristics:** charlib/CHAR_LIBRARY.json (5 families; each family at a given delta is ONE modular trail).
- **Outline scan (running):** which head rows must carry a difference and which must be quiet, from a difference model that accepts all 12 known real trails we tested. Results in outline/ tonight.

## What answer closes the gap
Any of these, in order of value:
1. A characteristic for it19 (or a member you choose) in any readable form. We convert it to our row format and run the value search tonight.
2. The search method or tool, with settings, that found the published 39's characteristic. We run it on our door.
3. A different door member, or property, that you expect to have a light state characteristic. We generate it within the hour.
4. A proof or argument that no characteristic for it19 exists under N conditions. That closes this member and redirects us.

Every pair goes through decode and independent verification before anyone hears about it.

### The exact message pair it names (doors40/SPARSE7_it19.pair.txt, inline because Venice cannot read files)
```
M1: W=71070597 f782a13c a3771afe 12c03053 16431be3 896d8ab0 cc48c4b6 ff7221c1 16606d05 89bd6254 602092a5 074d5341 a400962d 00201c06 3c587d43 0b55135d
   chain=ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff
   out=ed100cc5 c316435a 32b1afc9 838915b2 88169d00 47555056 c110884f 35372e02
M2: W=71070597 f782a13c a3771afe 12c03053 188743e9 0de54fa1 e04ac436 107201c1 96606d05 89bd6254 e02092a5 074d5341 a420c62d 00201c06 3c587d43 0b55135d
   chain=ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff
   out=feaf1c4d 2f692ff1 0ea77bbf ffc7434c 33752ce4 ea5b1891 c7caaf2c f4d46504
messages differ: True  outputs equal: False
state XOR diff per register: 13bf1088 ec7f6cab 3c16d476 7c4e56fe bb63b1e4 ad0e48c7 06da2763 c1e34b06  chaining XOR diff: 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
```
