
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
out = os.path.dirname(os.path.abspath(__file__)) + '/..'
EV = "research/dig/incoming2/sha256-37-G02-U03/work/ (lowm_copy.py = copy of pkgR37M3 experiments/lowm.py; scen.py, scen_out.json)"
KA = ("Known-answer check: the scratch copy reproduces time_log2 60.99099 (nfb 60951875249131685, per-FB 18.65699 units, vbar 46070.085) and 607,744 B = 2^19.2131 from lowm.py memory/ledger. "
      "Convention: ledger counts executed 256-bit primitives (H5); memory words of 32 B, code a 65,536 B bound. ")
R16 = ("R16SET size: the shipped R16x program (pkgR37M3) accepts 2,097,152 (u,l) pairs (65,536 per l x 32; 2,057,184 distinct u; recounted from work/r16.bin); the cell text's 1,052,672 pairs (1,042,240 distinct u, 28 usable l) is the earlier no-R16x set (S37-E8-OWN) and is not the object held. ")
def mk(obj, cid, q, status, number, notes, topic_lever=False):
    return dict(hash="sha256-37", row_i=None, row_j=None, object=obj, question=q, labels=["N"], status=status, number=number,
        source="our workflow: scan-once-wave2", own_test=True, evidence=EV, date="2026-10-12", lever=False, gain_bits=None,
        notes="universe cell %s. %s" % (cid, notes), topic=cid)
recs = {}
O1 = "row-16 accepted (u,l) set (held as LO/MID chunk tables)"
O2 = "per-first-block good-pair list"
c = "sha256-37|MEM.R16SET|MEM|%s"
recs[c % 'M1'] = mk(O1, c % 'M1', "M1 bytes held at peak", "COMPUTED",
  "EXACT: shipped program holds the set only as LO + MID chunk tables 2 x 4096 words x 32 B = 262,144 B (2^18) of the 607,744 B total (43.1%); per-l constants 4,096 B are separate. Raw set if held: 2,097,152 pairs x 4 B (u, per-l buckets) = 8,388,608 B (2^23) + 33 offsets (bound); 1,052,672-pair no-R16x set = 4,210,688 B",
  KA + R16 + "Peak = online phase; tables are built in preprocessing and never held twice (proof 14.1). Table-build memory in preprocessing was not measured.")
recs[c % 'M2'] = mk(O1, c % 'M2', "M2 exact recompute/stream time instead of holding", "COMPUTED",
  "LEDGER ARITHMETIC (model for the unshipped variants, bound): drop tables, filter directly (200 ops per group of 4 instead of 47): time_log2 61.39195 (+0.40096 bit), mem 345,600 B; drop the filter, exact-test all 32 l per lane: 64.5569 (+3.5659 bit); shipped 60.99099",
  KA + R16 + "Variant ledgers rerun with lowm.py constants PROBE and SURV_* edited in a scratch copy (scen.py). The direct-filter op count (32 l x 6 ops + 8 per group) is our estimate, not a written program; the no-filter row uses the shipped EX_OPS = 34 + SURV_LANE 7 per (lane, l). Stream/shard: the set is a fixed constant of the characteristic, so there is nothing per-run to stream; building LO/MID is inside PRE < 2^38 (actual build cost not measured).")
recs[c % 'M3'] = mk(O1, c % 'M3', "M3 S-optimal hold-vs-recompute point", "COMPUTED",
  "HOLD the two chunk tables (shipped): S = 60.99099 at 607,744 B (memory term 0). Recompute-direct S = 61.39195 (worse, memory term still 0); fully held set (8,734,340 B total) with a free-lookup oracle S = 63.8192 (time floor 60.76091, +2.8583 memory term)",
  KA + R16 + "Others fixed. Under S = T + max(0, log2 B - 20) every byte below 2^20 is free, so the tables stay. Oracle row = ledger with probe and survivor cost set to 0 (rare path kept): a lower bound on time for ANY row-16 structure, 0.23008 bit below shipped. A 9th-condition HI table (bit 30; 256 words = 8 KB, free under 2^20): ledger with PNZ halved and MU = 32/512 (assumed, not measured) gives 60.95521 at +0 extra ops/group, 60.97367 at +6, 60.9919 at +12; break-even about +12 ops per group. Upper bound 0.036 bit, not built.")
recs[c % 'M4'] = mk(O1, c % 'M4', "M4 breakpoint at 2^20 B", "COMPUTED",
  "Total 607,744 B is 440,832 B (0.787 bit) under 2^20; this object is 262,144 B. Crossing 2^20 with the full set (8.73 MB total) costs +2.8583 bit of memory term for at most 0.23008 bit of time: NOT worth it; even a free-lookup oracle only pays up to B = 2^20 x 2^0.23008 = 1.23 MB total",
  KA + R16 + "Breakeven computed from the oracle lower bound on time (probe and survivor stages cost 0), so it holds for every possible row-16 structure in this ledger.")
c = "sha256-37|MEM.PAIRS|MEM|%s"
P = ("Good-pair count per first block g = 830.9882 (exact, ledger); classes pass with p7 = 0.015869, a class of n <= 3600 variants has good fraction p6 = 0.066895; 50,000-first-block replay (proof 13.3) realized 835.0 per block, counted ops SD 4.2 x mean. ")
recs[c % 'M1'] = mk(O2, c % 'M1', "M1 bytes held at peak", "COMPUTED",
  "EXACT: 0 B held by the shipped program (pairs stream from the class pass plane into a 4-lane group register of 32 B; the 7,168 B spill area holds batch sums, not pairs). If materialised: mean 830.988 x 4 B = 3,323.95 B (exact mean), one class at most 3,600 x 4 = 14,400 B (bound), one first block at most 782,800 x 4 = 3,131,200 B (bound)",
  KA + P + "Entry size 4 B (32-bit a0) is our assumption for a materialised list; the packed entry words of proof 14.1 (102,400 B) are the shared rep lists, not per-first-block pairs. No quantiles sampled.")
recs[c % 'M2'] = mk(O2, c % 'M2', "M2 exact recompute/stream time instead of holding", "COMPUTED",
  "LEDGER ARITHMETIC: streaming is the shipped path (generation = ct_var 21.14 + perclass 24,666.75 = 24,687.9 ops per first block, 29.7 per pair; groups + probe 16,269.8). Holding it (one store and one load per group of 4, GROUP_BODY 31 -> 33): time_log2 60.99702 (+0.00603 bit), vbar 46,487.08",
  KA + P + "The list is per first block and random-CV dependent, so it cannot be reused across blocks: holding only adds work. +2 ops per group is our lower-bound count for materialising.")
recs[c % 'M3'] = mk(O2, c % 'M3', "M3 S-optimal hold-vs-recompute point", "COMPUTED",
  "STREAM (shipped): S = 60.99099 at 607,744 B. Materialised: S = 60.99702 (time +0.00603, memory term 0 since 611,068 B < 2^20)",
  KA + P + "Others fixed. Hold never wins: no time saved, small time added, memory irrelevant below 2^20.")
recs[c % 'M4'] = mk(O2, c % 'M4', "M4 breakpoint at 2^20 B", "COMPUTED",
  "Average list (3.3 KB) and one-class list (14.4 KB) stay under 2^20 (total 622,144 B); a worst-case whole-block list of 3,131,200 B would put the total at 3.74 MB (2^21.83), memory term +1.83 bit, for no time saving: crossing is never worth it",
  KA + P + "Worst case is the bound NVAR x 4 B with all 222 classes passing and every variant good; not reached in the 50,000-block replay.")
for k, r in recs.items():
    fn = os.path.join(out, k.replace('|', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    print(fn, add_cell.validate(json.load(open(fn, encoding='utf-8')), add_cell.load()))
