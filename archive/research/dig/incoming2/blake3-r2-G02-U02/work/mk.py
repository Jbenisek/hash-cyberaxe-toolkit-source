
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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
out=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G02-U02')
ev="research/dig/incoming2/blake3-r2-G02-U02/work/m_scan.py (reuses ledger.py of research/tools/build_pkg/scratch/pkgB3S2/pkg/blake3-r2/proof.md Sec 18; proof.md Sec 11, 12, 9.6, 9.9)"
base=("Known answer reproduced first: ledger.py gives time_log2 62.43471 (62.4347098), search-phase bytes 6,013,036,259,648 (2^42.45123) and output-phase 8,796,093,155,510 (2^43.0000000219) exactly as proof.md prints. "
      "Convention: word = 32 B, code 32 B/instruction (r2 proof), ledger charges are the proof worst-case budgets (bound, not best-case executed). Pareto score S = time_log2 + max(0, log2 B - 20). "
      "Peak is the OUTPUT phase (2^43), tables are released before it, so in the package as filed a search-phase object has zero marginal memory cost; the memory term only moves under B3-STREAM (peak = search phase, S 84.88594). ")
def rec(cell,obj,q,status,number,lever,gain,notes,lab=None):
    r=dict(hash="blake3-r2",row_i=None,row_j=None,object=obj,question=q,labels=lab or ["C"],status=status,number=number,
      source="our workflow: scan-once-wave2",own_test=True,evidence=ev,date="2026-10-12",lever=lever,gain_bits=gain,
      notes="universe cell "+cell+". "+base+notes)
    if gain is not None: r["gain_basis"]="S"
    fn=cell.replace("|","_")+".json"
    json.dump(r,open(os.path.join(out,fn),"w",encoding="utf-8"),indent=1)
    add_cell.validate(r,add_cell.load()); print("ok",fn)

rec("blake3-r2|MEM.ROT|MEM|M2","three rotation tables ROR12/ROR7/ROR16 (3*2^32 words = 412,316,860,416 B, 2^38.585)",
 "M2: exact ledger time to recompute the rotations instead of holding the tables (M1 exact: 3*2^32 words*32 B)?","COMPUTED",
 "recompute = 4-op scalar ROR (the proof's own build charge) vs XOR+load 2: +3 units per rotation, 4 rotations per passing lane (ROR12 twice, ROR7, ROR16). Per table: ROR16 +3, ROR7 +4 (loses the B12 address trick), ROR12 +6, all three +12 units per passing lane x (PASS_BUDGET+2^19)=633,770,615,068,172,911 lanes. dT = +0.001023 / +0.001364 / +0.002045 / +0.004088 bits (all three, net of the 3*2^35+2^32 one-time build saved). Sharding/streaming not applicable: reads are random 32-bit keys.",
 False,None,"Bound (ledger budgets). Lane-0 and masking details of the 4-op rotation follow the proof convention; not re-derived.")
rec("blake3-r2|MEM.ROT|MEM|M3","three rotation tables: S-optimal hold-vs-recompute",
 "M3: S-optimal point for the rotation tables, others fixed?","COMPUTED",
 "As filed (peak = output phase 2^43): HOLD, recompute only adds +0.0041 bit. If the output is streamed (B3-STREAM, peak = search phase): RECOMPUTE all three, dS = -0.0984 bit (dT +0.0041, memory term 42.4512 -> 42.3487, saves 412,316,860,416 B, -0.1025); best single table ROR16 dS = -0.0323, ROR7 -0.0320, ROR12 -0.0313.",
 True,0.098,"Conditional lever: only after an organizer ruling that streamed output is not held (B3-STREAM, OPEN); it stacks on that lever (S 84.88594 -> about 84.7875). One measurement, not chased; interaction with the BT and replica cuts is roughly additive in memory but not re-run jointly.")
rec("blake3-r2|MEM.ROT|MEM|M4","three rotation tables: breakpoint at 2^20 B",
 "M4: is crossing 2^20 B worth it for the rotation tables?","COMPUTED",
 "The tables are 2^38.585 B; removing them leaves the peak at 2^42.35 (stream) or 2^43 (as filed), far above 2^20, so the max(0, .) kink is never reached; the marginal price is 1 bit per doubling of the whole peak, dMem = log2(P/(P-412,316,860,416)) = 0.1025 bit (stream) / 0 (as filed). Break-even: recompute pays iff its time cost < 0.1025 bit; actual 0.0041. Crossing 2^20 would need the whole 2^42.45 B search state gone: no.",
 False,None,"Standalone the object alone would score 18.585 on the memory term, but it is not alone.")
rec("blake3-r2|MEM.BT|MEM|M2","BT and its six lane copies (7*2^32 words = 962,072,674,304 B, 2^39.807)",
 "M2: exact ledger time to compute the broadcast instead of loading BT?","COMPUTED",
 "Per opened cluster the proof charges 4 for two broadcasts (AND with lane mask + load of BT_i). Recompute of the whole table: AND, shift down 36i, 3 shifts + 3 ORs (w|w<<36, |<<72, |<<108) = 8 per broadcast, +6 each: +12 per opened cluster x (A_BUDGET+16384)=8,114,703,155,646,769,428 clusters: dT = +0.051483 bits (one-time build 30*2^32 saved). Cut only the six lane copies (keep BT_0; shift lane value down to lane 0, OR the base 2^252 into the address: +2 per broadcast, +4 per cluster): dT = +0.017366 bits. Straddling clusters (F_BUDGET 2.7e15) not added; effect < 1e-5 bit.",
 False,None,"Bound (ledger budgets; the lane-0 saving of one shift ignored because the ledger charges every lane alike). The +2 per broadcast for BT_0 access assumes loads take no immediate offset (the proof's XOR-base trick implies that).")
rec("blake3-r2|MEM.BT|MEM|M3","BT and six lane copies: S-optimal hold-vs-recompute",
 "M3: S-optimal point for BT and its lane copies, others fixed?","COMPUTED",
 "As filed: HOLD (recompute +0.0171 bit, memory term unchanged). With B3-STREAM: cut the six lane copies, keep BT_0: dS = -0.1954 bit (dT +0.0174, memory -0.2128, 824,633,720,832 B); dropping all 7 tables: dS = -0.2001 bit (dT +0.0515, memory -0.2515); the two are within 0.005, so the 6-copy cut is the cheap variant.",
 True,0.195,"Conditional lever: needs B3-STREAM first (OPEN, needs an organizer ruling); stacks on it, so S 84.88594 -> about 84.690. This is a different object from B3-replica (lane replicas of T2'/T1/gate table) and is not covered by that cell. One measurement, not chased.")
rec("blake3-r2|MEM.BT|MEM|M4","BT and six lane copies: breakpoint at 2^20 B",
 "M4: is crossing 2^20 B worth it for BT?","COMPUTED",
 "BT is 2^39.807 B; the peak stays at 2^42.2 to 2^43 without it, so the 2^20 kink is not crossed. Break-even: recompute pays iff time cost < log2(P/(P-B)): 6 copies 0.2128 bit vs 0.0174 actual; full BT 0.2515 vs 0.0515. As filed the memory term is flat (peak = output) so the answer is no.",
 False,None,"Only the peak-moving case (stream) is a win.")
rec("blake3-r2|MEM.SMALL|MEM|M2","member lists, P, automata, transition arrays, solver arrays, names (fewer than 2,563,914 words = 82,045,248 B)",
 "M2: exact ledger time to recompute the small data instead of holding it?","COMPUTED",
 "M1: the bound 2,563,914 words is exactly the sum of the component maxima (168,522 + 2^21 + 29,952 + 2^18 + 4,096 + 1,024 + 512 + 512), so it is a bound, not an executed count. Recompute of the member lists per context (2^26+2^20 units, the proof build charge; each of RUN_CONTEXTS=1,218,911,201,562,375 contexts reads all 2^19 members): dT = +4.9998 bits (about 31 x the whole ledger). Automata and transition arrays (2^26 build each) are read in every context and cluster: same verdict. The descriptor table (512 words) is already rebuilt per context (48,896 units).",
 False,None,"P (2^21 words, 67 MB) is labelled 'the table P of the earlier gate, kept' in Sec 11; whether anything still reads it was not traced here. Dropping it would save at most 2^27 build units and 0.016 bit of memory under stream. Not tested, a possible small cut.",lab=["N"])
rec("blake3-r2|MEM.SMALL|MEM|M3","small data: S-optimal hold-vs-recompute",
 "M3: S-optimal point for the small data, others fixed?","COMPUTED",
 "HOLD everything. Even deleting all 82,045,248 B for free would gain only 0.0000197 bit under stream (0 as filed); recomputing the member lists alone costs +5.0 bits for 1.3e-6 bit of memory.",
 False,None,"The memory term is insensitive: these are 1.4 percent of the search phase.",lab=["N"])
rec("blake3-r2|MEM.SMALL|MEM|M4","small data: breakpoint at 2^20 B",
 "M4: is crossing 2^20 B worth it for the small data?","COMPUTED",
 "The small data are at most 2^26.29 B (6.29 bits above the 2^20 kink if the program held nothing else), but the program peak is 2^42.45 to 2^43 B, so the kink is never reached and the marginal value is 1.97e-5 bit. No crossing is worth any recompute.",
 False,None,"Standalone score of the object alone is 6.290; irrelevant next to the big tables.",lab=["N"])
