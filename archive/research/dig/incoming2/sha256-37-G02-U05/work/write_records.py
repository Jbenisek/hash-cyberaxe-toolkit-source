
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

import json, sys, os, re
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G02-U05')
EV = ('research/dig/incoming2/sha256-37-G02-U05/work/m_scan.py; research/dig/incoming2/sha256-37-G02-U05/work/m_scan_out.json; '
      'research/tools/build_pkg/scratch/pkgR37M3/pkg/sha256-r37/proof.md Section 14.1; copy of lowm.py in work/')
KNOWN = ('Known-answer check passed first: lowm.py ledger reproduces time_log2 60.99099 (N = 6058690054895037231741, C = 2644) and lowm.py memory reproduces 607,744 B = 2^19.2131 (r37 convention, 1 primitive per 256-bit op, rotation = 1, code bound 8192 x 8 B = 65,536 B). ')
HEAD = 440832
recs = {}


def add(cell, q, question, number, notes, labels, topic):
    recs[cell + '|' + q] = dict(
        hash='sha256-37', row_i=None, row_j=None, id=cell + '|' + q, object=cell.split('|')[1] + ' memory object (pkgR37M3 ledger)',
        question=question, labels=labels, status='COMPUTED', number=number, source='our workflow: scan-once-wave2', own_test=True,
        evidence=EV, date='2026-10-12', lever=False, gain_bits=None, topic=topic,
        notes='universe cell ' + cell + '|' + q + '. ' + KNOWN + notes)


c = 'sha256-37|MEM.CUBE|MEM'
add(c, 'M2', 'Exact time (log2 T units) to recompute or stream the cube entries D[c] (256 B) and the sum spill area (7,168 B) instead of holding them?',
    'D[c] (256 B): recompute D[cu] = cu | S0(cu)<<32 as 3 rot + 2 xor + shift + or = 7 primitives instead of address+load = 2, RUN_CU 7 -> 12: T +0.001137 bit (log2 T 60.990989 -> 60.992127; vbar +78.5 ops/FB); with rotation priced as 3 primitives: +0.002500 bit. Spill (7,168 B): (A) recompute the main W6 sums for every subtraction run: +0.10669 bit (vbar +7,642.6); (B) one-batch sweeps, sums kept in registers (no spill, SWEEP_OVH once per batch): +0.000504 bit (vbar +34.8). Both objects dropped via (B): +0.001641 bit. All exact within the ledger model; (B) rests on the package-style live-plane count (32 sums + control < 64 registers), not a register allocation.',
    'Spill: class_det rewritten in work/m_scan.py (det_A, det_B) and fed to lowm.ledger; D[c]: RUN_CU patched. vmax_fb is recomputed through the same class_det. Bytes saved: 256 + 7,168 = 7,424 of 607,744.',
    ['N'], 'sha256-37.mem.cube.recompute')
add(c, 'M3', 'S-optimal hold-versus-recompute point for the cube entries and spill area, others fixed?',
    'HOLD both. S = time_log2 + max(0, log2 B - 20) = 60.990989 + 0 at B = 607,744 B (2^19.2131 < 2^20). Any recompute lowers B but the memory term is already 0, so S can only rise: best alternative (spill streamed, B) 60.991494 (+0.000504), D[c] recompute 60.992127 (+0.001137), worst (A) 61.097678 (+0.1067). S-optimal point is hold-all, S = 60.990989.',
    'The decision is forced by the 2^20 free threshold, not by the size of the saving. Streaming is a pure loss of 0.0005-0.1 bit unless B were above 2^20.',
    ['Z'], 'sha256-37.mem.cube.optimum')
add(c, 'M4', 'Breakpoint at 2^20 B for the cube/spill objects: S on both sides and is crossing worth it?',
    'Whole program 607,744 B sits 440,832 B (factor 1.7255, 0.7255 bit of memory) below 2^20. Dropping the cube objects (-7,424 B -> 600,320 B) does not cross anything: memory term stays 0, S rises by +0.0005 to +0.108 bit. Crossing upward would need +440,832 B (59.4 x the 7,424 B of these objects) and each doubling above 2^20 costs +1 bit of S; the objects give no time back for that. Not worth crossing in either direction.',
    'Breakpoint arithmetic only, B_total = 607,744 B from lowm.py memory.',
    ['Z'], 'sha256-37.mem.cube.breakpoint')

c = 'sha256-37|MEM.C7PL|MEM'
add(c, 'M2', 'Exact time to recompute the c7 planes (32 words, 1,024 B) per first block instead of holding them?',
    'Rebuild per first block from the 222 stored c7 words by a 32x32 delta-swap transposition run on 8 lanes of 32 bit at once: 480 primitives (5 stages x 16 pairs x 6; verified: output words equal the 32 held planes for all 32 planes) + 222 loads + 222 address adds + 222 lane inserts = 1,146, minus the 63 now spent loading the planes = +1,083 primitives per first block (FIXED 615 -> 1,698): T +0.015633 bit (log2 T 60.990989 -> 61.006623, time_log2 61.00663). Saves 1,024 B. The 222 loads and inserts are hand-counted (1 primitive each), the network count 480 is exact for the code run in work/m_scan.py.',
    'Estimate class: exact for the network and the ledger arithmetic, hand-priced for the gather. It still reads the c7 words of the class descriptors (28,416 B) held.',
    ['N'], 'sha256-37.mem.c7pl.recompute')
add(c, 'M3', 'S-optimal hold-versus-recompute point for the c7 planes, others fixed?',
    'HOLD. S = 60.990989 held (B = 607,744 B < 2^20, memory term 0); recompute gives S = 61.006623 (+0.015633 bit) at B = 606,720 B, still memory term 0. Hold is optimal.',
    'Memory term is zero on both sides.', ['Z'], 'sha256-37.mem.c7pl.optimum')
add(c, 'M4', 'Breakpoint at 2^20 B for the c7 planes: S on both sides and is crossing worth it?',
    'Objects are 1,024 B; program is 440,832 B below 2^20, so the planes could grow 431 x before crossing, and removing them (606,720 B) crosses nothing. Both sides have memory term 0: S 60.990989 held vs 61.006623 recomputed. Crossing is irrelevant for this object.',
    'Breakpoint arithmetic only.', ['Z'], 'sha256-37.mem.c7pl.breakpoint')

c = 'sha256-37|MEM.CHUNK|MEM'
add(c, 'M2', 'Exact time to replace the two 4096-word chunk tables LO and MID (262,144 B, two reads per lane) by recomputation?',
    '(a) Drop the tables and run the exact row-16 test (EX_OPS = 34, +1 counter) for all 32 l on every probed lane, replacing the probe (47 per group) and the survivor path: vbar 46,070.1 -> 965,458.4 ops/FB, T +3.3553 bit (time_log2 64.34633). Exact within the ledger. (b) ESTIMATE, hand-priced: SIMD prefilter across l (4 words x 8 lanes): 41 primitives per lane + exact tests of the 8 l of each word that shows a zero lane (about 34.8) = 75.8 per lane against 17.6 now (probe 11.75 + survivors 5.85): vbar 94,584.4, T +0.5726 bit (time_log2 61.56364). The filter itself was checked against the tables: 0 mismatches in 60,000 random u (5,431 nonzero against 5,440 expected). Neither (a) nor (b) changes vmax_fb in the patch (worst case already has every l survive).',
    'Bytes saved 262,144; B -> 345,600 in both. Convention r37 (one primitive per 256-bit op). Zero-lane detect priced at 4 primitives per word ((t-1) & ~t & high bits, false positives ignored).',
    ['N'], 'sha256-37.mem.chunk.recompute')
add(c, 'M3', 'S-optimal hold-versus-recompute point for the chunk tables, others fixed?',
    'HOLD both tables. S = 60.990989 held (B = 607,744 B, memory term 0). Dropping both: S = 61.563632 (SIMD prefilter, estimate) or 64.346322 (exact test on all 32 l), at B = 345,600 B with memory term 0. Intermediate points (one table kept) were not computed: the memory term is 0 at every B below 2^20, so holding the most is optimal; this makes the all-hold point the optimum without a scan.',
    'Intermediate (LO-only / MID-only) variants not priced; the argument does not need them.', ['Z'], 'sha256-37.mem.chunk.optimum')
add(c, 'M4', 'Breakpoint at 2^20 B for the chunk tables: S on both sides and is crossing worth it?',
    'The tables are 43.1 percent of the 607,744 B program; below 2^20 by 440,832 B, i.e. room for 3.36 more tables of 4096 words (131,072 B) at memory term 0. Dropping both crosses nothing (345,600 B): S rises to 61.5636 (estimate) / 64.3463 (exact). Crossing 2^20 upward would cost +1 bit per doubling; a third table (bit 30 / carry) was NOT priced here, so no gain is claimed.',
    'Headroom statement; no growth variant measured.', ['Z'], 'sha256-37.mem.chunk.breakpoint')

env_known = add_cell.load()
for cell, r in recs.items():
    fn = os.path.join(D, re.sub(r'[^A-Za-z0-9._-]', '_', cell) + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    add_cell.validate(json.load(open(fn, encoding='utf-8')), env_known)
    print('ok', fn)
