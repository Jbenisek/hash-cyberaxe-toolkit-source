
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

import json, glob, os, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
W = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha3-r5-G02-U02')
rss = []
for f in sorted(glob.glob(W + r'\work\bp_rss_k*.log')):
    try:
        rss.append(json.loads(open(f).read().strip().splitlines()[-1]))
    except Exception:
        pass
rl = ", ".join("k%d %.1f MB" % (d["k"], d["maxrss_KB_end"] / 1024) for d in rss)
rmax = max(d["maxrss_KB_end"] for d in rss) / 1024
nl = len(rss)
EV = "research/dig/incoming2/sha3-r5-G02-U02/work/ (ledger_ka.py, cores.py, cores_stats.json, bprime_mem.py, bp_*.log, pcore_mem.py, s_points.py)"
KA = ("Known answers reproduced first on pkgR5M (r5.py md5 6403cfe0, same as pkgR5T): ledger J.3 gives N=10073561282442, time_log2 32.79156 (filed 32.79157), S=32.79157+7.2=39.99157 at memory 2^27.2; "
      "T1/T2 rerun gives 1741 cores, 467 kept, sum C2 1,379,275,399,350, 48,592,224 half vectors (equal to GROUP_LOG totals); U.4 price 2^26.5335 units reproduced.")


def rec(cid, obj, q, status, num, notes, lever=False, gain=None):
    r = dict(hash="sha3-r5", row_i=None, row_j=None, object=obj, question=q, labels=["N"], status=status, number=num,
             source="our workflow: scan-once-wave2", own_test=True, evidence=EV, date="2026-10-12", lever=lever,
             gain_bits=gain, notes="universe cell %s. %s %s" % (cid, KA, notes),
             topic="sha3.r5.mem." + cid.split('|')[1].lower() + "." + cid.split('|')[3].lower())
    if lever:
        r["gain_basis"] = "S"
    return cid, r


R = []
t = "T1/T2 core list (467 kept of 1,741 cores) + MINW/WT2 (cores.bin)"
R.append(rec("sha3-r5|MEM.T1CORES|MEM|M1", t, "M1: bytes held at peak", "COMPUTED",
 "cores.bin = 13,325,904 B exact (2^23.668; export.py format: 4 + sum over 467 cores of (4 + sum over rows of (16 + 324 m)) + 32 MINW + 1,024 WT2; 4,542 rows, sum m = 40,896; per core 17,596-29,324 B, mean 28,533; 392 cores have 10 rows). Smaller forms: kept-core bit lists 4,574 bit indices (about 9.1 kB at 2 B), all 1,741 cores 17,100 indices (34.2 kB); MINW+WT2 = 1,056 B. Exact for the file; convention = data bytes of export.py, not Python object overhead. Not itemised in D161; not an object of the online program (P is advice, 8 B).",
 "Peak context: read only by the native T3 (mitm2.c) beside one core's tables; shipped r5.py trail_search holds the core list (467 tuples of <=10 ints) and one core's tables. Measured Python one-core halves() of the certified core: tracemalloc 41.8 MB, process RSS 82.8 MB (sampled, 1 core)."))
R.append(rec("sha3-r5|MEM.T1CORES|MEM|M2", t, "M2: exact time to recompute/stream instead of hold", "COMPUTED",
 "Charged price of producing the list = N1*2^12 + C1*56 + 2^32 = 131,616,018,432 prim = 97,133,593 units = 2^26.5335 (U.4, reproduced); after the J repricing of T2 (-33,576,992,448 prim) 98,039,025,984 prim = 72,353,525 units = 2^26.109, about 1% of N (7.434e9 units). Streaming (regenerate each core's table from its bit list inside the core-by-core loop, never holding the 13.3 MB list) adds no second T1/T2 pass: each kept core is used once by the P loop, so stream cost = the same charge. Measured wall time of T1 (8,674,833 nodes) + T2 over 1,741 cores in Python: 62 s.",
 "Label: exact arithmetic from the ledger; the per-core table rebuild (core_tables) is inside the 2^32 export bound, not separately counted by us."))
R.append(rec("sha3-r5|MEM.T1CORES|MEM|M3", t, "M3: S-optimal hold-versus-recompute point", "COMPUTED",
 "Hold. The list is not the peak of any phase: P phase 92,474,384 B (2^26.463 with the 2^18*32 code bound, D161), B'+K 2^27.17 stated. Adding cores.bin to the P phase gives 105,800,288 B = 2^26.657 (+0.194 bit of memory term only if P were the peak), still below the stated peak 2^27.2, so S = 39.99157 either way. Dropping it saves 0 bit at the current peak, at most 0.194 bit in a world where P is the peak; streaming adds no time. No gain.",
 "Label: exact arithmetic on D161 numbers; the code term is a bound (32 B per instruction convention)."))
R.append(rec("sha3-r5|MEM.T1CORES|MEM|M4", t, "M4: breakpoint at 2^20 B", "COMPUTED",
 "The object alone is 2^23.668 B, 3.668 bits above 2^20. In the run the peak is 2^27.2 (stated) / 2^26.46 (P phase), so crossing 2^20 for this list alone changes S by 0; getting the whole P phase under 2^20 would need its 83 MB tables to shrink 80x. Not worth crossing.",
 "Label: exact for the object size; the whole-run statement is a bound."))
t = "B-prime candidate working set (CandSetup + b_attempt)"
R.append(rec("sha3-r5|MEM.BPRIME|MEM|M1", t, "M1: bytes held at peak", "SAMPLED",
 "Stated 113.5 MiB = 119,013,376 B (v14 lineage bound, never derived). Measured on the unmodified shipped r5.py, R7 label k=1 (c=0, j=13, DF 41): Python-allocated peak (tracemalloc, above post-Base baseline) 24,189,590 B = 23.1 MiB, 1,116,024 B still held at return. Whole-process peak RSS over %d labels: %s (interpreter, module tables and Base included); max %.1f MB = %.0f%% of 113.5 MiB." % (nl, rl, rmax, 100 * rmax * 1048576 / 119013376 if False else 100 * rmax * 1e6 / 119013376),
 "Label: sampled over %d R7 labels (c=0, first accepted candidate), not a bound; Python object bytes, not the proof's data-byte convention. So 113.5 MiB is a safe bound, not the exact allocation. WK prim for B' k=1: 26,960,409,156." % nl))
R.append(rec("sha3-r5|MEM.BPRIME|MEM|M2", t, "M2: exact time to recompute/stream instead of hold", "COMPUTED",
 "B' is already built one candidate at a time (each attempt restarts from CandSetup); there is no stored table that a recompute would replace, so no recompute time exists. The priced way not to hold it beside the 50 echelon systems is the D152 phase split: 62 MiB scratch I/O at 1 prim per 32-bit word = 16,252,928 prim plus one 2^31 phase-boundary allowance = 1,596,854 units = +0.00031 bit on 2^32.79157 (reproduced).",
 "Label: exact arithmetic (the 2^31 is the lineage's allowance, a bound)."))
R.append(rec("sha3-r5|MEM.BPRIME|MEM|M3", t, "M3: S-optimal point", "SAMPLED",
 "Proven-today point (D152 split, B' phase 124.12 MiB = 2^26.956 < 2^27): S = 32.79187 + 7.0 = 39.79187, 0.1997 below the filed 39.99157. If B' were proved <= about 77.6 MiB (so cand phase B'+8+2+0.62 MiB <= the P-phase 88.2 MiB) so that the P phase (2^26.4626 incl. code bound) is the peak: S = 39.2544, 0.737 below the filed one at +0.0003 time. Samples straddle that threshold: B' Python-allocated 24 MB (k=1), whole-process RSS up to %.0f MB (k=8, DF 53, 43.2e9 WK prim), so no bound below the P phase is supported by our samples; a proof would need the array sizes of Cand/Model/d2u, which we did not derive." % rmax,
 "Label: first number COMPUTED from stated bounds, second CONDITIONAL on a proved B' bound. %d labels sampled. The Python P phase measured here (82.8 MB RSS, one core) is the same size, so the claim could not drop much below 2^26.4 anyway." % nl,
 lever=False, gain=None))
R.append(rec("sha3-r5|MEM.BPRIME|MEM|M4", t, "M4: breakpoint at 2^20 B", "COMPUTED",
 "B' at the stated 113.5 MiB is 2^26.83 (6.83 bits over 2^20); at the sampled 24 MB it is 2^24.5. B' online is at most 7.2% of N (B_TRUE 2^29 of 7.43e9 units; true max 2^28.60 = 5.5%), so a recompute blowup near 2^6.83 would cost more than it saves, and the P (2^26.46) and E (2^25.58) phases stay above 2^20 anyway: crossing 2^20 for B' alone gains 0 S. Not worth crossing.",
 "Label: exact arithmetic on stated bounds; time share is from the proof's caps."))
for cid, r in R:
    fn = os.path.join(W, cid.replace('|', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    add_cell.validate(json.load(open(fn, encoding='utf-8')), add_cell.load())
    print("valid", fn)
