# Earlier levers checked against the pkgCA member loop (read-only audit, 2026-10-09)

Sources: the MASTER_PLAN.md `## ` headings; HANDOFF.md section 13 and its "lever" lines; the "Levers found", "lever" and "gain"
lines of ai_credits.md; and pkgCA `proof.md`, which I grepped and skimmed in sections 1, 9.1, 9.8, 11 and 13. I also read lines
1-344 of research/impl/outer.py. My probes ran lines 1-270 of that file (definitions only) and nothing else.
Labels: PROVED, MEASURED, DERIVED, GUESS. Figures under "size then" are quoted from the record.
Cost shares from the section 11 table of pkgCA (DERIVED): batch 51.5 %, solver credit 25.1 %, Q path 20.9 %, passing lane 2.6 %,
context 0.01 %. pkgCB (64.87) cuts the solver rows. That makes the batch share larger, so the batch levers below are worth a little more there.

## Answer: a middle level and a top level are both open, and the middle one needs no new premise

**Middle level: the cluster lever (Remainder, 10-06), made exact.** pkgCA does not use it ("representative": 0 hits; every
"cluster" hit is about the dependence clause).
- Automaton (2) reads omega from its lowest bit up. The table below gives the share of omega words still alive after the low b bits.
  It is PROVED by an exact DP over the automaton's states, and its value at 32 bits equals E_COUNT/2^32 = 0.054416 exactly:
  b = 1-4: 1 | 5-6: 0.8125 | 7-12: 0.4062 | 13: 0.2158 | 14-21: 0.1079 | 22-27: 0.0645 | 28-32: 0.0544.
- On the omega side the rotations add up to 7 + 8 + 16 = 31 bits, so flipping a free e1 bit k in {2..7, 10..14} leaves omega's
  bits 0..k-2 unchanged (DERIVED). MEASURED: 1,500 samples per bit gave a minimum equal to the mean, k-1. In 30,000 samples, the
  32 members that differ in e1 bits 10-14 shared omega bits 0..8, and bit-14 pairs shared bits 0..12, with 0 exceptions.
  The carry argument still allows rare exceptions, about 2^-17 per pair (GUESS), through a borrow chain that wraps around.
  An exact build must test that carry condition or bound the loss. This is a short question for Sol.
- Design: lay out the U and E lists so that each 32-member cluster (e1 bits 10-14) is contiguous. Batch the representatives, and
  have each lane test also read an alive bit for omega mod 2^9 (+2 units per lane, GUESS). If the representative is dead (59.4 %,
  PROVED), its 31 partners fail automaton (2) and are skipped. If it is alive, the partners run in normal batches.
  Per member that is (81/7 + 0.406 * 311)/32 = 4.3 units against 9.57 now: the batch row x 0.45, worth about **0.45 bit** (GUESS
  from the 9.8 unit counts, not executed). A second level on bit 14 inside the alive clusters (alive share 0.2158/0.4062 = 0.53)
  brings it to about 0.5 bit (GUESS).
- Premise cost: no new H1' clause. Only outer steps that fail automaton (2) are skipped, and those have zero success (Lemma F),
  so the set of examined outer steps is unchanged. It adds one count budget (alive clusters), of the existing H4' type.

**Top level: the two-level arrangement (Borrow, 10-06) moved one level up.**
- omega depends on the context only through six words: C0.b1, C0.c1, C0.d1, A12 = C0.b1 + w6 + X4 + w2, S15, and A3 = S0 + S5.
  This is DERIVED from LINES and MEASURED as 2,000/2,000 against step CO.
- Variant A: hold C0.d1, D2.b1, w6, S11 and A12 fixed, draw S4, set X9 = rol(X4,7) ^ D3.b1, and solve D2.a1 from one 32-bit
  equation. The probe solved it with a 2^16 split; a carry-guess T-function solve should cost a few hundred units (DERIVED).
  The result is omega(y) = Bc(y) - A3 for every member: MEASURED in 16/16 inner contexts with 200 members each, at 0.44 solutions per S4 draw.
  The batch drops from 67 to about 47 units, and each Q path gains about 4 units of cached loads: about 0.2 bit alone (GUESS).
  Combined with the middle level, bucket the clusters by Bc_rep mod 2^9. The alive buckets of an inner context are then the
  alive set + A3, so there is no per-cluster test: about 0.6 bit combined (GUESS).
- Variant B, where all six words are fixed so contexts share omega exactly, is blocked. Its fiber is the solution set of two coupled implicit
  32-bit equations (A12 and A3), with no cheap enumeration (DERIVED). It is the same kind of block as the E1.a2 cyclic equation.
- Premise cost: H1'(ii) would take the top as its unit (the contexts of one top share four outer words). The judge has ruled
  this clause type unsupported per outer step (1a92bf64, afbe2154); hecmas's context unit is the precedent for it. The judge risk is real.

## Lever table

| # | Lever | Found | Size then | In pkgCA proof? | Member loop: applies? | Cheapest test |
|---|---|---|---|---|---|---|
| 1 | Two-level trials (member-only words tabulated, middle once) | Borrow 10-06 15:44, NOTES.md s.11 | 6 per-trial eqs before first test (not priced) | YES: 9.8, Lemma Y, U/E lists | used | - |
| 2 | Representative-and-cluster | Remainder 10-06 20:35-00:10, h8/cluster, pkg8 | est 1.9 bit (GUESS); filed 93.5 at 1.71 per trial-equivalent; 2.222 bit on 55/63 (DERIVED) | NO | YES, exact form above, ~0.45-0.5 bit (GUESS) | write the cluster batch listing, count it with the 9.8 batch counter (research/frontline/ca), price it with research/tools/pricing; Sol: exactness lemma |
| 3 | Level at the top (grouping) | Sol cloud 10-08/09: "no sharing group provably decoupled" | - | NO | variant A ~0.2 alone, ~0.6 with #2 (GUESS); needs the top-unit clause | measure clustering of filter events by top in research/impl |
| 4 | Outcome subset | Kernel 10-09 00:10, pkg19/subset | 1.4 bit, premise-free (DERIVED) | YES, S = 0x5f (6 of 7) | re-optimise: the batch row does not depend on S, so the optimum may move to more outcomes; 0-0.1 (GUESS) | rerun the 16,383-subset scan with the section 11 rows |
| 5 | Other-beta outcomes sharing tau | Outside view 10-09 02:35 | +0.37-0.46 bit (DERIVED then) | NO (8: bit-14 taus j=8-14 not listed) | unclear: Q* is beta*'s cube; pkg22x scored 81.47 on another base | same scan with those outcomes added |
| 6 | 7 proposals per 256-bit word | Kernel 10-08, pkg18, Sol AQ | ~1.1 bit, pkg14d 71.39 to pkg18 70.32 (DERIVED) | YES: 6.5, 9.8, seven 36-bit lanes | used | - |
| 7 | 8 lanes of 32 bits | HANDOFF 13 row 9 | 0.2-0.4 bit (GUESS then) | NO | no: 41 of 67 batch units are per-lane tests, the Q path is per lane, and 32-bit lanes lose the guard bits; <= 0 (DERIVED) | none |
| 8 | Sub-class curves | Borrow 10-06, winglock's 256-member sub-class | ~1.4x, 0.49 bit (MEASURED by them) | NO in the counter search; the root experiment keeps 131,072 + rule A | no: member choice was recorded as an exact zero (Kernel 02:40), and every member costs the same | none |
| 9 | Designed constants by SAT | 10-06 02:44; scouts2/constants | counter re-rank: ours 67.94 vs next 71.09 (DERIVED) | YES (outer.py 33-70) | re-rank only; the 3.15-bit gap probably holds (GUESS) | reprice the 65 sets with pkgCA rows |
| 10 | E1 pre-test before solver (Sol AX c) | Kernel 10-09 02:40 | up to 0.69 bit (GUESS then) | YES: guard (G7) + pre-check VP | used | - |
| 11 | Rate discount | Quotient 10-07 15:55 (board 2, ours 3.75) | 0.907 bit then (DERIVED) | YES: 5/7, i.e. 1.4 | 1.4 to 1.25 = 0.163 bit (DERIVED); judge risk; the toy run realised 0.94 +- 0.13 | owner decision |
| 12 | Budgets just above premise (6001/6000, Lemma U) | Quotient 10-07 | 0.249 bit on pkg8 (DERIVED) | NO: 17/16 on E, PASS, CREDIT; CREDIT x 1.06 | 0.042 + 0.017 bit with credit at 1.01 (DERIVED) | preregistered sample (fifties/rates GPU code) + Chernoff |
| 13 | Preprocessing convention | Quotient (Subflatus3: 2^86 costs 0.005 at ~94) | 0.005 bit | charged at 2^70 = 0.108 bit at 65 | 2^68 (pkgCB) 0.028; 2^66 0.007 (DERIVED) | tighter attested-device bound |
| 14 | Outer-word rule / cubes | Remainder 10-07 13:05; cloud 17:25 | ~0.12; certified ceiling +8.39 % C15 (PROVED then) | NO | supply no longer binds: w5 can be set per context via X9 (DERIVED). But model M keeps a2 = a1+b1+w5 uniform, so the model gain is 0 and any real gain is <= 0.12 (GUESS) | GPU E1 rate split by w5 bits; low priority |
| 15 | c1 split / bitslicing / outer-step filter | 55/63 skeptics | 0.147 / 0.02-0.15 / 0.116 | NO | N/A: c1 is prescribed in Q* and solved jointly | - |
| 16 | Cached-Y9 rows | Fibre 10-09 13:44 (H_G) | 64.86 | NO, by decision (measured premise) | current work, not an earlier lever | - |
| 17 | E1.a2 prescription, 50s inverse, 62/64 | Kernel 10-08/09 | +13 blocked; 62/64 refuted on memory | NO | other constructions; not member-loop levers | - |

## Order
1. #2 (middle level): write the listing, count it, price it, and get Sol's exactness lemma. This takes CPU minutes. It is the only large
   item with no new H1' clause. On pkgCB's 64.87 it would give about 64.4 (GUESS).
2. #4 and #5: one subset rescan with the new rows. #12 and #13 are bookkeeping that needs evidence. #11 and #3 depend on the judge, so they go to the owner.

Not done: no batch listing was executed or counted, no pricing run was made, the exactness of the shared prefix is not proved,
and the variant A solver was not timed. Probes (scratchpad; they may be cleared): toplevel_check.py, copass_probe.py,
lowbits_probe.py, prefix_alive.py, share_probe.py in
temporary-run-output
