
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
base = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G02-U07')
ev = "research/dig/incoming2/sha256-37-G02-U07/work/ (lowm_final.py copy of pkgR37M3, sens.py, disc.c, disc2.c, chk.py)"
KA = " Known-answer check: scratch copy of pkgR37M3 lowm_final.py reproduces time_log2 60.99099 and 607,744 B (2^19.2131); ledger floor preprocessing_log2 60.00141."
def rec(cid, obj, q, status, number, notes, labels=("N",)):
    return dict(hash="sha256-37", row_i=None, row_j=None, object=obj, question=q, labels=list(labels), status=status,
        number=number, source="our workflow: scan-once-wave2", own_test=True, evidence=ev, date="2026-10-12", lever=False,
        gain_bits=None, notes="universe cell %s. " % cid + notes + KA, topic=cid)
CODE_ZERO = ("Convention: pkgR37M3 proof 14.1 charges code as a bound of at most 8192 primitives x 8 B = 65,536 B (not an exact instruction count; the exact static size of the straight-line text was not measured). ")
R = []
c="sha256-37|MEM.CODE|MEM|M2"
R.append(rec(c,"program code (65,536 B bound)","M2 time to recompute/stream instead of holding","COMPUTED",
 "not applicable: code is not a table; ledger counts executed primitives, so 0 time_log2 either way (bound label)",
 CODE_ZERO+"Code has no recompute or stream form in the ledger; the only 'trade' is rolled vs unrolled text, and the ledger prices executed primitives only, so the ledger time is unchanged (60.99099). Instruction-fetch cost of a rolled loop was not measured (not in the ledger model)."))
c="sha256-37|MEM.CODE|MEM|M3"
R.append(rec(c,"program code (65,536 B bound)","M3 S-optimal hold-vs-recompute point","COMPUTED",
 "S = 60.99099 at any code size from 0 to 506,368 B (others fixed); S-optimal = any size in that range, current bound 65,536 B is inside",
 CODE_ZERO+"Others fixed (542,208 B of tables): total = 542,208 + code; memory term max(0, log2 B - 20) = 0 while code <= 506,368 B (63,296 primitives of 8 B). Removing all code would not change S. More unrolled code buys no ledger time (executed primitives are the charge), so no S gain."))
c="sha256-37|MEM.CODE|MEM|M4"
R.append(rec(c,"program code (65,536 B bound)","M4 breakpoint at 2^20 B","COMPUTED",
 "code breakpoint 506,368 B (7.73x the 65,536 B bound); total breakpoint headroom 440,832 B; crossing costs log2(B/2^20) bits and the most the whole ledger could save is 0.98958 bit, so crossing pays only if B < 2,082,059 B and the code removed all online work",
 CODE_ZERO+"Headroom: 2^20 - 607,744 = 440,832 B total; code alone could grow to 506,368 B if nothing else changes. Max possible saving = log2_T 60.990989 - preprocessing floor 60.001410 = 0.98958 bit (the 2^60 characteristic-search allowance is fixed), so extra memory beyond 2^20 is never worth it unless it removes essentially all online work; no code growth can do that. Bound, not a measurement of a rewritten program."))
PRE = ("Preprocessing (proof 14.2): discovery over the 2^29 values of E4, c7 grouping, 222 classes. Measured with our C scan disc.c/disc2.c (WSL, 1 core): |G| = 12,103,680, distinct c7 = 22,976, classes >= 3456 = 222, members 782,800, max class 3600 - all match the proof. ")
c="sha256-37|MEM.PRE|MEM|M1"
R.append(rec(c,"preprocessing working set (family discovery, PRE < 2^38 ops)","M1 bytes held at peak","COMPUTED",
 "exact allocations of our two-pass stream: pass 1 = 262,144 B (2^15 slots x 8 B; 22,976 keys need 183,808 B), pass 2 = 4,800 B; materialised variants: G as (a0,c7) 96,829,440 B = 2^26.53, G as a0 only 48,414,720 B, 222-class members only 3,131,200 B = 2^21.58. Peak of whole preprocessing = max(discovery, online tables) = 607,744 B",
 PRE+"The proof states only the online resident set (607,744 B); the preprocessing peak is not stated there and depends on how discovery is coded. The streaming tool passes pass-1 -> frees -> pass-2 and its output (n, first member, OR of xors per class) matches all 222 CLASSES entries of the program (c7, size, base/mask containment) with 0 mismatches. If both discovery tables and the 607,744 B online set were held at once: 873,440 B, still below 2^20. Python Env() build of the reference program peaks at 2.48 MB under tracemalloc (interpreter objects, a reference-implementation artifact, not the model's bytes)."))
c="sha256-37|MEM.PRE|MEM|M2"
R.append(rec(c,"preprocessing working set (family discovery, PRE < 2^38 ops)","M2 exact time to stream/recompute instead of holding","COMPUTED",
 "two-pass stream = 2 scans of 2^29 values (measured 5.3 s vs 1.1 s one-pass, 1 core); time_log2 unchanged at 60.99099 for PRE charged anywhere from 0 to 2^50 ops (60.990989434 -> 60.990989703 at 2^50)",
 PRE+"Ledger sensitivity (sens.py): pre_ops = 0, 2^38, 2^40, 2^44, 2^50 give time_log2 60.99099 each (log2_T 60.9909894344 / .94463 / .94660 / .94859 / .97025). The second scan costs about 2^29 x 80 ops = 2^35.3, inside the charged PRE = 2^38 (proof 14.2 total < 2^36.1). So streaming is free in time_log2."))
c="sha256-37|MEM.PRE|MEM|M3"
R.append(rec(c,"preprocessing working set (family discovery, PRE < 2^38 ops)","M3 S-optimal hold-vs-recompute point","COMPUTED",
 "S-optimal = stream (two-pass, <= 262,144 B): S = 60.99099 + 0 memory term; holding G costs +6.53 bit (96.8 MB) or +5.53 bit (a0 only), holding the 222-class members +1.58 bit, for 0 time gain",
 PRE+"If the judge counted the preprocessing peak, S for each variant = 60.99099 + max(0, log2 B - 20): (a0,c7) held 67.52; a0 only 66.52; class members only 62.57; stream 60.99. If only the online set counts (proof's reading) all four tie at 60.99099. Which reading the judge uses is not known from our files."))
c="sha256-37|MEM.PRE|MEM|M4"
R.append(rec(c,"preprocessing working set (family discovery, PRE < 2^38 ops)","M4 breakpoint at 2^20 B","COMPUTED",
 "streaming discovery stays under 2^20 B (262,144 B + 4,800 B; even with the 607,744 B online set held: 873,440 B); the first variant that crosses is holding the 222-class members (3,131,200 B, +1.58 bit); crossing buys 0 time",
 PRE+"Break-even on any crossing: the whole ledger can save at most 0.98958 bit, so no preprocessing table above 2,082,059 B can pay for itself, and since the PRE time is 2^28.6 units against 2^60.99, none pays at all. Crossing is not worth it."))
os.makedirs(base, exist_ok=True)
cells = add_cell.load()
for r in R:
    fn = os.path.join(base, r['topic'].replace('|','_') + '.json')
    json.dump(r, open(fn,'w',encoding='utf-8'), indent=1)
    add_cell.validate(json.load(open(fn,encoding='utf-8')), cells)
    print('ok', fn)
