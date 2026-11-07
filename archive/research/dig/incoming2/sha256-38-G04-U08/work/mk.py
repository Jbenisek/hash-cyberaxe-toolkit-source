
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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
base=dict(hash="sha256-38",row_i=14,row_j=15,source="our workflow: scan-once-wave2",own_test=True,
 evidence="research/dig/incoming2/sha256-38-G04-U08/work/pad.c; work/run.sh; work/out_pub.txt; work/out_stage1.txt; work/out_stage2.txt",date="2026-10-12",lever=False,gain_bits=0.0)
ev="Own pad.c validated: 128-byte test message (bytes 0..127) digest 76a19c57..ecea equals verifier hash_functions.digest(m,'sha256',38); published chi38 pair: CV2 equal, digests equal after the padding block."
R=[
("Q1",dict(object="padding block (W0=0x80000000, W1..W14=0, W15=1024) and length words W14/W15 of block 2",
 question="Q1 count/size of the padding object as the attack uses it",labels=["N"],status="COMPUTED",
 number="exact: 1 padding block, 16 words, 2 nonzero (W0=80000000, W15=00000400), identical in both members (difference 0); 1 extra 38-step compress per output pair, 0 inside the search. Published pair: CV2 equal, digest equal after block 3. In block 2 of chi38: W14 has NO difference cells (32 '='; dW14=0 in the published pair), W15 has n=2,u=1 (xor 04400800, dW15 mod = fc400800)",
 topic="sha256-38.CV.PADlen.Q1",notes="universe cell sha256-38|CV.PADlen|CV|Q1. "+ev)),
("Q2",dict(object="padding block as separate block 3 (vs block 2 being the last block)",
 question="Q2 necessity: can the padding block be dropped / block 2 made last (dW14=dW15=0)?",labels=["Z"],status="OPEN",
 number="NOT COMPLETED. Exact so far (rows <=13 of published chi38 held): dW14=0 is already the published pattern, 160 of 2^32 W14 values pass row 14 (A-cell pass 134,217,728; published W14 d28e48a0 among them). The decisive step (for each of the 160, scan all 2^32 W15 with dW15=0 for row 15) was started but killed unfinished at the time limit (machine load ~29); no result, UNKNOWN not UNSAT. In chi38 only dW15 would have to be removed (3 difference cells n,n,u in W15 and row-15 A/E cells)",
 topic="sha256-38.CV.PADlen.Q2",notes="universe cell sha256-38|CV.PADlen|CV|Q2. Status OPEN: scan2 mode 0 (dW15=0) printed no PASS before kill but covered an unknown fraction of the 160 passers. LOCAL_ONLY-type question anyway (rows <=13 held; other supports are G03). Re-run: work/run.sh ./pad scan2 out_stage1.txt (about 160 x 2 x 2^32 evaluations, ~20+ min per mode at load 29). "+ev)),
("Q3",dict(object="freedom of (W14,W15) of block 2 in the current layout",
 question="Q3 log2 freedom left in W14/W15",labels=["N"],status="LOCAL_ONLY",
 number="exact on published rows <=13: W14 row-14 passers 160 of 2^32 (log2 = 7.32 bits; structure: low 16 bits are 48a0 or 58a0 (one free bit, 0x1000) and the high 16 bits take 80 values); A14-cell pass 2^27. Padding block: 0 free bits. Block 2 if last: at most 440 of 512 free bits (FIPS arithmetic: W14,W15 and 0x80 byte fixed). W15 freedom after row 14: not completed",
 topic="sha256-38.CV.PADlen.Q3",notes="universe cell sha256-38|CV.PADlen|CV|Q3. LOCAL_ONLY: rows<=13 held, row-14 cells, plus-conditions rows 13/14. 160 = 2^7.32. The 440 count is arithmetic, not a scan. "+ev)),
("Q4",dict(object="block layout alternatives around the padding",
 question="Q4 alternatives: block 2 last; 120..127-byte messages; difference block earlier",labels=["Z"],status="LOCAL_ONLY",
 number="(a) block 2 last: not decided (see Q2, UNKNOWN). (b) message length 120..127 bytes: 0x80 lands inside block 2 data, padding block 3 still follows: same extra block, fewer free bits (strictly worse, FIPS arithmetic). (c) 128-byte layout (current): constant block 3, 1 compress per output. No alternative with a gain found",
 topic="sha256-38.CV.PADlen.Q4",notes="universe cell sha256-38|CV.PADlen|CV|Q4. (b),(c) arithmetic; (a) open. "+ev)),
]
for q,d in R:
    r=dict(base); r.update(d)
    fn=f"../sha256-38_CV.PADlen_CV_{q}.json"
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1)
    add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load()); print("ok",fn)
