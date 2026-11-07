# ATLAS_BLAKE3 - step atlas for the 2-round BLAKE3 record (c994a61f, 57.1890)

2026-10-12. The BLAKE3 version of ATLAS37 (SHA-256 r37). It covers the record c994a61f (pkgB3U), which builds on 5f7e222e / 7c2264a8
(pkgB3T). Source of every definition: pkgB3U `proof.md` Sections 1-9 (construction, Lemma Q, Lemma F, 9.4 J1-J3, 9.10, 10.1 counts).
Scripts (pure Python, 1 thread, all our own, written from the printed definitions, no participant code run):
`research\tools\traillab\b3atlas\` (with mc_coupled.txt) = `rows_dp.py, solo.py, typed_check.py, gtype.py, gpairs.py, g13.py, ey.py, third.py, coupled.py, coupled2.py, validate.py`
(plus mc_coupled.txt).

## The question: does BLAKE3 have the SHA "rows" gap?

In SHA r37 the trail prints per-row signed-bit conditions ("cells"), but the attack only needs the final event. The gains came where the
cells were stricter than the event (rows 18/19: 8 values = 6 parities; rows 22+: exact event 2.465x the cells).

**For BLAKE3 the answer is mostly no, and the reason can be stated exactly.** The record has no characteristic layer. Its probabilistic
part (calls E1 and E3 of round 1, 128-bit residual R) is split into *outcomes* (beta, tau, eps) = the XOR differences of E1's b1, a2, c2.
Every input with R = 0 falls into exactly one outcome. Each outcome's probability is an exact whole-word count, L_j * N3_j, over all
carry patterns (Section 17 program), not a product of per-bit cells. So nothing inside one outcome is "stricter than the event", and
there is no "two carry patterns, same difference" slack left to collect.

The one place where the attack *is* stricter than the event is in **which outcomes it lists**. That is the BLAKE3 analogue of the
rows, and it is a deliberate choice. Counts are below; the extra outcomes are priced out.

The stage that the SHA lesson actually applies to is a cost stage, not a rate stage: the **omega list filter**. It is a projection with
free witnesses, and it is looser than the exact joint event. That looseness is candidate 1.

## Step atlas (16 G calls x 4 quarter-steps = 64 steps)

Codes: **I** = inverted/solved exactly by construction (no probability). **P** = pinned constant (advice). **0** = zero difference, proved.
**F** = forced by an earlier difference (exact XOR consequence). **$** = paid by probability (filter, cube, solver). **L** = listed subset of
an exact partition (stricter than the event, by choice). **Z** = closed door. Quarter-steps: q1 = (a1, d1), q2 = (c1, b1), q3 = (a2, d2), q4 = (c2, b2).

| call | q1 | q2 | q3 | q4 | notes |
|---|---|---|---|---|---|
| K0, K1, K3 | I | I | I | I | solved backwards (steps O, M); Lemma T2 bijection onto admissible blocks |
| K2 | I (length diff 55^63 = 8 enters a1) | I | I (w5' = w5 + w4 - w4' cancels it at a2) | I | Lemma L: exact cancellation, cost 0 |
| D0-D3 | I | I | I | I | solved backwards; X3, X7, X11, X15 forced to pinned constants |
| C0 | I | I | I | I | backwards from y = Y4 (member) |
| C1 | forward | forward | forward | forward | produces Y9 = Q; **$** condition (1)/J1 on Q (pass 14,110,208 / 2^32), Y9 prefilter PF exact |
| C2 | forward | forward | forward | forward | no difference; Y6, Y14 recomputed per root (certificate) |
| C3 | P | P | P | P | Fact P: w4 = W4 vs W4' gives equal b, d outputs; a, c differ by DY3, DY11 (pinned, advice) |
| E0, E2 | 0 | 0 | 0 | 0 | identical inputs, so digest words 0, 2, 5, 7 are equal. **Stricter than the event** (the event only needs o0, o2, o5, o7 XOR-equal across E0/E2), but relaxing activates two more calls: doors 22, 24 (**Z**) |
| E1 | 0 (a1, d1 equal) | **$** c1 in cube Q* / Q_2 fixes beta exactly (11 bits, x2^11 rate) | **L** tau = Delta a2: lists 285020a0 only; d2 = ROR(tau,8) F | F eps forced by beta (Lemma N: eps ^ ROL(beta ^ eps, 1) = eta; checked for all three listed betas); b2 F | 14 outcomes of beta*, 19 of beta2; listed: 1 each |
| E3 | e1: DY3 additive; class fixes eta (Lemma Q, 2^19 members exact); h1 = eta F | g1: theta (**$** J1, list on Q); f1: sigma F | e2: eps (**$** J2 = list on omega, typed); h2 F | g2: J3 tau (**$** solver root h); f2 F | all conditions are exact XOR consequences of R = 0 for the outcome |
| final XOR o[i] = Z[i] ^ Z[i+8] | | | | | already used: R is cross E1/E3 (Lemma N); the outcome partition is exact |

Where the probability is paid (per outer step): filter (1) on Y9 x typed (2) on omega -> pre-check (nu in {3,4}, lossless Lemma VP) ->
joint screen (SG, lossless Lemma SL) -> joint solver (G7/G15, lossless) -> certificate. Cost shares of N = 7.064e19 (ledger): WB 83.1%
(list words alone u_W x WORDS = 5.4e19, about 77%), selection 6.9%, solver credit 6.7%, context/member 2.8%, blocks 0.4%.
**So 83% of the cost is spent per typed omega list word.** Any lever that is lossless and shrinks the list is worth about
log2(0.17 + 0.83 c) bits for a list kept at fraction c.

## Exact counts made here (own DP over the printed definitions)

Controls reproduce the package exactly: (1) = 14,110,208; (2) union = 63,633,856; SHARE = 897,886,944,002,048; typed (2)
23,820,160 (t = 0) and 34,028,800 (t = 1), with typing f9 ^ f10 = 1 and f24 ^ f25 = 1 ^ t.

### A. The rows: listed vs unlisted outcomes (the analogue of "cells vs event")

Inside the trials it already pays for, the attack keeps 25,165,824 / 71,698,432 = **35.1%** of beta*'s R = 0 events and
12,582,912 / 54,005,760 = **23.3%** of beta2's (ceiling +1.74 bit if all were free). Rate per filter word, each outcome on its own:

| tau (eps 6e21be55) | part r_j | (1) words | (2) words | r_j / (2) |
|---|---:|---:|---:|---:|
| **285020a0 (listed)** | 25,165,824 | 14,110,208 | 47,608,704 | **0.529** |
| 385020a0 | 16,777,216 | 56,440,832 | 142,826,112 | 0.117 |
| 185020a0 | 16,777,216 | 56,440,832 | 190,434,816 | 0.088 |
| 175020a0 | 6,291,456 | 14,110,208 | 86,561,280 | 0.073 |
| 685020a0 | 1,572,864 | 27,998,208 | 47,608,704 | 0.033 |
| others (8) | <= 1,572,864 | | | <= 0.017 |
| beta2 285020a0 / 6e61be55 (listed) | 12,582,912 | 14,110,208 | 23,804,352 | 0.529 |

Adding any outcome to S: E_COUNT +37% (685020a0, rate +4.2%) to +590% (185060a0, +2.8%). Best rate gain 185020a0/385020a0 (+44%)
costs E +258% / +184% and SHARE x13.0 / x9.6. **Every addition loses at the current ledger** (83% of cost scales with E). This closes
the row question on the 57.189 ledger (door 4 and door 36 were on older ledgers). The listed tau is the one with a 4.5x tighter filter.
This is the reverse of SHA: in BLAKE3 the stricter-than-event choice is the optimum, not a leak.

### B. Same tau, other beta: the third-beta row 18b3e098 / 285020a0 / 6e23be55

Typed (2) union with this row added: **0 new words in both types** (23,820,160 / 34,028,800 unchanged). Its J1 + J3 g-language
(|G13| = 2^24.58) keeps the typing relations g4 ^ g5 = 1, g21 ^ g22 = 1 and g0 ^ g1 = 1, so typed lists stay lossless for it. This
settles the item left OPEN in tighten/b3_ctr_class_transfer.md row 2. Rate +262,144 / 37,748,736 = +0.694% (ceiling -0.0100 bit),
less the credit for a fourth solver row. LEVERS measured -0.00968 on fa97a08f.

### C. Why the typed list is exactly the decoupled projection

g = E3.g1 = Q + h. J1 alone forces only g17 = g18 and g19 = 1 ^ g17 (|G| = 2^30); these do not bind (2) (the y-typed count with G equals
the untyped 63,633,856). J1 and J3 with independent witnesses (G13, |G13| = 1.5 x 2^25) force
{g0 ^ g1 = 1, g4 ^ g5 = 1, g21 ^ g22 = 1, g16..g19 relations}. With f = ROR(y ^ g, 12), g in G13, the per-member exact count equals the
typed count **exactly** for every member tried (8 of 8). So the 1-bit type already extracts everything the decoupled event gives. What is
left is the **coupling**: J1 and J3 share h through h2 = ROR(h ^ e2, 8), e2 = omega + f.

### D. The coupled list (candidate 1)

The exact condition for an omega list word to be able to hold a listed good trial, for any Y9:
there exist g, h with J1(g, h), J2(omega, f = ROR(y ^ g, 12)) and J3(g, h2 = ROR(h ^ (omega + f), 8)), where Q = g - h is free.
Checker: DFS over g (J2 + G13 pruning, about 4,096 leaves), then a 32-step NFA over h2 with J1 run on h = ROL(h2, 8) ^ e2. It was
validated on a constructed true instance (exact = True). Monte Carlo over typed-passing omega words (7 members, seeds 5 and 11): **71 of 82 complete (0.866); 11 of 82 = 13.4% cannot hold a joint root for any Y9** (95% interval about 7-23%). Per member: 8/10, 10/12, 11/12, 12/12, 10/12, 9/12, 11/12. These words are removable without loss, but only if a list can be built at the coupled condition. The fraction may depend on the member phase (b, u, v) = e1 bits 2, 21, 26 (PHASE of 9.4 ties h bits to b, u); that has not been split yet. Caveats: a sample, not a count; one constructed positive control only; the DFS is our own reading of J1-J3 (proof.md 9.4); the cost of building per-phase or per-member lists (preprocessing 2^54, memory) is not priced.

## Ranked candidate gaps

| # | gap | type | bits (est.) | test | doors |
|---|---|---|---|---|---|
| 1 | Coupled omega list: typed (2) words that no (g, h) can complete through J1 + J3 | cost, lossless | c = 0.866: log2(0.17 + 0.83c) = **-0.17** (range -0.09 to -0.30), before list-build cost | exact count per member phase (t, b, u, v): build the coupled automaton (alignments 0/8/12, guessed carries), or 2^20-sample GPU check; then phase-typed DFAs; prove lossless against N3 by the Section 17 split | new; door 27 is a different key; mem_join left "list x list join on E lanes" as a lead |
| 2 | Third-beta row 18b3e098 (same tau, 0 new list words) | rate | -0.010 ceiling, net about -0.005 after credit | add row 4 to S, measure screen calls (MU) on the preregistered run, Section 17 count for 6e23be55 | LEVERS -0.00968 (fa97); typed compatibility now shown |
| 3 | FACTOR 0.974 vs measured real/model 0.9945 | premise | -0.0055 verifiable, -0.030 if a measured factor were declared | preregistered real-rate run on the shipped walk | door 43 |
| 4 | Unlisted beta* / beta2 outcomes (65% / 77% of R = 0 in paid trials) | rate | ceiling +1.74; **every add loses** (table A) | closed at the current ledger; beta2's 18 other taus not yet ratio-checked (need their taus from the count program) | doors 4, 36, ctr_class_transfer row 5 |
| 5 | E0/E2 zero difference and C3 b/d pin (stricter than the XOR event) | structure | negative | none | doors 22, 24, 33 |

Not gaps (exact): K2 length cancellation, Lemma Q class, cube <-> beta, Lemma N eps, pre-check, screen, guards, prefilter PF.
No W22-style "fake freedom" was found: the free words of the construction (Lemma T2) are a bijection onto admissible blocks.
