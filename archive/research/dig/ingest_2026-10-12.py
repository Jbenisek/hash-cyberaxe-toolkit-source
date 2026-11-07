#!/usr/bin/env python3
"""One-time ingest of the scattered row-dig results into CELLS.jsonl (2026-10-12). Read-only on all sources.
Every record goes through add_cell.validate. Refuses to run if CELLS.jsonl already has records (use add_cell.py after that).
potential_bits / prior on OPEN cells are the ingestor's estimates (labelled in SCHEMA.md), not measurements."""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import add_cell

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
D = '2026-10-12'
OUT = []

TL = 'our trail lab'
def WF(n): return 'our workflow: ' + n

def A(id, hash, i, j, obj, q, labels, status, number, source, own, evidence, lever=False, gain=None, notes='', **opt):
    r = dict(id=id, hash=hash, row_i=i, row_j=j, object=obj, question=q, labels=list(labels), status=status,
             number=number, source=source, own_test=own, evidence=evidence, date=D, lever=lever, gain_bits=gain, notes=notes)
    r.update(opt)
    OUT.append(r)

def run():
    # ====================================================== sha256-37: ATLAS37 evidence E1..E22
    ATL = 'research/tools/traillab/ATLAS37.md'
    RES = 'research/retest/rows22_24/RESULT.md'
    AUD = 'research/retest/expansion_audit/AUDIT.md'
    GRD = 'research/retest/interaction_grid/GRID.md'
    CD = 'research/CLOSED_DOORS.md'
    LV = 'research/LEVERS.md'
    s = 'sha256-37'

    A('S37-E1', s, 18, 19, 'rows 18/19 parities (FP)', 'Are the 8 value bits E18[1,5,10,11,18,28,29], E19[29] really 6 parities, and what do the 4 patterns gain on the full path?',
      'P', 'SAMPLED', '6 parities, 4 feasible patterns; q3 +1.93 bit (CI 1.78-2.09)', WF('r37_unforced (tighten)'), True,
      'research/tighten/r37_unforced.md; ' + CD + ' (sha256 row 2); ' + ATL + ' E1', True, 1.93,
      'Filed inside ffbe30bb (60.38707) as the four-pattern q3; R37M four-pattern 61.24102 uses own prereg SMC q3 2^-72.02. Structural value 2.00.', gain_basis='q3', topic='r37.FP.gain_q3')
    for pid, num, ev in (('pair0 FP x EX', '+2.027 (CI 1.78-2.09)', 'pair_0'), ('pair1 FP x MOD', '+1.887', 'pair_1'),
                         ('pair3 FP x F67', '+2.006', 'pair_3'), ('pair4 FP x R16', '+2.0003 (per-l 1.987..2.014)', 'pair_4')):
        A('S37-FP-' + ev, s, 18, 19, 'rows 18/19 parities, re-measured in ' + pid, 'Same lever re-measured in the interaction grid with own seeds.', 'P', 'SAMPLED', num,
          WF('lever-interaction-grid'), True, 'research/retest/interaction_grid/%s/RESULT.md; %s' % (ev, GRD), True, None,
          'Grid pairs 0,1,3,4 all inside the filed CI; structural value 2.00.', gain_basis='q3', topic='r37.FP.gain_q3')
    A('S37-FP-base', s, 18, 19, 'FP no-FP baseline q3', 'Which q3 base is "no FP"?', 'P', 'COMPUTED', 'pair 6 uses -74.02 (FP = -0.7543 T); pairs 5,7 use -73.97 (72.04+1.93; FP = -0.7272 T)',
      WF('lever-interaction-grid'), True, GRD + ' (cross-pair consistency)', False, None, 'Both internally consistent; pick the proof figure -74.02 before any filing text.', topic='r37.FP.base_q3')

    A('S37-E2', s, 22, 24, 'W22 exact set / W24 s1 set', 'How many 32-bit W22 give the right ds1 for dW24, and what is the exact set for W24?', 'KBCE', 'BEDROCK',
      'W22: 75*2^17 = 9,830,400 of 2^32 (cells 2^22, x75/32); W24: 17*2^24 = 285,212,672 of 2^32', WF('r37-rows22-24-exact'), True,
      RES + '; ' + AUD + ' rows 1,6; ' + GRD + ' pair 2', True, None,
      '6 XOR patterns 32/32/8/2/0.5/0.5 of 75; only the chi signing (24n,23n,15u) has Pr>0. W22 bits 13,17,26 NOT free: 7 of 8 patterns give a wrong dW24 (exhaustive 2^32).', topic='r37.W22W24.exact_counts')
    A('S37-GPT-tail', s, 22, 24, 'W22 / W24 exact counts (hot-tail feed)', 'Exhaustive C counts of the ds1 equations for W22 and W24.', 'KBCE', 'COMPUTED',
      'W22: 75*2^17 = 9,830,400 of 2^32 (cells 2^22, x75/32); W24: 17*2^24 = 285,212,672 of 2^32', 'GPT 5.5', False,
      'row_interactions/hot_tail_event_feed.zip (hot_tail_summary.md, exhaustive_count_run.txt, tail_counts.json; read as data, code not run)', False, None,
      'Identical to our rows22_24 counts. GPT code was NOT run by us; confirmed_by is our independent automaton + MC. GPT notes the 1275/2^24 product is a component model only.',
      confirmed_by=['S37-E2'], topic='r37.W22W24.exact_counts')
    A('S37-E3', s, 24, 26, 'W26 cancellation (rows 25-36 not free)', 'Is a collision after row 24 enough, or does dW26 = 0 cost something?', 'BCE', 'BEDROCK',
      'eq36 <=> eq24 AND dW26 = 0; W24 s1-condition 17*2^24/2^32 = 17/256 vs cell 1/16 (x17/16); W24 n30u29 share 1/17', WF('r37-rows22-24-exact'), True,
      RES + '; ' + LV + ' row 252', True, None, 'Forward PROVED by invertibility; reverse COMPUTED, 0 exceptions in 2^31 and 2^34.', topic='r37.rows25_36.free')
    A('S37-claim-25-36', s, 25, 36, 'rows 25-36 "free after row 24" (GPT reduction, Cloud 38 echo)', 'Are rows 25-36 free once the state is equal after row 24?', 'E', 'KILLED',
      'claimed free; actual: costs the W26 cancellation 17/256', 'GPT 5.5', True, RES + ' (Reduction); ' + LV + ' row 252', False, None,
      'Refuted by our rows22_24 (forward proof, reverse 2^34). The GPT first-pass atlas still says rows 25-36 are "deterministic confirmation after required cancellation/equality under fixed equal later W" (row_interactions/row_interaction_atlas.md); the later GPT Zone D ledger already carries the correction.', topic='r37.rows25_36.free')
    A('S37-E4', s, 22, 23, 'exact event after row 21 (E22[29] coin)', 'What is q_event for rows 22+ under the exact collision event vs the printed cells?', 'SE', 'COMPUTED',
      'q_event = 1275/2^24 = 2^-13.684 vs q_cell 2^-15: x2.4902 uniform; x2.4648 +/- 0.0145 real pipeline', WF('r37-rows22-24-exact'), True,
      RES + '; research/tighten/r37_unforced.md; ' + GRD, True, 1.30,
      'Gain +1.30 bit q3 (log2 of the filed 2.458). MOD = EX: count one of them, never both.', gain_basis='q3', topic='r37.EX.ratio')
    A('S37-EX-mc', s, 22, 23, 'EX ratio, Monte Carlo uniform', 'Same ratio by Monte Carlo through the schedule.', 'SE', 'SAMPLED', 'x2.4925 [2.4883, 2.4967]', WF('r37-rows22-24-exact'), True, RES, True, None,
      'Agrees with the exact uniform 1275/512 = 2.49023.', gain_basis='q3', topic='r37.EX.ratio')
    A('S37-EX-filed', s, 22, 23, 'EX ratio, first measurement (smc_exact.c)', 'Original exact-event scoring of late rows.', 'SE', 'SAMPLED', 'x2.45789 (+1.30 bit; control 2^-15.001)', WF('pre_sha256_1'), True,
      'research/retest/pre_sha256_1/RESULT.md; ' + AUD + ' row 4', True, 1.30,
      'smc_exact.c is byte-equal to 7319bba9 (a rival) smc.c: provenance caveat; owner later clarified public code is OK inside WSL after reading. Not affected by the expansion artifact (W22..W36 recomputed).', gain_basis='q3', topic='r37.EX.ratio')
    A('S37-EX-p0', s, 22, 23, 'EX ratio on ffbe states, grid pair 0', 'EX measured on our filed states.', 'SE', 'SAMPLED', 'x2.4580 (80,487/32,745)', WF('lever-interaction-grid'), True,
      'research/retest/interaction_grid/pair_0/RESULT.md; ' + GRD, True, None, 'pair0 compiled smc_pair0.c = diff of a rival printed SMC; R37X re-measure with OUR q3smc.c pending (HANDOFF 01:08).', gain_basis='q3', topic='r37.EX.ratio')
    A('S37-EX-p1', s, 22, 23, 'EX ratio on ffbe states, grid pair 1', 'EX measured on our filed states (MOD).', 'SE', 'SAMPLED', 'x2.4416 (160,263/65,638)', WF('lever-interaction-grid'), True,
      'research/retest/interaction_grid/pair_1/RESULT.md; ' + GRD, True, None, 'Same provenance caveat as pair 0. Joint ratio differs from pair 0 by ~1 se (~0.01 bit).', gain_basis='q3', topic='r37.EX.ratio')
    A('S37-EX-pooled', s, 22, 23, 'EX ratio pooled (pairs 0+1) and 99% LB', 'What EX value may a filing use?', 'SE', 'SAMPLED', 'x2.4471 (240,750/98,383; +1.291 bit); 99% one-sided LB x2.4329 (+1.2827)', WF('lever-interaction-grid'), True,
      GRD + '; research/retest/interaction_grid/wave2_r37.md', True, 1.291,
      'Defensible stack uses the LB: EX point + HEDGE double-counts the q3 margin. R37X package built with x2.4331.', gain_basis='q3', topic='r37.EX.ratio')
    A('S37-E5', s, 21, 22, 'E21[29] consumed at step 22', 'Is "unforced" E21[29] really free?', 'S', 'KILLED', 'necessary, costs exactly 1 bit (flip UNSAT)', WF('r37_unforced (tighten)'), True,
      'research/tighten/r37_unforced.md; ' + CD + ' (sha256 row 1)', True, 0.0, 'Part of Grok\'s "seven unforced bits" (claimed gain, value 0). All seven necessary.', topic='r37.unforced7')
    A('S37-E6', s, 20, 21, 'E20[10,11,15,23,24] consumed at step 21', 'Are the E20 value bits unforced?', 'SC', 'KILLED', 'all necessary (each flip UNSAT; 2^32 W20 over 23 prefixes)', WF('r37_unforced (tighten)'), True,
      'research/tighten/r37_unforced.md item 2; ' + CD, True, 0.0, 'Same family as S37-E5.', topic='r37.unforced7')
    A('S37-unf7', s, 20, 22, 'Grok "seven unforced bits" (U 74 to 67)', 'Do seven rows 20-22 bits come free?', 'S', 'KILLED', 'claimed sizeable q3 gain; measured 0.000 bit', 'Grok cloud', True,
      CD + ' (section 5 row 3); research/tighten/r37_unforced.md', True, 0.0, 'Our UNSAT + count refuted it. A different set (8 E18/E19 bits to 6 parities) is worth 2 bits (S37-E1).', topic='r37.unforced7')
    A('S37-E7', s, 16, 17, 'row-16 two-bit relations necessary?', 'Are the row-16 two-bit relations required by the exact collision event?', 'ZC', 'CLAIMED-UNTESTED',
      'claimed closed: exact carry-state DP over all 2^23 E17 per violating pair, 0 row-17 extensions; E15[4]^E16[4] implied; sampled 234.9M proposals per ablation', 'Luna cloud', False,
      CD + ' row 170; research/retest/r16_per_l/RESULT.md; ' + ATL + ' E7', True, 0.0,
      'Claimed closed. We have NOT re-run the DP (the CLOSED_DOORS wording "CLOSED + PROVED" is Luna cloud\'s). ATLAS37 labels it Z/PROVED. Needs our own test before KILLED.', topic='r37.row16.relations')
    A('S37-E8', s, 15, 16, 'per-l row-16 counts (W15 = l in L*)', 'Row-16 candidate counts per l.', 'B', 'CLAIMED-UNTESTED',
      'sum over 32 l = 1,052,672; 28 nonzero, 4 empty; per-l 4,096..65,536 (16x spread); dW16 = 0 every l', 'Luna cloud', False,
      'research/retest/r16_per_l/RESULT.md; ' + ATL + ' E8', False, None,
      'Sum matches the filed ledger counts (0db0eeb6 / 7319bba) but the per-l table was not re-run by us. The 4 empty sets are claimed killed by two-bit relations, not dW16 (the proof wording "nonzero W16 difference" is wrong). Witness first said W9 caused it (HANDOFF 00:03 retracted).', topic='r37.row16.perl')
    A('S37-E9', s, 15, 18, 'R16 x FP additivity', 'Does the choice of l interact with the rows 18/19 parities?', 'Z', 'SAMPLED', 'additive; per-l 1.987..2.014 bit, flat', WF('lever-interaction-grid'), True, GRD + ' pair 4', False, None, '')
    A('S37-E10', s, 16, 17, 'A16/E16 coupling, A17 subset of A16', 'Are rows 16 and 17 independent?', 'C', 'COMPUTED', 'lift 10.5 (replicated in halves); pass(A17) subset of pass(A16) (4 of 4)', WF('trash (tighten)'), True,
      'research/tighten/trash_sha256.md items 1,5; ' + CD + ' sha256 row 5', False, None, 'Already inside the end-to-end q3.')
    A('S37-E11', s, 16, 18, 'W-row pass identities', 'Do W cells of dense-free candidates collapse?', 'C', 'COMPUTED', 'W16=W18=W20, W17=W19=W21=W23 (exact); W22/W24 behave as a prefix filter', WF('trash (tighten)'), True,
      'research/tighten/trash_sha256.md item 6', False, None, '')
    A('S37-E12', s, 6, 21, 'F6/F7 x rows 18/19', 'Do the s0 F-sets of W6/W7 steer the rows 18/19 parities?', 'Z', 'SAMPLED', 'additive, <= 0.04 bit, F67 flat (p 0.19)', WF('lever-interaction-grid'), True, GRD + ' pair 3', False, None,
      'Strata sampled uniformly, not with the attack\'s W7/W8 weights; steering ceiling 0.015 bit untested (see S37-OPEN-8-24).')
    A('S37-E13a', s, 9, 24, 'hidden W9 condition (our finding)', 'Do only some W9-cell values let any W22 reach dW24?', 'B', 'COMPUTED', 'only 2^18 of 2^23 W9-cell values let any W22 reach dW24 (hidden ~5-bit condition)', WF('expansion-artifact-audit'), True,
      'research/retest/expansion_audit/w22/w9side.log; ' + AUD + ' (limits)', False, None, 'Side finding of our audit; whether the filed ledgers charge it is a GUESS (both q3 measured on published W9).', topic='r37.W9.hidden')
    A('S37-E13b', s, 9, 24, 'hidden W9 condition closed', 'Is the hidden W9 condition already paid in the dense part?', '0', 'CLAIMED-UNTESTED',
      'claimed CLOSED: row-10 cells freeze the 9 s0-read bits of W9 to the reachable pattern (row 9: 12 solutions, 2 reachable); "Pr -> 1" was one survivor (rejected)', 'Grok cloud', False,
      LV + ' row 254; HANDOFF.md 00:26,00:48; ' + ATL + ' E13', False, None,
      'ATLAS37 labels E13 PROVED (Grok cloud 1) - that is an outside claim, we did not test it. Two Grok clouds agree; Grok R asked to confirm the 10 unreachable patterns fail a row-10 cell.', topic='r37.W9.hidden')
    A('S37-E14', s, 23, 25, 'dW23 = dW25 = 0', 'Which late schedule words carry a difference?', '0', 'BEDROCK', 'dW23 = dW25 = 0 PROVED; only dW26 varies among W23..W36; dW31 = 0 constant', WF('r37-rows22-24-exact'), True,
      RES + '; research/tools/traillab/README.md + chi/chi37.txt', False, None, '')
    A('S37-E15', s, 21, 22, 'row 22 X_E = 0', 'Does row 22 add a state condition?', '0', 'BEDROCK', 'X_E = dS1(E21)+dCh(E21,E20,E19) = 0 with Pr 1; only the chi signing of W22 holds (other 7 Pr 0)', TL, True,
      'research/tools/traillab/README.md + chi/chi37.txt; ' + RES, False, None, '')
    A('S37-E16', s, 16, 0, 'E-driven rows 16..21 (inverse expansion)', 'Can W16..W21 be derived from chosen E and W0..W5 solved?', 'I', 'BEDROCK', 'six free coordinates; W_{t-16} = W_t - s1(W_{t-2}) - W_{t-7} - s0(W_{t-15})', TL, True,
      'research/tools/traillab/README.md + chi/chi37.txt (edrive 16 21)', False, None, 'Construction; traillab rebuild check.')
    A('S37-E17', s, 8, 4, 'W8 from the 12,103,680 A0 variants', 'How many A0 variants keep E4 on its cell?', 'I', 'COMPUTED', '12,103,680 A0-variants (cell + s0 F-set)', TL, True,
      'research/tools/traillab/README.md + chi/chi37.txt (var W8 ... back)', False, None, 'Carried from the traillab README (allg_classes). The dense-part recount agent (research/retest/dense_boring) is not ingested here.')
    A('S37-E18', s, 18, 20, 'W18 free: 40 trails -> 1.15 bits', 'Does freeing W18 give 40 trails?', 'K', 'KILLED', 'held-model artifact: 40 = 18/16/6/0; re-expanded: 1 trail', WF('expansion-artifact-audit'), True,
      AUD + ' rows 14,19; research/retest/expansion_audit/why/RESULT.md; ' + CD + ' row 168', True, 0.0, 'Through row 23: 1.07 vs 1.15 bits is a GUESS. Not citable as a full path.', topic='r37.W18.free')
    A('S37-E19', s, 14, 16, 'dW16 = s1diff(W14) + dW9 = 0 for every l', 'Is dW16 a lever?', 'Z', 'CLAIMED-UNTESTED', 'constant 0 for all l', 'Luna cloud', False, 'research/retest/r16_per_l/RESULT.md', False, None, 'Same Luna cloud run as S37-E8.', topic='r37.row16.perl')
    A('S37-E20', s, 17, 22, 'birthday lens on rows 17-22 / tail / F6 / F7', 'Does list-matching beat sampling on r37 rows 17-22?', 'Z', 'KILLED', 'no independent inputs (row 16+17 joint index 2^64); <0.01 bit', WF('birthday-lens-sweep'), True,
      'research/retest/birthday/SUMMARY.md; ' + CD + ' row 169', True, 0.0, 'Own scout + test reports in research/retest/birthday/r37r38_0, r37r38_1.')
    A('S37-E21', s, 23, 36, 'rows 23..36 automatic', 'Is anything left to win in rows 23..36?', '0', 'BEDROCK', 'automatic once dW22/dW24 right, E22[29]=1, dW26=0; the only late cost is the W26 cancellation (S37-E3)', WF('r37-rows22-24-exact'), True,
      RES + '; ' + LV + ' row 251', False, None, 'Forward PROVED; reverse COMPUTED 0 exceptions in 2^34.')
    A('S37-E22', s, 22, 22, 'W22 bits 13,17,26 "free" (+3 bits)', 'Are W22 value bits free?', 'K', 'KILLED', 'value 0: bits set the s1 difference signs, 1 of 8 patterns works (exhaustive 2^32; 64 prefixes full path, all collisions rebuilt)', WF('expansion-artifact-audit'), True,
      AUD + ' rows 1-3; research/retest/expansion_audit/w22/RESULT.md; ' + CD + ' row 168; ' + LV + ' row 234', True, 0.0,
      'Filed ffbe30bb / fdef4bab not affected. Three independent confirmations incl. a cloud voice wbit_sched.c (exhaustive 2^25, schedule recomputed).', topic='r37.W22.free_bits')
    A('S37-claim-W22', s, 22, 22, 'W22 free bits (Cloud 32 / wbit_gain.c)', 'Cloud 32 claim: +3 bits + log2 3 on the published prefix, PROVED.', 'K', 'KILLED', 'claimed +3 bits (PROVED label; sd 0 over 200 prefixes in wbit_gain.c)', 'Grok cloud', True,
      LV + ' row 234; HANDOFF.md 23:59', True, 3.0, 'Held-fixed-words artifact (wbit_gain.c confirmed to hold later words fixed). Claimed gain kept as the number; value is 0.', gain_basis='q3', topic='r37.W22.free_bits')
    A('S37-W22F-pair', s, 22, 22, 'FP x W22F', 'Does W22F stack with FP?', 'K', 'KILLED', 'CONFLICT: joint = FP alone; held mode reproduces x8, real expansion puts 0 in 7 of 8 columns', WF('lever-interaction-grid'), True,
      GRD + ' pair 2', True, 0.0, 'Exhaustive 2^32, one prefix.')

    # ---- ATLAS ranked "?" targets (OPEN) with estimates
    T = 'research/tools/traillab (cmd in ATLAS37.md ranked table)'
    A('S37-O1', s, 17, 17, 'row-17 two-bit relations E17[0]!=E17[13], E16[24]=E17[24], E16[15]=E17[15]', 'Are the row-17 two-bit relations necessary for the exact event, or can the exact event accept more (like rows 18/19)?',
      'DI', 'OPEN', 'untested; ATLAS rank 1. Local bill (fixed Table-17 prefix) is 2^-13, no local parity collapse (GPT 5.5 DP, see S37-GPT-r17)', TL, False, ATL + ' (ranked table 1)', True, None,
      'Single flips UNSAT only on the fixed dense part. Run: traillab window --rows 17 36 --event out --relax r17x2=dropx2 E17.', potential_bits=1.0, prior=0.15, gain_basis='q3')
    A('S37-GPT-r17', s, 17, 17, 'row-17 local condition bill', 'Count of E17 values passing the printed cells and the four relations on the fixed prefix.', 'D', 'CLAIMED-UNTESTED',
      'E17 printed cells 8,388,608 = 2^-9; each relation 1/2; all five 524,288 = 2^-13; no 8-to-6 style collapse locally', 'GPT 5.5', False,
      'row_interactions/row17_local_audit.zip (row17_summary.md, row17_local_dp.out; code not run)', False, None,
      'LOCAL_ONLY in scope (fixed Table-17 prefix, not full path). Consistent with the 13-bit row-17 bill in our proofs; not re-run by us.')
    A('S37-O2', s, 17, 18, 'A15[29]=A17[29]=A18[29] chain on the A16[29] difference', 'Does the exact event accept the other sign path?', 'D', 'OPEN', 'untested; ATLAS rank 2', TL, False, ATL + ' (ranked 2)', True, None,
      'Not in the row-16 six relations.', potential_bits=0.5, prior=0.15, gain_basis='q3')
    A('S37-O3', s, 18, 20, 'E18[6]!=E18[19], E18[2]=E18[20] on top of the 6 parities', 'Is the two-bit pair needed given the exact event? Stack with R1.', 'DXCK', 'OPEN', 'untested; ATLAS rank 3', TL, False, ATL + ' (ranked 3)', True, None, '', potential_bits=0.5, prior=0.15, gain_basis='q3')
    A('S37-O4', s, 20, 20, 'E20[2]!=E20[16]', 'Is the E20 two-bit relation necessary (only single-flipped on the fixed dense part)?', 'DI', 'OPEN', 'untested; ATLAS rank 4', TL, False, ATL + ' (ranked 4)', True, None, '', potential_bits=0.3, prior=0.15, gain_basis='q3')
    A('S37-O5', s, 16, 20, 'A16 difference (bit 29) into E20', 'Are there alternative signings of the A16 -> E20 path?', 'D', 'OPEN', 'untested; ATLAS rank 5 (traillab backward 16 21)', TL, False, ATL + ' (ranked 5)', True, None, '', potential_bits=0.3, prior=0.10, gain_basis='q3')
    A('S37-O6', s, 15, 22, 'EX x R16 per l', 'Does the exact-event ratio vary with the choice of l (W15 feeds W22 and W24 via W17)?', 'DX', 'OPEN', 'partly decided: A part (W22) flat across l; B|A part flat under uniform W8; residual <= 0.015 bit not measured (wave2_r37)', WF('interaction-grid-wave2'), True,
      'research/retest/interaction_grid/wave2_r37.md; ' + ATL + ' (ranked 6)', True, None,
      'Sampling needs a clean reimplementation of the row-16..21 SMC sampler (the only harness compiles a rival code).', potential_bits=0.015, prior=0.5, gain_basis='q3')
    A('S37-O7', s, 8, 24, 'EX x F67 per W8 class', 'Can W8/F67 class steering raise the exact-event ratio?', 'DX', 'OPEN', 'ceiling 0.015 bit, untested (ATLAS rank 7; GRID next 4)', TL, False, ATL + '; ' + GRD, True, None, 'Strata so far sampled uniformly.', potential_bits=0.015, prior=0.5, gain_basis='q3')
    A('S37-O8', s, 24, 26, 'EX x HEDGE double count', 'Is the W24 tail hedge already inside the exact event?', 'BCE', 'COMPUTED',
      'OVERLAP +0.00244 bit (q3 -72.02) / +0.00104 (safety 1.003); no tail hedge left (dropped by fb039a6e); the double count is the q3 margin 0.0033 bit vs EX uncertainty 0.0084 bit', WF('interaction-grid-wave2'), True,
      'research/retest/interaction_grid/wave2_r37.md; ' + ATL + ' (ranked 8: listed open there, answered here)', False, None,
      'Stale in ATLAS37: it still lists (24,26) as ranked test 8. Use EX at its 99% LB with HEDGE.')
    A('S37-O9', s, 19, 20, 'other row-19 / row-17 value bits: parity-collapse search', 'Is there a second parity collapse (E19[24,23,18,15,4], mask 01848010) like rows 18/19?', 'DZ', 'OPEN', 'not run beyond rows 18/19; >200 patterns appear with dense values free', TL, False,
      ATL + ' (ranked 9); ' + CD + ' sha256 row 2', True, None, 'traillab exact --rows 19 21 --enum E19:all --relax r19=dropv E19 01848010.', potential_bits=1.0, prior=0.20, gain_basis='q3')
    A('S37-O10', s, 13, 17, 'E13/E14 differences into row 17; row-17 pass rate given row 16', 'What is the exact row-17 pass rate given row 16?', 'D', 'OPEN', 'not measured beyond 6 events', TL, False, ATL + ' (ranked 10)', True, None,
      'Row 17 is the costliest late row (A17/A16 2^-17.6 on 4 events, E17/E16 ~2^-13 on 2 events).', potential_bits=0.5, prior=0.10, gain_basis='q3')

    # ---- other sha256-37 records
    A('S37-pairs-additive', s, None, None, 'FP x MOD / F67 / R16 / CAP / AC pair verdicts', 'Which r37 levers stack?', 'Z', 'SAMPLED', 'FP x EX 0.000; FP x MOD -0.010 ns; FP x F67 <=0.04 ns; FP x R16 flat; FP x CAP enables; FP x RARE overlap 0.00054; FP x AC enables',
      WF('lever-interaction-grid'), True, GRD + ' (8 of 80 pairs)', False, None, 'MOD = EX (count one). 72 pairs were still untested at that time (wave 2 added several).')
    A('S37-RARE', s, None, None, 'w7_rare_path (price_r37.py bug)', 'What is RARE worth after the double-subtracted row charge is fixed?', 'Z', 'COMPUTED', 'corrected P2 -0.000404 (published -0.00044); P1 ~-0.00004', WF('lever-interaction-grid'), True, GRD + ' pair 6',
      True, 0.000404, 'Bug: price_r37.py subtracts the 19*2^-9 row charge twice.', gain_basis='T', topic='r37.RARE.gain')
    A('S37-RARE-pub', s, None, None, 'w7_rare_path as published', 'Published RARE gain.', 'Z', 'COMPUTED', '-0.00044', WF('w7 full runs'), True, LV + ' row 244', True, 0.00044, 'Superseded by the corrected figure.', gain_basis='T', topic='r37.RARE.gain')
    A('S37-CAP', s, None, None, 'w7_budget Bernstein cap', 'Does Bernstein replace the Chebyshev work cap?', 'Z', 'COMPUTED', '-0.00211 (slack 2^-12.25); smoke -0.00176 at s=2^-13.25', WF('boring-edges-sweep'), True, LV + ' rows 203,242; ' + GRD + ' pair 5', True, 0.00211,
      'Ledger + proof rewrite, no experiment. Pcap 2^-19.05 (grid, Bernstein-optimal s) vs 2^-9.23 (MAP, Chebyshev s): definitional, not a conflict.', gain_basis='T', topic='r37.CAP.gain')
    A('S37-CAP-smoke', s, None, None, 'w7_budget Bernstein cap, smoke', 'First smoke of the Bernstein cap.', 'Z', 'SAMPLED', '-0.00176 (s = 2^-13.25, Pcap 2^-19.7, 9 of 9 checks hold)', WF('w7 smokes'), True, LV + ' row 203', True, 0.00176, '', gain_basis='T', topic='r37.CAP.gain')
    A('S37-stack', s, None, None, 'best r37 stack (EX LB + CAP + RARE + q3 -72.0367)', 'Where does the defensible r37 stack land?', 'E', 'COMPUTED', '60.17110 (EX LB+CAP+RARE 60.17146; optimistic hedge 60.16833; double-count 60.16741 DO NOT FILE)',
      WF('interaction-grid-wave2'), True, 'research/retest/interaction_grid/wave2_r37.md', True, 0.21597, 'vs filed ffbe30bb 60.38707. A_C 2^58 variant 58.580.', gain_basis='T', topic='r37.stack')
    A('S37-stack-g1', s, None, None, 'r37 stack, first grid (EX pooled point + CAP + RARE)', 'First stack estimate.', 'E', 'COMPUTED', '60.1697 (EX alone 60.1725; +CAP 60.1700)', WF('lever-interaction-grid'), True, GRD + ' best stacks', True, 0.2173, 'Superseded: point EX double-counts the margin.', gain_basis='T', topic='r37.stack')
    A('S37-stack-pkg', s, None, None, 'R37X package (EX x2.4331 99% CP pooled, CAP, RARE)', 'Built stack.', 'E', 'COMPUTED', '60.17144 (filed b43280d0 NOT_EVALUABLE: H1/H3 heuristics; fix workflow running)', WF('build-r37-ex-stack'), True, 'HANDOFF.md 01:08,01:44', True, 0.21563, '', gain_basis='T', topic='r37.stack')
    A('S37-AC', s, None, None, 'A_C floor below 2^60 (metered own characteristic search)', 'Can a metered search cut the 2^60 characteristic-search floor (r37 ~58.6 at 2^58)?', 'E', 'OPEN',
      'dense part 2^52.7 units (not the issue); target metered search < 2^46.6 compr-equivalents; D142 STP query already > 2^46.2 (Cloud 40 GPT 5.5 claim)', 'GPT 5.5', False,
      LV + ' row 258; HANDOFF.md 00:43; research/retest/interaction_grid/wave2_r37.md', True, 1.585, 'Owner decision before any multi-day run; needs evidence, not a policy choice. Stack 60.17 -> 58.585 at 2^58.',
      potential_bits=1.585, prior=0.08, gain_basis='T')
    A('S37-Ebucket', s, -4, 16, 'E_-4 / W0 bucket steering of W16', 'Can first blocks be grouped by E_-4 to tune W16?', 'D', 'CLAIMED-UNTESTED', 'claimed CLOSED: other 7 chaining words stay uniform in a bucket; ~3.2 bit net deficit; leader g=8,129 already contains every pair the shift helps', 'Grok cloud', False,
      LV + ' row 241; HANDOFF.md 23:38', True, 0.0, 'Outside proof; we did not test. Witness kept it closed after reading proof.md lines 31,33,430 (a reading, not a test).')
    A('S37-q3e2e', s, 16, 36, 'rows >= 16 factor double count (bucket / row 16 / row 17)', 'Are the row>=16 factors already inside q3 (success = g x 32 x q3)?', 'C', 'CLAIMED-UNTESTED', 'claimed CLOSED by three independent voices + proof text: all rows 16..36 inside q3; extra factors double-count',
      'Grok cloud; Luna cloud; GPT 5.5 (three voices)', False, 'HANDOFF.md 23:46; ' + LV + ' row 237', False, 0.0, 'Earlier trash note said 0 to ~8 bits depending on whether q3 is end-to-end. Closure rests on voices and the proof text, not on our test.')
    A('S37-perl-order', s, 16, 17, 'per-l row-17 pass rate test order', 'Does the test order over the 32 l matter?', 'B', 'CLAIMED-UNTESTED', 'claimed KILL: one Rmask load tests row 16 for all 32 l; rows 17+ only on passing (u,l); q3 unchanged by order', 'Grok cloud', False,
      LV + ' row 248; HANDOFF.md 23:47', True, 0.0, 'Proof 6.2 + Grok voice; D159 dropped by Witness on that basis.')
    A('S37-denseVar', s, 4, 13, 'Zone D: broader dense family (A0/A1/A2 variants moving W8/W9/W10)', 'Do broader dense variants bias row 16/17 or the late event?', 'I', 'OPEN',
      'UNTESTED. GPT 5.5 claims uniform law for P0 (A0/c7/fibre) after the W6/W7 gate (0db0eeb6 lemma); birthday scouts say A1/A2 variants break E5/E6 cells in r37', 'GPT 5.5', False,
      LV + ' row 264; row_interactions/zone_d_dig_ledger.zip (zone_d_dig_ledger.md); research/tools/traillab/digs/zoneD (in progress, not ingested)', True, None,
      'Reopened by owner 10-12: an argument from the proof lemma is not a test. CONFLICT between sources: birthday workflow KILLED the A1/A2 variants (S37-bday-dense) but GPT keeps P1 open.', potential_bits=1.0, prior=0.10, gain_basis='T', topic='r37.denseVariants')
    A('S37-bday-dense', s, 4, 13, 'birthday lens: dense-part variants A1/A2', 'Do A1/A2 variants give a birthday gain?', 'Z', 'KILLED', 'KILL (measured) 0 bit', WF('birthday-lens-sweep'), True, 'research/retest/birthday/SUMMARY.md; research/retest/birthday/r37r38_0', True, 0.0,
      'Own measurement; scope is the birthday lens only, not the whole Zone D question.', topic='r37.denseVariants')
    for rr, (ks, mv, hot, mq, st) in {
        4: ('E4=a0+C4; W8 recomputed', 'yes', 'W8/s0W8/late event', 'Does E4/W8 class route the late event?', 'OPEN'),
        5: ('E5 fixed in A0 family', 'no', 'W9 if broader family', 'Does moving E5 in a broader family bias W9?', 'OPEN'),
        6: ('F6 exact gate', 'conditional', 'W6/s0W6/row22', 'Do F6 subfamilies predict row 16/17?', 'PARTIAL'),
        7: ('F7/c7 class exact', 'conditional', 'W7/W22/c7', 'Do c7 classes predict survival?', 'PARTIAL'),
        8: ('W8 support word moves in A0 family', 'yes', 'W23/W24', 'Does a W8 signature bias q_event?', 'OPEN'),
        9: ('W9 fixed in A0 family', 'no', 'row16/W24/W25', 'Can a broader family move W9 usefully?', 'OPEN'),
        10: ('W10 fixed in A0 family', 'no', 'row17/W25/W26', 'Can a broader family move W10 usefully?', 'OPEN'),
        11: ('W11 fixed in A0 family', 'no', 'W18/W26', 'Can a broader family move W11 while preserving dense rows?', 'OPEN'),
        12: ('state row contributes to row16 constants', 'unknown', 'row16/W19', 'Do A12/E12 signatures predict row 16?', 'OPEN'),
        13: ('state row contributes to row17 constants', 'unknown', 'row17/W20', 'Do A13/E13 signatures predict row 17?', 'OPEN')}.items():
        A('S37-ZD%02d' % rr, s, rr, None, 'Zone D row %d dossier' % rr, mq, 'D', 'OPEN', 'UNTESTED (%s); movable in A0 family: %s; hot targets: %s' % (ks, mv, hot), 'GPT 5.5', False,
          'row_interactions/zone_d_dig_ledger.zip (zone_d_row_matrix.csv); GPT status tag ' + st, True, None,
          'GPT planned dig, no results. Row-pair digs by our trail lab / Grok CLI 106 are in progress (research/tools/traillab/zoneD*, digs/zoneD) and not ingested here.', potential_bits=0.5, prior=0.04, gain_basis='T')
    A('S37-GPT-rank', s, 16, 24, 'closing rank ledger (U = 74)', 'Per-row closing ranks of the condition ledger.', 'D', 'CLAIMED-UNTESTED', 'ranks: 16:17, 17:13, 18:15, 19:6, 20:7, 21:1, 22:11, 23:0, 24:4, rows 25-36: 0; total U = 74', 'GPT 5.5', False,
      'row_interactions/row_interaction_atlas.md (condition_rank_by_row.csv)', False, None, 'Taken from the reference card; the sum is 74 (checked arithmetically). GPT first-pass atlas, structural + source-derived, no carry automaton.')
    A('S37-GPT-replay', s, 0, 36, 'Table 15 replay by row', 'Does the Table 17 message pair reproduce Table 15 cell by cell?', 'D', 'CLAIMED-UNTESTED', '0 mismatches in 3,788 checked cells (msb_left orientation; lsb_left 303 mismatches); step-36 A and E equal', 'GPT 5.5', False,
      'row_interactions/sha256_row_tests_feed.zip (table15_replay_by_row.csv, row_tests_summary.md; code not run)', False, None, 'Our trail lab independently validated 53/53 known answers (S37-TL-validate).')
    A('S37-GPT-sens', s, 0, 36, 'bit-flip sensitivity of base message words into rows', 'Empirical sensitivity of every message word into every row on the Table 17 base.', 'D', 'CLAIMED-UNTESTED', 'input_word_to_row_sensitivity.csv (29 KB), not examined cell by cell', 'GPT 5.5', False,
      'row_interactions/sha256_row_tests_feed.zip', False, None, 'Data only; priorities file marks rows 16,17,18,19,22,24 critical (same as our ranked list).')
    A('S37-TL-validate', s, None, None, 'trail lab validation', 'Does traillab reproduce the known answers?', 'D', 'COMPUTED', '53/53 known answers', TL, True, 'HANDOFF.md 01:37; research/tools/traillab/tests', False, None, 'Validated before the atlas37-fill runs.')
    A('S37-assign', s, 18, 21, 'row dig assignment: rows 18-21', 'Necessity of the row 18-21 value bits beyond the parities.', 'D', 'OPEN', 'assigned 10-12 01:56 to Grok left; no result landed', 'main session', False, 'HANDOFF.md 01:56', True, None, 'Assignment record, no result.')
    A('S37-assign17', s, 17, 17, 'row dig assignment: row 17 necessity', 'Which row-17 conditions are necessary?', 'D', 'OPEN', 'assigned 10-12 01:56 to Grok right; no result landed', 'main session', False, 'HANDOFF.md 01:56', True, None, 'Assignment record. Overlaps S37-O1.')
    A('S37-assign25', s, 25, 36, 'row dig assignment: rows 25-36', 'Row cards for 25-36.', 'D', 'OPEN', 'assigned to Luna local D168; no result landed', 'main session', False, 'HANDOFF.md 01:56; research/sol_answer_D167_row_cards.md (not ingested)', True, None, '')
    A('S37-assign014', s, 0, 15, 'row dig assignment: rows 0-3, 14-15', 'Row cards for 0-3 and 14-15.', 'D', 'OPEN', 'assigned to Luna local D169; no result landed', 'main session', False, 'HANDOFF.md 01:56; research/sol_answer_D169_first_block_cells.md (not ingested)', True, None, '')

    # ====================================================== sha256-38
    t = 'sha256-38'
    W2 = 'research/retest/interaction_grid/wave2_r38.md'
    A('S38-EX', t, 23, 25, 'r38 exact event EX (D165)', 'Exact event vs printed cells for r38 rows 23+ (W23 drawn from the printed pattern only).', 'E', 'SAMPLED', 'x1.118 (+0.161 bit q3); halves agree; FP-front pooled x1.1019 (+0.1400)', 'Luna local', True,
      W2 + '; research/sol_answer_D165_r38_exact_event.md (not ingested)', True, 0.161, 'D165 replayed by our workflow with 128 frozen seeds; counts match exactly. EX = MOD = W25 modular-only (0 exceptions in 26,149). Program/rebuild change needed: accept 0x6 and 0xe W25 patterns (rebuild() rejects all 94 extras).',
      gain_basis='q3', topic='r38.EX.ratio')
    A('S38-EX-fp', t, 23, 25, 'r38 FP x EX joint', 'EX under the four-pattern front.', 'E', 'SAMPLED', 'E/C = 1.1019 (+0.1400 bit); 2 x 4,000 replicates; halves 1.1033 / 1.1006; chi2 11.39 on 3 df (p ~0.01)', WF('interaction-grid-wave2'), True, W2 + ' sec 2', True, 0.1400,
      'OVERLAP small: EX falls 1.118 -> 1.102 under FP. FP gain itself (+2.00) is an estimate until D154.', gain_basis='q3', topic='r38.EX.ratio')
    A('S38-EX-c38', t, 23, 25, 'r38 exact event expectation (Cloud 38)', 'Cloud 38 expects an r38 exact-event gain of ~+1.3 bits.', 'E', 'CLAIMED-UNTESTED', 'expects ~+1.3 bit q3 (chi38 tail: dE19/dE21 cancelled by W23/W25 + one coin E23[29])', 'GPT 5.5', False,
      'HANDOFF.md 00:18', True, 1.3, 'Measured EX with W23 from the printed pattern is only +0.161 (S38-EX); the gap is the W23-full-set lever (S38-W23set). Not an independent gain.', gain_basis='q3', topic='r38.EX.ratio')
    A('S38-W25mod-g', t, 25, 27, 'r38 W25 modular-only (Grok L, 256 prefixes)', 'Gain of accepting the modular-only W25 carry 0x60000000.', 'E', 'CLAIMED-UNTESTED', 'pooled x1.0655 (+0.092 bit); mean 1.0768 [1.0712, 1.0823]', 'Grok left', False, LV + ' row 261; HANDOFF.md 00:57', True, 0.092,
      'Inside EX (S38-EX): count EX or the carry, never both. EX = carry 1.0655 x rest 1.049 per Grok L.', gain_basis='q3', topic='r38.W25mod.factor')
    A('S38-W25mod-p', t, 25, 27, 'r38 W25 modular-only (1 prefix)', 'First detection of the extra survivors with the same modular dW25.', 'E', 'COMPUTED', '8,192 / 139,264 extra survivors, +0.087 bit (1 prefix)', WF('expansion-artifact-audit'), True, LV + ' row 255; ' + AUD, True, 0.087, 'Side find of the audit.', gain_basis='q3', topic='r38.W25mod.factor')
    A('S38-W25mod-o', t, 25, 27, 'r38 W25 modular-only inside D165', 'The same lever on our own law.', 'E', 'SAMPLED', '0x6 share x1.094 (D165 law), x1.078 (FP law); 0xe share 0.024; Grok bit-31 "never" is false (19 events here, 470 in the FP run)', WF('interaction-grid-wave2'), True, W2 + ' sec 1', True, 0.0, 'The factor depends on the proposal law: quote only a value measured on the filing\'s own law.', topic='r38.W25mod.factor')
    A('S38-W23set', t, 23, 25, 'r38 EX with W23 over its FULL exact set', 'Does the exact event gain more if W23 is drawn from its full exact set (6 XOR patterns, 150 parts vs 32 = 75/32) instead of the printed pattern?', 'EB', 'CLAIMED-UNTESTED',
      'up to ~+1.2 bit q3 (spark 10-11 measured r38 window 2.38x)', 'Grok left', False, LV + ' row 262', True, 1.2, 'D165 sampled W23 from the printed pattern only. Two-bit conditions 19/16 if kept. Not measured by us.', potential_bits=1.2, prior=0.30, gain_basis='q3')
    A('S38-W23free', t, 23, 25, 'r38 W23 bits 13,17,26 "free" (+3)', 'Are W23 value bits free on 38 steps?', 'K', 'KILLED', 'value 0: chi38 W23 held 8 x 33,554,432 collisions, re-expanded only 111 with 139,264', WF('expansion-artifact-audit'), True,
      'research/retest/expansion_audit/why/RESULT.md; ' + AUD + ' rows 2,3; ' + LV + ' rows 235,250', True, 0.0, 'Claimed +4.585 q3 (log2 3 + W23 +3) -> 70.1 / 99 are void. Grok CLI 104 measured only the printed pattern passes (8783/8783). The log2 3 for E19/E20 survives only as the FP window measurement.',
      topic='r38.W23.free')
    A('S38-claim-W23', t, 23, 25, 'Cloud 32 r38 +4.585', 'Cloud 32: PROVED +4.585 bits on the published prefix.', 'K', 'KILLED', 'claimed +4.585 q3 (PROVED label)', 'Grok cloud', True, LV + ' row 235', True, 4.585, 'Refuted by S38-W23free.', gain_basis='q3', topic='r38.W23.free')
    A('S38-FP', t, 19, 20, 'r38 four-pattern E19/E20 (FP, D154)', 'What does the E19/E20 pattern relaxation gain on r38 on its own law?', 'P', 'OPEN', 'estimate +2.00 q3 (T -0.62 on fdef4bab); D154 not landed in these sources', 'Luna local', False,
      W2 + ' sec 3,6; research/sol_answer_D154_r38_four_pattern.md exists (written 02:17, not ingested)', True, 0.62, 'The +2.00 is transferred from r37 (E1). Needs its own-law measurement, then FP+EX joint re-run.',
      potential_bits=0.62, prior=0.80, gain_basis='T')
    A('S38-D7', t, 17, None, 'r38 D7 delta7 pairs-in-group', 'What is the measured H5 delta7?', 'C', 'SAMPLED', 'delta7 = 0.293 (99% CP 0.305; D146 CP99 0.296687); ledger -0.110 (71.0725 -> 70.96278)', WF('retest t4'), True,
      'research/retest/t4/RESULT.md; ' + W2 + ' sec 3,5', True, 0.110, 'Needs a preregistered rerun for filing. After FP the marginal is -0.041.', gain_basis='T', topic='r38.D7.gain')
    A('S38-D7-g', t, 17, None, 'r38 D7, other statements', 'D7 as quoted in other registers.', 'C', 'SAMPLED', 'about -0.1 (LEVERS 222); about -0.107 (GRID text)', WF('lever-interaction-grid'), True, LV + ' row 222; ' + GRD, True, 0.107, '', gain_basis='T', topic='r38.D7.gain')
    A('S38-stack', t, None, None, 'best r38 stack (D7 + EX + FP joint)', 'Where does the own r38 line land?', 'E', 'COMPUTED', '70.38897 (-0.684 vs 71.07250); A_C 2^68: 69.16210 (-1.910); FP is an estimate', WF('interaction-grid-wave2'), True, W2 + ' sec 3,5', True, 0.684,
      'W23F excluded. Product of separate FP and EX (70.38596) is 0.003 too much.', gain_basis='T')
    A('S38-CAPan', t, None, None, 'CAP analogue on r38', 'Does a Chebyshev-overflow tightening help ledger38?', 'Z', 'KILLED', 'dead < 1e-5 bit (uses 3.4e-6 of the 0.39 budget; 70.96278 -> 70.96280)', WF('interaction-grid-wave2'), True, W2 + ' sec 4', True, 0.0, '')
    A('S38-phiinv', t, 16, 16, 'R38M row 16 by phi^-1 (solver)', 'Can phi^-1 over (A2,G\') entries solve row 16 cheaply?', 'I', 'KILLED', 'c_tot = 631,973 word ops/entry (2^19.27, CI 630.0k-633.9k) -> S 96.27 vs 91.21; best tree 5,194 nodes (2^12.34), floor >= 2^14.3 even at 4 ops/node', WF('birthday-lens-sweep'), True,
      'research/retest/birthday/r38_phiinv/RESULT.md; ' + LV + ' row 256', True, 0.0, 'Recall 0 mismatches vs 2^32 brute force (3 runs x 64 targets). The birthday SUMMARY.md written earlier still lists this as OPEN (stale). Kernel vector 0x27f42515 confirmed.', topic='r38M.phiinv')
    A('S38-phiinv-claim', t, 16, 16, 'phi^-1 estimate 2^5.9 live states', 'GPT estimate: ~2^5.9 live carry states.', 'I', 'KILLED', 'claimed 2^5.9 ops per entry (independent predicates); ceiling ~1.5 bit', 'GPT 5.5', True,
      'research/retest/birthday/r38_phiinv/RESULT.md (check 3)', True, 1.5, 'Folding the W9 predicate raised nodes 4.6x: the independence estimate fails.', gain_basis='S', topic='r38M.phiinv')
    A('S38-validset', t, 16, 16, 'R38M reverse side: enumerate valid A1 set', 'Can the valid-A1 set be enumerated directly and matched forward?', 'I', 'KILLED', 'valid set 2^19.84 per (A0,A2) (923,932 published; 49 pairs mean 938,297, min 15,656, max 2,881,792); floor 938k/22 = 2^15.4 > 2^14.2 even at 1 op/element', WF('birthday-lens-sweep'), True,
      'research/retest/birthday/r38_validset/RESULT.md; ' + LV + ' row 259', True, 0.0, 'Only 49 of 196,608 (A0,A2) pairs; floor argument suffices. W9 part is 8 affine pieces (arithmetic coord), W8 carry-mixed.', topic='r38M.phiinv')
    A('S38-gamma', t, 16, 16, 'R38M gamma(A2) image generator', 'Is there an A1 source that does not freeze A2, so W16 - s1(W14) = phi(Y+A1)+gamma(A2)+Z can be generated from the image (2^18.04 per tail, 810 KB packed)?', 'I', 'CLAIMED-UNTESTED',
      '~2^5.1 ops per success IF an A1 source does not pin A2', 'Grok right', False, LV + ' row 263; HANDOFF.md 01:56 (Grok 105 running)', True, None, 'Needs validity check of the recovered (A1,A2).', potential_bits=2.0, prior=0.08, gain_basis='S')
    A('S38-bday-time', t, 17, 17, 'birthday lens: r38 time row 17 folded into T_j', 'Index size of row 17 folded.', 'Z', 'KILLED', 'index >= 2^96', WF('birthday-lens-sweep'), True, 'research/retest/birthday/SUMMARY.md', True, 0.0, '')
    A('S38-assign', t, 16, 17, 'row dig assignment: chi38 row 16/17 necessity', 'Which chi38 row-16/17 conditions are necessary?', 'D', 'OPEN', 'assigned to Luna cloud; no result landed', 'main session', False, 'HANDOFF.md 01:56', True, None, 'Assignment record.')

    # ====================================================== sha3-r6
    a = 'sha3-r6'
    WV = 'research/retest/interaction_grid/wave2_sha3.md'
    A('R6-8FORMS', a, None, None, '8FORMS value-masked 8-XOR-form table', 'Lowest r6 time-score build.', 'C', 'COMPUTED', '909b6453 121.8701 PASSED (review); promoted leader ab10cd11 122.66823', WF('r6 build'), True, WV + '; HANDOFF.md closing state', True, 0.7981, '', gain_basis='T')
    A('R6-COSET', a, None, None, 'coset-specialized survivor kernel (S6K)', 'Does a per-coset kernel cut the 44% batch-kernel row?', 'C', 'COMPUTED', 'f1346045 121.71644 (-0.1537 over 8FORMS) NOT_EVALUABLE; retry-1 6c60fdf7 121.72219 (+0.00575) REFUTED (F-SURVIVOR-MEAN-MISSING); retry 2 running', WF('fix-s6k-ruling'), True,
      WV + '; HANDOFF.md 01:08,01:37; research/dossiers/6c60fdf7', True, 0.1480, 'Gain after the fix 121.8701 - 121.72219 = 0.148. Retries are not limited (owner).', gain_basis='T', topic='r6.COSET.T')
    A('R6-COSET-v0', a, None, None, 'S6K first version', 'First coset-kernel figure.', 'C', 'COMPUTED', '121.71644', WF('build pkgS6K'), True, WV, True, 0.1537, 'Superseded by the fixed generator charge (121.72219).', gain_basis='T', topic='r6.COSET.T')
    A('R6-KEYW', a, None, None, 'wider key width b >= 141 in the coset regime', 'Does the coset regime shift the key-width optimum (shipped b=140)?', 'B', 'OPEN', 'b=141 -0.0126, b=142 -0.0189, b=144 -0.0237 and still falling; benefit side only, setup cost uncharged -> not claimable', WF('interaction-grid-wave2'), True, WV, True, 0.0237,
      'Needs the wider-key cost model in the coset regime (does S_g / FES plane count grow with b).', potential_bits=0.024, prior=0.30, gain_basis='T')
    A('R6-FESKEY', a, None, None, 'FES 4-slots-in-3-words packing key (D163)', 'Does the packing win?', 'Z', 'KILLED', 'T=36 lower bound +0.0011; best packing found T=39; T=35 would be -0.016', WF('lens_t3 / wave2_sha3'), True, WV + '; ' + LV + ' row 247', True, 0.0, '')
    A('R6-PARAM', a, None, None, 'free-parameter neighbourhood (KBUD/GENBUD/KG/FBDIV/FB/splits)', 'Is any dial off optimum at the coset ledger?', 'Z', 'KILLED', '0 bit; t3_r6 reproduces 121.71644; all elasticities < 0.01', WF('lens_t3'), True, WV + '; research/retest/lens_t3', True, 0.0, 'Premise-bound dials need a new prereg.')
    A('R6-RATE', a, None, None, 'rate-constant lanes (tail_sha3)', 'Rate-constant lane row.', 'Z', 'OPEN', '0.0049 bit, untested', WF('tail_sha3'), True, WV + '; research/retest/tail_sha3', True, 0.0049, '', potential_bits=0.0049, prior=0.5, gain_basis='T')
    A('R6-K13', a, None, None, 'memory-rule K=13 Gray-body (S)', 'Counted bitslice of the K=13 Gray body.', 'C', 'OPEN', 'S 124.05 vs 125.28 (S6D) / 128.03143 (S6R generic); needs counted bitslice', WF('interaction-grid-wave2'), True, WV, True, 1.23, 'Memory-rule board is a separate axis.', potential_bits=1.23, prior=0.30, gain_basis='S')
    A('R6-DPrho', a, None, None, 'dense bitsliced DP-rho unit question', 'How many ops per 64-bit word per step does the 256-lane DP-rho cost?', 'C', 'OPEN', '152.99 ops/step counted (one 256-lane op = one op) -> S 124.63; per 64-bit word 499-612 ops/step -> S 126.3-126.6', WF('retest t1'), True,
      'research/retest/t1/RESULT.md; ' + CD + ' section 5 row 14', True, 1.4, 'Not closed and not a win: OPEN depending on the word-width/spill rule. Birthday scout: DP-rho S1-S3 separable pairs 0 at r>=4 (KILL).', potential_bits=1.5, prior=0.10, gain_basis='S')
    A('R6-S6D', a, None, None, 'memory cut to exactly 2^20 (D166)', 'Is a 2^20 memory cap better?', 'Z', 'KILLED', 'time 125.33206 at mem 20 vs S 125.28: -0.05 worse', 'Luna local', True, LV + ' row 260; HANDOFF.md 00:52', True, 0.0, 'Arithmetic on our ledger; D166 answer file not ingested.')
    A('R6-bday', a, None, None, 'birthday lens: S1 8-bit filter, S2 Wagner, S3 key width, DP-rho', 'Any separable pairs?', 'Z', 'KILLED', '0 separable pairs at r >= 4', WF('birthday-lens-sweep'), True, 'research/retest/birthday/SUMMARY.md', True, 0.0, 'Measured in the scout pass (scratchpad bday/sep.py); no separate test run. A CLOSED_DOORS SHA3 row was requested.')
    A('R6-edges', a, None, None, 'T3 optimiser, T5 verifier edges, sha3 tailings', 'Any boring-edge gain?', 'Z', 'KILLED', '0 bit', WF('boring-edges-sweep'), True, 'research/retest/lens_t3; research/retest/lens_t5; research/retest/tail_sha3; ' + LV + ' row 247', True, 0.0, '')
    A('R6-zerodigest', a, None, None, 'zero-digest 4-round cores / full collision < 2^115', 'Is there a lighter zero-digest tail?', 'Z', 'CLAIMED-UNTESTED', 'claimed closed: parity-1 >= 145, parity-2 (w2 <= 16) >= 150, HW3 >= 165, kernel HW <= 2 >= 230; near-collision 2^117.85 + 6 digest bits = 2^123.85', 'Grok cloud; GPT 5.5 (Cloud 37)', False,
      CD + ' row 167; ' + LV + ' row 212; HANDOFF.md 00:00', False, 0.0, 'Outside bounds; our own search covered cores >= 145. Near-door: zero-digest cores outside the weight-2 kernel class and the unrestricted 4-round search are unrun.')

    # ====================================================== sha3-r5
    f = 'sha3-r5'
    A('R5-LEAN', f, None, None, 'pkgR5L lean time-score derivative', 'Best r5 stack.', 'C', 'COMPUTED', '32.85434; filed e1317b6a REFUTED (fatal: preprocessing bound deducted 23.2e9 online-connector primitives); fix workflow pkgR5L2 running', WF('fix-r5l-ruling'), True,
      WV + '; HANDOFF.md 01:50,02:04', True, None, 'Single package; no additive free lever.', gain_basis='T')
    A('R5-DT2', f, None, None, "D' + T2 on the memory-rule base", 'Does D\'+T2 add to LEAN?', 'Z', 'COMPUTED', '-0.0160 on 32.87429; OVERLAP with R5L (do not add)', WF('interaction-grid-wave2'), True, WV, False, 0.0160, 'Argued from tail notes, not re-run on one common base.', gain_basis='T')
    A('R5-E1', f, None, None, 'E stage 1 split (24 equations, degree 4, 32-dim window)', 'Is the stage-1 split separable (own c_df2.py ANF + hypergraph)?', 'C', 'OPEN', 'untested; safe online part 0.024 bit, G2 part 0.36 only if judges accept repricing', WF('birthday-lens-sweep'), True,
      'research/retest/birthday/SUMMARY.md (audit item 2)', True, 0.024, 'Dense window basis probably couples every pair. KILL if the graph is complete. Lists must be charged in prims against 203 prims per step.', potential_bits=0.024, prior=0.10, gain_basis='T')
    A('R5-T3', f, None, None, 'T3 popcount into key; connector / B\'', 'Any gain?', 'Z', 'KILLED', 'KILL (re-count) / no form', WF('birthday-lens-sweep'), True, 'research/retest/birthday/SUMMARY.md', True, 0.0, '')
    A('R5-CAPS', f, None, None, 'X_MAX/A_MAX/B_TRUE/coin caps', 'Are outcome-informed caps allowed?', 'Z', 'KILLED', 'refused outcome-informed class', 'judge ruling on our filing', True, WV, True, 0.0, 'A rule closure, not a maths result; own_test means our filing was ruled.')

    # ====================================================== blake3-r2
    b = 'blake3-r2'
    WB = 'research/retest/interaction_grid/wave2_blake3.md'
    for id_, obj, single, marg, st, own, note in (
        ('BND115', 'boundary words 186 -> 115 per live block', 0.022315, 0.022613, 'COMPUTED', True, 'certified exact DP (tail3), premise-free; LEVERS "tailings" quotes 0.0223'),
        ('SOLD', 'S_old at logged maxima (9010.5 s)', 0.012449, 0.012753, 'LOCAL_ONLY', True, 'weakest: the 116-line SEL log is not in the package; same SEL accounting area that refuted 5a08fffa'),
        ('F974', 'H1\' FACTOR 0.97 -> 0.974', 0.005487, 0.005526, 'COMPUTED', True, 'cited one-sided 1-1e-6 bound 0.97402 (proof 10.3); not re-run'),
        ('SCAN12', 'scan 21 -> 12 per passing lane', 0.004248, 0.004359, 'COMPUTED', True, 'hand count; 13 is the safe figure (+0.000485)'),
        ('CTX436', 'context 500 -> 436 (fixed name store = 1 op)', 0.002591, 0.002662, 'COMPUTED', True, 'reading of the machine rule')):
        A('B3-' + id_, b, None, None, obj, 'Gain on the pkgB3T ledger (57.2365).', 'C', st, 'single -%.6f; marginal inside B3U -%.6f' % (single, marg), WF('interaction-grid-wave2'), own, WB + '; research/retest/tail1; tail2; tail3', True, single, note, gain_basis='T')
    A('B3-LAM', b, None, None, 'H1\' lambda 24797 -> 24723', 'Lambda lever.', 'C', 'OPEN', '-0.003985 single (-0.004013 on B3U); premise not preregistered', WF('interaction-grid-wave2'), True, WB + '; research/retest/tail1', True, 0.003985, 'Shares premise H1\' with F974: if H1\' is challenged both fall.', potential_bits=0.004, prior=0.5, gain_basis='T')
    A('B3-URANGE', b, None, None, 'dispatch +2 per range risk', 'Possible under-charge already in the lead.', 'C', 'COMPUTED', '+0.001318 (risk, 19 -> 21)', WF('interaction-grid-wave2'), True, WB, False, -0.001318, 'Risk, not a lever.', gain_basis='T')
    A('B3-B3U', b, None, None, 'B3U stack of five levers', 'Where does the blake3 lead land?', 'E', 'COMPUTED', '57.18900 (-0.04750 vs 5f7e222e 57.2365); sum of singles -0.047089; all 15 pairs ADDITIVE (<= 0.0002); filed c994a61f PASSED; premise-robust subset ~57.2018-57.2022',
      WF('interaction-grid-wave2'), True, WB + '; HANDOFF.md 01:44,01:56', True, 0.0475, 'Control reproduces 57.23649786.', gain_basis='T')
    A('B3-STREAM', b, None, None, 'B3M stream outputs: peak = search phase 2^42.45124', 'Is a streamed output counted as held memory?', 'C', 'OPEN', 'S 85.43472 -> 84.88595 (-0.549; LEVERS says -0.548); total -1.30 with RELEASE, nested not additive', WF('interaction-grid-wave2'), True, WB + '; ' + LV + ' row 249', True, 0.549,
      'Needs an organizer ruling on the memory rule. Cap-t alternative is dead (net ~0).', potential_bits=0.549, prior=0.40, gain_basis='S')
    A('B3-RELEASE', b, None, None, 'B3M release search tables before writing output', 'Does releasing early lower the peak?', 'C', 'COMPUTED', 'S 86.19471 -> 85.43472 (-0.76) BUILT pkgB3S2; skeptic CONFIRMED; prefile ALL PASS', WF('build B3M'), True, LV + ' row 246; research/retest/b3m_maxphase/RESULT.md', True, 0.76, '', gain_basis='S')
    A('B3-replica', b, None, None, 'B3M replica cut after STREAM', 'Do lane replicas (6 (2^34+2^30) of 171*2^30 words) pay after STREAM?', 'C', 'OPEN', 'memory up to ~-0.6, time cost unknown, only after STREAM', WF('interaction-grid-wave2'), True, WB, True, 0.6, '', potential_bits=0.6, prior=0.10, gain_basis='S')
    A('B3-G5-meas', b, None, None, 'G5 route: measured y', 'What is the C2-stage rate y of the G5 route?', 'C', 'COMPUTED', 'y = 11.69 pooled over 1.4e9 D3 instances: 57.70, break-even with the board (58.16 with measured D3b rate); D3c stage alone 6.4-7.1 bits', WF('g5_y_result (tighten)'), True, 'research/tighten/g5_y_result.md; ' + CD + ' section 5 row 4', True, 0.0, 'Earlier claims: y >= 6.00 (46.01+y, 6 instances showed none, probability ~0.8) and y >= 1.52 (7-instance smoke): small samples.', topic='b3.G5.y')
    A('B3-G5-old', b, None, None, 'G5 route: early claim y >= 6.00 / "low 50s"', 'Early G5 claim.', 'C', 'KILLED', '46.01 + y with y >= 6.00 (6 instances, zero passes); smoke y >= 1.52 (47.91)', 'Grok cloud', True, CD + ' section 5 row 4', True, None, 'Small-sample artifact, superseded by the pooled 11.69.', topic='b3.G5.y')
    A('B3-G5-parity', b, None, None, 'G5 parity-aware 56.80', 'Does the parity-aware version of G5 pay?', 'C', 'OPEN', 'untested; 56.80 vs lead 57.2365', WF('tighten'), True, CD + ' near-doors', True, 0.44, 'No full pair built; route trace m0,m2,m4,m6,m7 UNSAT in 33 s (the trace only, retest/t6).', potential_bits=0.44, prior=0.08, gain_basis='T')
    A('B3-G5-claim', b, None, None, 'G5 y below 10.79 by tuple choice v2(kappa) = v2(dm7)', 'Can parameter tuples take y below 10.79?', 'C', 'CLAIMED-UNTESTED', 'each bit = 1 bit of score; PROVED criterion + exact counts (claimed)', 'Grok cloud', False, LV + ' row 238', True, 1.0, 'After g5-parity-followup.', potential_bits=1.0, prior=0.05, gain_basis='T')
    A('B3-swap', b, None, None, 'exchange-symmetry swapped solver rows', 'Do swapped rows lower the blake3 cost?', 'Z', 'KILLED', 'claimed -0.19 bit; units bug (4x); corrected best single add +0.193 bit (a loss), all 31 rows +3.10', WF('b3_swap_transfer'), True, 'research/tighten/b3_swap_transfer.md; ' + CD + ' section 5 row 1', True, 0.0, 'LEVERS row DEAD.')
    A('B3-bday', b, None, None, 'birthday lens S1-S9', 'Any blake3 birthday gain?', 'Z', 'KILLED', 'S1 done, S2/S3 Y9 closed [834], S4 k=2 break-even, S5/S6 2^128 per split, S7 31 splits measured, S9 G5 C2 trace UNSAT; S8 out of lens', WF('birthday-lens-sweep'), True, 'research/retest/birthday/SUMMARY.md; research/retest/birthday/blake3_0; blake3_1', True, 0.0, '')
    A('B3-rate', b, None, None, 'step-level rate multiplier (best quarter 1.45x)', 'Can a cheap predictor pick the best steps?', 'C', 'OPEN', 'oracle ceiling 1.44x / -0.55 bit only with free knowledge of lambda; exact counter ~8 s per step', WF('retest t2'), True, 'research/retest/t2/RESULT.md; ' + CD + ' section 5 row 7', True, 0.55, 'Conditional GUESS; noise doubt closed (sd 0.34 real).', potential_bits=0.55, prior=0.05, gain_basis='T')
    A('B3-live', b, None, None, 'liveness of (context, member) group', 'Predict live groups cheaply?', 'Z', 'KILLED', '2400 passing groups, 40.3% live; best single-j0 rule <= 7% dead at recall 0.95 (AUC ~0.5)', WF('pre_blake3_2'), True, LV + ' row 217; research/retest/pre_blake3_2', True, 0.0, 'Sampled 2^10 hull test exact but not costed.')


def parse_atlas_open():
    """Every remaining '?' cell of the ATLAS37 full matrix becomes an OPEN record (no estimate)."""
    have = {(r['row_i'], r['row_j']) for r in OUT if r['hash'] == 'sha256-37'}
    txt = open(os.path.join(WS, 'research', 'tools', 'traillab', 'ATLAS37.md'), encoding='utf-8').read()
    sec = txt.split('## Full matrix', 1)[1].split('## Evidence list', 1)[0]
    n = 0
    for line in sec.splitlines():
        m = re.match(r'\|\s*\*\*(-?\d+)\*\*\s*\|(.*)\|\s*$', line)
        if not m:
            continue
        i = int(m.group(1))
        cells = [c.strip() for c in m.group(2).split('|')]
        for k, c in enumerate(cells):
            j = k - 4
            if '?' not in c or (i, j) in have:
                continue
            labs = [ch for ch in 'DXCSIBPKEZ0' if ch in c.replace('x', '')]
            kind = 'schedule tap' if 'X' in c else 'state read'
            A('S37-Q%d_%d' % (i, j), 'sha256-37', i, j, 'atlas cell (%d,%d) %s' % (i, j, c), 'Direct %s of row %d into row %d with no measured or proved result yet: does it carry a lever?' % (kind, i, j),
              labs, 'OPEN', 'untested ("?" in ATLAS37 full matrix)', TL, False, 'research/tools/traillab/ATLAS37.md (full matrix)', True, None,
              'Generic gap cell exported from the matrix; no estimate. Dense rows 0..13 belong to Zone D.', gain_basis='T')
            n += 1
    return n


if __name__ == '__main__':
    store = add_cell.STORE
    if os.path.exists(store) and os.path.getsize(store) > 0:
        sys.exit('CELLS.jsonl already has records; use add_cell.py')
    run()
    nq = parse_atlas_open()
    seen, bad = [], 0
    for r in OUT:
        e = add_cell.validate(r, seen)
        if e:
            bad += 1
            print('INVALID', r['id'], e)
        seen.append(r)
    if bad:
        sys.exit('%d invalid records; nothing written' % bad)
    with open(store, 'w', encoding='utf-8', newline='\n') as fh:
        for r in OUT:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('wrote', len(OUT), 'records (%d generic atlas "?" cells)' % nq)
