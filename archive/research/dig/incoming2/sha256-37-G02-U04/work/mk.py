
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

import json, os
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G02-U04')
EV = 'research/dig/incoming2/sha256-37-G02-U04/work/variants.py; research/dig/incoming2/sha256-37-G02-U04/work/lowm.py (scratch copy of pkgR37M3 lowm.py; ledger and memory reproduce time_log2 60.99099 and 607,744 B = 2^19.2131)'
common = dict(hash='sha256-37', row_i=None, row_j=None, source='our workflow: scan-once-wave2', own_test=True, evidence=EV, date='2026-10-12', lever=False, gain_basis='S')
obj = {
 'REGS': ('plane registers (64-register budget)', 1024, 25088*0+0, 'REGS32_one_batch_sweep', 0.014542523571172694, 61.00554, 'one batch per sweep (about 28 live planes, fits 32 registers), SWEEP_OVH (195 ops) paid per batch instead of per two batches; nsw=nb in class_det. Saves 1,024 B of the 2,048 B register file. The 16-register or spilling variant and the subtraction-run live set (stated about 45 planes) are NOT priced (bound only: the sums are reloaded bit by bit anyway, so the live set may be lower).'),
 'PLANES': ('planes of the reps (8x14 + 42x16)', 25088, 0, 'PLANES_recompute_per_batch_use', 1.2012320814782598, 62.19223, 'rebuild the (17-k) bit planes of each batch from the packed entries at every use: (17-k)*256*3 + 64 ops replacing the 2*(17-k) plane loads (naive bit insertion priced as in proof 14.2 (iii); a log-step transpose would be cheaper, not tried)'),
 'ENTRIES': ('packed entries of the reps (50 batches x 64 words)', 102400, 0, 'ENTRIES_recompute_per_lane', 0.30273983938950266, 61.29373, 'rebuild the entry word of each scanned lane from the planes (3 ops per plane for s, 11 for S0, 2 to pack, minus the 1 load): +3*(17-k)+12 ops per scan lane in every run of a class; vmax_fb included'),
}
def put(cell, rec):
    rec.update(common); rec['notes'] = 'universe cell ' + cell + '. ' + rec['notes']
    f = os.path.join(D, cell.replace('|', '_') + '.json')
    json.dump(rec, open(f, 'w', encoding='utf-8'), indent=1)
for key, (name, bytes_, _, var, dbits, tl, desc) in obj.items():
    cell = lambda m: 'sha256-37|MEM.%s|MEM|%s' % (key, m)
    # M2
    put(cell('M2'), dict(object='MEM.%s (%s) recompute instead of hold' % (key, name), question='M2: exact ledger time to recompute / stream instead of holding',
        labels=['N'], status='COMPUTED', number='time_log2 %s -> %s (+%.5f bits, exact ledger under the stated model; convention: r37 ledger primitives, code 8 B/primitive bound as shipped); frees %d B' % ('60.99099', tl, dbits, bytes_),
        topic='sha256-37 MEM.%s M2' % key, gain_bits=-dbits, notes='Variant of pkgR37M3 lowm.py ledger, known answer reproduced first (time_log2 60.99099, 607,744 B). Variant: ' + desc + ' Program of the variant not built or run; ledger arithmetic only (COMPUTED, model-exact, not a shipped program).'))
    put(cell('M3'), dict(object='MEM.%s S-optimal hold-versus-recompute point' % key, question='M3: S-optimal point with the others fixed',
        labels=['Z'], status='COMPUTED', number='hold: S = 60.99099 (memory 2^19.2131 B < 2^20 so the memory term is 0); recompute: S = %s; hold is S-optimal by %.5f bits' % (tl, dbits),
        topic='sha256-37 MEM.%s M3' % key, notes='Because total memory 607,744 B is under 2^20 B the clamp max(0, log2 B - 20) is 0 and freeing %d B gains 0 in S while the recompute costs time; see M2 note for the variant. No S gain; free headroom to 2^20 is 440,832 B.' % bytes_))
    put(cell('M4'), dict(object='MEM.%s breakpoint at 2^20 B' % key, question='M4: S on both sides of 2^20 B, is crossing worth it',
        labels=['Z'], status='COMPUTED', number='program is at 2^19.2131 B, 440,832 B below 2^20; S = T on this side (60.99099); beyond 2^20 each doubling of bytes costs 1 bit of S; this object holds %d B and cannot be grown to save time (it is already resident); crossing is not worth it' % bytes_,
        topic='sha256-37 MEM.%s M4' % key, notes='S slope above 2^20: +log2(B/2^20) bits; crossing pays only if a larger table saves more than that many bits of time. Nothing in this object trades bytes for time above the hold point (the held form is the fast form). Window: only for the r37 table-free program pkgR37M3.'))
