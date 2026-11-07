
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
D=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G02-U04')
ev="research/dig/incoming2/blake3-r2-G02-U04/work/mvar.py (+listsize.py, ledger_new.py and frontline.py copied from research/tools/build_pkg/scratch/pkgB3V/work, mvar.json, listrows.json)"
conv=("Convention: pkgB3V proof (credited derivative of c994a61f), ledger_new.py machine units (430 per time unit), words 256 bit = 32 B, code 32 B/instruction, lists stored as doubled lists (H(st) twice, 7 entries per packed word) plus prefix counts C_st[0..2^17] one word each (the declared layout; packing 8 per word is not priced). "
      "KNOWN ANSWERS reproduced first: ledger_new.py NEW gives N=62,066,075,169,728,519,695, time_log2 57.0023; typed E-word counts recomputed by level16/get_lists: type0 23,820,160 and type1 34,028,800 (4,160 live low halves each, 6 live states + 1 dead each); class kept sums 389,525,760; dropping changes 11-13 (typed lists, member 68, no class build) gives 57.1890 = the c994a61f figure. "
      "The 23,820,160 / 34,028,800 are E-word counts (sum over live low halves of list length), NOT stored size: lists are stored once per live STATE. Package declares memory_log2_bytes 60 (bound: output < 2^59, search < 2^42.001 incl. code), so shipped S = 57.0023 + 40 = 97.0023. ")
base=dict(hash="blake3-r2",row_i=None,row_j=None,object="MEM.OMEGA typed omega lists (23,820,160 t=0 / 34,028,800 t=1 E-words; stored as 96 class-by-state doubled lists + prefix counts)",
 labels=["N"],status="COMPUTED",source="our workflow: scan-once-wave2",own_test=True,evidence=ev,date="2026-10-12",lever=False,gain_bits=None)
R={}
R["M1"]=dict(question="Bytes held at peak by the typed omega lists (exact allocation of the shipped program, bound vs exact)",
 number="EXACT list store: 96 lists (16 classes x 6 live states) = 160,506 packed list words + 96*(2^17+1) = 12,583,008 prefix words = 12,743,514 words = 407,792,448 B = 2^28.603 B (exact, undeduped; 30 distinct (type,state,mask) lists would be 42,090 + 3,932,190 words = 2^27.3 B). Package bound: 'fewer than 2^24 words' = 2^29 B (bound, tight within 0.4 bit); pure typed lists: 12 lists, 23,823 list words. Share of the search memory 2^42.001 B: 9.3e-5; of declared 2^60: 3.5e-10. Held through the whole search (read-only, written once in step 0).",
 notes="universe cell blake3-r2|MEM.OMEGA|MEM|M1. "+conv+"Per-list max 1,648 (t0) / 2,355 (t1) list words. Not run: the full shipped program (list builder get_lists of frontline.py run; sizes read from its output). Code of the mask test (5 masks D on omega bits 16-22) is in MEM.CODE3, not here.",
 topic="blake3-r2|MEM.OMEGA|MEM|M1")
R["M2"]=dict(question="Exact ledger time to recompute/stream/shard the lists instead of holding them",
 number="Hold = 0. Alternatives (ledger_new.py, whole-run N, dT vs shipped 57.0023): (a) class lists replaced by 12 typed lists + 128-bit mask test (changes 11-13 reverted): +0.18675 bit (57.1890), lists 12,743,514 -> 1,596,699 words (2^28.603 -> 2^25.607 B); (b) rebuild the (class,state) list at every live block from held typed lists: live blocks LIVE_B = 2,075,978,226,685,334 (2^50.883) x 332,373 units (2*(2^17+1) prefix + 6/entry, state-weighted mean) = +3.599 bit (60.6013); (c) full DFS rebuild per live block: 8.688e12 units/list (BUILD/96 = 2^42.98) -> +28.114 bit (85.1168). Break-even: a rebuild costing 208 units per live block already adds 0.01 bit, 29,900 units adds 1 bit.",
 notes="universe cell blake3-r2|MEM.OMEGA|MEM|M2. "+conv+"(b)/(c) are lower-bound models (one rebuild per live block, no sharing between blocks of one context, BUILD kept in the once row); sharding is not priced separately: 96 lists are already the shard unit and one list is read per live block. Not run: a program that rebuilds lists; ledger arithmetic only.",
 topic="blake3-r2|MEM.OMEGA|MEM|M2")
R["M3"]=dict(question="S-optimal hold-versus-recompute point for the lists with the other objects fixed",
 number="HOLD the shipped 96 class lists. S (declared 2^60 B) = 97.0023; typed-only 97.1890 (+0.1868); per-block rebuild 100.6013; DFS rebuild 125.1168. Even on a hypothetical search-only memory base 2^42.001 B (output streamed, not filed) the S memory term of the lists is log2(1+9.27e-5) = 1.34e-4 bit, while the cheapest saving (typed-only, -356,698,080 B) gains 1.17e-4 bit of memory term and costs 0.18675 bit of time: net loss 0.1866 bit. No recompute point beats holding.",
 notes="universe cell blake3-r2|MEM.OMEGA|MEM|M3. "+conv+"The lists are 2^-13.4 of the 2^42.001 B search store (T2'/T1/replicas/rotation tables dominate), so their hold-versus-recompute choice is decided by time alone. Not run: variants beyond (a)-(c) of M2 (e.g. packing prefix counts 8 per word: saves 2^28.6 -> ~2^26 B, needs extra shift/AND per lookup, unpriced; memory gain <1e-4 bit anyway).",
 topic="blake3-r2|MEM.OMEGA|MEM|M3")
R["M4"]=dict(question="Breakpoint at 2^20 B: S on both sides, is crossing worth it",
 number="Not worth it, and not reachable: the lists need 2^28.603 B (shipped) or 2^25.607 B (typed-only, 12 lists with 2^17+1 prefix words each); 2^20 B = 32,768 words, the 23,823 typed list words alone would fit but the prefix tables (12 x 131,073 words) do not. The whole program holds >= 2^42 B, so the term max(0, log2 B - 20) is already linear and the lists move it by <= 1.4e-4 bit (S=T+40 declared; T+22.001 on search-only base). Crossing 2^20 for the lists alone changes S by 0 for B and by -1.2e-4 at best.",
 notes="universe cell blake3-r2|MEM.OMEGA|MEM|M4. "+conv+"Breakpoint applies to total bytes, not per object; total is 2^42.001 (search) or 2^60 (declared), so no per-object crossing of 2^20 exists. Not run: a layout fitting the lists into 2^20 B (it would need on-the-fly prefix counts, i.e. a rank structure, unpriced).",
 topic="blake3-r2|MEM.OMEGA|MEM|M4")
for k,v in R.items():
    r=dict(base); r.update(v)
    fn=D+"/blake3-r2_MEM_OMEGA_MEM_%s.json"%k
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1)
    sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig')); import add_cell
    add_cell.validate(json.load(open(fn,encoding='utf-8')), add_cell.load()); print(k,'valid')
