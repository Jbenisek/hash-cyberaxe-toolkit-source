
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

import json, os, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G02-U01')
EV = ("research/dig/incoming2/sha256-38-G02-U01/work/g02_ledger38.py; research/dig/incoming2/sha256-38-G02-U01/work/g02_lib.py; research/dig/incoming2/sha256-38-G02-U01/work/g02_main.py; "
      "research/dig/incoming2/sha256-38-G02-U01/work/g02_schemes.py; research/dig/incoming2/sha256-38-G02-U01/work/main.out; research/tools/build_pkg/scratch/pkgR38d/work/src/ledger38d.py (ledger, copied and parametrised)")
KA = ("Known-answer check passed first (our g02_ledger38.py, a parametrised copy of pkgR38d ledger38d.py): k=0 reproduces time_log2 71.43541, memory 2^80.95526920 B (words 73251135004833792023924 x 32 B), S 132.39067251; "
      "D126 shard model at k=19 reproduces memory 4470913155625365120 B exactly, time_log2 88.21101, S 130.16627565 (D126 130.16627565; ours differs at 1e-8 bit in N_G). "
      "Convention: ledger words of 32 B; code is not in the r38d ledger bytes (proof says about 2^23 B); where code is added it is named. Pricing note: the D126 k=19 number only reproduces if the 256-block sentinel iteration is divided by B with the table (NB/B per group); the strict reading (all 256 sentinel iterations kept per group) gives best S 130.47885 at k=19; both shown. ")
def rec(cell, obj, q, number, lever=False, gain=None, notes=''):
    h = cell.split('|')[0]
    r = dict(id=cell, hash=h, row_i=None, row_j=None, object=obj, question=q, labels=[], status='COMPUTED', number=number,
             source='our workflow: scan-once-wave2', own_test=True, evidence=EV, date='2026-10-12', lever=lever, gain_bits=gain,
             notes='universe cell %s. %s%s' % (cell, KA, notes))
    if lever: r['gain_basis'] = 'S'
    fn = os.path.join(D, cell.replace('|', '_').replace('.', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    add_cell.validate(json.load(open(fn, encoding='utf-8')), add_cell.load()); print('ok', fn)
FIXN = " FIX = 2^33 words (F7 flag region) + 3*S_R (R_j lists) + 20000 scratch words = 583910972788 words = 18685151129216 B = 2^44.0870 B, ledger bound; actual allocator not measured. Online code does not read R_j (only P6 count/fill do)."
O_S = '256 x 2^64 header words (the sentinel pass table), filed r38d table line'
rec('sha256-38|MEM.SENT|MEM|M2', O_S, 'M2: exact ledger time to recompute / stream the 256-block sentinel pass table instead of holding it?',
    "No header-free bucket lookup is cheaper than the table in our ledger. Exact (ledger ops, k=0): one full rebuild of the headers (P6 zero 2^74.0 + count 2^76.690 + prefix 2^76.087 ops) = 2^77.549 ops = 2^66.135 units, already paid once inside T. Rebuild per use is not priced (N_G 2^67.9 groups x 256 lookups). Sorted entries with a key word cost more words than the headers they remove (E = 3.84 H). Whole-table replacement: scan R_j per lookup (S_R/256 variants x 21 ops, model) time_log2 98.364, S 122.451 (memory 2^44.087 B); shard route (D126 k=19) time 88.211, S 130.166.",
    notes="Rebuild ops exact (ledger); the 21 ops per variant of the scan-R model are ours (13 prelude of the P6 count body measured as 145-22*6, +3 loop, +5 membership test), a model not a program. Shares of the ledger words: SENT 6.44%, HDR 74.2%, P6T 19.3%, FIX 8e-10.")
rec('sha256-38|MEM.SENT|MEM|M3', O_S, 'M3: S-optimal hold-versus-recompute point for this object with the others fixed?',
    "Hold. Headers, entries and sentinels share one address (Y,Z0), so they shard together; joint S-optimum k=19 (S 130.16628, memory 2^61.955 B, D126 pricing; strict pricing also k=19, 130.47885). Ceiling: if SENT cost zero bytes at no time, best S 130.07013 (k=19): at most 0.0961 bit, so any recompute costing more than 0.096 bit loses. At k=0 the same ceiling is 0.0961 (132.2945 vs 132.3907).",
    notes="Ceiling is memory-only arithmetic on the ledger (time unchanged).")
rec('sha256-38|MEM.SENT|MEM|M4', O_S, 'M4: breakpoint at 2^20 B, S on both sides, is crossing worth it?',
    "SENT alone is 2^77 B at k=0, 288230376151711744 B (2^58.0) at k=19, and reaches <= 2^20 B only at k=57 (S 150.298, D126 pricing; k=45 138.303, k=30 130.179, k=19 130.166). No breakpoint of S inside the shard family: the total never gets below 2^44.087 B (FIX alone), the max(0,.) term is active everywhere, S rises 1 bit per doubling. Crossing 2^20 for the whole program means dropping tables, R_j and F7: stream P5 per lookup (model) time_log2 109.008, memory 1,688,576 B (scratch 640,000 B + code 2^20 B) = 2^20.687, S 109.695 (code 2^23 B: 9,028,608 B, S 112.114; with the measured mean P5 body 33.69 ops instead of the ledger max 58: S 108.962 / 111.381). That is 18-21 bits below the table optimum 130.166 but about 22 bits above the filed table-free R38M3 line (87.904). Getting under 2^20 B needs code <= 408,576 B (12,768 instructions at 32 B beside the 640,000 B scratch); not built.",
    notes="Code-size convention: r38 32 B per instruction; the proof says the table line's program text is about 2^23 B. P5-stream and scan-R are our ledger models (per lookup 768*(36+2^29*(58+3)) ops for the A0 window + 21 ops per valid variant), not programs.")
rec('sha256-38|MEM.HDR|MEM|M4', '3 x S_R 22 2^32 entry words (3 words per entry), filed r38d table line', 'M4: breakpoint at 2^20 B, S on both sides, is crossing worth it?',
    "Entry words are 74.2% of the ledger bytes: 1739573410328681606283264 B at k=0, 3317972965867388928 B at k=19; <= 2^20 B only at k >= 58 (S > 150). No 2^20 breakpoint in this family (total floor 2^44.087 B). The object is the one that pays: if the 3-word entry (c7+flag, A1, S0(A1), A2-record address, G-record address: about 137 bits of 256) were packed into 1 word (model: +2 ops per scan unit, +4 per W pass, +132 ops per (Y,variant) in the fill), D126 pricing best S 128.7563 at k=19 (memory 2^60.545 B), strict 129.3256 at k=18: gain 1.410 bit (D126) / 1.153 bit (strict); memory-only ceiling for removing HDR entirely 1.955 bit (k=18, S 128.2110). With sentinels also removed (count in header) 128.4852 (gain 1.681). Not built or run.",
    lever=True, gain=1.41, notes="LEVER (table line only, S rule): packing 3->1 words, gain 1.410 bit S over D126 130.1663 at k=19; model only (ledger arithmetic with the extra ops priced as stated), no program rebuilt, no organizer experiment. The table line stays 40 bits above the filed R38M3 (87.904): a lever for the table family, not for the board.")
rec('sha256-38|MEM.P6T|MEM|M4', '3 x min(S_R 22 2^32, 256 2^64) sentinel-entry words, filed r38d table line', 'M4: breakpoint at 2^20 B, S on both sides, is crossing worth it?',
    "Sentinel entries are 19.3% of the ledger bytes (453347182355485940514816 B at k=0; 864691128455135232 B at k=19). <= 2^20 B only at k >= 57; no breakpoint in the family (total floor 2^44.087 B). Bound vs expected: the ledger charges 3 words for all H = 256*2^64 headers; under H1 uniformity the mean bucket is 3.8372 entries and 0.97845 of headers are nonempty, so the expected need is 2.935 H words, 2.2% under the bound (0.031 bit; premise, not exact). Dropping them by storing the bucket count in the 256-bit header word (model: +3 ops per scan unit, +2 per nonempty header in the prefix pass): D126 pricing best S 129.85620 at k=19 (memory 2^61.645 B, time 88.21101): gain 0.3101 bit over 130.16628; strict pricing no gain (130.5386 vs 130.4788: the extra ops are charged on all 256 lookups). Not built.",
    lever=True, gain=0.31, notes="LEVER (table line only): count-in-header, 0.310 bit S at k=19 under D126 pricing, 0 under strict; model only; the sentinel is detected through the F7 table value 2 in the shipped program, that interaction is not rebuilt.")
rec('sha256-38|MEM.FIX38|MEM|M2', 'fixed non-table terms: F7 flag region 2^33 words, R_j lists 3*S_R words, 20000 scratch words (filed r38d)', 'M2: exact ledger time to recompute / stream it instead of holding it?',
    "R_j streamed: P5 enumeration is 2^52.5175 ops (2^41.104 units) per pass; regenerating it for the count and fill passes adds 2 passes = 2^53.52 ops, about 2^-47 of T (2^88.2), saving 3*S_R*32 = 2^44.07 B. F7 computed inline instead of the 2^38 B region: 25 ops per entry visited (ledger F7_in_ops 25): at k=19 S 130.1662890 vs 130.1662757 (+1.3e-5 bit worse). Both exact in ledger units but move S by under 2e-5 bit at the table optimum (memory-only ceiling for dropping FIX entirely 1.5e-5 bit)." + FIXN,
    notes="Streaming order of P5 against the P6 passes is not rebuilt; still a model.")
rec('sha256-38|MEM.FIX38|MEM|M3', 'fixed non-table terms: F7 flag region, R_j lists, scratch (filed r38d)', 'M3: S-optimal hold-versus-recompute point for this object with the others fixed?',
    "Hold at the table optimum: shrinking FIX to zero moves best S by 1.5e-5 bit. The decision flips only once the tables are gone: on the scan-R line (time_log2 98.364) FIX is the memory (2^44.087 B, S 122.451); inlining F7 there gives 122.430 (-0.021); streaming R_j and F7 too (P5 per lookup, time 109.008) gives S 109.695 with 1 MiB of code, 112.114 with 2^23 B code: recompute beats holding R_j by 12.8 to 10.3 bit." + FIXN,
    notes="Scan-R and P5-stream are ledger models (21 ops per variant; P5 window ops from pre2.json constants), not programs.")
rec('sha256-38|MEM.FIX38|MEM|M4', 'fixed non-table terms: F7 flag region, R_j lists, scratch (filed r38d)', 'M4: breakpoint at 2^20 B, S on both sides, is crossing worth it?',
    "FIX alone is 2^44.087 B (R_j 2^44.07, F7 2^38, scratch 640,000 B), so the table line can never sit below 2^44.087 B; the 2^20 breakpoint belongs to a different program: above it (R_j held, tables dropped) S 122.451; below it (P5 stream, F7 inline, 1.69 MB incl. scratch) S 109.695 at code 2^20 B (memory 2^20.687, 0.687 bit over the line), 112.114 at code 2^23 B. Crossing is worth 12.8 bit against the R_j-held line and 20.5 bit against the table optimum 130.166 (D126), but this family is 21.8 bit above the filed table-free R38M3 (87.904)." + FIXN,
    notes="One measurement, not chased.")
