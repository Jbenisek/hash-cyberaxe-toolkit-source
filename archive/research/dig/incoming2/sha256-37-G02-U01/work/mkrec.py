
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

import json, re, sys, os
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G02-U01')
EV = ("research/dig/incoming2/sha256-37-G02-U01/work/g02_mem.py; research/dig/incoming2/sha256-37-G02-U01/work/g02_run.py; "
      "research/dig/incoming2/sha256-37-G02-U01/work/grid.json; research/tools/build_pkg/scratch/pkgR37c/pkg/sha256-r37/experiments/xtab.py (ledger); "
      "research/tools/build_pkg/scratch/pkgR37M3/pkg/sha256-r37/experiments/lowm.py (ledger, memory)")
KA = ("Known-answer checks passed first (our scripts g02_mem.py): xtab.py ledger of the filed table line reproduces T=2137189670580414105336/661, "
      "time_log2 61.4877 (61.487698); byte bound 1105515320967168 = 2^49.97364; D126 shard model at k=5 reproduces nfb 11480695164613822619, "
      "T=89459989869750967895523/1322, mem 35088251224064, S 90.87120750106125; lowm.py ledger reproduces 60.99099 and memory 607,744 B. ")
MODEL = ("Shard model 'reject-early' (OURS, a model not a proof): hold 1/B of x (B=2^k) for T0 and records, B times more first blocks, a first block whose x is "
         "outside the held shard costs its compression plus 3 ops (shift, compare, branch); only matched first blocks pay the ledger's per-block work; "
         "preprocessing items (i)-(iii) divided by B (ceil); success/cap fixed point on the matched count. D126 instead charges every extra first block the "
         "full per-block work (pessimistic by 2.40 bits at its optimum: S 88.469 at k=7 vs D126 90.871 at k=5). Both share the x-uniform-shard premise. ")
recs = []
def add(cid, obj, q, num, status, notes, lever=False, gain=None):
    r = dict(id=cid, hash="sha256-37", row_i=None, row_j=None, object=obj, question=q, labels=[], status=status, number=num,
             source="our workflow: scan-once-wave2", own_test=True, evidence=EV, date="2026-10-12", lever=lever, gain_bits=gain,
             notes="universe cell %s. %s%s" % (cid, KA, notes))
    if gain is not None: r['gain_basis'] = 'S'
    recs.append(r)

add("sha256-37|MEM.T0|MEM|M4", "T0 table (x -> record address), filed r37 table line (pkgR37c)",
    "M4: S on both sides of the 2^20 B breakpoint for T0, and is crossing worth it?",
    "T0 = 2^32 x 8 B = 34,359,738,368 B = 2^35 (exact); share of the 2^49.97 total 3.1e-5 (dropping T0 alone gains 4.5e-5 bit). T0/B <= 2^20 B needs B=2^15 (k=15), "
    "but T0 shards only together with the records (same x split), so the crossing is a whole-line move. S at k=15 (R16T held, ANC<2^33): T 73.31820, mem 2^39.107, "
    "S 92.42516 vs best held S 88.46864 (k=7): crossing worth it = NO, +3.96 bit. With R16T->chunk tables and lane-scan->de Bruijn the line is flat there "
    "(k=15 S 88.29142, optimum k=16 88.29141): T0 reaches 2^20 B at the optimum, but the 2^20 breakpoint of the line is set by the records (k=30, S 91.18) and the 6.3 MB variant records, not by T0.",
    "LOCAL_ONLY", "Window answer: valid for the reject-early / D126 shard models with x-uniform shards; T0 alone cannot be sharded or dropped without the records (T0 is only the index into R(x)). "
    "Alternative index (sorted keys of the ~6.6e8 non-empty x, 12 B each = 2^32.9 B) not priced. ")

add("sha256-37|MEM.REC|MEM|M4", "(x,class) record store R(x), filed r37 table line (pkgR37c)",
    "M4: S on both sides of the 2^20 B breakpoint for the record store, and is crossing worth it?",
    "Records: 15,130,951,680 x 73,024 B (max; typical 32,208 B = 2^48.79 total) = 1,104,922,615,480,320 B = 2^49.9735 (exact bound). REC/B <= 2^20 B needs k=30 (1,029,039 B). "
    "Nearest points of the best line (R16T chunk tables + de Bruijn lane-scan, reject-early): S k=29 90.36636, k=30 91.18422 (T 88.31765, mem 7,647,568 B = 2^22.87 because the 6.3 MB variant records stay), "
    "k=31 92.08374; optimum k=16 S 88.29141 (T 74.31794, mem 2^33.97). Crossing worth it = NO inside the table line (+2.9 bit at k=30; the total never reaches 2^20 B since the ancillary floor is 2^22.6). "
    "Crossing to the table-free program: lowm at the table line's q3 (-74.03) T 62.76763 at 607,744 B (S 62.76763); at its own q3 (-71.47, filed) 60.99099: worth it by ~25.5 bit vs best held 88.29-88.47.",
    "LOCAL_ONLY", MODEL + "The lowm number at q3 -74.03 is ledger arithmetic only (lowm.ledger(q3_log2=-74.03)); the filed lowm has the relaxed row-16 cells (q3 -71.47), so part of its gain over the table line is not memory-related. ")

add("sha256-37|MEM.R16T|MEM|M4", "row-16 mask table R16x (2^34 x 32 B), filed r37 table line (pkgR37c)",
    "M4: S on both sides of the 2^20 B breakpoint for the row-16 table, and is crossing worth it?",
    "R16x = 2^34 x 32 B = 549,755,813,888 B = 2^39 (exact). Replacement by the two 4096-word chunk tables of lowm = 262,144 B = 2^18 (<2^20). Price at k=0 with everything else fixed: "
    "+0.60981 bit time (61.48770 -> 62.09751; +12,529 ops per first block: 33 more probe ops per 4-group plus 4 x (PNZ*8 + MU*41) survivor ops per group, groups per first block 222.14, vbar 12617.48 -> 25146.70), "
    "S 91.46134 -> 92.07043, i.e. NOT worth it while the records (2^49.97) are held. It is worth it once k>=7. S(held) - S(chunk) by k: k=6 -0.0465 (held better), k=7 +0.0398, k=8 +0.1472, k=10 +0.5838, k=12 +1.5714; "
    "best held 88.46864 (k=7) vs best chunk 88.31984 (k=10, T 68.33549, mem 2^39.984): crossing gains 0.149 bit.",
    "LOCAL_ONLY", MODEL + "Chunk-table probe and survivor ops taken from lowm.py constants (PROBE 11,12,12,12 vs table 3,4,4,3; PNZ=2971/32768, MU=1/8, SURV_FIX 8, SURV_LANE 7, EX_OPS 34); "
    "lowm survivor statistics are for its relaxed row-16 pair set (2,097,152 pairs), so this is an upper bound for the table line's 1,052,672 pairs. Priced in the ledger, not run as a program. ", lever=True, gain=0.149)

add("sha256-37|MEM.ANC|MEM|M1", "ancillary code and working space, filed r37 table line (pkgR37c)",
    "M1: bytes held at peak (bound vs exact)?",
    "BOUND < 2^33 B = 8,589,934,592 (proof Section 14, no derivation). Exact occupancy is not derivable from the proof text: the entry width of the lane-scan tables is not stated. "
    "Component sizes (our arithmetic): lane-scan tables 15 batches x 11 chunk positions x 2^24 entries (PRE item v) = 2,768,240,640 entries: 2 B/entry (12-bit lane index) 5,536,481,280 B = 2^32.37; "
    "4 B = 11,072,962,560 = 2^33.37 (EXCEEDS the 2^33 bound); 8 B = 22,145,925,120 = 2^34.37 (exceeds). Variant records 782,800 x 8 B = 6,262,400 B; code <= 2^16 B (lowm convention, bound); "
    "class descriptors 222 x 4 words x 32 B = 28,416 B. With 2 B entries the sum is 5,542,837,632 B = 2^32.37, inside the bound.",
    "LOCAL_ONLY", "Bound vs exact: the bound is the proof's; the 2/4/8 B rows are arithmetic on an assumed width, not read from a program (xtab.py is a Python reference and allocates none of this). "
    "Flag for the organizer note batch: if the shipped table uses >=4 B entries the stated 'below 2^33' ancillary bound is false; effect on the total <= 3e-5 bit at k=0 (2^34.4 vs 2^49.97) but about 0.8 bit near the optimum k=16. "
    "Code convention: 2^16 B bound (the r38 rule of 32 B per instruction is not used; the table line gives no instruction count). ")

add("sha256-37|MEM.ANC|MEM|M2", "ancillary code and working space (lane-scan tables), filed r37 table line (pkgR37c)",
    "M2: exact ledger time to recompute / stream the ancillary tables instead of holding them?",
    "Recompute the 24-bit lane-scan tables by lowest-set-bit extraction (x&-x 2 ops, de Bruijn multiply 1, shift 1, 32-entry load 1, offset add 1, x&=x-1 2, loop branch 1 = 9 ops per set lane instead of SCAN_LANE=4, "
    "+5 ops per passing fibre): exact ledger at k=0 T 61.487698 -> 61.508886 (+0.021188 bit), vbar 12617.48 -> 12969.86 (+352.38 ops per first block), nfb unchanged. In the chunk-table line +0.01391 bit at k=0. "
    "Variant records (6,262,400 B) are not repriced (recomputing from class lists as lowm does is a different program).",
    "LOCAL_ONLY", "The 9-op count is ours (not a shipped program); the ledger arithmetic is exact given it (ledger_param(scan_lane=9)). Streaming from the chunk position rather than recomputing is not priced. ")

add("sha256-37|MEM.ANC|MEM|M3", "ancillary code and working space, filed r37 table line (pkgR37c)",
    "M3: S-optimal hold-versus-recompute point for this object, others fixed?",
    "S_hold - S_recompute by shard factor k (negative = hold better): held R16T: k=0 -0.02118, k=5 -0.00443, k=7 -0.00005 (best point; hold wins by 5e-5 bit), k=10 +0.00741, k=15 +0.02107. "
    "With R16T chunk tables: k=0 -0.01391, k=5 -0.00393, k=10 +0.01125, k=12 +0.04514, k=15 +0.32711, k=16 +0.5935. Optimum: hold below k~7-8, recompute from k>=8 (held-R16T line) / k>=6 (chunk line). "
    "Best S: held-R16T line 88.46864 (hold, k=7) vs 88.46870 (recompute); chunk line 88.31984 (hold, k=10) vs 88.29141 (recompute, k=16): recompute gains 0.0284 bit at the global optimum.",
    "LOCAL_ONLY", MODEL + "Hold = ancillary charged at the proof bound 2^33; recompute = variant records + code + descriptors (6.3 MB) with the de Bruijn scan. ", lever=True, gain=0.028)

add("sha256-37|MEM.ANC|MEM|M4", "ancillary code and working space, filed r37 table line (pkgR37c)",
    "M4: S on both sides of the 2^20 B breakpoint for the ancillary space, and is crossing worth it?",
    "Without the lane-scan tables the ancillary floor is variant records 6,262,400 B + code 65,536 + descriptors 28,416 = 6,356,352 B = 2^22.6 > 2^20, so the table line cannot go below 2^20 B at all "
    "(flat floor: S(k=40) 100.97595 = T 98.31765 + 2.66). Crossing to <=2^20 B means leaving the table line: lowm (lists 127,744 B, 607,744 B total) at the same q3 -74.03 is T=S=62.76763 "
    "(own q3: 60.99099 filed) vs the table line's best S 88.29141 (k=16, ancillary recomputed) or 88.46864 (all held, k=7): worth it by ~25.5-25.7 bit. With the ancillary held at 2^33 the penalty alone is 13 bit.",
    "LOCAL_ONLY", MODEL + "lowm number at q3 -74.03 is ledger arithmetic (not the filed program). ")

for r in recs:
    fn = os.path.join(OUT, re.sub(r'[^A-Za-z0-9]+', '_', r['id']).strip('_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    print(os.path.basename(fn), add_cell.validate(json.load(open(fn, encoding='utf-8')), add_cell.load()))
