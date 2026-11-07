
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

import json, re, os, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
W = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming/sha256-37-U01')
txt = open(os.path.join(W, 'work', 'out_row14.txt')).read()
blocks = re.split(r'\n\n(?=[AEW]14\[)', txt)
info = {'A': [], 'E': [], 'W': []}
for b in blocks[1:] if False else blocks:
    m = re.match(r'([AEW])14\[(\d+)\] \'(.)\'', b)
    if not m: continue
    k, bit, sym = m.group(1), int(m.group(2)), m.group(3)
    loc = re.search(r'variants\):((?: \S+)+)', b).group(1).split()
    cnt = re.search(r'dropped \(P0, variants\):((?: \d+)+)', b).group(1).split()
    cons = re.search(r'C consistent bit-flip \(P0\): cons(\d)', b).group(1)
    d = re.search(r'D relaxed.*?: (\d+) total passing .*?extras (\d+); consistent (\d+); dmod<=15 kept (\d+); rows<=15 ok \(dropped conds\) (\d+); full-path EXACT (\d+)', b)
    info[k].append(dict(bit=bit, sym=sym, loc=loc[0], locall=len(set(loc)) == 1, cnt=cnt[0], cntall=len(set(cnt)) == 1, cons=cons, tot=int(d.group(1)), extras=int(d.group(2)), consistent=int(d.group(3)), ok15=int(d.group(5)), exact=int(d.group(6))))
def j(L): return ','.join(str(x['bit']) for x in L)
common_ev = 'research/dig/incoming/sha256-37-U01/work/out_row14.txt; research/dig/incoming/sha256-37-U01/work/zoneD14.c; research/dig/incoming/sha256-37-U01/work/out_row8.txt (validation)'
base = dict(hash='sha256-37', row_i=14, row_j=None, status='LOCAL_ONLY', source='our workflow: scan-once', own_test=True, evidence=common_ev, date='2026-10-12', lever=False, gain_bits=0.0, gain_basis='q3',
            question='Q2 necessity for row 14 of chi37: drop each printed condition singly; row-local solution count (dense row) and whether the event survives on the full path.')
validn = ('Tool research/dig/incoming/sha256-37-U01/work/zoneD14.c = zoneD.c helpers unchanged + new row-generic drop-one code; validated on row 8 (known answers from zoneD local.out/fwd.out: whole-row-8 count 8 on all 6 bases, A8[30,29,21,16,11,4] break A9; unmodified-anchor rebuild reproduces P0 incl. EXACT=1). '
          'Method: (A) flip bit in both members, hold the rest, first row<=15 whose modular difference breaks (P0 + 5 A0-variants); (B) row-local count: E14^x candidates (2^9 with the E value bits fixed, 2^10 when an E value bit is dropped), rows<10..13 held, whole-row-14 conditions with the one condition removed; (C) bit flip rebuilt with tl_build with the flipped row as anchor (W14: wx[14] flip); (D) every extra solution of the relaxed row (up to 256) rebuilt consistently with tl_build (anchor row 14 replaced) and checked rows<=15, 16..22, 23..36, EXACT. '
          'Baseline: the dense row has 8 row-14 solutions on all 6 bases (published + 7 others); the 7 others already fail rows<=15 (row 15) and EXACT, so the full path has 1 member.')
# A
A = info['A']
recA = dict(base, object='row14 A cells A14[15,23,25] drop-one', labels=['Z'],
    number='A14[15], [23], [25]: dropping any one leaves the row-14 dense-row count at 8 (baseline 8, all 6 bases): implied by the E14/W14 cells + step equation. Local flip breaks A14 itself on all 6 bases (NECESSARY as event condition). Consistent bit-flip: y not anchor-consistent (cons0), rows<=15 fail, EXACT 0. All 7 non-published row solutions (baseline = relaxed): consistent but 0 of 7 pass rows<=15, EXACT 0.',
    notes='Universe cell sha256-37|r14|A|Q2. ' + validn + ' Row 14 is anchor-held (Pr 1); nothing here is a cost. Not rerun: S37-ZDOWN-04..13, anchor Pr 1. LOCAL_ONLY: single-row perturbation on P0 + 5 A0-variants, full path checked on P0 only.')
# E
E = info['E']
e_break15 = [x for x in E if x['loc'] == 'E15']; e_break14 = [x for x in E if x['loc'] == 'E14']; e_none = [x for x in E if x['loc'] == '-']
e16 = [x for x in E if x['cnt'] == '16']; e8 = [x for x in E if x['cnt'] == '8']; e12 = [x for x in E if x['cnt'] == '12']
assert all(x['locall'] and x['cntall'] for x in E)
print('E break15', j(e_break15), 'break14', j(e_break14), 'none', j(e_none), '16:', j(e16), '12:', j(e12), '8:', j(e8))
assert all(x['cons'] == '0' and x['ok15'] == 0 and x['exact'] == 0 for x in E + info['W'] + A)
recE = dict(base, object='row14 E cells E14 value/sign bits (23) + plus bits 30,17 drop-one', labels=['K', 'Z'],
    number=('Local flip (both members, rest held), first break row<=15 on all 6 bases: E14 itself for bits %s (n/u difference bits); E15 for bits %s; none for bit %s (not needed in rows<=15). '
            'Row-local count (baseline 8) with the condition dropped: 16 for bits %s (+ plus-bit 30, i.e. one extra free bit); 8 (unchanged, implied) for bits %s; plus-bit 17 gives 12. '
            'Consistent bit flip: all 25 give cons0 (y not anchor-consistent), rows<=15 fail, EXACT 0. Extra solutions of each relaxed row (up to 15): consistent, 0 pass rows<=15, EXACT 0 for all. Event does not survive dropping any of them; no gain.')
           % (j(e_break14), j(e_break15), j(e_none), j(e16), j(e8)),
    notes='Universe cell sha256-37|r14|E|Q2. ' + validn + ' The plus relations E14[30], E14[17] were measured too (not in the asked list). Row 14 is anchor-held (Pr 1). Not rerun: S37-ZDOWN-04..13. LOCAL_ONLY: single-row perturbation on P0 + 5 A0-variants, full path on P0 only.')
# W
Wd = info['W']
w16 = [x for x in Wd if x['cnt'] == '16']; w8 = [x for x in Wd if x['cnt'] == '8']
assert all(x['loc'] == '-' for x in Wd)
print('W16', j(w16), 'W8', j(w8))
recW = dict(base, object='row14 W cells W14 bits 1,3,9,11,13,18,20,22,26,30 drop-one', labels=['K', 'Z'],
    number=('Local flip (x flipped, dW kept, rest held): no row<=15 breaks for any of the 10 bits on all 6 bases (not needed in rows<=15). Row-local count (baseline 8) with the condition dropped: 16 for bits %s (not implied by the E/A cells); 8 (implied) for bits %s. '
            'Consistent flip (wx[14] flipped, tl_build): all 10 inconsistent (cons0), expansion differences change (exp0), rows<=15 fail, EXACT 0. Extra solutions of each relaxed row: consistent, 0 pass rows<=15, EXACT 0. W14 bits are necessary for the event on the full path (W14 feeds W16 s1, W21, W29, W30) though not in the rows<=15 local model.')
           % (j(w16), j(w8)),
    notes='Universe cell sha256-37|r14|W|Q2. ' + validn + ' Row 14 is anchor-held (Pr 1). Not rerun: S37-ZDOWN-04..13. LOCAL_ONLY: single-row perturbation on P0 + 5 A0-variants, full path on P0 only.')
for nm, rec in (('sha256-37|r14|A|Q2', recA), ('sha256-37|r14|E|Q2', recE), ('sha256-37|r14|W|Q2', recW)):
    fn = os.path.join(W, nm.replace('|', '_') + '.json')
    json.dump(rec, open(fn, 'w', encoding='utf8'), indent=1)
    add_cell.validate(json.load(open(fn, encoding='utf8')), add_cell.load())
    print('ok', fn)
