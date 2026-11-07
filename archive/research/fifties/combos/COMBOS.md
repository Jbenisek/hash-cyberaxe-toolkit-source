# COMBOS: tested combinations, fifties round (2026-10-09)

All prices are against the pkgCJ ledger: N = 6022417582191478187278, 63.602640. Two refute checks rebuilt N independently and got the same value (COMPUTED).
pkgCJ may no longer be the current baseline: EXTERNAL_JOBS.md lists an exact-borrow gate (EBG).
Labels: COMPUTED / DERIVED / GUESS, as in the evidence files. Paths are relative to workspace\research\.

## Tested

| id | methods combined | verdict | gain (bits) | refuted? | evidence | next step |
|---|---|---|---|---|---|---|
| crossline-XF1 | Per-context alive16 mask table and carry index in the member walk (masked Y9 layout, 7-lane chunks), plus a wrap guard: full walk iff Y0_rep bits 8..15 = A bits 8..15, A = C0.b1+w6+X4+w2 | GAIN | -0.2889, giving 63.313775 (COMPUTED). Every charge is a worst case: 236 units per opened cluster vs 368. Sensitivity (DERIVED): +8 units gives 63.3351, +12 gives 63.3457, +24 with the table doubled gives 63.3887. Break-even for 63.50 is 309 units (73 units of margin). | No. 1,000 fresh contexts, 7,358,346 opened clusters: LOST 0; mask vs exact alive16 0 mismatches; guard fires on {0, 128} clusters per context; fills 6,754 masked vs 12,481 old, 0 violations (COMPUTED). Reprice matches to 1.2e-7. | fifties\combos\crossline-XF1\RESULT.md; ...\crossline-XF1\refute\xf1_check.py, price_out.txt | Sol audits the native unit charges. The 6.5 machine has no broadcast, so X_BCAST needs a precomputed per-g list (about 4 units) or costs +12. Sol also checks register liveness. Then integrate into a pkgCJ copy and recheck the 64 KiB limit. |
| upfront-G50-Y1 | Upfront context screen (1,024-member pilot, keep top half by pilot) plus the pkgCJ ledger with K' = ceil(K/R_min) | GAIN (model price on a new premise) | Keep 1/2: row (i) -0.20 (refute: 0.2102 at u=11, giving 63.3924); row (ii) -0.15 (refute: 0.1536). Keep 1/4, row (i): 0.28-0.30. The screen cost 600+1024u is charged; the gain is still 0.195 at u=40 (DERIVED). | No. Independent interpreter, 4,096 new contexts. Openings are a fixed cost (kept/all 1.0002); passes ratio 1.3019; thresholds fixed on one seed and tested on the other give 0.201 and 0.213 (COMPUTED). Unproven: H_S3 below leaf level; row (ii) inputs (218 units, 0.409) are briefed values, not tested. | fifties\combos\upfront-G50-Y1\RESULT.md; ...\upfront-G50-Y1\refute\indep.py, iprice_out.txt | Brief Sol on the screened-law row with premises H_S1-H_S3. Run a preregistered GPU sample (about 16M contexts) before filing. Judge risk: this is a selection premise, and pkgCA's was replaced (HANDOFF.md line 983). |
| crossline-XF2 (Grok job 52) | Representative gate (open iff the rep's omega mod 128 is in S7, rate 52/128) plus a 2-unit straddle guard (Y0[8..15] = A[8..15], and a 4-entry per-context table on e1 bits 20..21) | GAIN vs pkgCJ; about 0 on top of EBG if EBG is the same change | Grok: -0.0866, giving 63.516016. Proof-grade: 63.516161 (-0.0865), using the lemma share 52/128 + (38/64)(9/65536) = 0.40633 plus 20 units per context (COMPUTED). Break-even for 63.55 is an opening rate of 0.42462 or 9 guard units. | No. The guard is exact: of 16,752,384 fully evaluated byte-equal clusters, 107,814 split, 0 outside the guard, 0 false closes. Over 262,144 contexts, every guard-off block of 64 opens exactly 26 (T-function parity lemma, DERIVED then COMPUTED). | grok\work\job52_xf2_repgate\ANSWER.md; fifties\combos\crossline-XF2-grok52\refute\RESULT.md, tlemma_out.txt | Settle whether EBG = XF2. The lemma also proves EBG's opening rate is at most 0.40633, which is Astra 18's question. File with the proof-grade figure. |
| crossline-XF3 | Stage-2 cap metering on PF71 (frame search) | NO_GAIN | 0. The stage-2 share in PF71's O_tot is s = 0 (COMPUTED): the eight Section 11 rows sum to O_tot, 71.14095, and none is a stage-2 row. | No refute run (no gain claimed) | fifties\combos\xf3_pfmeter\RESULT.md, step1.out | Close. A separate lead is in push-next item 5. |
| solvers-GROK-R3 | Grok's R3: word-level SMT (z3 4.13.3, QF_BV) inverting one MITM split point | NO_GAIN | 0. At 128 free bits, a known-sat instance timed out at 900 s. Scaling: 24 bits 44.4 s, 28 bits 185.1 s, 32 bits timed out at 120 s (COMPUTED). Extrapolates to 2^58-2^86 s per point (GUESS). | No refute run. Controls: pinned sat, flipped unsat. | fifties\combos\solvers-GROK-R3\RESULT.md, summary.txt | Add one line to pkg13\mitm\bits\BITS.md section 6: R3 is closed for SMT too. |

Surviving gains: 3 (XF1, G50-Y1, XF2). G50-Y1 rests on a new selection premise. XF2 is worth about 0 if EBG is already the same change.

## Dropped (one line each)

- multiblock-grok-mb-0: Grok's null multi-block answer. Collision probability 0 and setup of at least 2^64 (COMPUTED, cvdiff_check T0-T4, cvdeps). Nothing left to run.
- tree-GROK-TREE-0: Grok's null tree answer. Every structure maps to CLOSED items (EDGES_FIBRE 1, 2, 23, 25; MITM/BITS 2^128) or to workstreams run elsewhere. zero_mask_frames.py already run: 0 equal digest words.
- literature-none-pubcrypt-grok50: null literature report with no test. Its negatives (CV/semi-free-start re-randomises the frame; forced round-1 pattern; partial-output birthday at least 2^64) could be filed as CLOSED.
- difffamily-GROK-LENSFF-VERDICT: Grok's empty verdict, made stronger by check_grok.py (families 1-2 vary on all 256 bits). Family 5 = EDGES_FIBRE 26; family 3 is the excluded workstream.
- solvers-GROK-0: Grok's "none" verdict. Its follow-up is covered by LEVERS_REAPPLY's 17 levers and overtaken by XF1/XF2.
- solvers-GROK-R1: repeats a closed route. BITS.md 2-3 cones span all 128 guess bits, and a determined half still costs 2^64 > 2^63.6 (DERIVED).
- solvers-GROK-R2: repeats a closed route. Cube-and-conquer only re-derives automaton (2)'s exact cluster table (LEVERS_REAPPLY lever 2; BITS.md 6).
- solvers-GROK-R4: repeats closed or parked items (EDGES_FIBRE 19 and 22, SOLVER.md (b')). Ceiling 0.34 bit even if every solver call vanished, and building a CNF costs more than one call's setup (DERIVED).

## Push next (ranked)

1. XF1 native ledger. Sol audits the unit charges (index 16, guard 4, broadcast, 8 per batch, 19 per rep batch, table at most 34,484) and register liveness. Then integrate into a pkgCJ copy and check 64 KiB. Reason: largest gain (-0.289), all worst case, reproduced on 1,000 contexts, 73 units of margin before 63.50. Optional GPU run: a masked-fill premise near 7,000 (GUESS, about 63.19).
2. XF2 vs EBG. Settle whether they are the same change. Either way, tlemma.py's parity lemma gives a proved opening bound of at most 0.40633. That closes EBG's open premise (Astra 18) and adds the exact straddle guard with its 9/65536 rate ceiling.
3. G50-Y1 screened-law row. Sol brief with H_S1-H_S3, then a preregistered GPU sample on the 3090. Owner decides on the selection-premise judge risk.
4. Joint reprice of XF1 + XF2/EBG + G50-Y1 on one ledger. NOT TESTED. The gains do not simply add (DERIVED): G50-Y1's gain falls with the fixed share (0.20 at 0.598, 0.15 at 0.452), and XF1 and XF2 both shrink the fixed openings row.
5. PF71 ROOT_CAP. Replace the static 20x cap (5.82% of O_tot) with a Bernstein run budget: 0.075 bit (DERIVED), only if a frame provably has at most 2^53 roots. First question: does Lemma TG give at most one root per trial with c in Q*?

## Main-thread housekeeping (facts from the agent reports)

- Grok numbering clash: job52_r1_counter overwrote grok\job52_brief.md. The XF2 brief survives at grok\work\job52_xf2_repgate\BRIEF_FULL.md, and the XF2 row's result cell in EXTERNAL_JOBS.md was restored. Several sub-agents took number 50 (multi-block, literature). Per the XF2 report, the next free Grok number is 55.
- EXTERNAL_JOBS.md row 98 has two rows joined on one line ("|| Sol 5.6 cloud"). Not touched.
- To record as CLOSED: the multi-block lens (EDGES_FIBRE.md), R3 for SMT (BITS.md section 6), XF3.
- Folder deviations: XF3 is in xf3_pfmeter, R3 in solvers-GROK-R3, G50 in upfront-G50-Y1 (not crossline-XF3, r3_smt or upfront_screen).
- Auto-mode block: the classifier refused the XF2 refute agent's call to stop its own PID 30180 ("Interfere With Workloads"). It was not worked around, and the run ended by itself at 981.6 s.
