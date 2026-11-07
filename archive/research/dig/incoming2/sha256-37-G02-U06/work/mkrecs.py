
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
out = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G02-U06')
EV = ('research/dig/incoming2/sha256-37-G02-U06/work/ (lowm_w.py = scratch copy of pkgR37M3 experiments/lowm.py with one added zero constant EXTRA_L; '
      'variants.py, variants2.py, tally.py; scant_results.json, perscal_results.json)')
COMMON = (" Known-answer check first: scratch ledger reproduces time_log2 60.99099 and memory 607,744 B = 2^19.2131 (lowm.py ledger / memory). "
          "Convention: proof.md Section 14.1, words of 32 B, code bound 65,536 B (8192 primitives x 8 B; the r37 convention, not 32 B per instruction). "
          "Score S = time_log2 + max(0, log2 B - 20); the shipped total is below 2^20, so memory costs 0 in S today and headroom is 440,832 B. "
          "Ledger arithmetic on the closed-form ledger only: no straight-line text was written or run for any variant, no register allocation done. ")


def rec(cell, obj, q, num, notes, lever=False, gain=None):
    kind = cell.split('|')[1]
    m = cell.split('|')[3]
    r = dict(hash='sha256-37', row_i=None, row_j=None, object=obj, question=q, labels=['N' if lever else 'Z'], status='COMPUTED',
             number=num, source='our workflow: scan-once-wave2', own_test=True, evidence=EV, date='2026-10-12', lever=lever,
             gain_bits=gain, topic='sha256-37.mem.' + kind.split('.')[1].lower() + '.' + m.lower(),
             notes='universe cell ' + cell + '. ' + notes + COMMON)
    if lever:
        r['gain_basis'] = 'S'
    fn = cell.replace('|', '_').replace('.', '_') + '.json'
    json.dump(r, open(os.path.join(out, fn), 'w', encoding='utf-8'), indent=1)


P = 'sha256-37|MEM.'
rec(P + 'SCANT|MEM|M2', 'lane-scan table (ctz table, 2048 words = 65,536 B)', 'M2: exact ledger time to recompute / stream the table instead of holding it',
    'Table-free lowest-set-bit index (c&(c-1), c^nc, b-1, SWAR popcount; identity checked on all 65,535 16-bit chunks and 2e5 random 64-bit words, 0 mismatches) prices SCAN_LANE 21, CLS_LANE 19, SURV_LANE 20 (chunk 11): time +0.0951 bit (61.08613); best table-free chunk 16: +0.0829 bit (61.07393, SCAN_FIX 46); chunk 64: +0.1017. Small tables instead: 256-entry table (8,192 B, chunk 8) +0.0129 bit; 64-entry (2,048 B, chunk 6) +0.0337. Memory after dropping: 542,208 B (exact). Streaming is not applicable: reads are data-dependent random accesses inside the hot loop.',
    'The table is used 3 ways in the ledger: class-plane scan (CLS_LANE), rep scan (SCAN_LANE) and survivor-mask scan (SURV_LANE). Chunk-width formulas for SCAN_FIX/SURV_FIX reproduce 70 and 8 at width 11 before use. No ctz/popcount primitive is assumed (the cost model lists none); immediates are free as in the shipped ledger.')
rec(P + 'SCANT|MEM|M3', 'lane-scan table (2048 words = 65,536 B)', 'M3: S-optimal hold-versus-recompute point for the scan table, others fixed',
    'S-optimal: hold a table of chunk width 13 (8192 words = 262,144 B; total 804,352 B < 2^20): SCAN_FIX 70 -> 58 (5 chunks per 64-bit part instead of 6): time_log2 60.98614 (-0.00485 bit), S 60.98614 vs 60.99099 shipped. Width 12: no change. Width 14 same time with total 1,066,496 B (S 61.01059); width 16 (2,097,152 B) time 60.97796 (-0.0130) but S 62.30972. Dropping the table is never S-optimal: every table-free point is worse by 0.083 to 0.10.',
    'Lever flagged: 0.00485 bit, derived by changing two scan-fix constants in the ledger (hand-derived formula, verified to reproduce 70 and 8 at width 11), not run as straight-line text. Per-lane cost 8 unchanged; the table must be rebuilt (preprocessing 8192 x 6 is far below the 2^38 allowance).',
    lever=True, gain=0.00485)
rec(P + 'SCANT|MEM|M4', 'lane-scan table (2048 words = 65,536 B)', 'M4: breakpoint at 2^20 B, S on both sides, is crossing worth it',
    'Crossing 2^20 with the scan table is not worth it: width 14 (total 1,066,496 B, 0.0245 bit above 2^20) S 61.01059 vs 60.98614 at width 13; width 15 S 61.58745; width 16 S 62.30972. Slope just above 2^20 is 1.376e-6 bit per byte (1.4427 bits per doubling). Hold-vs-drop flips only if the rest of the program exceeds B* = 65,536/(2^0.0829 - 1) = 1,107,588 B (2^20.08) against the best table-free variant; against the 8 KiB table the flip is at 6.37e6 B. Both sides of the shipped point are under 2^20, where the table is free to hold.',
    'Crossing needs the program to be 440,832 B larger first; nothing in this unit grows that much.')
rec(P + 'PERL|MEM|M2', 'per-l constants (32 x 4 words = 4,096 B) and L*/cells/S (bound 1280 words = 40,960 B)', 'M2: exact ledger time to recompute the constants / L* / S instead of holding them',
    'Per-l constants C_l, cxA_l, E15x_l, VA_l recomputed per exact row-16 test from x15 = LW15[l] and l-independent rows 12..14 (a15 = A15b + x15, e15 = E15b + x15, cxA = S0(a15)+maj+const, C = Cfix+S1(e15)+CH, VA = 3 ops): 31 ops replace the 8 load ops, EX_OPS 34 -> 57; known-answer: all 32 l reproduce LC and VA exactly (0 mismatches). Time +0.03434 bit (61.02533), memory 603,648 B. L*/S recomputed from CV0, MX, MY, LW15 (40+32 words kept) at each rare entry: 792 ops per entry plus 67 per l (33 ops per member-row, 24 common rows, 2 rows per l): +0.00509 bit (60.99609). Both: +0.03931 bit. Cells: 26 nonzero cell words + 21 two-bit relations on rows 16..36 are the characteristic itself (advice), not recomputable.',
    'M1 note: per-l constants 4,096 B exact. The 1280-word bound for cells/L*/S is a bound: a count of the data the model reads at run time (cells, S, per-l rows 12..15 of both members, MX, MY, LW15) is about 768 words = 24,576 B. The ledger charges these constants as immediates (no loads), so the recompute cost is purely additive.')
rec(P + 'PERL|MEM|M3', 'per-l constants and L*/cells/S', 'M3: S-optimal hold-versus-recompute point for this object, others fixed',
    'Hold everything: S = 60.99099 at 607,744 B. Dropping the per-l constants gives S 61.02533 (+0.0343); dropping L*/S to seeds gives S 60.99609 (+0.0051); the memory saved is worth 0 in S because the total stays below 2^20. No gain lever here.',
    'The bound 40,960 B could be tightened to about 24,576 B (data count) with no effect on S.')
rec(P + 'PERL|MEM|M4', 'per-l constants and L*/cells/S', 'M4: breakpoint at 2^20 B, is crossing worth it',
    'Hold-vs-recompute flips (S above 2^20) only if the rest of the program exceeds B* = b/(2^dT - 1): per-l constants 170,063 B (below 2^20, so hold even above 2^20); L*/S to seeds (38,656 B saved) 10.9e6 B (2^23.4), 6.3e6 B with the data-count version. The constants are held on both sides of 2^20 up to a very large program.',
    'Neither side of the shipped point crosses 2^20.')
rec(P + 'SCAL|MEM|M2', 'scalar planes (96 words = 3,072 B), cv_pre constants + first-block buffer (64 words = 2,048 B)', 'M2: exact ledger time to recompute / stream instead of holding',
    'Scalar planes (zq 17, zKZ 29, zCB3 32, zb 18) generated at point of use in each sweep (3 ops per plane, 2 for plane 0, as the class test already does for -x) instead of generated once, stored and reloaded: per class 410 -> 17, SWEEP_OVH 195 -> 272 (zq kept stored): time -0.01343 bit (60.97756), memory 605,216 B; dropping the 17 per-block zq planes as well: -0.01324. cv_pre recomputed per group of four (81 ops) instead of held: +0.22603 bit. First-block buffer: needed only to print the collision, regenerated from the RNG state in about 30 ops once per hit, not ledgered.',
    'Needs the 4 scalars (q, CB3, KZ, base) in registers during a sweep: about 40 live planes + 8 addresses + 4 is 52 of 64 by the proof count, not checked by a register allocation. The 64-word line also holds the register file and compression state (proof 14.1 last row), a bound that cannot be recomputed.')
rec(P + 'SCAL|MEM|M3', 'scalar planes, cv_pre constants, first-block buffer', 'M3: S-optimal hold-versus-recompute point for this object, others fixed',
    'S-optimal: regenerate the class scalar planes at use (S 60.97756, 605,216 B, -0.01343 bit vs shipped 60.99099); keep cv_pre held (recompute per group +0.226 bit). Store-and-reload is dominated by direct generation: with s sweeps per class the store route costs 3+2+2s ops per plane, direct 3s; direct wins at s = 1 and s = 4, the only values in the class types.',
    'Lever flagged: 0.01343 bit, a time AND memory gain at once, from ledger arithmetic only; the constants changed are FB_DET/cprep/SWEEP_OVH (hand-derived: 410 -> 17, 195 -> 272) and need a straight-line rewrite plus register check before any filing.',
    lever=True, gain=0.01343)
rec(P + 'SCAL|MEM|M4', 'scalar planes, cv_pre constants, first-block buffer', 'M4: breakpoint at 2^20 B, is crossing worth it',
    'No breakpoint for the scalar planes: direct generation lowers both time and memory, so it wins on both sides of 2^20. cv_pre: hold flips only above B* = 2,048/(2^0.226 - 1) = 12,075 B of other memory, i.e. always hold. Crossing 2^20 is never reached here.',
    'The two items of this object cost 5,120 B of the 440,832 B headroom.')
