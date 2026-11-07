
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

import json, os, re, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'results.json')))['res']
EV = ('research/dig/incoming2/sha256-38-G02-U04/work/run_all.py; research/dig/incoming2/sha256-38-G02-U04/work/memmodel.py; research/dig/incoming2/sha256-38-G02-U04/work/results.json; '
      'research/dig/incoming2/sha256-38-G02-U04/work/ledger.out (a0lean38.py ledger, copy of pkgR38M3 experiments/a0lean38.py, sha256 b725d37c...); research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/proof.md Section 14')
KA = ('Known-answer first (our scripts): a0lean38.py ledger of pkgR38M3 reproduces N_FB = 5840904760525073226269327, time_log2 = 87.90374 (exact log2(N/C) = 87.9037359544) and memory() reproduces 1,045,792 B (2^19.996165, 2,784 B under 2^20); a re-implementation of the ledger with extra-operation terms reproduces 87.9037359544 at zero extra; sampled P(any class passes F7) = 0.30319 (2e6 draws) vs ledger 1 - HIT0/2^32 = 0.30319. '
      'Convention: r38 proof, 32 B per instruction, 32 B per word (256-bit word RAM). Added operations are counted in the ledger as +dFB per first block, +dVisit per class visit (p7-weighted, K p7 = 6.02 visits per first block), +dW7 per class per W7 test, and also enter the V_MAX cap. ')


def f(x, n=6):
    return ('%+.' + str(n) + 'f') % x


def r(k):
    return R[k]


cells = {}


def add(cell, obj, q, number, notes):
    cells[cell] = dict(id=cell, hash='sha256-38', row_i=None, row_j=None, object=obj, question=q, labels=[], status='COMPUTED', number=number,
                       source='our workflow: scan-once-wave2', own_test=True, evidence=EV, date='2026-10-12', lever=False, gain_bits=None,
                       notes='universe cell %s. ' % cell + KA + notes, topic='sha256-38 memory axis ' + cell.split('|')[1])


O = 'class table of the r38 R38M3 line: 90 classes x (c7, base, mask+program number) = 270 words x 32 B = 8,640 B (proof Section 14)'
add('sha256-38|MEM.CTAB|MEM|M2', O, 'M2: exact ledger time to recompute / stream / shard the table instead of holding it?',
    'Ledger arithmetic, each row an alternative (dS = dT because the shipped B stays under 2^20): (a) pack 8 32-bit values per 256-bit word (30 words = 960 B, saves 7,680 B), priced +2.125 ops per class per W7 test and +3 ops per class visit (no variable shifts exist, so a running shift and mask; a count, no instruction list): dT = %s bit (T = 87.905968); (b) c7 recomputed from base for the 64 classes whose base is itself a member (the 26 added classes: base is not a member; 64 of 90 verified by c7of), 9 counted ops each per first block (+576 ops), saves 2,048 B: dT = %s; (c) whole table regenerated each first block by the exhaustive class scan, LOWER BOUND 2^32 candidates x 9 ops (cheapest member_test path, counted) = 3.9e10 ops per first block: dT = %s bit (T = 106.03); (d) unroll the W7 test per class with c7 as an immediate (-3 ops per class): needs +146,720 B, dT = %s but B = 1,192,512 (2^20.186) so dS = %s. Holding the table costs no S: the shipped total is 2,784 B under the line.'
    % (f(r('CTAB_pack8_per_word')['dT']), f(r('CTAB_c7_from_base_64cls')['dT']), f(r('CTAB_regen_each_FB_lowerbound')['dT'], 3), f(r('CTAB_unroll_W7')['dT']), f(r('CTAB_unroll_W7')['dS'])),
    '(a) and (b) are priced counts under the model (no instruction list from an allocator); (c) is a lower bound on a regeneration (the classes were found by an exhaustive 2^32 scan, class_runs of grok job111; we did not re-run it). Status COMPUTED = ledger arithmetic on stated alternatives, not a measurement of a built program.')
add('sha256-38|MEM.CTAB|MEM|M3', O, 'M3: S-optimal hold-versus-recompute point for the table with the other objects fixed?',
    'HOLD all 270 words. S = time_log2 = 87.90374 at B = 1,045,792 (headroom to 2^20: 2,784 B). Every shrink alternative has dS > 0 (pack8 %s, c7-from-base %s, regenerate +18.1); no alternative that saves bytes lowers S because max(0, log2 B - 20) is already 0. The only S-lowering direction would be spending the 2,784 B headroom, and the table has no use for it (unrolling costs +146,720 B, dS = %s).'
    % (f(r('CTAB_pack8_per_word')['dS']), f(r('CTAB_c7_from_base_64cls')['dS']), f(r('CTAB_unroll_W7')['dS'])),
    'Corner optimum under the stated alternatives; a packing not listed could shift it only if it saved time, and holding is already the time-minimal choice (the tabled loop is the cheapest dispatch we priced).')
add('sha256-38|MEM.CTAB|MEM|M4', O, 'M4: breakpoint at 2^20 B; S on both sides; is crossing worth it?',
    'Exact: S = T + max(0, log2 B - 20); slope above the line 1/(2^20 ln 2) = 1.3755e-6 bit per byte. Shipped B = 1,045,792 < 2^20, S = 87.903736 (no penalty). Holding the 8,640-B table on top of a full 2^20 would cost log2(1 + 8640/2^20) = 0.011839 bit. At the line the packed table (saves 7,680 B = 0.010522 bit, costs %s) would win by 0.0083 bit, but only if the rest of the program were already at or over 2^20; at the shipped point it loses (dS %s). Crossing by unrolling the W7 loop: +146,720 B to 1,192,512 = 2^20.186, S 88.086425 (dS %s): NOT worth it (saves 0.002884 bit of time for 0.18657 bit of memory price).'
    % (f(r('CTAB_pack8_per_word')['dT']), f(r('CTAB_pack8_per_word')['dS']), f(r('CTAB_unroll_W7')['dS'])),
    'Conditional on the other objects: the packed-table trade is a lever only if some other change pushes the total over 2^20 by at least 7,680 B; recorded as an option, not a gain.')

O7 = 'code of the seven plane programs: 9,946 instructions x 32 B = 318,272 B (lengths 1410, 1413, 1421, 1426, 1425, 1426, 1425; classes per program 16, 16, 16, 14, 12, 8, 8)'
dropk = {g: [k for k in R if k.startswith('CODE7_drop_prog%d(' % g)][0] for g in range(7)}
dtxt = '; '.join('prog%d (%s classes) saves %d B, dT %s' % (g, re.search(r'\((\d+)cls', dropk[g]).group(1), -R[dropk[g]]['dB'], f(R[dropk[g]]['dT'], 4)) for g in range(7))
add('sha256-38|MEM.CODE7|MEM|M2', O7, 'M2: exact ledger time to recompute / stream / shard the program code instead of holding it?',
    '(a) keep ONE program resident (max 1,426 instructions = 45,632 B, saves 272,640 B) and regenerate the program on every class visit: LOWER BOUND 1 op per emitted instruction (mean length 1419.7): dT = %s bit (T = 87.992169, B = 773,152); (b) same at the package\'s own generation charge (program generation charged 2^32 ops for the 9,946 instructions = 431,811 ops per instruction): dT = %s bit (T = 102.64); (c) shard by program (drop one program with its classes; ledger with K reduced and P(any class) re-sampled, 6e6 draws): %s. The programs are nearly cost-neutral to drop because per-first-block cost scales with the number of classes: the class count only amortises the fixed part (C + 35 + hit list + scalars and planes, about 2%% of a first block).'
    % (f(r('CODE7_resident1_regen_1op')['dT']), f(r('CODE7_resident1_regen_lump')['dT'], 3), dtxt),
    '(a) is a lower bound that no real generator reaches (the builder is a Python scheduler, not a word-RAM routine); (b) is a bound from the package\'s own lump charge; (c) assumes q3 and the H3 rate are the same per class and uses a sampled P(any class passes F7) (SAMPLED, binomial interval about +-0.0004 at 6e6 draws).')
add('sha256-38|MEM.CODE7|MEM|M3', O7, 'M3: S-optimal hold-versus-recompute point for the program code with the other objects fixed?',
    'HOLD all seven programs. Every alternative has dS > 0: resident-1 regeneration %s (1 op/instr lower bound) / %s (package charge); dropping a program costs %s to %s bit of time for about 45.6 KB. No byte saving lowers S while B < 2^20. Marginal worth of a program: 0.0025 to 0.0091 bit per 45 KB = 5.5e-8 to 2.0e-7 bit per byte, against the price above the line of 1.3755e-6 bit per byte: each program is worth holding only because the line is not crossed.'
    % (f(r('CODE7_resident1_regen_1op')['dS']), f(r('CODE7_resident1_regen_lump')['dS'], 3), f(min(R[k]['dT'] for k in dropk.values()), 4), f(max(R[k]['dT'] for k in dropk.values()), 4)),
    'Corner optimum under the stated alternatives; program lengths and class lists are the shipped ones (not re-optimised).')
add('sha256-38|MEM.CODE7|MEM|M4', O7, 'M4: breakpoint at 2^20 B; S on both sides; is crossing worth it?',
    'Exact: holding all 318,272 B on top of a full 2^20 would cost log2(1 + 318272/2^20) = 0.382421 bit; one program (45,632 B) 0.061456 bit. Shipped B = 1,045,792 is 2,784 B under the line, S = T = 87.903736. Crossing the line by ADDING a program (about 45 KB, 0.0598 bit of memory price) is not worth it: a program carrying 8 to 16 classes is worth 0.0025 to 0.0091 bit of time (7x to 24x too dear). Giving code BACK above the line: dropping program 5 (8 classes, 45,632 B) costs %s bit of time and would save up to 0.061456 bit if the total were over the line (net +0.0589 there). Regenerating all code at the 1 op/instruction LOWER BOUND (+0.0884 bit) would pay against 0.3824 only if the total were over by the full 318 KB, and loses at the package generation charge (+14.7 bit).'
    % f(R[dropk[5]]['dT'], 4),
    'Conditional on being over the line, which the shipped program is not. No gain claimed.')

OO = 'code of the W7 loop and the other routines: 57 instructions (52-instruction tree once + 5 for the loop) = 1,824 B, plus 600 instructions = 19,200 B (the 600 is an allotment, not an instruction list)'
add('sha256-38|MEM.CODEO|MEM|M2', OO, 'M2: exact ledger time to recompute / stream the routine code instead of holding it?',
    '(a) W7 tree not resident, regenerated for each of the 90 tests per first block: LOWER BOUND 52 ops per test (dW7 = +52): dT = %s bit (T = 87.952826), saves 1,824 B; (b) the 600 other-routine instructions streamed once per first block at 1 op per instruction (dFB = +600, an upper count of what executes per first block, lower-bound price per op): dT = %s bit, saves 19,200 B; (c) both: dT = %s bit (B = 1,024,768). At the package generation charge (431,811 ops per instruction) these would be about 2.2e7 per test and 2.6e8 per first block: not worth pricing further.'
    % (f(r('CODEO_W7_tree_regen_52')['dT']), f(r('CODEO_other600_regen_each_FB')['dT']), f(r('CODEO_all_regen')['dT'])),
    'Bounds: 1 op per emitted instruction is below any real generator; the 600 figure is the proof allotment (no instruction list), so (b) over-counts if some routines run only on hits.')
add('sha256-38|MEM.CODEO|MEM|M3', OO, 'M3: S-optimal hold-versus-recompute point for the routine code with the other objects fixed?',
    'HOLD both. dS = dT > 0 for all three alternatives (+0.049090, +0.006388, +0.055264) because B stays under 2^20 and the S memory term is 0.',
    'Corner optimum; exact under the stated alternatives, bounds as in M2.')
add('sha256-38|MEM.CODEO|MEM|M4', OO, 'M4: breakpoint at 2^20 B; S on both sides; is crossing worth it?',
    'Exact: 21,024 B on top of a full 2^20 would cost log2(1 + 21024/2^20) = 0.028640 bit; the 19,200-B routine block alone 0.026178 bit; the 1,824-B W7 loop code 0.002507 bit. Shipped total is under the line (S = T), so no cost now. Above the line only the 600-instruction block could pay to stream (+0.006388 bit at the 1 op/instruction lower bound against 0.026178 saved); the W7 loop code never (+0.049090 vs 0.002507). At the shipped point 2,784 B of headroom remain, absorbing loop-code growth up to 87 instructions (proof Section 14).',
    'Conditional on being over the line; lower-bound pricing of streaming.')

ex = add_cell.load()
for cell, rec in cells.items():
    fn = os.path.join(os.path.dirname(HERE), re.sub(r'[^A-Za-z0-9]+', '_', cell).strip('_') + '.json')
    json.dump(rec, open(fn, 'w', encoding='utf-8'), indent=1)
    print(os.path.basename(fn), add_cell.validate(json.load(open(fn, encoding='utf-8')), ex))
