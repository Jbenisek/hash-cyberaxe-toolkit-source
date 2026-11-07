
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

import json,os,sys
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
out=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G02-U02')
ev="research/dig/incoming2/sha256-37-G02-U02/work/mem_scan.py; research/dig/incoming2/sha256-37-G02-U02/work/lowm.py (copy of pkgR37M3 experiments/lowm.py); research/tools/build_pkg/scratch/pkgR37M3/pkg/sha256-r37/proof.md Sections 9, 14"
KN=" Known-answer check: lowm.py ledger reproduces time_log2 60.99099 and nfb 60951875249131685; lowm.py memory reproduces 607,744 B = 2^19.2131 (r37 convention: 32 B words, code bound 65,536 B), S = 60.99099 (memory term 0). Baseline per first block 2644 + 615 + 46070.085 = 49329.1 primitives. UNITS text says a bitmap would be 2^23 B: wrong, 2^32 bits = 2^29 B = 512 MiB."
def rec(cid,obj,q,num,notes,labels=("N",)):
    return dict(hash="sha256-37",row_i=None,row_j=None,object=obj,question=q,labels=list(labels),status="COMPUTED",number=num,source="our workflow: scan-once-wave2",own_test=True,evidence=ev,date="2026-10-12",lever=False,gain_bits=None,notes="universe cell "+cid+". "+notes+KN,topic="MEM."+cid.split('|')[1].split('.')[1])
R={}
f7="Bitmap hold of F7: 2^29 B, total 536,870,912+607,744 = 2^29.0016 B, memory term 9.0016 bits. Time with a bitmap class test (lower bound 6 and 8 primitives per class replacing the 397-primitive bit-sliced class test: sub+mask 2, shift 1, address add 1, load 1, bit test 2, branch 1 = 8; 6 is the optimistic count) is 61.0045 / 61.0109, i.e. +0.0135 / +0.0199 bits (estimate of mine, not a shipped program); S = 70.006 / 70.012. Even a FREE F7 test (F7_OPS = 166 removed from the ledger, exact ledger rerun) gives time_log2 60.98858, -0.0024 bits, S = 69.990."
R["sha256-37|MEM.F7|MEM|M3"]=rec("sha256-37|MEM.F7|MEM|M3","F7 membership set (class gate on x = A_-1)","M3: S-optimal hold-versus-recompute point for F7 with the other objects fixed",
 "Recompute (hold 0 B) is S-optimal: S = 60.99099. Hold bitmap: S = 70.006 (6/class) to 70.012 (8/class) (bound/estimate); free-test floor 69.990 (exact ledger). Max time saving from any F7 table: 0.0024 bits (exact ledger); cost to hold 9.0016 bits.",
 f7+" Free headroom to 2^20 is 440,832 B, but no table in that room beats the 166-primitive bit-sliced test (222 lanes in one pass, 0.75 primitive per class): table lookups cost at least 6 per class.")
R["sha256-37|MEM.F7|MEM|M4"]=rec("sha256-37|MEM.F7|MEM|M4","F7 membership set (class gate on x = A_-1)","M4: breakpoint at 2^20 B for F7, S on both sides, is crossing worth it",
 "No. Below 2^20 (shipped): S = 60.99099 at 607,744 B. Above (2^32-bit bitmap, 2^29.0016 B): S >= 69.990 (free test) and about 70.006 (6 prims/class lookup). Crossing needs a time saving > log2(B/2^20); F7 can save at most 0.0024 bits, so no table above 2^20 B with B > 2^20 x 1.0017 = 1,050,300 B can pay.",
 f7)
f6="Bitmap hold of F6: also 2^29 B (2^32 bits), total 2^29.0016, memory term 9.0016. F6 is tested on bit-sliced W planes (256 reps per batch, 27 primitives per run); a bitmap lookup needs the 32-bit word W6x per rep, i.e. a plane-to-word transpose of every rep (12,422 variants per first block on average) which the ledger does not price and which exceeds the 27 primitives per 256 reps by orders of magnitude. Bound used: even a FREE F6 test (27 removed from every W6_OPS and SUBF_OPS entry, exact ledger rerun) gives time_log2 60.98044, -0.01055 bits, S = 69.982."
R["sha256-37|MEM.F6|MEM|M3"]=rec("sha256-37|MEM.F6|MEM|M3","F6 membership set (W6 test on cb = C6 - A_-2)","M3: S-optimal hold-versus-recompute point for F6 with the others fixed",
 "Recompute (hold 0 B) is S-optimal: S = 60.99099. Hold bitmap: S >= 69.982 (free-lookup floor, exact ledger), real value higher. Max time saving from any F6 table 0.01055 bits; cost to hold 9.0016 bits.",f6)
R["sha256-37|MEM.F6|MEM|M4"]=rec("sha256-37|MEM.F6|MEM|M4","F6 membership set (W6 test on cb = C6 - A_-2)","M4: breakpoint at 2^20 B for F6, S on both sides, is crossing worth it",
 "No. Below 2^20: S = 60.99099 (607,744 B). Above: S >= 69.982 (2^29.0016 B). The saving ceiling 0.01055 bits would justify at most B = 2^20 x 2^0.01055 = 1,056,300 B total (about 8,800 B above the 2^20 line); the F6 bitmap is 512 MiB.",f6)
gl="G context (all exact from lowm.py unless marked): 222 class descriptors 28,416 B; lists as held = s_planes 25,088 + s_entries 102,400 = 127,488 B; list-related total 155,904 B of 607,744. Expected passing classes per first block 3.523, expected reps in passing classes 2,642.05 (of 166,490 reps in the 222 classes). Preprocessing (discovery of G over 2^29 E4 values, grouping, the ten lists, planes, entries) is bounded 2^36.1 ops in proof 14.2 and charged 2^38 ops = 2^26.63 compressions, which is 2^-34.4 of T: any rebuild confined to preprocessing is free in time."
R["sha256-37|MEM.G|MEM|M2"]=rec("sha256-37|MEM.G|MEM|M2","A0-variant family G and the 222 class lists","M2: exact ledger time to recompute / stream the class lists instead of holding them",
 "Preprocessing rebuild: 2^38 ops charged (bound; proof 14.2 gives < 2^36.1), effect on time_log2 about 2^-34.4 relative (negligible). Per-first-block streaming of the lists of the passing classes: lower bound +1.38 bits time at 30 primitives per rep (79,262 added primitives on 49,329), +1.65 at 40, +2.08 at 60 (2,642 reps per first block x per-rep entry/plane build; per-rep price is an estimate of mine, the rep count is exact). Exact recompute inside the loop was not written as a program.",
 gl+" Holding is therefore far cheaper than streaming, and streaming saves no S because the memory is already below 2^20.",labels=("N","E"))
R["sha256-37|MEM.G|MEM|M3"]=rec("sha256-37|MEM.G|MEM|M3","A0-variant family G and the 222 class lists","M3: S-optimal hold-versus-recompute point for G / the lists with the others fixed",
 "Hold the 222 descriptors and all lists resident (as shipped): S = 60.99099. Dropping lists saves 0 bits of S (memory term already 0) and costs >= 1.38 bits of time. Headroom to 2^20 is 440,832 B = 2.83 more class-set copies at the same density; upper bound of time gain from using it for further classes: 0.063 bits (all added classes assumed as good as the top 222; ideal-scaling model: per first block non-class cost 2644+218, class-scaled cost 397+46070; the real extra classes are smaller than 3456 variants, so the true value is lower).",
 gl+" Model for the gain: cost per good pair (N0 + s*scal)/(s*830.988) with s the class-set multiple.",labels=("N","E"))
R["sha256-37|MEM.G|MEM|M4"]=rec("sha256-37|MEM.G|MEM|M4","A0-variant family G and the 222 class lists","M4: breakpoint at 2^20 B for G (S on both sides, is crossing worth it)",
 "Below 2^20 is free: up to 440,832 B more (+0.063 bits ceiling gain, see M3). Crossing: holding all of G (12,103,680 variants, 15.46x the 782,800) at the same density needs 2,862,433 B = 2^21.449, memory term 1.449 bits against a time-gain ceiling of 0.0805 bits: S worse by >= 1.37 bits. A raw 32-bit list of G is 48,414,720 B = 2^25.53 (5.53 bits); the 22,976 c7 descriptors alone are 2,940,928 B = 2^21.49. Crossing is not worth it.",
 gl+" Only the already-shipped hold keeps the 2^20 line; the F-set variant (46,557 classes, d183) is a different object and was not re-scanned here.",labels=("N","E"))
for cid,r in R.items():
    fn=os.path.join(out,cid.replace('|','_')+'.json')
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1)
    errs=add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load())
    print(os.path.basename(fn),errs)
