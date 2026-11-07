
# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json, sys, re, os
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
BASE = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming/sha256-37-U02')
W = 'research/dig/incoming/sha256-37-U02/work/'
rows = []
for l in open(os.path.join(BASE, 'work', 'row15_full.txt')):
    m = re.match(r'dropE bit\s+(\d+) sym (\S) : L0 (\d+) \| L1 (\d+) \| L2 (\d+)', l)
    if m and m.group(2) != '=':
        rows.append(tuple(m.groups()))
tab = "; ".join("E15[%s](%s) %s/%s/%s" % r for r in rows)
common = dict(hash='sha256-37', source='our workflow: scan-once', own_test=True, date='2026-10-12', lever=False, gain_bits=None)
recs = {}
recs['sha256-37_r15_E_Q2'] = dict(common, row_i=15, row_j=15,
 object='row15 E15 value/sign cells (bits 4,7,9,11,12,15,16,17,18,19,20,22,26,27,30)',
 question='Q2: drop each E15 cell singly: row-15 local solution count over all 2^32 values of W15, and whether any extra W15 survives the next necessary conditions',
 labels=['D', 'Z'], status='COMPUTED',
 number='Required: L0 (E15+W15 cells, both members; A15 cell holds for every W15) 131,072 = 2^17 of 2^32; L1 (+ dW17=0 and dW30=0 schedule requirements) 4,096 = 2^12; L2 (+ row-16 local requirement X_E16=e7affd56 and X_A16=0) 32 = exactly the 32 l. Dropped, each as L0/L1/L2: ' + tab + '. Bits 30,22,17,12,9 and the + at bit 4 add nothing even at L0 (implied by the rest of the row); bits 27,26,20,19,18,16,15,11,7 double L0 and bits 26,18,16,15,11,7 raise L1, but L2 stays 32 for every drop: no extra W15 survives, no gain.',
 evidence=W + 'row15.c; ' + W + 'row15.py; ' + W + 'row15_full.txt; ' + W + 'backward_15_17.txt',
 notes='Universe cell sha256-37|r15|E|Q2. Own C enumeration (row15.c) of all 2^32 W15; E15y=E15x+dE15 and A15x=A15y are constants of the anchor rows 11..14 (constants from row15.py, own SHA-256 trace, digest checked for both members). Validated on known answers: on the 2^20 subset (mask 00fffff0) it gives cells 512 and drop-E15[7] 1024 exactly as traillab exact does, and at L2 it reproduces the 32 l of chi37 as a derived set (all 32 present, none else). Row-local model with rows 11..14 held (ATLAS37 Limits); extras were not run through rows 17..36, they are removed by the row-16 necessary condition. dropx on n/u bits drops value and sign. The + at bit 4 is the E15[4]=E16[4] relation, see the REL record.')
recs['sha256-37_r15_W_Q2'] = dict(common, row_i=15, row_j=15,
 object='row15 W15 cell u at bit 29 (==u...)',
 question='Q2: drop W15[29] singly: row-15 local count over all 2^32 W15 and the next necessary conditions',
 labels=['D', 'Z'], status='COMPUTED',
 number='Dropping the u at W15[29] while keeping the = at bits 30,31 and dW15=e0000000: L0 131,072 / L1 4,096 / L2 32, identical to the printed cell (131,072 / 4,096 / 32). Implied: x bit 29 = 0 makes y = x + e0000000 differ in bits 29,30,31, so the = at bits 30,31 already force bit 29 = 1. Dropping the whole W15 cell (all of bits 29..31) doubles L0 to 262,144 but L1 stays 4,096 and L2 32.',
 evidence=W + 'row15.c; ' + W + 'row15_full.txt',
 notes='Universe cell sha256-37|r15|W|Q2. Same enumeration and validation as the E record; W15 is a base word with no expansion equation; the 32 l are reproduced at L2. Row-local model with rows 11..14 held.')
recs['sha256-37_r15_REL_Q2'] = dict(common, row_i=15, row_j=18,
 object='row15 relation E15[4]=E16[4] (+ at bit 4 of E15/E16 and its x2 line)',
 question='Q2: drop the relation E15[4]=E16[4] singly: do violators (E15[4]!=E16[4]) survive to the event?',
 labels=['Z'], status='LOCAL_ONLY',
 number='Violators E15[4]!=E16[4] (dropq E16 00000010; dropx2 E15; lin E15[4]^E16[4]=1) pass rows 16 and 17 at the printed rate (accepted 4,118 and 65,673 of 1,048,576 vs 4,113 and 65,511) and die at row 18: accepted 0 of 1,048,576 vs 131,780 for the holders; seeds 1 and 2 both dead, 0 samples reach rows 22..36, EXACT 0. Dropping the relation therefore adds no EXACT sample; dropped/required = 1 on the prefix (violator share at row 18 below 3 in 1,048,576 per seed, rule of three). Control (same drop, relation re-added as lin =0) reproduces the baseline bit for bit: prefix -58.9863, EXACT 323.',
 evidence=W + 'win15.sh; ' + W + 'out_e15z.txt; ' + W + 'out_e15V.txt',
 notes='Universe cell sha256-37|r15|REL|Q2. S37-E7 called it implied (untested): it is not implied by rows 15..17, it is NECESSARY at row 18 (prefix kill, not run to the event because no sample survives). Both copies of the relation are dropped (the + in E16 and the x2 line), as in the R17-d trap. traillab window rows 22 36, event out, np 4096, mt 1024, 2 seeds; pass counts are SMC proposals. No gain.')
recs['sha256-37_r17_E_Q4'] = dict(common, row_i=17, row_j=18,
 object='row17 E17 signed cells u at bits 4 and 18 (dE17=fffbfff0)',
 question='Q4: other signed patterns with the same modular difference of E17: do they propagate to the same later differences?',
 labels=['Z'], status='LOCAL_ONLY',
 number='traillab sdiff: 15 signed patterns of fffbfff0 with weight <= 6 (mass 0.8906): the printed one (u at 18, u at 4, weight 2) plus 14 alternatives (weights 3..6). Each alternative used as the E17 cell (sym E17, other cells and rows as printed): rows 16 and 17 pass (row 17 accepted about 65.5k of 1,048,576 per seed, with 1 to 3 more forced bits), row 18 accepted 0 of 1,048,576 for all 14 on both seeds (printed pattern: 131,780), EXACT 0. None reaches the same later differences. Control (printed pattern via sym) reproduces prefix -58.9863 and EXACT 323.',
 evidence=W + 'sdiff_dE17.txt; ' + W + 'alts.txt; ' + W + 'q4.sh; ' + W + 'out_q4ctl.txt; ' + W + 'out_q4_a1.txt (a1..a14 likewise); ' + W + 'backward_15_17.txt',
 notes='Universe cell sha256-37|r17|E|Q4. Prefix-only (the SMC stops at row 18, so no alternative was run to the output event); rows 18..21 cells stay as printed, so this answers whether the printed later differences are reached, not whether a different characteristic could exist. np 4096, mt 1024, seeds 1,2. Bits where the alternative has a sign override the printed value condition; bits where it has none keep the printed condition. backward also lists signings of E13 for row 17 (22 patterns up to weight 6; only the printed one has Pr 1 under that model).')
recs['sha256-37_r17_REL_Q4'] = dict(common, row_i=17, row_j=19,
 object='row17 relations: E17[0]!=E17[13], E16[24]=E17[24], E16[15]=E17[15], A15[29]=A17[29], A17[29]=A18[29]',
 question='Q4: opposite relation (= vs !=) for each row-17 relation: does it reach the same later differences?',
 labels=['Z'], status='LOCAL_ONLY',
 number='Opposite imposed with the original dropped (both copies for the + relations), np 4096, mt 1024, seeds 1,2, window rows 22..36: E17[0]=E17[13]: dead at row 18 (0 of 1,048,576; holders 131,780). E16[24]!=E17[24]: passes row 18 (130,478 / 129,313), dead at row 19 (0; holders accept 1,048,576). E16[15]!=E17[15]: row 18 131,934 / 130,988, dead at row 19. A15[29]!=A17[29]: dead at row 18. A17[29]!=A18[29]: row 18 130,400 / 131,072, dead at row 19. EXACT 0, no sample reaches rows 22..36 in any of the five. Control (both A-side relations re-added as printed) reproduces prefix -58.9863 and EXACT 323.',
 evidence=W + 'q4.sh; ' + W + 'r17e.sh; ' + W + 'out_r17_a.txt; ' + W + 'out_r17_b.txt; ' + W + 'out_r17_c.txt; ' + W + 'out_r17_d.txt; ' + W + 'out_r17_e2.txt; ' + W + 'out_r17_e0.txt',
 notes='Universe cell sha256-37|r17|REL|Q4. An earlier variant out_r17_e.txt dropped x2 on A17 without re-adding A15[29]=A17[29] (dropx2 A17 removes both lines touching A17) and is superseded by out_r17_e2.txt. Prefix-only; later cells as printed. Relations imposed on member x, as in the R17-c/R17-d sweeps. A15[29]=A17[29] is the corrected reading (REFERENCE_CARD erratum).')
for k, r in recs.items():
    errs = add_cell.validate(r, add_cell.load())
    print(k, errs)
    json.dump(r, open(os.path.join(BASE, k + '.json'), 'w'), indent=1)
