
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
base=dict(hash="sha256-37",row_i=14,row_j=15,source="our workflow: scan-once-wave2",own_test=True,
 evidence="research/dig/incoming2/sha256-37-G04-U07/work/pad.c; work/run.sh; work/out.txt",date="2026-10-12",lever=False,gain_bits=0.0)
ev="Own pad.c validated: 128-byte test message digest equals verifier hash_functions.digest(m,'sha256',37); published pair CV2 equal and digests equal after the padding block; exhaustive 2^32 scan in published-difference mode reproduces the 8 row-14 passers of l16.out."
R=[
("Q1",dict(object="padding block (W0=0x80000000, W1..W14=0, W15=1024) and length words W14/W15 of block 3",
 question="Q1 count/size of the padding object as the attack uses it",labels=["N"],status="COMPUTED",
 number="exact: 1 padding block, 16 words, only 2 nonzero (W0=80000000, W15=00000400); identical in both members, difference 0; costs 1 extra 37-step compress per candidate pair that is output, 0 inside the search. Published pair: CV2 equal, digest equal after block 3. The data words W14/W15 of block 2 carry forced differences: W14 cells n=1,u=2 (xor 04400800, dW14=fc3ff800), W15 cell u=1 (xor 20000000, dW15=e0000000)",
 topic="sha256-37.CV.PADlen.Q1",notes="universe cell sha256-37|CV.PADlen|CV|Q1. Own code, validated on the verifier digest and the published pair. Block 3 is outside the characteristic (dCV=0 there). Cost relative to the 2^60-ish search is negligible (one compress; not itemised here).")),
("Q2",dict(object="padding block as separate block 3 (vs block 2 being the last block)",
 question="Q2 necessity: can the padding block be dropped / block 2 made last (W14,W15 = length words, dW14=dW15=0)?",labels=["K","Z"],status="LOCAL_ONLY",
 number="exact for the published chi37 and the published rows <=13: with dW14=dW15=0 (W14 any of 2^32 values, so also every length-word value), 0 of 2^32 pass the row-14 A cells (0 pass E/W cells too); with the published difference pattern the same scan gives 8 (A-cell pass 67,108,864). So a padded-last block 2 is impossible for this characteristic: the padding block is necessary, the extra block is the price. FIPS length words for a block-2-last message (W14=0, W15=8*len, len 65..119) are among the 2^32 tested",
 topic="sha256-37.CV.PADlen.Q2",notes="universe cell sha256-37|CV.PADlen|CV|Q2. LOCAL_ONLY: rows <=13 of the published pair held; a different characteristic with dW14=dW15=0 is a G03 support question and is not answered here. "+ev)),
("Q3",dict(object="freedom of (W14,W15) of block 2 under padded-last vs current layout",
 question="Q3 log2 freedom left in W14/W15",labels=["K"],status="LOCAL_ONLY",
 number="exact on published rows <=13: current layout row-14 passers 8 of 2^32 (3 bits; |L|=4096=12 bits and |L*|=32=5 bits after rows 14-15 and expansion, existing counts); dW14=dW15=0 layout: 0 passers (-inf bits, zero freedom). Padding block itself: 0 free bits (all 16 words fixed). Block-2 free bits if last: at most 440 of 512 (W14,W15 and the 0x80 byte fixed)",
 topic="sha256-37.CV.PADlen.Q3",notes="universe cell sha256-37|CV.PADlen|CV|Q3. The 440 vs 512 count is arithmetic from FIPS padding (55 data bytes max in a last block), not a scan. "+ev)),
("Q4",dict(object="block layout alternatives around the padding",
 question="Q4 alternatives: block 2 last; 120..127-byte messages; difference block earlier",labels=["Z"],status="LOCAL_ONLY",
 number="(a) block 2 last: impossible for chi37 (0 of 2^32, see Q2). (b) message length 120..127 bytes: 0x80 lands inside block 2 data (tail 56..63), padding block 3 still follows, so same extra block and fewer free bits (strictly worse). (c) 128-byte layout (current): block 3 constant, cost 1 compress per output. No alternative with a gain found; structural only, no gain",
 topic="sha256-37.CV.PADlen.Q4",notes="universe cell sha256-37|CV.PADlen|CV|Q4. (b) and (c) are FIPS arithmetic, (a) is the exhaustive scan. Longer messages with the difference block in the middle cost extra data blocks and are not scanned. "+ev)),
]
for q,d in R:
    r=dict(base); r.update(d)
    fn=f"sha256-37_CV.PADlen_CV_{q}.json"
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1)
    add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load()); print("ok",fn)
