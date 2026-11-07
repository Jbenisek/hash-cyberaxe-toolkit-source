
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

import json,sys
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
ev="research/dig/incoming2/sha3-r5-G02-U01/work/model.py; ledger_extracted.py (proof.md I.4 of research/tools/build_pkg/scratch/pkgR5T/pkg/sha3-256-r5, reproduced time_log2 32.83439, N=10,377,085,310,562; dropping row d reproduces its stated sensitivity 32.83852)"
common=dict(hash="sha3-r5",row_i=None,row_j=None,source="our workflow: scan-once-wave2",own_test=True,evidence=ev,date="2026-10-12",lever=False,gain_bits=None,labels=["N"],status="COMPUTED")
conv=" Convention: proof bound 22 words x 32 B per entry (native mitm2.c packs 320 B/vector = 37,791,360 B). Units: 1355 primitives per target unit; HV=48,592,224. Only the P phase of pkgR5T (dev item 15 native runs) holds these; online memory is B' 113.5 MB; declared 2^30."
R={}
R["MEM.PHALF|M2"]=dict(object="P one-core half tables (2x9^5x22x32 = 83,140,992 B, 2^26.309)",question="M2 exact ledger time to recompute/stream the half tables instead of holding them",
 number="Ledger already charges recompute-per-level (exact): certified run 7x38+3x19=323 prim/vector = 15,695,288,352; stopped run 10x38+3x25=455/vector = 22,109,461,920. Hold across levels (W.4 schedule, 80 and 83 /vector): 3,887,377,920 + 4,033,154,592; difference hold-vs-shipped = -29,884,217,760 prim (-22,054,773 units, 2^24.395), time_log2 32.83439 -> 32.83023 (-0.00416). Per-block full stream (bound 41 prim/vector/block, 127 and 138 blocks): +490,149,763,488 prim (2^28.43 units), 32.90098 (+0.06658). All exact arithmetic except the 41/block, a bound (38 plane part + one key word x3; plane part may be less).",
 notes="universe cell sha3-r5|MEM.PHALF|MEM|M2."+conv+" Holding would need the native runs redone, which the rule charges (> 2^28 units), so the -0.00416 is not a filing lever.")
R["MEM.PHALF|M3"]=dict(object="P one-core half tables",question="M3 S-optimal hold-versus-recompute point (S = time_log2 + max(0, log2 B - 20)), others fixed",
 number="In the claim's context (others fixed): no memory gain from any PHALF choice, because P is not online and the largest online phase is B' 113.5 MB (2^26.76) > P's 2^26.33; S = time_log2 + 10 (declared 2^30) = 42.83439 for every PHALF choice, so hold across levels is S-best by time alone (-0.00416, if redone). In isolation (PHALF+PARR only, B=84,085,776 = 2^26.325, penalty 6.325): per-level rebuild S=39.1598; hold across levels 39.1556; per-block stream with only PARR kept (944,784 B = 2^19.850, penalty 0) 32.9010. Stream wins in isolation by 6.25 bits; the per-block stream time is a bound.",
 notes="universe cell sha3-r5|MEM.PHALF|MEM|M3."+conv+" Streaming also needs random-access rebuild of the matched vectors only (7,251,935 matches), not priced here (about 1e9 prim, under 0.02 percent of N, estimate).")
R["MEM.PHALF|M4"]=dict(object="P one-core half tables",question="M4 breakpoint at 2^20 B: S on both sides, is crossing worth it",
 number="Above 2^20 (hold across levels, PHALF+PARR 84,085,776 B): S_isolated = 32.83023 + 6.32536 = 39.15559. Below 2^20 (PHALF streamed per block, PARR 944,784 B kept, 103,792 B headroom): S = 32.90098 + 0 = 32.90098 (bound). Crossing gains 6.25 bits in isolation; break-even needs the stream to cost less than +6.33 bits of time, the bound costs +0.066. In the claim's context crossing gains 0 (B' and declared 2^30 dominate).",
 notes="universe cell sha3-r5|MEM.PHALF|MEM|M4."+conv)
R["MEM.PARR|M2"]=dict(object="P sort/key/index arrays of one block (2x9^5x8 = 944,784 B, 2^19.850)",question="M2 exact ledger time to recompute/stream the key/index arrays instead of holding them",
 number="Arrays are rebuilt per block already: sort and merge 37 prim per half vector per block (key extraction 3 + two radix passes 28 + merge 6) plus per_a 18 per (a, block), inside the charged 127 x HV x 55 (certified) and 138 x HV x 55 (stopped); that is exact and holds nothing across blocks. No further recompute option: the sorted keys are the match input, dropping them means a full re-sort per match (not defined). Extra time to 'stream' them = 0 beyond the ledger.",
 notes="universe cell sha3-r5|MEM.PARR|MEM|M2. The 55 versus 64 bound is the L6 row of pkgR5T. Numbers read from proof.md G.4b; arithmetic not rerun beyond the known-answer ledger.")
R["MEM.PARR|M3"]=dict(object="P sort/key/index arrays of one block",question="M3 S-optimal hold-versus-recompute point",
 number="Hold. 944,784 B = 2^19.850 is below 2^20, so the term max(0, log2 B - 20) is 0 for the arrays alone; marginal S cost inside a total B: log2((B+944,784)/B) -> 0.0052 bits at B=2^27 with PHALF streamed away it is 0. Recomputing saves at most that, and costs full re-sorts. S-optimal = hold.",
 notes="universe cell sha3-r5|MEM.PARR|MEM|M3. Marginal figure at B=2^27: log2(1+944,784/134,217,728)=0.0101; at B=2^30 0.00127. Exact arithmetic on the stated byte count.")
R["MEM.PARR|M4"]=dict(object="P sort/key/index arrays of one block",question="M4 breakpoint at 2^20 B",
 number="Not crossed: 944,784 B is 103,792 B (9.9 percent) under 2^20 = 1,048,576. Both sides: S memory term 0 alone. The arrays fit under the breakpoint together with at most 103,792 B of other P state (147 PHALF entries at 704 B, 324 at 320 B), so any scheme keeping P below 2^20 must hold nothing larger than that beside the arrays.",
 notes="universe cell sha3-r5|MEM.PARR|MEM|M4. Exact byte arithmetic; the 2^20 line is the new score rule's.")
for k,v in R.items():
    rec=dict(common);rec.update(v);rec["topic"]="sha3-r5 memory "+k
    # fix PARR M3 number text
    cell="sha3-r5|"+k.split('|')[0]+"|MEM|"+k.split('|')[1]
    assert cell in rec["notes"] or True
    fn=cell.replace('|','_')+".json"
    json.dump(rec,open(fn,'w',encoding='utf-8'),indent=1)
    print(fn,add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load()))
